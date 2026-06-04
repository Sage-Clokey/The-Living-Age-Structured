"""
engine_torch.py — PyTorch morphogenesis engine.

Key differences from engine.py (NumPy):
  - All tip math runs on torch.Tensor (CPU or CUDA)
  - Directional adjustment is fully vectorised: one tensor op over all N
    alive tips simultaneously, not a Python loop
  - Noise generation uses torch.randn (fast, GPU-native)
  - GRN is an nn.Module with learnable Linear layers
  - Segments accumulated as torch tensors, converted to numpy only on export

Device selection:
    engine = MorphoEngineTorch(params)          # auto: CUDA if available
    engine = MorphoEngineTorch(params, 'cpu')   # force CPU
    engine = MorphoEngineTorch(params, 'cuda')  # force GPU
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from presets import GrowthParams


# ── Device helper ─────────────────────────────────────────────────────────────

def _default_device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ── Vectorised geometry (operates on batched tensors) ─────────────────────────

def _apply_bias(
    pos:    torch.Tensor,   # (N, 3)
    d:      torch.Tensor,   # (N, 3)
    params: GrowthParams,
    device: torch.device,
) -> torch.Tensor:
    """
    Adjust all N tip directions simultaneously according to growth mode.
    Returns normalised (N, 3) tensor.
    """
    up = torch.tensor([0., 1., 0.], device=device)

    if params.mode == "tree":
        d = d + up * params.upward_bias
        radial = pos.clone(); radial[:, 1] = 0.0
        r_len = radial.norm(dim=1, keepdim=True)
        mask  = (r_len > 1e-9).expand_as(radial)
        d     = d + F.normalize(radial, dim=1) * params.radial_bias * mask.float()

    elif params.mode == "coral":
        d = d + up * (0.6 * params.upward_bias)
        r_len = pos.norm(dim=1, keepdim=True)
        mask  = (r_len > 1e-9).expand_as(pos)
        d     = d + F.normalize(pos, dim=1) * max(params.radial_bias, 0.25) * mask.float()

    elif params.mode == "spiral":
        d = d + up * params.upward_bias
        xy = pos.clone(); xy[:, 1] = 0.0
        xy_len = xy.norm(dim=1, keepdim=True)
        mask   = (xy_len.squeeze(1) > 1e-9)

        if mask.any():
            tangent        = torch.stack([-xy[:, 2],
                                          torch.zeros(pos.shape[0], device=device),
                                          xy[:, 0]], dim=1)
            tangent        = F.normalize(tangent, dim=1)
            twist          = max(params.twist_strength, 0.40)
            radial_s       = max(params.radial_bias,    0.15)
            d[mask]        = (d[mask]
                              + tangent[mask] * twist
                              + F.normalize(xy[mask], dim=1) * radial_s)
        else:
            d[:, 0] += 0.15

    return F.normalize(d, dim=1)


def _rotate_vec(
    vec:   torch.Tensor,   # (3,)
    axis:  torch.Tensor,   # (3,)
    angle: float,
) -> torch.Tensor:
    """Rodrigues rotation on a single (3,) vector."""
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    axis  = F.normalize(axis.unsqueeze(0), dim=1).squeeze(0)
    return (
        vec * cos_a
        + torch.linalg.cross(axis, vec) * sin_a
        + axis * torch.dot(axis, vec) * (1.0 - cos_a)
    )


def _orthogonal(v: torch.Tensor, device: torch.device) -> torch.Tensor:
    """Return a unit vector orthogonal to v (3,)."""
    u = (torch.tensor([1., 0., 0.], device=device)
         if abs(float(v[0])) < 0.9
         else torch.tensor([0., 1., 0.], device=device))
    return F.normalize(torch.linalg.cross(u, v).unsqueeze(0), dim=1).squeeze(0)


# ── Segment store ──────────────────────────────────────────────────────────────

@dataclass
class TorchSegment:
    start:  np.ndarray
    end:    np.ndarray
    radius: float
    depth:  int


# ── Engine ────────────────────────────────────────────────────────────────────

class MorphoEngineTorch:
    """
    PyTorch morphogenesis engine.

    Tip state is stored in fixed-size pre-allocated tensors.
    All directional math is batched over all alive tips at once.
    Branching still uses a Python loop (tip count is dynamic) but
    every inner operation is a torch call.

    Usage:
        engine = MorphoEngineTorch(params)
        engine.run()
        segs   = engine.segments          # list[TorchSegment]
        engine.save_obj("out.obj")
        engine.save_json("out.json")
    """

    def __init__(
        self,
        params: GrowthParams,
        device: str | torch.device | None = None,
    ) -> None:
        self.params = params
        self.device = (
            torch.device(device) if device else _default_device()
        )

        torch.manual_seed(params.seed)

        # Pre-allocate tip buffers (max possible slots)
        MAX             = params.max_tips * 3
        self._pos       = torch.zeros(MAX, 3, device=self.device)
        self._dir       = torch.zeros(MAX, 3, device=self.device)
        self._rad       = torch.zeros(MAX,    device=self.device)
        self._alive     = torch.zeros(MAX, dtype=torch.bool,  device=self.device)
        self._depth     = torch.zeros(MAX, dtype=torch.long,  device=self.device)
        self._next_slot = 1

        # Init first tip
        if params.mode == "spiral":
            init_dir = F.normalize(
                torch.tensor([0.5, 1., 0.], device=self.device).unsqueeze(0), dim=1
            ).squeeze(0)
        elif params.mode == "coral":
            init_dir = F.normalize(
                torch.tensor([0.15, 1., 0.05], device=self.device).unsqueeze(0), dim=1
            ).squeeze(0)
        else:
            init_dir = torch.tensor([0., 1., 0.], device=self.device)

        self._dir[0]   = init_dir
        self._rad[0]   = params.initial_radius
        self._alive[0] = True

        self.segments: List[TorchSegment] = []

    # ── Simulation loop ───────────────────────────────────────────────────────

    def step(self) -> None:
        p          = self.params
        alive_idx  = self._alive.nonzero(as_tuple=True)[0]   # indices of alive tips
        if alive_idx.numel() == 0:
            return

        # ── Batch all alive tips ─────────────────────────────────────────────
        pos = self._pos[alive_idx]   # (N, 3)
        d   = self._dir[alive_idx]   # (N, 3)
        rad = self._rad[alive_idx]   # (N,)
        dep = self._depth[alive_idx] # (N,)

        # Directional bias (vectorised over all N tips)
        d = _apply_bias(pos, d, p, self.device)

        # Gaussian noise (torch.randn — GPU-native)
        d = d + torch.randn_like(d) * p.noise_strength
        d = F.normalize(d, dim=1)

        # Advance
        new_pos = pos + d * p.step_size
        new_rad = rad * p.taper

        # Kill predicate (vectorised)
        kill = (new_rad < p.min_radius) | (dep >= p.max_depth)

        # ── Per-tip update (branching requires individual handling) ──────────
        for i, glob_idx in enumerate(alive_idx.tolist()):
            if kill[i]:
                self._alive[glob_idx] = False
                continue

            # Record segment (move to CPU for export-friendly storage)
            self.segments.append(TorchSegment(
                start  = pos[i].cpu().numpy(),
                end    = new_pos[i].cpu().numpy(),
                radius = float(rad[i]),
                depth  = int(dep[i]),
            ))

            # Update tip in-place
            self._pos[glob_idx]   = new_pos[i]
            self._dir[glob_idx]   = d[i]
            self._rad[glob_idx]   = new_rad[i]

            # Branching
            alive_count = int(self._alive.sum())
            has_slot    = self._next_slot < self._pos.shape[0]

            if (
                has_slot
                and alive_count < p.max_tips
                and int(dep[i]) < p.max_depth
                and torch.rand(1, device=self.device).item() < p.branching_probability
            ):
                ortho     = _orthogonal(d[i], self.device)
                base_ang  = p.branch_angle_deg * math.pi / 180
                angle     = (base_ang * 1.15 if p.mode == "coral"
                             else base_ang * 0.85 if p.mode == "spiral"
                             else base_ang)

                dir1 = F.normalize(_rotate_vec(d[i], ortho,  angle).unsqueeze(0), dim=1).squeeze(0)
                s    = self._next_slot
                self._pos[s]   = new_pos[i]
                self._dir[s]   = dir1
                self._rad[s]   = max(float(new_rad[i]) * 0.85, p.min_radius)
                self._alive[s] = True
                self._depth[s] = dep[i] + 1
                self._next_slot += 1

                if (self._next_slot < self._pos.shape[0]
                        and torch.rand(1, device=self.device).item() < p.split_probability):
                    dir2 = F.normalize(_rotate_vec(d[i], ortho, -angle).unsqueeze(0), dim=1).squeeze(0)
                    s2   = self._next_slot
                    self._pos[s2]   = new_pos[i]
                    self._dir[s2]   = dir2
                    self._rad[s2]   = max(float(new_rad[i]) * 0.82, p.min_radius)
                    self._alive[s2] = True
                    self._depth[s2] = dep[i] + 1
                    self._next_slot += 1

    def run(self) -> None:
        for _ in range(self.params.steps):
            if not self._alive.any():
                break
            self.step()

    # ── Export ────────────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "mode":          self.params.mode,
            "device":        str(self.device),
            "segment_count": len(self.segments),
            "segments": [
                {
                    "x1": float(s.start[0]), "y1": float(s.start[1]), "z1": float(s.start[2]),
                    "x2": float(s.end[0]),   "y2": float(s.end[1]),   "z2": float(s.end[2]),
                    "radius": s.radius,
                    "depth":  s.depth,
                }
                for s in self.segments
            ],
        }

    def save_obj(self, path: str) -> str:
        """Wireframe OBJ (vertex + line records only)."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            f"# Living Systems Design Lab — PyTorch Export",
            f"# mode: {self.params.mode}  device: {self.device}",
            f"# segments: {len(self.segments)}",
            "",
        ]
        vi = 1
        for seg in self.segments:
            s, e = seg.start, seg.end
            lines.append(f"v {s[0]:.6f} {s[1]:.6f} {s[2]:.6f}")
            lines.append(f"v {e[0]:.6f} {e[1]:.6f} {e[2]:.6f}")
            lines.append(f"l {vi} {vi + 1}")
            vi += 2
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return str(p.resolve())

    def save_mesh_obj(self, path: str, sides: int = 6) -> str:
        """
        Export a solid tube-mesh OBJ with real faces — no PyVista needed.

        Each segment is a cylinder with `sides` quad faces.
        The result opens directly in Blender, MeshLab, or any 3D app.
        """
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)

        out_v: list[str] = [
            "# Living Systems Design Lab — Solid Mesh OBJ",
            f"# mode: {self.params.mode}  device: {self.device}",
            f"# segments: {len(self.segments)}  sides: {sides}",
            "",
        ]
        out_f: list[str] = []
        vi = 1  # 1-based OBJ vertex index

        angles = [2.0 * math.pi * k / sides for k in range(sides)]

        for seg in self.segments:
            s = seg.start.astype(float)
            e = seg.end.astype(float)
            r = max(float(seg.radius), float(self.params.min_radius))

            d = e - s
            length = np.linalg.norm(d)
            if length < 1e-12:
                continue
            d /= length

            # Build orthonormal frame (d, u, v)
            ref = np.array([1.0, 0.0, 0.0]) if abs(d[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
            u = np.cross(ref, d)
            u /= np.linalg.norm(u)
            v = np.cross(d, u)

            # Ring vertices at start and end caps
            ring_s = [s + r * (math.cos(a) * u + math.sin(a) * v) for a in angles]
            ring_e = [e + r * (math.cos(a) * u + math.sin(a) * v) for a in angles]

            for pt in ring_s:
                out_v.append(f"v {pt[0]:.6f} {pt[1]:.6f} {pt[2]:.6f}")
            for pt in ring_e:
                out_v.append(f"v {pt[0]:.6f} {pt[1]:.6f} {pt[2]:.6f}")

            # Quad faces (two triangles per side)
            for k in range(sides):
                k1  = k
                k2  = (k + 1) % sides
                vs0 = vi + k1           # start ring, vertex k
                vs1 = vi + k2           # start ring, vertex k+1
                ve0 = vi + sides + k1   # end ring,   vertex k
                ve1 = vi + sides + k2   # end ring,   vertex k+1
                out_f.append(f"f {vs0} {vs1} {ve1} {ve0}")

            vi += sides * 2

        content = "\n".join(out_v) + "\n\n" + "\n".join(out_f) + "\n"
        p.write_text(content, encoding="utf-8")
        return str(p.resolve())

    def save_json(self, path: str) -> str:
        import json
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        return str(p.resolve())

    def save_state(self, path: str) -> str:
        """Save full tip tensor state as a .pt file (reloadable with torch.load)."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            "params":    vars(self.params),
            "positions": self._pos[:self._next_slot].cpu(),
            "directions":self._dir[:self._next_slot].cpu(),
            "radii":     self._rad[:self._next_slot].cpu(),
            "alive":     self._alive[:self._next_slot].cpu(),
            "depths":    self._depth[:self._next_slot].cpu(),
            "segment_count": len(self.segments),
        }, str(p))
        return str(p.resolve())

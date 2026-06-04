"""
engine.py — Core morphogenesis simulation engine.

Architecture:
  - GrowthParams    : all tunable parameters (see presets.py)
  - Segment         : a grown branch segment (start, end, radius)
  - Tip             : an active growing apex
  - MorphogenesisEngine : runs the simulation, builds mesh output

Growth loop per step:
  1. For each alive tip, adjust direction (mode bias + tropism + noise + collision)
  2. Advance tip by step_size, record segment
  3. Possibly spawn child tips (branching / splitting)
  4. Kill tips that are too thin, too deep, or out of bounds

Coordinate system: Y-up (matches Three.js browser viewer).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np

try:
    import pyvista as pv
    _PYVISTA = True
except ImportError:
    _PYVISTA = False

from presets import GrowthParams


# ── Geometry utilities ────────────────────────────────────────────────────────

def normalize(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    return v / n if n > 1e-12 else v.copy()


def random_unit_vector() -> np.ndarray:
    """Uniformly distributed unit vector on the sphere."""
    phi   = math.acos(2.0 * random.random() - 1.0)
    theta = 2.0 * math.pi * random.random()
    return np.array([
        math.sin(phi) * math.cos(theta),
        math.sin(phi) * math.sin(theta),
        math.cos(phi),
    ])


def rotate_vector(vec: np.ndarray, axis: np.ndarray, angle_rad: float) -> np.ndarray:
    """Rodrigues' rotation formula."""
    axis   = normalize(axis)
    cos_a  = math.cos(angle_rad)
    sin_a  = math.sin(angle_rad)
    return (
        vec * cos_a
        + np.cross(axis, vec) * sin_a
        + axis * np.dot(axis, vec) * (1.0 - cos_a)
    )


def orthogonal_vector(v: np.ndarray) -> np.ndarray:
    """Return any unit vector orthogonal to v."""
    v = normalize(v)
    u = np.array([1.0, 0.0, 0.0]) if abs(v[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    return normalize(np.cross(u, v))


def distance_point_to_segment(p: np.ndarray, a: np.ndarray, b: np.ndarray) -> float:
    """Minimum distance from point p to segment ab."""
    ab    = b - a
    denom = np.dot(ab, ab)
    if denom < 1e-12:
        return float(np.linalg.norm(p - a))
    t       = float(np.dot(p - a, ab) / denom)
    t       = max(0.0, min(1.0, t))
    closest = a + t * ab
    return float(np.linalg.norm(p - closest))


# ── Data structures ───────────────────────────────────────────────────────────

@dataclass
class Segment:
    start:     np.ndarray
    end:       np.ndarray
    radius:    float
    parent_id: Optional[int] = None


@dataclass
class Tip:
    position:      np.ndarray
    direction:     np.ndarray
    radius:        float
    age:           int  = 0
    alive:         bool = True
    lineage_depth: int  = 0


# ── Engine ────────────────────────────────────────────────────────────────────

class MorphogenesisEngine:
    """
    Iterative branching growth engine.

    Usage:
        engine = MorphogenesisEngine(params)
        engine.run()
        mesh = engine.build_tube_mesh()
    """

    def __init__(self, params: GrowthParams) -> None:
        self.params   = params
        self.rng      = random.Random(params.seed)
        np.random.seed(params.seed)

        self.segments: List[Segment] = []
        self.tips:     List[Tip]     = []
        self.origin    = np.zeros(3, dtype=float)

        self._init_tips()

    # ── Initialisation ────────────────────────────────────────────────────────

    def _init_tips(self) -> None:
        if self.params.mode == "coral":
            init_dir = normalize(np.array([0.15, 1.0, 0.05]))
        elif self.params.mode == "spiral":
            init_dir = normalize(np.array([0.50, 1.0, 0.00]))
        else:
            init_dir = np.array([0.0, 1.0, 0.0])

        self.tips.append(Tip(
            position      = self.origin.copy(),
            direction     = init_dir,
            radius        = self.params.initial_radius,
            age           = 0,
            alive         = True,
            lineage_depth = 0,
        ))

    # ── Direction adjustment per mode ────────────────────────────────────────

    def _mode_bias(self, pos: np.ndarray, direction: np.ndarray) -> np.ndarray:
        p  = self.params
        d  = direction.copy()
        up = np.array([0.0, 1.0, 0.0])

        if p.mode == "tree":
            d += up * p.upward_bias
            radial = np.array([pos[0], 0.0, pos[2]])
            if np.linalg.norm(radial) > 1e-9:
                d += normalize(radial) * p.radial_bias

        elif p.mode == "coral":
            d += up * (0.6 * p.upward_bias)
            radial = pos.copy()
            if np.linalg.norm(radial) > 1e-9:
                d += normalize(radial) * max(p.radial_bias, 0.25)

        elif p.mode == "spiral":
            d += up * p.upward_bias
            xy = np.array([pos[0], 0.0, pos[2]])
            if np.linalg.norm(xy) > 1e-9:
                tangent = np.array([-xy[2], 0.0, xy[0]])
                d += normalize(tangent) * max(p.twist_strength, 0.40)
                d += normalize(xy)      * max(p.radial_bias,    0.15)
            else:
                d[0] += 0.15

        return normalize(d)

    def _apply_tropism(self, pos: np.ndarray, direction: np.ndarray) -> np.ndarray:
        if self.params.tropism_target is None:
            return direction
        toward = self.params.tropism_target - pos
        if np.linalg.norm(toward) < 1e-12:
            return direction
        return normalize(direction + normalize(toward) * 0.25)

    def _apply_noise(self, direction: np.ndarray) -> np.ndarray:
        noise = np.random.normal(size=3)
        noise = normalize(noise)
        return normalize(direction + noise * self.params.noise_strength)

    def _apply_collision(self, pos: np.ndarray, direction: np.ndarray) -> np.ndarray:
        p = self.params
        if not p.collision_avoidance or not self.segments:
            return direction

        repel        = np.zeros(3)
        sample_point = pos + direction * p.step_size

        for seg in self.segments[-500:]:
            dist = distance_point_to_segment(sample_point, seg.start, seg.end)
            if dist < p.collision_distance:
                midpoint = 0.5 * (seg.start + seg.end)
                away     = sample_point - midpoint
                if np.linalg.norm(away) > 1e-12:
                    strength = (p.collision_distance - dist) / p.collision_distance
                    repel   += normalize(away) * strength

        if np.linalg.norm(repel) > 1e-12:
            direction = normalize(direction + 0.8 * repel)

        return direction

    # ── Tip lifecycle ─────────────────────────────────────────────────────────

    def _should_kill(self, new_pos: np.ndarray, new_radius: float, depth: int) -> bool:
        if new_radius < self.params.min_radius:
            return True
        if depth >= self.params.max_depth:
            return True
        limit = self.params.kill_if_outside_radius
        if limit is not None and np.linalg.norm(new_pos - self.origin) > limit:
            return True
        return False

    def _grow_tip(self, tip: Tip, tip_index: int) -> List[Tip]:
        if not tip.alive:
            return []

        d = tip.direction.copy()
        d = self._mode_bias(tip.position, d)
        d = self._apply_tropism(tip.position, d)
        d = self._apply_noise(d)
        d = self._apply_collision(tip.position, d)

        start      = tip.position.copy()
        end        = start + d * self.params.step_size
        new_radius = tip.radius * self.params.taper

        if self._should_kill(end, new_radius, tip.lineage_depth):
            tip.alive = False
            return []

        self.segments.append(Segment(
            start     = start,
            end       = end,
            radius    = tip.radius,
            parent_id = tip_index,
        ))

        tip.position  = end
        tip.direction = d
        tip.radius    = new_radius
        tip.age      += 1

        spawned: List[Tip] = []

        alive_count = sum(1 for t in self.tips if t.alive) + len(spawned)
        can_branch  = (
            tip.lineage_depth < self.params.max_depth
            and alive_count < self.params.max_tips
        )

        if can_branch and self.rng.random() < self.params.branching_probability:
            ortho = orthogonal_vector(d)
            angle = math.radians(self.params.branch_angle_deg)

            if self.params.mode == "coral":
                angle *= 1.15
            elif self.params.mode == "spiral":
                angle *= 0.85

            dir1 = normalize(rotate_vector(d, ortho, angle))
            spawned.append(Tip(
                position      = end.copy(),
                direction     = dir1,
                radius        = max(new_radius * 0.85, self.params.min_radius),
                age           = 0,
                alive         = True,
                lineage_depth = tip.lineage_depth + 1,
            ))

            if self.rng.random() < self.params.split_probability:
                dir2 = normalize(rotate_vector(d, ortho, -angle))
                spawned.append(Tip(
                    position      = end.copy(),
                    direction     = dir2,
                    radius        = max(new_radius * 0.82, self.params.min_radius),
                    age           = 0,
                    alive         = True,
                    lineage_depth = tip.lineage_depth + 1,
                ))

        return spawned

    # ── Simulation loop ───────────────────────────────────────────────────────

    def step(self) -> None:
        new_tips: List[Tip] = []
        for idx, tip in list(enumerate(self.tips)):
            if not tip.alive:
                continue
            new_tips.extend(self._grow_tip(tip, idx))
        self.tips.extend(new_tips)

    def run(self) -> None:
        for _ in range(self.params.steps):
            if not any(t.alive for t in self.tips):
                break
            self.step()

    # ── Mesh output (requires PyVista) ────────────────────────────────────────

    def build_tube_mesh(self, sides: int = 6):
        if not _PYVISTA:
            raise ImportError("pyvista is required for mesh output.")
        if not self.segments:
            return pv.PolyData()

        n = len(self.segments)

        # Build all line segments as one PolyData, then tube in a single pass.
        # This is orders of magnitude faster than tubing each segment separately.
        points = np.empty((n * 2, 3), dtype=float)
        lines  = np.empty(n * 3,      dtype=int)

        for i, seg in enumerate(self.segments):
            points[i * 2]     = seg.start
            points[i * 2 + 1] = seg.end
            lines[i * 3]      = 2
            lines[i * 3 + 1]  = i * 2
            lines[i * 3 + 2]  = i * 2 + 1

        pd        = pv.PolyData()
        pd.points = points
        pd.lines  = lines

        radii                   = np.repeat(
            [max(s.radius, self.params.min_radius) for s in self.segments], 2
        )
        pd.point_data["radius"] = radii

        return pd.tube(scalars="radius", n_sides=sides, absolute=True)

    def build_tip_points(self):
        if not _PYVISTA:
            raise ImportError("pyvista is required for mesh output.")
        alive = [t.position for t in self.tips if t.alive]
        if not alive:
            return pv.PolyData()
        return pv.PolyData(np.array(alive))

    # ── Plain-Python geometry access ─────────────────────────────────────────

    def to_edge_list(self) -> List[Tuple[np.ndarray, np.ndarray]]:
        """Return segments as [(start, end), ...] — no PyVista needed."""
        return [(s.start, s.end) for s in self.segments]

    def to_dict(self) -> dict:
        """Serialisable dict for JSON export or API responses."""
        return {
            "mode":          self.params.mode,
            "segment_count": len(self.segments),
            "segments": [
                {
                    "x1": float(s.start[0]), "y1": float(s.start[1]), "z1": float(s.start[2]),
                    "x2": float(s.end[0]),   "y2": float(s.end[1]),   "z2": float(s.end[2]),
                    "radius":    float(s.radius),
                    "parent_id": s.parent_id if s.parent_id is not None else -1,
                }
                for s in self.segments
            ],
        }

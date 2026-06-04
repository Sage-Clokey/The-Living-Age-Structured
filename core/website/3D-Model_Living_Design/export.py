"""
export.py — Export generated structures to file formats.

Supported formats:
  - OBJ (tube mesh via PyVista)
  - OBJ wireframe (lightweight, lines only — no PyVista needed)
  - JSON (segment list for browser/API consumption)
  - STL (solid mesh via PyVista)

Usage:
    engine = MorphogenesisEngine(params)
    engine.run()

    export_obj(engine, "outputs/tree.obj")
    export_wireframe_obj(engine, "outputs/tree_wire.obj")
    export_json(engine, "outputs/tree.json")
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from engine import MorphogenesisEngine


# ── OBJ tube mesh (requires PyVista) ─────────────────────────────────────────

def export_obj(
    engine:   MorphogenesisEngine,
    path:     str = "outputs/structure.obj",
    sides:    int = 8,
) -> str:
    """
    Export a solid tube-mesh OBJ.
    Each segment becomes a tube polygon, merged into one mesh.
    Requires PyVista.
    """
    try:
        import pyvista as pv
    except ImportError:
        raise ImportError("pyvista is required for OBJ mesh export.")

    mesh = engine.build_tube_mesh(sides=sides)
    if mesh.n_points == 0:
        raise ValueError("Engine has no geometry to export.")

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    mesh.save(str(p))
    return str(p.resolve())


def export_stl(
    engine: MorphogenesisEngine,
    path:   str = "outputs/structure.stl",
    sides:  int = 8,
) -> str:
    """Export a solid STL mesh. Requires PyVista."""
    try:
        import pyvista as pv
    except ImportError:
        raise ImportError("pyvista is required for STL export.")

    mesh = engine.build_tube_mesh(sides=sides)
    if mesh.n_points == 0:
        raise ValueError("Engine has no geometry to export.")

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    mesh.save(str(p))
    return str(p.resolve())


# ── OBJ wireframe (no PyVista) ────────────────────────────────────────────────

def export_wireframe_obj(
    engine: MorphogenesisEngine,
    path:   str = "outputs/structure_wire.obj",
) -> str:
    """
    Lightweight line-based OBJ.
    No tubes — just L (line) primitives from each segment.
    Works without PyVista; compatible with Blender import.
    """
    lines:  list[str] = [
        "# Living Systems Design Lab — Wireframe Export",
        f"# mode: {engine.params.mode}",
        f"# segments: {len(engine.segments)}",
        "",
    ]
    vert_idx = 1

    for seg in engine.segments:
        s, e = seg.start, seg.end
        lines.append(f"v {s[0]:.6f} {s[1]:.6f} {s[2]:.6f}")
        lines.append(f"v {e[0]:.6f} {e[1]:.6f} {e[2]:.6f}")
        lines.append(f"l {vert_idx} {vert_idx + 1}")
        vert_idx += 2

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(p.resolve())


# ── JSON ──────────────────────────────────────────────────────────────────────

def export_json(
    engine:  MorphogenesisEngine,
    path:    str = "outputs/structure.json",
    indent:  int = 2,
) -> str:
    """
    Serialise the segment list to JSON.
    The browser viewer and API both consume this format.
    """
    data = engine.to_dict()

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=indent), encoding="utf-8")
    return str(p.resolve())


# ── CSV (point cloud) ─────────────────────────────────────────────────────────

def export_csv(
    engine: MorphogenesisEngine,
    path:   str = "outputs/structure.csv",
) -> str:
    """
    Export segment midpoints + radius as a CSV point cloud.
    Useful for downstream analysis or Blender geometry nodes.
    """
    rows = ["x,y,z,radius,depth"]
    for seg in engine.segments:
        mid = 0.5 * (seg.start + seg.end)
        depth = seg.parent_id if seg.parent_id is not None else 0
        rows.append(
            f"{mid[0]:.6f},{mid[1]:.6f},{mid[2]:.6f},"
            f"{seg.radius:.6f},{depth}"
        )

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return str(p.resolve())

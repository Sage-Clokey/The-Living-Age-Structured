"""
viewer.py — PyVista visualisation for the morphogenesis engine.

Two modes:
  show()    — render the final completed structure
  animate() — step through growth in real time

Colour scheme mirrors the website: gold trunk → green canopy.

Rendering strategy:
  - build_lines_polydata() is instant (just numpy arrays)
  - Tubes are generated in one VTK pass via build_tube_mesh()
  - If tube generation fails for any reason, falls back to line rendering
"""

from __future__ import annotations

import numpy as np

try:
    import pyvista as pv
    _PYVISTA = True
except ImportError:
    _PYVISTA = False

from engine import MorphogenesisEngine
from presets import GrowthParams


_BG     = "#07090a"
_CANOPY = "#7a9e7e"
_TIPS   = "#4aaa5a"
_DIM    = "#1a2a1a"


def _require_pyvista() -> None:
    if not _PYVISTA:
        raise ImportError(
            "pyvista is required for visualisation.\n"
            "Install it with:  pip install pyvista"
        )


def _build_lines(engine: MorphogenesisEngine) -> pv.PolyData:
    """Build a lightweight line PolyData (no tubes). Instant even at 10k segs."""
    n      = len(engine.segments)
    points = np.empty((n * 2, 3), dtype=float)
    lines  = np.empty(n * 3,      dtype=int)

    for i, seg in enumerate(engine.segments):
        points[i * 2]     = seg.start
        points[i * 2 + 1] = seg.end
        lines[i * 3]      = 2
        lines[i * 3 + 1]  = i * 2
        lines[i * 3 + 2]  = i * 2 + 1

    pd        = pv.PolyData()
    pd.points = points
    pd.lines  = lines
    return pd


def show(
    engine: MorphogenesisEngine,
    title:  str = "Living Structure",
    tubes:  bool = True,
    sides:  int  = 6,
) -> None:
    """
    Render the completed structure in an interactive PyVista window.

    Parameters
    ----------
    tubes : bool
        True  → render as solid tubes (slower build, better look)
        False → render as lines (instant, good for inspection)
    """
    _require_pyvista()

    print(f"  building mesh ({len(engine.segments)} segments)...", end=" ", flush=True)

    geo = None
    if tubes:
        try:
            geo = engine.build_tube_mesh(sides=sides)
            if geo.n_points == 0:
                geo = None
        except Exception as e:
            print(f"tube build failed ({e}), falling back to lines")
            geo = None

    if geo is None:
        geo   = _build_lines(engine)
        tubes = False

    print("done")

    tips = engine.build_tip_points()

    plotter = pv.Plotter(window_size=(1200, 900))
    plotter.set_background(_BG)
    plotter.add_title(title, font_size=12, color=_CANOPY)

    if geo.n_points > 0:
        if tubes:
            plotter.add_mesh(
                geo,
                color          = _CANOPY,
                smooth_shading = True,
                ambient        = 0.15,
                diffuse        = 0.85,
            )
        else:
            plotter.add_mesh(geo, color=_CANOPY, line_width=1.5)

    if tips.n_points > 0:
        plotter.add_mesh(
            tips,
            render_points_as_spheres = True,
            point_size               = 8,
            color                    = _TIPS,
        )

    plotter.add_axes(color=_DIM)
    plotter.show_grid(color=_DIM)

    print("  opening window — close it to continue")
    plotter.show()


def animate(
    params:  GrowthParams,
    every_n: int = 4,
) -> None:
    """Step through growth in real time using line rendering (fast)."""
    _require_pyvista()

    engine = MorphogenesisEngine(params)

    plotter = pv.Plotter(window_size=(1200, 900))
    plotter.set_background(_BG)
    plotter.add_title(f"Growing: {params.mode}", font_size=12, color=_CANOPY)
    plotter.add_axes(color=_DIM)
    plotter.show_grid(color=_DIM)

    line_actor = None
    tip_actor  = None

    plotter.show(auto_close=False, interactive_update=True)

    for i in range(params.steps):
        if not any(t.alive for t in engine.tips):
            break
        engine.step()

        if i % every_n == 0 or i == params.steps - 1:
            lines = _build_lines(engine)
            tips  = engine.build_tip_points()

            if line_actor is not None:
                plotter.remove_actor(line_actor)
            if tip_actor is not None:
                plotter.remove_actor(tip_actor)

            if lines.n_points > 0:
                line_actor = plotter.add_mesh(lines, color=_CANOPY, line_width=1.5)
            if tips.n_points > 0:
                tip_actor = plotter.add_mesh(
                    tips,
                    render_points_as_spheres=True,
                    point_size=8,
                    color=_TIPS,
                )

            plotter.render()

    plotter.close()

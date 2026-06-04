"""
morpho/constraints.py

Hard and soft spatial constraints applied to the simulation state each
timestep.  Currently implements a simple AABB bounding box that reflects
cells back inside the volume.
"""

from __future__ import annotations

import numpy as np
from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from morpho.state import SimulationState


def apply_bounds(
    state: "SimulationState",
    bounds: Tuple[np.ndarray, np.ndarray],
) -> None:
    """
    Reflect cells that have drifted outside the bounding box back inside.

    Uses elastic reflection: the offending position component is mirrored
    and the corresponding velocity component is negated (with a damping
    factor to avoid perpetual bouncing).

    Parameters
    ----------
    state : SimulationState
        The current simulation state (modified in-place).
    bounds : (min_corner, max_corner)
        Two (3,) arrays defining the AABB.
    """
    lo, hi = bounds
    lo = np.asarray(lo, dtype=float)
    hi = np.asarray(hi, dtype=float)
    damping: float = 0.5

    for cell in state.cells:
        for axis in range(3):
            # Lower wall
            if cell.position[axis] - cell.radius < lo[axis]:
                cell.position[axis] = lo[axis] + cell.radius
                cell.velocity[axis] = abs(cell.velocity[axis]) * damping

            # Upper wall
            if cell.position[axis] + cell.radius > hi[axis]:
                cell.position[axis] = hi[axis] - cell.radius
                cell.velocity[axis] = -abs(cell.velocity[axis]) * damping


def apply_gravity(state: "SimulationState", g: float = -0.01) -> None:
    """
    Apply a downward gravitational acceleration to all cells.

    Parameters
    ----------
    state : SimulationState
    g : float
        Gravitational acceleration (negative = downward in Y).
    """
    for cell in state.cells:
        cell.velocity[1] += g


def apply_crown_envelope(
    state: "SimulationState",
    envelope_fn,
    y_base: float = 0.0,
    y_height: float = 20.0,
) -> None:
    """
    Confine cells within a rotationally symmetric crown envelope.

    Any cell whose XZ distance from the Y-axis exceeds the envelope radius
    at its height is snapped back to the boundary and its outward velocity
    is killed.  This shapes the simulation into species-specific silhouettes
    (conical for conifers, spheroidal for broadleaves, etc.).

    Parameters
    ----------
    state : SimulationState
    envelope_fn : callable (h_norm: float) -> float
        Maximum allowed XZ radius at normalised height h_norm ∈ [0, 1].
        Derived from tree_data.make_envelope_fn() or make_plot_envelope_fn().
    y_base : float
        Y coordinate of the crown base (usually 0.0).
    y_height : float
        Total crown height in simulation units.
    """
    for cell in state.cells:
        h_norm = (cell.position[1] - y_base) / y_height
        h_norm = max(0.0, min(1.0, h_norm))

        max_r = envelope_fn(h_norm)
        # Never squeeze tighter than the cell's own radius
        max_r = max(max_r, cell.radius * 0.6)

        xz = cell.position[[0, 2]]
        dist = float(np.linalg.norm(xz))

        if dist > max_r and dist > 1e-8:
            cell.position[[0, 2]] = xz * (max_r / dist)
            cell.velocity[[0, 2]] *= 0.08   # kill outward velocity

        # Hard ceiling: no cells above the crown apex
        y_top = y_base + y_height
        if cell.position[1] > y_top:
            cell.position[1] = y_top
            if cell.velocity[1] > 0:
                cell.velocity[1] *= -0.1


def apply_ground_plane(state: "SimulationState", y_floor: float = 0.0) -> None:
    """
    Prevent cells from passing through a horizontal ground plane at y_floor.

    Parameters
    ----------
    state : SimulationState
    y_floor : float
        Y-coordinate of the ground plane.
    """
    for cell in state.cells:
        if cell.position[1] - cell.radius < y_floor:
            cell.position[1] = y_floor + cell.radius
            if cell.velocity[1] < 0:
                cell.velocity[1] = 0.0

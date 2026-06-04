"""
morpho/utils.py

General-purpose mathematical helpers used throughout the simulation.
"""

from __future__ import annotations

import numpy as np
from typing import Tuple


def normalise(v: np.ndarray, fallback: np.ndarray | None = None) -> np.ndarray:
    """
    Return the unit vector of *v*.

    If *v* is near-zero, returns *fallback* (default: [1, 0, 0]).
    """
    norm = np.linalg.norm(v)
    if norm < 1e-10:
        return fallback if fallback is not None else np.array([1.0, 0.0, 0.0])
    return v / norm


def clamp(value: float, lo: float, hi: float) -> float:
    """Clamp *value* to [lo, hi]."""
    return max(lo, min(hi, value))


def random_unit_vector() -> np.ndarray:
    """Return a uniformly random unit vector on the sphere."""
    v = np.random.randn(3)
    return normalise(v)


def distance(a: np.ndarray, b: np.ndarray) -> float:
    """Euclidean distance between two 3-D points."""
    return float(np.linalg.norm(a - b))


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation: a + t*(b-a)."""
    return a + t * (b - a)


def aabb(
    positions: np.ndarray,
    radii: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute the axis-aligned bounding box of a set of spheres.

    Parameters
    ----------
    positions : np.ndarray, shape (N, 3)
    radii : np.ndarray, shape (N,)

    Returns
    -------
    (min_corner, max_corner) : Tuple[np.ndarray, np.ndarray]
    """
    r = radii[:, np.newaxis]
    mins = (positions - r).min(axis=0)
    maxs = (positions + r).max(axis=0)
    return mins, maxs


def build_spatial_grid(
    positions: np.ndarray,
    cell_size: float,
) -> dict:
    """
    Build a simple hash-grid for O(N) neighbour lookups.

    Parameters
    ----------
    positions : np.ndarray, shape (N, 3)
        Cell positions.
    cell_size : float
        Grid voxel edge length (typically 2 × max_radius).

    Returns
    -------
    dict mapping (ix, iy, iz) → list of cell indices.
    """
    grid: dict = {}
    for idx, pos in enumerate(positions):
        key = tuple((pos / cell_size).astype(int))
        grid.setdefault(key, []).append(idx)
    return grid


def get_neighbours_grid(
    idx: int,
    positions: np.ndarray,
    grid: dict,
    cell_size: float,
) -> list:
    """
    Return indices of cells in neighbouring voxels (27-voxel search).

    Parameters
    ----------
    idx : int
        Index of the query cell.
    positions : np.ndarray, shape (N, 3)
    grid : dict
        Output of build_spatial_grid.
    cell_size : float

    Returns
    -------
    list of int
        Neighbour indices (excluding idx itself).
    """
    pos = positions[idx]
    base = (pos / cell_size).astype(int)
    neighbours = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                key = (base[0] + dx, base[1] + dy, base[2] + dz)
                for j in grid.get(key, []):
                    if j != idx:
                        neighbours.append(j)
    return neighbours

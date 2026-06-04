"""
morpho/forces.py

Physical force functions between cells.

All functions return a 3-D numpy force vector that should be applied to
the *first* cell argument (cell_a).  The reaction force on cell_b is
simply the negation.
"""

from __future__ import annotations

import numpy as np
from morpho.cell import Cell


# ------------------------------------------------------------------
# Repulsion
# ------------------------------------------------------------------

def compute_repulsion(cell_a: Cell, cell_b: Cell) -> np.ndarray:
    """
    Hertz-like soft repulsion between overlapping cells.

    When two cells overlap (centre-centre distance < sum of radii) a
    repulsive force pushes them apart.  The force magnitude scales with
    the overlap depth and the geometric mean of the two stiffnesses.

    Parameters
    ----------
    cell_a, cell_b : Cell
        The pair of cells to evaluate.

    Returns
    -------
    np.ndarray, shape (3,)
        Force vector acting ON cell_a (pointing away from cell_b).
    """
    delta: np.ndarray = cell_a.position - cell_b.position
    distance: float = float(np.linalg.norm(delta))

    contact_dist: float = cell_a.radius + cell_b.radius

    if distance < 1e-8:
        # Cells are coincident — push in a random direction
        direction = np.random.randn(3)
        direction /= np.linalg.norm(direction)
        overlap = contact_dist
    elif distance >= contact_dist:
        # No overlap
        return np.zeros(3, dtype=float)
    else:
        direction = delta / distance
        overlap = contact_dist - distance

    # Stiffness as geometric mean
    k: float = np.sqrt(cell_a.stiffness * cell_b.stiffness)
    force_magnitude: float = k * overlap

    return direction * force_magnitude


# ------------------------------------------------------------------
# Adhesion
# ------------------------------------------------------------------

def compute_adhesion(cell_a: Cell, cell_b: Cell) -> np.ndarray:
    """
    Short-range adhesion that pulls cells together when they are close
    but not yet fully overlapping.

    The adhesion force acts in the range
    [contact_dist, contact_dist * adhesion_range_factor].

    Parameters
    ----------
    cell_a, cell_b : Cell
        The pair of cells to evaluate.

    Returns
    -------
    np.ndarray, shape (3,)
        Force vector acting ON cell_a (pointing toward cell_b).
    """
    adhesion_range_factor: float = 1.5  # adhesion active up to 1.5× contact dist

    delta: np.ndarray = cell_b.position - cell_a.position
    distance: float = float(np.linalg.norm(delta))

    contact_dist: float = cell_a.radius + cell_b.radius
    max_dist: float = contact_dist * adhesion_range_factor

    if distance < 1e-8 or distance < contact_dist or distance > max_dist:
        return np.zeros(3, dtype=float)

    direction = delta / distance

    # Linear fall-off from contact surface to max_dist
    gap: float = distance - contact_dist
    range_width: float = max_dist - contact_dist
    falloff: float = 1.0 - gap / range_width

    # Adhesion strength as geometric mean
    a: float = np.sqrt(cell_a.adhesion * cell_b.adhesion)
    force_magnitude: float = a * falloff

    return direction * force_magnitude


# ------------------------------------------------------------------
# Noise
# ------------------------------------------------------------------

def compute_noise(cell: Cell, noise_strength: float) -> np.ndarray:
    """
    Isotropic Brownian noise applied to a single cell.

    Parameters
    ----------
    cell : Cell
        The cell receiving the noise.
    noise_strength : float
        RMS magnitude of the noise force.

    Returns
    -------
    np.ndarray, shape (3,)
        Random force vector.
    """
    return np.random.randn(3) * noise_strength


# ------------------------------------------------------------------
# Anisotropy bias
# ------------------------------------------------------------------

def compute_anisotropy(
    cell: Cell,
    anisotropy_vector: np.ndarray,
    anisotropy_strength: float,
) -> np.ndarray:
    """
    Directional bias force that nudges cells toward a preferred axis.

    Parameters
    ----------
    cell : Cell
        Target cell (unused currently, reserved for future per-cell bias).
    anisotropy_vector : np.ndarray, shape (3,)
        Preferred direction (need not be normalised).
    anisotropy_strength : float
        Magnitude of the bias force.

    Returns
    -------
    np.ndarray, shape (3,)
        Bias force vector.
    """
    norm: float = float(np.linalg.norm(anisotropy_vector))
    if norm < 1e-8 or anisotropy_strength < 1e-8:
        return np.zeros(3, dtype=float)

    direction = anisotropy_vector / norm
    return direction * anisotropy_strength

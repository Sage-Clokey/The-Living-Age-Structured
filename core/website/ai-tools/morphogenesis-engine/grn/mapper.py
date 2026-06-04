"""
grn/mapper.py

Maps GRN gene-activity levels to cell physics parameters.

This is the key bridge between the regulatory layer and the physics
simulation.  Each function takes a GRNState and writes directly into
a Cell object or returns a derived value.

Mapping design
--------------
All mappings are monotone and inspectable — no black-box ML.  Each
relationship has a biological rationale:

  growth gene   → growth_rate, division_radius
  branch gene   → division_radius  (high branch → divide sooner / smaller)
  adhesion gene → adhesion         (E-cadherin analog)
  diff gene     → stiffness        (mature cells stiffen like ECM)
  polarity gene → anisotropy bias  (PCP pathway → directional growth)
"""

from __future__ import annotations

import numpy as np
from grn.grn import GRNState


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _sigmoid(x: float, center: float = 0.5, sharpness: float = 8.0) -> float:
    """Smooth threshold function mapping any real → (0, 1)."""
    return float(1.0 / (1.0 + np.exp(-sharpness * (x - center))))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def apply_grn_to_cell(cell, grn: GRNState) -> None:
    """
    Write GRN outputs into cell physics parameters.

    Called once per cell per simulation step, before the physics update.
    Overwrites the cell's current parameter values with GRN-derived ones.

    Parameter mappings
    ------------------
    growth_rate
        Base rate scaled by growth gene; reduced when diff is high
        (differentiated cells grow slowly like mature tissue).

    division_radius
        Threshold at which the cell divides.  High branch gene → divides
        at a smaller radius (more frequent, smaller daughters).

    stiffness
        Low at birth; increases with diff (ECM deposition / cell stiffening).

    adhesion
        Directly proportional to adhesion gene (cadherin-like program).
    """
    # Growth rate: [0.02, 0.10], reduced strongly by differentiation
    cell.growth_rate = (0.02 + grn.growth * 0.08) * (1.0 - grn.diff * 0.75)

    # Division radius: [0.45, 1.0], reduced by high branch gene
    branch_suppression = 1.0 - grn.branch * 0.55
    cell.division_radius = float(np.clip(0.45 + branch_suppression * 0.55, 0.4, 1.05))

    # Stiffness: [0.6, 2.5], rises sharply with differentiation
    cell.stiffness = 0.6 + grn.diff * 1.9

    # Adhesion: [0.1, 1.8]
    cell.adhesion = 0.1 + grn.adhesion * 1.7


def grn_anisotropy(grn: GRNState) -> np.ndarray:
    """
    Return a 3-D bias vector derived from the polarity gene.

    High polarity → strong upward bias (like apical-basal polarity in
    epithelial sheets, or gravitropic response in plants).

    The returned vector is not normalised — its magnitude encodes strength.
    The caller accumulates these across all cells and uses the mean.
    """
    strength = grn.polarity * 0.12
    return np.array([0.0, 1.0, 0.0], dtype=float) * strength


def branching_probability(grn: GRNState) -> float:
    """
    Return the per-step probability of a branching event for this cell.

    High branch gene → higher probability.
    High diff gene   → strongly suppressed (mature cells don't branch).
    """
    raw = _sigmoid(grn.branch, center=0.4, sharpness=7.0) * 0.018
    return float(raw * (1.0 - grn.diff))

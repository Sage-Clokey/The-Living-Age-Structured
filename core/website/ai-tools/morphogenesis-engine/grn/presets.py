"""
grn/presets.py

Named GRN configurations for common morphogenetic programs.

Each preset returns a (GRNState, GrowthProgram) pair.

GRNState  defines the initial per-cell gene activities and the
          regulatory dynamics that will evolve during simulation.

GrowthProgram  sets the global physics-level defaults used by the
               existing Simulation engine.  The GRN layer overrides
               cell parameters each step, so the program acts as a
               starting baseline rather than a fixed constraint.

Presets
-------
tree_grn    Upward-biased columnar growth with moderate branching.
            High polarity → strong apical dominance.

coral_grn   Outward-spreading radial branching with high noise.
            High branch + low polarity → chaotic reef-like geometry.

spiral_grn  Tight helical tower.
            High polarity + very low branch → single organised column.

from_dict   Build a (GRNState, GrowthProgram) from a plain Python dict,
            suitable for JSON input from a web API or CLI.
"""

from __future__ import annotations

import numpy as np

from morpho.program import GrowthProgram
from grn.grn import GRNState


# ---------------------------------------------------------------------------
# Named presets
# ---------------------------------------------------------------------------

def tree_grn() -> tuple[GRNState, GrowthProgram]:
    """Strong upward growth, moderate branching, high polarity."""
    grn = GRNState(
        growth=0.70,
        branch=0.30,
        adhesion=0.50,
        polarity=0.85,
        diff=0.0,
    )
    program = GrowthProgram(
        growth_rate_multiplier=1.2,
        stiffness_multiplier=1.3,
        adhesion_multiplier=0.8,
        division_size_multiplier=0.90,
        noise_strength=0.012,
        anisotropy_vector=np.array([0.0, 1.0, 0.0]),
        anisotropy_strength=0.08,
    )
    return grn, program


def coral_grn() -> tuple[GRNState, GrowthProgram]:
    """Outward radial branching, high noise, low directional bias."""
    grn = GRNState(
        growth=0.60,
        branch=0.70,
        adhesion=0.40,
        polarity=0.30,
        diff=0.0,
    )
    program = GrowthProgram(
        growth_rate_multiplier=1.0,
        stiffness_multiplier=0.85,
        adhesion_multiplier=1.25,
        division_size_multiplier=0.72,
        noise_strength=0.042,
        anisotropy_vector=np.array([0.0, 0.4, 0.0]),
        anisotropy_strength=0.025,
    )
    return grn, program


def spiral_grn() -> tuple[GRNState, GrowthProgram]:
    """Tight helical column, very low branching, minimal noise."""
    grn = GRNState(
        growth=0.65,
        branch=0.12,
        adhesion=0.65,
        polarity=0.92,
        diff=0.0,
    )
    program = GrowthProgram(
        growth_rate_multiplier=1.1,
        stiffness_multiplier=1.6,
        adhesion_multiplier=1.5,
        division_size_multiplier=1.10,
        noise_strength=0.006,
        anisotropy_vector=np.array([0.0, 1.0, 0.0]),
        anisotropy_strength=0.11,
    )
    return grn, program


# ---------------------------------------------------------------------------
# Generic dict → (GRNState, GrowthProgram)
# ---------------------------------------------------------------------------

def from_dict(d: dict) -> tuple[GRNState, GrowthProgram]:
    """
    Build a (GRNState, GrowthProgram) from a plain dictionary.

    Expected keys (all optional, defaults shown):
      growth              0.5   [0–1]
      branch              0.3   [0–1]
      adhesion            0.5   [0–1]
      polarity            0.6   [0–1]
      diff                0.0   [0–1]
      anisotropy_strength 0.06

    The GrowthProgram values are derived from the GRN values so that
    the physics baseline is consistent with the regulatory state.

    Example
    -------
    >>> grn, prog = from_dict({"growth": 0.8, "branch": 0.6, "polarity": 0.4})
    """
    grn = GRNState(
        growth=float(d.get("growth",   0.5)),
        branch=float(d.get("branch",   0.3)),
        adhesion=float(d.get("adhesion", 0.5)),
        polarity=float(d.get("polarity", 0.6)),
        diff=float(d.get("diff",     0.0)),
    )

    aniso_str = float(d.get("anisotropy_strength", 0.06))

    program = GrowthProgram(
        growth_rate_multiplier  = 0.6 + grn.growth   * 1.0,
        stiffness_multiplier    = 0.7 + grn.diff      * 1.5,
        adhesion_multiplier     = 0.3 + grn.adhesion  * 1.5,
        division_size_multiplier= 1.2 - grn.branch    * 0.6,
        noise_strength          = 0.05 - grn.polarity * 0.04,
        anisotropy_vector       = np.array([0.0, 1.0, 0.0]),
        anisotropy_strength     = grn.polarity * aniso_str,
    )

    return grn, program


# ---------------------------------------------------------------------------
# Registry for CLI / API lookup
# ---------------------------------------------------------------------------

PRESETS = {
    "tree":   tree_grn,
    "coral":  coral_grn,
    "spiral": spiral_grn,
}

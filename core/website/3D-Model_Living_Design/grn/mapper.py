"""
grn/mapper.py — Map GRN regulatory state to GrowthParams.

This is the key modelling move: GRN outputs become simulation parameters
rather than fixed constants.

Mapping:
    growth gene      → step_size   (how fast tips advance)
    branch gene      → branching_probability
    adhesion gene    → taper       (how well structure holds together)
    polarity gene    → upward_bias (directional preference)
    differentiation  → max_depth   (tips become terminal as cells mature)

Each mapping is a linear or sigmoid rescaling centred on the base preset value,
so a GRN starting from neutral (all genes = 0.5) reproduces the base preset.
"""

from __future__ import annotations

import copy
import numpy as np

from .grn  import GRNState
from presets import GrowthParams


def grn_to_params(state: GRNState, base: GrowthParams) -> GrowthParams:
    """
    Return a new GrowthParams derived from base by applying GRN state.

    Parameters
    ----------
    state : current regulatory state of the organism
    base  : the preset GrowthParams to modify

    Returns
    -------
    A new GrowthParams — base is not mutated.
    """
    p = copy.deepcopy(base)

    # growth gene → step size (neutral 0.5 → 1× base; range ~0.5×–1.5×)
    p.step_size = float(
        np.clip(base.step_size * (0.5 + state.growth), 0.05, 0.8)
    )

    # branch gene → branching probability (neutral 0.5 → ~base value)
    p.branching_probability = float(
        np.clip(base.branching_probability * (0.2 + 2.4 * state.branch), 0.01, 0.45)
    )

    # adhesion gene → taper (high adhesion = slow taper = thicker structure)
    p.taper = float(
        np.clip(0.970 + 0.025 * state.adhesion, 0.92, 0.999)
    )

    # polarity gene → upward bias (neutral 0.5 → base; range ~0.3×–1.7×)
    p.upward_bias = float(
        np.clip(base.upward_bias * (0.3 + 1.4 * state.polarity), 0.0, 1.8)
    )

    # differentiation → max_depth (mature cells become terminal sooner)
    p.max_depth = max(2, int(base.max_depth * (1.0 - 0.6 * state.differentiation)))

    return p

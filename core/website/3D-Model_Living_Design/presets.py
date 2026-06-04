"""
presets.py — Growth parameter definitions for the Living Systems Design Lab.

GrowthParams holds every tunable variable for the morphogenesis engine.
The three preset functions (tree, coral, spiral) set sensible defaults
for each biological archetype.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np


@dataclass
class GrowthParams:
    # ── Identity ──────────────────────────────────────────────────────────────
    mode: str = "tree"          # tree | coral | spiral

    # ── Simulation budget ─────────────────────────────────────────────────────
    steps: int     = 300
    step_size: float = 0.25
    max_tips: int  = 128
    max_depth: int = 8
    seed: int      = 42

    # ── Directional bias ──────────────────────────────────────────────────────
    upward_bias: float    = 0.70   # tendency toward +Y
    radial_bias: float    = 0.00   # tendency away from origin (XZ plane)
    twist_strength: float = 0.00   # tangential twist around Y axis

    # ── Noise ─────────────────────────────────────────────────────────────────
    noise_strength: float = 0.20

    # ── Branching ─────────────────────────────────────────────────────────────
    branching_probability: float = 0.08
    branch_angle_deg: float      = 28.0
    split_probability: float     = 0.50  # chance of two-child split vs. one

    # ── Geometry ──────────────────────────────────────────────────────────────
    taper: float          = 0.985   # radius shrink per step
    min_radius: float     = 0.015
    initial_radius: float = 0.080

    # ── Collision avoidance ───────────────────────────────────────────────────
    collision_avoidance: bool   = True
    collision_distance: float   = 0.12

    # ── Bounds ────────────────────────────────────────────────────────────────
    kill_if_outside_radius: Optional[float] = None

    # ── Tropism ───────────────────────────────────────────────────────────────
    tropism_target: Optional[np.ndarray] = None  # optional attractor point


# ── Preset factories ──────────────────────────────────────────────────────────

def tree() -> GrowthParams:
    """Strong upward growth, moderate branching, trunk-to-canopy taper."""
    return GrowthParams(
        mode                  = "tree",
        steps                 = 320,
        step_size             = 0.22,
        branching_probability = 0.09,
        max_tips              = 80,
        max_depth             = 8,
        upward_bias           = 0.95,
        radial_bias           = 0.08,
        twist_strength        = 0.00,
        noise_strength        = 0.10,
        branch_angle_deg      = 24.0,
        split_probability     = 0.45,
        taper                 = 0.986,
        min_radius            = 0.012,
        initial_radius        = 0.085,
        collision_avoidance   = True,
        collision_distance    = 0.10,
        seed                  = 42,
    )


def coral() -> GrowthParams:
    """Outward radial spread, high noise, dense branching, reef-like density."""
    return GrowthParams(
        mode                  = "coral",
        steps                 = 420,
        step_size             = 0.16,
        branching_probability = 0.14,
        max_tips              = 150,
        max_depth             = 10,
        upward_bias           = 0.55,
        radial_bias           = 0.35,
        twist_strength        = 0.00,
        noise_strength        = 0.28,
        branch_angle_deg      = 34.0,
        split_probability     = 0.65,
        taper                 = 0.989,
        min_radius            = 0.010,
        initial_radius        = 0.055,
        collision_avoidance   = True,
        collision_distance    = 0.08,
        seed                  = 42,
    )


def shelter() -> GrowthParams:
    """Vaulted dome — trunk rises then arches outward at wide angles, open space beneath."""
    return GrowthParams(
        mode                  = "tree",
        steps                 = 400,
        step_size             = 0.17,
        branching_probability = 0.16,
        max_tips              = 220,
        max_depth             = 10,
        upward_bias           = 0.55,
        radial_bias           = 1.00,
        twist_strength        = 0.00,
        noise_strength        = 0.13,
        branch_angle_deg      = 52.0,
        split_probability     = 0.72,
        taper                 = 0.990,
        min_radius            = 0.009,
        initial_radius        = 0.080,
        collision_avoidance   = True,
        collision_distance    = 0.08,
        seed                  = 42,
    )


def spiral() -> GrowthParams:
    """Helical upward growth with tangential twist, architectural feel."""
    return GrowthParams(
        mode                  = "spiral",
        steps                 = 340,
        step_size             = 0.18,
        branching_probability = 0.05,
        max_tips              = 48,
        max_depth             = 6,
        upward_bias           = 0.80,
        radial_bias           = 0.22,
        twist_strength        = 0.72,
        noise_strength        = 0.08,
        branch_angle_deg      = 18.0,
        split_probability     = 0.25,
        taper                 = 0.992,
        min_radius            = 0.012,
        initial_radius        = 0.070,
        collision_avoidance   = True,
        collision_distance    = 0.10,
        seed                  = 42,
    )

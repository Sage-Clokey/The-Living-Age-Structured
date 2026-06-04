"""
config.py — Simulation parameters for the coral morphogenesis engine.

All tunable knobs live here. Edit this file to explore different coral
morphologies without touching simulation logic.

Biological mapping
------------------
step_size         : apical extension rate — how far a tip grows per iteration
branch_probability: probability a lateral branch buds off each step
turn_noise        : stochastic angular deviation (models growth-cone noise)
upward_bias       : phototropic / gravitropic pull toward +Y axis
min_separation    : minimum node spacing (inter-branch competition / collision)
max_nodes         : hard cap on total nodes (simulation terminates here)
random_seed       : fixed seed for reproducibility; None = fully random
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SimConfig:
    """Dataclass holding all coral simulation parameters."""

    # ------------------------------------------------------------------
    # Growth geometry
    # ------------------------------------------------------------------
    step_size: float = 0.28
    """Apical extension distance per iteration (world units)."""

    branch_probability: float = 0.10
    """Probability [0–1] of spawning a lateral branch at each growth step."""

    turn_noise: float = 0.32
    """Magnitude of random directional noise applied each step (radians-ish).
    Higher → more tortuous, chaotic branches. Lower → straighter columns."""

    upward_bias: float = 0.55
    """Strength of phototropic / gravitropic pull toward +Y.
    0.0 = isotropic blob. 1.0+ = aggressively columnar."""

    min_separation: float = 0.22
    """Minimum allowed distance between any two nodes (collision avoidance).
    Prevents self-intersection; lower values allow denser packing."""

    branch_angle: float = 0.55
    """Lateral branch deflection angle in radians (~31°).
    Increase for more splayed fans; decrease for tighter corymbs."""

    # ------------------------------------------------------------------
    # Simulation limits
    # ------------------------------------------------------------------
    max_nodes: int = 800
    """Simulation terminates once this many nodes are grown."""

    max_tips: int = 80
    """Maximum concurrent active tips. Prevents exponential tip explosion."""

    initial_tips: int = 3
    """Number of seed tips radiating from the root node at t=0."""

    max_retries: int = 3
    """Times a blocked tip re-randomises its direction before dying.
    Higher → coral fills denser; lower → branches terminate earlier."""

    # ------------------------------------------------------------------
    # Visual morphology
    # ------------------------------------------------------------------
    base_radius: float = 0.16
    """Tube radius at root depth (world units). Thickest part of the coral."""

    radius_taper: float = 0.935
    """Multiplicative radius reduction per depth level.
    0.9 = aggressive taper. 0.99 = nearly uniform thickness."""

    # ------------------------------------------------------------------
    # Animation
    # ------------------------------------------------------------------
    steps_per_frame: int = 2
    """Simulation steps computed per visual frame update.
    Higher → faster growth animation but choppier visual."""

    callback_interval_ms: int = 50
    """Milliseconds between animation frame callbacks (~20 fps at 50ms)."""

    # ------------------------------------------------------------------
    # Reproducibility
    # ------------------------------------------------------------------
    random_seed: int = 42
    """NumPy random seed. Change to explore different growth patterns."""

"""
grn/presets.py — Pre-built GRN weight matrices.

Each preset captures a different developmental strategy.

Gene order: [growth, branch, adhesion, polarity, differentiation]
Row i = how genes 0–4 combine to activate gene i.

Positive weight  → activation
Negative weight  → repression
"""

from __future__ import annotations

import numpy as np
from .grn import GRNNetwork


def development_grn() -> GRNNetwork:
    """
    Classic developmental GRN.

    Dynamics:
      - Growth activates branching (auxin-like positive feedback)
      - Adhesion provides lateral inhibition (Notch-like)
      - Polarity self-reinforces (directional memory)
      - Differentiation inhibits growth (maturation switch)
      - High differentiation is self-limiting (prevents runaway)
    """
    W = np.array([
        #  grow   branch  adhes  polar   diff     (input gene)
        [  0.80,   0.00,  -0.30,  0.20,  -0.70],  # growth output
        [  0.60,   0.50,  -0.80,  0.10,  -0.40],  # branch output
        [  0.10,   0.20,   0.70, -0.10,   0.30],  # adhesion output
        [  0.00,  -0.10,  -0.10,  0.90,  -0.20],  # polarity output
        [ -0.20,   0.00,   0.20, -0.30,   0.60],  # differentiation output
    ], dtype=float)

    bias = np.array([-0.50, -1.00, -0.20, -0.50, -1.50], dtype=float)
    return GRNNetwork(weights=W, bias=bias)


def morphogen_grn() -> GRNNetwork:
    """
    Morphogen-sensitive GRN.

    Growth and branching are strongly driven by external nutrient signal.
    Differentiation is triggered by morphogen gradient (positional cue).
    Models patterning by spatial signal interpretation.
    """
    W = np.array([
        [  0.90,   0.10,  -0.20,  0.30,  -0.80],
        [  0.70,   0.30,  -0.60,  0.00,  -0.50],
        [  0.00,   0.10,   0.80, -0.20,   0.20],
        [  0.10,  -0.20,  -0.10,  0.80,  -0.10],
        [  0.00,   0.10,   0.10, -0.20,   0.70],
    ], dtype=float)

    bias = np.array([-0.40, -1.20, -0.10, -0.30, -1.80], dtype=float)
    return GRNNetwork(weights=W, bias=bias)


def minimal_grn() -> GRNNetwork:
    """
    Minimal self-sustaining network.
    Growth and polarity self-reinforce; everything else neutral.
    Good for debugging or as a baseline.
    """
    W = np.array([
        [  0.90,   0.00,   0.00,  0.00,   0.00],
        [  0.40,   0.30,   0.00,  0.00,   0.00],
        [  0.00,   0.00,   0.60,  0.00,   0.00],
        [  0.00,   0.00,   0.00,  0.85,   0.00],
        [  0.00,   0.00,   0.00,  0.00,   0.50],
    ], dtype=float)

    bias = np.array([-0.30, -0.80, -0.20, -0.40, -1.00], dtype=float)
    return GRNNetwork(weights=W, bias=bias)

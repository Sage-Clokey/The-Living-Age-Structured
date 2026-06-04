"""
grn/signals.py — Spatial signal / morphogen field.

Provides three named signals that decay with distance from a source point:

  nutrient  — analogous to light or nutrient gradient; drives growth
  inhibitor — lateral inhibition (e.g. Notch); suppresses nearby branching
  morphogen — positional cue (e.g. WNT/BMP gradient); governs patterning

Usage:
    field = SignalField()
    sig   = field.sample(np.array([1.0, 2.5, 0.3]))
    # → np.array([nutrient, inhibitor, morphogen])
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np


@dataclass
class SignalField:
    """
    Three-signal spatial field.

    All signals follow a Gaussian decay from their source:
        signal(pos) = strength * exp(-decay * ‖pos - source‖)
    """

    # ── Nutrient (upward light / resource gradient) ───────────────────────────
    nutrient_source:   np.ndarray = field(default_factory=lambda: np.array([0.0, 10.0, 0.0]))
    nutrient_strength: float      = 1.0

    # ── Lateral inhibitor ─────────────────────────────────────────────────────
    inhibitor_source:   np.ndarray = field(default_factory=lambda: np.array([2.0, 0.0, 0.0]))
    inhibitor_strength: float      = 0.5

    # ── Positional morphogen ──────────────────────────────────────────────────
    morphogen_source:   np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0]))
    morphogen_strength: float      = 0.5

    # ── Decay constant ────────────────────────────────────────────────────────
    decay: float = 0.30

    def sample(self, pos: np.ndarray) -> np.ndarray:
        """
        Return the [nutrient, inhibitor, morphogen] signal vector at pos.

        Parameters
        ----------
        pos : (3,) world-space position

        Returns
        -------
        (3,) array of signal intensities in [0, max_strength]
        """
        return np.array([
            self._gaussian(pos, self.nutrient_source,  self.nutrient_strength),
            self._gaussian(pos, self.inhibitor_source, self.inhibitor_strength),
            self._gaussian(pos, self.morphogen_source, self.morphogen_strength),
        ])

    def _gaussian(
        self,
        pos:      np.ndarray,
        source:   np.ndarray,
        strength: float,
    ) -> float:
        d = float(np.linalg.norm(pos - source))
        return strength * math.exp(-self.decay * d)

    # ── Convenience constructors ──────────────────────────────────────────────

    @classmethod
    def phototropic(cls, light_height: float = 12.0) -> SignalField:
        """Light comes from directly above — drives upward tree growth."""
        return cls(
            nutrient_source    = np.array([0.0, light_height, 0.0]),
            nutrient_strength  = 1.4,
            inhibitor_strength = 0.2,
            morphogen_strength = 0.3,
            decay              = 0.18,
        )

    @classmethod
    def reef(cls) -> SignalField:
        """Diffuse nutrient and strong lateral inhibition — coral pattern."""
        return cls(
            nutrient_source    = np.array([0.0, 8.0, 0.0]),
            nutrient_strength  = 0.9,
            inhibitor_source   = np.array([0.0, 0.0, 0.0]),
            inhibitor_strength = 0.8,
            morphogen_strength = 0.6,
            decay              = 0.25,
        )

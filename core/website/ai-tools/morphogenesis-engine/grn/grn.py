"""
grn/grn.py

Gene Regulatory Network state for a single cell.

Each cell carries 5 internal gene-activity variables (0.0 – 1.0):

  growth     controls growth rate and readiness to divide
  branch     controls branching / division probability
  adhesion   controls cell-cell stickiness
  polarity   controls directional growth bias strength
  diff       differentiation state  (0 = stem-like, 1 = terminal)

These are updated each step based on:
  - Local morphogen signal levels sampled from the SignalField
  - Cross-regulation between genes (activation / inhibition)
  - Small Gaussian noise (biological stochasticity)

Biological analogues
--------------------
  growth   ~ WNT / nutrient response pathway
  branch   ~ FGF activator  (inhibited by Notch-like lateral signal)
  adhesion ~ E-cadherin / N-cadherin program
  polarity ~ PCP (planar cell polarity) pathway
  diff     ~ irreversible ratchet driven by cumulative growth activity
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import Dict


@dataclass
class GRNState:
    """
    Internal regulatory state of one simulated cell.

    All values are clamped to [0.0, 1.0] after each update.
    """

    growth:   float = 0.5
    branch:   float = 0.3
    adhesion: float = 0.5
    polarity: float = 0.6
    diff:     float = 0.0   # 0 = undifferentiated, 1 = terminal / mature

    def as_dict(self) -> Dict[str, float]:
        return {
            "growth":   self.growth,
            "branch":   self.branch,
            "adhesion": self.adhesion,
            "polarity": self.polarity,
            "diff":     self.diff,
        }

    def update(
        self,
        nutrient:    float,
        morphogen_a: float,
        morphogen_b: float,
        dt:          float = 0.1,
        noise:       float = 0.02,
    ) -> None:
        """
        Advance gene activities by one timestep dt.

        Parameters
        ----------
        nutrient : float [0,1]
            Local nutrient / WNT-like signal level.
        morphogen_a : float [0,1]
            FGF-like activator; promotes branching when high.
        morphogen_b : float [0,1]
            Notch-like inhibitor; suppresses branching, promotes adhesion.
        dt : float
            Timestep size.
        noise : float
            Standard deviation of per-gene Gaussian noise.

        Update rules (biologically inspired):
          growth   <- nutrient drives up, high diff suppresses
          branch   <- morphogen_a activates, morphogen_b inhibits,
                      self-damping prevents runaway
          adhesion <- morphogen_b drives up (lateral inhibition → cohesion)
          polarity <- nutrient drives up (cells polarize toward resources)
          diff     <- irreversible ratchet: high growth + low branch
                      accumulates differentiation over time
        """
        rng = np.random.default_rng()

        d_growth = (nutrient * 1.0 - self.growth * 0.8 - self.diff * 0.4) * dt

        d_branch = (
            morphogen_a * 0.9
            - morphogen_b * 0.6
            - self.branch * 0.5
        ) * dt

        d_adhesion = (morphogen_b * 1.0 - self.adhesion * 0.7) * dt

        d_polarity = (nutrient * 1.2 - self.polarity * 0.6) * dt

        # Differentiation is an irreversible ratchet — never decreases
        d_diff = max(0.0, (self.growth * 0.3 - self.branch * 0.2 - 0.1) * dt)

        if noise > 0:
            n = rng.normal(scale=noise, size=5) * dt
        else:
            n = np.zeros(5)

        self.growth   = float(np.clip(self.growth   + d_growth   + n[0], 0.0, 1.0))
        self.branch   = float(np.clip(self.branch   + d_branch   + n[1], 0.0, 1.0))
        self.adhesion = float(np.clip(self.adhesion + d_adhesion + n[2], 0.0, 1.0))
        self.polarity = float(np.clip(self.polarity + d_polarity + n[3], 0.0, 1.0))
        self.diff     = float(np.clip(self.diff     + d_diff     + n[4], 0.0, 1.0))

    def __repr__(self) -> str:
        return (
            f"GRNState(growth={self.growth:.2f}, branch={self.branch:.2f}, "
            f"adhesion={self.adhesion:.2f}, polarity={self.polarity:.2f}, "
            f"diff={self.diff:.2f})"
        )

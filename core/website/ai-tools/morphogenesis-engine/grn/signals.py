"""
grn/signals.py

Morphogen signal field — simplified radial point-source diffusion.

Instead of solving a PDE on a grid (expensive, requires spatial
discretisation), we use a superposition of Gaussian-decaying point
sources.  This gives smooth, biologically plausible gradients at
O(N * S) cost where N = cells and S = sources per cell.

Three signals are tracked:

  nutrient     Depleted by cells, replenished from a fixed anchor point
               (analogous to a root or vascular supply).
               Drives the WNT / growth response.

  morphogen_a  FGF-like activator secreted primarily by tip cells
               (cells with high growth rate and low adhesion).
               Promotes branching when sensed.

  morphogen_b  Notch-like inhibitor secreted by all cells in proportion
               to local cell density.  Suppresses nearby branching
               (lateral inhibition) and promotes cohesive adhesion.

All field values are normalised to [0, 1] at each sample point.
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class SignalSource:
    """A single point source contributing to the signal field."""
    position:    np.ndarray
    nutrient:    float = 0.0
    morphogen_a: float = 0.0
    morphogen_b: float = 0.0


class SignalField:
    """
    A superposition of Gaussian-decaying point sources.

    Parameters
    ----------
    decay_length : float
        Spatial scale of signal decay.  Larger values → signals travel
        further before fading.  Typical range: 2.0 – 6.0.
    """

    def __init__(self, decay_length: float = 3.0) -> None:
        self.decay_length = decay_length
        self.sources: List[SignalSource] = []

    # ------------------------------------------------------------------
    # Source management
    # ------------------------------------------------------------------

    def add_source(self, source: SignalSource) -> None:
        self.sources.append(source)

    def clear_sources(self) -> None:
        self.sources.clear()

    # ------------------------------------------------------------------
    # Sampling
    # ------------------------------------------------------------------

    def sample(self, position: np.ndarray) -> Tuple[float, float, float]:
        """
        Return (nutrient, morphogen_a, morphogen_b) at a world position.

        Returns a baseline of (0.5, 0.0, 0.0) when no sources exist.
        """
        if not self.sources:
            return 0.5, 0.0, 0.0

        total_n = 0.0
        total_a = 0.0
        total_b = 0.0

        for src in self.sources:
            dist = float(np.linalg.norm(position - src.position))
            w = np.exp(-dist / self.decay_length)
            total_n += src.nutrient    * w
            total_a += src.morphogen_a * w
            total_b += src.morphogen_b * w

        return (
            float(np.clip(total_n, 0.0, 1.0)),
            float(np.clip(total_a, 0.0, 1.0)),
            float(np.clip(total_b, 0.0, 1.0)),
        )

    # ------------------------------------------------------------------
    # Rebuild from current cell population
    # ------------------------------------------------------------------

    def rebuild_from_cells(
        self,
        cells,
        nutrient_center:   np.ndarray,
        nutrient_strength: float = 1.5,
        tip_growth_thresh: float = 0.07,
    ) -> None:
        """
        Rebuild the signal field from the current cell population.

        Called once per simulation step.

        Logic
        -----
        Nutrient
            Comes from a fixed point source at the vascular anchor
            (default: the coordinate origin).

        Morphogen A (FGF-like activator)
            Secreted only by "tip" cells — identified as cells whose
            growth_rate exceeds tip_growth_thresh after GRN mapping.
            High morphogen_a locally → promotes nearby branching.

        Morphogen B (Notch-like inhibitor)
            Secreted by every cell in proportion to total population size.
            Acts as a crowd signal that suppresses branching density.

        Parameters
        ----------
        cells : list of Cell
            Current cell population.
        nutrient_center : np.ndarray, shape (3,)
            World position of the nutrient anchor (typically origin).
        nutrient_strength : float
            Peak intensity of the nutrient source.
        tip_growth_thresh : float
            growth_rate above which a cell is classified as a tip cell.
        """
        self.clear_sources()

        # Fixed nutrient anchor
        self.add_source(SignalSource(
            position=nutrient_center.copy(),
            nutrient=nutrient_strength,
        ))

        n_cells = len(cells)
        if n_cells == 0:
            return

        # Morphogen B scales with density (crowd inhibitor)
        # Caps at 1.0 for very large populations
        mb_per_cell = float(np.clip(0.05 + n_cells * 0.003, 0.0, 1.0))

        for cell in cells:
            is_tip = cell.growth_rate > tip_growth_thresh
            ma = 0.7 if is_tip else 0.0

            self.add_source(SignalSource(
                position=cell.position.copy(),
                morphogen_a=ma,
                morphogen_b=mb_per_cell,
            ))

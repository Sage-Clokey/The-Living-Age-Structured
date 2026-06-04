"""
morpho/program.py

Defines GrowthProgram — a set of scalar and vector modifiers that shape
the behaviour of every cell in the simulation.

A GrowthProgram is created by the interpreter and injected into the
SimulationState.  Each simulation step applies the program to every cell
before physics are computed.
"""

from __future__ import annotations

import numpy as np
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from morpho.cell import Cell


class GrowthProgram:
    """
    A collection of per-cell behavioural modifiers.

    Attributes
    ----------
    growth_rate_multiplier : float
        Scales every cell's growth_rate (default 1.0 = no change).
    stiffness_multiplier : float
        Scales every cell's stiffness.
    adhesion_multiplier : float
        Scales every cell's adhesion.
    division_size_multiplier : float
        Scales every cell's division_radius (larger → cells grow bigger
        before dividing; smaller → more frequent, smaller divisions).
    noise_strength : float
        Magnitude of random Brownian noise added each step.
    anisotropy_vector : np.ndarray, shape (3,)
        Preferred growth direction.  Applied as a gentle velocity bias.
        Zero vector means isotropic growth.
    anisotropy_strength : float
        How strongly the anisotropy_vector biases movement.
    """

    def __init__(
        self,
        growth_rate_multiplier: float = 1.0,
        stiffness_multiplier: float = 1.0,
        adhesion_multiplier: float = 1.0,
        division_size_multiplier: float = 1.0,
        noise_strength: float = 0.01,
        anisotropy_vector: Optional[np.ndarray] = None,
        anisotropy_strength: float = 0.0,
    ) -> None:
        self.growth_rate_multiplier: float = float(growth_rate_multiplier)
        self.stiffness_multiplier: float = float(stiffness_multiplier)
        self.adhesion_multiplier: float = float(adhesion_multiplier)
        self.division_size_multiplier: float = float(division_size_multiplier)
        self.noise_strength: float = float(noise_strength)
        self.anisotropy_vector: np.ndarray = (
            np.array(anisotropy_vector, dtype=float)
            if anisotropy_vector is not None
            else np.zeros(3, dtype=float)
        )
        self.anisotropy_strength: float = float(anisotropy_strength)

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------

    def apply(self, cell: "Cell") -> None:
        """
        Stamp this program's modifiers onto a cell instance.

        This rewrites the cell's *base* parameters so that downstream
        physics code (forces, growth) automatically picks them up.

        Note: apply() is idempotent only if called once per cell
        per initialisation.  In the simulation loop the modifiers are
        applied relative to the cell's *current* state, so they should
        be treated as scale factors set at birth, not reapplied every
        tick.
        """
        cell.growth_rate *= self.growth_rate_multiplier
        cell.stiffness *= self.stiffness_multiplier
        cell.adhesion *= self.adhesion_multiplier
        cell.division_radius *= self.division_size_multiplier

    # ------------------------------------------------------------------
    # Repr
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"GrowthProgram("
            f"growth×{self.growth_rate_multiplier:.2f}, "
            f"stiffness×{self.stiffness_multiplier:.2f}, "
            f"adhesion×{self.adhesion_multiplier:.2f}, "
            f"div_size×{self.division_size_multiplier:.2f}, "
            f"noise={self.noise_strength:.4f}, "
            f"aniso={self.anisotropy_vector}@{self.anisotropy_strength:.2f})"
        )

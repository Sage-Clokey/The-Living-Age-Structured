"""
grn/runner.py

GRN-driven simulation loop.

Wraps the existing Simulation physics engine with a per-cell Gene
Regulatory Network layer.  Each simulation step:

  1. Rebuild the signal field from current cell positions.
  2. Sample signals at each cell's world position.
  3. Update each cell's GRN state.
  4. Map GRN state → cell physics parameters (growth_rate, stiffness, …).
  5. Compute the population-average anisotropy bias and write it into the
     shared GrowthProgram so that the physics step picks it up.
  6. Run one physics step (Simulation.step() — forces, divisions, bounds).

New daughter cells created by division inherit a slightly noisy copy of
the template GRNState and have their parameters set by the GRN on the
very next step, so no special handling is needed at division time.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Optional

import numpy as np

# Allow importing morpho from the parent directory when grn/ is run directly
sys.path.insert(0, str(Path(__file__).parent.parent))

from morpho.cell import Cell
from morpho.program import GrowthProgram
from morpho.state import SimulationState
from morpho.simulation import Simulation
from grn.grn import GRNState
from grn.signals import SignalField
from grn.mapper import apply_grn_to_cell, grn_anisotropy


class GRNSimulation:
    """
    Simulation loop that couples a per-cell GRN layer to the physics engine.

    Parameters
    ----------
    state : SimulationState
        Initial cell population and growth program.
    dt : float
        Timestep size (seconds).
    damping : float
        Velocity damping factor per step (overdamped / viscous medium).
    grn_noise : float
        Standard deviation of per-gene Gaussian noise on GRN updates.
    signal_decay : float
        Spatial decay length (world units) of morphogen gradients.
    initial_grn : GRNState, optional
        Template GRN state used to initialise all cells.
        Daughter cells at division inherit this with small perturbations.
    """

    def __init__(
        self,
        state:        SimulationState,
        dt:           float = 0.1,
        damping:      float = 0.8,
        grn_noise:    float = 0.03,
        signal_decay: float = 3.0,
        initial_grn:  Optional[GRNState] = None,
    ) -> None:
        self.physics = Simulation(state=state, dt=dt, damping=damping)
        self.grn_noise = grn_noise

        self.signal_field = SignalField(decay_length=signal_decay)
        self.nutrient_center = np.array([0.0, 0.0, 0.0], dtype=float)

        self._template_grn: GRNState = initial_grn or GRNState()
        self._grn_map: Dict[int, GRNState] = {}
        self._rng = np.random.default_rng(42)

        # Initialise GRN states for seed cells
        for cell in state.cells:
            self._grn_map[cell.id] = self._spawn_grn()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _spawn_grn(self) -> GRNState:
        """Create a new GRN state as a noisy copy of the template."""
        t = self._template_grn
        noise = self._rng.normal(scale=0.04, size=5)
        return GRNState(
            growth   = float(np.clip(t.growth   + noise[0], 0.0, 1.0)),
            branch   = float(np.clip(t.branch   + noise[1], 0.0, 1.0)),
            adhesion = float(np.clip(t.adhesion + noise[2], 0.0, 1.0)),
            polarity = float(np.clip(t.polarity + noise[3], 0.0, 1.0)),
            diff     = float(np.clip(t.diff     + noise[4], 0.0, 1.0)),
        )

    def _ensure_grn(self, cell: Cell) -> GRNState:
        """Return the GRN state for a cell, creating one if it's new."""
        if cell.id not in self._grn_map:
            self._grn_map[cell.id] = self._spawn_grn()
        return self._grn_map[cell.id]

    # ------------------------------------------------------------------
    # Single step
    # ------------------------------------------------------------------

    def step(self) -> None:
        """Advance the simulation by one timestep."""
        state = self.physics.state
        cells = state.cells

        # 1. Rebuild signal field from current cell positions
        self.signal_field.rebuild_from_cells(cells, self.nutrient_center)

        # 2. Update GRN for every cell, apply to physics params
        total_aniso = np.zeros(3, dtype=float)

        for cell in cells:
            grn = self._ensure_grn(cell)

            nutrient, morph_a, morph_b = self.signal_field.sample(cell.position)

            grn.update(
                nutrient=nutrient,
                morphogen_a=morph_a,
                morphogen_b=morph_b,
                dt=self.physics.dt,
                noise=self.grn_noise,
            )

            apply_grn_to_cell(cell, grn)
            total_aniso += grn_anisotropy(grn)

        # 3. Write population-average anisotropy into the global GrowthProgram
        if state.program is not None and len(cells) > 0:
            avg = total_aniso / len(cells)
            strength = float(np.linalg.norm(avg))
            if strength > 1e-8:
                state.program.anisotropy_vector = avg / strength
            else:
                state.program.anisotropy_vector = np.zeros(3)
            state.program.anisotropy_strength = strength

        # 4. Physics step (forces + divisions)
        self.physics.step()

    # ------------------------------------------------------------------
    # Multi-step runner
    # ------------------------------------------------------------------

    def run(
        self,
        steps:        int,
        verbose:      bool = True,
        report_every: int  = 10,
    ) -> None:
        """Run the simulation for *steps* timesteps."""
        for s in range(steps):
            self.step()
            if verbose and (s + 1) % report_every == 0:
                n = self.physics.state.n_cells
                t = self.physics.state.time
                print(f"  step {s+1:4d}/{steps}  |  t={t:.2f}s  |  cells={n}")

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def grn_summary(self) -> str:
        """Return a human-readable summary of GRN state across all cells."""
        if not self._grn_map:
            return "No cells."
        states = list(self._grn_map.values())
        keys   = ["growth", "branch", "adhesion", "polarity", "diff"]
        lines  = ["GRN state averages:"]
        for k in keys:
            vals = [getattr(g, k) for g in states]
            lines.append(
                f"  {k:<10} avg={np.mean(vals):.3f}"
                f"  min={np.min(vals):.3f}"
                f"  max={np.max(vals):.3f}"
            )
        return "\n".join(lines)

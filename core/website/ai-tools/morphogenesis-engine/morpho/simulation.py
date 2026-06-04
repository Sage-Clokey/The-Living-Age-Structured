"""
morpho/simulation.py

Core simulation engine — vectorised with numpy and scipy.spatial.cKDTree.

Each timestep:
  1. Grow all cells (radius increases, age advances).
  2. Use cKDTree for O(N log N) neighbour queries.
  3. Compute repulsion + adhesion forces in vectorised numpy.
  4. Apply per-cell noise and anisotropy bias.
  5. Integrate velocity and position (Euler).
  6. Apply velocity damping (overdamped / viscous medium).
  7. Handle cell division.
  8. Apply optional spatial constraints.

Performance: supports 500–2000 cells comfortably in pure Python/numpy.
"""

from __future__ import annotations

from typing import Optional, Tuple, List

import numpy as np
from scipy.spatial import cKDTree

from morpho.state import SimulationState
from morpho.cell import Cell
from morpho.program import GrowthProgram
from morpho.division import handle_divisions


class Simulation:
    """
    The main simulation engine.

    Parameters
    ----------
    state : SimulationState
        The initial state (cells + program).
    dt : float
        Timestep size (seconds).
    damping : float
        Velocity damping per step  (0 = no damping, 1 = full reset).
        Simulates a viscous / overdamped medium.
    bounds : optional tuple of (min_corner, max_corner)
        When provided, cells are confined inside this AABB each step.
    """

    def __init__(
        self,
        state: SimulationState,
        dt: float = 0.1,
        damping: float = 0.8,
        bounds: Optional[Tuple[np.ndarray, np.ndarray]] = None,
    ) -> None:
        self.state: SimulationState = state
        self.dt: float = dt
        self.damping: float = damping
        self.bounds: Optional[Tuple[np.ndarray, np.ndarray]] = bounds
        self._step_count: int = 0

    # ------------------------------------------------------------------
    # Single step — vectorised
    # ------------------------------------------------------------------

    def step(self) -> None:
        """Advance the simulation by one timestep dt."""
        cells = self.state.cells
        n = len(cells)

        if n == 0:
            return

        dt = self.dt
        program = self.state.program

        # ---- Collect arrays ------------------------------------------
        positions = np.array([c.position for c in cells], dtype=float)   # (N,3)
        velocities = np.array([c.velocity for c in cells], dtype=float)   # (N,3)
        radii = np.array([c.radius for c in cells], dtype=float)          # (N,)
        stiffness = np.array([c.stiffness for c in cells], dtype=float)   # (N,)
        adhesion_arr = np.array([c.adhesion for c in cells], dtype=float) # (N,)
        growth_rates = np.array([c.growth_rate for c in cells], dtype=float)

        # ---- 1. Grow all cells ----------------------------------------
        radii += growth_rates * dt
        for cell, r in zip(cells, radii):
            cell.radius = float(r)
            cell.age += dt

        # ---- 2. Build cKDTree ----------------------------------------
        # Maximum interaction radius = 1.5 × largest contact distance seen
        max_r = float(radii.max())
        query_radius = max_r * 3.0   # repulsion up to contact + adhesion range

        tree = cKDTree(positions)
        # pairs: list of (i, j) with distance < query_radius (i != j)
        pairs = tree.query_pairs(r=query_radius, output_type='ndarray')  # (M,2)

        # ---- 3. Vectorised pairwise forces ---------------------------
        forces = np.zeros((n, 3), dtype=float)

        if len(pairs) > 0:
            i_idx = pairs[:, 0]
            j_idx = pairs[:, 1]

            delta = positions[i_idx] - positions[j_idx]      # (M,3)
            dist = np.linalg.norm(delta, axis=1)              # (M,)

            contact = radii[i_idx] + radii[j_idx]             # (M,)

            # Safe direction vectors
            safe_dist = np.where(dist < 1e-8, 1e-8, dist)
            direction = delta / safe_dist[:, np.newaxis]       # (M,3)

            # ---- Repulsion (overlap region) --------------------------
            overlap = contact - dist                           # (M,)
            rep_mask = overlap > 0
            if rep_mask.any():
                k = np.sqrt(stiffness[i_idx] * stiffness[j_idx])  # (M,)
                f_rep = (k * overlap)[:, np.newaxis] * direction   # (M,3)
                f_rep_masked = f_rep * rep_mask[:, np.newaxis]

                np.add.at(forces, i_idx, f_rep_masked)
                np.add.at(forces, j_idx, -f_rep_masked)

            # ---- Adhesion (contact_dist to 1.5 × contact_dist) ------
            adh_range = contact * 1.5
            adh_mask = (~rep_mask) & (dist < adh_range)
            if adh_mask.any():
                gap = dist - contact
                range_w = adh_range - contact
                # Avoid division by zero when range_w is very small
                safe_rw = np.where(range_w < 1e-8, 1e-8, range_w)
                falloff = 1.0 - gap / safe_rw
                a = np.sqrt(adhesion_arr[i_idx] * adhesion_arr[j_idx])
                f_adh = (a * falloff)[:, np.newaxis] * (-direction)  # toward j
                f_adh_masked = f_adh * adh_mask[:, np.newaxis]

                np.add.at(forces, i_idx, f_adh_masked)
                np.add.at(forces, j_idx, -f_adh_masked)

        # ---- 4. Noise -----------------------------------------------
        noise_str = program.noise_strength if program is not None else 0.02
        if noise_str > 1e-10:
            forces += np.random.randn(n, 3) * noise_str

        # ---- 5. Anisotropy bias -------------------------------------
        if program is not None:
            aniso_vec = program.anisotropy_vector
            aniso_str = program.anisotropy_strength
            if aniso_str > 1e-8 and np.linalg.norm(aniso_vec) > 1e-8:
                bias = aniso_vec / np.linalg.norm(aniso_vec) * aniso_str
                forces += bias[np.newaxis, :]

        # ---- 6. Euler integration -----------------------------------
        velocities += forces * dt
        velocities *= (1.0 - self.damping)
        positions += velocities * dt

        # Write back
        for i, cell in enumerate(cells):
            cell.position = positions[i]
            cell.velocity = velocities[i]

        # ---- 7. Bounds -----------------------------------------------
        if self.bounds is not None:
            from morpho.constraints import apply_bounds
            apply_bounds(self.state, self.bounds)

        # ---- 8. Division ---------------------------------------------
        handle_divisions(self.state)

        # ---- 9. Advance time ----------------------------------------
        self.state.time += dt
        self._step_count += 1

    # ------------------------------------------------------------------
    # Multi-step runner
    # ------------------------------------------------------------------

    def run(
        self,
        steps: int,
        verbose: bool = True,
        report_every: int = 10,
    ) -> None:
        """
        Run the simulation for *steps* timesteps.

        Parameters
        ----------
        steps : int
            Number of steps to execute.
        verbose : bool
            Print progress if True.
        report_every : int
            Print status every this many steps.
        """
        for s in range(steps):
            self.step()
            if verbose and (s + 1) % report_every == 0:
                n = self.state.n_cells
                t = self.state.time
                print(f"  step {s+1:4d}/{steps}  |  t={t:.2f}s  |  cells={n}")

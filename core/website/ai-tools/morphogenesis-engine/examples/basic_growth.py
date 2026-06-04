"""
examples/basic_growth.py

Demonstrates a simple isotropic growth simulation without a user prompt.

The seed cell grows and divides in all directions, producing a roughly
spherical blob of cells.  The resulting mesh is saved to
outputs/basic_growth.obj.

Run from the project root:
    python examples/basic_growth.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

# Allow running from examples/ sub-directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from morpho.cell import Cell
from morpho.program import GrowthProgram
from morpho.state import SimulationState
from morpho.simulation import Simulation
from morpho.geometry import cells_to_mesh
from morpho.export import export_mesh


def main() -> None:
    print("Basic growth example — isotropic blob")
    print("=" * 40)

    # ------------------------------------------------------------------
    # Growth program: neutral defaults (no directional bias)
    # ------------------------------------------------------------------
    program = GrowthProgram(
        growth_rate_multiplier=1.0,
        stiffness_multiplier=1.0,
        adhesion_multiplier=1.0,
        division_size_multiplier=1.0,
        noise_strength=0.015,
    )

    # ------------------------------------------------------------------
    # Seed cell
    # ------------------------------------------------------------------
    seed = Cell(
        position=np.zeros(3),
        radius=0.4,
        growth_rate=0.06,
        division_radius=1.0,
        stiffness=1.0,
        adhesion=0.5,
    )

    state = SimulationState(program=program)
    state.add_cell(seed)

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------
    sim = Simulation(state=state, dt=0.1, damping=0.75)
    steps = 100

    print(f"Running {steps} steps …")
    sim.run(steps=steps, verbose=True, report_every=25)

    print(f"\nFinal cell count: {state.n_cells}")

    # ------------------------------------------------------------------
    # Mesh + export
    # ------------------------------------------------------------------
    print("Generating mesh …")
    mesh = cells_to_mesh(state, subdivisions=2)
    out = export_mesh(mesh, "basic_growth.obj")
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()

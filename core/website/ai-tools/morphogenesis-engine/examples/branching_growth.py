"""
examples/branching_growth.py

Demonstrates a branching, upward-growing simulation.

The growth program uses:
- High division frequency  (small division_size_multiplier)
- Upward anisotropy        (cells biased toward +Y)
- Moderate noise           (prevents perfect symmetry, enables branching)
- Thick core               (high growth rate → cells get big before dividing)

The resulting mesh is saved to outputs/branching_growth.obj.

Run from the project root:
    python examples/branching_growth.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from morpho.cell import Cell
from morpho.program import GrowthProgram
from morpho.state import SimulationState
from morpho.simulation import Simulation
from morpho.geometry import cells_to_mesh
from morpho.export import export_mesh


def main() -> None:
    print("Branching growth example — upward tree-like structure")
    print("=" * 50)

    # ------------------------------------------------------------------
    # Growth program crafted to mimic plant-like branching morphology
    # ------------------------------------------------------------------
    program = GrowthProgram(
        growth_rate_multiplier=1.6,       # thick, fast-growing cells
        stiffness_multiplier=1.2,         # slightly rigid
        adhesion_multiplier=0.8,          # moderate adhesion
        division_size_multiplier=0.65,    # divide frequently
        noise_strength=0.04,              # enough noise for asymmetry
        anisotropy_vector=np.array([0.0, 1.0, 0.0]),  # grow upward
        anisotropy_strength=0.07,
    )

    # ------------------------------------------------------------------
    # Three seed cells arranged in a small triangle at the base
    # ------------------------------------------------------------------
    seeds = [
        Cell(position=np.array([0.0,   0.0, 0.0]),  radius=0.4,
             growth_rate=0.06, division_radius=1.0,
             stiffness=1.0, adhesion=0.5),
        Cell(position=np.array([0.6,   0.0, 0.0]),  radius=0.4,
             growth_rate=0.06, division_radius=1.0,
             stiffness=1.0, adhesion=0.5),
        Cell(position=np.array([0.3,   0.0, 0.52]), radius=0.4,
             growth_rate=0.06, division_radius=1.0,
             stiffness=1.0, adhesion=0.5),
    ]

    state = SimulationState(program=program)
    for seed in seeds:
        state.add_cell(seed)

    # ------------------------------------------------------------------
    # Run simulation
    # ------------------------------------------------------------------
    sim = Simulation(state=state, dt=0.1, damping=0.80)
    steps = 140

    print(f"Seeding with {state.n_cells} cells.")
    print(f"Running {steps} steps …")
    sim.run(steps=steps, verbose=True, report_every=20)

    print(f"\nFinal cell count: {state.n_cells}")

    # ------------------------------------------------------------------
    # Mesh + export
    # ------------------------------------------------------------------
    print("Generating mesh …")
    mesh = cells_to_mesh(state, subdivisions=2)
    out = export_mesh(mesh, "branching_growth.obj")
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()

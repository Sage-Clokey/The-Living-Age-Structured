"""
main.py — morphogenetic-designer entry point.

Usage
-----
    python main.py

The program will:
  1. Ask for a natural-language growth description.
  2. Interpret the prompt into a GrowthProgram.
  3. Seed the simulation with a single starting cell.
  4. Run the morphogenesis simulation.
  5. Extract a 3-D mesh from the final cell configuration.
  6. Save the mesh to outputs/organism.obj.

Example prompt
--------------
    grow upward with branching and thick core
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

# Ensure the project root is on sys.path when run directly
sys.path.insert(0, str(Path(__file__).parent))

from morpho.cell import Cell
from morpho.program import GrowthProgram
from morpho.state import SimulationState
from morpho.simulation import Simulation
from morpho.interpreter import interpret, describe_program
from morpho.geometry import cells_to_mesh
from morpho.export import export_mesh
from morpho import tree_data


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_STEPS: int = 200          # number of simulation timesteps
DT: float = 0.1                   # timestep size (seconds)
DAMPING: float = 0.75             # velocity damping per step
OUTPUT_FILENAME: str = "organism.obj"
SPHERE_SUBDIVISIONS: int = 2      # icosphere resolution (2 = ~80 tri/sphere)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _banner() -> None:
    print()
    print("=" * 60)
    print("  Morphogenetic Designer  v0.1.0")
    print("=" * 60)
    print()


def _seed_state(program: GrowthProgram) -> SimulationState:
    """Create the initial SimulationState with one seed cell."""
    seed = Cell(
        position=np.array([0.0, 0.0, 0.0]),
        radius=0.4,
        growth_rate=0.08,        # faster growth → more cells in fewer steps
        division_radius=0.85,    # divide at smaller size → more divisions
        stiffness=1.0,
        adhesion=0.5,
    )

    state = SimulationState(program=program)
    # apply() is called inside add_cell
    state.add_cell(seed)
    return state


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _choose_mode() -> str:
    """Ask the user which growth-program source to use."""
    print("Choose growth source:")
    print("  [p] Natural-language prompt  (default)")
    print("  [s] Field-survey species     (from archive.zip)")
    print("  [l] LiDAR plot profile       (from archive.zip ALS data)")
    print()
    try:
        choice = input("Mode [p/s/l]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        choice = "p"
    return choice if choice in ("s", "l") else "p"


def _program_from_species() -> GrowthProgram:
    """Interactively pick a species and return a calibrated GrowthProgram."""
    archive = tree_data.ARCHIVE_PATH
    print("\nLoading field survey …")
    species_list = tree_data.get_species_list(archive)
    print()
    print(f"  {'Species':<10}  {'n':>5}  {'DBH(mm)':>8}  {'H(m)':>6}  {'H/D':>6}")
    print("  " + "-" * 46)
    for idx, s in enumerate(species_list, 1):
        print(f"  {idx:2d}. {tree_data.describe_species(s)}")
    print()
    try:
        raw = input("Enter species name or number: ").strip()
    except (EOFError, KeyboardInterrupt):
        raw = "Spruce"
    # Accept number or name
    if raw.isdigit():
        i = int(raw) - 1
        if 0 <= i < len(species_list):
            species_name = species_list[i].name
        else:
            print(f"Invalid number — using Spruce.")
            species_name = "Spruce"
    else:
        species_name = raw if raw else "Spruce"
    print(f"\nBuilding GrowthProgram for: {species_name}")
    program = tree_data.species_to_program(species_name, archive)
    return program


def _program_from_plot() -> GrowthProgram:
    """Interactively pick a plot and return a LiDAR-derived GrowthProgram."""
    print("\nAvailable plots: 1 – 10  (each ~7–12 MB LAS scan)")
    try:
        raw = input("Enter plot number [1-10]: ").strip()
    except (EOFError, KeyboardInterrupt):
        raw = "1"
    plot_id = int(raw) if raw.isdigit() and 1 <= int(raw) <= 10 else 1
    print(f"Loading LAS data for plot {plot_id} (this may take a moment) …")
    stats = tree_data.get_plot_stats(plot_id)
    print(f"  {tree_data.describe_plot_stats(stats)}")
    program = tree_data.plot_to_program(plot_id)
    return program


def main() -> None:
    _banner()

    # ------------------------------------------------------------------
    # 1. Choose source
    # ------------------------------------------------------------------
    mode = _choose_mode()
    print()

    # ------------------------------------------------------------------
    # 2. Build GrowthProgram
    # ------------------------------------------------------------------
    if mode == "s":
        program: GrowthProgram = _program_from_species()
    elif mode == "l":
        program = _program_from_plot()
    else:
        # --- prompt mode (original behaviour) -------------------------
        print("Describe how you want the organism to grow.")
        print("Example: grow upward with branching and thick core")
        print()
        try:
            prompt = input("Enter prompt: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nNo prompt given — using default: 'grow upward with branching'")
            prompt = "grow upward with branching"
        if not prompt:
            prompt = "grow upward with branching"
            print(f"Using default prompt: '{prompt}'")
        program = interpret(prompt)

    print()
    print(describe_program(program))
    print()

    # ------------------------------------------------------------------
    # 3. Seed simulation
    # ------------------------------------------------------------------
    state = _seed_state(program)
    sim = Simulation(state=state, dt=DT, damping=DAMPING)

    print(f"Starting with {state.n_cells} seed cell(s).")
    print(f"Running {DEFAULT_STEPS} steps  (dt={DT}s, damping={DAMPING}) …")
    print("  (Tip: more cells appear after ~step 50 as divisions accelerate)")
    print()

    # ------------------------------------------------------------------
    # 4. Run simulation
    # ------------------------------------------------------------------
    t0 = time.perf_counter()
    sim.run(steps=DEFAULT_STEPS, verbose=True, report_every=20)
    elapsed = time.perf_counter() - t0

    print()
    print(f"Simulation complete in {elapsed:.2f}s.")
    print(f"Final cell count: {state.n_cells}")
    print()

    # ------------------------------------------------------------------
    # 5. Generate mesh
    # ------------------------------------------------------------------
    print("Generating mesh …")
    t1 = time.perf_counter()
    mesh = cells_to_mesh(state, subdivisions=SPHERE_SUBDIVISIONS)
    mesh_time = time.perf_counter() - t1
    print(
        f"Mesh generated in {mesh_time:.2f}s: "
        f"{len(mesh.vertices)} vertices, {len(mesh.faces)} faces."
    )
    print()

    # ------------------------------------------------------------------
    # 6. Export mesh
    # ------------------------------------------------------------------
    print(f"Exporting mesh to outputs/{OUTPUT_FILENAME} …")
    out_path = export_mesh(mesh, OUTPUT_FILENAME)
    print(f"Saved: {out_path}")
    print()
    print("Done.")


if __name__ == "__main__":
    main()

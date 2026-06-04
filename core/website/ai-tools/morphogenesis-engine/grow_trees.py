#!/usr/bin/env python3
"""
grow_trees.py

Batch-generate 3-D growth meshes for every tree species recorded in the
field survey, and optionally one mesh per LiDAR plot, using real
measurement data from archive.zip.

Each simulation is seeded from a single cell and runs a morphogenesis
loop guided by two data layers from the archive:

  1. GrowthProgram  — calibrated from field-survey DBH / height / species
                      (growth rate, stiffness, adhesion, division frequency,
                      anisotropy strength).

  2. Crown envelope — a rotationally symmetric silhouette constraint derived
                      from species botany (conical for conifers, spheroidal
                      for broadleaves, wide for riparian species) or from
                      LiDAR H/W ratios for plot mode.

Output meshes are written to outputs/:
  outputs/tree_Spruce.obj
  outputs/tree_Birch.obj
  …
  outputs/plot_01.obj   (only with --plots flag)
  …

Usage
-----
    python grow_trees.py                  # all 9 species, 500 steps each
    python grow_trees.py --steps 300      # faster, lower cell count
    python grow_trees.py --plots          # also generate per-plot meshes
    python grow_trees.py --species Fir    # single species only
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import List, Optional

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from morpho.cell import Cell
from morpho.program import GrowthProgram
from morpho.state import SimulationState
from morpho.simulation import Simulation
from morpho.constraints import apply_crown_envelope, apply_ground_plane
from morpho.geometry import cells_to_mesh, smooth_mesh
from morpho.export import export_mesh
from morpho import tree_data


# ---------------------------------------------------------------------------
# Simulation constants
# ---------------------------------------------------------------------------

DEFAULT_STEPS: int = 500
DT: float = 0.1
DAMPING: float = 0.75
ENVELOPE_WARMUP: int = 80       # steps before envelope activates
ANISO_BOOST: float = 2.0        # scale anisotropy for stronger vertical drive
SUBDIVISIONS: int = 2           # icosphere subdivision level (2 ≈ 80 tri/sphere)
SMOOTH_ITERATIONS: int = 1      # Laplacian smoothing passes on final mesh
# After hitting the 2000-cell cap, run this many more steps for shape relaxation.
# Gives every species equal time to elongate, regardless of how quickly it grew.
RELAX_STEPS: int = 350


# ---------------------------------------------------------------------------
# Simulation runner
# ---------------------------------------------------------------------------

def _seed_state(program: GrowthProgram) -> SimulationState:
    # Use faster base growth / smaller division threshold so all species —
    # including slow-growing ones (Tilia, Willow) — reliably hit the 2000-cell
    # cap within 500 steps.  The GrowthProgram multipliers still scale these.
    seed = Cell(
        position=np.array([0.0, 0.0, 0.0]),
        radius=0.4,
        growth_rate=0.10,
        division_radius=0.75,
    )
    state = SimulationState(program=program)
    state.add_cell(seed)
    return state


def _run(
    state: SimulationState,
    envelope_fn,
    y_height: float,
    steps: int,
    label: str = "",
) -> None:
    """
    Two-phase simulation loop.

    Phase 1 — Growth: run up to *steps* timesteps, stopping as soon as the
    cell cap is reached.  Envelope activates after ENVELOPE_WARMUP steps.

    Phase 2 — Relaxation: run RELAX_STEPS additional steps.  By giving every
    species the same relaxation budget the shape elongation (driven by
    anisotropy) is equal across species regardless of how fast they grew.
    """
    from morpho.division import _MAX_CELLS
    sim = Simulation(state=state, dt=DT, damping=DAMPING)

    def _apply_constraints(s: int) -> None:
        apply_ground_plane(state, y_floor=0.0)
        if s >= ENVELOPE_WARMUP:
            apply_crown_envelope(state, envelope_fn, y_base=0.0, y_height=y_height)

    # -- Phase 1: grow to cell cap ---
    for s in range(steps):
        sim.step()
        _apply_constraints(s)
        if state.n_cells >= _MAX_CELLS:
            if label:
                print(f"    [cap at step {s+1}]", flush=True)
            break

    # -- Phase 2: shape relaxation ---
    for s in range(RELAX_STEPS):
        sim.step()
        _apply_constraints(ENVELOPE_WARMUP + s)   # envelope always active

        if label and (s + 1) % max(1, RELAX_STEPS // 4) == 0:
            pos = np.array([c.position for c in state.cells])
            h = pos[:, 1].max() - pos[:, 1].min() if len(pos) > 1 else 0.0
            print(
                f"    relax {s+1:4d}/{RELAX_STEPS}  cells={state.n_cells:4d}  height={h:.2f}",
                flush=True,
            )


# ---------------------------------------------------------------------------
# Per-species mesh generation
# ---------------------------------------------------------------------------

def grow_species(species_name: str, steps: int, verbose: bool = False) -> Path:
    """
    Grow and export a 3-D mesh for one tree species.

    Returns the path of the written .obj file.
    """
    program = tree_data.species_to_program(species_name)
    # Boost anisotropy so upward drive clearly differentiates crown height
    program.anisotropy_strength *= ANISO_BOOST

    envelope_fn, y_height = tree_data.make_envelope_fn(species_name)
    state = _seed_state(program)

    _run(state, envelope_fn, y_height, steps, label=species_name if verbose else "")

    mesh = cells_to_mesh(state, subdivisions=SUBDIVISIONS)
    if SMOOTH_ITERATIONS > 0:
        mesh = smooth_mesh(mesh, iterations=SMOOTH_ITERATIONS)

    return export_mesh(mesh, f"tree_{species_name}.obj")


# ---------------------------------------------------------------------------
# Per-plot mesh generation
# ---------------------------------------------------------------------------

def grow_plot(plot_id: int, steps: int, verbose: bool = False) -> Path:
    """
    Grow and export a 3-D mesh shaped by a plot's LiDAR crown profile.

    Returns the path of the written .obj file.
    """
    program = tree_data.plot_to_program(plot_id)
    program.anisotropy_strength *= ANISO_BOOST

    envelope_fn, y_height = tree_data.make_plot_envelope_fn(plot_id)
    state = _seed_state(program)

    _run(state, envelope_fn, y_height, steps, label=f"plot_{plot_id:02d}" if verbose else "")

    mesh = cells_to_mesh(state, subdivisions=SUBDIVISIONS)
    if SMOOTH_ITERATIONS > 0:
        mesh = smooth_mesh(mesh, iterations=SMOOTH_ITERATIONS)

    return export_mesh(mesh, f"plot_{plot_id:02d}.obj")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batch-generate 3-D tree growth meshes from archive.zip data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--steps", type=int, default=DEFAULT_STEPS,
        help=f"Simulation steps per mesh (default {DEFAULT_STEPS}).",
    )
    parser.add_argument(
        "--plots", action="store_true",
        help="Also generate one mesh per LiDAR plot (plots 1–10, reads LAS files).",
    )
    parser.add_argument(
        "--species", type=str, default=None,
        help="Generate only this species (e.g. --species Fir). Default: all.",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Print per-step progress for each simulation.",
    )
    args = parser.parse_args()

    print()
    print("=" * 62)
    print("  Tree Growth 3-D Generator")
    print("=" * 62)
    print(f"  Archive  : {tree_data.ARCHIVE_PATH.name}")
    print(f"  Steps    : {args.steps}  (dt={DT}, damping={DAMPING})")
    print(f"  Envelope : activates at step {ENVELOPE_WARMUP}")
    print(f"  Outputs  : outputs/")
    print()

    # ---- Resolve species list ----
    all_species = tree_data.get_species_list()
    if args.species:
        name = args.species.strip().title()
        target = [s for s in all_species if s.name.lower() == name.lower()]
        if not target:
            available = ", ".join(s.name for s in all_species)
            print(f"Unknown species '{args.species}'. Available: {available}")
            sys.exit(1)
        species_to_run = target
    else:
        species_to_run = all_species

    # ---- Species meshes ----
    print(f"Generating {len(species_to_run)} species mesh(es) …")
    print()

    results = []
    total_t0 = time.perf_counter()

    for sp in species_to_run:
        t0 = time.perf_counter()
        tag = f"[{sp.name:<10}]"

        spec_txt = tree_data.describe_species(sp)
        print(f"  {tag}  {spec_txt}")

        if args.verbose:
            print()

        try:
            out = grow_species(sp.name, args.steps, verbose=args.verbose)
            elapsed = time.perf_counter() - t0
            status = f"→ {out.name}  ({elapsed:.1f}s)"
            ok = True
        except Exception as exc:
            status = f"FAILED — {exc}"
            out = None
            ok = False

        if args.verbose:
            print()
        print(f"  {tag}  {status}")
        print()
        results.append((sp.name, out, ok))

    # ---- Plot meshes (optional) ----
    if args.plots:
        print(f"Generating 10 LiDAR-plot meshes (loads LAS data per plot) …")
        print()

        for pid in range(1, 11):
            t0 = time.perf_counter()
            tag = f"[plot {pid:2d}  ]"
            print(f"  {tag}", end="", flush=True)

            try:
                stats = tree_data.get_plot_stats(pid)
                print(f"  {tree_data.describe_plot_stats(stats)}")
                if args.verbose:
                    print()
                out = grow_plot(pid, args.steps, verbose=args.verbose)
                elapsed = time.perf_counter() - t0
                status = f"→ {out.name}  ({elapsed:.1f}s)"
                ok = True
            except Exception as exc:
                status = f"FAILED — {exc}"
                out = None
                ok = False

            if args.verbose:
                print()
            print(f"  {tag}  {status}")
            print()
            results.append((f"plot_{pid:02d}", out, ok))

    # ---- Summary ----
    total_elapsed = time.perf_counter() - total_t0
    ok_count = sum(1 for _, _, s in results if s)
    print("=" * 62)
    print(f"  Done — {ok_count}/{len(results)} meshes written  ({total_elapsed:.1f}s total)")
    print()
    print("  Files written:")
    for name, path, ok in results:
        if ok and path:
            print(f"    outputs/{path.name}")
    print()


if __name__ == "__main__":
    main()

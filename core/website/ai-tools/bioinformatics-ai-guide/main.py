"""
main.py — Entry point for the coral morphogenesis simulation.

Wires together config, simulation, and visualizer into a live animation.

Flow
----
1. Load SimConfig (edit config.py to change parameters).
2. Initialise CoralSimulation with a root node and seed tips.
3. Initialise CoralVisualizer with the PyVista plotter.
4. Register an animation callback that advances + renders each frame.
5. plotter.show() blocks, driving the event loop until the window closes.
6. On exit, save the final mesh as OBJ to outputs/.

Controls
--------
  Close the window         : stop simulation
  Mouse drag               : orbit camera
  Scroll wheel             : zoom
  R                        : reset camera
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

from config import SimConfig
from simulation import CoralSimulation
from visualization import CoralVisualizer


# ---------------------------------------------------------------------------
# Animation callback factory
# ---------------------------------------------------------------------------

def build_callback(
    sim: CoralSimulation,
    viz: CoralVisualizer,
    config: SimConfig,
) -> "function":
    """
    Return a closure used as the PyVista timer callback.

    The callback advances the simulation by ``steps_per_frame`` steps,
    then pushes the updated mesh to the visualizer.  When growth
    finishes, a screenshot is saved and the callback becomes a no-op
    (the window stays open for inspection).

    Parameters
    ----------
    sim    : Running CoralSimulation.
    viz    : CoralVisualizer holding the PyVista plotter.
    config : Shared SimConfig.
    """
    _done = False

    def _callback() -> None:
        nonlocal _done

        if _done:
            return

        if not sim.is_alive:
            _done = True
            print("\n\n  Growth complete — close the window to exit.")
            _save_screenshot(viz)
            return

        # Advance multiple steps per frame for speed
        for _ in range(config.steps_per_frame):
            sim.step()
            if not sim.is_alive:
                break

        mesh = sim.to_polydata()
        viz.update(
            mesh,
            n_nodes=sim.n_nodes,
            n_tips=len(sim.active_tips),
            max_nodes=config.max_nodes,
        )

        # Terminal progress line (overwrites in-place)
        print(
            f"  nodes={sim.n_nodes:4d}  tips={len(sim.active_tips):3d}  "
            f"frame={viz.frame:4d}   ",
            end="\r",
            flush=True,
        )

    return _callback


def _save_screenshot(viz: CoralVisualizer) -> None:
    out_dir = Path(__file__).parent / "outputs"
    out_dir.mkdir(exist_ok=True)
    try:
        viz.save_screenshot(str(out_dir / "coral_final.png"))
    except Exception as exc:
        print(f"  Screenshot failed: {exc}")


def _save_mesh(sim: CoralSimulation) -> None:
    out_dir = Path(__file__).parent / "outputs"
    out_dir.mkdir(exist_ok=True)
    obj_path = out_dir / "coral_final.obj"
    try:
        mesh = sim.to_polydata()
        if mesh.n_points > 0:
            mesh.save(str(obj_path))
            print(f"  Mesh saved     → {obj_path}")
    except Exception as exc:
        print(f"  OBJ export failed: {exc}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    _print_banner()

    # ------------------------------------------------------------------
    # 1. Config
    # ------------------------------------------------------------------
    config = SimConfig()

    print(f"  max_nodes        = {config.max_nodes}")
    print(f"  branch_prob      = {config.branch_probability}")
    print(f"  upward_bias      = {config.upward_bias}")
    print(f"  turn_noise       = {config.turn_noise}")
    print(f"  step_size        = {config.step_size}")
    print(f"  branch_angle     = {config.branch_angle:.2f} rad "
          f"({np.degrees(config.branch_angle):.1f}°)")
    print(f"  random_seed      = {config.random_seed}")
    print()

    # ------------------------------------------------------------------
    # 2. Simulation
    # ------------------------------------------------------------------
    sim = CoralSimulation(config)
    print(f"  Seeded {len(sim.active_tips)} initial tips from root node.")
    print()

    # ------------------------------------------------------------------
    # 3. Visualizer
    # ------------------------------------------------------------------
    viz = CoralVisualizer()

    # ------------------------------------------------------------------
    # 4. Animation loop (callback-driven)
    # ------------------------------------------------------------------
    print("  Growing… (close the window to stop early)")
    print()

    callback = build_callback(sim, viz, config)
    viz.plotter.add_callback(callback, interval=config.callback_interval_ms)

    # Blocking call — drives the event loop until the user closes the window
    viz.plotter.show()

    # ------------------------------------------------------------------
    # 5. Post-run: save OBJ mesh
    # ------------------------------------------------------------------
    print()
    print(f"  Final node count : {sim.n_nodes}")
    _save_mesh(sim)

    viz.close()

    print()
    print("  Done.")
    print()


def _print_banner() -> None:
    print()
    print("  ┌────────────────────────────────────────────┐")
    print("  │   CORAL MORPHOGENESIS SIMULATION  v1.0    │")
    print("  │   Living Architecture Engine               │")
    print("  └────────────────────────────────────────────┘")
    print()


if __name__ == "__main__":
    main()

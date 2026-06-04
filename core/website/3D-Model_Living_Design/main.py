"""
main.py — Living Systems Design Lab entry point.

Usage:
    python main.py tree
    python main.py coral
    python main.py spiral
    python main.py grn
    python main.py prompt "dense coral, spreading"

    Flags:
      --animate        step through growth in real time (PyVista)
      --export         save OBJ + JSON to outputs/
      --no-view        skip the viewer (useful with --export only)

Examples:
    python main.py tree --animate
    python main.py spiral --export --no-view
    python main.py prompt "wild spiral cathedral, tall" --export
    python main.py grn --export
"""

from __future__ import annotations

import os
import sys

from presets import tree, coral, spiral, GrowthParams
from engine import MorphogenesisEngine
from export import export_wireframe_obj, export_json


def _ensure_outputs() -> None:
    os.makedirs("saved simulations", exist_ok=True)


# ── Preset runs ───────────────────────────────────────────────────────────────

def run_preset(
    name:     str,
    animate:  bool = False,
    do_view:  bool = True,
    do_export: bool = False,
) -> None:
    presets = {"tree": tree, "coral": coral, "spiral": spiral}
    if name not in presets:
        print(f"Unknown preset '{name}'. Choose: tree | coral | spiral | grn | prompt")
        sys.exit(1)

    params = presets[name]()
    print(f"[{name}]  steps={params.steps}  max_tips={params.max_tips}  "
          f"branch={params.branching_probability:.2f}")

    if animate:
        from viewer import animate as run_animate
        run_animate(params, every_n=4)
        return

    engine = MorphogenesisEngine(params)
    engine.run()
    print(f"  generated {len(engine.segments)} segments")

    if do_export:
        _ensure_outputs()
        p1 = export_wireframe_obj(engine, f"saved simulations/{name}.obj")
        p2 = export_json(engine,          f"saved simulations/{name}.json")
        print(f"  exported: {p1}")
        print(f"  exported: {p2}")

    if do_view:
        from viewer import show
        show(engine, title=f"Living Structure: {name}")


# ── Prompt run ────────────────────────────────────────────────────────────────

def run_prompt(
    prompt:   str,
    do_view:  bool = True,
    do_export: bool = False,
) -> None:
    from prompt_translate import translate

    params = translate(prompt)
    print(f"[prompt]  '{prompt}'")
    print(f"  mode={params.mode}  steps={params.steps}  "
          f"branch={params.branching_probability:.2f}  "
          f"upward={params.upward_bias:.2f}")

    engine = MorphogenesisEngine(params)
    engine.run()
    print(f"  generated {len(engine.segments)} segments")

    if do_export:
        _ensure_outputs()
        slug = prompt.lower().replace(" ", "_").replace(",", "")[:40]
        p1 = export_wireframe_obj(engine, f"saved simulations/{slug}.obj")
        p2 = export_json(engine,          f"saved simulations/{slug}.json")
        print(f"  exported: {p1}")
        print(f"  exported: {p2}")

    if do_view:
        from viewer import show
        show(engine, title=f"Prompt: {prompt}")


# ── GRN run ───────────────────────────────────────────────────────────────────

def run_grn(
    do_view:   bool = True,
    do_export: bool = False,
) -> None:
    import numpy as np
    from grn.runner  import GRNRunner
    from grn.signals import SignalField
    from grn.presets import development_grn

    print("[grn]  running GRN-driven morphogenesis...")

    signal_field = SignalField(
        nutrient_source   = np.array([0.0, 14.0, 0.0]),
        nutrient_strength = 1.2,
        inhibitor_strength = 0.35,
        morphogen_strength = 0.70,
        decay              = 0.22,
    )

    runner = GRNRunner(
        base_params         = tree(),
        grn                 = development_grn(),
        signal_field        = signal_field,
        grn_update_interval = 5,
    )

    engine = runner.run()
    print(f"  generated {len(engine.segments)} segments")
    runner.print_summary()

    if do_export:
        _ensure_outputs()
        p1 = export_wireframe_obj(engine, "saved simulations/grn_structure.obj")
        p2 = export_json(engine,          "saved simulations/grn_structure.json")
        print(f"  exported: {p1}")
        print(f"  exported: {p2}")

    if do_view:
        from viewer import show
        show(engine, title="GRN-Driven Morphogenesis")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    args     = sys.argv[1:]
    animate  = "--animate"  in args
    do_view  = "--no-view"  not in args
    do_export = "--export"  in args

    # Strip flags
    positional = [a for a in args if not a.startswith("--")]

    if not positional:
        print(__doc__)
        sys.exit(0)

    mode = positional[0].lower()

    if mode == "grn":
        run_grn(do_view=do_view, do_export=do_export)

    elif mode == "prompt":
        prompt_text = " ".join(positional[1:]) if len(positional) > 1 else "grow a tree"
        run_prompt(prompt_text, do_view=do_view, do_export=do_export)

    else:
        run_preset(mode, animate=animate, do_view=do_view, do_export=do_export)

"""
save_torch_models.py — Generate all preset 3D models using the PyTorch engine
and save them to the "saved simulations/" folder.

Outputs per preset:
  saved simulations/<name>.obj   — wireframe OBJ (vertex + line records)
  saved simulations/<name>.json  — segment list as JSON
  saved simulations/<name>.pt    — full tip-tensor checkpoint (torch.save)

Run:
    python save_torch_models.py
    python save_torch_models.py --cpu    # force CPU even if CUDA available
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import torch

# Local modules
from engine_torch import MorphoEngineTorch
from presets import tree, coral, spiral, GrowthParams

OUT_DIR = Path("saved simulations")


def _run_and_save(name: str, params: GrowthParams, device: str | None) -> None:
    print(f"\n[{name}]  steps={params.steps}  max_tips={params.max_tips}  "
          f"branch={params.branching_probability:.2f}")

    engine = MorphoEngineTorch(params, device=device)
    t0 = time.perf_counter()
    engine.run()
    elapsed = time.perf_counter() - t0

    n = len(engine.segments)
    print(f"  {n} segments  |  {elapsed:.2f}s  |  device={engine.device}")

    p_mesh = engine.save_mesh_obj(str(OUT_DIR / f"{name}.obj"))
    p_json = engine.save_json(str(OUT_DIR / f"{name}.json"))
    p_pt   = engine.save_state(str(OUT_DIR / f"{name}.pt"))

    print(f"  -> {p_mesh}")
    print(f"  -> {p_json}")
    print(f"  -> {p_pt}")


def _run_grn(device: str | None) -> None:
    """GRN-driven tree simulation using the NumPy engine (GRN runner not yet
    ported to PyTorch).  Converts segments to TorchSegment equivalents and
    saves via a lightweight wrapper so the output format matches."""
    import numpy as np
    from grn.runner  import GRNRunner
    from grn.signals import SignalField
    from grn.presets import development_grn
    from engine_torch import TorchSegment, MorphoEngineTorch

    print("\n[grn]  running GRN-driven morphogenesis (NumPy engine + GRN)...")

    signal_field = SignalField(
        nutrient_source    = np.array([0.0, 14.0, 0.0]),
        nutrient_strength  = 1.2,
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

    numpy_engine = runner.run()
    print(f"  {len(numpy_engine.segments)} segments")
    runner.print_summary()

    # --- wrap in a torch engine shell just for saving ---
    params = numpy_engine.params
    torch_engine = MorphoEngineTorch.__new__(MorphoEngineTorch)
    torch_engine.params  = params
    torch_engine.device  = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
    torch_engine.segments = [
        TorchSegment(
            start  = seg.start,
            end    = seg.end,
            radius = seg.radius,
            depth  = 0,
        )
        for seg in numpy_engine.segments
    ]
    torch_engine._pos       = torch.zeros(1, 3)
    torch_engine._dir       = torch.zeros(1, 3)
    torch_engine._rad       = torch.zeros(1)
    torch_engine._alive     = torch.zeros(1, dtype=torch.bool)
    torch_engine._depth     = torch.zeros(1, dtype=torch.long)
    torch_engine._next_slot = 1

    p_mesh = torch_engine.save_mesh_obj(str(OUT_DIR / "grn_structure.obj"))
    p_json = torch_engine.save_json(str(OUT_DIR / "grn_structure.json"))
    print(f"  -> {p_mesh}")
    print(f"  -> {p_json}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate PyTorch morphogenesis models")
    parser.add_argument("--cpu", action="store_true", help="Force CPU (ignore CUDA)")
    args = parser.parse_args()

    device = "cpu" if args.cpu else None

    OUT_DIR.mkdir(exist_ok=True)

    print("=== PyTorch Morphogenesis Model Generator ===")
    if device is None:
        dev = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Device: {dev} (auto-detected)")
    else:
        print(f"Device: {device} (forced)")

    _run_and_save("tree",   tree(),   device)
    _run_and_save("coral",  coral(),  device)
    _run_and_save("spiral", spiral(), device)
    _run_grn(device)

    print("\n=== Done ===")
    objs = list(OUT_DIR.glob("*.obj"))
    print(f"Files in '{OUT_DIR}/':")
    for f in sorted(OUT_DIR.iterdir()):
        print(f"  {f.name}  ({f.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()

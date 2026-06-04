"""
grow_video.py — morphogenetic growth video renderer.

Runs the morphogenesis simulation, captures a snapshot every N steps,
renders each snapshot as a 3-D matplotlib figure, and stitches the frames
into an MP4 video.

Usage
-----
    python grow_video.py
    python grow_video.py --prompt "spread outward flat and stiff"
    python grow_video.py --preset tree-building
    python grow_video.py --steps 300 --fps 24 --capture-every 6

Output
------
    outputs/growth.mp4
    outputs/frames/          (individual PNG frames, kept for inspection)
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import List, NamedTuple, Tuple

import numpy as np

# Non-interactive matplotlib backend — must be set before any other import
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 — registers 3D projection

sys.path.insert(0, str(Path(__file__).parent))

from morpho.cell import Cell
from morpho.program import GrowthProgram
from morpho.state import SimulationState
from morpho.simulation import Simulation
from morpho.interpreter import interpret, describe_program


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

TOTAL_STEPS: int = 220
CAPTURE_EVERY: int = 4       # one frame per N simulation steps  → ~55 frames
FPS: int = 20
DT: float = 0.1
DAMPING: float = 0.75
OUTPUT_DIR: Path = Path("outputs")
VIDEO_NAME: str = "growth.mp4"
FRAME_DIR: Path = OUTPUT_DIR / "frames"
FIG_DPI: int = 110


# ---------------------------------------------------------------------------
# Snapshot — lightweight struct captured during simulation
# ---------------------------------------------------------------------------

class Snapshot(NamedTuple):
    positions: np.ndarray   # (N, 3) float
    radii: np.ndarray       # (N,)   float
    ages: np.ndarray        # (N,)   float
    time: float
    n_cells: int
    step: int


# ---------------------------------------------------------------------------
# Built-in presets
# ---------------------------------------------------------------------------

PRESETS: dict[str, dict] = {
    "default": {
        "prompt": "grow upward with branching and thick core",
        "steps": 220,
        "seeds": [
            dict(position=np.array([0.0, 0.0, 0.0]), radius=0.4,
                 growth_rate=0.08, division_radius=0.85,
                 stiffness=1.0, adhesion=0.5),
        ],
        "program_override": None,
        "style": "default",
    },

    "tree-building": {
        "prompt": "grow upward branching organic living",
        # Living-building GrowthProgram:
        # - Soft stiffness (1.0) → cells deform around each other; no rigid lattice
        # - Low adhesion (0.52) → loose, flowing clusters instead of flat floor plates
        # - High noise (0.052) → natural asymmetry, emergent branching, no grid artifacts
        # - Larger division radius (0.78×) → cells grow big before splitting, so the
        #   structure has thick trunk regions and thin, tendril-like tips
        # - Gentle anisotropy (0.09) → upward drive without overriding organic spread
        # - Four asymmetric seeds → mimics root flare, prevents bilateral symmetry
        "steps": 280,
        "seeds": [
            # Central stem — large + fast → dominant trunk
            dict(position=np.array([ 0.00, 0.0,  0.00]), radius=0.50,
                 growth_rate=0.09, division_radius=0.95,
                 stiffness=1.0, adhesion=0.50),
            # Asymmetric root offsets → organic lean and root flare
            dict(position=np.array([ 0.55, 0.0,  0.15]), radius=0.38,
                 growth_rate=0.06, division_radius=0.90,
                 stiffness=0.90, adhesion=0.55),
            dict(position=np.array([-0.40, 0.0,  0.50]), radius=0.38,
                 growth_rate=0.06, division_radius=0.88,
                 stiffness=0.90, adhesion=0.55),
            dict(position=np.array([ 0.15, 0.0, -0.52]), radius=0.35,
                 growth_rate=0.05, division_radius=0.85,
                 stiffness=0.85, adhesion=0.60),
        ],
        "program_override": GrowthProgram(
            growth_rate_multiplier=1.3,
            stiffness_multiplier=1.0,       # soft — organic deformation, no rigid lattice
            adhesion_multiplier=0.52,       # loose clusters → flowing, not layered
            division_size_multiplier=0.78,  # larger cells before split → structural variety
            noise_strength=0.052,           # organic noise → natural asymmetric branching
            anisotropy_vector=np.array([0.0, 1.0, 0.0]),  # +Y upward
            anisotropy_strength=0.09,       # gentle vertical bias — form wins over direction
        ),
        "style": "living",
    },

    "blob": {
        "prompt": "spread outward flat and stiff",
        "steps": 180,
        "seeds": [
            dict(position=np.array([0.0, 0.0, 0.0]), radius=0.4,
                 growth_rate=0.07, division_radius=0.90,
                 stiffness=1.0, adhesion=0.7),
        ],
        "program_override": None,
        "style": "default",
    },
}


# ---------------------------------------------------------------------------
# Simulation runner with snapshot capture
# ---------------------------------------------------------------------------

def run_and_capture(
    sim: Simulation,
    total_steps: int,
    capture_every: int,
) -> List[Snapshot]:
    """Advance the simulation, returning one Snapshot every *capture_every* steps."""
    snapshots: List[Snapshot] = []

    for s in range(total_steps):
        sim.step()

        if s % capture_every == 0 or s == total_steps - 1:
            cells = sim.state.cells
            snap = Snapshot(
                positions=np.array([c.position for c in cells], dtype=float),
                radii=np.array([c.radius    for c in cells], dtype=float),
                ages=np.array([c.age       for c in cells], dtype=float),
                time=sim.state.time,
                n_cells=sim.state.n_cells,
                step=s + 1,
            )
            snapshots.append(snap)

        if (s + 1) % 50 == 0:
            print(f"  step {s+1:4d}/{total_steps}  |  cells={sim.state.n_cells}")

    return snapshots


# ---------------------------------------------------------------------------
# Axis limits — computed once from all snapshots for a stable camera
# ---------------------------------------------------------------------------

def global_axis_limits(snapshots: List[Snapshot]) -> Tuple[float, float]:
    all_pos = np.vstack([s.positions for s in snapshots])
    margin = 0.6
    lo = float(all_pos.min()) - margin
    hi = float(all_pos.max()) + margin
    # Expand symmetrically so the scene is centred
    center = (lo + hi) / 2.0
    half   = (hi - lo) / 2.0 * 1.05
    return (center - half, center + half)


# ---------------------------------------------------------------------------
# Frame renderer
# ---------------------------------------------------------------------------

_BG = "#0c0c1e"          # deep navy background

# Botanical colormap for the "living" style:
# dark earth root → amber heartwood → golden trunk → lime canopy → pale growing tip
from matplotlib.colors import LinearSegmentedColormap
_LIVING_CMAP = LinearSegmentedColormap.from_list(
    "living",
    [
        "#120800",  # deep root — almost black
        "#5c2600",  # heartwood — dark brown
        "#a05010",  # warm amber — lower trunk
        "#d4901a",  # golden — mid structure
        "#b8d428",  # chartreuse — canopy emergence
        "#e8f890",  # pale lime — newest growing tips
    ],
)
_LIVING_BG = "#060b06"   # deep forest-black for the living style


def render_frame(
    snap: Snapshot,
    frame_idx: int,
    total_frames: int,
    axis_lim: Tuple[float, float],
    savepath: Path,
    azim_start: float = 25.0,
    azim_total: float = 110.0,   # total camera rotation over the full video
    style: str = "default",      # "default" | "living"
) -> None:
    """Render *snap* as a 3-D matplotlib scatter plot and save to *savepath*.

    style="living"  uses a botanical colormap, dark forest background, and a
    soft glow pass so the organism reads as a warm, living shape rather than
    a uniform point cloud.
    """

    positions = snap.positions
    radii     = snap.radii

    # --- Choose style settings --------------------------------------------
    living = (style == "living")
    bg     = _LIVING_BG if living else _BG
    cmap   = _LIVING_CMAP if living else "plasma"
    bar_color = "#44bb66" if living else "#6655ee"

    # --- Color: normalised Y (height) → maps to chosen colormap ----------
    y = positions[:, 1]
    y_lo, y_hi = y.min(), y.max()
    color_norm = (y - y_lo) / max(y_hi - y_lo, 1e-6)

    # --- Marker area proportional to radius² (screen-space approx) --------
    s = np.clip((radii * 55.0) ** 2, 4.0, 2800.0)

    # --- Camera: slow orbit -----------------------------------------------
    progress = frame_idx / max(total_frames - 1, 1)
    azim = azim_start + progress * azim_total

    # --- Figure -----------------------------------------------------------
    fig = plt.figure(figsize=(9, 9), facecolor=bg, dpi=FIG_DPI)
    ax  = fig.add_subplot(111, projection="3d")
    ax.set_facecolor(bg)

    x3, z3, y3 = positions[:, 0], positions[:, 2], positions[:, 1]

    # Glow pass — wide, translucent halo that gives organic depth
    if living:
        ax.scatter(
            x3, z3, y3,
            s=np.clip(s * 5.0, 20.0, 14000.0),
            c=color_norm,
            cmap=cmap,
            alpha=0.06,
            edgecolors="none",
            depthshade=False,
        )

    # Main scatter — cells as sized, coloured points
    ax.scatter(
        x3, z3, y3,
        s=s,
        c=color_norm,
        cmap=cmap,
        alpha=0.85,
        edgecolors="none",
        depthshade=True,
    )

    lo, hi = axis_lim
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_zlim(lo, hi)
    ax.set_axis_off()
    ax.view_init(elev=18, azim=azim)

    # --- HUD: time / cell count / progress --------------------------------
    hud_color = "#99ddaa" if living else "#aaaadd"
    fig.text(
        0.5, 0.055,
        f"t = {snap.time:.1f} s    cells = {snap.n_cells}    "
        f"{int(progress * 100):3d} %",
        ha="center", color=hud_color, fontsize=11,
        fontfamily="monospace",
    )

    # Thin progress bar
    bar = fig.add_axes([0.15, 0.03, 0.70, 0.010])
    bar.set_xlim(0.0, 1.0)
    bar.set_ylim(0.0, 1.0)
    bar.set_facecolor("#0e1a0e" if living else "#1c1c38")
    bar.barh(0.5, progress, height=1.0, left=0.0, color=bar_color, zorder=2)
    bar.set_axis_off()

    fig.savefig(savepath, dpi=FIG_DPI, bbox_inches="tight", facecolor=bg)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Video assembly
# ---------------------------------------------------------------------------

def frames_to_video(frame_dir: Path, output_path: Path, fps: int) -> "Path | None":
    """
    Assemble PNG frames into a video/animation.

    Tries in order:
      1. imageio + libx264  (needs imageio-ffmpeg)
      2. ffmpeg subprocess
      3. Pillow animated GIF  (Pillow is in the base requirements)

    Returns the Path of the file actually created, or None on total failure.
    """
    frames = sorted(frame_dir.glob("frame_*.png"))
    if not frames:
        return None

    # --- Strategy 1: imageio ----------------------------------------------
    try:
        import imageio.v2 as iio  # type: ignore
        with iio.get_writer(str(output_path), fps=fps, codec="libx264",
                            quality=8, macro_block_size=None) as writer:
            for f in frames:
                writer.append_data(iio.imread(str(f)))
        return output_path
    except Exception:
        pass

    try:
        import imageio  # type: ignore
        writer = imageio.get_writer(str(output_path), fps=fps)
        for f in frames:
            writer.append_data(imageio.imread(str(f)))
        writer.close()
        return output_path
    except Exception:
        pass

    # --- Strategy 2: ffmpeg subprocess ------------------------------------
    try:
        result = subprocess.run(
            [
                "ffmpeg", "-y",
                "-framerate", str(fps),
                "-i", str(frame_dir / "frame_%04d.png"),
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-crf", "18",
                str(output_path),
            ],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            return output_path
    except FileNotFoundError:
        pass

    # --- Strategy 3: Pillow animated GIF ----------------------------------
    try:
        from PIL import Image
        gif_path = output_path.with_suffix(".gif")
        duration_ms = int(1000 / fps)
        imgs = [Image.open(str(f)).convert("RGB") for f in frames]
        imgs_p = [img.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
                  for img in imgs]
        imgs_p[0].save(
            gif_path,
            save_all=True,
            append_images=imgs_p[1:],
            loop=0,
            duration=duration_ms,
            optimize=False,
        )
        return gif_path
    except Exception:
        pass

    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render a morphogenetic growth animation to MP4."
    )
    parser.add_argument(
        "--prompt", default=None,
        help="Natural-language growth description (overrides --preset prompt).",
    )
    parser.add_argument(
        "--preset", default="default", choices=list(PRESETS.keys()),
        help="Built-in growth preset.",
    )
    parser.add_argument("--steps",         type=int, default=None)
    parser.add_argument("--fps",           type=int, default=FPS)
    parser.add_argument("--capture-every", type=int, default=CAPTURE_EVERY)
    parser.add_argument("--output",        default=VIDEO_NAME,
                        help="Output MP4 filename (inside outputs/).")
    args = parser.parse_args()

    preset = PRESETS[args.preset]
    prompt = args.prompt or preset["prompt"]
    steps  = args.steps  or preset["steps"]

    print()
    print("=" * 62)
    print("  Morphogenetic Growth — Video Renderer")
    print("=" * 62)
    print(f"  Preset        : {args.preset}")
    print(f"  Prompt        : {prompt}")
    print(f"  Sim steps     : {steps}")
    print(f"  Capture every : {args.capture_every} steps")
    print(f"  FPS           : {args.fps}")
    print()

    # ---- Directories -----
    OUTPUT_DIR.mkdir(exist_ok=True)
    FRAME_DIR.mkdir(exist_ok=True)
    for old in FRAME_DIR.glob("frame_*.png"):
        old.unlink()

    # ---- Build program ---------------------------------------------------
    if preset["program_override"] is not None and args.prompt is None:
        program = preset["program_override"]
        print(f"Using handcrafted GrowthProgram for preset '{args.preset}'.")
    else:
        program = interpret(prompt)
        print(describe_program(program))
    print()

    # ---- Seed simulation -------------------------------------------------
    state = SimulationState(program=program)
    for seed_kwargs in preset["seeds"]:
        state.add_cell(Cell(**seed_kwargs))

    sim = Simulation(state=state, dt=DT, damping=DAMPING)
    print(f"Seeded with {state.n_cells} cell(s).")
    print()

    # ---- Run + capture ---------------------------------------------------
    print(f"Running simulation …")
    t0 = time.perf_counter()
    snapshots = run_and_capture(sim, steps, args.capture_every)
    sim_elapsed = time.perf_counter() - t0

    print()
    print(f"Simulation done in {sim_elapsed:.1f}s.")
    print(f"Captured {len(snapshots)} frames.  Final cell count: {state.n_cells}")
    print()

    # ---- Global axis limits (stable camera) ------------------------------
    lo, hi = global_axis_limits(snapshots)
    print(f"Axis limits: {lo:.2f} → {hi:.2f}")
    print()

    # ---- Render frames ---------------------------------------------------
    render_style = preset.get("style", "default")
    print(f"Rendering {len(snapshots)} frames (style={render_style}) …")
    t1 = time.perf_counter()
    for i, snap in enumerate(snapshots):
        savepath = FRAME_DIR / f"frame_{i:04d}.png"
        render_frame(snap, i, len(snapshots), (lo, hi), savepath,
                     style=render_style)
        if (i + 1) % 10 == 0 or i == len(snapshots) - 1:
            print(f"  rendered {i+1}/{len(snapshots)}")
    render_elapsed = time.perf_counter() - t1
    print(f"Frames rendered in {render_elapsed:.1f}s.")
    print()

    # ---- Assemble video --------------------------------------------------
    video_path = OUTPUT_DIR / args.output
    print(f"Assembling video → {video_path} …")
    out_file = frames_to_video(FRAME_DIR, video_path, args.fps)

    if out_file is not None:
        size_mb = out_file.stat().st_size / 1_048_576
        fmt = "GIF" if out_file.suffix == ".gif" else "MP4"
        print(f"{fmt} saved: {out_file}  ({size_mb:.1f} MB)")
        if fmt == "GIF":
            print("(Install imageio-ffmpeg or ffmpeg to get an MP4 instead.)")
    else:
        print("Assembly failed — imageio-ffmpeg, ffmpeg, and Pillow all unavailable.")
        print(f"Frames saved in:  {FRAME_DIR}/")
        print()
        print("Combine manually with ffmpeg:")
        print(
            f"  ffmpeg -framerate {args.fps} "
            f"-i {FRAME_DIR}/frame_%04d.png "
            f"-c:v libx264 -pix_fmt yuv420p {video_path}"
        )

    print()
    print("Done.")


if __name__ == "__main__":
    main()

"""
prompt_translate.py — Natural language → GrowthParams.

Parses a plain-English prompt and maps keywords to mode selection
and parameter modifiers, then returns a fully configured GrowthParams.

Examples:
    "grow a tree"
    "coral reef, dense"
    "tall spiral tower"
    "wild branching coral, spreading"
    "living bridge"
"""

from __future__ import annotations

import copy
from presets import GrowthParams, tree, coral, spiral, shelter


# ── Keyword tables ────────────────────────────────────────────────────────────

_MODE_KEYWORDS = {
    "shelter":  ["shelter", "canopy", "dome", "pavilion", "vault",
                 "living roof", "living shelter", "living canopy"],
    "coral":    ["coral", "reef", "algae", "polyp"],
    "spiral":   ["spiral", "helix", "helical", "tower", "cathedral",
                 "bridge", "living bridge", "spire", "column"],
    "tree":     ["tree", "forest", "oak", "pine", "branch",
                 "trunk", "bough", "sapling"],
}

_MODIFIERS: list[tuple[list[str], dict]] = [
    # (keyword list, parameter delta dict)
    (
        ["dense", "thick", "bushy", "full", "lush", "crowded"],
        dict(branching_probability_mul=1.5, max_tips_mul=1.5,
             split_probability_mul=1.3),
    ),
    (
        ["sparse", "minimal", "bare", "thin", "skeletal"],
        dict(branching_probability_mul=0.45, max_tips_mul=0.5),
    ),
    (
        ["tall", "towering", "high", "soaring", "vertical"],
        dict(upward_bias_mul=1.3, steps_mul=1.3, radial_bias_mul=0.6),
    ),
    (
        ["wide", "spreading", "broad", "flat", "low", "horizontal"],
        dict(radial_bias_mul=2.0, upward_bias_mul=0.55),
    ),
    (
        ["wild", "chaotic", "random", "organic", "messy", "noisy"],
        dict(noise_strength_mul=1.6, branching_probability_mul=1.3,
             branch_angle_deg_mul=1.2),
    ),
    (
        ["tight", "precise", "controlled", "clean", "ordered"],
        dict(noise_strength_mul=0.4, branch_angle_deg_mul=0.7),
    ),
    (
        ["living bridge", "bridge", "horizontal arch", "spanning"],
        dict(upward_bias_abs=0.05, radial_bias_abs=1.0, twist_strength_abs=0.3),
    ),
]


# ── Public function ───────────────────────────────────────────────────────────

def translate(prompt: str) -> GrowthParams:
    """
    Convert a natural-language prompt string to a GrowthParams instance.

    Steps:
      1. Detect growth mode from keywords.
      2. Start from the matching preset.
      3. Apply modifier keywords.
    """
    p = prompt.lower()

    # ── Mode selection ────────────────────────────────────────────────────────
    params: GrowthParams
    if any(kw in p for kw in _MODE_KEYWORDS["shelter"]):
        params = shelter()
    elif any(kw in p for kw in _MODE_KEYWORDS["coral"]):
        params = coral()
    elif any(kw in p for kw in _MODE_KEYWORDS["spiral"]):
        params = spiral()
    else:
        params = tree()

    # ── Modifier application ──────────────────────────────────────────────────
    for keywords, delta in _MODIFIERS:
        if not any(kw in p for kw in keywords):
            continue

        for key, val in delta.items():
            if key.endswith("_mul"):
                attr = key[:-4]
                current = getattr(params, attr)
                setattr(params, attr, current * val)
            elif key.endswith("_abs"):
                attr = key[:-4]
                setattr(params, attr, val)

    # ── Clamp safety bounds ───────────────────────────────────────────────────
    params.branching_probability = float(
        min(0.60, max(0.01, params.branching_probability))
    )
    params.max_tips    = int(min(500, max(8, params.max_tips)))
    params.steps       = int(min(800, max(50, params.steps)))
    params.upward_bias = float(min(2.0, max(0.0, params.upward_bias)))
    params.radial_bias = float(min(1.5, max(0.0, params.radial_bias)))
    params.noise_strength = float(min(0.7, max(0.02, params.noise_strength)))
    params.branch_angle_deg = float(min(70.0, max(5.0, params.branch_angle_deg)))

    return params


# ── CLI for quick testing ─────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "coral reef, dense"
    p = translate(prompt)
    print(f"Prompt  : {prompt!r}")
    print(f"Mode    : {p.mode}")
    print(f"Steps   : {p.steps}")
    print(f"Branch  : {p.branching_probability:.3f}")
    print(f"Up bias : {p.upward_bias:.3f}")
    print(f"Radial  : {p.radial_bias:.3f}")
    print(f"Noise   : {p.noise_strength:.3f}")
    print(f"Twist   : {p.twist_strength:.3f}")
    print(f"MaxTips : {p.max_tips}")

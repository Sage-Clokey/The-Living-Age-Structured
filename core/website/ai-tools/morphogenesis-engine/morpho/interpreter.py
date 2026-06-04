"""
morpho/interpreter.py

Rule-based natural language interpreter that converts plain-English
prompts into GrowthProgram instances.

No external API is required — interpretation is purely keyword-driven.
The interpreter scans for known keywords and accumulates modifier
adjustments.  Multiple keywords may appear in a single prompt and their
effects are multiplied together.

Recognised keywords
-------------------
branching / branch   → more frequent divisions (smaller division_radius)
thick / wide / fat   → higher growth_rate
stiff / rigid        → higher stiffness
spread / flat        → higher adhesion, lower anisotropy
upward / tall        → anisotropy toward +Y axis
downward / deep      → anisotropy toward -Y axis
sideways / outward   → anisotropy toward +X axis
noisy / random       → increased noise_strength
smooth / quiet       → reduced noise_strength
slow                 → reduced growth_rate
fast                 → increased growth_rate
compact / tight      → reduced adhesion, higher stiffness
loose / soft         → reduced stiffness
"""

from __future__ import annotations

import re
from typing import List

import numpy as np

from morpho.program import GrowthProgram


# ---------------------------------------------------------------------------
# Keyword rule table
# Each entry: (pattern, attribute, delta_or_factor, mode)
# mode "mul" → multiply current value by factor
# mode "add" → add delta to current value
# mode "set" → set directly
# ---------------------------------------------------------------------------

_RULES = [
    # --- division frequency ---
    (r"\bbranch(?:ing)?\b",  "division_size_multiplier", 0.65,  "mul"),
    (r"\bdivid",             "division_size_multiplier", 0.70,  "mul"),

    # --- growth rate ---
    (r"\bthick\b",           "growth_rate_multiplier",   1.6,   "mul"),
    (r"\bwide\b",            "growth_rate_multiplier",   1.4,   "mul"),
    (r"\bfat\b",             "growth_rate_multiplier",   1.5,   "mul"),
    (r"\bfast\b",            "growth_rate_multiplier",   1.8,   "mul"),
    (r"\bslow\b",            "growth_rate_multiplier",   0.5,   "mul"),

    # --- stiffness ---
    (r"\bstiff\b",           "stiffness_multiplier",     2.0,   "mul"),
    (r"\brigid\b",           "stiffness_multiplier",     2.5,   "mul"),
    (r"\bsoft\b",            "stiffness_multiplier",     0.4,   "mul"),
    (r"\bloose\b",           "stiffness_multiplier",     0.3,   "mul"),
    (r"\bcompact\b",         "stiffness_multiplier",     1.8,   "mul"),

    # --- adhesion ---
    (r"\bspread\b",          "adhesion_multiplier",      2.0,   "mul"),
    (r"\bflat\b",            "adhesion_multiplier",      2.2,   "mul"),
    (r"\bcompact\b",         "adhesion_multiplier",      0.4,   "mul"),
    (r"\btight\b",           "adhesion_multiplier",      0.3,   "mul"),
    (r"\bstick\b",           "adhesion_multiplier",      2.5,   "mul"),

    # --- noise ---
    (r"\bnoisy\b",           "noise_strength",           3.0,   "mul"),
    (r"\brandom\b",          "noise_strength",           2.5,   "mul"),
    (r"\bsmooth\b",          "noise_strength",           0.2,   "mul"),
    (r"\bquiet\b",           "noise_strength",           0.1,   "mul"),
]

# Directional anisotropy rules → (pattern, vector, strength)
_ANISO_RULES = [
    (r"\bupward\b",          np.array([0.0,  1.0, 0.0]), 0.08),
    (r"\btall\b",            np.array([0.0,  1.0, 0.0]), 0.06),
    (r"\bdown(?:ward)?\b",   np.array([0.0, -1.0, 0.0]), 0.06),
    (r"\bdeep\b",            np.array([0.0, -1.0, 0.0]), 0.05),
    (r"\bsideways\b",        np.array([1.0,  0.0, 0.0]), 0.06),
    (r"\boutward\b",         np.array([1.0,  0.0, 0.0]), 0.05),
    (r"\binward\b",          np.array([-1.0, 0.0, 0.0]), 0.05),
]


def interpret(prompt: str) -> GrowthProgram:
    """
    Parse a natural-language prompt and return a GrowthProgram.

    Parameters
    ----------
    prompt : str
        Free-form English description of desired growth behaviour.

    Returns
    -------
    GrowthProgram
        Configured with multipliers derived from the detected keywords.
    """
    text = prompt.lower().strip()

    # Start with neutral defaults
    growth_rate_mul: float = 1.0
    stiffness_mul: float = 1.0
    adhesion_mul: float = 1.0
    division_size_mul: float = 1.0
    noise_strength: float = 0.02
    aniso_vec: np.ndarray = np.zeros(3, dtype=float)
    aniso_str: float = 0.0

    # Apply scalar rules
    for pattern, attr, factor, mode in _RULES:
        if re.search(pattern, text):
            if attr == "growth_rate_multiplier":
                growth_rate_mul *= factor
            elif attr == "stiffness_multiplier":
                stiffness_mul *= factor
            elif attr == "adhesion_multiplier":
                adhesion_mul *= factor
            elif attr == "division_size_multiplier":
                division_size_mul *= factor
            elif attr == "noise_strength":
                noise_strength *= factor

    # Apply anisotropy rules (accumulate vectors, take final normalised result)
    for pattern, vec, strength in _ANISO_RULES:
        if re.search(pattern, text):
            aniso_vec += vec
            aniso_str = max(aniso_str, strength)

    # Clamp extreme values for simulation stability
    growth_rate_mul = max(0.1, min(growth_rate_mul, 10.0))
    stiffness_mul = max(0.1, min(stiffness_mul, 10.0))
    adhesion_mul = max(0.0, min(adhesion_mul, 10.0))
    division_size_mul = max(0.3, min(division_size_mul, 5.0))
    noise_strength = max(0.0, min(noise_strength, 1.0))

    program = GrowthProgram(
        growth_rate_multiplier=growth_rate_mul,
        stiffness_multiplier=stiffness_mul,
        adhesion_multiplier=adhesion_mul,
        division_size_multiplier=division_size_mul,
        noise_strength=noise_strength,
        anisotropy_vector=aniso_vec if np.linalg.norm(aniso_vec) > 1e-8 else None,
        anisotropy_strength=aniso_str,
    )

    return program


def describe_program(program: GrowthProgram) -> str:
    """
    Return a human-readable summary of a GrowthProgram.

    Useful for echoing back what the interpreter understood.
    """
    lines: List[str] = [
        "Interpreted growth program:",
        f"  Growth rate ×{program.growth_rate_multiplier:.2f}",
        f"  Stiffness   ×{program.stiffness_multiplier:.2f}",
        f"  Adhesion    ×{program.adhesion_multiplier:.2f}",
        f"  Div. size   ×{program.division_size_multiplier:.2f}",
        f"  Noise        {program.noise_strength:.4f}",
    ]
    if np.linalg.norm(program.anisotropy_vector) > 1e-8:
        lines.append(
            f"  Anisotropy  {program.anisotropy_vector}  "
            f"(strength={program.anisotropy_strength:.3f})"
        )
    return "\n".join(lines)

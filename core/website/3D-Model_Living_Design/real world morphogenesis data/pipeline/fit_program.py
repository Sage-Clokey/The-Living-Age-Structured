"""
pipeline/fit_program.py

Maps registry features → GrowthProgram parameters for the morphogenesis engine.

For each species/source group in the registry, computes median morphological
features across all scans and derives the 7 GrowthProgram parameters using
the same biologically-grounded mappings as morpho/tree_data.py but driven
by real measured data instead of hand-tuned tables.

Output: growth_programs.json
  {
    "Maize": {
      "growth_rate_multiplier": 1.24,
      "stiffness_multiplier": ...,
      ...
      "scan_count": 47,
      "sources": ["pheno4d", "maizefield3d"]
    },
    ...
  }

This JSON can be read directly by the morphogenesis engine to load
data-calibrated GrowthPrograms.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))
from pipeline import registry

OUTPUT_PATH = Path(__file__).parent.parent / "growth_programs.json"


# ---------------------------------------------------------------------------
# Feature → GrowthProgram mapping
# ---------------------------------------------------------------------------

def features_to_program(
    median_feats: dict,
    species: Optional[str] = None,
) -> dict:
    """
    Derive GrowthProgram parameters from median scan features.

    Mapping rationale (mirrors morpho/tree_data.py logic but data-driven):

    growth_rate_multiplier
        ← height  (taller plants grew faster; normalized to [0.6, 1.8])

    anisotropy_strength
        ← hw_ratio  (slender = strong upward bias; [0.04, 0.16])

    division_size_multiplier
        ← upper_density  (dense upper canopy = more upper branching;
          inverted so high density → smaller division size → more cells)

    adhesion_multiplier
        ← spread_asymm  (high asymmetry = irregular crown = more adhesion)

    stiffness_multiplier
        ← hw_ratio  (slender upright plants are stiffer; [0.8, 2.0])

    noise_strength
        ← spread_asymm  (more irregular → more noise)

    anisotropy_vector
        Always [0, 1, 0] (upward) — can be overridden for architectural use.
    """
    h = float(median_feats.get("height", 10.0))
    hw = float(median_feats.get("hw_ratio", 1.0))
    upper = float(median_feats.get("upper_density", 0.5))
    asymm = float(median_feats.get("spread_asymm", 0.3))

    # growth_rate_multiplier: height in [0.5, 500] → [0.6, 1.8]
    h_norm = (np.log1p(h) - np.log1p(0.5)) / (np.log1p(500) - np.log1p(0.5))
    growth_mul = 0.6 + 1.2 * float(np.clip(h_norm, 0, 1))

    # anisotropy_strength: hw_ratio [0.5, 10] → [0.04, 0.16]
    hw_norm = (np.log1p(hw) - np.log1p(0.5)) / (np.log1p(10) - np.log1p(0.5))
    aniso_str = 0.04 + 0.12 * float(np.clip(hw_norm, 0, 1))

    # division_size_multiplier: upper_density [0, 1] → [0.85, 0.50]
    # (dense upper growth = more divisions = smaller div_size)
    div_mul = 0.85 - 0.35 * float(np.clip(upper, 0, 1))

    # adhesion_multiplier: spread_asymm [0, 1] → [0.6, 2.5]
    adh_mul = 0.6 + 1.9 * float(np.clip(asymm, 0, 1))

    # stiffness_multiplier: hw_ratio [0.5, 10] → [0.8, 2.0]
    stiff_mul = 0.8 + 1.2 * float(np.clip(hw_norm, 0, 1))

    # noise_strength: spread_asymm [0, 1] → [0.008, 0.035]
    noise = 0.008 + 0.027 * float(np.clip(asymm, 0, 1))

    return {
        "growth_rate_multiplier": round(growth_mul, 3),
        "stiffness_multiplier": round(stiff_mul, 3),
        "adhesion_multiplier": round(adh_mul, 3),
        "division_size_multiplier": round(div_mul, 3),
        "noise_strength": round(noise, 5),
        "anisotropy_vector": [0.0, 1.0, 0.0],
        "anisotropy_strength": round(aniso_str, 4),
    }


# ---------------------------------------------------------------------------
# Group and fit
# ---------------------------------------------------------------------------

def run(reg: Optional[dict] = None, verbose: bool = True) -> dict:
    if reg is None:
        reg = registry.load()

    if len(reg) == 0:
        print("Registry is empty — run ingest.py first.")
        return {}

    # Group by species
    groups: dict = defaultdict(lambda: {"features": [], "sources": set()})
    for entry in reg.values():
        species = entry.get("species") or "Unknown"
        feats = entry.get("features", {})
        if "error" in feats:
            continue
        groups[species]["features"].append(feats)
        groups[species]["sources"].add(entry.get("source", "?"))

    programs = {}
    for species, group in sorted(groups.items()):
        feat_list = group["features"]
        if not feat_list:
            continue

        # Compute median over each feature key
        all_keys = set()
        for f in feat_list:
            all_keys.update(f.keys())

        median_feats = {}
        for key in all_keys:
            vals = [f[key] for f in feat_list if key in f and isinstance(f[key], (int, float))]
            if vals:
                median_feats[key] = float(np.median(vals))

        params = features_to_program(median_feats, species)
        params["scan_count"] = len(feat_list)
        params["sources"] = sorted(group["sources"])
        params["median_features"] = {k: round(v, 4) for k, v in median_feats.items()
                                      if isinstance(v, float)}
        programs[species] = params

        if verbose:
            print(f"  {species:<25} n={len(feat_list):4d}  "
                  f"growth×{params['growth_rate_multiplier']:.2f}  "
                  f"stiff×{params['stiffness_multiplier']:.2f}  "
                  f"div×{params['division_size_multiplier']:.2f}  "
                  f"noise={params['noise_strength']:.4f}")

    with open(OUTPUT_PATH, "w") as f:
        json.dump(programs, f, indent=2)

    if verbose:
        print(f"\nSaved {len(programs)} species programs → {OUTPUT_PATH.name}")

    return programs


if __name__ == "__main__":
    print("Fitting GrowthProgram parameters from registry...")
    run()

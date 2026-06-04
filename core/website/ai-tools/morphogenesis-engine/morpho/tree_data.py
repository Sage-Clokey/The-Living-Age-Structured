"""
morpho/tree_data.py

Loads real tree growth data from archive.zip and converts it into
GrowthProgram instances that guide the morphogenesis simulation.

Data sources inside archive.zip
--------------------------------
  field_survey.geojson  — 3,602 surveyed trees: species, DBH (mm),
                          height (m), plot number.
  als/plot_NN.las        — Airborne LiDAR scans per plot.
                           classification 2 = ground, 5 = high vegetation.

Public API
----------
ARCHIVE_PATH                   default path  (archive.zip beside main.py)
get_species_list(archive_path) list[SpeciesStats]  sorted by count
species_to_program(species, …) GrowthProgram  from field-survey profile
get_plot_stats(plot_id, …)     PlotCrownStats from LiDAR
plot_to_program(plot_id, …)    GrowthProgram  from LiDAR crown profile
"""

from __future__ import annotations

import io
import json
import math
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np

from morpho.program import GrowthProgram

# ---------------------------------------------------------------------------
# Default archive location — sits next to main.py, one level above morpho/
# ---------------------------------------------------------------------------

ARCHIVE_PATH: Path = Path(__file__).parent.parent / "archive.zip"

# ---------------------------------------------------------------------------
# Biological trait table
# Each species entry encodes known silvicultural / dendrological properties
# as multiplier factors applied on top of data-derived base values.
#
#   branching_mul  →  division_size_multiplier  (lower = more divisions)
#   stiffness_mul  →  stiffness_multiplier
#   adhesion_mul   →  adhesion_multiplier
#   noise_mul      →  noise_strength scale factor
# ---------------------------------------------------------------------------

_SPECIES_TRAITS: Dict[str, Dict[str, float]] = {
    # Conifers: high stiffness, dense branching, narrow crowns
    "Spruce": {"branching_mul": 0.60, "stiffness_mul": 1.8, "adhesion_mul": 0.9,  "noise_mul": 0.8},
    "Fir":    {"branching_mul": 0.55, "stiffness_mul": 2.0, "adhesion_mul": 0.7,  "noise_mul": 0.7},
    "Pine":   {"branching_mul": 0.65, "stiffness_mul": 1.6, "adhesion_mul": 0.8,  "noise_mul": 1.0},
    # Broadleaves: variable stiffness, wider crowns, more adhesion
    "Birch":  {"branching_mul": 0.72, "stiffness_mul": 1.2, "adhesion_mul": 1.2,  "noise_mul": 1.2},
    "Aspen":  {"branching_mul": 0.78, "stiffness_mul": 1.0, "adhesion_mul": 1.8,  "noise_mul": 1.3},
    "Tilia":  {"branching_mul": 0.68, "stiffness_mul": 1.1, "adhesion_mul": 1.0,  "noise_mul": 1.0},
    "Alder":  {"branching_mul": 0.75, "stiffness_mul": 0.8, "adhesion_mul": 2.0,  "noise_mul": 1.2},
    "Willow": {"branching_mul": 0.78, "stiffness_mul": 0.5, "adhesion_mul": 2.5,  "noise_mul": 1.5},
    "Elm":    {"branching_mul": 0.70, "stiffness_mul": 1.3, "adhesion_mul": 1.6,  "noise_mul": 1.1},
}
_DEFAULT_TRAITS: Dict[str, float] = {
    "branching_mul": 0.70, "stiffness_mul": 1.0, "adhesion_mul": 1.0, "noise_mul": 1.0,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class SpeciesStats:
    name: str
    count: int
    dbh_mean: float     # mm — diameter at breast height
    height_mean: float  # m
    hd_ratio: float     # height(m) / dbh(m) — slenderness index


@dataclass
class PlotCrownStats:
    plot_id: int
    crown_max_h: float   # m — 99th-percentile normalised height
    crown_mean_h: float  # m — mean normalised vegetation height
    crown_width: float   # m — 5th–95th-pct XY spread
    hw_ratio: float      # crown_max_h / (crown_width / 2)
    upper_frac: float    # fraction of veg points above 70 % of max height


# ---------------------------------------------------------------------------
# Field survey
# ---------------------------------------------------------------------------

def _load_survey_records(zf: zipfile.ZipFile) -> List[dict]:
    with zf.open("field_survey.geojson") as f:
        data = json.load(f)
    return [feat["properties"] for feat in data["features"]]


def get_species_list(archive_path: Path = ARCHIVE_PATH) -> List[SpeciesStats]:
    """
    Return per-species statistics derived from the field survey.

    Returns
    -------
    list of SpeciesStats sorted by tree count (descending).
    """
    with zipfile.ZipFile(archive_path) as zf:
        records = _load_survey_records(zf)

    bins: Dict[str, Dict[str, list]] = defaultdict(lambda: {"dbh": [], "height": []})
    for r in records:
        sp = r.get("species")
        if not sp:
            continue
        if r.get("dbh") is not None:
            bins[sp]["dbh"].append(r["dbh"])
        if r.get("height") is not None:
            bins[sp]["height"].append(r["height"])

    out = []
    for sp, vals in bins.items():
        dbh_list = vals["dbh"]
        h_list = vals["height"]
        dbh_mean = float(np.mean(dbh_list)) if dbh_list else 0.0
        h_mean = float(np.mean(h_list)) if h_list else 0.0
        hd = h_mean / (dbh_mean / 1000.0) if dbh_mean > 0 else 0.0
        out.append(SpeciesStats(
            name=sp,
            count=len(dbh_list),
            dbh_mean=dbh_mean,
            height_mean=h_mean,
            hd_ratio=hd,
        ))

    return sorted(out, key=lambda s: -s.count)


def species_to_program(
    species: str,
    archive_path: Path = ARCHIVE_PATH,
) -> GrowthProgram:
    """
    Build a GrowthProgram calibrated to a tree species.

    Uses measured DBH and height from the field survey combined with
    species-specific biological traits (stiffness, branching, adhesion).

    Parameter derivation
    --------------------
    growth_rate_multiplier   ← DBH mean (larger trunk ≡ faster past growth)
    anisotropy_strength      ← h/d slenderness (taller relative to width → stronger upward)
    division_size_multiplier ← species branching habit (conifer vs broadleaf)
    stiffness_multiplier     ← species wood stiffness
    adhesion_multiplier      ← species crown spreading tendency
    noise_strength           ← species growth regularity
    """
    sp_list = get_species_list(archive_path)
    stat = next((s for s in sp_list if s.name.lower() == species.strip().lower()), None)
    if stat is None:
        available = ", ".join(s.name for s in sp_list)
        raise ValueError(f"Unknown species '{species}'. Available: {available}")

    traits = _SPECIES_TRAITS.get(stat.name, _DEFAULT_TRAITS)

    # growth_rate_multiplier: DBH 15–40 mm → multiplier 0.6–1.8
    dbh_c = max(15.0, min(40.0, stat.dbh_mean))
    growth_mul = 0.6 + 1.2 * (dbh_c - 15.0) / 25.0

    # anisotropy_strength: h/d ratio 400–1100 → 0.04–0.16
    hd_c = max(400.0, min(1100.0, stat.hd_ratio))
    aniso_str = 0.04 + 0.12 * (hd_c - 400.0) / 700.0

    noise = 0.02 * traits["noise_mul"]

    return GrowthProgram(
        growth_rate_multiplier=round(growth_mul, 3),
        stiffness_multiplier=traits["stiffness_mul"],
        adhesion_multiplier=traits["adhesion_mul"],
        division_size_multiplier=traits["branching_mul"],
        noise_strength=round(noise, 5),
        anisotropy_vector=np.array([0.0, 1.0, 0.0]),
        anisotropy_strength=round(aniso_str, 4),
    )


def describe_species(stat: SpeciesStats) -> str:
    """One-line summary of a SpeciesStats."""
    return (
        f"{stat.name:<10}  n={stat.count:4d}  "
        f"DBH={stat.dbh_mean:5.1f} mm  "
        f"H={stat.height_mean:5.1f} m  "
        f"H/D={stat.hd_ratio:6.0f}"
    )


# ---------------------------------------------------------------------------
# LiDAR (ALS)
# ---------------------------------------------------------------------------

def _compute_crown_stats(las_bytes: bytes, plot_id: int) -> PlotCrownStats:
    """Derive crown metrics from raw LAS file bytes."""
    try:
        import laspy
    except ImportError as exc:
        raise ImportError(
            "laspy is required for LiDAR analysis.  "
            "Install it with:  pip install laspy"
        ) from exc

    las = laspy.read(io.BytesIO(las_bytes))
    z = np.asarray(las.z, dtype=float)
    cls = np.asarray(las.classification, dtype=np.uint8)
    x = np.asarray(las.x, dtype=float)
    y = np.asarray(las.y, dtype=float)

    gnd = cls == 2
    veg = cls == 5

    if not gnd.any() or not veg.any():
        raise ValueError(f"Plot {plot_id}: no ground or vegetation points found.")

    ground_level = float(np.percentile(z[gnd], 10))   # robust ground estimate
    norm_veg = z[veg] - ground_level

    crown_max_h = float(np.percentile(norm_veg, 99))
    crown_mean_h = float(np.mean(norm_veg))

    x_spread = float(np.percentile(x[veg], 95) - np.percentile(x[veg], 5))
    y_spread = float(np.percentile(y[veg], 95) - np.percentile(y[veg], 5))
    crown_width = (x_spread + y_spread) / 2.0

    hw_ratio = crown_max_h / (crown_width / 2.0) if crown_width > 0 else 1.0
    upper_frac = float(np.mean(norm_veg > crown_max_h * 0.70))

    return PlotCrownStats(
        plot_id=plot_id,
        crown_max_h=crown_max_h,
        crown_mean_h=crown_mean_h,
        crown_width=crown_width,
        hw_ratio=hw_ratio,
        upper_frac=upper_frac,
    )


def get_plot_stats(
    plot_id: int,
    archive_path: Path = ARCHIVE_PATH,
) -> PlotCrownStats:
    """
    Load and return LiDAR crown statistics for one plot (1–10).

    Reads the LAS file directly from the zip (no extraction needed).
    """
    if not 1 <= plot_id <= 10:
        raise ValueError(f"plot_id must be between 1 and 10, got {plot_id}")
    las_name = f"als/plot_{plot_id:02d}.las"
    with zipfile.ZipFile(archive_path) as zf:
        with zf.open(las_name) as f:
            data = f.read()
    return _compute_crown_stats(data, plot_id)


def plot_to_program(
    plot_id: int,
    archive_path: Path = ARCHIVE_PATH,
) -> GrowthProgram:
    """
    Build a GrowthProgram from LiDAR crown statistics for one plot.

    Crown metric → simulation parameter
    ------------------------------------
    crown_max_h   → anisotropy_strength      (taller canopy → stronger upward)
    upper_frac    → division_size_multiplier (dense upper layer → more branching)
    hw_ratio      → adhesion_multiplier      (narrow → low adhesion; wide → high)
    crown_mean_h  → growth_rate_multiplier

    Parameters
    ----------
    plot_id : int  1–10 matching als/plot_NN.las in archive.zip
    """
    stats = get_plot_stats(plot_id, archive_path)

    # anisotropy_strength: max height 23–32 m → 0.05–0.15
    aniso_str = 0.05 + 0.10 * (stats.crown_max_h - 23.0) / 9.0
    aniso_str = round(max(0.04, min(0.16, aniso_str)), 4)

    # division_size_multiplier: upper_frac 0.30–0.85 → 0.85–0.52
    div_mul = 0.85 - 0.33 * (stats.upper_frac - 0.30) / 0.55
    div_mul = round(max(0.50, min(0.90, div_mul)), 3)

    # adhesion_multiplier: hw_ratio 0.56–0.81 → 1.8–0.6
    adh_mul = 1.8 - 1.2 * (stats.hw_ratio - 0.56) / 0.25
    adh_mul = round(max(0.5, min(2.0, adh_mul)), 3)

    # growth_rate_multiplier: mean height 12–24 m → 0.7–1.5
    growth_mul = 0.7 + 0.8 * (stats.crown_mean_h - 12.0) / 12.0
    growth_mul = round(max(0.5, min(1.8, growth_mul)), 3)

    return GrowthProgram(
        growth_rate_multiplier=growth_mul,
        stiffness_multiplier=1.2,
        adhesion_multiplier=adh_mul,
        division_size_multiplier=div_mul,
        noise_strength=0.025,
        anisotropy_vector=np.array([0.0, 1.0, 0.0]),
        anisotropy_strength=aniso_str,
    )


# ---------------------------------------------------------------------------
# Crown envelope specifications
# ---------------------------------------------------------------------------

# Per-species crown shape descriptors (from dendrological literature):
#   shape   — 'conifer' (conical, widest at base), 'broadleaf' (spheroidal,
#               widest in middle), 'spreading' (wide throughout)
#   R_max   — maximum XZ radius in simulation units
#   param   — shape exponent (higher → tighter taper for conifers;
#               lower → wider/flatter spheroid for broadleaves)
#   y_height— total crown height in simulation units (sets envelope scale)
_CROWN_SPECS: Dict[str, Tuple[str, float, float, float]] = {
    # Conifers — conical: wide at base (h=0), tapers to apex (h=1).
    # y_height ≈ 12 calibrated to actual simulation cell height (~9-11 units).
    # Steeper taper_p → narrower cone shape.
    "Spruce": ("conifer",    7.0, 1.10, 12.0),  # classic Christmas-tree cone
    "Fir":    ("conifer",    5.5, 1.40, 12.0),  # narrowest, sharpest taper
    "Pine":   ("conifer",    8.5, 0.85, 11.0),  # open, rounded cone
    # Broadleaves — spheroidal: narrow trunk (h≈0), wide crown (h≈0.5), narrow apex.
    # sin(π h)^p with lower p → wider, flatter crown.
    "Birch":  ("broadleaf",  9.0, 0.75, 12.0),  # airy spheroid
    "Aspen":  ("broadleaf", 11.0, 0.65, 12.0),  # widest rounded crown
    "Tilia":  ("broadleaf",  8.0, 0.85, 12.0),  # dense teardrop
    # Spreading — broad throughout height: stays wide, gentle taper at apex.
    "Alder":  ("spreading", 10.0, 1.0,  12.0),  # irregular, multi-stem
    "Willow": ("spreading", 12.0, 1.0,  12.0),  # widest, low and drooping
    "Elm":    ("spreading", 10.5, 1.0,  12.0),  # vase-shaped spread
}
_DEFAULT_CROWN_SPEC: Tuple[str, float, float, float] = ("broadleaf", 9.0, 0.75, 12.0)


def make_envelope_fn(
    species_name: str,
) -> Tuple[Callable[[float], float], float]:
    """
    Return ``(envelope_fn, y_height)`` for the named species.

    ``envelope_fn(h_norm)`` gives the maximum allowed XZ radius (simulation
    units) at normalised crown height ``h_norm ∈ [0, 1]``.

    Shape families
    --------------
    conifer   — r = R * (1 − h)^p      (widest at base, tapers to apex)
    broadleaf — r = R * sin(π h)^p     (widest in middle, 0 at base & tip)
    spreading — r = R * (1 − 0.5 h^1.2)  (wide, gentle taper at top)
    """
    spec = _CROWN_SPECS.get(species_name.strip().title(), _DEFAULT_CROWN_SPEC)
    shape, R, p, y_height = spec

    if shape == "conifer":
        def fn(h: float, _R: float = R, _p: float = p) -> float:
            return _R * max(0.0, (1.0 - h) ** _p)
    elif shape == "broadleaf":
        def fn(h: float, _R: float = R, _p: float = p) -> float:
            return _R * (math.sin(math.pi * max(0.0, min(1.0, h)))) ** _p
    else:  # spreading
        def fn(h: float, _R: float = R) -> float:
            return _R * max(0.0, 1.0 - 0.50 * h ** 1.2)

    return fn, y_height


def make_plot_envelope_fn(
    plot_id: int,
    archive_path: Path = ARCHIVE_PATH,
) -> Tuple[Callable[[float], float], float]:
    """
    Return ``(envelope_fn, y_height)`` derived from a plot's LiDAR crown profile.

    The H/W ratio from the ALS scan determines whether the dominant
    canopy structure is narrow-columnar (conifer-like) or wide-spreading.
    """
    stats = get_plot_stats(plot_id, archive_path)
    hw = stats.hw_ratio   # 0.56 – 0.81 across the 10 plots
    y_height = 12.0

    # R_max: narrow canopy (high hw) → smaller lateral extent
    R_max = (y_height / hw) * 0.60

    if hw >= 0.75:
        # Narrow, tall canopy → conical envelope
        p = 0.5 + (hw - 0.75) * 5.0   # ~[0.50, 0.80]
        def fn(h: float, _R: float = R_max, _p: float = p) -> float:
            return _R * max(0.0, (1.0 - h) ** _p)
    elif hw >= 0.65:
        # Intermediate → spheroidal
        p = 0.65 + stats.upper_frac * 0.25
        def fn(h: float, _R: float = R_max, _p: float = p) -> float:
            return _R * (math.sin(math.pi * max(0.0, min(1.0, h)))) ** _p
    else:
        # Wide, spreading canopy
        def fn(h: float, _R: float = R_max) -> float:
            return _R * max(0.0, 1.0 - 0.45 * h ** 1.1)

    return fn, y_height


def describe_plot_stats(stats: PlotCrownStats) -> str:
    """One-line summary of a PlotCrownStats."""
    return (
        f"Plot {stats.plot_id:2d}  "
        f"max_h={stats.crown_max_h:.1f} m  "
        f"mean_h={stats.crown_mean_h:.1f} m  "
        f"width={stats.crown_width:.1f} m  "
        f"H/W={stats.hw_ratio:.2f}  "
        f"upper_dens={stats.upper_frac:.3f}"
    )

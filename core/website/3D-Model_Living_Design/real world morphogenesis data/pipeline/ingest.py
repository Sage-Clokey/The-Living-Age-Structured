"""
pipeline/ingest.py

Scans all known data sources and the data/new/ drop folder,
extracts features from any unprocessed scan, and updates registry.json.

Supported sources:
  chickpea_3D_zenodo/    — PLY files, extracts week number from filename
  pheno4d_maize_tomato/  — TXT files inside Pheno4D.zip, grouped by plant
  maizefield3d_hf/       — ZIP of PLY files (uses 10k subsample)
  crops3d_8species/      — ZIP of PLY/TXT files
  data/new/              — drop any .ply or .txt file here → auto-ingested

Run:
  python pipeline/ingest.py

Adding new data:
  - Drop new .ply or .txt point cloud files into  data/new/<species>/
  - Or unzip directly into data/<source_name>/
  - Re-run ingest.py — only new files are processed
"""

from __future__ import annotations

import io
import re
import sys
import zipfile
from pathlib import Path

# Allow running from anywhere
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline import extract, registry

BASE = Path(__file__).parent.parent
DATA_DIR = BASE / "data"


# ---------------------------------------------------------------------------
# Filename parsers
# ---------------------------------------------------------------------------

def _parse_chickpea(name: str) -> tuple[str, str, int | None]:
    """
    Parse chickpea filename → (species, plant_id, timestep).
    Examples:
      PUSA76_4_groundtruth_pointcloud.ply  → ('Chickpea_PUSA76', 'PUSA76_4', None)
      PBASlasher_S2s_Wk4_pointcloud.ply   → ('Chickpea_PBASlasher', 'PBASlasher_S2s', 4)
    """
    stem = Path(name).stem
    parts = stem.split("_")
    genotype = parts[0]
    species = f"Chickpea_{genotype}"

    # Weekly scan: contains WkN
    wk_match = re.search(r"Wk(\d+)", stem)
    timestep = int(wk_match.group(1)) if wk_match else None

    # Plant ID: first two underscore-joined parts
    plant_id = "_".join(parts[:2]) if len(parts) >= 2 else parts[0]

    return species, plant_id, timestep


def _parse_pheno4d(name: str) -> tuple[str, str, int]:
    """
    Parse Pheno4D path → (species, plant_id, timestep_day).
    Example: Pheno4D/Maize01/M01_0313_a.txt → ('Maize', 'Maize01', 313)
    """
    parts = Path(name).parts
    plant_id = parts[1] if len(parts) >= 2 else "unknown"  # e.g. 'Maize01'
    species = re.sub(r"\d+", "", plant_id)  # 'Maize'

    # Extract day number from filename: M01_0313_a → 313
    day_match = re.search(r"_(\d{4})", Path(name).stem)
    timestep = int(day_match.group(1)) if day_match else 0

    return species, plant_id, timestep


def _parse_new(path: Path) -> tuple[str, str, int | None]:
    """
    Parse a file from data/new/.
    Folder name = species if present, else 'Unknown'.
    """
    species = path.parent.name if path.parent.name != "new" else "Unknown"
    plant_id = path.stem
    return species, plant_id, None


# ---------------------------------------------------------------------------
# Source processors
# ---------------------------------------------------------------------------

def _ingest_chickpea(reg: dict, verbose: bool = True) -> int:
    """Process chickpea_3D_zenodo/chickpea_3D.zip (point clouds only)."""
    zip_path = BASE / "chickpea_3D_zenodo" / "chickpea_3D.zip"
    if not zip_path.exists():
        return 0

    added = 0
    with zipfile.ZipFile(zip_path) as zf:
        ply_files = [n for n in zf.namelist()
                     if n.endswith(".ply") and "pointcloud" in n]
        for name in ply_files:
            # Use zip path as the stable "file path" for registry
            virtual_path = zip_path / name
            if registry.is_registered(reg, virtual_path):
                continue
            try:
                with zf.open(name) as f:
                    tmp = Path(f"/tmp/_morph_{Path(name).name}")
                    tmp.write_bytes(f.read())
                feats = extract.extract_features(tmp)
                tmp.unlink(missing_ok=True)
                species, plant_id, timestep = _parse_chickpea(name)
                registry.add(reg, virtual_path, "chickpea", feats,
                             species=species, plant_id=plant_id,
                             timestep=timestep)
                added += 1
                if verbose:
                    print(f"  + chickpea: {name}")
            except Exception as e:
                print(f"  ! chickpea {name}: {e}")
    return added


def _ingest_pheno4d(reg: dict, verbose: bool = True) -> int:
    """Process pheno4d_maize_tomato/Pheno4D.zip (annotated TXT files only)."""
    zip_path = BASE / "pheno4d_maize_tomato" / "Pheno4D.zip"
    if not zip_path.exists():
        return 0

    added = 0
    with zipfile.ZipFile(zip_path) as zf:
        # Only annotated files (_a suffix = have organ labels)
        txt_files = [n for n in zf.namelist()
                     if n.endswith(".txt") and "_a." in n]
        for name in txt_files:
            virtual_path = zip_path / name
            if registry.is_registered(reg, virtual_path):
                continue
            try:
                with zf.open(name) as f:
                    tmp = Path(f"/tmp/_morph_{Path(name).name}")
                    tmp.write_bytes(f.read())
                feats = extract.extract_features(tmp, subsample=30_000)
                tmp.unlink(missing_ok=True)
                species, plant_id, timestep = _parse_pheno4d(name)
                registry.add(reg, virtual_path, "pheno4d", feats,
                             species=species, plant_id=plant_id,
                             timestep=timestep)
                added += 1
                if verbose:
                    print(f"  + pheno4d: {plant_id} day {timestep}")
            except Exception as e:
                print(f"  ! pheno4d {name}: {e}")
    return added


def _ingest_maizefield(reg: dict, verbose: bool = True) -> int:
    """Process MaizeField3D 10k-point subsample zip."""
    zip_path = (BASE / "maizefield3d_hf" / "datasets"
                / "FielGrwon_ZeaMays_RawPCD_10k.zip")
    if not zip_path.exists():
        return 0

    added = 0
    with zipfile.ZipFile(zip_path) as zf:
        ply_files = [n for n in zf.namelist() if n.endswith(".ply")]
        for name in ply_files:
            virtual_path = zip_path / name
            if registry.is_registered(reg, virtual_path):
                continue
            try:
                with zf.open(name) as f:
                    tmp = Path(f"/tmp/_morph_{Path(name).name}")
                    tmp.write_bytes(f.read())
                feats = extract.extract_features(tmp)
                tmp.unlink(missing_ok=True)
                plant_id = Path(name).stem
                registry.add(reg, virtual_path, "maizefield3d", feats,
                             species="Maize", plant_id=plant_id)
                added += 1
                if verbose:
                    print(f"  + maizefield3d: {plant_id}")
            except Exception as e:
                print(f"  ! maizefield3d {name}: {e}")
    return added


def _ingest_new(reg: dict, verbose: bool = True) -> int:
    """Process any .ply or .txt files dropped into data/new/."""
    new_dir = DATA_DIR / "new"
    if not new_dir.exists():
        return 0

    added = 0
    for path in sorted(new_dir.rglob("*")):
        if path.suffix.lower() not in (".ply", ".txt", ".csv"):
            continue
        if registry.is_registered(reg, path):
            continue
        try:
            feats = extract.extract_features(path)
            species, plant_id, timestep = _parse_new(path)
            registry.add(reg, path, "new", feats,
                         species=species, plant_id=plant_id,
                         timestep=timestep)
            added += 1
            if verbose:
                print(f"  + new: {path.name} (species={species})")
        except Exception as e:
            print(f"  ! new {path.name}: {e}")
    return added


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(verbose: bool = True) -> dict:
    reg = registry.load()
    before = len(reg)

    if verbose:
        print(registry.summary(reg))
        print("Scanning for new files...")

    total = 0
    total += _ingest_chickpea(reg, verbose)
    total += _ingest_pheno4d(reg, verbose)
    total += _ingest_maizefield(reg, verbose)
    total += _ingest_new(reg, verbose)

    registry.save(reg)

    if verbose:
        print(f"\nDone. Added {total} new scans ({before} → {len(reg)} total).")
        print(registry.summary(reg))

    return reg


if __name__ == "__main__":
    run()

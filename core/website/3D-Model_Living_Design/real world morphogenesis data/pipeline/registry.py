"""
pipeline/registry.py

Persistent JSON registry of every processed scan.

Schema per entry:
  scan_id       — sha1 of the file path (stable identifier)
  path          — absolute path to source file
  source        — dataset name (chickpea, pheno4d, maizefield3d, crops3d, new)
  species       — inferred species name if detectable from filename
  plant_id      — plant identifier within dataset (e.g. "Maize01")
  timestep      — numeric day/week index for time-series data (None if static)
  features      — dict of extracted morphological features
  processed_at  — ISO timestamp

Adding new data: just drop files into data/<source>/ or data/new/ and
run ingest.py — new files are hashed and only unprocessed ones are added.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REGISTRY_PATH = Path(__file__).parent.parent / "registry.json"


def _scan_id(path: Path) -> str:
    return hashlib.sha1(str(path).encode()).hexdigest()[:16]


def load() -> dict:
    if REGISTRY_PATH.exists():
        with open(REGISTRY_PATH) as f:
            return json.load(f)
    return {}


def save(registry: dict) -> None:
    with open(REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2)


def add(
    registry: dict,
    path: Path,
    source: str,
    features: dict,
    species: Optional[str] = None,
    plant_id: Optional[str] = None,
    timestep: Optional[int] = None,
) -> str:
    scan_id = _scan_id(path)
    registry[scan_id] = {
        "scan_id": scan_id,
        "path": str(path),
        "source": source,
        "species": species,
        "plant_id": plant_id,
        "timestep": timestep,
        "features": features,
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }
    return scan_id


def is_registered(registry: dict, path: Path) -> bool:
    return _scan_id(path) in registry


def get_sequences(registry: dict, source: Optional[str] = None) -> dict:
    """
    Group registry entries into temporal sequences by plant_id.

    Returns dict: {plant_id: [sorted list of entries by timestep]}
    Only includes entries that have a timestep value.
    """
    sequences: dict = {}
    for entry in registry.values():
        if entry.get("timestep") is None:
            continue
        if source and entry.get("source") != source:
            continue
        pid = entry.get("plant_id", "unknown")
        sequences.setdefault(pid, []).append(entry)
    for pid in sequences:
        sequences[pid].sort(key=lambda e: e["timestep"])
    return sequences


def get_by_source(registry: dict, source: str) -> list:
    return [e for e in registry.values() if e.get("source") == source]


def summary(registry: dict) -> str:
    from collections import Counter
    sources = Counter(e.get("source", "?") for e in registry.values())
    lines = [f"Registry: {len(registry)} scans total"]
    for src, count in sorted(sources.items()):
        lines.append(f"  {src}: {count}")
    return "\n".join(lines)

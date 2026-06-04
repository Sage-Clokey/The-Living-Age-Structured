"""
pipeline/extract.py

Extracts morphological features from a single point cloud scan.
Works with PLY (chickpea, MaizeField3D) and TXT (Pheno4D) formats.

All coordinates are normalized within-scan so different scans are
comparable regardless of absolute position.

Output features (all unitless after normalization):
  height          — normalized crown height (max axis - min along height axis)
  width           — mean lateral spread (5th–95th pct, XZ or XY)
  hw_ratio        — height / (width / 2) — slenderness index
  upper_density   — fraction of points above 70% of height
  spread_asymm    — std of lateral distances from centroid (branching asymmetry)
  point_count     — raw number of points (proxy for surface complexity)
  organ_ratio     — ratio of non-stem points to total (labeled data only)
"""

from __future__ import annotations

import struct
from pathlib import Path
from typing import Optional
import numpy as np


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def _load_ply(path: Path) -> np.ndarray:
    """Load XYZ from a PLY file (ASCII or binary). Returns (N, 3) array."""
    with open(path, "rb") as f:
        raw = f.read()

    # Parse header
    header_end = raw.find(b"end_header\n")
    if header_end == -1:
        header_end = raw.find(b"end_header\r\n")
        header_offset = header_end + 12
    else:
        header_offset = header_end + 11

    header = raw[:header_end].decode("ascii", errors="replace")
    is_binary_little = "format binary_little_endian" in header
    is_binary_big = "format binary_big_endian" in header

    # Count vertices
    n_verts = 0
    props = []
    in_vertex = False
    for line in header.split("\n"):
        line = line.strip()
        if line.startswith("element vertex"):
            n_verts = int(line.split()[-1])
            in_vertex = True
        elif line.startswith("element") and in_vertex:
            in_vertex = False
        elif line.startswith("property") and in_vertex:
            parts = line.split()
            props.append((parts[1], parts[2]))  # (type, name)

    if n_verts == 0:
        return np.empty((0, 3), dtype=np.float32)

    if is_binary_little or is_binary_big:
        # Build struct format
        type_map = {
            "float": "f", "float32": "f",
            "double": "d", "float64": "d",
            "int": "i", "int32": "i",
            "uint": "I", "uint32": "I",
            "uchar": "B", "uint8": "B",
            "char": "b", "int8": "b",
            "short": "h", "int16": "h",
            "ushort": "H", "uint16": "H",
        }
        fmt = ("<" if is_binary_little else ">") + "".join(
            type_map.get(t, "f") for t, _ in props
        )
        row_size = struct.calcsize(fmt)
        body = raw[header_offset:]
        rows = []
        for i in range(n_verts):
            row = struct.unpack_from(fmt, body, i * row_size)
            rows.append(row[:3])  # x, y, z
        return np.array(rows, dtype=np.float32)
    else:
        # ASCII
        body = raw[header_offset:].decode("ascii", errors="replace")
        lines = [l.strip() for l in body.split("\n") if l.strip()]
        pts = []
        for line in lines[:n_verts]:
            vals = line.split()
            pts.append([float(vals[0]), float(vals[1]), float(vals[2])])
        return np.array(pts, dtype=np.float32)


def _load_txt(path: Path) -> tuple[np.ndarray, Optional[np.ndarray]]:
    """
    Load Pheno4D-format TXT: x y z [label1 [label2]].
    Returns (xyz array, labels array or None).
    """
    data = np.loadtxt(path, dtype=np.float32)
    if data.ndim == 1:
        data = data[np.newaxis, :]
    xyz = data[:, :3]
    labels = data[:, 3].astype(np.int32) if data.shape[1] >= 4 else None
    return xyz, labels


# ---------------------------------------------------------------------------
# Feature extraction
# ---------------------------------------------------------------------------

def _height_axis(xyz: np.ndarray) -> int:
    """Return index of the axis with greatest range (the 'height' axis)."""
    ranges = xyz.max(axis=0) - xyz.min(axis=0)
    return int(np.argmax(ranges))


def extract_features(path: Path, subsample: int = 50_000) -> dict:
    """
    Extract morphological features from any supported point cloud file.

    Parameters
    ----------
    path : Path
        .ply or .txt point cloud file.
    subsample : int
        Max points to use (random subsample for speed on large files).

    Returns
    -------
    dict with numeric feature values and metadata.
    """
    path = Path(path)
    suffix = path.suffix.lower()
    labels = None

    if suffix == ".ply":
        xyz = _load_ply(path)
    elif suffix in (".txt", ".csv"):
        xyz, labels = _load_txt(path)
    else:
        raise ValueError(f"Unsupported format: {suffix}")

    if len(xyz) == 0:
        return {"error": "empty point cloud", "path": str(path)}

    # Subsample for speed
    if len(xyz) > subsample:
        idx = np.random.choice(len(xyz), subsample, replace=False)
        xyz = xyz[idx]
        if labels is not None:
            labels = labels[idx]

    # Normalize: translate so min of each axis = 0
    xyz = xyz - xyz.min(axis=0)

    # Identify height axis (greatest range)
    h_axis = _height_axis(xyz)
    lateral_axes = [i for i in range(3) if i != h_axis]

    h_vals = xyz[:, h_axis]
    lat_x = xyz[:, lateral_axes[0]]
    lat_z = xyz[:, lateral_axes[1]]

    height = float(h_vals.max() - h_vals.min())
    width_x = float(np.percentile(lat_x, 95) - np.percentile(lat_x, 5))
    width_z = float(np.percentile(lat_z, 95) - np.percentile(lat_z, 5))
    width = (width_x + width_z) / 2.0
    hw_ratio = height / (width / 2.0) if width > 0 else 1.0

    # Upper density: fraction of points above 70% of height
    upper_density = float(np.mean(h_vals > 0.70 * height))

    # Spread asymmetry: std of distance from lateral centroid
    cx = float(np.mean(lat_x))
    cz = float(np.mean(lat_z))
    dist_from_center = np.sqrt((lat_x - cx) ** 2 + (lat_z - cz) ** 2)
    spread_asymm = float(np.std(dist_from_center) / (width + 1e-6))

    # Organ ratio from labels (0 = stem/background, >0 = leaves/branches)
    organ_ratio = None
    if labels is not None:
        organ_ratio = float(np.mean(labels > 0))

    features = {
        "height": round(height, 4),
        "width": round(width, 4),
        "hw_ratio": round(hw_ratio, 4),
        "upper_density": round(upper_density, 4),
        "spread_asymm": round(spread_asymm, 4),
        "point_count": len(xyz),
        "height_axis": h_axis,
    }
    if organ_ratio is not None:
        features["organ_ratio"] = round(organ_ratio, 4)

    return features

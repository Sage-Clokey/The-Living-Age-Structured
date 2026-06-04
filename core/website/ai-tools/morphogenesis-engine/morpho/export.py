"""
morpho/export.py

Mesh export utilities.

Saves meshes to the outputs/ directory.  Supports OBJ (default),
STL, and PLY formats.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

# Resolve the outputs/ directory relative to this package
_PACKAGE_ROOT = Path(__file__).parent.parent
_OUTPUTS_DIR = _PACKAGE_ROOT / "outputs"


def _ensure_outputs_dir() -> Path:
    """Create the outputs/ directory if it does not exist."""
    _OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    return _OUTPUTS_DIR


def export_mesh(
    mesh: object,
    filename: str,
    output_dir: Optional[str] = None,
) -> Path:
    """
    Save a trimesh.Trimesh to disk.

    Parameters
    ----------
    mesh : trimesh.Trimesh
        The mesh to export.
    filename : str
        Target filename, e.g. ``"organism.obj"``.  The file extension
        determines the format (obj / stl / ply).
    output_dir : str | None
        Directory to write to.  Defaults to the project's ``outputs/``
        folder.

    Returns
    -------
    Path
        Absolute path of the written file.

    Raises
    ------
    ImportError
        If trimesh is not installed.
    ValueError
        If the file extension is not supported.
    """
    try:
        import trimesh  # noqa: F401
    except ImportError:
        raise ImportError(
            "trimesh is required for mesh export.  "
            "Install it with:  pip install trimesh"
        )

    supported = {".obj", ".stl", ".ply", ".glb", ".gltf"}
    ext = Path(filename).suffix.lower()
    if ext not in supported:
        raise ValueError(
            f"Unsupported file format '{ext}'.  "
            f"Supported: {', '.join(sorted(supported))}"
        )

    if output_dir is None:
        out_dir = _ensure_outputs_dir()
    else:
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / filename

    mesh.export(str(out_path))
    return out_path.resolve()


def export_mesh_obj(mesh: object, filename: str = "organism.obj") -> Path:
    """Convenience wrapper: export as OBJ to outputs/."""
    return export_mesh(mesh, filename)


def export_mesh_stl(mesh: object, filename: str = "organism.stl") -> Path:
    """Convenience wrapper: export as STL to outputs/."""
    return export_mesh(mesh, filename)

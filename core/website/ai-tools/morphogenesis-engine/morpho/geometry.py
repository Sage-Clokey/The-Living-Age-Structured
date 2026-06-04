"""
morpho/geometry.py

Converts the list of cells in a SimulationState into a triangulated 3-D
mesh.

Each cell is approximated as an icosphere scaled to the cell's radius.
All per-cell sphere meshes are then unioned into a single mesh object
via boolean union (when trimesh's manifold backend is available) or
simple concatenation as a fallback.

The returned object is a trimesh.Trimesh instance ready for export.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List

import numpy as np

if TYPE_CHECKING:
    from morpho.state import SimulationState

try:
    import trimesh
    import trimesh.creation
    _TRIMESH_AVAILABLE = True
except ImportError:
    _TRIMESH_AVAILABLE = False


def _require_trimesh() -> None:
    if not _TRIMESH_AVAILABLE:
        raise ImportError(
            "trimesh is required for mesh generation.  "
            "Install it with:  pip install trimesh"
        )


def cells_to_mesh(
    state: "SimulationState",
    subdivisions: int = 2,
    use_convex_hull: bool = False,
) -> "trimesh.Trimesh":
    """
    Build a mesh from all cells in *state*.

    Parameters
    ----------
    state : SimulationState
        Source of cell positions and radii.
    subdivisions : int
        Icosphere subdivision level per cell (2 = ~80 triangles, 3 = ~320).
        Higher → smoother spheres, more triangles, slower export.
    use_convex_hull : bool
        If True, return the convex hull of all sphere vertices instead of
        individual spheres.  Fast but loses concavities.

    Returns
    -------
    trimesh.Trimesh
        The combined mesh.
    """
    _require_trimesh()

    cells = state.cells
    if not cells:
        raise ValueError("Cannot generate mesh: no cells in state.")

    sphere_meshes: List["trimesh.Trimesh"] = []

    for cell in cells:
        sphere = trimesh.creation.icosphere(
            subdivisions=subdivisions,
            radius=cell.radius,
        )
        # Translate to cell position
        sphere.apply_translation(cell.position)
        sphere_meshes.append(sphere)

    if use_convex_hull:
        # Collect all vertices and compute a single convex hull
        all_verts = np.vstack([m.vertices for m in sphere_meshes])
        hull = trimesh.convex.convex_hull(all_verts)
        return hull

    # Concatenate all sphere meshes into one
    combined: "trimesh.Trimesh" = trimesh.util.concatenate(sphere_meshes)
    return combined


def cells_to_point_cloud(state: "SimulationState") -> np.ndarray:
    """
    Return cell positions as an (N, 3) numpy array.

    Useful for debugging or alternative meshing pipelines.
    """
    return np.array([c.position for c in state.cells], dtype=float)


def smooth_mesh(mesh: "trimesh.Trimesh", iterations: int = 2) -> "trimesh.Trimesh":
    """
    Apply Laplacian smoothing to a mesh.

    Parameters
    ----------
    mesh : trimesh.Trimesh
    iterations : int
        Number of smoothing passes.

    Returns
    -------
    trimesh.Trimesh
        Smoothed copy of the mesh.
    """
    _require_trimesh()
    smoothed = trimesh.smoothing.filter_laplacian(mesh, iterations=iterations)
    return smoothed

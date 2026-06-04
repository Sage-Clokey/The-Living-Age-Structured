"""
simulation.py — Core coral morphogenesis engine.

Models tip-based growth inspired by coral polyp biology:

  - Apical meristems (growing tips) extend the coral branch by branch each step.
  - Stochastic direction noise (growth-cone Brownian motion) creates organic curves.
  - Phototropic / gravitropic bias pulls growth toward +Y (light / buoyancy).
  - Lateral budding with configurable probability creates branching topology.
  - Node-to-node collision avoidance models space competition between branches.
  - Radius tapers exponentially with depth (thick trunk → hair-thin tips).

Data model
----------
  positions      : list of (3,) float64 arrays — node world positions
  parent_indices : list of int — parent node index, -1 for the root
  radii          : list of float — absolute tube radius at each node
  depths         : list of int — branch depth level of each node
  active_tips    : list of Tip — currently growing apical ends
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
import pyvista as pv

from config import SimConfig

# VTK tube filter — bundled with every PyVista installation
try:
    from vtkmodules.vtkFiltersCore import vtkTubeFilter
except ImportError:
    from vtk import vtkTubeFilter  # type: ignore[import]


# ---------------------------------------------------------------------------
# Tip data structure
# ---------------------------------------------------------------------------

@dataclass
class Tip:
    """A single active growing tip (apical meristem) of the coral."""

    node_index: int
    """Index into CoralSimulation.positions for this tip's current node."""

    direction: np.ndarray
    """Current unit growth direction vector, shape (3,)."""

    depth: int
    """Branch depth level (0 = root-adjacent; increments each division)."""


# ---------------------------------------------------------------------------
# Simulation class
# ---------------------------------------------------------------------------

class CoralSimulation:
    """
    Biologically inspired coral growth simulation.

    Usage
    -----
    >>> cfg = SimConfig()
    >>> sim = CoralSimulation(cfg)
    >>> while sim.is_alive:
    ...     sim.step()
    >>> mesh = sim.to_polydata()
    """

    def __init__(self, config: SimConfig) -> None:
        self.config = config
        self._rng = np.random.default_rng(config.random_seed)

        # Node arrays (grown incrementally)
        self.positions: List[np.ndarray] = []
        self.parent_indices: List[int] = []
        self.radii: List[float] = []
        self.depths: List[int] = []

        # Active growing fronts
        self.active_tips: List[Tip] = []

        self._initialize()

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def _initialize(self) -> None:
        """
        Seed the simulation with one root node and ``initial_tips`` growing
        tips fanned radially outward and biased upward.

        This mimics a coral larva settling on a substrate and sending out its
        first polyp buds.
        """
        root_idx = self._add_node(position=np.zeros(3), parent=-1, depth=0)

        n = self.config.initial_tips
        for i in range(n):
            # Fan tips evenly around the Y axis, leaning mostly upward
            angle = 2.0 * np.pi * i / n
            direction = np.array([
                np.cos(angle) * 0.45,
                1.0,                    # strong upward component
                np.sin(angle) * 0.45,
            ])
            direction /= np.linalg.norm(direction)
            self.active_tips.append(
                Tip(node_index=root_idx, direction=direction, depth=0)
            )

    # ------------------------------------------------------------------
    # Node management
    # ------------------------------------------------------------------

    def _add_node(
        self,
        position: np.ndarray,
        parent: int,
        depth: int,
    ) -> int:
        """Append a new node, returning its index."""
        idx = len(self.positions)
        self.positions.append(position.copy())
        self.parent_indices.append(parent)
        self.radii.append(self._compute_radius(depth))
        self.depths.append(depth)
        return idx

    def _compute_radius(self, depth: int) -> float:
        """
        Compute tube radius for a node at the given depth.

        Exponential taper mimics vascular tapering in biological organisms:
        thick calcareous base → progressively thinner branches → hair-like tips.
        """
        return self.config.base_radius * (self.config.radius_taper ** depth)

    # ------------------------------------------------------------------
    # Direction computation
    # ------------------------------------------------------------------

    def compute_new_direction(self, direction: np.ndarray) -> np.ndarray:
        """
        Compute the next growth direction from the current one.

        Combines three biological signals:
        1. Persistence — the tip tends to continue in its current direction.
        2. Noise       — growth-cone cytoskeletal stochasticity deflects the tip.
        3. Tropism     — phototropic / gravitropic bias pulls toward +Y (light).

        Parameters
        ----------
        direction : np.ndarray, shape (3,)
            Current normalised growth direction.

        Returns
        -------
        np.ndarray, shape (3,)
            New normalised growth direction.
        """
        noise = self._rng.standard_normal(3) * self.config.turn_noise
        upward = np.array([0.0, 1.0, 0.0]) * self.config.upward_bias

        candidate = direction + noise + upward
        norm = np.linalg.norm(candidate)
        return candidate / norm if norm > 1e-8 else direction.copy()

    def _branch_direction(self, direction: np.ndarray) -> np.ndarray:
        """
        Compute a lateral branch direction at ``branch_angle`` from the
        primary growth direction.

        The deflection plane is chosen at random, mimicking the stochastic
        activation of lateral polyp buds in real coral colonies.

        Parameters
        ----------
        direction : np.ndarray, shape (3,)
            Current (parent) growth direction.

        Returns
        -------
        np.ndarray, shape (3,)
            Normalised lateral branch direction.
        """
        # Build a random vector perpendicular to `direction`
        perp = self._rng.standard_normal(3)
        perp -= perp.dot(direction) * direction
        norm = np.linalg.norm(perp)
        if norm < 1e-8:
            # Edge case: direction is nearly axis-aligned — use a fixed perp
            perp = np.array([1.0, 0.0, 0.0])
            perp -= perp.dot(direction) * direction
            perp /= np.linalg.norm(perp)
        else:
            perp /= norm

        angle = self.config.branch_angle
        branch_dir = direction * np.cos(angle) + perp * np.sin(angle)
        return branch_dir / np.linalg.norm(branch_dir)

    # ------------------------------------------------------------------
    # Collision avoidance
    # ------------------------------------------------------------------

    def check_collision(self, proposed: np.ndarray) -> bool:
        """
        Return True if ``proposed`` is too close to any existing node.

        Vectorised O(N) distance check via numpy broadcasting.

        # TODO: replace with scipy.spatial.cKDTree for O(log N) performance
        # at large node counts (> 2000 nodes).

        Parameters
        ----------
        proposed : np.ndarray, shape (3,)
            Candidate position to test.
        """
        if len(self.positions) < 2:
            return False
        pts = np.array(self.positions, dtype=np.float64)
        dists = np.linalg.norm(pts - proposed, axis=1)
        return bool(np.any(dists < self.config.min_separation))

    # ------------------------------------------------------------------
    # Tip growth
    # ------------------------------------------------------------------

    def grow_tip(self, tip: Tip) -> Tuple[Optional[Tip], Optional[Tip]]:
        """
        Attempt to advance a single tip by one growth step.

        The tip tries up to ``max_retries`` directions to escape a collision.
        If all retries fail, the tip dies (models branch termination due to
        space competition with neighbours).

        Parameters
        ----------
        tip : Tip
            The tip to grow.

        Returns
        -------
        updated_tip : Tip or None
            The advanced tip at the new node. None if growth was blocked.
        branch_tip : Tip or None
            A newly spawned lateral tip, or None if no branch occurred.
        """
        current_pos = self.positions[tip.node_index]

        # Try up to max_retries directions to escape a collision
        new_dir = tip.direction
        proposed_pos: Optional[np.ndarray] = None

        for _ in range(self.config.max_retries):
            new_dir = self.compute_new_direction(new_dir)
            candidate = current_pos + new_dir * self.config.step_size
            if not self.check_collision(candidate):
                proposed_pos = candidate
                break

        if proposed_pos is None:
            return None, None  # tip is blocked — natural branch termination

        new_depth = tip.depth + 1
        new_idx = self._add_node(
            position=proposed_pos,
            parent=tip.node_index,
            depth=new_depth,
        )
        updated_tip = Tip(node_index=new_idx, direction=new_dir, depth=new_depth)

        # Stochastic lateral budding
        branch_tip: Optional[Tip] = None
        if (
            self._rng.random() < self.config.branch_probability
            and len(self.active_tips) < self.config.max_tips
        ):
            branch_dir = self._branch_direction(new_dir)
            branch_tip = Tip(
                node_index=new_idx,
                direction=branch_dir,
                depth=new_depth,
            )

        return updated_tip, branch_tip

    # ------------------------------------------------------------------
    # Simulation step
    # ------------------------------------------------------------------

    def step(self) -> int:
        """
        Advance every active tip by one growth iteration.

        Returns
        -------
        int
            Number of new nodes added this step.
        """
        if not self.active_tips or self.n_nodes >= self.config.max_nodes:
            return 0

        new_tips: List[Tip] = []
        added = 0

        for tip in self.active_tips:
            if self.n_nodes >= self.config.max_nodes:
                break

            updated, branch = self.grow_tip(tip)

            if updated is not None:
                new_tips.append(updated)
                added += 1
                if branch is not None:
                    new_tips.append(branch)
            # Blocked tips are dropped (branch termination)

        self.active_tips = new_tips
        return added

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def n_nodes(self) -> int:
        """Total number of nodes grown so far."""
        return len(self.positions)

    @property
    def is_alive(self) -> bool:
        """True while tips remain active and the node cap is not reached."""
        return bool(self.active_tips) and self.n_nodes < self.config.max_nodes

    # ------------------------------------------------------------------
    # Mesh export
    # ------------------------------------------------------------------

    def to_polydata(self) -> pv.PolyData:
        """
        Convert the node graph to a PyVista tube mesh.

        Each parent→child edge becomes a tube segment whose radius is
        interpolated from the ``radius`` point array using VTK's
        ``VaryRadiusByAbsoluteScalar`` mode — the scalar value at each
        point IS the tube radius in world units.

        This produces accurate biological taper: thick calcareous base,
        progressively finer branches, hair-like growing tips.

        Returns
        -------
        pv.PolyData
            Triangulated tube mesh ready for rendering or export.
        """
        if self.n_nodes < 2:
            return pv.PolyData()

        points = np.array(self.positions, dtype=np.float64)
        radii = np.array(self.radii, dtype=np.float64)

        # Build flat VTK connectivity: [2, parent, child, 2, parent, child, ...]
        lines: List[int] = []
        for i, parent in enumerate(self.parent_indices):
            if parent >= 0:
                lines.extend([2, parent, i])

        if not lines:
            return pv.PolyData()

        pd = pv.PolyData()
        pd.points = points
        pd.lines = np.array(lines, dtype=np.intp)
        pd.point_data["radius"] = radii

        # VTK tube filter with absolute scalar radius
        # SetVaryRadiusToVaryRadiusByAbsoluteScalar() uses the active scalar
        # value as the actual tube radius — not a normalized multiplier.
        tube = vtkTubeFilter()
        tube.SetInputData(pd)
        tube.SetVaryRadiusToVaryRadiusByAbsoluteScalar()
        tube.SetNumberOfSides(8)
        tube.SetCapping(True)
        tube.Update()

        return pv.wrap(tube.GetOutput())

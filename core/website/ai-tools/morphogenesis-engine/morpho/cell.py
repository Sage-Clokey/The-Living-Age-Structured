"""
morpho/cell.py

Defines the Cell class — the fundamental unit of the morphogenesis simulation.
Each cell has physical properties and can grow and divide.
"""

from __future__ import annotations

import numpy as np
from typing import Tuple


_cell_id_counter: int = 0


def _next_id() -> int:
    global _cell_id_counter
    _cell_id_counter += 1
    return _cell_id_counter


class Cell:
    """
    A single biological cell in the simulation.

    Attributes
    ----------
    id : int
        Unique identifier.
    position : np.ndarray, shape (3,)
        World-space position.
    velocity : np.ndarray, shape (3,)
        Current velocity vector.
    radius : float
        Current radius of the cell.
    growth_rate : float
        Rate at which radius increases per unit time.
    division_radius : float
        Radius threshold that triggers division.
    stiffness : float
        How strongly the cell resists compression (repulsion strength).
    adhesion : float
        How strongly the cell sticks to neighbours (adhesion strength).
    age : float
        Elapsed simulation time since birth.
    """

    def __init__(
        self,
        position: np.ndarray,
        radius: float = 0.5,
        growth_rate: float = 0.05,
        division_radius: float = 1.0,
        stiffness: float = 1.0,
        adhesion: float = 0.5,
    ) -> None:
        self.id: int = _next_id()
        self.position: np.ndarray = np.array(position, dtype=float)
        self.velocity: np.ndarray = np.zeros(3, dtype=float)
        self.radius: float = float(radius)
        self.growth_rate: float = float(growth_rate)
        self.division_radius: float = float(division_radius)
        self.stiffness: float = float(stiffness)
        self.adhesion: float = float(adhesion)
        self.age: float = 0.0

    # ------------------------------------------------------------------
    # Growth
    # ------------------------------------------------------------------

    def grow(self, dt: float) -> None:
        """Increase the cell radius by growth_rate * dt."""
        self.radius += self.growth_rate * dt
        self.age += dt

    # ------------------------------------------------------------------
    # Division
    # ------------------------------------------------------------------

    def should_divide(self) -> bool:
        """Return True when the cell has grown large enough to divide."""
        return self.radius >= self.division_radius

    def divide(self) -> "Cell":
        """
        Split this cell into two.

        The parent cell shrinks to half its current radius.  A daughter
        cell is created at a small random offset and inherits the same
        parameters.

        Returns
        -------
        Cell
            The newly created daughter cell.
        """
        self.radius *= 0.5

        # Random unit-vector offset so the daughter is placed nearby
        offset_dir = np.random.randn(3)
        norm = np.linalg.norm(offset_dir)
        if norm < 1e-8:
            offset_dir = np.array([1.0, 0.0, 0.0])
        else:
            offset_dir /= norm

        daughter_pos = self.position + offset_dir * self.radius * 1.2

        daughter = Cell(
            position=daughter_pos,
            radius=self.radius,
            growth_rate=self.growth_rate,
            division_radius=self.division_radius,
            stiffness=self.stiffness,
            adhesion=self.adhesion,
        )
        return daughter

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"Cell(id={self.id}, pos={np.round(self.position, 2)}, "
            f"r={self.radius:.3f})"
        )

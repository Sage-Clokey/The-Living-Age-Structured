"""
morpho/state.py

Defines SimulationState — the single source of truth for the entire
simulation at any instant in time.
"""

from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from morpho.cell import Cell
    from morpho.program import GrowthProgram


class SimulationState:
    """
    Container for all mutable simulation data.

    Attributes
    ----------
    cells : List[Cell]
        All living cells in the simulation.
    time : float
        Accumulated simulation time in seconds.
    program : GrowthProgram | None
        Active growth program.  May be None (no modifiers).
    """

    def __init__(
        self,
        cells: Optional[List["Cell"]] = None,
        program: Optional["GrowthProgram"] = None,
    ) -> None:
        from morpho.cell import Cell  # local import to avoid circularity

        self.cells: List[Cell] = cells if cells is not None else []
        self.time: float = 0.0
        self.program: Optional["GrowthProgram"] = program

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    @property
    def n_cells(self) -> int:
        """Number of cells currently in the simulation."""
        return len(self.cells)

    def add_cell(self, cell: "Cell") -> None:
        """Add a cell to the state, optionally applying the active program."""
        if self.program is not None:
            self.program.apply(cell)
        self.cells.append(cell)

    # ------------------------------------------------------------------
    # Repr
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"SimulationState(t={self.time:.3f}s, "
            f"n_cells={self.n_cells}, "
            f"program={self.program})"
        )

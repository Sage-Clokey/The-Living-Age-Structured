"""
morpho/division.py

Handles cell division logic for the simulation.

Division is checked each timestep after growth.  Cells that have
exceeded their division_radius are split into parent + daughter.
"""

from __future__ import annotations

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from morpho.state import SimulationState


# Maximum cells allowed before division is suppressed (performance guard)
_MAX_CELLS: int = 2000


def handle_divisions(state: "SimulationState") -> int:
    """
    Scan all cells and divide those that have reached their division
    threshold.

    Newly created daughter cells are appended to the state cell list.
    The program is applied to each new daughter so she inherits the
    current growth modifiers.

    Parameters
    ----------
    state : SimulationState
        Modified in-place.

    Returns
    -------
    int
        Number of new cells created this step.
    """
    if len(state.cells) >= _MAX_CELLS:
        return 0

    candidates: List[int] = [
        i for i, c in enumerate(state.cells) if c.should_divide()
    ]

    new_cells = []
    for i in candidates:
        cell = state.cells[i]
        daughter = cell.divide()
        # Daughter inherits the parent's already-modified parameters
        # (growth_rate, stiffness, etc. were set at the parent's birth).
        # Do NOT re-apply the program multipliers — that would compound them
        # exponentially across generations.
        new_cells.append(daughter)

        # Stop if we would exceed the cap
        if len(state.cells) + len(new_cells) >= _MAX_CELLS:
            break

    state.cells.extend(new_cells)
    return len(new_cells)

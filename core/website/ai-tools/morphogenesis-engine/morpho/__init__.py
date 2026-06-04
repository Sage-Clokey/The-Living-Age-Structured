"""
morpho — morphogenetic simulation package.

Public API surface (everything you need for typical use):

    from morpho.cell import Cell
    from morpho.program import GrowthProgram
    from morpho.state import SimulationState
    from morpho.simulation import Simulation
    from morpho.interpreter import interpret, describe_program
    from morpho.geometry import cells_to_mesh
    from morpho.export import export_mesh
"""

from morpho.cell import Cell
from morpho.program import GrowthProgram
from morpho.state import SimulationState
from morpho.simulation import Simulation
from morpho.interpreter import interpret, describe_program
from morpho.geometry import cells_to_mesh
from morpho.export import export_mesh

__all__ = [
    "Cell",
    "GrowthProgram",
    "SimulationState",
    "Simulation",
    "interpret",
    "describe_program",
    "cells_to_mesh",
    "export_mesh",
]

__version__ = "0.1.0"

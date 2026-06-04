"""
grn/ — Gene Regulatory Network layer for the Living Systems Design Lab.

Architecture:
  grn.py      — GRNState dataclass + GRNNetwork (weight-matrix model)
  signals.py  — SignalField (nutrient, inhibitor, morphogen gradients)
  mapper.py   — grn_to_params() maps regulatory state → GrowthParams
  presets.py  — pre-built GRN weight matrices
  runner.py   — GRNRunner integrates GRN updates into the engine loop

The pipeline:
  regulatory state + signal environment
      → update gene activity (GRNNetwork.update)
      → map state to growth behaviour (grn_to_params)
      → run morphogenesis step (MorphogenesisEngine.step)
      → repeat
"""

from .grn      import GRNState, GRNNetwork
from .signals  import SignalField
from .mapper   import grn_to_params
from .presets  import development_grn, morphogen_grn
from .runner   import GRNRunner

__all__ = [
    "GRNState", "GRNNetwork",
    "SignalField",
    "grn_to_params",
    "development_grn", "morphogen_grn",
    "GRNRunner",
]

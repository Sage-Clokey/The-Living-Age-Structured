"""
grn/runner.py — GRN-driven morphogenesis runner.

GRNRunner wraps MorphogenesisEngine and updates the regulatory state
during simulation, coupling the GRN dynamics to growth behaviour.

Update loop:
  for each simulation step:
    1. engine.step()                          — grow tips
    2. every grn_update_interval steps:
       a. compute mean tip position
       b. sample SignalField at that position
       c. GRNNetwork.update(state, signals)   — evolve gene activity
       d. grn_to_params(state, base)          — remap GRN → params
       e. engine.params = new_params          — inject into engine

This connects:
  gene regulatory program → cell behaviour → emergent 3D morphology
"""

from __future__ import annotations

import copy
from typing import List

import numpy as np

from .grn      import GRNNetwork, GRNState
from .signals  import SignalField
from .mapper   import grn_to_params
from .presets  import development_grn

from presets import GrowthParams, tree
from engine  import MorphogenesisEngine


class GRNRunner:
    """
    Morphogenesis engine with coupled GRN dynamics.

    Parameters
    ----------
    base_params          : Starting GrowthParams (mode, seed, etc.)
    grn                  : GRNNetwork instance
    signal_field         : SignalField — spatial signal environment
    init_state           : Starting GRNState (defaults to neutral 0.5)
    grn_update_interval  : How often (in simulation steps) to update the GRN
    """

    def __init__(
        self,
        base_params:         GrowthParams  = None,
        grn:                 GRNNetwork    = None,
        signal_field:        SignalField   = None,
        init_state:          GRNState      = None,
        grn_update_interval: int           = 5,
    ) -> None:
        self.base_params         = base_params or tree()
        self.grn                 = grn or development_grn()
        self.signal_field        = signal_field or SignalField()
        self.grn_state           = init_state or GRNState()
        self.grn_update_interval = grn_update_interval

        self._state_history: List[GRNState] = [copy.copy(self.grn_state)]

    # ── Internal ──────────────────────────────────────────────────────────────

    def _mean_tip_position(self, engine: MorphogenesisEngine) -> np.ndarray:
        alive = [t.position for t in engine.tips if t.alive]
        if not alive:
            return np.zeros(3)
        return np.mean(alive, axis=0)

    def _update_grn(self, mean_pos: np.ndarray) -> None:
        """Sample signals at mean tip position, run one GRN step."""
        signals_3 = self.signal_field.sample(mean_pos)

        # Map 3 spatial signals → 5-gene input vector
        # nutrient   drives growth + branch
        # inhibitor  reinforces adhesion
        # morphogen  triggers differentiation
        signal_input = np.array([
            signals_3[0] * 0.60,   # → growth
            signals_3[0] * 0.40,   # → branch
            signals_3[1] * 0.35,   # → adhesion
            0.00,                   # → polarity (intrinsic; not signal-driven)
            signals_3[2] * 0.55,   # → differentiation
        ])

        self.grn_state = self.grn.update(self.grn_state, signal_input)
        self._state_history.append(copy.copy(self.grn_state))

    # ── Public interface ──────────────────────────────────────────────────────

    def run(self) -> MorphogenesisEngine:
        """
        Run the GRN-driven simulation.

        Returns the completed MorphogenesisEngine (with all segments).
        """
        params = grn_to_params(self.grn_state, self.base_params)
        engine = MorphogenesisEngine(params)

        for step in range(self.base_params.steps):
            if not any(t.alive for t in engine.tips):
                break

            engine.step()

            if step % self.grn_update_interval == 0:
                mean_pos   = self._mean_tip_position(engine)
                self._update_grn(mean_pos)
                new_params = grn_to_params(self.grn_state, self.base_params)
                engine.params = new_params

        return engine

    @property
    def state_history(self) -> List[GRNState]:
        """All GRN states recorded during simulation."""
        return self._state_history

    def print_summary(self) -> None:
        """Print start and end GRN states."""
        s0 = self._state_history[0]
        sf = self._state_history[-1]
        print(f"GRN steps recorded : {len(self._state_history)}")
        print(f"Initial state      : {s0}")
        print(f"Final state        : {sf}")
        print(f"  growth     {s0.growth:.3f} → {sf.growth:.3f}")
        print(f"  branch     {s0.branch:.3f} → {sf.branch:.3f}")
        print(f"  adhesion   {s0.adhesion:.3f} → {sf.adhesion:.3f}")
        print(f"  polarity   {s0.polarity:.3f} → {sf.polarity:.3f}")
        print(f"  diff       {s0.differentiation:.3f} → {sf.differentiation:.3f}")

"""
grn/grn.py — Gene Regulatory Network model.

Models a simplified GRN as a weight-matrix dynamical system:

    next_state = sigmoid(W @ current_state + bias + signal_input)

Five internal genes:
  0  growth          — controls tip advancement speed
  1  branch          — controls branching probability
  2  adhesion        — controls structural cohesion / taper
  3  polarity        — controls directional bias
  4  differentiation — drives terminal cell fate (reduces max depth)

The weight matrix W encodes gene–gene interactions (activation / repression).
Signal inputs from SignalField are added to the pre-sigmoid activations.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass
class GRNState:
    """Regulatory state of a cell or growing tip."""
    growth:          float = 0.50
    branch:          float = 0.20
    adhesion:        float = 0.50
    polarity:        float = 0.70
    differentiation: float = 0.00

    def as_array(self) -> np.ndarray:
        return np.array([
            self.growth,
            self.branch,
            self.adhesion,
            self.polarity,
            self.differentiation,
        ], dtype=float)

    @classmethod
    def from_array(cls, arr: np.ndarray) -> GRNState:
        return cls(
            growth          = float(arr[0]),
            branch          = float(arr[1]),
            adhesion        = float(arr[2]),
            polarity        = float(arr[3]),
            differentiation = float(arr[4]),
        )

    def __repr__(self) -> str:
        return (
            f"GRNState("
            f"growth={self.growth:.3f}, "
            f"branch={self.branch:.3f}, "
            f"adhesion={self.adhesion:.3f}, "
            f"polarity={self.polarity:.3f}, "
            f"diff={self.differentiation:.3f})"
        )


class GRNNetwork:
    """
    Discrete-time gene regulatory network.

    State update rule:
        x_{t+1} = sigmoid(W @ x_t + bias + signal)

    Parameters
    ----------
    weights : (5, 5) ndarray
        Gene–gene interaction matrix.
        weights[i, j] > 0  → gene j activates gene i
        weights[i, j] < 0  → gene j represses gene i
    bias : (5,) ndarray
        Baseline activation for each gene.
    """

    N_GENES = 5

    def __init__(self, weights: np.ndarray, bias: np.ndarray) -> None:
        if weights.shape != (self.N_GENES, self.N_GENES):
            raise ValueError(f"weights must be ({self.N_GENES}, {self.N_GENES})")
        if bias.shape != (self.N_GENES,):
            raise ValueError(f"bias must be ({self.N_GENES},)")
        self.weights = weights.astype(float)
        self.bias    = bias.astype(float)

    def update(self, state: GRNState, signal_input: np.ndarray) -> GRNState:
        """
        Run one GRN update step.

        Parameters
        ----------
        state        : current GRN state
        signal_input : (5,) external signal contributions
        """
        x   = state.as_array()
        raw = self.weights @ x + self.bias + signal_input
        new = self._sigmoid(raw)
        return GRNState.from_array(new)

    @staticmethod
    def _sigmoid(x: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-np.clip(x, -20.0, 20.0)))

    @classmethod
    def identity(cls) -> GRNNetwork:
        """Minimal network with no gene–gene interactions."""
        return cls(
            weights = np.eye(cls.N_GENES, dtype=float) * 0.5,
            bias    = np.zeros(cls.N_GENES, dtype=float),
        )

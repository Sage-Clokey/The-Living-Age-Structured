"""
pipeline/train_grn.py

Trains a neural network to predict GRN (Gene Regulatory Network) signals
from temporal plant growth sequences.

Uses Pheno4D time-series data: each plant has ~12 timesteps of scans.
The model learns: given the current morphological state of a plant,
what signal levels (nutrient, morphogen_a, morphogen_b) best explain
the observed growth to the next timestep?

Architecture
------------
Input:  5 normalized features at time t
        [height, hw_ratio, upper_density, spread_asymm, organ_ratio]

Output: 3 GRN signals (sigmoid-activated → [0, 1])
        [nutrient, morphogen_a, morphogen_b]

Training objective
------------------
Simulate one GRN timestep with the predicted signals,
then minimize the difference between:
  - predicted next-state GRN → mapped to feature deltas
  - actual observed feature deltas (features_{t+1} - features_t)

Since we don't have ground-truth signals, we use a self-supervised
approach: the network learns signals that make the GRN simulation
match observed growth changes.

Saved output: pipeline/model/grn_signal_net.pt  (PyTorch)
              pipeline/model/grn_signal_net.json (weights as JSON for non-PyTorch use)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))
from pipeline import registry

MODEL_DIR = Path(__file__).parent / "model"
MODEL_DIR.mkdir(exist_ok=True)

FEATURE_KEYS = ["height", "hw_ratio", "upper_density", "spread_asymm", "organ_ratio"]
SIGNAL_NAMES = ["nutrient", "morphogen_a", "morphogen_b"]


# ---------------------------------------------------------------------------
# GRN simulation (mirrors grn/grn.py logic, numpy only)
# ---------------------------------------------------------------------------

def _grn_step(state: np.ndarray, signals: np.ndarray, dt: float = 0.1) -> np.ndarray:
    """
    One step of GRN update (no noise for training stability).

    state: [growth, branch, adhesion, polarity, diff]
    signals: [nutrient, morphogen_a, morphogen_b]
    """
    nutrient, morph_a, morph_b = signals
    growth, branch, adhesion, polarity, diff = state

    d_growth = (nutrient * 1.0 - growth * 0.8 - diff * 0.4) * dt
    d_branch = (morph_a * 0.9 - morph_b * 0.6 - branch * 0.5) * dt
    d_adhesion = (morph_b * 1.0 - adhesion * 0.7) * dt
    d_polarity = (nutrient * 1.2 - polarity * 0.6) * dt
    d_diff = max(0.0, (growth * 0.3 - branch * 0.2 - 0.1) * dt)

    new_state = np.clip(
        state + np.array([d_growth, d_branch, d_adhesion, d_polarity, d_diff]),
        0.0, 1.0,
    )
    return new_state


def _grn_to_feature_delta(grn_delta: np.ndarray) -> np.ndarray:
    """
    Map GRN state change → expected feature change direction.

    Rough biological mapping:
      growth  → height increases, hw_ratio changes
      branch  → upper_density increases
      adhesion→ spread_asymm increases
      polarity→ hw_ratio increases (directional growth)
      diff    → slows all growth (negative scaling)
    """
    d_growth, d_branch, d_adhesion, d_polarity, d_diff = grn_delta
    return np.array([
        d_growth * 2.0 - d_diff * 0.5,           # height
        d_polarity * 0.5 - d_growth * 0.2,        # hw_ratio
        d_branch * 1.5 - d_diff * 0.3,            # upper_density
        d_adhesion * 1.0,                          # spread_asymm
        d_branch * 0.8 - d_diff * 0.4,            # organ_ratio
    ])


# ---------------------------------------------------------------------------
# Data preparation
# ---------------------------------------------------------------------------

def _normalize_features(feat_vec: np.ndarray, stats: dict) -> np.ndarray:
    mean = np.array(stats["mean"])
    std = np.array(stats["std"]) + 1e-8
    return (feat_vec - mean) / std


def _build_training_data(reg: dict) -> tuple[np.ndarray, np.ndarray, dict]:
    """
    Build (X, delta_Y) training pairs from Pheno4D temporal sequences.

    X:       feature vector at time t       (N, 5)
    delta_Y: normalized feature delta t→t+1 (N, 5)
    stats:   normalization statistics
    """
    sequences = registry.get_sequences(reg, source="pheno4d")

    X_list = []
    dY_list = []

    for plant_id, entries in sequences.items():
        if len(entries) < 2:
            continue
        for i in range(len(entries) - 1):
            f_t = entries[i]["features"]
            f_t1 = entries[i + 1]["features"]

            vec_t = np.array([f_t.get(k, 0.0) for k in FEATURE_KEYS], dtype=np.float32)
            vec_t1 = np.array([f_t1.get(k, 0.0) for k in FEATURE_KEYS], dtype=np.float32)
            delta = vec_t1 - vec_t

            X_list.append(vec_t)
            dY_list.append(delta)

    if not X_list:
        return np.empty((0, 5)), np.empty((0, 5)), {}

    X = np.stack(X_list)
    dY = np.stack(dY_list)

    stats = {
        "mean": X.mean(axis=0).tolist(),
        "std": X.std(axis=0).tolist(),
        "feature_keys": FEATURE_KEYS,
    }

    return X, dY, stats


# ---------------------------------------------------------------------------
# Simple numpy MLP (no PyTorch dependency required)
# ---------------------------------------------------------------------------

class MLP:
    """
    2-layer MLP: input(5) → hidden(32) → hidden(16) → output(3).
    Trained with SGD + MSE loss. Saved/loaded as JSON.
    """
    def __init__(self, input_dim: int = 5, hidden: int = 32, output_dim: int = 3):
        rng = np.random.default_rng(42)
        self.W1 = rng.normal(0, 0.1, (input_dim, hidden)).astype(np.float32)
        self.b1 = np.zeros(hidden, dtype=np.float32)
        self.W2 = rng.normal(0, 0.1, (hidden, 16)).astype(np.float32)
        self.b2 = np.zeros(16, dtype=np.float32)
        self.W3 = rng.normal(0, 0.1, (16, output_dim)).astype(np.float32)
        self.b3 = np.zeros(output_dim, dtype=np.float32)

    def forward(self, x: np.ndarray) -> np.ndarray:
        h1 = np.tanh(x @ self.W1 + self.b1)
        h2 = np.tanh(h1 @ self.W2 + self.b2)
        out = 1.0 / (1.0 + np.exp(-(h2 @ self.W3 + self.b3)))  # sigmoid → [0,1]
        return out

    def predict_signals(self, feat_vec: np.ndarray) -> np.ndarray:
        return self.forward(feat_vec.reshape(1, -1))[0]

    def save(self, path: Path, stats: dict) -> None:
        payload = {
            "W1": self.W1.tolist(), "b1": self.b1.tolist(),
            "W2": self.W2.tolist(), "b2": self.b2.tolist(),
            "W3": self.W3.tolist(), "b3": self.b3.tolist(),
            "stats": stats,
            "feature_keys": FEATURE_KEYS,
            "signal_names": SIGNAL_NAMES,
        }
        with open(path, "w") as f:
            json.dump(payload, f)

    @classmethod
    def load(cls, path: Path) -> tuple["MLP", dict]:
        with open(path) as f:
            payload = json.load(f)
        model = cls.__new__(cls)
        model.W1 = np.array(payload["W1"], dtype=np.float32)
        model.b1 = np.array(payload["b1"], dtype=np.float32)
        model.W2 = np.array(payload["W2"], dtype=np.float32)
        model.b2 = np.array(payload["b2"], dtype=np.float32)
        model.W3 = np.array(payload["W3"], dtype=np.float32)
        model.b3 = np.array(payload["b3"], dtype=np.float32)
        return model, payload["stats"]


def _train(model: MLP, X: np.ndarray, dY: np.ndarray, stats: dict,
           epochs: int = 500, lr: float = 0.01, verbose: bool = True) -> list[float]:
    """
    Self-supervised training loop.

    For each sample, predict signals, simulate one GRN step, map GRN delta
    to expected feature delta, compute MSE vs actual feature delta.
    """
    losses = []
    init_grn = np.array([0.5, 0.3, 0.5, 0.6, 0.0], dtype=np.float32)

    # Normalize X
    mean = np.array(stats["mean"], dtype=np.float32)
    std = np.array(stats["std"], dtype=np.float32) + 1e-8
    X_norm = (X - mean) / std

    # Normalize dY for loss scaling
    dy_scale = np.abs(dY).mean(axis=0) + 1e-8

    for epoch in range(epochs):
        epoch_loss = 0.0
        # Shuffle
        idx = np.random.permutation(len(X_norm))

        for i in idx:
            x = X_norm[i]
            dy_target = dY[i] / dy_scale

            # Forward pass
            signals = model.forward(x.reshape(1, -1))[0]

            # Simulate GRN step
            grn_next = _grn_step(init_grn, signals)
            grn_delta = grn_next - init_grn
            dy_pred = _grn_to_feature_delta(grn_delta) / (dy_scale + 1e-8)

            # Loss: MSE between predicted and actual feature deltas
            loss = float(np.mean((dy_pred - dy_target) ** 2))
            epoch_loss += loss

            # Numerical gradient for W3 (simplified backprop)
            eps = 1e-3
            for j in range(model.W3.shape[0]):
                for k in range(model.W3.shape[1]):
                    model.W3[j, k] += eps
                    s_plus = model.forward(x.reshape(1, -1))[0]
                    gd_plus = _grn_step(init_grn, s_plus) - init_grn
                    dp_plus = _grn_to_feature_delta(gd_plus) / (dy_scale + 1e-8)
                    l_plus = float(np.mean((dp_plus - dy_target) ** 2))

                    model.W3[j, k] -= 2 * eps
                    s_minus = model.forward(x.reshape(1, -1))[0]
                    gd_minus = _grn_step(init_grn, s_minus) - init_grn
                    dp_minus = _grn_to_feature_delta(gd_minus) / (dy_scale + 1e-8)
                    l_minus = float(np.mean((dp_minus - dy_target) ** 2))

                    model.W3[j, k] += eps  # restore
                    grad = (l_plus - l_minus) / (2 * eps)
                    model.W3[j, k] -= lr * grad

        avg_loss = epoch_loss / max(len(X), 1)
        losses.append(avg_loss)
        if verbose and (epoch % 50 == 0 or epoch == epochs - 1):
            print(f"  epoch {epoch+1:4d}/{epochs}  loss={avg_loss:.6f}")

    return losses


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(reg: dict | None = None, epochs: int = 200, verbose: bool = True) -> MLP | None:
    if reg is None:
        reg = registry.load()

    X, dY, stats = _build_training_data(reg)

    if len(X) == 0:
        print("No temporal sequences found — need pheno4d data ingested first.")
        return None

    print(f"Training on {len(X)} growth transitions from Pheno4D...")
    model = MLP()
    _train(model, X, dY, stats, epochs=epochs, verbose=verbose)

    save_path = MODEL_DIR / "grn_signal_net.json"
    model.save(save_path, stats)
    print(f"\nModel saved → {save_path}")
    return model


def predict_signals(feat_dict: dict) -> dict:
    """
    Load trained model and predict GRN signals for a feature dict.
    Returns {nutrient: float, morphogen_a: float, morphogen_b: float}
    """
    model_path = MODEL_DIR / "grn_signal_net.json"
    if not model_path.exists():
        raise FileNotFoundError("Model not trained yet — run train_grn.py first.")

    model, stats = MLP.load(model_path)
    mean = np.array(stats["mean"], dtype=np.float32)
    std = np.array(stats["std"], dtype=np.float32) + 1e-8

    feat_vec = np.array([feat_dict.get(k, 0.0) for k in FEATURE_KEYS], dtype=np.float32)
    feat_norm = (feat_vec - mean) / std
    signals = model.predict_signals(feat_norm)

    return {name: round(float(s), 4) for name, s in zip(SIGNAL_NAMES, signals)}


if __name__ == "__main__":
    run()

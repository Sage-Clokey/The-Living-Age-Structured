"""
Training and evaluation pipeline for Models A, B, and C.

Trains all three models, evaluates with F_max and AUPR, and performs stratified analysis.
"""

import json
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from pathlib import Path

from models import get_model
from evaluate import compute_fmax, compute_aupr, stratified_analysis, plot_results

DATA_DIR = Path(__file__).parent / "data"
RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def prepare_dataloaders(
    features: dict[str, np.ndarray],
    test_size: float = 0.2,
    batch_size: int = 64,
    kingdom_labels: np.ndarray = None,
) -> tuple[DataLoader, DataLoader, np.ndarray, np.ndarray]:
    """
    Split data and create DataLoaders.
    Stratifies by kingdom to ensure balanced representation.
    """
    n_samples = features["labels"].shape[0]
    indices = np.arange(n_samples)

    # Stratify by kingdom if available
    if kingdom_labels is not None:
        train_idx, test_idx = train_test_split(
            indices, test_size=test_size, random_state=42, stratify=kingdom_labels
        )
    else:
        train_idx, test_idx = train_test_split(indices, test_size=test_size, random_state=42)

    def make_loader(idx, shuffle=False):
        tensors = {}
        for key in ["esm_embeddings", "domain_bag", "context", "labels"]:
            if key in features:
                tensors[key] = torch.tensor(features[key][idx], dtype=torch.float32)

        dataset = TensorDataset(*tensors.values())
        return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle), list(tensors.keys())

    train_loader, keys = make_loader(train_idx, shuffle=True)
    test_loader, _ = make_loader(test_idx, shuffle=False)

    return train_loader, test_loader, train_idx, test_idx, keys


def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    feature_keys: list[str],
    n_epochs: int = 50,
    lr: float = 1e-3,
    weight_decay: float = 1e-4,
) -> list[float]:
    """Train a model with binary cross-entropy loss."""
    model = model.to(DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=n_epochs)
    criterion = nn.BCEWithLogitsLoss()

    losses = []
    model.train()

    for epoch in range(n_epochs):
        epoch_loss = 0.0
        n_batches = 0

        for batch in train_loader:
            batch_dict = {k: v.to(DEVICE) for k, v in zip(feature_keys, batch)}
            labels = batch_dict.pop("labels")

            # Map feature keys to model forward kwargs
            kwargs = {}
            if "esm_embeddings" in batch_dict:
                kwargs["esm_embedding"] = batch_dict["esm_embeddings"]
            if "domain_bag" in batch_dict:
                kwargs["domain_bag"] = batch_dict["domain_bag"]
            if "context" in batch_dict:
                kwargs["context"] = batch_dict["context"]

            logits = model(**kwargs)
            loss = criterion(logits, labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()
            n_batches += 1

        scheduler.step()
        avg_loss = epoch_loss / n_batches
        losses.append(avg_loss)

        if (epoch + 1) % 10 == 0:
            print(f"    Epoch {epoch + 1}/{n_epochs} — Loss: {avg_loss:.4f}")

    return losses


def evaluate_model(
    model: nn.Module,
    test_loader: DataLoader,
    feature_keys: list[str],
) -> tuple[np.ndarray, np.ndarray]:
    """Get predictions and true labels from test set."""
    model = model.to(DEVICE)
    model.eval()

    all_preds = []
    all_labels = []

    with torch.no_grad():
        for batch in test_loader:
            batch_dict = {k: v.to(DEVICE) for k, v in zip(feature_keys, batch)}
            labels = batch_dict.pop("labels")

            kwargs = {}
            if "esm_embeddings" in batch_dict:
                kwargs["esm_embedding"] = batch_dict["esm_embeddings"]
            if "domain_bag" in batch_dict:
                kwargs["domain_bag"] = batch_dict["domain_bag"]
            if "context" in batch_dict:
                kwargs["context"] = batch_dict["context"]

            logits = model(**kwargs)
            probs = torch.sigmoid(logits)

            all_preds.append(probs.cpu().numpy())
            all_labels.append(labels.cpu().numpy())

    return np.vstack(all_preds), np.vstack(all_labels)


def run_experiment(
    features: dict[str, np.ndarray],
    go_vocab: list[str],
    kingdom_labels: np.ndarray,
    n_epochs: int = 50,
    batch_size: int = 64,
):
    """Run the full experiment: train and evaluate Models A, B, C."""
    print("=" * 60)
    print("TRAINING EXPERIMENT")
    print(f"Device: {DEVICE}")
    print(f"Samples: {features['labels'].shape[0]}")
    print(f"GO terms: {features['labels'].shape[1]}")
    print("=" * 60)

    # Prepare data
    train_loader, test_loader, train_idx, test_idx, feature_keys = prepare_dataloaders(
        features, batch_size=batch_size, kingdom_labels=kingdom_labels
    )
    print(f"Train: {len(train_idx)}, Test: {len(test_idx)}")

    n_labels = features["labels"].shape[1]
    n_domains = features["domain_bag"].shape[1]

    results = {}

    # Model A: Sequence Only
    if "esm_embeddings" in features:
        print("\n--- Model A: Sequence Only (ESM-2 -> MLP) ---")
        model_a = get_model("A", embedding_dim=1280, n_labels=n_labels)
        print(f"  Parameters: {sum(p.numel() for p in model_a.parameters()):,}")
        keys_a = [k for k in feature_keys if k in ["esm_embeddings", "labels"]]
        # Need to make a loader with just these features
        train_a, test_a = make_subset_loaders(features, train_idx, test_idx, keys_a, batch_size)
        losses_a = train_model(model_a, train_a, keys_a, n_epochs=n_epochs)
        preds_a, labels_a = evaluate_model(model_a, test_a, keys_a)
        fmax_a = compute_fmax(labels_a, preds_a)
        aupr_a = compute_aupr(labels_a, preds_a)
        print(f"  F_max: {fmax_a:.4f} | AUPR: {aupr_a:.4f}")
        results["A"] = {"fmax": fmax_a, "aupr": aupr_a, "preds": preds_a, "labels": labels_a, "losses": losses_a}
        torch.save(model_a.state_dict(), RESULTS_DIR / "model_a.pt")

    # Model B: Domain Grammar Only
    print("\n--- Model B: Domain Grammar Only (Domains + Context -> MLP) ---")
    model_b = get_model("B", n_domains=n_domains, n_labels=n_labels)
    print(f"  Parameters: {sum(p.numel() for p in model_b.parameters()):,}")
    keys_b = [k for k in feature_keys if k in ["domain_bag", "context", "labels"]]
    train_b, test_b = make_subset_loaders(features, train_idx, test_idx, keys_b, batch_size)
    losses_b = train_model(model_b, train_b, keys_b, n_epochs=n_epochs)
    preds_b, labels_b = evaluate_model(model_b, test_b, keys_b)
    fmax_b = compute_fmax(labels_b, preds_b)
    aupr_b = compute_aupr(labels_b, preds_b)
    print(f"  F_max: {fmax_b:.4f} | AUPR: {aupr_b:.4f}")
    results["B"] = {"fmax": fmax_b, "aupr": aupr_b, "preds": preds_b, "labels": labels_b, "losses": losses_b}
    torch.save(model_b.state_dict(), RESULTS_DIR / "model_b.pt")

    # Model C: Combined
    if "esm_embeddings" in features:
        print("\n--- Model C: Combined (ESM-2 + Domains + Context -> MLP) ---")
        model_c = get_model("C", n_domains=n_domains, n_labels=n_labels)
        print(f"  Parameters: {sum(p.numel() for p in model_c.parameters()):,}")
        keys_c = [k for k in feature_keys if k in ["esm_embeddings", "domain_bag", "context", "labels"]]
        train_c, test_c = make_subset_loaders(features, train_idx, test_idx, keys_c, batch_size)
        losses_c = train_model(model_c, train_c, keys_c, n_epochs=n_epochs)
        preds_c, labels_c = evaluate_model(model_c, test_c, keys_c)
        fmax_c = compute_fmax(labels_c, preds_c)
        aupr_c = compute_aupr(labels_c, preds_c)
        print(f"  F_max: {fmax_c:.4f} | AUPR: {aupr_c:.4f}")
        results["C"] = {"fmax": fmax_c, "aupr": aupr_c, "preds": preds_c, "labels": labels_c, "losses": losses_c}
        torch.save(model_c.state_dict(), RESULTS_DIR / "model_c.pt")

    # Stratified analysis
    print("\n--- Stratified Analysis ---")
    kingdom_test = kingdom_labels[test_idx]
    n_domains_test = features["domain_bag"][test_idx].sum(axis=1)

    strat_results = stratified_analysis(results, kingdom_test, n_domains_test)

    # Save results
    summary = {
        model_name: {"fmax": r["fmax"], "aupr": r["aupr"]}
        for model_name, r in results.items()
    }
    summary["stratified"] = strat_results
    with open(RESULTS_DIR / "results_summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)

    # Plot
    plot_results(results, kingdom_test, n_domains_test, RESULTS_DIR)

    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)
    print(f"\nResults saved to {RESULTS_DIR}/")

    return results


def make_subset_loaders(
    features: dict, train_idx: np.ndarray, test_idx: np.ndarray,
    keys: list[str], batch_size: int
) -> tuple[DataLoader, DataLoader]:
    """Create DataLoaders with only the specified feature keys."""
    def make(idx, shuffle):
        tensors = [torch.tensor(features[k][idx], dtype=torch.float32) for k in keys]
        return DataLoader(TensorDataset(*tensors), batch_size=batch_size, shuffle=shuffle)
    return make(train_idx, True), make(test_idx, False)


if __name__ == "__main__":
    from data_pipeline import build_dataset, filter_go_terms
    from feature_engineering import prepare_all_features

    # Build dataset
    df = build_dataset(max_per_kingdom=5000)
    df, go_vocab = filter_go_terms(df, min_proteins=50)

    # Prepare features
    features = prepare_all_features(df, go_vocab, generate_embeddings=True)

    # Kingdom labels for stratification
    kingdom_map = {"Archaea": 0, "Bacteria": 1, "Eukarya": 2}
    kingdom_labels = df["kingdom"].map(kingdom_map).values

    # Run experiment
    results = run_experiment(features, go_vocab, kingdom_labels, n_epochs=50)

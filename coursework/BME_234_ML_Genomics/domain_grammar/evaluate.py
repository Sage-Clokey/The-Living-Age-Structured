"""
Evaluation metrics and visualization for the domain grammar experiment.

Implements:
- F_max (protein-centric, CAFA standard)
- AUPR (area under precision-recall curve)
- Stratified analysis by kingdom and domain count
- Result visualization
"""

import numpy as np
from sklearn.metrics import precision_recall_curve, average_precision_score
from pathlib import Path


def compute_fmax(labels: np.ndarray, preds: np.ndarray, n_thresholds: int = 50) -> float:
    """
    Compute protein-centric F_max: maximum F1 across thresholds.
    For each threshold, compute precision and recall per protein, then average.
    This is the CAFA standard metric.
    """
    thresholds = np.linspace(0.01, 0.99, n_thresholds)
    best_f1 = 0.0

    for t in thresholds:
        binary_preds = (preds >= t).astype(float)

        # Per-protein precision and recall
        tp = (binary_preds * labels).sum(axis=1)
        pred_pos = binary_preds.sum(axis=1)
        true_pos = labels.sum(axis=1)

        # Avoid division by zero
        precision = np.where(pred_pos > 0, tp / pred_pos, 0.0)
        recall = np.where(true_pos > 0, tp / true_pos, 0.0)

        # Only count proteins that have predictions or labels
        mask = (pred_pos > 0) | (true_pos > 0)
        if mask.sum() == 0:
            continue

        avg_precision = precision[mask].mean()
        avg_recall = recall[mask].mean()

        if avg_precision + avg_recall > 0:
            f1 = 2 * avg_precision * avg_recall / (avg_precision + avg_recall)
            best_f1 = max(best_f1, f1)

    return best_f1


def compute_aupr(labels: np.ndarray, preds: np.ndarray) -> float:
    """
    Compute micro-averaged area under precision-recall curve.
    Flattens all proteins and terms into a single binary classification.
    """
    # Micro-average: flatten
    return average_precision_score(labels.ravel(), preds.ravel())


def stratified_analysis(
    results: dict,
    kingdom_labels: np.ndarray,
    n_domains: np.ndarray,
) -> dict:
    """
    Compute F_max stratified by:
    - Kingdom (Archaea, Bacteria, Eukarya)
    - Single-domain vs multi-domain proteins
    """
    kingdom_names = {0: "Archaea", 1: "Bacteria", 2: "Eukarya"}
    strat = {}

    for model_name, r in results.items():
        preds = r["preds"]
        labels = r["labels"]
        model_strat = {}

        # By kingdom
        for k_idx, k_name in kingdom_names.items():
            mask = kingdom_labels == k_idx
            if mask.sum() > 10:
                fmax = compute_fmax(labels[mask], preds[mask])
                model_strat[f"kingdom_{k_name}"] = {"fmax": fmax, "n": int(mask.sum())}

        # Single vs multi-domain
        single_mask = n_domains <= 1
        multi_mask = n_domains > 1
        if single_mask.sum() > 10:
            model_strat["single_domain"] = {
                "fmax": compute_fmax(labels[single_mask], preds[single_mask]),
                "n": int(single_mask.sum()),
            }
        if multi_mask.sum() > 10:
            model_strat["multi_domain"] = {
                "fmax": compute_fmax(labels[multi_mask], preds[multi_mask]),
                "n": int(multi_mask.sum()),
            }

        strat[model_name] = model_strat
        print(f"\n  Model {model_name}:")
        for k, v in model_strat.items():
            print(f"    {k}: F_max={v['fmax']:.4f} (n={v['n']})")

    return strat


def plot_results(
    results: dict,
    kingdom_labels: np.ndarray,
    n_domains: np.ndarray,
    output_dir: Path,
):
    """Generate publication-quality result plots."""
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # 1. Overall comparison bar chart
    ax = axes[0]
    models = sorted(results.keys())
    fmax_vals = [results[m]["fmax"] for m in models]
    aupr_vals = [results[m]["aupr"] for m in models]

    x = np.arange(len(models))
    width = 0.35
    ax.bar(x - width / 2, fmax_vals, width, label="F_max", color="#2ecc71")
    ax.bar(x + width / 2, aupr_vals, width, label="AUPR", color="#3498db")
    ax.set_xticks(x)
    ax.set_xticklabels([f"Model {m}" for m in models])
    ax.set_ylabel("Score")
    ax.set_title("Overall Performance")
    ax.legend()
    ax.set_ylim(0, 1)

    # 2. Kingdom stratification
    ax = axes[1]
    kingdom_names = ["Archaea", "Bacteria", "Eukarya"]
    x = np.arange(len(kingdom_names))
    width = 0.25
    for i, m in enumerate(models):
        fmax_by_kingdom = []
        for k_name in kingdom_names:
            mask = kingdom_labels == ["Archaea", "Bacteria", "Eukarya"].index(k_name)
            if mask.sum() > 10:
                fmax_by_kingdom.append(compute_fmax(results[m]["labels"][mask], results[m]["preds"][mask]))
            else:
                fmax_by_kingdom.append(0)
        ax.bar(x + i * width - width, fmax_by_kingdom, width, label=f"Model {m}")
    ax.set_xticks(x)
    ax.set_xticklabels(kingdom_names)
    ax.set_ylabel("F_max")
    ax.set_title("Performance by Kingdom")
    ax.legend()
    ax.set_ylim(0, 1)

    # 3. Training loss curves
    ax = axes[2]
    for m in models:
        if "losses" in results[m]:
            ax.plot(results[m]["losses"], label=f"Model {m}")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("BCE Loss")
    ax.set_title("Training Loss")
    ax.legend()

    plt.tight_layout()
    plt.savefig(output_dir / "results_comparison.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n  Saved plot to {output_dir / 'results_comparison.png'}")

    # 4. Domain count analysis
    fig, ax = plt.subplots(figsize=(8, 5))
    domain_bins = [(1, 1, "1 domain"), (2, 3, "2-3 domains"), (4, 20, "4+ domains")]
    x = np.arange(len(domain_bins))
    width = 0.25

    for i, m in enumerate(models):
        fmax_by_bin = []
        for lo, hi, label in domain_bins:
            mask = (n_domains >= lo) & (n_domains <= hi)
            if mask.sum() > 10:
                fmax_by_bin.append(compute_fmax(results[m]["labels"][mask], results[m]["preds"][mask]))
            else:
                fmax_by_bin.append(0)
        ax.bar(x + i * width - width, fmax_by_bin, width, label=f"Model {m}")

    ax.set_xticks(x)
    ax.set_xticklabels([b[2] for b in domain_bins])
    ax.set_ylabel("F_max")
    ax.set_title("Performance by Domain Count")
    ax.legend()
    ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(output_dir / "domain_count_analysis.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved plot to {output_dir / 'domain_count_analysis.png'}")

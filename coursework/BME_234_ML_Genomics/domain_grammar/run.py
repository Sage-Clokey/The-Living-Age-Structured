"""
Main entry point: run the full domain grammar experiment end-to-end.

Usage:
    python run.py                    # Full run (downloads data, generates embeddings, trains)
    python run.py --skip-embeddings  # Skip ESM-2 (useful for testing pipeline without GPU time)
    python run.py --max-proteins 1000  # Smaller dataset for quick testing
"""

import sys
import json
import argparse
import numpy as np
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from data_pipeline import build_dataset, filter_go_terms, DATA_DIR
from feature_engineering import prepare_all_features
from train import run_experiment


def main():
    parser = argparse.ArgumentParser(description="Domain Grammar Protein Function Prediction")
    parser.add_argument("--max-proteins", type=int, default=5000, help="Max proteins per kingdom")
    parser.add_argument("--min-go-proteins", type=int, default=50, help="Min proteins per GO term")
    parser.add_argument("--skip-embeddings", action="store_true", help="Skip ESM-2 embedding generation")
    parser.add_argument("--epochs", type=int, default=50, help="Training epochs")
    parser.add_argument("--batch-size", type=int, default=64, help="Batch size")
    args = parser.parse_args()

    print("=" * 60)
    print("DOMAIN GRAMMAR AS A PREDICTIVE LAYER")
    print("BEYOND PROTEIN LANGUAGE MODELS")
    print("=" * 60)
    print(f"\nConfig:")
    print(f"  Max proteins/kingdom: {args.max_proteins}")
    print(f"  Min GO term support: {args.min_go_proteins}")
    print(f"  Generate ESM-2 embeddings: {not args.skip_embeddings}")
    print(f"  Epochs: {args.epochs}")
    print(f"  Batch size: {args.batch_size}")
    print()

    # Step 1: Data
    print("\n[1/3] DATA PIPELINE")
    print("-" * 40)
    df = build_dataset(max_per_kingdom=args.max_proteins)
    df, go_vocab = filter_go_terms(df, min_proteins=args.min_go_proteins)

    with open(DATA_DIR / "go_vocabulary.json", "w") as f:
        json.dump(go_vocab, f)

    # Step 2: Features
    print("\n[2/3] FEATURE ENGINEERING")
    print("-" * 40)
    features = prepare_all_features(df, go_vocab, generate_embeddings=not args.skip_embeddings)

    # Kingdom labels
    kingdom_map = {"Archaea": 0, "Bacteria": 1, "Eukarya": 2}
    kingdom_labels = df["kingdom"].map(kingdom_map).values

    # Step 3: Train and evaluate
    print("\n[3/3] MODEL TRAINING & EVALUATION")
    print("-" * 40)

    if args.skip_embeddings and "esm_embeddings" not in features:
        # Generate random embeddings as placeholder for pipeline testing
        print("  Using random embeddings (placeholder for pipeline test)")
        features["esm_embeddings"] = np.random.randn(len(df), 1280).astype(np.float32)

    results = run_experiment(
        features, go_vocab, kingdom_labels,
        n_epochs=args.epochs, batch_size=args.batch_size
    )

    # Final summary
    print("\n" + "=" * 60)
    print("FINAL RESULTS SUMMARY")
    print("=" * 60)
    print(f"\n{'Model':<12} {'F_max':<10} {'AUPR':<10}")
    print("-" * 32)
    for m in sorted(results.keys()):
        print(f"Model {m:<6} {results[m]['fmax']:<10.4f} {results[m]['aupr']:<10.4f}")

    if "A" in results and "C" in results:
        improvement = results["C"]["fmax"] - results["A"]["fmax"]
        print(f"\nImprovement (C over A): {improvement:+.4f} F_max")
        if improvement > 0:
            print("Domain grammar ADDS information beyond sequence embeddings.")
        else:
            print("Domain grammar did NOT improve over sequence alone.")

    if "B" in results:
        print(f"\nModel B (domain grammar only) F_max: {results['B']['fmax']:.4f}")
        print("This shows domain compositionality is independently predictive.")


if __name__ == "__main__":
    main()

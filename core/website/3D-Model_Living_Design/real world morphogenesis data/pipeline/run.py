"""
pipeline/run.py

Main entry point for the morphogenesis data pipeline.

Usage:
  python pipeline/run.py                  # ingest new data + fit programs
  python pipeline/run.py --train          # also train GRN signal model
  python pipeline/run.py --ingest-only    # only scan for new files
  python pipeline/run.py --status         # show registry summary only
  python pipeline/run.py --scan PATH      # extract + print features for one file

Adding new growth shape data:
  1. Drop .ply or .txt point cloud files into  data/new/<species_name>/
  2. Run:  python pipeline/run.py
  All new files are automatically detected, features extracted, registry
  updated, and GrowthProgram parameters re-fitted to include new data.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline import ingest, fit_program, registry
from pipeline.extract import extract_features


def print_programs(programs: dict) -> None:
    print("\n=== GrowthProgram Parameters ===")
    for species, params in programs.items():
        print(f"\n{species}  (n={params['scan_count']}, sources={params['sources']})")
        for k, v in params.items():
            if k in ("scan_count", "sources", "median_features"):
                continue
            print(f"  {k}: {v}")


def main() -> None:
    args = set(sys.argv[1:])
    base = Path(__file__).parent.parent

    if "--status" in args:
        reg = registry.load()
        print(registry.summary(reg))
        seqs = registry.get_sequences(reg)
        if seqs:
            print(f"\nTemporal sequences ({len(seqs)} plants):")
            for pid, entries in sorted(seqs.items()):
                print(f"  {pid}: {len(entries)} timesteps")
        return

    if "--scan" in args:
        idx = sys.argv.index("--scan")
        if idx + 1 >= len(sys.argv):
            print("Usage: --scan PATH")
            return
        path = Path(sys.argv[idx + 1])
        print(f"Extracting features from: {path}")
        feats = extract_features(path)
        print(json.dumps(feats, indent=2))
        return

    # Default: ingest + fit
    print("=" * 60)
    print("Morphogenesis Data Pipeline")
    print("=" * 60)

    print("\n[1/3] Ingesting new data...")
    reg = ingest.run(verbose=True)

    if "--ingest-only" in args:
        return

    print("\n[2/3] Fitting GrowthProgram parameters...")
    programs = fit_program.run(reg=reg, verbose=True)
    print_programs(programs)

    if "--train" in args:
        print("\n[3/3] Training GRN signal model...")
        from pipeline import train_grn
        train_grn.run(reg=reg, epochs=200, verbose=True)
    else:
        print("\n[3/3] Skipped GRN training (add --train to enable).")
        print("      Training requires Pheno4D temporal sequences.")

    print("\n" + "=" * 60)
    print("Done. Output files:")
    print(f"  registry.json       — all processed scans + features")
    print(f"  growth_programs.json — fitted GrowthProgram parameters")
    print(f"  pipeline/model/     — trained GRN model (if --train used)")
    print()
    print("To add new growth data:")
    print("  Drop .ply or .txt files into  data/new/<species>/")
    print("  Then re-run:  python pipeline/run.py")


if __name__ == "__main__":
    main()

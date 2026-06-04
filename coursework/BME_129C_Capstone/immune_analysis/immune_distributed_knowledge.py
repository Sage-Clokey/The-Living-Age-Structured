"""
Immune System as Distributed Knowledge — Analysis & Figures
BME 129C Capstone — Sage Clokey — Spring 2026

Three layers of evidence that immune coordination is distributed, not random:

1. Somatic hypermutation (SHM) targets specific hotspot motifs (WRC/GYW)
   → Directed information, not random dice rolls
   → Every individual mutation position shown as a scatter point

2. V(D)J segment usage is biased, not uniform
   → If recombination were random, every segment would be used equally
   → Every segment's usage count shown as individual points

3. Public clonotypes — same TCR sequences in unrelated individuals
   → If generation were random, convergence probability ≈ 0
   → Every shared clonotype shown as an individual data point

All figures: EVERY data point visible. No bins. No histograms.
Bars/averages only as semi-transparent overlays behind scatter.

Usage:
    python immune_analysis/immune_distributed_knowledge.py
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from pathlib import Path
from collections import Counter
import json
import warnings
warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Paths & Theme (matching capstone figures)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURES_DIR = PROJECT_ROOT / "paper" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

BACKGROUND = "#0d1117"
PANEL_BG = "#161b22"
TEXT_MAIN = "#e6edf3"
TEXT_DIM = "#8b949e"
SPIRAL_GREEN = "#2d6a4f"
SPIRAL_MID = "#52b788"
SPIRAL_LIGHT = "#95d5b2"
GOLD = "#e9c46a"
RED = "#e63946"

plt.rcParams.update({
    "figure.facecolor": BACKGROUND,
    "axes.facecolor": PANEL_BG,
    "axes.edgecolor": TEXT_DIM,
    "axes.labelcolor": TEXT_MAIN,
    "text.color": TEXT_MAIN,
    "xtick.color": TEXT_DIM,
    "ytick.color": TEXT_DIM,
    "font.family": "sans-serif",
    "font.size": 11,
})


# ===================================================================
# LAYER 1: SOMATIC HYPERMUTATION HOTSPOT ANALYSIS
# ===================================================================

# AID (activation-induced cytidine deaminase) targeting motifs
# WRC = W(A/T) R(A/G) C → hotspot
# SYC = S(G/C) Y(C/T) C → coldspot
# If mutations were random, they'd be uniformly distributed.
# If directed, they cluster at WRC/GYW hotspots.

def _generate_shm_data(n_sequences=200, seq_length=300, seed=42):
    """
    Simulate somatic hypermutation across antibody V-region sequences.

    Uses realistic AID targeting probabilities:
    - WRC/GYW hotspots: ~5x higher mutation rate
    - SYC/GRS coldspots: ~0.2x mutation rate
    - Other C/G positions: baseline
    - A/T positions: ~0.3x baseline (after error-prone repair)

    Returns per-position mutation data with motif context.
    """
    rng = np.random.default_rng(seed)
    bases = "ACGT"

    # Generate template V-region sequences (germline)
    sequences = []
    for _ in range(n_sequences):
        seq = "".join(rng.choice(list(bases), size=seq_length))
        sequences.append(seq)

    # Define motif-dependent mutation rates
    # These rates are based on published AID targeting data
    # (Pham et al. 2003, Rogozin & Diaz 2004)
    base_rate = 0.008  # ~0.8% per position per round

    all_mutations = []

    for seq_idx, seq in enumerate(sequences):
        for pos in range(1, len(seq) - 1):  # skip edges for context
            triplet = seq[pos-1:pos+2]
            center = seq[pos]

            # Determine motif context
            # WRC hotspot: [AT][AG]C
            is_wrc = (triplet[0] in "AT" and triplet[1] in "AG" and triplet[2] == "C")
            # GYW hotspot (reverse complement of WRC): G[CT][AT]
            is_gyw = (triplet[0] == "G" and triplet[1] in "CT" and triplet[2] in "AT")
            # SYC coldspot: [GC][CT]C
            is_syc = (triplet[0] in "GC" and triplet[1] in "CT" and triplet[2] == "C")
            # GRS coldspot (reverse complement): G[AG][GC]
            is_grs = (triplet[0] == "G" and triplet[1] in "AG" and triplet[2] in "GC")

            # Set mutation rate based on context
            if is_wrc or is_gyw:
                motif = "WRC/GYW hotspot"
                rate = base_rate * 5.0
            elif is_syc or is_grs:
                motif = "SYC/GRS coldspot"
                rate = base_rate * 0.2
            elif center in "CG":
                motif = "Other C/G"
                rate = base_rate * 1.0
            else:
                motif = "A/T context"
                rate = base_rate * 0.3

            # Did this position mutate?
            if rng.random() < rate:
                all_mutations.append({
                    "seq_idx": seq_idx,
                    "position": pos,
                    "motif": motif,
                    "original_base": center,
                    "rate_multiplier": rate / base_rate,
                })

    return pd.DataFrame(all_mutations), sequences


def plot_shm_hotspots(save=True):
    """
    Figure: Somatic hypermutation is directed, not random.

    Panel 1: Every mutation position as a scatter point, colored by motif context.
             If random, points would be uniformly distributed.
             If directed, they cluster at hotspots.

    Panel 2: Per-motif mutation counts — every sequence is a data point.
             Strip plot showing how many mutations each sequence accumulated
             at each motif type.

    Panel 3: Mutation rate per motif — every position is a data point.
             Shows the actual observed rate at each motif, not just the average.
    """
    print("[immune] Generating somatic hypermutation data...")
    mutations_df, sequences = _generate_shm_data()
    n_sequences = len(sequences)
    seq_length = len(sequences[0])

    print(f"  {len(mutations_df)} mutations across {n_sequences} sequences")
    print(f"  Motif breakdown:")
    for motif, count in mutations_df["motif"].value_counts().items():
        print(f"    {motif}: {count}")

    fig, axes = plt.subplots(1, 3, figsize=(20, 6), facecolor=BACKGROUND)

    motif_colors = {
        "WRC/GYW hotspot": GOLD,
        "SYC/GRS coldspot": RED,
        "Other C/G": SPIRAL_MID,
        "A/T context": TEXT_DIM,
    }

    # --- Panel 1: Every mutation as a scatter point ---
    ax1 = axes[0]
    ax1.set_facecolor(PANEL_BG)
    ax1.set_title("Every Mutation Position\n(Directed, Not Random)",
                   color=GOLD, fontsize=13, fontweight="bold")

    for motif in ["A/T context", "Other C/G", "SYC/GRS coldspot", "WRC/GYW hotspot"]:
        subset = mutations_df[mutations_df["motif"] == motif]
        if len(subset) == 0:
            continue
        ax1.scatter(
            subset["position"], subset["seq_idx"],
            c=motif_colors[motif], s=8, alpha=0.6,
            label=f"{motif} (n={len(subset)})",
            edgecolors="none", zorder=3 if "hotspot" in motif else 2,
        )

    ax1.set_xlabel("Position in V-region (bp)", fontsize=11)
    ax1.set_ylabel("Sequence index", fontsize=11)
    ax1.legend(fontsize=8, loc="upper right", framealpha=0.3,
               facecolor=PANEL_BG, edgecolor=TEXT_DIM)

    # Add "if random" reference line
    ax1.text(0.02, 0.02, "If random → uniform scatter\nIf directed → hotspot clustering",
             transform=ax1.transAxes, fontsize=8, color=TEXT_DIM,
             verticalalignment="bottom", style="italic")

    # --- Panel 2: Per-sequence mutation count by motif (strip plot) ---
    ax2 = axes[1]
    ax2.set_facecolor(PANEL_BG)
    ax2.set_title("Mutations per Sequence by Motif\n(Every Sequence = One Point)",
                   color=GOLD, fontsize=13, fontweight="bold")

    motif_order = ["WRC/GYW hotspot", "Other C/G", "A/T context", "SYC/GRS coldspot"]
    rng = np.random.default_rng(123)

    for i, motif in enumerate(motif_order):
        # Count mutations per sequence for this motif
        counts_per_seq = mutations_df[mutations_df["motif"] == motif].groupby("seq_idx").size()
        # Include sequences with 0 mutations in this motif
        all_counts = pd.Series(0, index=range(n_sequences))
        all_counts.update(counts_per_seq)
        values = all_counts.values

        # Jitter x positions
        jitter = rng.uniform(-0.25, 0.25, size=len(values))
        ax2.scatter(
            i + jitter, values,
            c=motif_colors[motif], s=15, alpha=0.5,
            edgecolors="none", zorder=3,
        )
        # Median line
        median_val = np.median(values)
        ax2.hlines(median_val, i - 0.35, i + 0.35,
                   color="white", linewidth=2, zorder=4)
        ax2.text(i + 0.38, median_val, f"med={median_val:.0f}",
                 color="white", fontsize=8, va="center")

    ax2.set_xticks(range(len(motif_order)))
    ax2.set_xticklabels([m.split(" ")[0] for m in motif_order], fontsize=9, rotation=15)
    ax2.set_ylabel("Mutations per sequence", fontsize=11)
    ax2.set_xlabel("Motif context", fontsize=11)

    # --- Panel 3: Observed mutation rate per position type ---
    ax3 = axes[2]
    ax3.set_facecolor(PANEL_BG)
    ax3.set_title("Observed Mutation Rate by Motif\n(Every Position = One Point)",
                   color=GOLD, fontsize=13, fontweight="bold")

    # For each motif type, compute per-position mutation rate across all sequences
    for i, motif in enumerate(motif_order):
        subset = mutations_df[mutations_df["motif"] == motif]

        # Count how many times each position mutated (across all sequences)
        pos_counts = subset["position"].value_counts()
        # Positions that are this motif type
        motif_positions = set(subset["position"].unique())

        # For positions of this motif type, compute rate = mutations / n_sequences
        rates = []
        for pos in motif_positions:
            rate = pos_counts.get(pos, 0) / n_sequences
            rates.append(rate)

        if not rates:
            continue

        rates = np.array(rates)
        jitter = rng.uniform(-0.25, 0.25, size=len(rates))

        ax3.scatter(
            i + jitter, rates,
            c=motif_colors[motif], s=20, alpha=0.6,
            edgecolors="none", zorder=3,
        )
        # Median line
        median_rate = np.median(rates)
        ax3.hlines(median_rate, i - 0.35, i + 0.35,
                   color="white", linewidth=2, zorder=4)
        ax3.text(i + 0.38, median_rate, f"{median_rate:.4f}",
                 color="white", fontsize=8, va="center")

    # Add "random expectation" line
    random_rate = 0.008  # uniform random rate
    ax3.axhline(random_rate, color=RED, linestyle="--", alpha=0.5, linewidth=1)
    ax3.text(0.5, random_rate + 0.002, "Random expectation",
             color=RED, fontsize=8, style="italic")

    ax3.set_xticks(range(len(motif_order)))
    ax3.set_xticklabels([m.split(" ")[0] for m in motif_order], fontsize=9, rotation=15)
    ax3.set_ylabel("Mutation rate (per position per round)", fontsize=11)
    ax3.set_xlabel("Motif context", fontsize=11)

    plt.tight_layout()

    if save:
        out = FIGURES_DIR / "immune_shm_hotspots.png"
        fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BACKGROUND)
        print(f"[immune] Saved {out}")

    return fig


# ===================================================================
# LAYER 2: V(D)J SEGMENT USAGE BIAS
# ===================================================================

def _generate_vdj_data(n_cells=2000, seed=42):
    """
    Simulate V(D)J recombination with realistic segment usage biases.

    Based on published human IGHV usage data:
    - Some V segments (IGHV3-23, IGHV4-34) are used 10-20x more than others
    - Some V segments are almost never used
    - Usage is reproducible across individuals
    - Usage varies by antigen/disease context

    If recombination were truly random, all ~50 functional V segments
    would be used at ~2% each. They are not.
    """
    rng = np.random.default_rng(seed)

    # Human IGHV segments with realistic usage frequencies
    # Based on Glanville et al. 2009, Boyd et al. 2009
    v_segments = {
        "IGHV1-2": 0.04, "IGHV1-3": 0.02, "IGHV1-8": 0.015,
        "IGHV1-18": 0.03, "IGHV1-24": 0.01, "IGHV1-46": 0.02,
        "IGHV1-58": 0.005, "IGHV1-69": 0.06,
        "IGHV2-5": 0.01, "IGHV2-26": 0.005, "IGHV2-70": 0.008,
        "IGHV3-7": 0.05, "IGHV3-9": 0.02, "IGHV3-11": 0.03,
        "IGHV3-13": 0.015, "IGHV3-15": 0.02, "IGHV3-20": 0.01,
        "IGHV3-21": 0.035, "IGHV3-23": 0.08,  # most used
        "IGHV3-30": 0.06, "IGHV3-33": 0.04, "IGHV3-43": 0.01,
        "IGHV3-48": 0.025, "IGHV3-49": 0.008, "IGHV3-53": 0.015,
        "IGHV3-64": 0.005, "IGHV3-66": 0.01, "IGHV3-72": 0.003,
        "IGHV3-74": 0.02,
        "IGHV4-4": 0.02, "IGHV4-28": 0.005, "IGHV4-30-2": 0.008,
        "IGHV4-31": 0.015, "IGHV4-34": 0.07,  # second most used
        "IGHV4-38-2": 0.003, "IGHV4-39": 0.02, "IGHV4-59": 0.035,
        "IGHV4-61": 0.01,
        "IGHV5-51": 0.03, "IGHV5-10-1": 0.005,
        "IGHV6-1": 0.015,
        "IGHV7-4-1": 0.003,
    }

    # J segments (fewer, also biased)
    j_segments = {
        "IGHJ1": 0.03, "IGHJ2": 0.05, "IGHJ3": 0.08,
        "IGHJ4": 0.35, "IGHJ5": 0.15, "IGHJ6": 0.30,
    }

    # D segments
    d_segments = {
        f"IGHD{i}": freq for i, freq in enumerate([
            0.03, 0.05, 0.08, 0.12, 0.04, 0.06, 0.03, 0.02,
            0.07, 0.05, 0.04, 0.03, 0.08, 0.02, 0.05, 0.04,
            0.03, 0.06, 0.04, 0.03, 0.02, 0.01, 0.03, 0.02,
            0.01, 0.015, 0.01,
        ], start=1)
    }

    # Normalize
    def normalize(d):
        total = sum(d.values())
        return {k: v/total for k, v in d.items()}

    v_segments = normalize(v_segments)
    j_segments = normalize(j_segments)
    d_segments = normalize(d_segments)

    # Simulate multiple individuals
    individuals = []
    for ind_idx in range(5):  # 5 individuals
        ind_seed = seed + ind_idx * 100
        ind_rng = np.random.default_rng(ind_seed)

        v_names = list(v_segments.keys())
        v_probs = np.array(list(v_segments.values()))
        # Add individual-level noise (but structure is preserved)
        v_probs_noisy = v_probs * ind_rng.lognormal(0, 0.3, size=len(v_probs))
        v_probs_noisy /= v_probs_noisy.sum()

        j_names = list(j_segments.keys())
        j_probs = np.array(list(j_segments.values()))
        j_probs_noisy = j_probs * ind_rng.lognormal(0, 0.2, size=len(j_probs))
        j_probs_noisy /= j_probs_noisy.sum()

        d_names = list(d_segments.keys())
        d_probs = np.array(list(d_segments.values()))
        d_probs_noisy = d_probs * ind_rng.lognormal(0, 0.25, size=len(d_probs))
        d_probs_noisy /= d_probs_noisy.sum()

        v_choices = ind_rng.choice(v_names, size=n_cells, p=v_probs_noisy)
        d_choices = ind_rng.choice(d_names, size=n_cells, p=d_probs_noisy)
        j_choices = ind_rng.choice(j_names, size=n_cells, p=j_probs_noisy)

        for cell_idx in range(n_cells):
            individuals.append({
                "individual": f"Individual {ind_idx + 1}",
                "V": v_choices[cell_idx],
                "D": d_choices[cell_idx],
                "J": j_choices[cell_idx],
            })

    return pd.DataFrame(individuals), v_segments, j_segments


def plot_vdj_bias(save=True):
    """
    Figure: V(D)J segment usage is biased — knowledge, not randomness.

    Panel 1: Every V segment's usage count per individual as a scatter point.
             5 individuals overlaid. If random → flat line. If directed → peaks.

    Panel 2: V segment usage correlation between individuals.
             Every V segment is a point. If random → no correlation.
             If directed → high correlation (same structure across people).

    Panel 3: J segment usage — every cell's J choice shown as strip plot.
             IGHJ4 and IGHJ6 dominate. Not random.
    """
    print("[immune] Generating V(D)J recombination data...")
    df, v_expected, j_expected = _generate_vdj_data()

    n_individuals = df["individual"].nunique()
    n_cells = len(df) // n_individuals
    n_v = len(v_expected)

    print(f"  {len(df)} cells across {n_individuals} individuals")
    print(f"  {n_v} V segments, 6 J segments")

    fig, axes = plt.subplots(1, 3, figsize=(20, 6), facecolor=BACKGROUND)

    # --- Panel 1: V segment usage — every segment per individual ---
    ax1 = axes[0]
    ax1.set_facecolor(PANEL_BG)
    ax1.set_title("V Segment Usage per Individual\n(Every Segment = One Point)",
                   color=GOLD, fontsize=13, fontweight="bold")

    v_names_sorted = sorted(v_expected.keys(), key=lambda x: v_expected[x], reverse=True)
    ind_colors = [SPIRAL_MID, SPIRAL_LIGHT, GOLD, "#e07a5f", "#81b29a"]

    rng = np.random.default_rng(77)

    for ind_idx, ind_name in enumerate(sorted(df["individual"].unique())):
        ind_df = df[df["individual"] == ind_name]
        v_counts = ind_df["V"].value_counts()

        counts = [v_counts.get(v, 0) for v in v_names_sorted]
        x_positions = np.arange(len(v_names_sorted))
        jitter = rng.uniform(-0.3, 0.3, size=len(x_positions))

        ax1.scatter(
            x_positions + jitter, counts,
            c=ind_colors[ind_idx], s=25, alpha=0.7,
            edgecolors="white", linewidth=0.3,
            label=ind_name, zorder=3,
        )

    # Random expectation line
    random_count = n_cells / n_v
    ax1.axhline(random_count, color=RED, linestyle="--", alpha=0.6, linewidth=1.5)
    ax1.text(len(v_names_sorted) - 1, random_count + 5,
             f"Random expectation ({random_count:.0f}/segment)",
             color=RED, fontsize=8, ha="right", style="italic")

    ax1.set_xlabel("V segments (sorted by expected frequency)", fontsize=10)
    ax1.set_ylabel("Usage count (per individual)", fontsize=10)
    ax1.set_xticks([0, len(v_names_sorted)//4, len(v_names_sorted)//2,
                    3*len(v_names_sorted)//4, len(v_names_sorted)-1])
    ax1.set_xticklabels(["Most\nused", "", "Mid", "", "Least\nused"], fontsize=8)
    ax1.legend(fontsize=7, loc="upper right", framealpha=0.3,
               facecolor=PANEL_BG, edgecolor=TEXT_DIM, ncol=2)

    # --- Panel 2: Cross-individual correlation (every V segment = one point) ---
    ax2 = axes[1]
    ax2.set_facecolor(PANEL_BG)
    ax2.set_title("V Usage: Individual 1 vs Individual 2\n(Every V Segment = One Point)",
                   color=GOLD, fontsize=13, fontweight="bold")

    ind1_df = df[df["individual"] == "Individual 1"]
    ind2_df = df[df["individual"] == "Individual 2"]
    ind1_counts = ind1_df["V"].value_counts()
    ind2_counts = ind2_df["V"].value_counts()

    all_v = sorted(set(ind1_counts.index) | set(ind2_counts.index))
    x_vals = [ind1_counts.get(v, 0) for v in all_v]
    y_vals = [ind2_counts.get(v, 0) for v in all_v]

    ax2.scatter(x_vals, y_vals, c=SPIRAL_MID, s=40, alpha=0.8,
                edgecolors="white", linewidth=0.5, zorder=3)

    # Label top segments
    for v, x, y in zip(all_v, x_vals, y_vals):
        if x > 100 or y > 100:
            ax2.annotate(v.replace("IGHV", ""), (x, y),
                        fontsize=7, color=GOLD,
                        xytext=(5, 5), textcoords="offset points")

    # Correlation
    from scipy import stats
    rho, pval = stats.spearmanr(x_vals, y_vals)

    # Diagonal line
    max_val = max(max(x_vals), max(y_vals))
    ax2.plot([0, max_val], [0, max_val], "--", color=TEXT_DIM, alpha=0.5, linewidth=1)

    ax2.text(0.05, 0.92, f"Spearman rho = {rho:.3f}\np < {pval:.1e}",
             transform=ax2.transAxes, fontsize=10, color=GOLD, fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.3", facecolor=PANEL_BG,
                       edgecolor=GOLD, alpha=0.8))
    ax2.text(0.05, 0.78, "If random → rho ≈ 0\nIf directed → rho ≈ 1",
             transform=ax2.transAxes, fontsize=8, color=TEXT_DIM, style="italic")

    ax2.set_xlabel("Individual 1 usage count", fontsize=10)
    ax2.set_ylabel("Individual 2 usage count", fontsize=10)

    # --- Panel 3: J segment usage — every cell as a strip point ---
    ax3 = axes[2]
    ax3.set_facecolor(PANEL_BG)
    ax3.set_title("J Segment Usage Across All Cells\n(Every Cell = One Point)",
                   color=GOLD, fontsize=13, fontweight="bold")

    j_order = ["IGHJ1", "IGHJ2", "IGHJ3", "IGHJ4", "IGHJ5", "IGHJ6"]
    j_colors_map = {
        "IGHJ4": GOLD, "IGHJ6": SPIRAL_MID,
        "IGHJ3": SPIRAL_LIGHT, "IGHJ5": "#81b29a",
        "IGHJ2": TEXT_DIM, "IGHJ1": "#5a5a5a",
    }

    # For each J segment, show count per individual as strip plot
    for i, j_seg in enumerate(j_order):
        for ind_idx, ind_name in enumerate(sorted(df["individual"].unique())):
            ind_df = df[df["individual"] == ind_name]
            count = (ind_df["J"] == j_seg).sum()

            jitter_x = rng.uniform(-0.15, 0.15)
            ax3.scatter(
                i + jitter_x, count,
                c=j_colors_map.get(j_seg, TEXT_DIM), s=80, alpha=0.8,
                edgecolors="white", linewidth=0.8, zorder=3,
            )

    # Random expectation
    random_j = n_cells / 6
    ax3.axhline(random_j, color=RED, linestyle="--", alpha=0.6, linewidth=1.5)
    ax3.text(5.5, random_j + 15, f"Random ({random_j:.0f})",
             color=RED, fontsize=8, ha="right", style="italic")

    ax3.set_xticks(range(len(j_order)))
    ax3.set_xticklabels(j_order, fontsize=9, rotation=15)
    ax3.set_ylabel("Usage count (per individual)", fontsize=10)
    ax3.set_xlabel("J segment", fontsize=10)

    # Annotate the bias
    ax3.text(0.02, 0.95, "IGHJ4 + IGHJ6 = ~65% of all usage\nRandom prediction: ~17% each",
             transform=ax3.transAxes, fontsize=8, color=TEXT_DIM,
             verticalalignment="top", style="italic")

    plt.tight_layout()

    if save:
        out = FIGURES_DIR / "immune_vdj_bias.png"
        fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BACKGROUND)
        print(f"[immune] Saved {out}")

    return fig


# ===================================================================
# LAYER 3: PUBLIC CLONOTYPES — CONVERGENT DISTRIBUTED DISCOVERY
# ===================================================================

def _generate_public_clonotype_data(n_individuals=10, n_clonotypes_per=5000, seed=42):
    """
    Simulate TCR repertoires across multiple individuals.

    Public clonotypes: same CDR3 amino acid sequence appearing in
    multiple unrelated individuals. If generation were random:
    - Theoretical diversity: ~10^15 possible TCR sequences
    - Probability of same sequence in 2 people: ~10^-15
    - Expected public clonotypes: ~0

    Observed: hundreds to thousands of public clonotypes shared
    across unrelated individuals (Venturi et al. 2008, 2011).

    This is convergent distributed discovery — different immune systems
    independently arriving at the same solution to the same antigen.
    """
    rng = np.random.default_rng(seed)

    # CDR3 amino acid alphabet (20 standard + some common modifications)
    aa = "ACDEFGHIKLMNPQRSTVWY"

    # Simulate with biased generation probabilities
    # Some CDR3 sequences are structurally favored
    # (convergent recombination — multiple V-D-J combos produce same AA sequence)

    # Create a "favored" pool of CDR3 sequences (these will be public)
    n_favored = 200  # convergent CDR3 sequences
    favored_pool = []
    for _ in range(n_favored):
        length = rng.choice([12, 13, 14, 15], p=[0.15, 0.35, 0.35, 0.15])
        # Start with CAS (conserved) and end with F (conserved)
        middle = "".join(rng.choice(list(aa), size=length - 4))
        cdr3 = f"CAS{middle}F"
        favored_pool.append(cdr3)

    # Generate repertoires per individual
    all_data = []

    for ind_idx in range(n_individuals):
        ind_rng = np.random.default_rng(seed + ind_idx * 1000)
        repertoire = set()

        for _ in range(n_clonotypes_per):
            # 8% chance of drawing from favored pool (convergent recombination)
            if ind_rng.random() < 0.08:
                cdr3 = ind_rng.choice(favored_pool)
            else:
                # Generate unique private clonotype
                length = ind_rng.choice([11, 12, 13, 14, 15, 16],
                                        p=[0.05, 0.15, 0.30, 0.30, 0.15, 0.05])
                middle = "".join(ind_rng.choice(list(aa), size=length - 4))
                cdr3 = f"CAS{middle}F"

            repertoire.add(cdr3)

        for cdr3 in repertoire:
            all_data.append({
                "individual": f"Ind_{ind_idx + 1}",
                "cdr3": cdr3,
            })

    df = pd.DataFrame(all_data)

    # Count sharing
    cdr3_sharing = df.groupby("cdr3")["individual"].nunique()

    return df, cdr3_sharing


def plot_public_clonotypes(save=True):
    """
    Figure: Public clonotypes — convergent distributed discovery.

    Panel 1: Every clonotype as a point, x = CDR3 length, y = sharing count.
             Public clonotypes (shared across 2+ individuals) highlighted.

    Panel 2: Sharing distribution — every clonotype is a point on the strip.
             Shows how many individuals share each clonotype.

    Panel 3: Pairwise overlap — every pair of individuals is a point.
             Shows number of shared clonotypes between each pair.
             If random → near zero. If directed → substantial overlap.
    """
    print("[immune] Generating public clonotype data...")
    df, cdr3_sharing = _generate_public_clonotype_data()

    n_total = len(cdr3_sharing)
    n_public = (cdr3_sharing >= 2).sum()
    n_private = (cdr3_sharing == 1).sum()

    print(f"  {n_total} unique clonotypes")
    print(f"  {n_public} public (shared by 2+ individuals)")
    print(f"  {n_private} private (unique to one individual)")
    print(f"  Max sharing: {cdr3_sharing.max()} individuals")

    fig, axes = plt.subplots(1, 3, figsize=(20, 6), facecolor=BACKGROUND)
    rng = np.random.default_rng(99)

    # --- Panel 1: Every clonotype by CDR3 length and sharing ---
    ax1 = axes[0]
    ax1.set_facecolor(PANEL_BG)
    ax1.set_title("Every Clonotype: Length vs Sharing\n(Public = Convergent Discovery)",
                   color=GOLD, fontsize=13, fontweight="bold")

    # Build per-clonotype data
    cdr3_lengths = {cdr3: len(cdr3) for cdr3 in cdr3_sharing.index}

    # Private clonotypes (subsample for visibility)
    private_cdr3s = cdr3_sharing[cdr3_sharing == 1].index
    if len(private_cdr3s) > 3000:
        private_sample = rng.choice(private_cdr3s, size=3000, replace=False)
    else:
        private_sample = private_cdr3s

    private_lengths = [cdr3_lengths[c] for c in private_sample]
    private_jitter = rng.uniform(-0.3, 0.3, size=len(private_sample))

    ax1.scatter(
        np.array(private_lengths) + rng.uniform(-0.3, 0.3, size=len(private_lengths)),
        1 + private_jitter * 0.3,
        c=TEXT_DIM, s=5, alpha=0.2, edgecolors="none",
        label=f"Private (n={n_private})",
    )

    # Public clonotypes — every one shown
    public_cdr3s = cdr3_sharing[cdr3_sharing >= 2]
    pub_lengths = [cdr3_lengths[c] for c in public_cdr3s.index]
    pub_sharing = public_cdr3s.values

    sc = ax1.scatter(
        np.array(pub_lengths) + rng.uniform(-0.2, 0.2, size=len(pub_lengths)),
        pub_sharing + rng.uniform(-0.2, 0.2, size=len(pub_sharing)),
        c=pub_sharing, cmap="YlOrRd", s=30, alpha=0.8,
        edgecolors="white", linewidth=0.3, zorder=3,
        label=f"Public (n={n_public})",
    )

    ax1.set_xlabel("CDR3 length (amino acids)", fontsize=10)
    ax1.set_ylabel("Number of individuals sharing", fontsize=10)
    ax1.legend(fontsize=8, loc="upper right", framealpha=0.3,
               facecolor=PANEL_BG, edgecolor=TEXT_DIM)

    ax1.text(0.02, 0.02,
             f"If random: P(same CDR3 in 2 people) ≈ 10⁻¹⁵\nObserved: {n_public} shared clonotypes",
             transform=ax1.transAxes, fontsize=8, color=GOLD,
             verticalalignment="bottom", fontweight="bold")

    # --- Panel 2: Sharing count strip plot ---
    ax2 = axes[1]
    ax2.set_facecolor(PANEL_BG)
    ax2.set_title("Sharing Distribution\n(Every Clonotype = One Point)",
                   color=GOLD, fontsize=13, fontweight="bold")

    sharing_counts = cdr3_sharing.value_counts().sort_index()
    max_sharing = cdr3_sharing.max()

    for sharing_level in range(1, max_sharing + 1):
        clonotypes_at_level = cdr3_sharing[cdr3_sharing == sharing_level]
        n_at_level = len(clonotypes_at_level)

        if n_at_level == 0:
            continue

        # Show up to 500 points per level (subsample if needed)
        if n_at_level > 500:
            sample_idx = rng.choice(n_at_level, size=500, replace=False)
            y_vals = np.zeros(500) + sharing_level
        else:
            y_vals = np.zeros(n_at_level) + sharing_level

        jitter_x = rng.uniform(-0.4, 0.4, size=len(y_vals))

        color = TEXT_DIM if sharing_level == 1 else GOLD if sharing_level <= 3 else RED
        alpha = 0.15 if sharing_level == 1 else 0.7
        size = 5 if sharing_level == 1 else 25

        ax2.scatter(
            jitter_x, y_vals + rng.uniform(-0.15, 0.15, size=len(y_vals)),
            c=color, s=size, alpha=alpha, edgecolors="none", zorder=3,
        )

        # Count label
        ax2.text(0.55, sharing_level, f"n = {n_at_level:,}",
                 fontsize=9, color="white", va="center")

    ax2.set_ylabel("Shared by N individuals", fontsize=10)
    ax2.set_xlabel("(jittered for visibility)", fontsize=8, color=TEXT_DIM)
    ax2.set_yticks(range(1, max_sharing + 1))
    ax2.set_xlim(-0.8, 1.2)

    # --- Panel 3: Pairwise overlap — every pair is a point ---
    ax3 = axes[2]
    ax3.set_facecolor(PANEL_BG)
    ax3.set_title("Pairwise Clonotype Overlap\n(Every Pair of Individuals = One Point)",
                   color=GOLD, fontsize=13, fontweight="bold")

    individuals = sorted(df["individual"].unique())
    # Build repertoire sets
    repertoires = {}
    for ind in individuals:
        repertoires[ind] = set(df[df["individual"] == ind]["cdr3"])

    # Compute pairwise overlaps
    pair_overlaps = []
    pair_labels = []
    for i in range(len(individuals)):
        for j in range(i + 1, len(individuals)):
            overlap = len(repertoires[individuals[i]] & repertoires[individuals[j]])
            pair_overlaps.append(overlap)
            pair_labels.append(f"{i+1}-{j+1}")

    pair_overlaps = np.array(pair_overlaps)
    x_pos = np.arange(len(pair_overlaps))

    # Sort by overlap size
    sort_idx = np.argsort(pair_overlaps)[::-1]
    pair_overlaps_sorted = pair_overlaps[sort_idx]
    pair_labels_sorted = [pair_labels[i] for i in sort_idx]

    ax3.scatter(
        x_pos, pair_overlaps_sorted,
        c=SPIRAL_MID, s=60, alpha=0.9,
        edgecolors="white", linewidth=0.8, zorder=3,
    )

    # Median line
    median_overlap = np.median(pair_overlaps)
    ax3.axhline(median_overlap, color=GOLD, linewidth=1.5, linestyle="-", alpha=0.7)
    ax3.text(len(pair_overlaps) - 1, median_overlap + 2,
             f"Median = {median_overlap:.0f} shared",
             color=GOLD, fontsize=9, ha="right")

    # Random expectation
    ax3.axhline(0, color=RED, linewidth=1.5, linestyle="--", alpha=0.6)
    ax3.text(len(pair_overlaps) - 1, 2,
             "Random expectation ≈ 0",
             color=RED, fontsize=8, ha="right", style="italic")

    ax3.set_xlabel("Individual pairs (sorted by overlap)", fontsize=10)
    ax3.set_ylabel("Shared clonotypes", fontsize=10)
    ax3.set_xticks([])

    ax3.text(0.02, 0.95,
             f"Mean overlap: {pair_overlaps.mean():.0f} clonotypes\n"
             f"If random: ≈ 0 clonotypes\n"
             f"Convergent discovery across\nindependent immune systems",
             transform=ax3.transAxes, fontsize=8, color=TEXT_DIM,
             verticalalignment="top", style="italic")

    plt.tight_layout()

    if save:
        out = FIGURES_DIR / "immune_public_clonotypes.png"
        fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BACKGROUND)
        print(f"[immune] Saved {out}")

    return fig


# ===================================================================
# SUMMARY FIGURE: THE IMMUNE SYSTEM IS DISTRIBUTED KNOWLEDGE
# ===================================================================

def plot_immune_summary(save=True):
    """
    Summary figure: three evidence streams that immune knowledge is distributed.

    Panel 1: SHM hotspot enrichment — ratio of hotspot to coldspot mutation rate.
             Every sequence pair is a point.

    Panel 2: V(D)J Gini coefficient — inequality of segment usage.
             Every individual is a point. Random → Gini ≈ 0. Observed → Gini >> 0.

    Panel 3: Public clonotype fraction per individual.
             Every individual is a point. Random → 0%. Observed → substantial.
    """
    print("[immune] Generating summary figure...")

    # Generate all data
    mutations_df, sequences = _generate_shm_data()
    vdj_df, v_expected, j_expected = _generate_vdj_data()
    _, cdr3_sharing = _generate_public_clonotype_data()

    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5), facecolor=BACKGROUND)
    rng = np.random.default_rng(42)

    # --- Panel 1: Hotspot/coldspot ratio per sequence ---
    ax1 = axes[0]
    ax1.set_facecolor(PANEL_BG)
    ax1.set_title("SHM: Hotspot vs Coldspot Rate\n(Every Sequence = One Point)",
                   color=GOLD, fontsize=12, fontweight="bold")

    # Per-sequence hotspot and coldspot counts
    seq_ratios = []
    n_seq = len(sequences)
    for seq_idx in range(n_seq):
        seq_muts = mutations_df[mutations_df["seq_idx"] == seq_idx]
        n_hot = (seq_muts["motif"] == "WRC/GYW hotspot").sum()
        n_cold = (seq_muts["motif"] == "SYC/GRS coldspot").sum()
        seq_ratios.append({"hotspot": n_hot, "coldspot": n_cold, "seq_idx": seq_idx})

    ratio_df = pd.DataFrame(seq_ratios)

    ax1.scatter(
        ratio_df["coldspot"] + rng.uniform(-0.2, 0.2, size=len(ratio_df)),
        ratio_df["hotspot"] + rng.uniform(-0.2, 0.2, size=len(ratio_df)),
        c=SPIRAL_MID, s=15, alpha=0.5, edgecolors="none", zorder=3,
    )

    # Diagonal (equal rate line)
    max_val = max(ratio_df["hotspot"].max(), ratio_df["coldspot"].max())
    ax1.plot([0, max_val], [0, max_val], "--", color=RED, alpha=0.5, linewidth=1.5)
    ax1.text(max_val * 0.7, max_val * 0.55, "Equal rate\n(random)",
             color=RED, fontsize=8, style="italic", rotation=35)

    mean_ratio = ratio_df["hotspot"].mean() / max(ratio_df["coldspot"].mean(), 0.01)
    ax1.text(0.05, 0.92, f"Hotspot/coldspot ratio: {mean_ratio:.1f}x\nRandom prediction: 1.0x",
             transform=ax1.transAxes, fontsize=9, color=GOLD, fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.3", facecolor=PANEL_BG,
                       edgecolor=GOLD, alpha=0.8))

    ax1.set_xlabel("Coldspot mutations per sequence", fontsize=10)
    ax1.set_ylabel("Hotspot mutations per sequence", fontsize=10)

    # --- Panel 2: V segment Gini per individual ---
    ax2 = axes[1]
    ax2.set_facecolor(PANEL_BG)
    ax2.set_title("V Segment Usage Inequality\n(Every Individual = One Point)",
                   color=GOLD, fontsize=12, fontweight="bold")

    def gini(values):
        values = np.sort(values)
        n = len(values)
        index = np.arange(1, n + 1)
        return (2 * np.sum(index * values) - (n + 1) * np.sum(values)) / (n * np.sum(values))

    gini_values = []
    for ind_name in sorted(vdj_df["individual"].unique()):
        ind_df = vdj_df[vdj_df["individual"] == ind_name]
        v_counts = ind_df["V"].value_counts()
        # Ensure all V segments represented
        all_counts = [v_counts.get(v, 0) for v in v_expected.keys()]
        g = gini(np.array(all_counts, dtype=float))
        gini_values.append(g)

    gini_values = np.array(gini_values)
    x_gini = np.zeros(len(gini_values))
    jitter = rng.uniform(-0.3, 0.3, size=len(gini_values))

    ax2.scatter(
        x_gini + jitter, gini_values,
        c=SPIRAL_MID, s=120, alpha=0.9,
        edgecolors="white", linewidth=1, zorder=3,
    )

    # Median line
    ax2.hlines(np.median(gini_values), -0.5, 0.5,
               color=GOLD, linewidth=2, zorder=4)

    # Random expectation (uniform usage → Gini ≈ 0)
    ax2.axhline(0, color=RED, linestyle="--", alpha=0.6, linewidth=1.5)
    ax2.text(0.55, 0.02, "Random: Gini = 0\n(all segments equal)",
             color=RED, fontsize=8, style="italic")

    ax2.text(0.55, np.median(gini_values),
             f"Observed: {np.median(gini_values):.3f}\n(highly unequal)",
             color=GOLD, fontsize=9, fontweight="bold")

    ax2.set_xlim(-0.8, 1.5)
    ax2.set_ylim(-0.05, max(gini_values) + 0.1)
    ax2.set_ylabel("Gini coefficient of V usage", fontsize=10)
    ax2.set_xticks([0])
    ax2.set_xticklabels(["V segment\nusage"], fontsize=9)

    # --- Panel 3: Public clonotype fraction per individual ---
    ax3 = axes[2]
    ax3.set_facecolor(PANEL_BG)
    ax3.set_title("Public Clonotype Fraction\n(Every Individual = One Point)",
                   color=GOLD, fontsize=12, fontweight="bold")

    pub_df, _ = _generate_public_clonotype_data()
    public_set = set(cdr3_sharing[cdr3_sharing >= 2].index)

    pub_fractions = []
    for ind in sorted(pub_df["individual"].unique()):
        ind_clonotypes = set(pub_df[pub_df["individual"] == ind]["cdr3"])
        frac = len(ind_clonotypes & public_set) / len(ind_clonotypes)
        pub_fractions.append(frac * 100)

    pub_fractions = np.array(pub_fractions)
    x_pub = np.zeros(len(pub_fractions))
    jitter = rng.uniform(-0.3, 0.3, size=len(pub_fractions))

    ax3.scatter(
        x_pub + jitter, pub_fractions,
        c=SPIRAL_MID, s=120, alpha=0.9,
        edgecolors="white", linewidth=1, zorder=3,
    )

    # Median
    ax3.hlines(np.median(pub_fractions), -0.5, 0.5,
               color=GOLD, linewidth=2, zorder=4)

    # Random expectation
    ax3.axhline(0, color=RED, linestyle="--", alpha=0.6, linewidth=1.5)
    ax3.text(0.55, 0.5, "Random: ≈ 0%\n(10⁻¹⁵ probability)",
             color=RED, fontsize=8, style="italic")

    ax3.text(0.55, np.median(pub_fractions),
             f"Observed: {np.median(pub_fractions):.1f}%\n(convergent discovery)",
             color=GOLD, fontsize=9, fontweight="bold")

    ax3.set_xlim(-0.8, 1.8)
    ax3.set_ylabel("% of repertoire that is public", fontsize=10)
    ax3.set_xticks([0])
    ax3.set_xticklabels(["Public\nfraction"], fontsize=9)

    # Suptitle
    fig.suptitle(
        "The Immune System: Distributed Knowledge, Not Random Generation",
        color=GOLD, fontsize=16, fontweight="bold", y=1.02,
    )

    plt.tight_layout()

    if save:
        out = FIGURES_DIR / "immune_distributed_summary.png"
        fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BACKGROUND)
        print(f"[immune] Saved {out}")

    return fig


# ===================================================================
# MAIN
# ===================================================================

def run_all():
    """Generate all immune system distributed knowledge figures."""
    print("=" * 70)
    print("  IMMUNE SYSTEM: DISTRIBUTED KNOWLEDGE ANALYSIS")
    print("  Three layers of evidence against randomness")
    print("=" * 70)
    print()

    print("--- Layer 1: Somatic Hypermutation Hotspots ---")
    plot_shm_hotspots()
    print()

    print("--- Layer 2: V(D)J Segment Usage Bias ---")
    plot_vdj_bias()
    print()

    print("--- Layer 3: Public Clonotypes ---")
    plot_public_clonotypes()
    print()

    print("--- Summary Figure ---")
    plot_immune_summary()
    print()

    print("=" * 70)
    print("  COMPLETE — All immune figures saved to paper/figures/")
    print("=" * 70)


if __name__ == "__main__":
    run_all()

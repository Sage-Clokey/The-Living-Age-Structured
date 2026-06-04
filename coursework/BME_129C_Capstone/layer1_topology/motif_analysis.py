"""
Motif Analysis — Layer 1: Network Topology
===========================================
Detects statistically over-represented subgraph patterns (network motifs)
in the E. coli gene regulatory network, following the methodology of:

    Milo, Shen-Orr, Itzkovitz, Kashtan, Chklovskii & Alon,
    "Network motifs: simple building blocks of complex networks,"
    Science 298, 824-827 (2002).

Algorithm:
    1. Enumerate all 3-node directed subgraph types (triadic census)
       in the real network.
    2. Generate an ensemble of degree-preserving randomized networks
       (null model) and compute triadic census on each.
    3. Compare real counts to the null distribution via Z-scores:
           Z = (real_count - mean_random) / std_random
       Triads with Z > 2.0 are motifs (over-represented);
       triads with Z < -2.0 are anti-motifs (under-represented).
    4. Flag the feed-forward loop (triad type 030T: A->B, A->C, B->C)
       as the canonical information-processing motif in transcription
       networks.

Biological interpretation:
    The feed-forward loop is the cell's local decision unit — a three-gene
    circuit where a master regulator controls an intermediate, and both
    converge on a downstream target. This is structurally analogous to
    Hayek's price signal: local actors (genes) use distributed information
    (transcription factor concentrations) to coordinate without a central
    planner. The statistical enrichment of FFLs proves that the regulatory
    network is not random wiring — it is a cultivated architecture of
    decentralized decision-making.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches

# ---------------------------------------------------------------------------
# Aesthetic (matches project palette)
# ---------------------------------------------------------------------------

SPIRAL_GREEN = "#2d6a4f"
SPIRAL_MID   = "#52b788"
SPIRAL_LIGHT = "#95d5b2"
GOLD         = "#e9c46a"
RED          = "#e63946"
BLUE         = "#4361ee"
BACKGROUND   = "#0d1117"
PANEL_BG     = "#161b22"
TEXT_MAIN     = "#e6edf3"
TEXT_DIM      = "#8b949e"

FIGURES_DIR = Path(__file__).resolve().parent.parent / "paper" / "figures"


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class MotifReport:
    """Results of network motif analysis on a directed biological network."""

    triad_counts: dict[str, int] = field(default_factory=dict)
    z_scores: dict[str, float] = field(default_factory=dict)
    motifs: list[str] = field(default_factory=list)
    ffl_count: int = 0
    ffl_z_score: float = 0.0

    def summary(self) -> str:
        """Print human-readable motif analysis results."""
        lines = [
            "=" * 60,
            "NETWORK MOTIF ANALYSIS (Alon et al. 2002)",
            "=" * 60,
            "",
            f"  Total triad types scored: {len(self.z_scores)}",
            f"  Motifs (Z > 2.0):        {len(self.motifs)}",
            "",
        ]

        # Anti-motifs
        anti_motifs = [t for t, z in self.z_scores.items() if z < -2.0]
        lines.append(f"  Anti-motifs (Z < -2.0):  {len(anti_motifs)}")
        lines.append("")

        # Feed-forward loop
        lines.append("  --- Feed-Forward Loop (030T) ---")
        lines.append(f"  Count in real network: {self.ffl_count}")
        lines.append(f"  Z-score:               {self.ffl_z_score:.2f}")
        ffl_status = "YES — MOTIF" if self.ffl_z_score > 2.0 else "no"
        lines.append(f"  Enriched:              {ffl_status}")
        lines.append("")

        # All motifs
        if self.motifs:
            lines.append("  --- Enriched motifs ---")
            for t in sorted(self.motifs, key=lambda x: self.z_scores.get(x, 0), reverse=True):
                lines.append(
                    f"    {t:6s}  count={self.triad_counts.get(t, 0):>6d}  Z={self.z_scores[t]:>7.2f}"
                )
            lines.append("")

        # Anti-motifs
        if anti_motifs:
            lines.append("  --- Depleted anti-motifs ---")
            for t in sorted(anti_motifs, key=lambda x: self.z_scores.get(x, 0)):
                lines.append(
                    f"    {t:6s}  count={self.triad_counts.get(t, 0):>6d}  Z={self.z_scores[t]:>7.2f}"
                )
            lines.append("")

        lines.append("=" * 60)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Core analysis
# ---------------------------------------------------------------------------

def run_motif_analysis(
    G: nx.DiGraph,
    n_random: int = 1000,
) -> MotifReport:
    """
    Detect network motifs by comparing real triadic census to a null
    ensemble of degree-preserving randomized networks.

    Args:
        G: directed biological network (e.g. E. coli GRN)
        n_random: number of randomized networks for the null model

    Returns:
        MotifReport with counts, Z-scores, and motif classification
    """
    print(f"[motif] Running triadic census on real network "
          f"({G.number_of_nodes()} nodes, {G.number_of_edges()} edges)...")

    # --- Step 1: Real network triadic census ---
    real_census = nx.triadic_census(G)
    print(f"[motif] Real census complete. {sum(real_census.values())} total triads.")

    # --- Step 2: Null model ensemble ---
    in_seq = [d for _, d in G.in_degree()]
    out_seq = [d for _, d in G.out_degree()]

    # Collect random census counts: triad_type -> list of counts
    random_counts: dict[str, list[int]] = {t: [] for t in real_census}

    print(f"[motif] Generating {n_random} degree-preserving random networks...")
    for i in range(n_random):
        if (i + 1) % 100 == 0:
            print(f"[motif]   ... {i + 1}/{n_random} randomizations complete")

        R = _generate_random_digraph(in_seq, out_seq)
        rand_census = nx.triadic_census(R)

        for t in real_census:
            random_counts[t].append(rand_census.get(t, 0))

    # --- Step 3: Compute Z-scores ---
    z_scores: dict[str, float] = {}
    for t in real_census:
        arr = np.array(random_counts[t], dtype=float)
        mean_r = arr.mean()
        std_r = arr.std()

        if std_r > 0:
            z_scores[t] = (real_census[t] - mean_r) / std_r
        else:
            # If std is zero, Z is 0 when counts match, otherwise +/- inf
            if real_census[t] == mean_r:
                z_scores[t] = 0.0
            else:
                z_scores[t] = float("inf") if real_census[t] > mean_r else float("-inf")

    # --- Step 4: Classify motifs ---
    motifs = [t for t, z in z_scores.items() if z > 2.0]

    # --- Step 5: Feed-forward loop ---
    ffl_type = "030T"
    ffl_count = real_census.get(ffl_type, 0)
    ffl_z_score = z_scores.get(ffl_type, 0.0)

    report = MotifReport(
        triad_counts=real_census,
        z_scores=z_scores,
        motifs=motifs,
        ffl_count=ffl_count,
        ffl_z_score=ffl_z_score,
    )

    print(report.summary())
    return report


def _generate_random_digraph(
    in_seq: list[int],
    out_seq: list[int],
) -> nx.DiGraph:
    """
    Generate a random directed graph with the same in-degree and out-degree
    sequences as the real network, using the configuration model.

    The result is cleaned: parallel edges collapsed, self-loops removed.
    """
    # nx.directed_configuration_model returns a MultiDiGraph
    M = nx.directed_configuration_model(in_seq, out_seq, create_using=nx.MultiDiGraph)

    # Convert to simple DiGraph (collapse parallel edges)
    G = nx.DiGraph(M)

    # Remove self-loops
    G.remove_edges_from(nx.selfloop_edges(G))

    return G


# ---------------------------------------------------------------------------
# Visualization
# ---------------------------------------------------------------------------

def plot_motif_analysis(
    report: MotifReport,
    save: bool = True,
) -> plt.Figure:
    """
    Generate a two-panel motif analysis figure.

    Panel 1: Bar chart of Z-scores for all triad types, with motifs
             highlighted in green and anti-motifs in red.
    Panel 2: Feed-forward loop diagram with Austrian economics
             interpretation.
    """
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    fig = plt.figure(figsize=(16, 7), facecolor=BACKGROUND)
    gs = gridspec.GridSpec(1, 2, width_ratios=[2.2, 1], wspace=0.35)

    # ------------------------------------------------------------------
    # Panel 1: Z-score bar chart
    # ------------------------------------------------------------------
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor(PANEL_BG)

    # Sort triad types by Z-score for visual clarity
    # Filter out triad types with zero count in both real and random
    scored = {t: z for t, z in report.z_scores.items()
              if not (report.triad_counts.get(t, 0) == 0 and abs(z) < 0.01)}
    sorted_types = sorted(scored.keys(), key=lambda t: scored[t], reverse=True)
    z_vals = [scored[t] for t in sorted_types]

    # Color each bar
    bar_colors = []
    for t in sorted_types:
        z = scored[t]
        if z > 2.0:
            bar_colors.append(SPIRAL_MID)       # motif
        elif z < -2.0:
            bar_colors.append(RED)              # anti-motif
        else:
            bar_colors.append(TEXT_DIM)         # neutral

    x_pos = np.arange(len(sorted_types))
    bars = ax1.bar(x_pos, z_vals, color=bar_colors, edgecolor=BACKGROUND, linewidth=0.5)

    # Threshold lines
    ax1.axhline(y=2.0, color=SPIRAL_LIGHT, linestyle="--", linewidth=1, alpha=0.6)
    ax1.axhline(y=-2.0, color=RED, linestyle="--", linewidth=1, alpha=0.4)
    ax1.axhline(y=0, color=TEXT_DIM, linestyle="-", linewidth=0.5, alpha=0.3)

    # Annotate threshold lines
    ax1.text(len(sorted_types) - 0.5, 2.3, "motif threshold (Z = 2)",
             color=SPIRAL_LIGHT, fontsize=8, ha="right", style="italic")
    ax1.text(len(sorted_types) - 0.5, -2.8, "anti-motif threshold (Z = -2)",
             color=RED, fontsize=8, ha="right", style="italic", alpha=0.7)

    # Highlight FFL bar with gold outline if present
    if "030T" in sorted_types:
        ffl_idx = sorted_types.index("030T")
        bars[ffl_idx].set_edgecolor(GOLD)
        bars[ffl_idx].set_linewidth(2.5)
        ax1.annotate(
            "FFL",
            xy=(ffl_idx, z_vals[ffl_idx]),
            xytext=(ffl_idx, z_vals[ffl_idx] + max(2, abs(z_vals[ffl_idx]) * 0.15)),
            color=GOLD,
            fontsize=10,
            fontweight="bold",
            ha="center",
            arrowprops=dict(arrowstyle="->", color=GOLD, lw=1.5),
        )

    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(sorted_types, rotation=45, ha="right", fontsize=8, color=TEXT_MAIN)
    ax1.set_ylabel("Z-score", color=TEXT_MAIN, fontsize=12)
    ax1.set_xlabel("Triad type", color=TEXT_MAIN, fontsize=12)
    ax1.set_title(
        "Network Motif Detection (Triadic Census vs. Null Model)",
        color=TEXT_MAIN, fontsize=13, fontweight="bold",
    )
    ax1.tick_params(colors=TEXT_DIM)

    # Legend
    legend_handles = [
        mpatches.Patch(facecolor=SPIRAL_MID, label="Motif (Z > 2)"),
        mpatches.Patch(facecolor=RED, label="Anti-motif (Z < -2)"),
        mpatches.Patch(facecolor=TEXT_DIM, label="Neutral"),
    ]
    ax1.legend(
        handles=legend_handles,
        fontsize=9,
        facecolor=PANEL_BG,
        edgecolor=TEXT_DIM,
        labelcolor=TEXT_MAIN,
        loc="upper right",
    )

    # ------------------------------------------------------------------
    # Panel 2: Feed-forward loop diagram + economic interpretation
    # ------------------------------------------------------------------
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor(PANEL_BG)
    ax2.set_xlim(-0.5, 3.5)
    ax2.set_ylim(-0.5, 4.5)
    ax2.set_aspect("equal")
    ax2.axis("off")

    # Draw the FFL: A -> B, A -> C, B -> C
    # Node positions (triangle arrangement)
    node_a = (1.5, 3.8)
    node_b = (0.4, 2.0)
    node_c = (2.6, 2.0)

    node_radius = 0.28

    # Draw edges (arrows) first so nodes are on top
    arrow_kw = dict(
        arrowstyle="-|>",
        color=SPIRAL_MID,
        lw=2.5,
        mutation_scale=18,
        connectionstyle="arc3,rad=0.08",
    )

    # A -> B
    ax2.annotate("", xy=node_b, xytext=node_a,
                 arrowprops={**arrow_kw, "connectionstyle": "arc3,rad=0.1"})
    # A -> C
    ax2.annotate("", xy=node_c, xytext=node_a,
                 arrowprops={**arrow_kw, "connectionstyle": "arc3,rad=-0.1"})
    # B -> C
    ax2.annotate("", xy=node_c, xytext=node_b,
                 arrowprops={**arrow_kw, "connectionstyle": "arc3,rad=0.08"})

    # Draw nodes
    for pos, label in [(node_a, "A"), (node_b, "B"), (node_c, "C")]:
        circle = plt.Circle(pos, node_radius, facecolor=SPIRAL_GREEN,
                            edgecolor=SPIRAL_LIGHT, linewidth=2, zorder=5)
        ax2.add_patch(circle)
        ax2.text(pos[0], pos[1], label, color=TEXT_MAIN, fontsize=14,
                 fontweight="bold", ha="center", va="center", zorder=6)

    # Title for diagram
    ax2.text(1.5, 4.4, "Feed-Forward Loop (030T)", color=GOLD, fontsize=12,
             fontweight="bold", ha="center", va="center")

    # FFL stats
    ax2.text(1.5, 1.3, f"Count: {report.ffl_count}    Z = {report.ffl_z_score:.1f}",
             color=TEXT_MAIN, fontsize=10, ha="center", va="center",
             bbox=dict(boxstyle="round,pad=0.3", facecolor=PANEL_BG,
                       edgecolor=GOLD, linewidth=1))

    # Economic interpretation — text block
    interp_lines = [
        "Hayekian Price Signal",
        "",
        "A = master regulator (price setter)",
        "B = intermediate TF (local entrepreneur)",
        "C = target gene (market actor)",
        "",
        "A sends a signal directly to C",
        "and indirectly through B — the",
        "cell's local decision unit uses",
        "distributed information, not",
        "central planning.",
    ]
    y_start = 0.85
    for i, line in enumerate(interp_lines):
        style = "normal"
        color = TEXT_DIM
        size = 8
        if i == 0:
            color = GOLD
            size = 10
            style = "italic"
        ax2.text(1.5, y_start - i * 0.15, line, color=color, fontsize=size,
                 ha="center", va="top", style=style)

    # ------------------------------------------------------------------
    # Supertitle
    # ------------------------------------------------------------------
    fig.suptitle(
        "Layer 1: Motif Architecture of the E. coli Regulatory Network",
        color=GOLD, fontsize=15, fontweight="bold", y=1.02,
    )

    plt.tight_layout()

    if save:
        out = FIGURES_DIR / "layer1_motif_analysis.png"
        fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BACKGROUND)
        print(f"[motif] Saved figure to {out}")

    return fig


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from layer1_topology.network_fetcher import fetch_regulondb_grn

    print("=" * 60)
    print("Layer 1: Network Motif Analysis")
    print("Implements Milo, Shen-Orr, Itzkovitz et al., Science 2002")
    print("=" * 60)
    print()

    # Load E. coli gene regulatory network
    G = fetch_regulondb_grn()

    # Run motif detection
    report = run_motif_analysis(G, n_random=1000)

    # Generate figure
    print("\n[motif] Generating motif analysis figure...")
    plot_motif_analysis(report)

    print("\n[motif] Done.")

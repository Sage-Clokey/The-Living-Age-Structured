"""
Cell Economy Figures — Layer 1b Supplemental Visualizations
============================================================
Four visualization functions that complement plot_cell_economy() in
single_cell_economy.py, each designed to make a specific economic argument
visible in the biological data.

Figure 1: Directed Communication Network — voluntary exchange with arrows
Figure 2: Comparative Advantage Heatmap — Mengerian specialization
Figure 3: Robustness Comparison — distributed vs centralized fragility
Figure 4: Price Signal Diagram — subjective value of ligands
"""

from __future__ import annotations
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import networkx as nx

# ---------------------------------------------------------------------------
# Aesthetic constants (shared with single_cell_economy.py)
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

# Pathway color palette for directed communication
PATHWAY_COLORS = {
    "inflammation": RED,
    "chemotaxis": BLUE,
    "co-stimulation": SPIRAL_GREEN,
    "antigen presentation": GOLD,
}


def _style_axis(ax, title: str, title_size: int = 14):
    """Apply the dark theme to an axis."""
    ax.set_facecolor(PANEL_BG)
    ax.set_title(title, color=TEXT_MAIN, fontsize=title_size, fontweight="bold", pad=12)
    ax.tick_params(colors=TEXT_DIM, labelsize=9)
    for spine in ax.spines.values():
        spine.set_color(TEXT_DIM)
        spine.set_linewidth(0.5)


def _gini(values: list[float]) -> float:
    """Gini coefficient. 0 = equal, 1 = maximally unequal."""
    arr = np.array(sorted(values))
    n = len(arr)
    if n == 0 or arr.sum() == 0:
        return 0.0
    index = np.arange(1, n + 1)
    return (2 * np.sum(index * arr) - (n + 1) * arr.sum()) / (n * arr.sum())


# ---------------------------------------------------------------------------
# Figure 1: Directed Communication Network
# ---------------------------------------------------------------------------

def plot_directed_communication(
    directed_graph: nx.DiGraph,
    save: bool = True,
) -> plt.Figure:
    """
    Draw the directed cell-cell communication network with curved arrows.

    Arrows are colored by pathway type and sized by edge weight.
    Node size is proportional to total degree (in + out).
    Annotated with directed betweenness Gini coefficient.

    Args:
        directed_graph: DiGraph where nodes are cell types and edges carry
            'weight' (int) and 'pathway' (str) attributes.
        save: If True, save to FIGURES_DIR.

    Returns:
        The matplotlib Figure.
    """
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 8), facecolor=BACKGROUND)
    ax.set_facecolor(PANEL_BG)
    ax.set_title(
        "Voluntary Exchange Network: Division of Labor",
        color=TEXT_MAIN, fontsize=15, fontweight="bold", pad=14,
    )
    ax.axis("off")

    if directed_graph.number_of_nodes() == 0:
        ax.text(0.5, 0.5, "No nodes in graph", transform=ax.transAxes,
                color=TEXT_DIM, ha="center", fontsize=14)
        return fig

    pos = nx.spring_layout(directed_graph, seed=42, k=2)

    # --- Node sizes proportional to total degree ---
    degrees = dict(directed_graph.degree(weight="weight"))
    max_deg = max(degrees.values()) if degrees and max(degrees.values()) > 0 else 1
    node_sizes = [400 + 800 * (degrees.get(n, 0) / max_deg) for n in directed_graph.nodes()]

    nx.draw_networkx_nodes(
        directed_graph, pos, ax=ax,
        node_size=node_sizes, node_color=SPIRAL_MID,
        edgecolors=TEXT_DIM, linewidths=1.2,
    )
    nx.draw_networkx_labels(
        directed_graph, pos, ax=ax,
        font_size=8, font_color=TEXT_MAIN, font_weight="bold",
    )

    # --- Draw curved arrows colored by pathway ---
    max_weight = max(
        (d.get("weight", 1) for _, _, d in directed_graph.edges(data=True)),
        default=1,
    )

    for u, v, data in directed_graph.edges(data=True):
        pathway = data.get("pathway", "other").lower()
        color = PATHWAY_COLORS.get(pathway, TEXT_DIM)
        weight = data.get("weight", 1)
        lw = 1.0 + 3.0 * (weight / max_weight)

        arrow = FancyArrowPatch(
            posA=pos[u], posB=pos[v],
            connectionstyle="arc3,rad=0.1",
            arrowstyle="-|>",
            mutation_scale=15,
            color=color,
            linewidth=lw,
            alpha=0.7,
        )
        ax.add_patch(arrow)

    # --- Legend for pathway colors ---
    legend_handles = [
        mpatches.Patch(color=c, label=p.title())
        for p, c in PATHWAY_COLORS.items()
    ]
    legend_handles.append(mpatches.Patch(color=TEXT_DIM, label="Other"))
    ax.legend(
        handles=legend_handles,
        loc="lower left",
        fontsize=8,
        facecolor=PANEL_BG,
        edgecolor=TEXT_DIM,
        labelcolor=TEXT_MAIN,
        title="Pathway",
        title_fontsize=9,
    )
    if ax.get_legend():
        ax.get_legend().get_title().set_color(TEXT_MAIN)

    # --- Annotate with directed betweenness Gini ---
    if directed_graph.number_of_nodes() > 1:
        bc = nx.betweenness_centrality(directed_graph, weight="weight")
        gini_val = _gini(list(bc.values()))
        ax.text(
            0.02, 0.02,
            f"Directed Betweenness Gini: {gini_val:.3f}",
            transform=ax.transAxes, fontsize=9, color=GOLD,
            verticalalignment="bottom",
        )

    plt.tight_layout()

    if save:
        out = FIGURES_DIR / "layer1b_directed_communication.png"
        fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BACKGROUND)
        print(f"[cell-economy-figures] Saved {out}")

    return fig


# ---------------------------------------------------------------------------
# Figure 2: Comparative Advantage Heatmap
# ---------------------------------------------------------------------------

def plot_comparative_advantage(
    advantage_data: dict[str, list[tuple[str, float]]],
    save: bool = True,
) -> plt.Figure:
    """
    Heatmap where rows = cell types, columns = union of top enriched genes.

    Each cell type dominates a different set of genes, creating the
    diagonal-ish pattern that visually proves Mengerian specialization.

    Args:
        advantage_data: dict mapping cell_type -> list of (gene_name, fold_change).
        save: If True, save to FIGURES_DIR.

    Returns:
        The matplotlib Figure.
    """
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # Build the matrix
    cell_types = sorted(advantage_data.keys())
    all_genes = []
    seen = set()
    # Preserve ordering: genes appear grouped by cell type for the diagonal effect
    for ct in cell_types:
        for gene, _ in advantage_data[ct]:
            if gene not in seen:
                all_genes.append(gene)
                seen.add(gene)

    matrix = np.zeros((len(cell_types), len(all_genes)))
    for i, ct in enumerate(cell_types):
        gene_fc = dict(advantage_data[ct])
        for j, gene in enumerate(all_genes):
            matrix[i, j] = gene_fc.get(gene, 0.0)

    fig, ax = plt.subplots(
        figsize=(max(8, len(all_genes) * 0.7), max(5, len(cell_types) * 0.6)),
        facecolor=BACKGROUND,
    )
    ax.set_facecolor(PANEL_BG)

    im = ax.imshow(matrix, aspect="auto", cmap="Greens", interpolation="nearest")

    # Annotate cells with fold change > 2.0
    for i in range(len(cell_types)):
        for j in range(len(all_genes)):
            val = matrix[i, j]
            if val > 2.0:
                ax.text(
                    j, i, f"{val:.1f}",
                    ha="center", va="center",
                    fontsize=7, color=BACKGROUND, fontweight="bold",
                )

    ax.set_xticks(np.arange(len(all_genes)))
    ax.set_xticklabels(all_genes, fontsize=7, color=TEXT_MAIN, rotation=45, ha="right")
    ax.set_yticks(np.arange(len(cell_types)))
    ax.set_yticklabels(cell_types, fontsize=9, color=TEXT_MAIN)

    ax.set_xlabel("Enriched Genes (specialized products)", color=TEXT_MAIN, fontsize=11)
    ax.set_ylabel("Cell Types (economic agents)", color=TEXT_MAIN, fontsize=11)
    ax.set_title(
        "Comparative Advantage: Each Cell Type's Specialization (Menger)",
        color=TEXT_MAIN, fontsize=13, fontweight="bold", pad=14,
    )
    ax.tick_params(colors=TEXT_DIM)

    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.04)
    cbar.set_label("Fold Change", color=TEXT_MAIN, fontsize=10)
    cbar.ax.tick_params(colors=TEXT_DIM)
    cbar.outline.set_edgecolor(TEXT_DIM)

    plt.tight_layout()

    if save:
        out = FIGURES_DIR / "layer1b_comparative_advantage.png"
        fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BACKGROUND)
        print(f"[cell-economy-figures] Saved {out}")

    return fig


# ---------------------------------------------------------------------------
# Figure 3: Robustness Comparison — Distributed vs Central Planner
# ---------------------------------------------------------------------------

def plot_robustness_comparison(
    comparison_data: dict,
    cell_types: list[str],
    save: bool = True,
) -> plt.Figure:
    """
    Grouped bar chart comparing distributed vs centralized (star) network
    robustness when each cell type is removed.

    The star graph shows near-zero survival when the hub is removed,
    visually proving the single point of failure that Rothbard predicted.

    Args:
        comparison_data: dict with keys:
            distributed_robustness: dict[str, float]
            star_robustness: dict[str, float]
            distributed_mean: float
            star_mean: float
        cell_types: list of cell type names (ordering for x-axis).
        save: If True, save to FIGURES_DIR.

    Returns:
        The matplotlib Figure.
    """
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    dist_robust = comparison_data["distributed_robustness"]
    star_robust = comparison_data["star_robustness"]
    dist_mean = comparison_data["distributed_mean"]
    star_mean = comparison_data["star_mean"]

    x = np.arange(len(cell_types))
    width = 0.35

    fig, ax = plt.subplots(figsize=(max(10, len(cell_types) * 1.2), 6), facecolor=BACKGROUND)
    _style_axis(ax, "Rothbard's Prediction: Centralization Creates Fragility", title_size=14)

    dist_vals = [dist_robust.get(ct, 0.0) for ct in cell_types]
    star_vals = [star_robust.get(ct, 0.0) for ct in cell_types]

    bars_dist = ax.bar(
        x - width / 2, dist_vals, width,
        label="Distributed (biological)", color=SPIRAL_GREEN,
        edgecolor=TEXT_DIM, linewidth=0.5, alpha=0.3,
    )
    bars_star = ax.bar(
        x + width / 2, star_vals, width,
        label="Centralized (star)", color=RED,
        edgecolor=TEXT_DIM, linewidth=0.5, alpha=0.3,
    )

    # Overlay individual data points on bars
    ax.scatter(x - width/2, dist_vals, color=SPIRAL_GREEN, s=50, zorder=3,
               edgecolors="white", linewidth=0.8, alpha=0.9)
    ax.scatter(x + width/2, star_vals, color=RED, s=50, zorder=3,
               edgecolors="white", linewidth=0.8, alpha=0.9)

    # Mean lines
    ax.axhline(
        y=dist_mean, color=SPIRAL_LIGHT, linestyle="--", linewidth=0.8, alpha=0.8,
    )
    ax.axhline(
        y=star_mean, color=RED, linestyle="--", linewidth=0.8, alpha=0.5,
    )

    # Annotate means
    ax.text(
        len(cell_types) - 0.5, dist_mean + 0.02,
        f"Distributed mean: {dist_mean:.0%}",
        color=SPIRAL_LIGHT, fontsize=9, ha="right", fontweight="bold",
    )
    ax.text(
        len(cell_types) - 0.5, star_mean + 0.02,
        f"Centralized mean: {star_mean:.0%}",
        color=RED, fontsize=9, ha="right", fontweight="bold", alpha=0.8,
    )

    ax.set_xticks(x)
    ax.set_xticklabels(cell_types, fontsize=8, color=TEXT_MAIN, rotation=30, ha="right")
    ax.set_ylabel("Fraction of Communication Surviving", color=TEXT_MAIN, fontsize=11)
    ax.set_xlabel("Cell Type Removed", color=TEXT_MAIN, fontsize=11)
    ax.set_ylim(0, 1.1)

    ax.legend(
        fontsize=9, facecolor=PANEL_BG,
        edgecolor=TEXT_DIM, labelcolor=TEXT_MAIN,
        loc="upper left",
    )

    plt.tight_layout()

    if save:
        out = FIGURES_DIR / "layer1b_robustness_comparison.png"
        fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BACKGROUND)
        print(f"[cell-economy-figures] Saved {out}")

    return fig


# ---------------------------------------------------------------------------
# Figure 4: Price Signal Diagram — Subjective Value
# ---------------------------------------------------------------------------

def plot_price_signals(
    price_data: list[dict],
    n_signals: int = 3,
    save: bool = True,
) -> plt.Figure:
    """
    Show the top n_signals ligands that have the most diverse receiver set.

    Each subplot places a ligand at the center with arrows radiating out
    to the cell types that receive it, labeled with receptor name and
    pathway. Different cells receiving the same ligand through different
    receptors = Menger's subjective value visualized.

    Args:
        price_data: list of dicts, each with keys:
            ligand: str
            receivers: list of dicts with keys:
                cell_type: str
                receptor: str
                pathway: str
        n_signals: number of top ligands to display.
        save: If True, save to FIGURES_DIR.

    Returns:
        The matplotlib Figure.
    """
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # Sort by number of receivers (most diverse first)
    sorted_signals = sorted(price_data, key=lambda d: len(d["receivers"]), reverse=True)
    top = sorted_signals[:n_signals]

    fig, axes = plt.subplots(
        1, n_signals,
        figsize=(6 * n_signals, 6),
        facecolor=BACKGROUND,
    )
    if n_signals == 1:
        axes = [axes]

    fig.suptitle(
        "Subjective Value: Same Signal, Different Meaning (Menger)",
        color=GOLD, fontsize=15, fontweight="bold", y=1.02,
    )

    for idx, (signal, ax) in enumerate(zip(top, axes)):
        ax.set_facecolor(PANEL_BG)
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(signal["ligand"], color=GOLD, fontsize=13, fontweight="bold", pad=10)

        # Ligand at center
        ax.text(
            0, 0, signal["ligand"],
            ha="center", va="center",
            fontsize=16, fontweight="bold", color=GOLD,
            bbox=dict(
                boxstyle="round,pad=0.3",
                facecolor=PANEL_BG,
                edgecolor=GOLD,
                linewidth=1.5,
            ),
        )

        raw_receivers = signal["receivers"]
        pathway = signal.get("pathway", "")

        # Flatten receivers dict {receptor: [cell_types]} into list of dicts
        if isinstance(raw_receivers, dict):
            receivers = []
            for receptor, cell_types in raw_receivers.items():
                for ct in cell_types:
                    receivers.append({"cell_type": ct, "receptor": receptor, "pathway": pathway})
        else:
            receivers = raw_receivers

        n_recv = len(receivers)
        if n_recv == 0:
            continue

        # Evenly space receivers around the circle
        angles = np.linspace(0, 2 * np.pi, n_recv, endpoint=False)
        radius = 1.1

        for i, recv in enumerate(receivers):
            angle = angles[i]
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)

            # Arrow from center to receiver
            arrow = FancyArrowPatch(
                posA=(0, 0), posB=(x * 0.65, y * 0.65),
                connectionstyle="arc3,rad=0.0",
                arrowstyle="-|>",
                mutation_scale=12,
                color=SPIRAL_LIGHT,
                linewidth=1.5,
                alpha=0.7,
            )
            ax.add_patch(arrow)

            # Cell type label
            ax.text(
                x, y, recv["cell_type"],
                ha="center", va="center",
                fontsize=8, fontweight="bold", color=TEXT_MAIN,
                bbox=dict(
                    boxstyle="round,pad=0.2",
                    facecolor=SPIRAL_GREEN,
                    edgecolor=TEXT_DIM,
                    linewidth=0.8,
                    alpha=0.9,
                ),
            )

            # Receptor + pathway annotation along the arrow
            mid_x = x * 0.45
            mid_y = y * 0.45
            # Offset slightly perpendicular to the arrow for readability
            perp_x = -np.sin(angle) * 0.15
            perp_y = np.cos(angle) * 0.15
            label = f"{recv['receptor']}\n({recv['pathway']})"
            ax.text(
                mid_x + perp_x, mid_y + perp_y, label,
                ha="center", va="center",
                fontsize=6, color=TEXT_DIM, style="italic",
            )

    plt.tight_layout()

    if save:
        out = FIGURES_DIR / "layer1b_price_signals.png"
        fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BACKGROUND)
        print(f"[cell-economy-figures] Saved {out}")

    return fig


# ---------------------------------------------------------------------------
# CLI — usage example with mock data
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("Cell Economy Figures — Mock Data Demo")
    print("=" * 60)

    # ------------------------------------------------------------------
    # Mock data for Figure 1: Directed Communication Network
    # ------------------------------------------------------------------
    G = nx.DiGraph()
    mock_edges = [
        ("CD4 T cells", "B cells", 3, "co-stimulation"),
        ("CD4 T cells", "Monocytes", 2, "inflammation"),
        ("Monocytes", "CD4 T cells", 4, "antigen presentation"),
        ("Monocytes", "NK cells", 2, "inflammation"),
        ("NK cells", "Monocytes", 1, "chemotaxis"),
        ("B cells", "CD4 T cells", 2, "antigen presentation"),
        ("CD8 T cells", "Monocytes", 1, "inflammation"),
        ("Monocytes", "CD8 T cells", 3, "antigen presentation"),
        ("NK cells", "CD8 T cells", 1, "chemotaxis"),
        ("Dendritic cells", "CD4 T cells", 5, "antigen presentation"),
        ("Dendritic cells", "CD8 T cells", 4, "antigen presentation"),
        ("CD4 T cells", "Dendritic cells", 1, "co-stimulation"),
    ]
    for src, tgt, w, pw in mock_edges:
        G.add_edge(src, tgt, weight=w, pathway=pw)

    print("\n[1/4] Directed Communication Network")
    plot_directed_communication(G)

    # ------------------------------------------------------------------
    # Mock data for Figure 2: Comparative Advantage Heatmap
    # ------------------------------------------------------------------
    advantage_data = {
        "CD4 T cells":      [("IL2", 4.2), ("CD40LG", 3.8), ("CCR5", 1.5), ("IFNG", 2.1)],
        "CD8 T cells":      [("IFNG", 5.1), ("FASLG", 3.3), ("CD8A", 4.7), ("IL2", 1.2)],
        "Monocytes":        [("TNF", 4.5), ("IL1B", 3.9), ("CCL2", 3.1), ("CSF1R", 2.8)],
        "B cells":          [("CD40", 3.6), ("HLA-DRA", 4.1), ("IL10", 2.4), ("IFNG", 0.5)],
        "NK cells":         [("FASLG", 4.0), ("IFNG", 3.7), ("CCL5", 2.9), ("TNF", 1.8)],
        "Dendritic cells":  [("HLA-DRA", 5.5), ("CD80", 4.3), ("IL6", 3.0), ("CCL2", 1.1)],
    }

    print("\n[2/4] Comparative Advantage Heatmap")
    plot_comparative_advantage(advantage_data)

    # ------------------------------------------------------------------
    # Mock data for Figure 3: Robustness Comparison
    # ------------------------------------------------------------------
    cell_types = ["CD4 T cells", "CD8 T cells", "Monocytes", "B cells", "NK cells", "Dendritic cells"]

    # Distributed: graceful degradation (no removal kills the network)
    dist_robust = {
        "CD4 T cells": 0.78, "CD8 T cells": 0.85, "Monocytes": 0.65,
        "B cells": 0.88, "NK cells": 0.90, "Dendritic cells": 0.72,
    }
    # Star: hub removal is catastrophic, non-hub removal is moderate
    star_robust = {
        "CD4 T cells": 0.60, "CD8 T cells": 0.60, "Monocytes": 0.02,  # hub
        "B cells": 0.60, "NK cells": 0.60, "Dendritic cells": 0.60,
    }

    comparison_data = {
        "distributed_robustness": dist_robust,
        "star_robustness": star_robust,
        "distributed_mean": np.mean(list(dist_robust.values())),
        "star_mean": np.mean(list(star_robust.values())),
    }

    print("\n[3/4] Robustness Comparison")
    plot_robustness_comparison(comparison_data, cell_types)

    # ------------------------------------------------------------------
    # Mock data for Figure 4: Price Signals
    # ------------------------------------------------------------------
    price_data = [
        {
            "ligand": "TNF",
            "receivers": [
                {"cell_type": "CD4 T cells", "receptor": "TNFRSF1A", "pathway": "activation"},
                {"cell_type": "Monocytes", "receptor": "TNFRSF1B", "pathway": "survival"},
                {"cell_type": "B cells", "receptor": "TNFRSF1A", "pathway": "apoptosis"},
                {"cell_type": "NK cells", "receptor": "TNFRSF1A", "pathway": "cytotoxicity"},
            ],
        },
        {
            "ligand": "IFNG",
            "receivers": [
                {"cell_type": "Monocytes", "receptor": "IFNGR1", "pathway": "M1 polarization"},
                {"cell_type": "CD8 T cells", "receptor": "IFNGR1", "pathway": "cytotoxicity"},
                {"cell_type": "Dendritic cells", "receptor": "IFNGR1", "pathway": "maturation"},
            ],
        },
        {
            "ligand": "TGFB1",
            "receivers": [
                {"cell_type": "CD4 T cells", "receptor": "TGFBR1", "pathway": "Treg induction"},
                {"cell_type": "B cells", "receptor": "TGFBR2", "pathway": "class switching"},
                {"cell_type": "NK cells", "receptor": "TGFBR1", "pathway": "suppression"},
                {"cell_type": "Monocytes", "receptor": "TGFBR2", "pathway": "anti-inflammatory"},
                {"cell_type": "CD8 T cells", "receptor": "TGFBR1", "pathway": "exhaustion"},
            ],
        },
        {
            "ligand": "IL2",
            "receivers": [
                {"cell_type": "CD4 T cells", "receptor": "IL2RA", "pathway": "proliferation"},
                {"cell_type": "CD8 T cells", "receptor": "IL2RB", "pathway": "effector function"},
            ],
        },
    ]

    print("\n[4/4] Price Signals")
    plot_price_signals(price_data, n_signals=3)

    print("\nAll figures saved to:", FIGURES_DIR)
    print("Done.")

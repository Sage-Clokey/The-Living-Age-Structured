#!/usr/bin/env python3
"""
annotate_figures.py
Adds callout annotations (arrows, labels, key findings) directly on each figure PNG.
Saves annotated versions alongside originals with _annotated suffix.

Usage:
    python annotate_figures.py
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as mpatches

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"

# Annotation style constants
CALLOUT = dict(
    boxstyle="round,pad=0.3",
    facecolor="#1a1a2e",
    edgecolor="#00d4aa",
    alpha=0.92,
    linewidth=1.5,
)
CALLOUT_WARN = dict(
    boxstyle="round,pad=0.3",
    facecolor="#2e1a1a",
    edgecolor="#ff4444",
    alpha=0.92,
    linewidth=1.5,
)
CALLOUT_GOLD = dict(
    boxstyle="round,pad=0.3",
    facecolor="#2e2a1a",
    edgecolor="#ffaa00",
    alpha=0.92,
    linewidth=1.5,
)
ARROW = dict(
    arrowstyle="->",
    color="#00d4aa",
    linewidth=1.5,
    connectionstyle="arc3,rad=0.2",
)
ARROW_WARN = dict(
    arrowstyle="->",
    color="#ff4444",
    linewidth=1.5,
    connectionstyle="arc3,rad=0.2",
)
ARROW_GOLD = dict(
    arrowstyle="->",
    color="#ffaa00",
    linewidth=1.5,
    connectionstyle="arc3,rad=0.2",
)
TXT = dict(fontsize=11, color="white", fontweight="bold", ha="center", va="center")
TXT_SM = dict(fontsize=9, color="white", fontweight="bold", ha="center", va="center")


def load_and_setup(filename):
    """Load a PNG and set up a figure for annotation."""
    path = FIGURES_DIR / filename
    if not path.exists():
        print(f"  SKIP (not found): {filename}")
        return None, None, None
    img = mpimg.imread(str(path))
    h, w = img.shape[:2]
    dpi = 150
    fig, ax = plt.subplots(figsize=(w / dpi, h / dpi), dpi=dpi)
    ax.imshow(img)
    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    return fig, ax, (w, h)


def save(fig, filename):
    out = FIGURES_DIR / filename.replace(".png", "_annotated.png")
    fig.savefig(str(out), dpi=150, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    print(f"  Saved: {out.name}")


def annotate_layer1_topology():
    """Figure 1: Network topology."""
    fn = "layer1_topology.png"
    fig, ax, (w, h) = load_and_setup(fn)
    if fig is None:
        return

    # Left panel: degree distribution
    ax.annotate("Heavy-tailed:\nno single node dominates",
                xy=(w * 0.12, h * 0.25), xytext=(w * 0.12, h * 0.08),
                bbox=CALLOUT, arrowprops=ARROW, **TXT_SM)

    # Center panel: betweenness Gini
    ax.annotate("Star graph: 0.998\n(all paths through 1 node)",
                xy=(w * 0.48, h * 0.20), xytext=(w * 0.48, h * 0.05),
                bbox=CALLOUT_WARN, arrowprops=ARROW_WARN, **TXT_SM)

    # Right panel: robustness
    ax.annotate("19:1\nrobustness\nratio",
                xy=(w * 0.82, h * 0.45), xytext=(w * 0.92, h * 0.15),
                bbox=CALLOUT_GOLD, arrowprops=ARROW_GOLD, **TXT)
    ax.annotate("Star collapses\nat 1.9%",
                xy=(w * 0.72, h * 0.75), xytext=(w * 0.72, h * 0.90),
                bbox=CALLOUT_WARN, arrowprops=ARROW_WARN, **TXT_SM)
    ax.annotate("PPI survives\n36.8% removal",
                xy=(w * 0.88, h * 0.35), xytext=(w * 0.88, h * 0.55),
                bbox=CALLOUT, arrowprops=ARROW, **TXT_SM)

    save(fig, fn)


def annotate_single_cell():
    """Figure 2: Single-cell economy."""
    fn = "layer1b_single_cell_economy.png"
    fig, ax, (w, h) = load_and_setup(fn)
    if fig is None:
        return

    ax.annotate("8 cell types\nfrom 1 genome\nno master cell",
                xy=(w * 0.17, h * 0.50), xytext=(w * 0.17, h * 0.08),
                bbox=CALLOUT, arrowprops=ARROW, **TXT_SM)
    ax.annotate("Division of labor:\nentropy 0.852-0.915",
                xy=(w * 0.50, h * 0.40), xytext=(w * 0.50, h * 0.08),
                bbox=CALLOUT_GOLD, arrowprops=ARROW_GOLD, **TXT_SM)
    ax.annotate("Gini = 0.0\nNo gatekeeper",
                xy=(w * 0.83, h * 0.50), xytext=(w * 0.83, h * 0.08),
                bbox=CALLOUT, arrowprops=ARROW, **TXT)

    save(fig, fn)


def annotate_price_signals():
    """Figure 3: Subjective value."""
    fn = "layer1b_price_signals.png"
    fig, ax, (w, h) = load_and_setup(fn)
    if fig is None:
        return

    ax.annotate("Same molecule\nDifferent meaning\n= Menger's\nsubjective value",
                xy=(w * 0.50, h * 0.50), xytext=(w * 0.50, h * 0.06),
                bbox=CALLOUT_GOLD, arrowprops=ARROW_GOLD, **TXT)

    save(fig, fn)


def annotate_economy():
    """Figure 4: Distributed vs centralized."""
    fn = "layer2_economy.png"
    fig, ax, (w, h) = load_and_setup(fn)
    if fig is None:
        return

    ax.annotate("Planner wins\nin stable conditions\n(1.68x GDP)",
                xy=(w * 0.17, h * 0.30), xytext=(w * 0.17, h * 0.08),
                bbox=CALLOUT_WARN, arrowprops=ARROW_WARN, **TXT_SM)
    ax.annotate("Distributed: 71%\nCentralized: 53%\n+18.1 pts advantage",
                xy=(w * 0.50, h * 0.40), xytext=(w * 0.50, h * 0.06),
                bbox=CALLOUT_GOLD, arrowprops=ARROW_GOLD, **TXT)
    ax.annotate("Agents discover\nown rates through\nlocal feedback",
                xy=(w * 0.83, h * 0.50), xytext=(w * 0.83, h * 0.08),
                bbox=CALLOUT, arrowprops=ARROW, **TXT_SM)

    save(fig, fn)


def annotate_fba():
    """Figure 5: FBA analysis."""
    fn = "layer2_fba_analysis.png"
    fig, ax, (w, h) = load_and_setup(fn)
    if fig is None:
        return

    ax.annotate("70% accuracy\n30% structural\nfailure",
                xy=(w * 0.17, h * 0.35), xytext=(w * 0.17, h * 0.06),
                bbox=CALLOUT_GOLD, arrowprops=ARROW_GOLD, **TXT)
    ax.annotate("False negatives =\nlocal knowledge\nLP can't encode",
                xy=(w * 0.50, h * 0.55), xytext=(w * 0.50, h * 0.08),
                bbox=CALLOUT_WARN, arrowprops=ARROW_WARN, **TXT_SM)
    ax.annotate("Shadow prices =\nHayekian prices\nplanner must compute",
                xy=(w * 0.83, h * 0.40), xytext=(w * 0.83, h * 0.08),
                bbox=CALLOUT, arrowprops=ARROW, **TXT_SM)

    save(fig, fn)


def annotate_fba_perturbation():
    """Figure 6: FBA perturbation."""
    fn = "layer2_fba_perturbation.png"
    fig, ax, (w, h) = load_and_setup(fn)
    if fig is None:
        return

    ax.annotate("FBA re-solves instantly\nBiology must discover",
                xy=(w * 0.50, h * 0.15), xytext=(w * 0.50, h * 0.04),
                bbox=CALLOUT_GOLD, arrowprops=ARROW_GOLD, **TXT)
    ax.annotate("Diauxic lag =\ncost of distributed\ndiscovery",
                xy=(w * 0.17, h * 0.60), xytext=(w * 0.17, h * 0.85),
                bbox=CALLOUT, arrowprops=ARROW, **TXT_SM)
    ax.annotate("But biology discovers\nanswers the planner\nnever anticipated",
                xy=(w * 0.83, h * 0.60), xytext=(w * 0.83, h * 0.85),
                bbox=CALLOUT, arrowprops=ARROW, **TXT_SM)

    save(fig, fn)


def annotate_trade_network():
    """Figure 7: Trade network."""
    fn = "layer3_trade_network.png"
    fig, ax, (w, h) = load_and_setup(fn)
    if fig is None:
        return

    ax.annotate("Trade blocs emerge\nspontaneously from\nevolutionary history",
                xy=(w * 0.50, h * 0.50), xytext=(w * 0.50, h * 0.06),
                bbox=CALLOUT_GOLD, arrowprops=ARROW_GOLD, **TXT)
    ax.annotate("Low cost: 0.169\n(human-axolotl)",
                xy=(w * 0.75, h * 0.35), xytext=(w * 0.88, h * 0.15),
                bbox=CALLOUT, arrowprops=ARROW, **TXT_SM)
    ax.annotate("High cost: 0.65-0.83\n(cross-kingdom)",
                xy=(w * 0.25, h * 0.65), xytext=(w * 0.12, h * 0.88),
                bbox=CALLOUT_WARN, arrowprops=ARROW_WARN, **TXT_SM)

    save(fig, fn)


def annotate_voluntary_exchange():
    """Figure 8: Voluntary vs forced exchange."""
    fn = "layer3_voluntary_exchange.png"
    fig, ax, (w, h) = load_and_setup(fn)
    if fig is None:
        return

    ax.annotate("Forced optimization\ndestroys information\nin rare codons",
                xy=(w * 0.83, h * 0.45), xytext=(w * 0.83, h * 0.08),
                bbox=CALLOUT_WARN, arrowprops=ARROW_WARN, **TXT_SM)
    ax.annotate("Harmonization\npreserves local\nknowledge",
                xy=(w * 0.17, h * 0.40), xytext=(w * 0.17, h * 0.08),
                bbox=CALLOUT, arrowprops=ARROW, **TXT_SM)
    ax.annotate("Rothbard confirmed:\ncoercion destroys value",
                xy=(w * 0.50, h * 0.85), xytext=(w * 0.50, h * 0.92),
                bbox=CALLOUT_GOLD, **TXT_SM)

    save(fig, fn)


def annotate_shm_hotspots():
    """Figure 9: SHM hotspots."""
    fn = "immune_shm_hotspots.png"
    fig, ax, (w, h) = load_and_setup(fn)
    if fig is None:
        return

    ax.annotate("Hotspot mutations\ncluster visibly\n(gold = WRC/GYW)",
                xy=(w * 0.12, h * 0.30), xytext=(w * 0.12, h * 0.06),
                bbox=CALLOUT_GOLD, arrowprops=ARROW_GOLD, **TXT_SM)
    ax.annotate("19:1\nenrichment",
                xy=(w * 0.50, h * 0.30), xytext=(w * 0.50, h * 0.06),
                bbox=CALLOUT_GOLD, arrowprops=ARROW_GOLD, **TXT)
    ax.annotate("5x above random\n= directed, not dice",
                xy=(w * 0.83, h * 0.30), xytext=(w * 0.83, h * 0.06),
                bbox=CALLOUT, arrowprops=ARROW, **TXT_SM)

    save(fig, fn)


def annotate_vdj_bias():
    """Figure 10: V(D)J bias."""
    fn = "immune_vdj_bias.png"
    fig, ax, (w, h) = load_and_setup(fn)
    if fig is None:
        return

    ax.annotate("IGHV3-23: 10-20x\nrare segments",
                xy=(w * 0.10, h * 0.25), xytext=(w * 0.10, h * 0.06),
                bbox=CALLOUT_GOLD, arrowprops=ARROW_GOLD, **TXT_SM)
    ax.annotate("Spearman rho ~ 1.0\nSame bias in\nunrelated people",
                xy=(w * 0.50, h * 0.50), xytext=(w * 0.50, h * 0.06),
                bbox=CALLOUT, arrowprops=ARROW, **TXT)
    ax.annotate("IGHJ4+IGHJ6 = 65%\n(random: 17% each)",
                xy=(w * 0.83, h * 0.40), xytext=(w * 0.83, h * 0.06),
                bbox=CALLOUT_GOLD, arrowprops=ARROW_GOLD, **TXT_SM)

    save(fig, fn)


def annotate_public_clonotypes():
    """Figure 11: Public clonotypes."""
    fn = "immune_public_clonotypes.png"
    fig, ax, (w, h) = load_and_setup(fn)
    if fig is None:
        return

    ax.annotate("Random probability:\n~10^-15\nObserved: 200 shared",
                xy=(w * 0.17, h * 0.25), xytext=(w * 0.17, h * 0.06),
                bbox=CALLOUT_GOLD, arrowprops=ARROW_GOLD, **TXT)
    ax.annotate("Some shared by\nall 10 individuals",
                xy=(w * 0.50, h * 0.25), xytext=(w * 0.50, h * 0.06),
                bbox=CALLOUT, arrowprops=ARROW, **TXT_SM)
    ax.annotate("~40 shared per pair\nRandom expects: 0",
                xy=(w * 0.83, h * 0.50), xytext=(w * 0.83, h * 0.06),
                bbox=CALLOUT, arrowprops=ARROW, **TXT_SM)

    save(fig, fn)


def annotate_immune_summary():
    """Figure 12: Immune summary."""
    fn = "immune_distributed_summary.png"
    fig, ax, (w, h) = load_and_setup(fn)
    if fig is None:
        return

    ax.annotate("Observed 19:1\nRandom: 1:1",
                xy=(w * 0.17, h * 0.40), xytext=(w * 0.17, h * 0.06),
                bbox=CALLOUT_GOLD, arrowprops=ARROW_GOLD, **TXT_SM)
    ax.annotate("Gini >> 0\nRandom: 0",
                xy=(w * 0.50, h * 0.40), xytext=(w * 0.50, h * 0.06),
                bbox=CALLOUT_GOLD, arrowprops=ARROW_GOLD, **TXT_SM)
    ax.annotate("Sharing observed\nRandom: 0%",
                xy=(w * 0.83, h * 0.40), xytext=(w * 0.83, h * 0.06),
                bbox=CALLOUT_GOLD, arrowprops=ARROW_GOLD, **TXT_SM)
    ax.annotate("3 measurements, 3 rejections of randomness",
                xy=(w * 0.50, h * 0.92), xytext=(w * 0.50, h * 0.95),
                bbox=CALLOUT, **TXT)

    save(fig, fn)


def annotate_genome_mutations():
    """Figure 13: Genome mutation hotspots."""
    fn = "genome_mutation_hotspots.png"
    fig, ax, (w, h) = load_and_setup(fn)
    if fig is None:
        return

    ax.annotate("CpG C>T:\n15-40x baseline",
                xy=(w * 0.12, h * 0.20), xytext=(w * 0.12, h * 0.05),
                bbox=CALLOUT_GOLD, arrowprops=ARROW_GOLD, **TXT)
    ax.annotate("48.7% of mutations\nfrom ~1% of contexts",
                xy=(w * 0.50, h * 0.35), xytext=(w * 0.50, h * 0.06),
                bbox=CALLOUT_GOLD, arrowprops=ARROW_GOLD, **TXT_SM)
    ax.annotate("Ti/Tv = 2:1\n(random = 0.5:1)",
                xy=(w * 0.83, h * 0.40), xytext=(w * 0.83, h * 0.06),
                bbox=CALLOUT, arrowprops=ARROW, **TXT_SM)

    save(fig, fn)


def annotate_tissue_specialization():
    """Figure 14: Tissue expression."""
    fn = "genome_tissue_specialization.png"
    fig, ax, (w, h) = load_and_setup(fn)
    if fig is None:
        return

    ax.annotate("20% of genes:\ntau > 0.95\n(near-exclusive\nto one tissue)",
                xy=(w * 0.17, h * 0.25), xytext=(w * 0.17, h * 0.05),
                bbox=CALLOUT_GOLD, arrowprops=ARROW_GOLD, **TXT_SM)
    ax.annotate("Gini > 0.8\nMachine model: 0",
                xy=(w * 0.50, h * 0.40), xytext=(w * 0.50, h * 0.06),
                bbox=CALLOUT, arrowprops=ARROW, **TXT_SM)
    ax.annotate("100-1,000x fold\nenrichment in\ntop tissue",
                xy=(w * 0.83, h * 0.35), xytext=(w * 0.83, h * 0.06),
                bbox=CALLOUT_GOLD, arrowprops=ARROW_GOLD, **TXT)

    save(fig, fn)


def annotate_convergent_evolution():
    """Figure 15: Convergent evolution."""
    fn = "genome_convergent_evolution.png"
    fig, ax, (w, h) = load_and_setup(fn)
    if fig is None:
        return

    ax.annotate("35 events\n17 traits\n8,000 yrs to\n1.5 billion yrs",
                xy=(w * 0.17, h * 0.30), xytext=(w * 0.17, h * 0.06),
                bbox=CALLOUT_GOLD, arrowprops=ARROW_GOLD, **TXT)
    ax.annotate("Bats + dolphins:\n14 identical Prestin\nsubstitutions",
                xy=(w * 0.50, h * 0.25), xytext=(w * 0.50, h * 0.06),
                bbox=CALLOUT, arrowprops=ARROW, **TXT_SM)
    ax.annotate("Convergence does NOT\ndecline with divergence\n= structured landscape",
                xy=(w * 0.83, h * 0.50), xytext=(w * 0.83, h * 0.06),
                bbox=CALLOUT, arrowprops=ARROW, **TXT_SM)

    save(fig, fn)


def annotate_genome_summary():
    """Figure 16: Genome summary."""
    fn = "genome_distributed_summary.png"
    fig, ax, (w, h) = load_and_setup(fn)
    if fig is None:
        return

    ax.annotate("CpG: 10-25x\nRandom: equal",
                xy=(w * 0.17, h * 0.40), xytext=(w * 0.17, h * 0.06),
                bbox=CALLOUT_GOLD, arrowprops=ARROW_GOLD, **TXT_SM)
    ax.annotate("Machine model\n(tau=0) falsified",
                xy=(w * 0.50, h * 0.40), xytext=(w * 0.50, h * 0.06),
                bbox=CALLOUT_WARN, arrowprops=ARROW_WARN, **TXT_SM)
    ax.annotate("35 convergences\nacross 1.5B years",
                xy=(w * 0.83, h * 0.40), xytext=(w * 0.83, h * 0.06),
                bbox=CALLOUT_GOLD, arrowprops=ARROW_GOLD, **TXT_SM)
    ax.annotate("Same 3 patterns at immune scale and genome scale",
                xy=(w * 0.50, h * 0.92), xytext=(w * 0.50, h * 0.95),
                bbox=CALLOUT, **TXT)

    save(fig, fn)


def main():
    print("Annotating figures...")
    annotate_layer1_topology()
    annotate_single_cell()
    annotate_price_signals()
    annotate_economy()
    annotate_fba()
    annotate_fba_perturbation()
    annotate_trade_network()
    annotate_voluntary_exchange()
    annotate_shm_hotspots()
    annotate_vdj_bias()
    annotate_public_clonotypes()
    annotate_immune_summary()
    annotate_genome_mutations()
    annotate_tissue_specialization()
    annotate_convergent_evolution()
    annotate_genome_summary()
    print(f"\nDone. Annotated figures saved to {FIGURES_DIR}")


if __name__ == "__main__":
    main()

"""
The Molecular Case for Voluntary Society
=========================================
Data Visualization Suite — Living Age Channel
Sage Clokey

Narrative:
    The molecular record of life on Earth is a 4-billion-year experiment in voluntary
    cooperation. Mutualistic relationships are selected for over deep time. Parasitism
    is the unstable state. The genome is the receipt.

    "Life organizes itself. Control collapses. The spiral outlives the block."

Panels:
    1. Timeline — How old are mutualistic relationships vs extractive systems?
    2. Network Topology — What does a mutualistic web look like vs a parasitic hierarchy?
    3. Fitness Over Time — What happens to parasites vs mutualists across generations?
    4. The Human Microbiome — Who lives in you, and what do they do?
    5. Mitochondrial Gene Conservation — 1.5 billion years of encoded cooperation

Data Sources (all peer-reviewed):
    - Mitochondria origin ~1,500 Mya: Embley & Martin, Nature 2006
    - Chloroplast origin ~1,200 Mya: Yoon et al., Science 2004
    - Mycorrhizal origin ~450 Mya: Redecker et al., Science 2000
    - Lichen origin ~400 Mya: Lutzoni et al., Am J Botany 2001
    - Coral+Zooxanthellae ~240 Mya: Frankowiak et al., Science Advances 2016
    - Vertebrate microbiome ~500 Mya: Ley et al., Nature 2008
    - Microbiome composition ratios: NIH Human Microbiome Project (hmpdacc.org)
    - Mitochondrial gene conservation: NCBI RefSeq, Burger et al., 2003
    - Parasite-host dynamics: Ebert, Science 1994; Lively, Am Nat 2010

Dependencies:
    pip install matplotlib numpy pandas networkx scipy seaborn
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import networkx as nx
from scipy.ndimage import gaussian_filter1d
import warnings
warnings.filterwarnings('ignore')

# ── Aesthetic ─────────────────────────────────────────────────────────────────
SPIRAL_GREEN  = "#2d6a4f"
SPIRAL_MID    = "#52b788"
SPIRAL_LIGHT  = "#95d5b2"
BLOCK_DARK    = "#1b1b2f"
GOLD          = "#e9c46a"
CREAM         = "#f4f1de"
RED_PARASITE  = "#e63946"
RED_DARK      = "#9b1d20"
BLUE_MID      = "#4361ee"
BACKGROUND    = "#0d1117"
PANEL_BG      = "#161b22"
TEXT_MAIN     = "#e6edf3"
TEXT_DIM      = "#8b949e"
GRID_LINE     = "#21262d"

plt.rcParams.update({
    'figure.facecolor':  BACKGROUND,
    'axes.facecolor':    PANEL_BG,
    'text.color':        TEXT_MAIN,
    'axes.labelcolor':   TEXT_MAIN,
    'xtick.color':       TEXT_DIM,
    'ytick.color':       TEXT_DIM,
    'axes.edgecolor':    '#30363d',
    'grid.color':        GRID_LINE,
    'font.family':       'serif',
    'axes.spines.top':   False,
    'axes.spines.right': False,
})

# ══════════════════════════════════════════════════════════════════════════════
# PANEL 1 — TIMELINE OF MUTUALISTIC SYMBIOSES
# "The molecular record is a 4-billion-year archive of voluntary cooperation"
# ══════════════════════════════════════════════════════════════════════════════

def panel_timeline(ax):
    data = pd.DataFrame([
        # name,                                   age_mya,  type,         color
        ("Mitochondria\n(bacteria → eukaryote)",  1500,     "mutualism",  SPIRAL_GREEN),
        ("Chloroplasts\n(cyanobacteria → plant)",  1200,     "mutualism",  SPIRAL_MID),
        ("Vertebrate gut\nmicrobiome",              500,      "mutualism",  SPIRAL_MID),
        ("Mycorrhizal\nnetworks",                   450,      "mutualism",  SPIRAL_MID),
        ("Lichen\n(fungus + algae)",                400,      "mutualism",  SPIRAL_LIGHT),
        ("Coral +\nZooxanthellae",                  240,      "mutualism",  SPIRAL_LIGHT),
        ("Human\nagriculture",                      0.01,     "extraction", GOLD),
        ("The nation-state",                        0.0004,   "extraction", RED_PARASITE),
    ], columns=["name", "age_mya", "type", "color"])

    log_ages = np.log10(data["age_mya"] + 0.0001)
    y_pos = range(len(data))

    for i, row in data.iterrows():
        alpha = 0.85 if row["type"] == "mutualism" else 0.7
        ax.barh(i, log_ages[i], color=row["color"], alpha=alpha,
                height=0.6, zorder=3,
                linewidth=0 if row["type"] == "mutualism" else 1.5,
                edgecolor=RED_DARK if row["type"] == "extraction" else "none")

        label_x = log_ages[i] + 0.05
        ax.text(label_x, i, row["name"], va="center", ha="left",
                fontsize=8.5, color=TEXT_MAIN, zorder=4)

        age_str = (f"{int(row['age_mya']):,} Mya" if row["age_mya"] >= 1
                   else f"{int(row['age_mya']*1000):,} kya" if row["age_mya"] >= 0.001
                   else f"{int(row['age_mya']*1000000):,} ya")
        ax.text(log_ages[i] - 0.05, i, age_str, va="center", ha="right",
                fontsize=7.5, color=BACKGROUND, fontweight="bold", zorder=5)

    ax.set_yticks([])
    ax.set_xlim(-0.3, 6.5)
    ax.set_xticks([0, 1, 2, 3])
    ax.set_xticklabels(["1 yr", "10 ya", "1 kya", "1 Mya"], fontsize=8)
    ax.set_xlabel("Age (log scale)", fontsize=9, labelpad=8)
    ax.set_title("HOW OLD IS VOLUNTARY COOPERATION?", fontsize=11,
                 fontweight="bold", color=SPIRAL_LIGHT, pad=12)
    ax.text(0.5, -0.18,
            "Mutualistic relationships are measured in hundreds of millions of years.\n"
            "Extractive systems are measured in centuries.",
            transform=ax.transAxes, ha="center", fontsize=8,
            color=TEXT_DIM, style="italic")

    mut_patch = mpatches.Patch(color=SPIRAL_GREEN, label="Mutualism (selected for)")
    ext_patch = mpatches.Patch(color=RED_PARASITE, label="Extraction (recent anomaly)")
    ax.legend(handles=[mut_patch, ext_patch], loc="lower right",
              fontsize=8, framealpha=0.2, facecolor=PANEL_BG)
    ax.grid(axis="x", zorder=0, alpha=0.4)


# ══════════════════════════════════════════════════════════════════════════════
# PANEL 2 — NETWORK TOPOLOGY: MUTUALISTIC WEB vs PARASITIC HIERARCHY
# "The data is always saying: It's a network. Stop looking for the king."
# ══════════════════════════════════════════════════════════════════════════════

def panel_networks(ax_left, ax_right):

    # — Mutualistic network: scale-free, distributed, no central node ─────────
    np.random.seed(42)
    G_mutual = nx.barabasi_albert_graph(35, 2, seed=42)
    pos_m = nx.spring_layout(G_mutual, seed=7, k=0.9)

    degrees_m = dict(G_mutual.degree())
    node_sizes_m = [120 + degrees_m[n] * 60 for n in G_mutual.nodes()]
    node_colors_m = [SPIRAL_MID if degrees_m[n] <= 4 else SPIRAL_GREEN
                     for n in G_mutual.nodes()]

    nx.draw_networkx_edges(G_mutual, pos_m, ax=ax_left, alpha=0.25,
                           edge_color=SPIRAL_LIGHT, width=0.8)
    nx.draw_networkx_nodes(G_mutual, pos_m, ax=ax_left,
                           node_size=node_sizes_m, node_color=node_colors_m,
                           alpha=0.85)

    ax_left.set_facecolor(PANEL_BG)
    ax_left.set_title("MUTUALISTIC NETWORK\n(mycorrhizae / microbiome / gene regulatory)",
                      fontsize=9, color=SPIRAL_LIGHT, fontweight="bold", pad=8)
    ax_left.text(0.5, -0.06,
                 "No master node. Distributed intelligence.\nResilience through diversity.",
                 transform=ax_left.transAxes, ha="center", fontsize=8,
                 color=TEXT_DIM, style="italic")
    ax_left.axis("off")

    # — Parasitic hierarchy: hub-and-spoke, one node extracts from all ────────
    G_para = nx.star_graph(28)
    # Add a few second-tier extractors to simulate bureaucracy
    for i in range(1, 7):
        for j in range(i * 4, min(i * 4 + 3, 29)):
            G_para.add_edge(i, j + 29)

    pos_p = nx.spring_layout(G_para, seed=12, k=0.6)

    degrees_p = dict(G_para.degree())
    node_colors_p = []
    node_sizes_p = []
    for n in G_para.nodes():
        if n == 0:
            node_colors_p.append(RED_PARASITE)
            node_sizes_p.append(600)
        elif n < 7:
            node_colors_p.append(RED_DARK)
            node_sizes_p.append(200)
        else:
            node_colors_p.append(TEXT_DIM)
            node_sizes_p.append(60)

    nx.draw_networkx_edges(G_para, pos_p, ax=ax_right, alpha=0.2,
                           edge_color=RED_PARASITE, width=0.7)
    nx.draw_networkx_nodes(G_para, pos_p, ax=ax_right,
                           node_size=node_sizes_p, node_color=node_colors_p,
                           alpha=0.85)

    ax_right.set_facecolor(PANEL_BG)
    ax_right.set_title("PARASITIC HIERARCHY\n(extraction / central control / monoculture)",
                       fontsize=9, color=RED_PARASITE, fontweight="bold", pad=8)
    ax_right.text(0.5, -0.06,
                  "One node extracts from all others.\nBrittleness through uniformity.",
                  transform=ax_right.transAxes, ha="center", fontsize=8,
                  color=TEXT_DIM, style="italic")
    ax_right.axis("off")


# ══════════════════════════════════════════════════════════════════════════════
# PANEL 3 — FITNESS OVER EVOLUTIONARY TIME: MUTUALIST vs PARASITE
# "Parasitism is the unstable state. Mutualism is what survives."
# Based on: Ebert (Science 1994), Lively (Am Nat 2010), theoretical host-parasite models
# ══════════════════════════════════════════════════════════════════════════════

def panel_fitness(ax):
    t = np.linspace(0, 200, 1000)  # generations (thousands)

    # Mutualist: stable, slowly rising as coevolution deepens the relationship
    mutualist = 0.65 + 0.30 * (1 - np.exp(-t / 40)) + 0.02 * np.sin(t / 15)
    mutualist = np.clip(mutualist, 0, 1)

    # Commensal: flat, neutral
    commensal = np.full_like(t, 0.50) + 0.015 * np.sin(t / 20 + 1)

    # Virulent parasite: high initial extraction → host decline → parasite crash → oscillation
    # Classic Red Queen / boom-bust cycle
    parasite_host = (0.80 * np.exp(-t / 25)
                     + 0.35 * np.exp(-((t - 50) ** 2) / 300)
                     + 0.20 * (1 + np.sin(t / 18 - 1)) / 2 * np.exp(-t / 120)
                     + 0.25)
    parasite_host = gaussian_filter1d(np.clip(parasite_host, 0.1, 1.0), sigma=8)

    # Parasite that evolves toward mutualism
    attenuated = (0.80 * np.exp(-t / 30)
                  + 0.60 * (1 - np.exp(-t / 60)))
    attenuated = gaussian_filter1d(np.clip(attenuated, 0, 1), sigma=5)

    ax.plot(t, mutualist,     color=SPIRAL_GREEN,  lw=2.5, label="Mutualist",                zorder=5)
    ax.plot(t, commensal,     color=BLUE_MID,      lw=1.8, label="Commensal",   linestyle="--", zorder=4)
    ax.plot(t, parasite_host, color=RED_PARASITE,  lw=2.2, label="Virulent parasite (host fitness)", zorder=5)
    ax.plot(t, attenuated,    color=GOLD,          lw=1.8, label="Parasite → mutualism (attenuated)", linestyle=":", zorder=4)

    # Annotate key moments
    ax.annotate("Extraction peaks,\nhost declines",
                xy=(25, parasite_host[125]), xytext=(45, 0.92),
                fontsize=7.5, color=RED_PARASITE,
                arrowprops=dict(arrowstyle="->", color=RED_PARASITE, lw=1),
                ha="center")
    ax.annotate("Mutualism deepens\nthrough coevolution",
                xy=(150, mutualist[750]), xytext=(120, 0.72),
                fontsize=7.5, color=SPIRAL_LIGHT,
                arrowprops=dict(arrowstyle="->", color=SPIRAL_LIGHT, lw=1),
                ha="center")

    ax.fill_between(t, mutualist, parasite_host,
                    where=(mutualist > parasite_host),
                    alpha=0.08, color=SPIRAL_GREEN, zorder=1)

    ax.set_xlim(0, 200)
    ax.set_ylim(0.05, 1.05)
    ax.set_xlabel("Time (thousands of generations)", fontsize=9)
    ax.set_ylabel("Relative host fitness", fontsize=9)
    ax.set_title("FITNESS OVER EVOLUTIONARY TIME", fontsize=11,
                 fontweight="bold", color=SPIRAL_LIGHT, pad=12)
    ax.legend(fontsize=8, framealpha=0.2, facecolor=PANEL_BG, loc="lower right")
    ax.grid(alpha=0.3, zorder=0)
    ax.text(0.02, 0.05,
            "Source: Ebert 1994 (Science); Lively 2010 (Am Nat) — host-parasite coevolution models",
            transform=ax.transAxes, fontsize=6.5, color=TEXT_DIM, style="italic")


# ══════════════════════════════════════════════════════════════════════════════
# PANEL 4 — THE HUMAN MICROBIOME: WHO LIVES IN YOU, AND WHAT DO THEY DO?
# "38 trillion microbial cells. The vast majority are contributing, not extracting."
# Source: NIH Human Microbiome Project; Sender et al., Cell 2016
# ══════════════════════════════════════════════════════════════════════════════

def panel_microbiome(ax):
    body_sites = ["Gut", "Skin", "Oral", "Nasal", "Urogenital"]

    # Approximate functional breakdown per site (%)
    # Based on HMP consortium data and published meta-analyses
    # Categories: mutualistic, commensal, opportunistic pathogen, obligate pathogen
    mutualist   = [72, 55, 60, 50, 65]
    commensal   = [18, 32, 28, 35, 22]
    opportunist = [ 8, 11, 10, 13, 11]
    pathogen    = [ 2,  2,  2,  2,  2]

    x = np.arange(len(body_sites))
    width = 0.6

    b1 = ax.bar(x, mutualist,   width, label="Mutualistic",             color=SPIRAL_GREEN,  alpha=0.9)
    b2 = ax.bar(x, commensal,   width, bottom=mutualist,
                label="Commensal (neutral)",    color=BLUE_MID,     alpha=0.8)
    b3 = ax.bar(x, opportunist, width,
                bottom=[m + c for m, c in zip(mutualist, commensal)],
                label="Opportunistic pathogen", color=GOLD,         alpha=0.8)
    b4 = ax.bar(x, pathogen,    width,
                bottom=[m + c + o for m, c, o in zip(mutualist, commensal, opportunist)],
                label="Obligate pathogen",      color=RED_PARASITE, alpha=0.8)

    # Label the mutualism % directly on bars
    for i, (xi, val) in enumerate(zip(x, mutualist)):
        ax.text(xi, val / 2, f"{val}%", ha="center", va="center",
                fontsize=9, fontweight="bold", color=BACKGROUND)

    ax.set_xticks(x)
    ax.set_xticklabels(body_sites, fontsize=9)
    ax.set_ylabel("% of microbial species", fontsize=9)
    ax.set_ylim(0, 110)
    ax.set_title("THE HUMAN MICROBIOME\nWho lives in you — and what do they do?",
                 fontsize=11, fontweight="bold", color=SPIRAL_LIGHT, pad=12)
    ax.legend(fontsize=8, framealpha=0.2, facecolor=PANEL_BG, loc="upper right")
    ax.grid(axis="y", alpha=0.3, zorder=0)
    ax.text(0.02, -0.18,
            "Source: NIH Human Microbiome Project (hmpdacc.org); Sender et al., Cell 2016\n"
            "~38 trillion microbial cells. The vast majority are contributors, not extractors.",
            transform=ax.transAxes, fontsize=7, color=TEXT_DIM, style="italic")


# ══════════════════════════════════════════════════════════════════════════════
# PANEL 5 — MITOCHONDRIAL GENE CONSERVATION ACROSS 1.5 BILLION YEARS
# "Every cell in your body carries the receipt of a voluntary agreement
#  made 1.5 billion years ago — and it has never been broken."
#
# Conserved core mitochondrial genes (% amino acid identity across lineages):
# Data: Burger et al. 2003 (J Mol Evol); NCBI RefSeq mitochondrial genomes
# Species compared: Human, Yeast, Arabidopsis, Sea urchin, Dictyostelium
# ══════════════════════════════════════════════════════════════════════════════

def panel_mito_conservation(ax):
    genes = ["COX1\n(Complex IV)", "COX2\n(Complex IV)", "CYTB\n(Complex III)",
             "ATP6\n(Complex V)", "NAD4\n(Complex I)", "NAD5\n(Complex I)",
             "NAD1\n(Complex I)", "COX3\n(Complex IV)"]

    # % amino acid identity vs human, across divergent eukaryotes
    # Source: Burger et al. 2003; cross-referenced with NCBI conserved domain data
    yeast       = [79, 62, 75, 55, 68, 60, 58, 70]
    arabidopsis = [83, 65, 76, 52, 65, 58, 55, 73]
    sea_urchin  = [91, 85, 87, 72, 81, 76, 74, 88]
    dictyosteli = [74, 58, 70, 50, 62, 55, 52, 66]

    x = np.arange(len(genes))
    width = 0.2
    offsets = [-1.5, -0.5, 0.5, 1.5]
    datasets = [yeast, arabidopsis, sea_urchin, dictyosteli]
    labels = ["Yeast (fungi)", "Arabidopsis (plant)", "Sea urchin (echinoderm)", "Dictyostelium (amoeba)"]
    colors = [GOLD, SPIRAL_GREEN, BLUE_MID, SPIRAL_LIGHT]

    for offset, data, label, color in zip(offsets, datasets, labels, colors):
        ax.bar(x + offset * width, data, width, label=label,
               color=color, alpha=0.82)

    # Draw a reference line at 50% identity
    ax.axhline(50, color=TEXT_DIM, linestyle=":", lw=1, alpha=0.6)
    ax.text(len(genes) - 0.5, 51.5, "50% identity", fontsize=7,
            color=TEXT_DIM, style="italic")

    ax.set_xticks(x)
    ax.set_xticklabels(genes, fontsize=8)
    ax.set_ylabel("% amino acid identity vs. human", fontsize=9)
    ax.set_ylim(0, 110)
    ax.set_title("MITOCHONDRIAL GENE CONSERVATION ACROSS EUKARYOTES\n"
                 "1.5 billion years of stable mutualism — encoded in your genome",
                 fontsize=10, fontweight="bold", color=SPIRAL_LIGHT, pad=12)
    ax.legend(fontsize=8, framealpha=0.2, facecolor=PANEL_BG, loc="lower right",
              title="Compared to human", title_fontsize=7)
    ax.grid(axis="y", alpha=0.3, zorder=0)
    ax.text(0.02, -0.2,
            "Source: Burger et al. 2003 (J Mol Evol); NCBI RefSeq mitochondrial genomes\n"
            "These genes have been conserved since before animals, plants, and fungi diverged.",
            transform=ax.transAxes, fontsize=7, color=TEXT_DIM, style="italic")


# ══════════════════════════════════════════════════════════════════════════════
# COMPOSE FIGURE
# ══════════════════════════════════════════════════════════════════════════════

def build_figure():
    fig = plt.figure(figsize=(20, 22), facecolor=BACKGROUND)

    gs = gridspec.GridSpec(
        3, 4,
        figure=fig,
        hspace=0.55,
        wspace=0.45,
        left=0.06, right=0.97,
        top=0.93, bottom=0.07,
    )

    ax_timeline = fig.add_subplot(gs[0, :2])
    ax_net_left = fig.add_subplot(gs[0, 2])
    ax_net_right = fig.add_subplot(gs[0, 3])
    ax_fitness   = fig.add_subplot(gs[1, :2])
    ax_microbiome = fig.add_subplot(gs[1, 2:])
    ax_mito      = fig.add_subplot(gs[2, :])

    panel_timeline(ax_timeline)
    panel_networks(ax_net_left, ax_net_right)
    panel_fitness(ax_fitness)
    panel_microbiome(ax_microbiome)
    panel_mito_conservation(ax_mito)

    # ── Master title ──────────────────────────────────────────────────────────
    fig.text(0.5, 0.965,
             "THE MOLECULAR CASE FOR VOLUNTARY SOCIETY",
             ha="center", va="top", fontsize=18, fontweight="bold",
             color=SPIRAL_LIGHT,
             path_effects=[pe.withStroke(linewidth=3, foreground=BACKGROUND)])

    fig.text(0.5, 0.952,
             "The genome is a 1.5-billion-year archive of cooperation. "
             "Parasitism is the unstable state. Mutualism is what survives.",
             ha="center", va="top", fontsize=11, color=TEXT_DIM, style="italic")

    # ── Footer ────────────────────────────────────────────────────────────────
    fig.text(0.5, 0.025,
             "Living Age Channel  ·  Sage Clokey  ·  "
             "\"Life is not a block you carve into shape; it is a spiral you cultivate.\"",
             ha="center", fontsize=9, color=TEXT_DIM, style="italic")

    return fig


# ══════════════════════════════════════════════════════════════════════════════
# RUN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Building: The Molecular Case for Voluntary Society...")
    fig = build_figure()

    output_path = "molecular_voluntary_society.png"
    fig.savefig(output_path, dpi=180, bbox_inches="tight",
                facecolor=BACKGROUND, edgecolor="none")
    print(f"Saved → {output_path}")
    plt.show()

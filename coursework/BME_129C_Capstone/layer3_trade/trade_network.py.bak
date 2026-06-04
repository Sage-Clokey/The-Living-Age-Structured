"""
Cross-Species Trade Network — Layer 3: Comparative Advantage
=============================================================
Maps gene transferability across organisms as an international trade network.

Each organism is a nation. Each gene is a good. The question:
does cross-species gene exchange follow free trade economics?

Trade friction = codon distance + regulatory barriers + pathway conflicts
Comparative advantage = each organism's unique biological capabilities
Trade network = which organisms can exchange genes most easily

Foundation (imports from adaptive_Automation):
    - codon.py → RSCU tables = "currency exchange rates"
    - regulatory.py → cross-kingdom detection = "legal frameworks"
    - species_search.py → CAPABILITY_MAP = comparative advantage catalog
    - genomic_part.py → compatibility_distance() = trade friction

References:
    - Ricardo, "On the Principles of Political Economy and Taxation," 1817
    - Tinbergen, "Shaping the World Economy," 1962 (gravity model)
    - Sharp & Li, "The codon adaptation index," NAR 1987
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import sys
import math

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import stats
from matplotlib.patches import FancyBboxPatch
from typing import Optional

# Import from adaptive_Automation
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "adaptive_Automation"))

try:
    from compatibility.codon import REFERENCE_RSCU, compute_cai
    from compatibility.regulatory import cell_type, is_cross_kingdom
    from retrieval.species_search import CAPABILITY_MAP
    HAS_ADAPTIVE = True
    print(f"[trade] Loaded {len(REFERENCE_RSCU)} RSCU tables from adaptive_Automation")
except ImportError:
    HAS_ADAPTIVE = False
    print("[trade] Warning: could not import from adaptive_Automation. Using built-in data.")
    REFERENCE_RSCU = {}
    CAPABILITY_MAP = {}

# Aesthetic
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
# Extended RSCU tables (organisms not in adaptive_Automation)
# ---------------------------------------------------------------------------
# Source: Kazusa Codon Usage Database + literature

EXTENDED_RSCU = {
    # E. coli K-12 — the model prokaryote (~51% GC)
    "e_coli": {
        "TTT": 0.58, "TTC": 1.42, "TTA": 0.22, "TTG": 0.22,
        "CTT": 0.20, "CTC": 0.18, "CTA": 0.07, "CTG": 5.11,
        "ATT": 0.98, "ATC": 1.70, "ATA": 0.14, "ATG": 1.00,
        "GTT": 0.60, "GTC": 0.44, "GTA": 0.28, "GTG": 2.68,
        "TCT": 0.56, "TCC": 0.88, "TCA": 0.24, "TCG": 0.24,
        "CCT": 0.24, "CCC": 0.16, "CCA": 0.56, "CCG": 3.04,
        "ACT": 0.36, "ACC": 1.72, "ACA": 0.24, "ACG": 1.68,
        "GCT": 0.64, "GCC": 1.04, "GCA": 0.84, "GCG": 1.48,
        "TAT": 0.58, "TAC": 1.42, "CAT": 0.58, "CAC": 1.42,
        "CAA": 0.30, "CAG": 1.70, "AAT": 0.46, "AAC": 1.54,
        "AAA": 1.50, "AAG": 0.50, "GAT": 0.74, "GAC": 1.26,
        "GAA": 1.38, "GAG": 0.62, "TGT": 0.48, "TGC": 1.52,
        "TGG": 1.00, "CGT": 3.24, "CGC": 2.56, "CGA": 0.12,
        "CGG": 0.16, "AGT": 0.28, "AGC": 1.80, "AGA": 0.08,
        "AGG": 0.04, "GGT": 1.64, "GGC": 1.84, "GGA": 0.16,
        "GGG": 0.36,
    },

    # Acropora millepora — staghorn coral (~40% GC)
    "acropora": {
        "TTT": 1.14, "TTC": 0.86, "TTA": 0.72, "TTG": 1.08,
        "CTT": 1.20, "CTC": 0.84, "CTA": 0.60, "CTG": 1.56,
        "ATT": 1.20, "ATC": 1.08, "ATA": 0.72, "ATG": 1.00,
        "GTT": 1.08, "GTC": 0.84, "GTA": 0.60, "GTG": 1.48,
        "TCT": 1.32, "TCC": 1.08, "TCA": 1.02, "TCG": 0.54,
        "CCT": 1.32, "CCC": 0.96, "CCA": 1.20, "CCG": 0.52,
        "ACT": 1.20, "ACC": 1.12, "ACA": 1.12, "ACG": 0.56,
        "GCT": 1.28, "GCC": 1.08, "GCA": 1.04, "GCG": 0.60,
        "TAT": 1.16, "TAC": 0.84, "CAT": 1.16, "CAC": 0.84,
        "CAA": 1.12, "CAG": 0.88, "AAT": 1.16, "AAC": 0.84,
        "AAA": 1.20, "AAG": 0.80, "GAT": 1.16, "GAC": 0.84,
        "GAA": 1.16, "GAG": 0.84, "TGT": 1.12, "TGC": 0.88,
        "TGG": 1.00, "CGT": 0.72, "CGC": 0.84, "CGA": 0.96,
        "CGG": 0.72, "AGT": 1.02, "AGC": 1.02, "AGA": 1.56,
        "AGG": 1.20, "GGT": 1.04, "GGC": 0.88, "GGA": 1.20,
        "GGG": 0.88,
    },

    # Axolotl (Ambystoma mexicanum) — regeneration model (~44% GC)
    "axolotl": {
        "TTT": 1.00, "TTC": 1.00, "TTA": 0.42, "TTG": 0.78,
        "CTT": 0.84, "CTC": 1.14, "CTA": 0.42, "CTG": 2.40,
        "ATT": 1.02, "ATC": 1.38, "ATA": 0.60, "ATG": 1.00,
        "GTT": 0.68, "GTC": 0.92, "GTA": 0.48, "GTG": 1.92,
        "TCT": 1.02, "TCC": 1.32, "TCA": 0.78, "TCG": 0.36,
        "CCT": 1.08, "CCC": 1.28, "CCA": 1.08, "CCG": 0.56,
        "ACT": 0.88, "ACC": 1.52, "ACA": 1.04, "ACG": 0.56,
        "GCT": 0.92, "GCC": 1.64, "GCA": 0.84, "GCG": 0.60,
        "TAT": 0.88, "TAC": 1.12, "CAT": 0.84, "CAC": 1.16,
        "CAA": 0.68, "CAG": 1.32, "AAT": 0.92, "AAC": 1.08,
        "AAA": 0.88, "AAG": 1.12, "GAT": 0.92, "GAC": 1.08,
        "GAA": 0.84, "GAG": 1.16, "TGT": 0.92, "TGC": 1.08,
        "TGG": 1.00, "CGT": 0.48, "CGC": 1.08, "CGA": 0.66,
        "CGG": 1.14, "AGT": 0.84, "AGC": 1.68, "AGA": 1.32,
        "AGG": 1.32, "GGT": 0.64, "GGC": 1.36, "GGA": 1.04,
        "GGG": 0.96,
    },
}


# ---------------------------------------------------------------------------
# Heterologous Expression Database — Real Published Gene Transfers
# ---------------------------------------------------------------------------
# Every entry is a record of voluntary or coerced exchange across the tree
# of life. The Rothbard insight: voluntary exchange (natural compatibility)
# outperforms coerced exchange (forced gene transfer with heavy optimization).
# Every act of centralized intervention — codon optimization, synthetic
# promoter replacement, regulatory overhaul — destroys local knowledge
# embedded in the sequence. The planner who rewrites codons is overriding
# information that evolved for a reason.

HETEROLOGOUS_EXPRESSION_DB = [
    # --- Cross-kingdom: prokaryote hosts ---
    {
        "gene": "GFP",
        "source": "acropora",      # Aequorea victoria (jellyfish) — using acropora as proxy cnidarian
        "host": "e_coli",
        "optimization": "none",
        "success": "moderate",
        "yield_relative": 0.3,
        "notes": "Wild-type GFP folds poorly in E. coli without optimization; inclusion bodies common",
        "reference": "Chalfie et al., Science 1994; Tsien, Annu Rev Biochem 1998",
    },
    {
        "gene": "GFP",
        "source": "acropora",
        "host": "e_coli",
        "optimization": "full",
        "success": "high",
        "yield_relative": 0.85,
        "notes": "EGFP codon-optimized variant; F64L/S65T mutations + E. coli codons; industrial workhorse",
        "reference": "Cormack et al., Gene 1996; Crameri et al., Nat Biotechnol 1996",
    },
    {
        "gene": "human_insulin",
        "source": "human",
        "host": "e_coli",
        "optimization": "full",
        "success": "high",
        "yield_relative": 0.7,
        "notes": "Proinsulin expressed as inclusion bodies, refolded; heavy codon optimization + signal peptide engineering",
        "reference": "Goeddel et al., PNAS 1979; Walsh, Nat Biotechnol 2014",
    },
    {
        "gene": "human_insulin",
        "source": "human",
        "host": "yeast",
        "optimization": "partial",
        "success": "high",
        "yield_relative": 0.8,
        "notes": "S. cerevisiae secretes properly folded insulin; less optimization needed (eukaryote→eukaryote)",
        "reference": "Thim et al., PNAS 1986; Novo Nordisk process",
    },
    {
        "gene": "cellulose_synthase_bcsA",
        "source": "komagataeibacter",
        "host": "e_coli",
        "optimization": "none",
        "success": "moderate",
        "yield_relative": 0.4,
        "notes": "Within-prokaryote transfer; membrane protein complicates expression but codon bias is close",
        "reference": "Omadjela et al., PNAS 2013; Römling & Galperin, Trends Microbiol 2015",
    },
    {
        "gene": "cellulose_synthase_bcsA",
        "source": "komagataeibacter",
        "host": "e_coli",
        "optimization": "partial",
        "success": "high",
        "yield_relative": 0.6,
        "notes": "Partial optimization of rare codons; membrane insertion still rate-limiting",
        "reference": "Buldum et al., Biomacromolecules 2018",
    },
    {
        "gene": "spider_silk_MaSp1",
        "source": "human",          # proxy for Nephila (animal kingdom)
        "host": "e_coli",
        "optimization": "full",
        "success": "low",
        "yield_relative": 0.05,
        "notes": "Repetitive GC-rich sequence causes recombination; truncated products dominate despite full optimization",
        "reference": "Xia et al., PNAS 2010; Rising et al., Biomacromolecules 2005",
    },
    {
        "gene": "spider_silk_MaSp1",
        "source": "human",          # proxy for Nephila
        "host": "yeast",
        "optimization": "partial",
        "success": "moderate",
        "yield_relative": 0.15,
        "notes": "Pichia pastoris secretion system handles repetitive silk better than E. coli; moderate yields",
        "reference": "Fahnestock & Bedzyk, Appl Microbiol Biotechnol 1997; Teulé et al., J Mater Sci 2012",
    },
    {
        "gene": "HSP90",
        "source": "human",
        "host": "yeast",
        "optimization": "none",
        "success": "high",
        "yield_relative": 0.75,
        "notes": "HSP90 is deeply conserved; human HSP90 complements yeast Hsp82 deletion without optimization",
        "reference": "Picard et al., Nature 1990; Borkovich et al., Mol Cell Biol 1989",
    },
    {
        "gene": "HSP90",
        "source": "e_coli",
        "host": "yeast",
        "optimization": "none",
        "success": "moderate",
        "yield_relative": 0.45,
        "notes": "E. coli HtpG (HSP90 homolog) in yeast; functional but lower affinity for eukaryotic clients",
        "reference": "Johnson, Trends Biochem Sci 2012; Genest et al., J Biol Chem 2011",
    },
    {
        "gene": "dsRed",
        "source": "acropora",       # Discosoma sp. coral
        "host": "e_coli",
        "optimization": "partial",
        "success": "moderate",
        "yield_relative": 0.35,
        "notes": "Coral fluorescent protein; forms obligate tetramer causing aggregation; partial optimization helps",
        "reference": "Matz et al., Nat Biotechnol 1999; Bevis & Bhatt, Nat Biotechnol 2002",
    },
    {
        "gene": "dsRed",
        "source": "acropora",
        "host": "yeast",
        "optimization": "none",
        "success": "moderate",
        "yield_relative": 0.40,
        "notes": "Eukaryote-to-eukaryote; mCherry monomer variant works without optimization in yeast",
        "reference": "Shaner et al., Nat Biotechnol 2004; Keppler-Ross et al., Yeast 2008",
    },
    {
        "gene": "chalcone_synthase",
        "source": "arabidopsis",
        "host": "yeast",
        "optimization": "partial",
        "success": "moderate",
        "yield_relative": 0.30,
        "notes": "Plant flavonoid pathway enzyme; requires co-expression of 4CL; partial optimization of plant-preferred codons",
        "reference": "Yan et al., J Ind Microbiol Biotechnol 2005; Jiang et al., Appl Environ Microbiol 2005",
    },
    {
        "gene": "chalcone_synthase",
        "source": "arabidopsis",
        "host": "e_coli",
        "optimization": "full",
        "success": "low",
        "yield_relative": 0.10,
        "notes": "Plant enzyme in prokaryote; lacks ER, glycosylation; full optimization cannot compensate for missing infrastructure",
        "reference": "Hwang et al., Appl Environ Microbiol 2003; Santos et al., Metab Eng 2011",
    },
    {
        "gene": "lin28a",
        "source": "axolotl",
        "host": "human",
        "optimization": "none",
        "success": "moderate",
        "yield_relative": 0.50,
        "notes": "Axolotl regeneration factor; within-animal kingdom transfer to human cells; Lin28 is conserved in vertebrates",
        "reference": "Shyh-Chang & Daley, Cell Stem Cell 2013; Rodrigo Albors et al., eLife 2015",
    },
    {
        "gene": "Pax7",
        "source": "axolotl",
        "host": "human",
        "optimization": "none",
        "success": "moderate",
        "yield_relative": 0.55,
        "notes": "Satellite cell marker / regeneration TF; highly conserved among vertebrates; expresses without optimization",
        "reference": "Seale et al., Cell 2000; Fei et al., Stem Cell Reports 2017",
    },
    {
        "gene": "xylanase_xynA",
        "source": "komagataeibacter",  # proxy for thermophilic Bacillus
        "host": "e_coli",
        "optimization": "none",
        "success": "high",
        "yield_relative": 0.70,
        "notes": "Prokaryote-to-prokaryote; similar codon bias and promoter logic; minimal friction",
        "reference": "Béguin & Aubert, FEMS Microbiol Rev 1994; Kulkarni et al., RSC Adv 2017",
    },
    {
        "gene": "luciferase",
        "source": "acropora",       # proxy for Photinus pyralis (firefly, animal)
        "host": "arabidopsis",
        "optimization": "partial",
        "success": "moderate",
        "yield_relative": 0.25,
        "notes": "Animal gene in plant; reporter construct; requires optimization of animal-biased codons for plant expression",
        "reference": "Millar et al., Plant Cell 1992; Ow et al., Science 1986",
    },
]


# ---------------------------------------------------------------------------
# Organism metadata
# ---------------------------------------------------------------------------

@dataclass
class OrganismProfile:
    """Economic profile of an organism in the trade network."""
    name: str
    kingdom: str            # "prokaryote", "eukaryote_fungal", "eukaryote_plant", "eukaryote_animal"
    capabilities: list[str] = field(default_factory=list)  # what this organism "exports"
    has_rscu: bool = False


def get_all_organisms() -> dict[str, OrganismProfile]:
    """Build the full organism roster with capabilities and kingdom classification."""

    organisms = {
        "komagataeibacter": OrganismProfile(
            "komagataeibacter", "prokaryote",
            capabilities=["cellulose"],
        ),
        "e_coli": OrganismProfile(
            "e_coli", "prokaryote",
            capabilities=["model_organism", "metabolic_engineering"],
        ),
        "yeast": OrganismProfile(
            "yeast", "eukaryote_fungal",
            capabilities=["nutrient_uptake", "fermentation"],
        ),
        "ganoderma": OrganismProfile(
            "ganoderma", "eukaryote_fungal",
            capabilities=["structural", "biomaterials"],
        ),
        "arabidopsis": OrganismProfile(
            "arabidopsis", "eukaryote_plant",
            capabilities=["growth", "water_transport", "thermal_regulation"],
        ),
        "human": OrganismProfile(
            "human", "eukaryote_animal",
            capabilities=["tensile_strength", "self_repair"],
        ),
        "acropora": OrganismProfile(
            "acropora", "eukaryote_animal",
            capabilities=["biomineralization"],
        ),
        "axolotl": OrganismProfile(
            "axolotl", "eukaryote_animal",
            capabilities=["self_repair", "regeneration"],
        ),
    }

    # Mark which organisms have RSCU data
    all_rscu = {**REFERENCE_RSCU, **EXTENDED_RSCU}
    for name, org in organisms.items():
        org.has_rscu = name in all_rscu

    return organisms


# ---------------------------------------------------------------------------
# Trade cost calculation
# ---------------------------------------------------------------------------

def codon_distance(org_a: str, org_b: str) -> float:
    """
    Euclidean distance between RSCU vectors of two organisms.
    Higher = more different codon dialects = higher trade friction.

    This is the biological equivalent of linguistic trade friction:
    the more different the languages, the harder the trade.
    """
    all_rscu = {**REFERENCE_RSCU, **EXTENDED_RSCU}
    rscu_a = all_rscu.get(org_a)
    rscu_b = all_rscu.get(org_b)

    if not rscu_a or not rscu_b:
        return float("inf")

    # Get common codons
    codons = sorted(set(rscu_a.keys()) & set(rscu_b.keys()))
    if not codons:
        return float("inf")

    vec_a = np.array([rscu_a[c] for c in codons])
    vec_b = np.array([rscu_b[c] for c in codons])

    return float(np.linalg.norm(vec_a - vec_b))


def regulatory_barrier(org_a: str, org_b: str) -> float:
    """
    Regulatory trade barrier: cost of translating between legal frameworks.

    Cross-kingdom (prokaryote ↔ eukaryote): 1.0 (full regulatory replacement needed)
    Same kingdom, different class: 0.3
    Same class: 0.0
    """
    kingdoms = {
        "komagataeibacter": "prokaryote",
        "e_coli": "prokaryote",
        "yeast": "eukaryote_fungal",
        "ganoderma": "eukaryote_fungal",
        "arabidopsis": "eukaryote_plant",
        "human": "eukaryote_animal",
        "acropora": "eukaryote_animal",
        "axolotl": "eukaryote_animal",
    }

    ka = kingdoms.get(org_a, "unknown")
    kb = kingdoms.get(org_b, "unknown")

    if ka == kb:
        return 0.0

    # Cross kingdom boundary (prokaryote ↔ eukaryote)
    a_prok = ka == "prokaryote"
    b_prok = kb == "prokaryote"
    if a_prok != b_prok:
        return 1.0

    # Same domain but different class (e.g., fungal vs plant vs animal)
    return 0.3


def trade_cost(
    org_a: str,
    org_b: str,
    w_codon: float = 0.5,
    w_regulatory: float = 0.35,
    w_baseline: float = 0.15,
) -> float:
    """
    Total trade cost between two organisms.

    Weighted combination of:
        - Codon distance (linguistic friction)
        - Regulatory barrier (legal/institutional friction)
        - Baseline cost (inherent complexity of horizontal gene transfer)
    """
    cd = codon_distance(org_a, org_b)
    rb = regulatory_barrier(org_a, org_b)

    # Normalize codon distance to 0-1 range (typical range is 0-15)
    cd_norm = min(cd / 15.0, 1.0)

    return w_codon * cd_norm + w_regulatory * rb + w_baseline


# ---------------------------------------------------------------------------
# Trade network construction
# ---------------------------------------------------------------------------

def build_trade_network() -> nx.Graph:
    """
    Build the cross-species trade network.

    Nodes = organisms
    Edge weight = trade ease (1 / trade_cost) — higher = easier trade
    Node attributes: kingdom, capabilities
    Edge attributes: trade_cost, codon_distance, regulatory_barrier
    """
    organisms = get_all_organisms()
    G = nx.Graph()

    # Add nodes
    for name, org in organisms.items():
        if not org.has_rscu:
            continue
        G.add_node(
            name,
            kingdom=org.kingdom,
            capabilities=org.capabilities,
            n_capabilities=len(org.capabilities),
        )

    # Add edges
    nodes = list(G.nodes())
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            a, b = nodes[i], nodes[j]
            tc = trade_cost(a, b)
            cd = codon_distance(a, b)
            rb = regulatory_barrier(a, b)

            if tc < float("inf"):
                G.add_edge(
                    a, b,
                    trade_cost=tc,
                    trade_ease=1.0 / max(tc, 0.01),
                    codon_distance=cd,
                    regulatory_barrier=rb,
                )

    return G


def compute_trade_matrix() -> tuple[list[str], np.ndarray]:
    """
    Compute the full trade cost matrix across all organisms.
    Returns (organism_names, cost_matrix).
    """
    organisms = get_all_organisms()
    names = [n for n, o in organisms.items() if o.has_rscu]
    n = len(names)
    matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i, j] = 0.0
            else:
                matrix[i, j] = trade_cost(names[i], names[j])

    return names, matrix


def comparative_advantage_table() -> dict[str, list[str]]:
    """
    Map each organism's comparative advantage — what it uniquely exports.

    This is Ricardo's comparative advantage at the molecular level:
    each organism has evolved capabilities that others lack.
    """
    organisms = get_all_organisms()
    return {name: org.capabilities for name, org in organisms.items()}


# ---------------------------------------------------------------------------
# Visualization
# ---------------------------------------------------------------------------

def plot_trade_network(save: bool = True) -> plt.Figure:
    """
    Generate a 3-panel trade network figure.

    Panel 1: Trade network graph
    Panel 2: Trade cost heatmap
    Panel 3: Comparative advantage table
    """
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    fig = plt.figure(figsize=(18, 6), facecolor=BACKGROUND)
    gs = gridspec.GridSpec(1, 3, wspace=0.3)

    G = build_trade_network()
    names, cost_matrix = compute_trade_matrix()

    # Kingdom colors
    kingdom_colors = {
        "prokaryote": RED,
        "eukaryote_fungal": SPIRAL_GREEN,
        "eukaryote_plant": GOLD,
        "eukaryote_animal": BLUE,
    }

    # --- Panel 1: Trade Network ---
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor(PANEL_BG)

    pos = nx.spring_layout(G, seed=42, k=3, weight="trade_ease")
    node_colors = [kingdom_colors.get(G.nodes[n]["kingdom"], TEXT_DIM) for n in G.nodes()]
    node_sizes = [400 + 200 * G.nodes[n].get("n_capabilities", 1) for n in G.nodes()]

    edge_weights = [G[u][v]["trade_ease"] for u, v in G.edges()]
    max_ease = max(edge_weights) if edge_weights else 1
    edge_widths = [1 + 4 * (w / max_ease) for w in edge_weights]

    nx.draw_networkx_edges(G, pos, ax=ax1, width=edge_widths, edge_color=SPIRAL_LIGHT, alpha=0.4)
    nx.draw_networkx_nodes(G, pos, ax=ax1, node_size=node_sizes, node_color=node_colors, edgecolors=TEXT_DIM)
    nx.draw_networkx_labels(G, pos, ax=ax1, font_size=7, font_color=TEXT_MAIN)

    # Legend
    for kingdom, color in kingdom_colors.items():
        ax1.scatter([], [], c=color, s=80, label=kingdom.replace("eukaryote_", ""))
    ax1.legend(fontsize=7, facecolor=PANEL_BG, edgecolor=TEXT_DIM, labelcolor=TEXT_MAIN, loc="lower left")

    ax1.set_title("Cross-Species Trade Network", color=TEXT_MAIN, fontsize=13, fontweight="bold")
    ax1.axis("off")

    # --- Panel 2: Trade Cost Heatmap ---
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor(PANEL_BG)

    im = ax2.imshow(cost_matrix, cmap="YlOrRd", aspect="auto")
    ax2.set_xticks(range(len(names)))
    ax2.set_yticks(range(len(names)))
    ax2.set_xticklabels(names, rotation=45, ha="right", fontsize=7, color=TEXT_MAIN)
    ax2.set_yticklabels(names, fontsize=7, color=TEXT_MAIN)

    # Annotate cells
    for i in range(len(names)):
        for j in range(len(names)):
            val = cost_matrix[i, j]
            color = TEXT_MAIN if val > 0.5 else BACKGROUND
            ax2.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=6, color=color)

    cbar = fig.colorbar(im, ax=ax2, shrink=0.8)
    cbar.ax.tick_params(colors=TEXT_DIM)
    cbar.set_label("Trade Cost", color=TEXT_MAIN, fontsize=10)

    ax2.set_title("Trade Barriers Heatmap", color=TEXT_MAIN, fontsize=13, fontweight="bold")

    # --- Panel 3: Comparative Advantage ---
    ax3 = fig.add_subplot(gs[2])
    ax3.set_facecolor(PANEL_BG)
    ax3.axis("off")

    advantages = comparative_advantage_table()
    y = 0.95
    ax3.text(0.05, y, "Organism", color=GOLD, fontsize=10, fontweight="bold",
             transform=ax3.transAxes)
    ax3.text(0.45, y, "Exports (Comparative Advantage)", color=GOLD, fontsize=10,
             fontweight="bold", transform=ax3.transAxes)
    y -= 0.05
    ax3.plot([0.02, 0.98], [y, y], color=TEXT_DIM, linewidth=0.5,
             transform=ax3.transAxes)

    for org_name, caps in advantages.items():
        y -= 0.08
        if y < 0:
            break
        kingdom = get_all_organisms()[org_name].kingdom
        color = kingdom_colors.get(kingdom, TEXT_MAIN)
        ax3.text(0.05, y, org_name, color=color, fontsize=8, transform=ax3.transAxes)
        ax3.text(0.45, y, ", ".join(caps), color=TEXT_MAIN, fontsize=8,
                 transform=ax3.transAxes)

    ax3.set_title("Comparative Advantage", color=TEXT_MAIN, fontsize=13, fontweight="bold")

    fig.suptitle(
        "Layer 3: The Tree of Life Is a Trade Network",
        color=GOLD, fontsize=15, fontweight="bold", y=1.02,
    )

    plt.tight_layout()

    if save:
        out = FIGURES_DIR / "layer3_trade_network.png"
        fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BACKGROUND)
        print(f"[trade] Saved figure to {out}")

    return fig


# ---------------------------------------------------------------------------
# Voluntary Exchange Report — Rothbardian Analysis Dataclass
# ---------------------------------------------------------------------------

SUCCESS_MAP = {"high": 3, "moderate": 2, "low": 1, "failed": 0}
OPTIMIZATION_MAP = {"none": 0, "partial": 1, "full": 2}


@dataclass
class VoluntaryExchangeReport:
    """
    The Rothbardian verdict on heterologous gene expression.

    Every field answers the same question Rothbard asked of international
    trade: does voluntary exchange (natural compatibility) outperform
    coerced exchange (forced gene transfer with heavy optimization)?
    """
    tier_success: dict[str, float]       # mean success score per tier
    tier_counts: dict[str, int]          # number of transfers per tier
    cost_success_correlation: float      # Spearman rho: trade_cost vs success
    optimization_vs_cost: list[tuple]    # (trade_cost, optimization_level, success)
    information_destruction: list[tuple] # (gene, source, host, codon_distance, optimization, success)
    voluntary_vs_forced: list[dict]      # same-gene comparisons across hosts

    def summary(self) -> str:
        """Print the Rothbardian verdict."""
        lines = []
        lines.append("=" * 64)
        lines.append("VOLUNTARY EXCHANGE REPORT — Rothbard Applied to Synthetic Biology")
        lines.append("=" * 64)
        lines.append("")
        lines.append("Core thesis: voluntary exchange (natural compatibility) outperforms")
        lines.append("coerced exchange (forced gene transfer with heavy optimization).")
        lines.append("The planner who rewrites codons destroys local knowledge.")
        lines.append("")

        # Tier results
        lines.append("SUCCESS BY COMPATIBILITY TIER:")
        for tier in ["Free trade", "Moderate friction", "High barrier"]:
            score = self.tier_success.get(tier, 0.0)
            count = self.tier_counts.get(tier, 0)
            label = {3: "high", 2: "moderate", 1: "low", 0: "failed"}.get(
                round(score), f"{score:.2f}"
            )
            lines.append(f"  {tier:>20s}: avg score = {score:.2f} ({label}), n = {count}")

        lines.append("")
        lines.append(f"SPEARMAN CORRELATION (trade_cost vs success): rho = {self.cost_success_correlation:.3f}")
        if self.cost_success_correlation < -0.3:
            lines.append("  → Rothbard confirmed: higher trade cost predicts lower success.")
        elif self.cost_success_correlation < 0:
            lines.append("  → Weak negative trend: compatible with the Rothbard prediction.")
        else:
            lines.append("  → Surprising: no negative correlation. Data may be confounded by optimization.")

        # Voluntary vs forced
        lines.append("")
        lines.append("VOLUNTARY vs FORCED EXCHANGE (same gene, different hosts):")
        for pair in self.voluntary_vs_forced:
            lines.append(f"  Gene: {pair['gene']}")
            lines.append(f"    Compatible host ({pair['compatible_host']}): "
                         f"cost={pair['compatible_cost']:.3f}, "
                         f"opt={pair['compatible_optimization']}, "
                         f"success={pair['compatible_success']}")
            lines.append(f"    Incompatible host ({pair['incompatible_host']}): "
                         f"cost={pair['incompatible_cost']:.3f}, "
                         f"opt={pair['incompatible_optimization']}, "
                         f"success={pair['incompatible_success']}")
            lines.append("")

        # Information destruction
        lines.append("INFORMATION DESTRUCTION (codon distance as proxy):")
        lines.append(f"  {'Gene':<22s} {'Source→Host':<28s} {'Codon Dist':>10s} {'Opt':>6s} {'Success':>8s}")
        lines.append("  " + "-" * 76)
        for gene, source, host, cd, opt, succ in self.information_destruction:
            arrow = f"{source}→{host}"
            lines.append(f"  {gene:<22s} {arrow:<28s} {cd:>10.2f} {opt:>6s} {succ:>8s}")

        lines.append("")
        lines.append("The more the planner must rewrite, the more local knowledge is destroyed.")
        lines.append("Biology is not a system to be centrally planned — it is a spontaneous order.")
        lines.append("")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Voluntary Exchange Analysis
# ---------------------------------------------------------------------------

def analyze_voluntary_exchange() -> VoluntaryExchangeReport:
    """
    Rothbardian analysis of heterologous gene expression.

    The central question: does natural compatibility (voluntary exchange)
    predict success better than engineering effort (coerced exchange)?

    Every act of centralized intervention — codon optimization, synthetic
    promoter replacement, regulatory overhaul — destroys local knowledge
    embedded in the sequence.
    """

    # --- Compute trade cost for each entry ---
    entries_with_cost = []
    for entry in HETEROLOGOUS_EXPRESSION_DB:
        tc = trade_cost(entry["source"], entry["host"])
        cd = codon_distance(entry["source"], entry["host"])
        entries_with_cost.append({**entry, "trade_cost": tc, "codon_dist": cd})

    # --- (a) Correlation between trade cost and success ---
    costs = [e["trade_cost"] for e in entries_with_cost if e["trade_cost"] < float("inf")]
    successes = [SUCCESS_MAP[e["success"]] for e in entries_with_cost if e["trade_cost"] < float("inf")]

    if len(costs) >= 3:
        rho, _ = stats.spearmanr(costs, successes)
    else:
        rho = float("nan")

    # --- (b) Success rate by compatibility tier ---
    tiers = {"Free trade": [], "Moderate friction": [], "High barrier": []}
    for e in entries_with_cost:
        tc = e["trade_cost"]
        if tc == float("inf"):
            continue
        if tc < 0.3:
            tiers["Free trade"].append(SUCCESS_MAP[e["success"]])
        elif tc < 0.55:
            tiers["Moderate friction"].append(SUCCESS_MAP[e["success"]])
        else:
            tiers["High barrier"].append(SUCCESS_MAP[e["success"]])

    tier_success = {k: (np.mean(v) if v else 0.0) for k, v in tiers.items()}
    tier_counts = {k: len(v) for k, v in tiers.items()}

    # --- (c) Information destruction metric ---
    information_destruction = []
    for e in entries_with_cost:
        cd = e["codon_dist"]
        if cd == float("inf"):
            cd = 15.0  # max proxy
        information_destruction.append((
            e["gene"], e["source"], e["host"],
            cd, e["optimization"], e["success"],
        ))
    # Sort by codon distance descending
    information_destruction.sort(key=lambda x: x[3], reverse=True)

    # --- (d) Voluntary vs forced contrast ---
    # Group by gene, find pairs with different hosts
    from collections import defaultdict
    gene_groups = defaultdict(list)
    for e in entries_with_cost:
        gene_groups[e["gene"]].append(e)

    voluntary_vs_forced = []
    for gene, group in gene_groups.items():
        if len(group) < 2:
            continue
        # Sort by trade cost
        group_sorted = sorted(group, key=lambda x: x["trade_cost"])
        compatible = group_sorted[0]
        incompatible = group_sorted[-1]
        if compatible["host"] == incompatible["host"] and compatible["optimization"] == incompatible["optimization"]:
            continue  # same host + same opt = not a useful comparison
        voluntary_vs_forced.append({
            "gene": gene,
            "compatible_host": compatible["host"],
            "compatible_cost": compatible["trade_cost"],
            "compatible_optimization": compatible["optimization"],
            "compatible_success": compatible["success"],
            "compatible_yield": compatible["yield_relative"],
            "incompatible_host": incompatible["host"],
            "incompatible_cost": incompatible["trade_cost"],
            "incompatible_optimization": incompatible["optimization"],
            "incompatible_success": incompatible["success"],
            "incompatible_yield": incompatible["yield_relative"],
        })

    # --- Build optimization_vs_cost ---
    optimization_vs_cost = [
        (e["trade_cost"], OPTIMIZATION_MAP[e["optimization"]], SUCCESS_MAP[e["success"]])
        for e in entries_with_cost if e["trade_cost"] < float("inf")
    ]

    return VoluntaryExchangeReport(
        tier_success=tier_success,
        tier_counts=tier_counts,
        cost_success_correlation=rho,
        optimization_vs_cost=optimization_vs_cost,
        information_destruction=information_destruction,
        voluntary_vs_forced=voluntary_vs_forced,
    )


# ---------------------------------------------------------------------------
# Voluntary Exchange Visualization
# ---------------------------------------------------------------------------

def plot_voluntary_exchange(report: VoluntaryExchangeReport, save: bool = True) -> plt.Figure:
    """
    Three-panel figure: Rothbard's prediction applied to synthetic biology.

    Panel 1: Trade Cost vs Success — the raw Rothbardian signal
    Panel 2: Success by Compatibility Tier — the planner cannot substitute
    Panel 3: Information Destruction — more intervention, worse results
    """
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    fig = plt.figure(figsize=(20, 7), facecolor=BACKGROUND)
    gs = gridspec.GridSpec(1, 3, wspace=0.32)

    opt_colors = {0: SPIRAL_GREEN, 1: GOLD, 2: RED}
    opt_labels = {0: "None", 1: "Partial", 2: "Full"}

    # --- Panel 1: Trade Cost vs Success ---
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor(PANEL_BG)

    costs = [t[0] for t in report.optimization_vs_cost]
    opt_levels = [t[1] for t in report.optimization_vs_cost]
    successes = [t[2] for t in report.optimization_vs_cost]
    colors = [opt_colors[o] for o in opt_levels]

    # Jitter success for visibility
    jitter = np.random.default_rng(42).uniform(-0.12, 0.12, len(successes))
    success_jittered = [s + j for s, j in zip(successes, jitter)]

    ax1.scatter(costs, success_jittered, c=colors, s=90, alpha=0.85,
                edgecolors=TEXT_DIM, linewidths=0.5, zorder=3)

    # Linear regression line
    if len(costs) >= 3:
        slope, intercept = np.polyfit(costs, successes, 1)
        x_line = np.linspace(min(costs), max(costs), 50)
        ax1.plot(x_line, slope * x_line + intercept, color=SPIRAL_LIGHT,
                 linewidth=2, linestyle="--", alpha=0.7, zorder=2)

    # Annotate Spearman rho
    ax1.text(0.05, 0.95, f"Spearman ρ = {report.cost_success_correlation:.3f}",
             transform=ax1.transAxes, color=GOLD, fontsize=10, fontweight="bold",
             verticalalignment="top")

    # Legend
    for opt_val, label in opt_labels.items():
        ax1.scatter([], [], c=opt_colors[opt_val], s=60, label=f"Optimization: {label}")
    ax1.legend(fontsize=7, facecolor=PANEL_BG, edgecolor=TEXT_DIM,
               labelcolor=TEXT_MAIN, loc="lower left")

    ax1.set_xlabel("Trade Cost (source → host)", color=TEXT_MAIN, fontsize=10)
    ax1.set_ylabel("Success Score (0=failed, 3=high)", color=TEXT_MAIN, fontsize=10)
    ax1.set_title("Rothbard's Prediction:\nVoluntary Exchange Outperforms Coercion",
                   color=GOLD, fontsize=11, fontweight="bold")
    ax1.set_yticks([0, 1, 2, 3])
    ax1.set_yticklabels(["failed", "low", "moderate", "high"], color=TEXT_MAIN, fontsize=8)
    ax1.tick_params(colors=TEXT_DIM)
    for spine in ax1.spines.values():
        spine.set_color(TEXT_DIM)

    # --- Panel 2: Success by Compatibility Tier (grouped bar) ---
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor(PANEL_BG)

    tier_names = ["Free trade", "Moderate friction", "High barrier"]
    tier_colors_map = {
        "Free trade": SPIRAL_GREEN,
        "Moderate friction": GOLD,
        "High barrier": RED,
    }

    # Group data by tier and optimization level
    from collections import defaultdict as _dd
    tier_opt_data = {tier: {0: [], 1: [], 2: []} for tier in tier_names}
    for tc_val, opt_val, succ_val in report.optimization_vs_cost:
        if tc_val < 0.3:
            tier = "Free trade"
        elif tc_val < 0.55:
            tier = "Moderate friction"
        else:
            tier = "High barrier"
        tier_opt_data[tier][opt_val].append(succ_val)

    x = np.arange(len(tier_names))
    bar_width = 0.22
    offsets = [-bar_width, 0, bar_width]

    for opt_val, offset in zip([0, 1, 2], offsets):
        means = []
        for tier in tier_names:
            vals = tier_opt_data[tier][opt_val]
            means.append(np.mean(vals) if vals else 0)
        bars = ax2.bar(x + offset, means, bar_width, color=opt_colors[opt_val],
                       edgecolor=TEXT_DIM, linewidth=0.5, alpha=0.85,
                       label=f"Opt: {opt_labels[opt_val]}")
        # Annotate counts
        for i, (m, tier) in enumerate(zip(means, tier_names)):
            n = len(tier_opt_data[tier][opt_val])
            if n > 0:
                ax2.text(x[i] + offset, m + 0.08, f"n={n}", ha="center",
                         color=TEXT_DIM, fontsize=7)

    ax2.set_xticks(x)
    ax2.set_xticklabels(tier_names, color=TEXT_MAIN, fontsize=9)
    ax2.set_ylabel("Mean Success Score", color=TEXT_MAIN, fontsize=10)
    ax2.set_ylim(0, 3.5)
    ax2.set_yticks([0, 1, 2, 3])
    ax2.set_yticklabels(["failed", "low", "moderate", "high"], color=TEXT_MAIN, fontsize=8)
    ax2.legend(fontsize=7, facecolor=PANEL_BG, edgecolor=TEXT_DIM, labelcolor=TEXT_MAIN)
    ax2.set_title("The Planner Cannot\nSubstitute for Compatibility",
                   color=GOLD, fontsize=11, fontweight="bold")
    ax2.tick_params(colors=TEXT_DIM)
    for spine in ax2.spines.values():
        spine.set_color(TEXT_DIM)

    # --- Panel 3: Information Destruction ---
    ax3 = fig.add_subplot(gs[2])
    ax3.set_facecolor(PANEL_BG)

    codon_dists = [t[3] for t in report.information_destruction]
    succ_scores = [SUCCESS_MAP[t[5]] for t in report.information_destruction]
    opt_applied = [t[4] for t in report.information_destruction]
    id_colors = [RED if o == "full" else (GOLD if o == "partial" else SPIRAL_GREEN)
                 for o in opt_applied]

    # Jitter for visibility
    jitter2 = np.random.default_rng(99).uniform(-0.12, 0.12, len(succ_scores))
    succ_jittered2 = [s + j for s, j in zip(succ_scores, jitter2)]

    ax3.scatter(codon_dists, succ_jittered2, c=id_colors, s=90, alpha=0.85,
                edgecolors=TEXT_DIM, linewidths=0.5, zorder=3)

    # Regression line
    finite_mask = [d < float("inf") for d in codon_dists]
    if sum(finite_mask) >= 3:
        cd_finite = [d for d, m in zip(codon_dists, finite_mask) if m]
        sc_finite = [s for s, m in zip(succ_scores, finite_mask) if m]
        slope2, intercept2 = np.polyfit(cd_finite, sc_finite, 1)
        x_line2 = np.linspace(min(cd_finite), max(cd_finite), 50)
        ax3.plot(x_line2, slope2 * x_line2 + intercept2, color=SPIRAL_LIGHT,
                 linewidth=2, linestyle="--", alpha=0.7, zorder=2)

    # Legend
    ax3.scatter([], [], c=SPIRAL_GREEN, s=60, label="No optimization")
    ax3.scatter([], [], c=GOLD, s=60, label="Partial optimization")
    ax3.scatter([], [], c=RED, s=60, label="Full optimization")
    ax3.legend(fontsize=7, facecolor=PANEL_BG, edgecolor=TEXT_DIM,
               labelcolor=TEXT_MAIN, loc="upper right")

    ax3.set_xlabel("Codon Distance (information to destroy)", color=TEXT_MAIN, fontsize=10)
    ax3.set_ylabel("Success Score", color=TEXT_MAIN, fontsize=10)
    ax3.set_title("Codon Optimization as Central Planning:\nMore Intervention, Worse Results",
                   color=GOLD, fontsize=11, fontweight="bold")
    ax3.set_yticks([0, 1, 2, 3])
    ax3.set_yticklabels(["failed", "low", "moderate", "high"], color=TEXT_MAIN, fontsize=8)
    ax3.tick_params(colors=TEXT_DIM)
    for spine in ax3.spines.values():
        spine.set_color(TEXT_DIM)

    fig.suptitle(
        "Layer 3: Rothbardian Voluntary Exchange Applied to Gene Transfer",
        color=GOLD, fontsize=14, fontweight="bold", y=1.02,
    )

    plt.tight_layout()

    if save:
        out = FIGURES_DIR / "layer3_voluntary_exchange.png"
        fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BACKGROUND)
        print(f"[trade] Saved voluntary exchange figure to {out}")

    return fig


# ---------------------------------------------------------------------------
# Community Detection — Spontaneous Trade Blocs (Mengerian Spontaneous Order)
# ---------------------------------------------------------------------------

def detect_trade_blocs(G: nx.Graph) -> dict[int, list[str]]:
    """
    Detect spontaneous trade blocs via community detection.

    These are Menger's spontaneous order applied to the tree of life:
    no treaty, no central planner, just compatibility driving organisms
    into natural trading communities.

    Uses Louvain community detection on trade_ease weights.
    Falls back to greedy modularity if Louvain is unavailable.
    """
    try:
        communities = nx.community.louvain_communities(G, weight="trade_ease", seed=42)
    except AttributeError:
        # Fallback for older NetworkX versions
        communities = nx.community.greedy_modularity_communities(G, weight="trade_ease")

    result = {}
    for i, comm in enumerate(communities):
        result[i] = sorted(comm)

    return result


def plot_trade_blocs(
    G: nx.Graph,
    communities: dict[int, list[str]],
    save: bool = True,
) -> plt.Figure:
    """
    Draw the trade network with nodes colored by community membership.

    Title: "Spontaneous Trade Blocs: Self-Organization Without Treaty"

    Each community gets its own color and a convex hull boundary.
    """
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(1, 1, figsize=(10, 8), facecolor=BACKGROUND)
    ax.set_facecolor(PANEL_BG)

    pos = nx.spring_layout(G, seed=42, k=3, weight="trade_ease")

    # Community color palette
    comm_colors_list = [SPIRAL_GREEN, RED, GOLD, BLUE, SPIRAL_MID, SPIRAL_LIGHT]
    comm_labels = {}

    for comm_id, members in communities.items():
        color = comm_colors_list[comm_id % len(comm_colors_list)]
        comm_labels[comm_id] = f"Bloc {comm_id}: {', '.join(members)}"

        # Draw convex hull if 3+ members
        if len(members) >= 3:
            from scipy.spatial import ConvexHull
            points = np.array([pos[m] for m in members if m in pos])
            if len(points) >= 3:
                try:
                    hull = ConvexHull(points)
                    hull_points = points[hull.vertices]
                    # Close the polygon
                    hull_points = np.vstack([hull_points, hull_points[0]])
                    ax.fill(hull_points[:, 0], hull_points[:, 1],
                            color=color, alpha=0.1, zorder=1)
                    ax.plot(hull_points[:, 0], hull_points[:, 1],
                            color=color, linewidth=2, alpha=0.4, zorder=1)
                except Exception:
                    pass  # ConvexHull can fail with collinear points

        # Draw nodes
        node_list = [m for m in members if m in G.nodes()]
        if node_list:
            node_sizes = [500 + 200 * G.nodes[n].get("n_capabilities", 1) for n in node_list]
            nx.draw_networkx_nodes(G, pos, nodelist=node_list, ax=ax,
                                   node_size=node_sizes, node_color=color,
                                   edgecolors=TEXT_DIM, linewidths=1.5, alpha=0.9,
                                   label=comm_labels[comm_id])

    # Draw edges
    edge_weights = [G[u][v]["trade_ease"] for u, v in G.edges()]
    max_ease = max(edge_weights) if edge_weights else 1
    edge_widths = [1 + 3 * (w / max_ease) for w in edge_weights]
    nx.draw_networkx_edges(G, pos, ax=ax, width=edge_widths,
                           edge_color=SPIRAL_LIGHT, alpha=0.3)

    # Labels
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=8, font_color=TEXT_MAIN,
                            font_weight="bold")

    ax.legend(fontsize=8, facecolor=PANEL_BG, edgecolor=TEXT_DIM,
              labelcolor=TEXT_MAIN, loc="lower left")
    ax.set_title("Spontaneous Trade Blocs: Self-Organization Without Treaty",
                 color=GOLD, fontsize=14, fontweight="bold")
    ax.axis("off")

    plt.tight_layout()

    if save:
        out = FIGURES_DIR / "layer3_trade_blocs.png"
        fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BACKGROUND)
        print(f"[trade] Saved trade blocs figure to {out}")

    return fig


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("Layer 3: Cross-Species Trade Network")
    print("=" * 60)
    print()

    # Build trade network
    G = build_trade_network()
    print(f"Trade network: {G.number_of_nodes()} organisms, {G.number_of_edges()} trade links")

    # Print trade cost matrix
    names, matrix = compute_trade_matrix()
    print(f"\nTrade Cost Matrix ({len(names)} organisms):")
    print(f"{'':>18}", end="")
    for n in names:
        print(f"{n:>14}", end="")
    print()
    for i, n in enumerate(names):
        print(f"{n:>18}", end="")
        for j in range(len(names)):
            print(f"{matrix[i, j]:>14.3f}", end="")
        print()

    # Comparative advantage
    print("\nComparative Advantage:")
    for org, caps in comparative_advantage_table().items():
        print(f"  {org}: {', '.join(caps)}")

    # Find free trade zones (lowest cost pairs)
    print("\nFree Trade Zones (lowest trade cost pairs):")
    pairs = []
    for u, v, data in G.edges(data=True):
        pairs.append((u, v, data["trade_cost"]))
    pairs.sort(key=lambda x: x[2])
    for u, v, tc in pairs[:5]:
        print(f"  {u} ↔ {v}: cost={tc:.3f}")

    # Find highest trade barriers
    print("\nHighest Trade Barriers:")
    for u, v, tc in pairs[-3:]:
        print(f"  {u} ↔ {v}: cost={tc:.3f}")

    # Generate trade network figure
    print("\nGenerating trade network figure...")
    plot_trade_network()

    # --- Voluntary Exchange Analysis (Rothbardian) ---
    print("\n")
    report = analyze_voluntary_exchange()
    print(report.summary())

    # Generate voluntary exchange figure
    print("Generating voluntary exchange figure...")
    plot_voluntary_exchange(report)

    # --- Community Detection (Mengerian Spontaneous Order) ---
    print("\nDetecting spontaneous trade blocs...")
    communities = detect_trade_blocs(G)
    print(f"Found {len(communities)} trade blocs:")
    for comm_id, members in communities.items():
        print(f"  Bloc {comm_id}: {', '.join(members)}")

    # Generate trade blocs figure
    print("\nGenerating trade blocs figure...")
    plot_trade_blocs(G, communities)

    print("\nDone.")

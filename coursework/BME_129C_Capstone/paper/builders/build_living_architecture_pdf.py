"""
Build The Living Architecture as PDF with integrated figures.
Converts Markdown -> HTML with academic styling -> PDF via WeasyPrint.

Includes all figures from the capstone_summary_visual: individual panel
figures (L1, L2, L3, price system, FBA) and viral network figures are
injected into the appropriate sections alongside the existing annotated
composite figures.

Usage: python paper/builders/build_living_architecture_pdf.py
"""

import re
import base64
from pathlib import Path
import markdown
from weasyprint import HTML

PAPER_DIR = Path(__file__).resolve().parent.parent
WRITING_DIR = PAPER_DIR / "writing"
FIGURES_DIR = PAPER_DIR / "figures"
INDIVIDUAL_DIR = FIGURES_DIR / "individual"
MD_FILE = WRITING_DIR / "the_living_architecture.md"
OUT_PDF = PAPER_DIR / "deliverables" / "the_living_architecture.pdf"


# Additional figures to inject, keyed by the anchor figure reference they follow.
# Each entry: (anchor_pattern, list of (figure_path, caption, relevance))
EXTRA_FIGURES = [
    # Layer 1 — after Figure 1 (topology annotated)
    ("![Figure 1.", [
        ("individual/L1_degree_distribution.png",
         "Figure 1a. Degree distribution of the E. coli gene regulatory network.",
         "The degree distribution follows a power law (α 2.0–2.5), matching the "
         "Barabasi-Albert model for decentralized network growth. Many nodes have "
         "few connections; a few hubs have many — but no single node dominates. "
         "This is the topological signature of distributed knowledge: information "
         "is held by many agents, not concentrated in one."),
        ("individual/L1_robustness_curves.png",
         "Figure 1b. Robustness under targeted node removal.",
         "Biological networks survive the loss of 37% of their most connected "
         "nodes before fragmenting. The star graph — the architecture of central "
         "planning — collapses at 1.9%. This 19:1 ratio quantifies the structural "
         "cost of centralization: concentrate knowledge in one node, and the system "
         "dies when that node is removed. Distribute it, and the system routes "
         "around any loss."),
        ("individual/L1_centrality_gini.png",
         "Figure 1c. Betweenness centrality Gini coefficient across network architectures.",
         "The star graph has a Gini of 0.998 — nearly all shortest paths run through "
         "one node. Biological networks occupy intermediate values (0.72–0.94): "
         "structured but distributed. Information flows through many channels, not "
         "one. This metric directly measures how centralized or distributed the "
         "knowledge flow is within each architecture."),
        ("individual/L1_motif_zscore.png",
         "Figure 1d. Feed-forward loop Z-scores against 1,000 randomized networks.",
         "Feed-forward loops are massively over-represented in the E. coli GRN "
         "(Z-score > 10). These are coordination motifs — fast regulatory shortcuts "
         "that propagate local information without waiting for central command. "
         "They are the recurring grammar of distributed regulation: Hayekian price "
         "signal shortcuts evolved into the network architecture itself."),
    ]),

    # Layer 2 — after Figure 4 (economy annotated)
    ("![Figure 4.", [
        ("individual/L2_gdp_over_time.png",
         "Figure 4a. GDP over time — distributed versus centralized allocation.",
         "Thirteen metabolic pathway agents share a metabolite pool with no central "
         "allocator. The centralized regime achieves higher absolute output under "
         "stable conditions — the planner can see the whole board. But this "
         "advantage exists only while conditions remain exactly as planned. The "
         "moment the environment changes, the planner's fixed allocation becomes "
         "wrong."),
        ("individual/L2_perturbation_robustness.png",
         "Figure 4b. Perturbation robustness — GDP retention under stress.",
         "Under perturbation, distributed allocation retains 71% of GDP while "
         "centralized retains 53% — an 18-point advantage for the market under "
         "stress. The distributed agents self-correct through local price signals: "
         "each detects the metabolite change in the shared pool and adjusts its "
         "production rate. The planner has no mechanism to discover the new optimum "
         "because its allocation was based on a fixed global ranking, not feedback."),
        ("individual/L2_rate_convergence.png",
         "Figure 4c. Production rate convergence across metabolic agents.",
         "Agents begin at uniform rates — they do not know what the economy needs — "
         "and discover their optimal production levels through iterative feedback. "
         "The early oscillations are price discovery. The final rates are unequal, "
         "reflecting the economy's differential demand. Nobody assigned these rates. "
         "They emerged from the competitive process itself — Kirznerian "
         "entrepreneurial discovery at the molecular level."),
    ]),

    # FBA — after Figure 5 (FBA annotated)
    ("![Figure 5.", [
        ("individual/L2_fba_knockout_scatter.png",
         "Figure 5a. FBA knockout predictions versus Keio experimental data.",
         "Each point is one gene. The omniscient planner — a linear program with "
         "perfect stoichiometric knowledge of 2,712 reactions — achieves 70% "
         "accuracy. The 30% failure is not random noise. It is structural: "
         "knowledge encoded in allosteric feedback, protein folding, expression "
         "timing, and chaperone requirements exists only in the local state of "
         "each molecular agent and cannot be captured in a stoichiometric matrix."),
        ("individual/L2_fba_confusion_matrix.png",
         "Figure 5b. FBA confusion matrix — the two types of planning failure.",
         "False positives (planner says essential, cell survives) represent "
         "Kirznerian entrepreneurial adaptation — the cell discovers alternative "
         "routes the planner did not anticipate. False negatives (planner says "
         "viable, cell dies) represent Hayekian local knowledge the LP cannot "
         "encode — regulatory dependencies invisible to stoichiometry. Both "
         "failure modes confirm that the knowledge problem is structural, not "
         "a matter of insufficient data."),
        ("individual/L2_fba_shadow_prices.png",
         "Figure 5c. Shadow prices across metabolic conditions.",
         "FBA dual variables report the marginal growth value of every metabolite "
         "under different conditions. NADH is cheap on glucose, expensive on "
         "acetate. Oxygen is free aerobically, most valuable anaerobically. The "
         "same molecule has different marginal value depending on context — "
         "Menger's subjective value computed from real metabolic data. The LP "
         "must compute these prices to solve its optimization, proving that price "
         "information is essential even for the central planner."),
    ]),

    # FBA perturbation — after Figure 6
    ("![Figure 6.", [
        ("individual/L2_fba_pert_carbon.png",
         "Figure 6a. FBA perturbation: glucose-to-acetate carbon source switch.",
         "FBA instantly re-optimizes to the new global optimum. Real E. coli shows "
         "diauxic lag — a measurable delay while the cell's distributed regulatory "
         "network discovers the new environment through CRP-cAMP signaling and "
         "catabolite repression. The planner assumes instant, costless knowledge "
         "transfer. Biology pays the real cost of discovery — but can discover "
         "anything, not just what the planner anticipated."),
        ("individual/L2_fba_pert_nitrogen.png",
         "Figure 6b. FBA perturbation: nitrogen limitation.",
         "Under nitrogen starvation, FBA predicts the new optimum instantly. Real "
         "E. coli upregulates high-affinity ammonium transporters via the NtrBC "
         "two-component system — entrepreneurial alertness at the molecular level. "
         "The cell senses the local scarcity signal and responds by activating "
         "alternative acquisition strategies the LP did not plan for."),
        ("individual/L2_fba_pert_anaerobic.png",
         "Figure 6c. FBA perturbation: aerobic-to-anaerobic shift.",
         "FBA re-solves the optimization with oxygen removed. Real E. coli activates "
         "the ArcAB and FNR regulatory cascades through local oxygen sensing — a "
         "distributed response to environmental change that the stoichiometric model "
         "cannot simulate. The regulatory cost of discovery is real but enables "
         "adaptation to conditions the planner never modeled."),
    ]),

    # Layer 3 — after Figure 7 (trade network annotated)
    ("![Figure 7.", [
        ("individual/L3_trade_network_graph.png",
         "Figure 7a. Cross-species gene exchange network.",
         "Eight organisms across four kingdoms connected by edges weighted by trade "
         "ease (inverse cost). Each organism occupies a unique position in the "
         "network, specializing in capabilities others lack — coral exports "
         "biomineralization, spider exports silk, bacteria export cellulose. This "
         "is Ricardian comparative advantage at the molecular level. No organism "
         "does everything; each contributes what it does best."),
        ("individual/L3_trade_cost_heatmap.png",
         "Figure 7b. Trade cost heatmap — evolutionary distance as trade friction.",
         "Costs scale with evolutionary distance: within-kingdom pairs (0.17–0.38) "
         "trade easily because they share regulatory machinery. Cross-kingdom pairs "
         "(0.65–0.83) face high friction from fundamental regulatory divergence "
         "(prokaryotic vs eukaryotic transcription, different codon usage, "
         "incompatible post-translational processing). This is the biological "
         "gravity model — institutional distance determines trade cost."),
        ("individual/L3_comparative_advantage_table.png",
         "Figure 7c. Comparative advantage table — each organism's exportable specialties.",
         "Every organism in the analysis has unique capabilities that no other "
         "organism possesses. This is not redundancy — it is the division of labor "
         "across the tree of life. The synthetic biologist who wants to combine "
         "these capabilities into one construct is building a small economy and "
         "must account for the trade costs between each contributor."),
    ]),

    # Price system panels — after Figure 8 (voluntary exchange)
    ("![Figure 8.", [
        ("individual/panel_a_price_tiers.png",
         "Figure 8a. The Price System of the Cell — Panel A: Three tiers of molecular prices.",
         "Living systems have a real price system operating at three levels. "
         "Intracellular metabolite ratios (ATP/ADP, NAD+/NADH, AMP/ATP) function "
         "as cost of capital — emerging from the cell's own activity, not set by "
         "any authority. Intercellular signals (cytokines, morphogens, growth "
         "factors, oxygen tension) function as market prices — carrying tissue-level "
         "information that cells read locally. mTOR integrates all prices "
         "simultaneously and makes the grow-or-conserve decision — the entrepreneur "
         "reading the full local market. Not metaphor — every ratio is quantifiable, "
         "every signal has a known receptor."),
        ("individual/panel_b_shadow_prices.png",
         "Figure 8b. The Price System of the Cell — Panel B: Menger's subjective value measured.",
         "FBA shadow prices from the iML1515 genome-scale model under four "
         "conditions. NADH is cheap on glucose, expensive on acetate. Oxygen is "
         "free aerobically, most valuable anaerobically. Ammonium is irrelevant "
         "under nitrogen sufficiency, critical under limitation. The molecule "
         "does not change — the context does. This IS Menger's subjective value "
         "theory (1871), measured in a genome-scale model. Even the omniscient "
         "planner must compute these prices to solve its optimization."),
        ("individual/panel_c_price_discovery.png",
         "Figure 8c. The Price System of the Cell — Panel C: Price discovery without a planner.",
         "Metabolite pools oscillate then converge to stable values. Early "
         "oscillation is the market discovery phase — supply and demand adjusting "
         "through local feedback. Late convergence is equilibrium found without "
         "any planner telling the system where to settle. Oversupply causes "
         "producers to slow down (price drops); scarcity causes producers to speed "
         "up (price rises). This is Hayek's price discovery happening at the "
         "molecular level — the invisible hand in a metabolite pool."),
        ("individual/panel_d_cancer_price_system.png",
         "Figure 8d. The Price System of the Cell — Panel D: Cancer breaks the price system.",
         "Using TCGA PanCancerAtlas data (10,967 samples, 32 cancer types), the "
         "most mutated genes map to price system components: TP53 (damage price / "
         "apoptosis signal), PIK3CA/PTEN/mTOR (price integrators), EGFR/ERBB2 "
         "(growth factor receptors / price readers), NF2 (spatial/contact price). "
         "The tissue-specific variation is the finding: TP53 is 96% in ovarian but "
         "1% in thyroid. PIK3CA is 52% in uterine but 3% in ovarian. Different "
         "tissues break different price components because different tissues rely "
         "on different prices. Cancer is not a gene disease — it is a price system "
         "disease. The disease is the calculation problem at the cellular level."),
    ]),

    # Viral figures — after Figure 16 (genome summary)
    ("![Figure 16.", [
        ("viral_genome_composition.png",
         "Figure 17. Human genome composition — viral DNA dwarfs protein-coding genes.",
         "Endogenous retroviruses (ERVs) constitute 8% of the human genome — more "
         "than five times the 1.5% that codes for proteins. Transposable elements "
         "of viral origin account for nearly half of all genomic sequence. These "
         "are not junk or parasitic remnants. They are the communication "
         "infrastructure of the distributed genome — regulatory elements, "
         "promoters, enhancers, and structural features co-opted from viral "
         "sequences over billions of years of integration."),
        ("viral_syncytin_conservation.png",
         "Figure 18. Syncytin — a captured viral gene essential for mammalian pregnancy.",
         "Syncytin is a retroviral envelope gene captured by the mammalian genome "
         "and placed under purifying selection. It enables placental "
         "syncytiotrophoblast fusion — the cell fusion event required for nutrient "
         "exchange between mother and fetus. Mammalian pregnancy literally depends "
         "on a virus. This is not parasitism. It is co-option — the distributed "
         "genome incorporating external information and repurposing it for a "
         "function no endogenous gene could perform."),
        ("viral_phage_network.png",
         "Figure 19. The global phage network — the first internet.",
         "10^31 bacteriophages on Earth conduct approximately 10^25 gene transfers "
         "per day through transduction. This is horizontal information transfer at "
         "a scale that dwarfs all human communication networks combined. Phages "
         "move genes between bacteria — antibiotic resistance, metabolic "
         "capabilities, toxin production — creating a distributed gene-sharing "
         "economy that predates multicellular life by billions of years."),
        ("viral_gut_virome.png",
         "Figure 20. The gut virome — distributed population control.",
         "The human gut virome is >90% bacteriophages, forming a stable resident "
         "community that regulates bacterial populations through lysis and "
         "lysogeny. This is not infection — it is distributed population control. "
         "Phages keep bacterial populations in check without any central immune "
         "authority, maintaining the ecological balance of the gut microbiome "
         "through local predator-prey dynamics."),
        ("viral_erv_regulatory.png",
         "Figure 21. ERV-derived regulatory elements — viral DNA as gene switches.",
         "Endogenous retroviral long terminal repeats (LTRs) have been co-opted "
         "as promoters, enhancers, and insulators across human tissues. Viral DNA "
         "became the regulatory infrastructure of the distributed genome — price "
         "signals repurposed from an external source. These elements control "
         "tissue-specific gene expression, proving that the genome integrates "
         "information from its environment and repurposes it for coordination."),
        ("viral_autoimmune_rise.png",
         "Figure 22. The rise of autoimmune and allergic disease — inverse correlation with infection.",
         "As infectious disease exposure has decreased over the past century, "
         "autoimmune and allergic conditions have risen dramatically. The immune "
         "system evolved as a distributed economy calibrated by continuous "
         "microbial input. Removing that input — reducing the price signals the "
         "system was designed to read — produces miscalibration. The system that "
         "evolved to process distributed information from its environment "
         "malfunctions when that information is withdrawn."),
        ("viral_communication_summary.png",
         "Figure 23. Viral communication across scales — from molecules to ecosystems.",
         "Viruses operate as communication channels at every scale of biological "
         "organization: molecular co-option (syncytin, ERV regulatory elements), "
         "cellular regulation (phage-mediated bacterial population control), "
         "organismal adaptation (horizontal gene transfer), and ecosystem-level "
         "gene flow (the global virome). They are not just pathogens. They are "
         "the postal service of the distributed network of life — moving "
         "information between nodes that cannot communicate directly."),
    ]),
]


def find_figure(src):
    """Resolve a figure path relative to the paper directory."""
    candidates = [
        FIGURES_DIR / src,
        INDIVIDUAL_DIR / src,
        FIGURES_DIR / Path(src).name,
        INDIVIDUAL_DIR / Path(src).name,
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def make_img_md(src, caption, relevance=""):
    """Create a markdown image line with caption and relevance explanation."""
    lines = f"\n![{caption}]({src})\n\n**{caption}** {relevance}\n"
    return lines


THESIS_BLOCK = """\

---

> **Living things are not machines.** There are two types of order: decentralized and centralized. Centralized order requires uniformity. Decentralized order requires ordered diversity. Life is decentralized, and life must die to become centralized — it must be reduced to parts, and in doing so it loses what makes it valuable. The diversity of life is not random difference. It is based on local knowledge of time and place that no central planner can predict. Distributed nodes can plan, but central planners cannot. The distributed knowledge is coordinated by prices — the ratio between the voluntary exchange of anything between nodes. Living order is organized by choice. State order is dictated by control.
>
> The differences are a feature, not a bug. The differences are how adaptation is possible. It is trial and error directed by distributed knowledge — just how Hayek explains the market at the human-to-human level with trade. Eugenics is the same fatal conceit: you cannot centrally plan life. If there is distributed knowledge in living things, it is in the DNA — and bioinformatics is the analysis of that genetic data. Bioinformatics is the study of distributed knowledge in living systems.
>
> This capstone provides quantitative evidence — drawn from network topology, single-cell transcriptomics, agent-based metabolic simulation, genome-scale flux balance analysis, cross-species gene transfer, and cancer genomics — that the distributed architecture of biology is not a constraint to be overcome but the fundamental reason living systems outperform every centralized alternative we can design or simulate.

---

"""

THROUGHLINE_BLOCK = """\

---

## The Throughline

Every layer answers the same question from a different angle: does biology operate like a centrally planned economy or a free market?

The network structure says market — no master node, self-regulation, feed-forward price signals. Single cells say market — specialization, voluntary exchange, subjective value, distributed robustness. Metabolic allocation says market — distributed beats centralized under perturbation, even against an omniscient planner. Cancer genomics says market — disease is the destruction of the cellular price system, not the presence of bad parts. Cross-species trade says market — voluntary exchange succeeds, forced exchange fails, trade blocs emerge spontaneously.

**Life is the original decentralized network.** The self-assembling internet. The adaptive computer that built itself, runs itself, repairs itself, and has been doing so for four billion years. We did not invent this architecture. We finally recognized it.

The question is not how to program life. It is how to join the computation — how to lead life to lead itself, and in doing so, grow something that lasts. Not by controlling it. By being part of it. Cultivate conditions, don't command outcomes. Read the price system, don't override it. Reduce trade barriers, don't force trade. Be a node, not a planner.

**That is the Living Age.** The bridge from silicon to carbon. From programming to cultivating. From central planning to distributed participation. From using life as a part of a machine to doing things with life as a living network that we join, not command.

---

"""


def inject_extra_figures(md_text):
    """Inject additional figures after their anchor figure references."""
    for anchor, figures in EXTRA_FIGURES:
        insert_lines = []
        for src, caption, relevance in figures:
            path = find_figure(src)
            if path:
                insert_lines.append(make_img_md(src, caption, relevance))

        if insert_lines and anchor in md_text:
            idx = md_text.index(anchor)
            end_of_line = md_text.index("\n", idx)
            insertion = "\n" + "".join(insert_lines)
            md_text = md_text[:end_of_line] + insertion + md_text[end_of_line:]

    return md_text


def inject_thesis_and_throughline(md_text):
    """Insert thesis block before Abstract, throughline after conclusion."""
    # Insert thesis block before "## Abstract"
    abstract_marker = "## Abstract"
    if abstract_marker in md_text:
        idx = md_text.index(abstract_marker)
        md_text = md_text[:idx] + THESIS_BLOCK + md_text[idx:]

    # Insert throughline before "## References"
    ref_marker = "## References"
    if ref_marker in md_text:
        idx = md_text.index(ref_marker)
        md_text = md_text[:idx] + THROUGHLINE_BLOCK + md_text[idx:]

    return md_text


def embed_image(match):
    """Replace markdown image references with base64-embedded images."""
    alt = match.group(1)
    src = match.group(2)

    candidates = [
        PAPER_DIR / src,
        WRITING_DIR / src,
        FIGURES_DIR / Path(src).name,
        INDIVIDUAL_DIR / Path(src).name,
    ]

    img_path = None
    for c in candidates:
        if c.exists():
            img_path = c
            break

    if img_path is None:
        return f'<p class="missing-fig">[Figure not found: {src}]</p>'

    suffix = img_path.suffix.lower()
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".svg": "image/svg+xml", ".webp": "image/webp"}.get(suffix, "image/png")

    if suffix == ".pdf":
        png_alt = img_path.with_suffix(".png")
        if png_alt.exists():
            img_path = png_alt
            mime = "image/png"
        else:
            return f'<p class="missing-fig">[PDF figure: {src} — convert to PNG]</p>'

    data = base64.b64encode(img_path.read_bytes()).decode()
    return f'<img src="data:{mime};base64,{data}" alt="{alt}" class="figure-img">'


def md_to_html(md_text: str) -> str:
    """Convert markdown to HTML, embedding images as base64."""
    md_text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', embed_image, md_text)
    extensions = ['tables', 'fenced_code', 'footnotes', 'smarty']
    return markdown.markdown(md_text, extensions=extensions)


def build():
    md_text = MD_FILE.read_text(encoding="utf-8")

    # Inject thesis statement and throughline
    md_text = inject_thesis_and_throughline(md_text)

    # Inject the additional figures from the summary visual
    md_text = inject_extra_figures(md_text)

    html_body = md_to_html(md_text)

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
@page {{
    size: letter;
    margin: 1in 1in 1in 1in;
    @bottom-center {{
        content: counter(page);
        font-family: Georgia, serif;
        font-size: 9pt;
        color: #666;
    }}
}}

body {{
    font-family: Georgia, "Times New Roman", serif;
    font-size: 11pt;
    line-height: 1.65;
    color: #1a1a1a;
    max-width: 100%;
    text-align: justify;
    hyphens: auto;
}}

h1 {{
    font-size: 18pt;
    font-weight: bold;
    text-align: center;
    margin-bottom: 6pt;
    line-height: 1.3;
    color: #0d1117;
    page-break-after: avoid;
}}

h1 + p {{
    text-align: center;
}}

h2 {{
    font-size: 14pt;
    font-weight: bold;
    margin-top: 28pt;
    margin-bottom: 10pt;
    color: #1b4332;
    border-bottom: 1px solid #2d6a4f;
    padding-bottom: 4pt;
    page-break-after: avoid;
}}

h3 {{
    font-size: 12pt;
    font-weight: bold;
    margin-top: 20pt;
    margin-bottom: 8pt;
    color: #2d6a4f;
    page-break-after: avoid;
}}

h4 {{
    font-size: 11pt;
    font-weight: bold;
    margin-top: 16pt;
    margin-bottom: 6pt;
    color: #40916c;
    page-break-after: avoid;
}}

p {{
    margin-bottom: 8pt;
    orphans: 3;
    widows: 3;
}}

blockquote {{
    margin: 16pt 30pt;
    padding: 8pt 16pt;
    border-left: 3px solid #2d6a4f;
    background: #f8f9f7;
    font-style: italic;
    color: #333;
    page-break-inside: avoid;
}}

blockquote p {{
    margin-bottom: 4pt;
}}

strong {{
    color: #1a1a1a;
}}

.figure-img {{
    display: block;
    max-width: 100%;
    margin: 16pt auto;
    page-break-inside: avoid;
}}

table {{
    border-collapse: collapse;
    width: 100%;
    margin: 14pt 0;
    font-size: 9.5pt;
    page-break-inside: avoid;
}}

th {{
    background: #1b4332;
    color: white;
    font-weight: bold;
    padding: 6pt 8pt;
    text-align: left;
    border: 1px solid #1b4332;
}}

td {{
    padding: 5pt 8pt;
    border: 1px solid #ddd;
    vertical-align: top;
}}

tr:nth-child(even) {{
    background: #f5f7f5;
}}

hr {{
    border: none;
    border-top: 1px solid #ccc;
    margin: 24pt 0;
}}

ul, ol {{
    margin: 8pt 0 8pt 24pt;
}}

li {{
    margin-bottom: 4pt;
}}

code {{
    font-family: "Courier New", monospace;
    font-size: 10pt;
    background: #f0f0f0;
    padding: 1pt 3pt;
    border-radius: 2pt;
}}

.missing-fig {{
    background: #fff3cd;
    border: 1px solid #ffc107;
    padding: 8pt;
    text-align: center;
    color: #856404;
    font-style: italic;
}}

h2 {{
    page-break-before: auto;
}}

p:has(> img), p:has(> .figure-img) {{
    page-break-inside: avoid;
    page-break-after: avoid;
}}

h1 + p > strong {{
    font-size: 12pt;
}}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

    print(f"Reading: {MD_FILE.name}")
    print("Injecting thesis statement and throughline...")
    print("Injecting additional figures from summary visual...")
    print("Generating PDF (this may take a moment for a large document)...")
    HTML(string=full_html, base_url=str(PAPER_DIR)).write_pdf(str(OUT_PDF))
    print(f"Saved: {OUT_PDF}")
    print(f"Size: {OUT_PDF.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    build()

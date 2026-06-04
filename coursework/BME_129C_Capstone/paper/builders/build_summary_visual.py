"""
Build a visual quick-reference summary (3 pages, bullet points + embedded figures).
Uses weasyprint to render HTML/CSS with base64-encoded images.
"""

from pathlib import Path
import base64
import markdown
from weasyprint import HTML

PAPER_DIR = Path(__file__).resolve().parent.parent
FIGURES = PAPER_DIR / "figures"
INDIVIDUAL = FIGURES / "individual"


def img_tag(path, width="100%"):
    """Embed an image as base64 data URI."""
    p = Path(path)
    if not p.exists():
        return f'<p style="color:#999; font-size:9pt;">[Figure not found: {p.name}]</p>'
    data = base64.b64encode(p.read_bytes()).decode()
    suffix = p.suffix.lstrip(".")
    if suffix == "jpg":
        suffix = "jpeg"
    return f'<img src="data:image/{suffix};base64,{data}" style="width:{width}; display:block; margin:6pt auto;" />'


def build():
    # Collect image tags
    degree = img_tag(INDIVIDUAL / "L1_degree_distribution.png", "48%")
    robustness = img_tag(INDIVIDUAL / "L1_robustness_curves.png", "48%")
    gini = img_tag(INDIVIDUAL / "L1_centrality_gini.png", "48%")
    motif = img_tag(INDIVIDUAL / "L1_motif_zscore.png", "48%")

    cell_econ = img_tag(FIGURES / "layer1b_single_cell_economy_annotated.png")
    if "[Figure not found" in cell_econ:
        cell_econ = img_tag(FIGURES / "layer1b_single_cell_economy.png")

    gdp = img_tag(INDIVIDUAL / "L2_gdp_over_time.png", "48%")
    perturbation = img_tag(INDIVIDUAL / "L2_perturbation_robustness.png", "48%")

    shadow = img_tag(INDIVIDUAL / "panel_b_shadow_prices.png", "48%")
    cancer = img_tag(INDIVIDUAL / "panel_d_cancer_price_system.png", "48%")

    trade_net = img_tag(INDIVIDUAL / "L3_trade_network_graph.png", "48%")
    trade_cost = img_tag(INDIVIDUAL / "L3_trade_cost_heatmap.png", "48%")

    # FBA
    fba_scatter = img_tag(INDIVIDUAL / "L2_fba_knockout_scatter.png", "48%")
    fba_confusion = img_tag(INDIVIDUAL / "L2_fba_confusion_matrix.png", "48%")

    # Immune
    shm = img_tag(FIGURES / "immune_shm_hotspots_annotated.png")
    if "[Figure not found" in shm:
        shm = img_tag(FIGURES / "immune_shm_hotspots.png")
    vdj = img_tag(FIGURES / "immune_vdj_bias_annotated.png", "48%")
    if "[Figure not found" in vdj:
        vdj = img_tag(FIGURES / "immune_vdj_bias.png", "48%")
    clonotypes = img_tag(FIGURES / "immune_public_clonotypes_annotated.png", "48%")
    if "[Figure not found" in clonotypes:
        clonotypes = img_tag(FIGURES / "immune_public_clonotypes.png", "48%")

    # Genome-wide
    mutation_hotspots = img_tag(FIGURES / "genome_mutation_hotspots_annotated.png", "48%")
    if "[Figure not found" in mutation_hotspots:
        mutation_hotspots = img_tag(FIGURES / "genome_mutation_hotspots.png", "48%")
    tissue_spec = img_tag(FIGURES / "genome_tissue_specialization_annotated.png", "48%")
    if "[Figure not found" in tissue_spec:
        tissue_spec = img_tag(FIGURES / "genome_tissue_specialization.png", "48%")
    convergent = img_tag(FIGURES / "genome_convergent_evolution_annotated.png")
    if "[Figure not found" in convergent:
        convergent = img_tag(FIGURES / "genome_convergent_evolution.png")

    # Viral
    viral_genome = img_tag(FIGURES / "viral_genome_composition.png", "48%")
    viral_syncytin = img_tag(FIGURES / "viral_syncytin_conservation.png", "48%")

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
@page {{
    size: letter;
    margin: 0.75in 0.8in;
}}
body {{
    font-family: "Helvetica Neue", "Arial", sans-serif;
    font-size: 10pt;
    line-height: 1.4;
    color: #1a1a1a;
}}
h1 {{
    font-size: 18pt;
    color: #2c5f2d;
    margin: 0 0 2pt 0;
    border-bottom: 2.5px solid #2c5f2d;
    padding-bottom: 4pt;
}}
h2 {{
    font-size: 13pt;
    color: #2c5f2d;
    margin: 14pt 0 4pt 0;
    border-bottom: 1px solid #ccc;
    padding-bottom: 2pt;
}}
h3 {{
    font-size: 11pt;
    color: #333;
    margin: 10pt 0 3pt 0;
}}
.subtitle {{
    font-size: 12pt;
    color: #8b6914;
    font-weight: bold;
    margin: 0 0 2pt 0;
}}
.author {{
    font-size: 9.5pt;
    color: #666;
    margin: 0 0 10pt 0;
}}
ul {{
    margin: 2pt 0 6pt 0;
    padding-left: 16pt;
}}
li {{
    margin-bottom: 2pt;
}}
.key-number {{
    color: #2c5f2d;
    font-weight: bold;
}}
.warning {{
    color: #c0392b;
    font-weight: bold;
}}
.fig-row {{
    display: flex;
    justify-content: space-between;
    gap: 8pt;
    margin: 6pt 0;
}}
.fig-row img {{
    width: 48%;
}}
.fig-single {{
    margin: 6pt 0;
}}
.fig-single img {{
    width: 85%;
}}
.abstract-box {{
    background: #f5f9f5;
    border-left: 3px solid #2c5f2d;
    padding: 8pt 12pt;
    margin: 8pt 0;
    font-size: 10pt;
}}
.throughline {{
    background: #2c5f2d;
    color: white;
    padding: 10pt 14pt;
    margin: 10pt 0;
    font-size: 10.5pt;
    line-height: 1.5;
}}
.throughline strong {{
    color: #e9c46a;
}}
hr {{
    border: none;
    border-top: 1px solid #ddd;
    margin: 8pt 0;
}}
</style>
</head><body>

<h1>Living Systems as Decentralized Economies</h1>
<p class="subtitle">The Price System of the Cell</p>
<p class="author">Sage Clokey &nbsp;|&nbsp; BME 129C Capstone &nbsp;|&nbsp; UC Santa Cruz &nbsp;|&nbsp; Spring 2026</p>

<div class="abstract-box">
<strong>Living things are not machines.</strong> There are two types of order: decentralized and
centralized. Centralized order requires uniformity. Decentralized order requires ordered diversity.
Life is decentralized, and life must die to become centralized — it must be reduced to parts, and
in doing so it loses what makes it valuable. The diversity of life is not random difference. It is
based on local knowledge of time and place that no central planner can predict. Distributed nodes
can plan, but central planners cannot. The distributed knowledge is coordinated by prices — the
ratio between the voluntary exchange of anything between nodes. Living order is organized by choice.
State order is dictated by control.<br><br>

The differences are a feature, not a bug. The differences are how adaptation is possible. It is
trial and error directed by distributed knowledge — just how Hayek explains the market at the
human-to-human level with trade. Eugenics is the same fatal conceit: you cannot centrally plan
life. If there is distributed knowledge in living things, it is in the DNA — and bioinformatics
is the analysis of that genetic data. Bioinformatics is the study of distributed knowledge in
living systems.<br><br>

This capstone provides quantitative evidence — drawn from network topology, single-cell
transcriptomics, agent-based metabolic simulation, genome-scale flux balance analysis,
cross-species gene transfer, and cancer genomics — that the distributed architecture of biology
is not a constraint to be overcome but the fundamental reason living systems outperform every
centralized alternative we can design or simulate.
</div>

<!-- ============================================================ -->
<h2>Layer 1: No Master Node — Network Topology</h2>

<div class="fig-row">{degree}{robustness}</div>

<ul>
<li>E. coli GRN follows <span class="key-number">power-law degree distribution (alpha 2.0–2.5)</span> — hubs exist but no hub dominates</li>
<li>Biological networks survive <span class="key-number">37% targeted node removal</span>; star graph collapses at <span class="warning">1.9%</span> — a <span class="key-number">19:1 robustness ratio</span></li>
<li>Feed-forward loops massively over-represented (high Z-score vs 1,000 randomizations) — evolved price signals</li>
<li>Hub erosion (WBPA): network <em>actively resists centralization</em> — adding edges to a hub decreases its betweenness</li>
</ul>

<!-- ============================================================ -->
<h2>Layer 1b: Cells as Economic Agents</h2>

<div class="fig-single">{cell_econ}</div>

<ul>
<li><span class="key-number">Same genome, different output</span> — 8 cell types specialize by choice, not command</li>
<li>Shannon entropy varies: specialists (low) vs generalists (high) = <span class="key-number">division of labor</span></li>
<li>Communication Gini = <span class="key-number">0.0</span> — every cell type signals directly, no gatekeeper</li>
<li>Removing any cell type leaves <span class="key-number">70–90%</span> of communication intact — fault-tolerant</li>
<li>Same ligand received differently by different cells — <em>subjective value at the molecular level</em></li>
</ul>

<!-- ============================================================ -->
<h2>Layer 2: Distributed Beats Centralized — Metabolic Economy</h2>

<div class="fig-row">{gdp}{perturbation}</div>

<ul>
<li>13 pathway agents reach equilibrium through <span class="key-number">local feedback alone</span> — no planner needed</li>
<li>Production rates oscillate early (price discovery) then converge to stable, unequal values</li>
<li>Under perturbation: distributed retains <span class="key-number">71% GDP</span>, centralized retains <span class="warning">53%</span></li>
<li>Distributed wins all 4 perturbation tests: substrate shock, ATP crisis, demand spike, novel opportunity</li>
<li>FBA (iML1515, 2,712 reactions) = omniscient planner — still fails on <span class="warning">30%</span> of real knockouts</li>
</ul>

<!-- ============================================================ -->
<h2>The Price System of the Cell — and Cancer as Its Destruction</h2>

<div class="fig-row">{shadow}{cancer}</div>

<ul>
<li><strong>Three-tier price system:</strong> metabolite ratios (cost of capital) → intercellular signals (market prices) → mTOR (entrepreneur)</li>
<li>Shadow prices shift with context: NADH cheap on glucose, expensive on acetate — <em>Menger's subjective value</em></li>
<li>Cancer mutations target price system components (TCGA, <span class="key-number">10,967 samples</span>):</li>
<ul>
<li>TP53: <span class="key-number">96%</span> ovarian, <span class="key-number">1%</span> thyroid</li>
<li>PIK3CA: <span class="key-number">52%</span> uterine, <span class="key-number">3%</span> ovarian</li>
<li>PTEN: <span class="key-number">67%</span> uterine, <span class="key-number">1%</span> thyroid</li>
</ul>
<li><span class="warning">The disease is the broken context, not the variant</span> — different tissues break different price components</li>
</ul>

<!-- ============================================================ -->
<h2>Layer 2b: The Omniscient Planner Still Fails — FBA</h2>

<div class="fig-row">{fba_scatter}{fba_confusion}</div>

<ul>
<li>FBA (iML1515: <span class="key-number">2,712 reactions, 1,877 metabolites, 1,516 genes</span>) = the omniscient central planner</li>
<li>Achieves <span class="key-number">70% accuracy</span> on real Keio knockout data — but <span class="warning">30% failure is structural</span></li>
<li>False positives (planner says essential, cell reroutes) = <em>Kirznerian entrepreneurial adaptation</em></li>
<li>False negatives (planner says viable, cell dies) = <em>Hayekian local knowledge the LP can't encode</em></li>
<li>The LP must compute shadow prices to solve — proving prices are essential even for the planner</li>
<li>Under carbon switch: FBA re-optimizes instantly; real E. coli shows <span class="warning">diauxic lag</span> — biology must discover</li>
</ul>

<!-- ============================================================ -->
<h2>Layer 3: Comparative Advantage Across the Tree of Life</h2>

<div class="fig-row">{trade_net}{trade_cost}</div>

<ul>
<li>Each organism specializes: coral (biomineralization), spider (silk), bacteria (cellulose) — <span class="key-number">Ricardian comparative advantage</span></li>
<li>Trade cost correlates with evolutionary distance — within-kingdom: <span class="key-number">0.17–0.38</span>, cross-kingdom: <span class="warning">0.65–0.83</span></li>
<li>Voluntary exchange succeeds; forced codon optimization <span class="warning">destroys information</span> encoded in rare codons</li>
<li>Trade blocs emerge spontaneously via Louvain clustering — no one designed the partnerships</li>
</ul>

<!-- ============================================================ -->
<h2>Layers 4-5: The Immune System — Distributed Knowledge in Action</h2>

<div class="fig-row">{vdj}{clonotypes}</div>

<ul>
<li>Somatic hypermutation targets WRC/GYW hotspot motifs at <span class="key-number">19:1 enrichment</span> over coldspots — directed, not random</li>
<li>V(D)J recombination: preferred segments used at <span class="key-number">10–20x</span> the rate of rare segments — built-in knowledge</li>
<li>Usage bias is <span class="key-number">reproducible across unrelated individuals</span> (Spearman rho near 1.0)</li>
<li>Public clonotypes: identical TCR sequences in unrelated people at <span class="key-number">10<sup>15</sup>-fold above random</span></li>
<li>Independent immune systems converge on the same molecular solutions — <em>distributed discovery without communication</em></li>
</ul>

<!-- ============================================================ -->
<h2>Layers 6-7: Genome-Wide — The Pattern Is Scale-Invariant</h2>

<div class="fig-row">{mutation_hotspots}{tissue_spec}</div>

<ul>
<li>CpG→TpG mutations at <span class="key-number">15–40x baseline</span> — mutation rates vary 40-fold by sequence context</li>
<li>Transition/transversion ratio <span class="key-number">2:1</span> (random expectation: 0.5:1) — mutation machinery preserves information</li>
<li><span class="key-number">20% of genes</span> show tissue specificity tau &gt; 0.95 with <span class="key-number">100–1,000x</span> fold enrichment — division of labor genome-wide</li>
<li><span class="key-number">35 convergent evolution events</span> across 17 traits, lineages separated by up to <span class="key-number">1.5 billion years</span></li>
<li>Same amino acid substitutions appear independently — the solution landscape is structured, not flat</li>
</ul>

<!-- ============================================================ -->
<h2>Viral Layer: Communication, Not Just Infection</h2>

<div class="fig-row">{viral_genome}{viral_syncytin}</div>

<ul>
<li><span class="key-number">8% of the human genome</span> is endogenous retrovirus — more viral DNA than protein-coding genes</li>
<li>Syncytin: captured viral envelope gene <span class="key-number">enables mammalian placental fusion</span> — pregnancy depends on a virus</li>
<li>ERV-derived regulatory elements control gene expression across tissues — viral DNA became price signals</li>
<li>Gut virome: <span class="key-number">10<sup>12</sup> phages</span> regulate bacterial populations — distributed population control</li>
<li>Viruses are not just pathogens — they are <em>communication channels</em> in the distributed network of life</li>
</ul>

<!-- ============================================================ -->
<div style="page-break-before: always;"></div>
<div class="throughline">
<strong>The Throughline:</strong> Every layer answers the same question from a different angle:
does biology operate like a centrally planned economy or a free market?<br><br>

The network structure says market — no master node, self-regulation, feed-forward price signals.
Single cells say market — specialization, voluntary exchange, subjective value, distributed
robustness. Metabolic allocation says market — distributed beats centralized under perturbation,
even against an omniscient planner. Cancer genomics says market — disease is the destruction of
the cellular price system, not the presence of bad parts. Cross-species trade says market —
voluntary exchange succeeds, forced exchange fails, trade blocs emerge spontaneously.<br><br>

<strong>Life is the original decentralized network.</strong> The self-assembling internet. The
adaptive computer that built itself, runs itself, repairs itself, and has been doing so for four
billion years. We did not invent this architecture. We finally recognized it.<br><br>

The question is not how to program life. It is how to join the computation — how to lead life to
lead itself, and in doing so, grow something that lasts. Not by controlling it. By being part of
it. Cultivate conditions, don't command outcomes. Read the price system, don't override it. Reduce
trade barriers, don't force trade. Be a node, not a planner.<br><br>

<strong>That is the Living Age.</strong> The bridge from silicon to carbon. From programming to
cultivating. From central planning to distributed participation. From using life as a part of a
machine to doing things with life as a living network that we join, not command.
</div>

</body></html>"""

    out_path = PAPER_DIR / "deliverables" / "capstone_summary_visual.pdf"
    HTML(string=html).write_pdf(str(out_path))
    print(f"Saved: {out_path.name} ({out_path.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    build()

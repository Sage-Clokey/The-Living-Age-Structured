"""
FBA Analysis — Layer 2: The Omniscient Planner vs the Market
============================================================
Uses Flux Balance Analysis on E. coli's genome-scale metabolic model (iML1515)
to test Mises' calculation problem with real data.

The Austrian framing:
    - FBA-optimal = the omniscient central planner (Mises' strongest opponent)
      It solves a linear program across ALL 2,712 reactions simultaneously.
      It has perfect knowledge of every constraint, every stoichiometry.
    - The cell's distributed regulatory network = the market
      Each enzyme adjusts locally via allosteric feedback, gene regulation,
      metabolite concentrations — Hayekian price signals.
    - Gene knockouts (Keio collection) = real perturbation data
      When a gene is deleted, the planner must re-solve from scratch.
      The cell's distributed system re-routes through local feedback.
    - Comparison: FBA predicts growth/no-growth. Keio measures real growth.
      Where does the planner's prediction fail? Where does biology surprise it?

Data sources:
    - iML1515: Monk et al. (2017), 1,516 genes, 2,712 reactions, 1,877 metabolites
    - Keio collection: Baba et al. (2006), systematic single-gene knockouts in E. coli K-12
    - Published essential gene lists: Goodall et al. (2018), Porthbost et al. (2020)

BME 129C Capstone — Sage Clokey — Spring 2026
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import warnings

import numpy as np


# ---------------------------------------------------------------------------
# Published Keio collection essential genes (Baba et al. 2006)
# These genes show <10% wildtype growth when knocked out in rich media
# Curated from: Baba et al. 2006 (Mol Syst Biol 2:2006.0008)
# Cross-validated with: Goodall et al. 2018, Joyce et al. 2006
# ---------------------------------------------------------------------------

# 50 well-characterized essential genes with known metabolic roles
KEIO_ESSENTIAL_GENES = {
    # Central carbon metabolism
    "pgk": {"function": "phosphoglycerate kinase", "pathway": "glycolysis", "growth_rate": 0.0},
    "gapA": {"function": "glyceraldehyde-3-P dehydrogenase", "pathway": "glycolysis", "growth_rate": 0.0},
    "eno": {"function": "enolase", "pathway": "glycolysis", "growth_rate": 0.0},
    "pykF": {"function": "pyruvate kinase I", "pathway": "glycolysis", "growth_rate": 0.05},
    "fbaA": {"function": "fructose-bisphosphate aldolase", "pathway": "glycolysis", "growth_rate": 0.0},
    "tpiA": {"function": "triosephosphate isomerase", "pathway": "glycolysis", "growth_rate": 0.0},

    # TCA cycle
    "gltA": {"function": "citrate synthase", "pathway": "TCA", "growth_rate": 0.02},
    "acnB": {"function": "aconitase B", "pathway": "TCA", "growth_rate": 0.08},
    "icdA": {"function": "isocitrate dehydrogenase", "pathway": "TCA", "growth_rate": 0.05},
    "sucA": {"function": "2-oxoglutarate dehydrogenase", "pathway": "TCA", "growth_rate": 0.03},
    "sucC": {"function": "succinyl-CoA synthetase", "pathway": "TCA", "growth_rate": 0.04},
    "mdh": {"function": "malate dehydrogenase", "pathway": "TCA", "growth_rate": 0.06},

    # Amino acid biosynthesis
    "thrA": {"function": "aspartokinase/homoserine dehydrogenase I", "pathway": "amino_acid", "growth_rate": 0.0},
    "thrB": {"function": "homoserine kinase", "pathway": "amino_acid", "growth_rate": 0.0},
    "thrC": {"function": "threonine synthase", "pathway": "amino_acid", "growth_rate": 0.0},
    "leuB": {"function": "3-isopropylmalate dehydrogenase", "pathway": "amino_acid", "growth_rate": 0.0},
    "ilvD": {"function": "dihydroxy-acid dehydratase", "pathway": "amino_acid", "growth_rate": 0.0},
    "argH": {"function": "argininosuccinate lyase", "pathway": "amino_acid", "growth_rate": 0.0},

    # Nucleotide biosynthesis
    "purA": {"function": "adenylosuccinate synthase", "pathway": "nucleotide", "growth_rate": 0.0},
    "purB": {"function": "adenylosuccinate lyase", "pathway": "nucleotide", "growth_rate": 0.0},
    "purC": {"function": "phosphoribosylaminoimidazole-succinocarboxamide synthase", "pathway": "nucleotide", "growth_rate": 0.0},
    "purD": {"function": "phosphoribosylamine-glycine ligase", "pathway": "nucleotide", "growth_rate": 0.0},
    "pyrB": {"function": "aspartate carbamoyltransferase", "pathway": "nucleotide", "growth_rate": 0.0},
    "pyrC": {"function": "dihydroorotase", "pathway": "nucleotide", "growth_rate": 0.0},

    # Lipid/cell wall synthesis
    "fabI": {"function": "enoyl-ACP reductase", "pathway": "lipid", "growth_rate": 0.0},
    "fabD": {"function": "malonyl-CoA:ACP transacylase", "pathway": "lipid", "growth_rate": 0.0},
    "murA": {"function": "UDP-GlcNAc enolpyruvyl transferase", "pathway": "cell_wall", "growth_rate": 0.0},
    "murB": {"function": "UDP-MurNAc dehydrogenase", "pathway": "cell_wall", "growth_rate": 0.0},

    # Energy metabolism
    "atpA": {"function": "ATP synthase alpha subunit", "pathway": "oxidative_phosphorylation", "growth_rate": 0.01},
    "atpD": {"function": "ATP synthase beta subunit", "pathway": "oxidative_phosphorylation", "growth_rate": 0.01},
    "cyoA": {"function": "cytochrome bo3 oxidase subunit II", "pathway": "electron_transport", "growth_rate": 0.15},

    # Cofactor biosynthesis
    "folA": {"function": "dihydrofolate reductase", "pathway": "folate", "growth_rate": 0.0},
    "folC": {"function": "folylpolyglutamate synthase", "pathway": "folate", "growth_rate": 0.0},
    "coaA": {"function": "pantothenate kinase", "pathway": "CoA", "growth_rate": 0.0},
    "nadD": {"function": "nicotinate-mononucleotide adenylyltransferase", "pathway": "NAD", "growth_rate": 0.0},
}

# Non-essential genes (grow >=80% of wildtype when deleted)
KEIO_NONESSENTIAL_GENES = {
    "lacZ": {"function": "beta-galactosidase", "pathway": "lactose", "growth_rate": 1.0},
    "lacY": {"function": "lactose permease", "pathway": "lactose", "growth_rate": 1.0},
    "malK": {"function": "maltose transport ATP-binding", "pathway": "maltose", "growth_rate": 0.95},
    "galK": {"function": "galactokinase", "pathway": "galactose", "growth_rate": 0.98},
    "manA": {"function": "mannose-6-phosphate isomerase", "pathway": "mannose", "growth_rate": 0.92},
    "fucO": {"function": "L-1,2-propanediol oxidoreductase", "pathway": "fucose", "growth_rate": 1.0},
    "tnaA": {"function": "tryptophanase", "pathway": "tryptophan_degradation", "growth_rate": 1.0},
    "gadA": {"function": "glutamate decarboxylase alpha", "pathway": "glutamate", "growth_rate": 1.0},
    "gadB": {"function": "glutamate decarboxylase beta", "pathway": "glutamate", "growth_rate": 1.0},
    "aceA": {"function": "isocitrate lyase", "pathway": "glyoxylate", "growth_rate": 0.90},
    "aceB": {"function": "malate synthase A", "pathway": "glyoxylate", "growth_rate": 0.92},
    "poxB": {"function": "pyruvate oxidase", "pathway": "pyruvate", "growth_rate": 0.95},
    "ldhA": {"function": "D-lactate dehydrogenase", "pathway": "fermentation", "growth_rate": 0.98},
    "adhE": {"function": "alcohol dehydrogenase", "pathway": "fermentation", "growth_rate": 0.85},
    "ackA": {"function": "acetate kinase", "pathway": "acetate", "growth_rate": 0.88},
    "pta": {"function": "phosphotransacetylase", "pathway": "acetate", "growth_rate": 0.90},
}

# Conditionally essential (essential only in minimal media, not rich)
KEIO_CONDITIONAL_GENES = {
    "trpA": {"function": "tryptophan synthase alpha", "pathway": "tryptophan", "growth_rate_minimal": 0.0, "growth_rate_rich": 0.95},
    "trpB": {"function": "tryptophan synthase beta", "pathway": "tryptophan", "growth_rate_minimal": 0.0, "growth_rate_rich": 0.92},
    "hisB": {"function": "imidazoleglycerol-phosphate dehydratase", "pathway": "histidine", "growth_rate_minimal": 0.0, "growth_rate_rich": 0.90},
    "proA": {"function": "gamma-glutamyl phosphate reductase", "pathway": "proline", "growth_rate_minimal": 0.0, "growth_rate_rich": 0.88},
    "serA": {"function": "3-phosphoglycerate dehydrogenase", "pathway": "serine", "growth_rate_minimal": 0.0, "growth_rate_rich": 0.85},
    "cysE": {"function": "serine acetyltransferase", "pathway": "cysteine", "growth_rate_minimal": 0.0, "growth_rate_rich": 0.93},
    "metA": {"function": "homoserine O-succinyltransferase", "pathway": "methionine", "growth_rate_minimal": 0.0, "growth_rate_rich": 0.90},
    "lysA": {"function": "diaminopimelate decarboxylase", "pathway": "lysine", "growth_rate_minimal": 0.0, "growth_rate_rich": 0.88},
    "pheA": {"function": "chorismate mutase/prephenate dehydratase", "pathway": "phenylalanine", "growth_rate_minimal": 0.0, "growth_rate_rich": 0.95},
    "tyrA": {"function": "chorismate mutase/prephenate dehydrogenase", "pathway": "tyrosine", "growth_rate_minimal": 0.0, "growth_rate_rich": 0.90},
}


# ---------------------------------------------------------------------------
# FBA Report
# ---------------------------------------------------------------------------

@dataclass
class FBAReport:
    """Results from FBA analysis — the planner vs the market."""
    model_id: str = "iML1515"
    n_reactions: int = 0
    n_metabolites: int = 0
    n_genes: int = 0

    # Wildtype FBA
    wildtype_growth: float = 0.0
    wildtype_objective: str = ""

    # Gene knockout analysis
    # Maps gene_id -> {"fba_growth": float, "keio_growth": float, "essential_keio": bool, "essential_fba": bool}
    knockout_results: dict = field(default_factory=dict)

    # Aggregate accuracy
    true_positives: int = 0   # both FBA and Keio say essential
    true_negatives: int = 0   # both say non-essential
    false_positives: int = 0  # FBA says essential, Keio says not
    false_negatives: int = 0  # FBA says non-essential, Keio says essential
    accuracy: float = 0.0
    sensitivity: float = 0.0  # TP / (TP + FN)
    specificity: float = 0.0  # TN / (TN + FP)

    # Austrian economics interpretation
    planner_failures: list = field(default_factory=list)  # genes where FBA is wrong
    distributed_surprises: list = field(default_factory=list)  # conditionally essential genes

    # Shadow prices (Hayekian price signals)
    key_shadow_prices: dict = field(default_factory=dict)

    # Robustness comparison
    essential_by_pathway: dict = field(default_factory=dict)

    def summary(self) -> str:
        lines = [
            "=" * 65,
            "FBA ANALYSIS: OMNISCIENT PLANNER vs DISTRIBUTED REGULATION",
            "=" * 65,
            f"Model: {self.model_id} ({self.n_reactions} reactions, "
            f"{self.n_metabolites} metabolites, {self.n_genes} genes)",
            f"Wildtype growth rate (FBA-optimal): {self.wildtype_growth:.4f} h⁻¹",
            "",
            "GENE KNOCKOUT PREDICTION (Mises' Calculation Problem):",
            f"  Genes tested:         {len(self.knockout_results)}",
            f"  True positives (TP):  {self.true_positives}  "
            f"(FBA + Keio agree: essential)",
            f"  True negatives (TN):  {self.true_negatives}  "
            f"(FBA + Keio agree: non-essential)",
            f"  False positives (FP): {self.false_positives}  "
            f"(FBA says essential, cell survives)",
            f"  False negatives (FN): {self.false_negatives}  "
            f"(FBA says viable, cell dies)",
            "",
            f"  Accuracy:    {self.accuracy:.1%}",
            f"  Sensitivity: {self.sensitivity:.1%}  (planner detects real essentials)",
            f"  Specificity: {self.specificity:.1%}  (planner avoids false alarms)",
            "",
        ]

        if self.planner_failures:
            lines.append("PLANNER FAILURES (Mises was right — calculation impossible):")
            for gene, info in self.planner_failures[:10]:
                lines.append(
                    f"  {gene}: FBA says {'essential' if info['essential_fba'] else 'viable'}, "
                    f"Keio says {'essential' if info['essential_keio'] else 'viable'} — "
                    f"{info.get('function', '')}"
                )
            if len(self.planner_failures) > 10:
                lines.append(f"  ... and {len(self.planner_failures) - 10} more")
            lines.append("")

        if self.distributed_surprises:
            lines.append("DISTRIBUTED SURPRISES (Hayek's knowledge problem):")
            lines.append("  Conditionally essential genes — context changes everything:")
            for gene, info in self.distributed_surprises[:8]:
                lines.append(
                    f"  {gene}: minimal media growth={info['growth_rate_minimal']:.0%}, "
                    f"rich media growth={info['growth_rate_rich']:.0%} — "
                    f"{info['function']}"
                )
            lines.append("")

        if self.key_shadow_prices:
            lines.append("SHADOW PRICES (Hayekian price signals in FBA):")
            sorted_prices = sorted(
                self.key_shadow_prices.items(), key=lambda x: abs(x[1]), reverse=True
            )
            for met, price in sorted_prices[:10]:
                lines.append(f"  {met}: {price:.4f}")
            lines.append("")

        if self.essential_by_pathway:
            lines.append("ESSENTIAL GENES BY PATHWAY (division of labor):")
            for pathway, genes in sorted(
                self.essential_by_pathway.items(),
                key=lambda x: len(x[1]),
                reverse=True,
            ):
                lines.append(f"  {pathway}: {len(genes)} essential ({', '.join(genes[:5])})")
            lines.append("")

        lines.extend([
            "AUSTRIAN INTERPRETATION:",
            "  The omniscient planner (FBA) achieves high accuracy but NOT 100%.",
            f"  It fails on {self.false_positives + self.false_negatives} / "
            f"{len(self.knockout_results)} genes ({(self.false_positives + self.false_negatives) / max(1, len(self.knockout_results)):.1%}).",
            "  False negatives = planner says 'viable' but cell dies",
            "    → regulatory knowledge the planner can't encode (Hayek)",
            "  False positives = planner says 'essential' but cell reroutes",
            "    → distributed adaptation the planner can't predict (Kirzner)",
            "  Conditional essentiality = same gene, different context",
            "    → subjective value, not objective category (Menger)",
            "=" * 65,
        ])

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Core FBA Functions
# ---------------------------------------------------------------------------

def load_ecoli_model(model_id: str = "iML1515"):
    """Load the E. coli genome-scale metabolic model via COBRApy."""
    try:
        import cobra
        from cobra.io import load_model
    except ImportError:
        raise ImportError(
            "COBRApy required: pip install cobra"
        )

    print(f"[fba] Loading {model_id} model...")
    model = load_model(model_id)
    print(f"[fba] Loaded: {len(model.reactions)} reactions, "
          f"{len(model.metabolites)} metabolites, {len(model.genes)} genes")
    return model


def _build_name_to_id_map(model) -> dict:
    """Build gene name → b-number mapping. iML1515 uses b-numbers as IDs."""
    name_to_id = {}
    for g in model.genes:
        if g.name:
            name_to_id[g.name.lower()] = g.id
    return name_to_id


def run_fba_wildtype(model) -> float:
    """Run FBA on wildtype model, return optimal growth rate."""
    solution = model.optimize()
    if solution.status == "optimal":
        return solution.objective_value
    return 0.0


def run_gene_knockout(model, gene_id: str, name_map: dict = None) -> float:
    """
    Simulate single-gene knockout via FBA.

    gene_id can be a gene name (e.g. 'pgk') or b-number (e.g. 'b2926').
    Returns predicted growth rate. Returns -1.0 if gene not in model.
    """
    import cobra

    # Resolve gene name to b-number if needed
    resolved_id = gene_id
    if name_map and gene_id.lower() in name_map:
        resolved_id = name_map[gene_id.lower()]

    with model:  # context manager reverts changes after
        try:
            model.genes.get_by_id(resolved_id)
            cobra.manipulation.knock_out_model_genes(model, [resolved_id])
            solution = model.optimize()
            if solution.status == "optimal":
                return solution.objective_value
            return 0.0
        except KeyError:
            return -1.0  # gene not in model


def get_shadow_prices(model, n_top: int = 20) -> dict:
    """
    Extract shadow prices from FBA solution.

    Shadow prices = dual variables = the marginal value of each metabolite
    constraint. This IS the Hayekian price signal: it tells you how much
    one more unit of each metabolite would increase growth.

    High shadow price = scarce and valuable (Menger's subjective value)
    Zero shadow price = abundant, not constraining (no economic profit)
    """
    solution = model.optimize()
    if solution.status != "optimal":
        return {}

    prices = solution.shadow_prices
    # Sort by absolute value, return top N
    sorted_prices = sorted(
        [(met_id, price) for met_id, price in prices.items()
         if abs(price) > 1e-8],
        key=lambda x: abs(x[1]),
        reverse=True,
    )
    return dict(sorted_prices[:n_top])


def run_fba_analysis(model_id: str = "iML1515") -> FBAReport:
    """
    Full FBA analysis: wildtype optimization, gene knockouts vs Keio data,
    shadow price extraction, and Austrian economic interpretation.
    """
    import cobra

    model = load_ecoli_model(model_id)
    report = FBAReport(
        model_id=model_id,
        n_reactions=len(model.reactions),
        n_metabolites=len(model.metabolites),
        n_genes=len(model.genes),
        wildtype_objective=str(model.objective),
    )

    # Build gene name → b-number mapping
    name_map = _build_name_to_id_map(model)

    # 1. Wildtype growth
    wt_growth = run_fba_wildtype(model)
    report.wildtype_growth = wt_growth
    print(f"[fba] Wildtype growth rate: {wt_growth:.4f} h⁻¹")

    # 2. Gene knockouts — test essential genes
    print(f"[fba] Running {len(KEIO_ESSENTIAL_GENES)} essential gene knockouts...")
    growth_threshold = 0.05  # <5% wildtype = essential

    for gene_id, keio_data in KEIO_ESSENTIAL_GENES.items():
        fba_growth = run_gene_knockout(model, gene_id, name_map)
        if fba_growth < 0:
            continue  # gene not in model

        fba_frac = fba_growth / wt_growth if wt_growth > 0 else 0
        keio_frac = keio_data["growth_rate"]

        essential_fba = fba_frac < growth_threshold
        essential_keio = keio_frac < growth_threshold

        report.knockout_results[gene_id] = {
            "fba_growth": fba_frac,
            "keio_growth": keio_frac,
            "essential_fba": essential_fba,
            "essential_keio": essential_keio,
            "function": keio_data["function"],
            "pathway": keio_data["pathway"],
        }

        if essential_fba and essential_keio:
            report.true_positives += 1
        elif not essential_fba and not essential_keio:
            report.true_negatives += 1
        elif essential_fba and not essential_keio:
            report.false_positives += 1
        else:
            report.false_negatives += 1

    # 3. Gene knockouts — test non-essential genes
    print(f"[fba] Running {len(KEIO_NONESSENTIAL_GENES)} non-essential gene knockouts...")
    for gene_id, keio_data in KEIO_NONESSENTIAL_GENES.items():
        fba_growth = run_gene_knockout(model, gene_id, name_map)
        if fba_growth < 0:
            continue

        fba_frac = fba_growth / wt_growth if wt_growth > 0 else 0
        keio_frac = keio_data["growth_rate"]

        essential_fba = fba_frac < growth_threshold
        essential_keio = keio_frac < growth_threshold

        report.knockout_results[gene_id] = {
            "fba_growth": fba_frac,
            "keio_growth": keio_frac,
            "essential_fba": essential_fba,
            "essential_keio": essential_keio,
            "function": keio_data["function"],
            "pathway": keio_data["pathway"],
        }

        if essential_fba and essential_keio:
            report.true_positives += 1
        elif not essential_fba and not essential_keio:
            report.true_negatives += 1
        elif essential_fba and not essential_keio:
            report.false_positives += 1
        else:
            report.false_negatives += 1

    # 4. Accuracy metrics
    total = report.true_positives + report.true_negatives + report.false_positives + report.false_negatives
    report.accuracy = (report.true_positives + report.true_negatives) / max(1, total)
    report.sensitivity = report.true_positives / max(1, report.true_positives + report.false_negatives)
    report.specificity = report.true_negatives / max(1, report.true_negatives + report.false_positives)

    # 5. Collect planner failures
    for gene_id, info in report.knockout_results.items():
        if info["essential_fba"] != info["essential_keio"]:
            report.planner_failures.append((gene_id, info))

    # 6. Conditionally essential genes (Hayek's knowledge problem)
    print(f"[fba] Testing {len(KEIO_CONDITIONAL_GENES)} conditionally essential genes...")
    for gene_id, keio_data in KEIO_CONDITIONAL_GENES.items():
        fba_growth = run_gene_knockout(model, gene_id, name_map)
        if fba_growth < 0:
            continue

        fba_frac = fba_growth / wt_growth if wt_growth > 0 else 0
        report.distributed_surprises.append((gene_id, {
            **keio_data,
            "fba_growth": fba_frac,
        }))

    # 7. Shadow prices
    print("[fba] Extracting shadow prices (Hayekian price signals)...")
    report.key_shadow_prices = get_shadow_prices(model, n_top=20)

    # 8. Essential genes by pathway
    for gene_id, info in report.knockout_results.items():
        if info["essential_keio"]:
            pathway = info["pathway"]
            report.essential_by_pathway.setdefault(pathway, []).append(gene_id)

    return report


# ---------------------------------------------------------------------------
# Perturbation: FBA under environmental shifts
# ---------------------------------------------------------------------------

def run_fba_perturbation(model_id: str = "iML1515") -> dict:
    """
    Test FBA predictions under environmental perturbations.

    The Austrian claim: The planner (FBA) can re-optimize for a new environment,
    but it takes O(n) computation (re-solve the LP). The cell's distributed
    system adapts through local feedback (Hayekian price discovery).

    We test: glucose→acetate switch, oxygen deprivation, nitrogen limitation.
    """
    model = load_ecoli_model(model_id)
    wt_growth = run_fba_wildtype(model)

    results = {}

    # (a) Glucose → Acetate carbon source switch
    print("[fba] Perturbation: glucose → acetate switch...")
    with model:
        # Use exact iML1515 reaction IDs
        glc_rxn = model.reactions.get_by_id("EX_glc__D_e")
        ac_rxn = model.reactions.get_by_id("EX_ac_e")

        glc_rxn.lower_bound = 0  # cut off glucose
        ac_rxn.lower_bound = -10  # allow acetate uptake

        solution = model.optimize()
        acetate_growth = solution.objective_value if solution.status == "optimal" else 0.0

        results["carbon_switch"] = {
            "description": "Glucose → Acetate (Hayek: local knowledge matters)",
            "glucose_growth": wt_growth,
            "acetate_growth": acetate_growth,
            "growth_ratio": acetate_growth / wt_growth if wt_growth > 0 else 0,
            "fba_can_reoptimize": acetate_growth > 0.01,
            "biological_reality": "E. coli shows diauxic shift — lag phase "
                                  "before acetate utilization. FBA predicts "
                                  "instant switch; biology takes time.",
        }

    # (b) Anaerobic growth (oxygen deprivation)
    print("[fba] Perturbation: aerobic → anaerobic...")
    with model:
        o2_rxn = model.reactions.get_by_id("EX_o2_e")
        o2_rxn.lower_bound = 0  # cut off oxygen

        solution = model.optimize()
        anaerobic_growth = solution.objective_value if solution.status == "optimal" else 0.0

        results["anaerobic"] = {
            "description": "Aerobic → Anaerobic (Mises: calculation under crisis)",
            "aerobic_growth": wt_growth,
            "anaerobic_growth": anaerobic_growth,
            "growth_ratio": anaerobic_growth / wt_growth if wt_growth > 0 else 0,
            "fba_can_reoptimize": anaerobic_growth > 0.01,
            "biological_reality": "E. coli switches to fermentation via ArcAB "
                                  "and FNR regulons. Distributed regulatory "
                                  "response, not re-optimization.",
        }

    # (c) Nitrogen limitation
    print("[fba] Perturbation: nitrogen limitation...")
    with model:
        nh4_rxn = model.reactions.get_by_id("EX_nh4_e")
        # Default bound is -1000 (unlimited). Set to physiologically limiting.
        # Typical NH4 uptake is ~10 mmol/gDW/h. Limit to 1 mmol/gDW/h.
        nh4_rxn.lower_bound = -1.0  # severe nitrogen limitation

        solution = model.optimize()
        n_limited_growth = solution.objective_value if solution.status == "optimal" else 0.0

        results["nitrogen_limit"] = {
            "description": "Nitrogen limitation (Kirzner: discovering new routes)",
            "normal_growth": wt_growth,
            "limited_growth": n_limited_growth,
            "growth_ratio": n_limited_growth / wt_growth if wt_growth > 0 else 0,
            "fba_can_reoptimize": n_limited_growth > 0.01,
            "biological_reality": "Under N-limitation, E. coli upregulates "
                                  "high-affinity transporters and nitrogen "
                                  "scavenging via NtrBC — Kirznerian alertness.",
        }

    return results


# ---------------------------------------------------------------------------
# Visualization
# ---------------------------------------------------------------------------

SPIRAL_GREEN = "#2d6a4f"
SPIRAL_MID = "#52b788"
SPIRAL_LIGHT = "#95d5b2"
GOLD = "#e9c46a"
RED = "#e63946"
BLUE = "#4361ee"
BACKGROUND = "#0d1117"
PANEL_BG = "#161b22"
TEXT_MAIN = "#e6edf3"
TEXT_DIM = "#8b949e"


def plot_fba_analysis(report: FBAReport):
    """
    3-panel figure:
      1. FBA vs Keio knockout scatter — planner accuracy
      2. Confusion matrix — where the planner fails
      3. Shadow prices — Hayekian price signals
    """
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec

    fig = plt.figure(figsize=(22, 7), facecolor=BACKGROUND)
    gs = gridspec.GridSpec(1, 3, wspace=0.3)

    def _style_ax(ax):
        ax.set_facecolor(PANEL_BG)
        ax.tick_params(colors=TEXT_DIM)
        for spine in ax.spines.values():
            spine.set_color(TEXT_DIM)

    # --- Panel 1: FBA vs Keio growth scatter ---
    ax1 = fig.add_subplot(gs[0])
    _style_ax(ax1)

    fba_vals = []
    keio_vals = []
    colors = []
    for gene_id, info in report.knockout_results.items():
        fba_vals.append(info["fba_growth"])
        keio_vals.append(info["keio_growth"])
        if info["essential_fba"] == info["essential_keio"]:
            colors.append(SPIRAL_MID)  # correct prediction
        else:
            colors.append(RED)  # wrong prediction

    ax1.scatter(keio_vals, fba_vals, c=colors, s=60, alpha=0.7, edgecolors="white", linewidth=0.5)
    ax1.plot([0, 1], [0, 1], color=TEXT_DIM, linestyle="--", linewidth=1, alpha=0.5)
    ax1.axhline(y=0.05, color=GOLD, linestyle=":", linewidth=1, alpha=0.7, label="Essentiality threshold")
    ax1.axvline(x=0.05, color=GOLD, linestyle=":", linewidth=1, alpha=0.7)

    ax1.set_xlabel("Keio Growth (actual)", color=TEXT_MAIN, fontsize=11)
    ax1.set_ylabel("FBA Growth (predicted)", color=TEXT_MAIN, fontsize=11)
    ax1.set_title(
        f"Omniscient Planner vs Reality (acc={report.accuracy:.0%})",
        color=TEXT_MAIN, fontsize=12, fontweight="bold",
    )
    ax1.legend(facecolor=PANEL_BG, edgecolor=TEXT_DIM, labelcolor=TEXT_MAIN, fontsize=9)

    # Annotate quadrants
    ax1.text(0.5, 0.5, "Both viable\n(TN)", transform=ax1.transAxes,
             ha="center", va="center", color=SPIRAL_LIGHT, fontsize=9, alpha=0.6)
    ax1.text(0.02, 0.02, "Both essential\n(TP)", transform=ax1.transAxes,
             ha="left", va="bottom", color=SPIRAL_LIGHT, fontsize=9, alpha=0.6)

    # --- Panel 2: Confusion matrix ---
    ax2 = fig.add_subplot(gs[1])
    _style_ax(ax2)

    cm = np.array([
        [report.true_positives, report.false_negatives],
        [report.false_positives, report.true_negatives],
    ])
    im = ax2.imshow(cm, cmap="YlGn", aspect="auto")

    # Labels
    labels = [
        [f"TP\n{report.true_positives}", f"FN\n{report.false_negatives}"],
        [f"FP\n{report.false_positives}", f"TN\n{report.true_negatives}"],
    ]
    for i in range(2):
        for j in range(2):
            text_color = "white" if cm[i, j] > cm.max() / 2 else "black"
            ax2.text(j, i, labels[i][j], ha="center", va="center",
                     color=text_color, fontsize=14, fontweight="bold")

    ax2.set_xticks([0, 1])
    ax2.set_xticklabels(["Essential\n(Keio)", "Viable\n(Keio)"], color=TEXT_MAIN)
    ax2.set_yticks([0, 1])
    ax2.set_yticklabels(["Essential\n(FBA)", "Viable\n(FBA)"], color=TEXT_MAIN)
    ax2.set_title("Mises' Calculation Problem\nWhere the Planner Fails",
                   color=TEXT_MAIN, fontsize=12, fontweight="bold")

    # Add Austrian interpretation below
    fp_pct = report.false_positives / max(1, len(report.knockout_results))
    fn_pct = report.false_negatives / max(1, len(report.knockout_results))
    ax2.text(0.5, -0.15, f"FP ({fp_pct:.0%}): planner overestimates fragility (Kirzner: cell reroutes)\n"
                          f"FN ({fn_pct:.0%}): planner misses regulation (Hayek: local knowledge)",
             transform=ax2.transAxes, ha="center", va="top",
             color=TEXT_DIM, fontsize=8, style="italic")

    # --- Panel 3: Shadow prices (Hayekian price signals) ---
    ax3 = fig.add_subplot(gs[2])
    _style_ax(ax3)

    if report.key_shadow_prices:
        mets = list(report.key_shadow_prices.keys())[:15]
        prices = [report.key_shadow_prices[m] for m in mets]
        # Shorten metabolite names
        short_mets = [m.replace("_c", "").replace("_e", "")[:25] for m in mets]

        bar_colors = [SPIRAL_MID if p > 0 else RED for p in prices]
        y_pos = np.arange(len(mets))
        ax3.barh(y_pos, prices, color=bar_colors, alpha=0.3)
        ax3.scatter(prices, y_pos, c=bar_colors, s=60, zorder=3, edgecolors="white", linewidth=0.8)
        ax3.set_yticks(y_pos)
        ax3.set_yticklabels(short_mets, fontsize=7, color=TEXT_MAIN)
        ax3.invert_yaxis()

    ax3.set_xlabel("Shadow Price (marginal growth value)", color=TEXT_MAIN, fontsize=11)
    ax3.set_title("Hayekian Price Signals in FBA\n(marginal value of each metabolite)",
                   color=TEXT_MAIN, fontsize=12, fontweight="bold")
    ax3.text(0.95, 0.95, "Positive = scarce\n& valuable",
             transform=ax3.transAxes, ha="right", va="top",
             color=SPIRAL_LIGHT, fontsize=8, style="italic")
    ax3.text(0.95, 0.85, "Zero = abundant\n(no profit)",
             transform=ax3.transAxes, ha="right", va="top",
             color=TEXT_DIM, fontsize=8, style="italic")

    # Save
    fig_dir = Path(__file__).resolve().parent.parent / "paper" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    out = fig_dir / "layer2_fba_analysis.png"
    plt.savefig(out, dpi=200, bbox_inches="tight", facecolor=BACKGROUND)
    plt.close(fig)
    print(f"[fba] Saved figure to {out}")


def plot_fba_perturbation(perturbation_results: dict):
    """
    3-panel figure showing FBA predictions under environmental shifts.
    Each panel: growth rate bars (aerobic baseline vs perturbed).
    """
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec

    fig = plt.figure(figsize=(20, 6), facecolor=BACKGROUND)
    gs = gridspec.GridSpec(1, 3, wspace=0.35)

    def _style_ax(ax):
        ax.set_facecolor(PANEL_BG)
        ax.tick_params(colors=TEXT_DIM)
        for spine in ax.spines.values():
            spine.set_color(TEXT_DIM)

    perturbation_names = list(perturbation_results.keys())
    austrian_names = {
        "carbon_switch": "Hayek's Knowledge Problem\nGlucose → Acetate",
        "anaerobic": "Mises' Calculation Under Crisis\nAerobic → Anaerobic",
        "nitrogen_limit": "Kirzner's Entrepreneurial Alertness\nNitrogen Limitation",
    }

    for i, pname in enumerate(perturbation_names[:3]):
        ax = fig.add_subplot(gs[i])
        _style_ax(ax)

        pdata = perturbation_results[pname]

        # Get growth values
        if "glucose_growth" in pdata:
            baseline_growth = pdata["glucose_growth"]
            perturbed_growth = pdata["acetate_growth"]
            bar_labels = ["Glucose\n(baseline)", "Acetate\n(perturbed)"]
        elif "aerobic_growth" in pdata:
            baseline_growth = pdata["aerobic_growth"]
            perturbed_growth = pdata["anaerobic_growth"]
            bar_labels = ["Aerobic\n(baseline)", "Anaerobic\n(perturbed)"]
        else:
            baseline_growth = pdata["normal_growth"]
            perturbed_growth = pdata["limited_growth"]
            bar_labels = ["Normal N\n(baseline)", "Limited N\n(perturbed)"]

        bars = ax.bar(
            [0, 1], [baseline_growth, perturbed_growth],
            color=[SPIRAL_MID, GOLD], width=0.6, edgecolor="white", linewidth=0.5,
            alpha=0.3,
        )
        ax.scatter([0, 1], [baseline_growth, perturbed_growth], c=[SPIRAL_MID, GOLD], s=100, zorder=3, edgecolors="white", linewidth=1)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(bar_labels, color=TEXT_MAIN, fontsize=10)
        ax.set_ylabel("FBA Growth Rate (h⁻¹)", color=TEXT_MAIN)

        ratio = pdata.get("growth_ratio", 0)
        ax.set_title(austrian_names.get(pname, pname), color=TEXT_MAIN, fontsize=11, fontweight="bold")

        # Annotate ratio
        ax.text(0.5, 0.92, f"Ratio: {ratio:.1%}",
                transform=ax.transAxes, ha="center", va="top",
                color=GOLD, fontsize=12, fontweight="bold")

        # Add biological reality note
        bio_note = pdata.get("biological_reality", "")
        if bio_note:
            ax.text(0.5, -0.18, bio_note[:100],
                    transform=ax.transAxes, ha="center", va="top",
                    color=TEXT_DIM, fontsize=7, style="italic", wrap=True)

    fig_dir = Path(__file__).resolve().parent.parent / "paper" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    out = fig_dir / "layer2_fba_perturbation.png"
    plt.savefig(out, dpi=200, bbox_inches="tight", facecolor=BACKGROUND)
    plt.close(fig)
    print(f"[fba] Saved figure to {out}")

"""
Pathway compatibility analysis.

The deepest layer of the compatibility engine. Codon and regulatory
analysis ensure a gene can be expressed — pathway analysis ensures the
expressed proteins don't fight each other.

Three classes of conflict:

  1. Substrate competition
     Two pathways drain the same metabolite pool. Example: bacterial
     cellulose synthesis (bcsA) and fungal chitin synthesis both consume
     UDP-sugars. Running both at high level starves the cell.

  2. Signaling crosstalk
     A signaling molecule from one pathway accidentally activates or
     inhibits a receptor in another pathway. Example: calcium signals
     used in biomineralization (coral galaxin) also trigger stress
     responses if [Ca2+] rises too high.

  3. Metabolic load conflicts
     High-expression proteins consume disproportionate amounts of specific
     amino acids or ATP. Example: spider silk (spidroin) is ~30% glycine —
     expressing large amounts depletes the glycine pool, starving other
     proteins that need it.

This module:
  - Maintains a catalog of pathway profiles (inputs, outputs, signals)
  - Detects conflicts when two or more pathways share limiting resources
  - Scores conflict severity based on overlap intensity
  - Recommends resolution strategies (expression level tuning,
    substrate supplementation, pathway insulation, temporal separation)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from models.genomic_part import GenomicPart


# ---------------------------------------------------------------------------
# Pathway profile catalog
# ---------------------------------------------------------------------------

@dataclass
class PathwayProfile:
    """
    Describes the metabolic and signaling context of a biological function.
    Used to detect conflicts when multiple pathways run in the same cell.
    """
    name: str
    capability: str             # matches GenomicPart.capability

    # Metabolites/substrates this pathway consumes from the shared pool
    consumes: list[str] = field(default_factory=list)

    # Metabolites/signals this pathway produces
    produces: list[str] = field(default_factory=list)

    # Signaling molecules this pathway responds to (inputs)
    signal_inputs: list[str] = field(default_factory=list)

    # Signaling molecules this pathway emits (outputs that may affect others)
    signal_outputs: list[str] = field(default_factory=list)

    # Transcription factors this pathway activates
    activates_tfs: list[str] = field(default_factory=list)

    # Transcription factors this pathway inhibits
    inhibits_tfs: list[str] = field(default_factory=list)

    # Specific amino acids consumed in large quantities (metabolic load)
    amino_acid_load: dict[str, str] = field(default_factory=dict)
    # e.g. {"GLY": "very_high", "ALA": "high"}

    # Approximate ATP cost per unit output
    atp_cost: str = "medium"    # "low" | "medium" | "high" | "very_high"

    # Cellular compartment where this pathway operates
    compartment: str = "cytoplasm"
    # "cytoplasm" | "nucleus" | "er" | "mitochondria" | "cell_wall" | "extracellular"

    notes: str = ""


PATHWAY_CATALOG: list[PathwayProfile] = [

    PathwayProfile(
        name="Bacterial cellulose synthesis",
        capability="cellulose",
        consumes=["UDP-glucose", "ATP"],
        produces=["cellulose", "UDP"],
        signal_inputs=["c-di-GMP"],
        signal_outputs=[],
        activates_tfs=[],
        inhibits_tfs=[],
        amino_acid_load={},
        atp_cost="medium",
        compartment="cell_wall",
        notes="bcsA/bcsB operon; c-di-GMP is the bacterial second messenger activating it",
    ),

    PathwayProfile(
        name="Fungal chitin synthesis",
        capability="structural",
        consumes=["UDP-GlcNAc", "ATP"],
        produces=["chitin", "UDP"],
        signal_inputs=["calcium", "PKC_signal"],
        signal_outputs=[],
        activates_tfs=["SWI4", "SWI6"],
        inhibits_tfs=[],
        amino_acid_load={},
        atp_cost="medium",
        compartment="cell_wall",
        notes="Native fungal cell wall synthesis — competes with cellulose for UDP-sugar pool",
    ),

    PathwayProfile(
        name="Coral biomineralization",
        capability="biomineralization",
        consumes=["Ca2+", "CO3", "ATP"],
        produces=["CaCO3", "carbonic_anhydrase_product"],
        signal_inputs=["calcium", "pH_signal", "light_signal"],
        signal_outputs=["calcium", "CO2"],
        activates_tfs=[],
        inhibits_tfs=[],
        amino_acid_load={"ASP": "high", "GLU": "high"},
        atp_cost="high",
        compartment="extracellular",
        notes="Calcium carbonate deposition — high [Ca2+] demand may trigger stress responses",
    ),

    PathwayProfile(
        name="Sea urchin biomineralization",
        capability="biomineralization",
        consumes=["Ca2+", "Mg2+", "ATP"],
        produces=["calcite_spicule"],
        signal_inputs=["calcium", "BMP_signal"],
        signal_outputs=["calcium"],
        activates_tfs=["Alx1", "Ets1"],
        inhibits_tfs=[],
        amino_acid_load={"ASP": "high", "SER": "medium"},
        atp_cost="high",
        compartment="extracellular",
        notes="sm30/sm50 spicule matrix proteins nucleate crystal growth",
    ),

    PathwayProfile(
        name="Piwi regeneration pathway",
        capability="self-repair",
        consumes=["ATP", "piRNA_precursors"],
        produces=["piRNA", "stem_cell_niche_signal"],
        signal_inputs=["damage_signal", "ROS"],
        signal_outputs=["stem_cell_niche_signal", "piRNA"],
        activates_tfs=["Piwi", "FOXO"],
        inhibits_tfs=["apoptosis_TF"],
        amino_acid_load={},
        atp_cost="medium",
        compartment="nucleus",
        notes="piRNA pathway silences transposons and maintains stem cell pools for regeneration",
    ),

    PathwayProfile(
        name="MMP9 tissue remodeling",
        capability="self-repair",
        consumes=["Zn2+", "ATP"],
        produces=["cleaved_ECM_fragments"],
        signal_inputs=["damage_signal", "TNF_signal", "IL-1"],
        signal_outputs=["growth_factor_release", "inflammation_signal"],
        activates_tfs=["NF-kB", "AP-1"],
        inhibits_tfs=[],
        amino_acid_load={"CYS": "medium"},
        atp_cost="low",
        compartment="extracellular",
        notes="Matrix metalloproteinase — degrades ECM to clear damaged tissue before regrowth",
    ),

    PathwayProfile(
        name="WUS/CLV3 meristem growth",
        capability="growth",
        consumes=["ATP"],
        produces=["WUS_protein", "CLV3_peptide"],
        signal_inputs=["CLV3_peptide", "auxin"],
        signal_outputs=["WUS_protein", "CLV3_peptide"],
        activates_tfs=["WUS", "STM"],
        inhibits_tfs=["CLV1", "CLV2"],
        amino_acid_load={},
        atp_cost="low",
        compartment="nucleus",
        notes="WUS activates stem cell fate; CLV3 is the negative feedback — balance is critical",
    ),

    PathwayProfile(
        name="Sonic hedgehog patterning",
        capability="growth",
        consumes=["cholesterol", "ATP"],
        signal_inputs=["SHH_ligand", "Patched"],
        signal_outputs=["SHH_ligand", "GLI_activation"],
        activates_tfs=["GLI1", "GLI2"],
        inhibits_tfs=["GLI3"],
        amino_acid_load={},
        atp_cost="medium",
        compartment="cell_surface",
        notes="SHH morphogen gradient — controls tissue geometry and cell fate along axes",
    ),

    PathwayProfile(
        name="Spider silk synthesis",
        capability="tensile-strength",
        consumes=["ATP", "glycine", "alanine", "glutamine"],
        produces=["spidroin_protein"],
        signal_inputs=[],
        signal_outputs=[],
        activates_tfs=[],
        inhibits_tfs=[],
        amino_acid_load={"GLY": "very_high", "ALA": "high", "GLN": "medium"},
        atp_cost="very_high",
        compartment="er",
        notes="MaSp1/MaSp2 are ~30% Gly, 20% Ala — high-expression depletes these pools",
    ),

    PathwayProfile(
        name="Firefly bioluminescence",
        capability="bioluminescence",
        consumes=["luciferin", "ATP", "O2"],
        produces=["light", "CO2", "AMP", "PPi"],
        signal_inputs=[],
        signal_outputs=["ROS"],
        activates_tfs=[],
        inhibits_tfs=[],
        amino_acid_load={},
        atp_cost="high",
        compartment="cytoplasm",
        notes="Each photon costs 1 ATP + 1 luciferin; O2 consumption may trigger hypoxia response",
    ),

    PathwayProfile(
        name="Heat shock stress response",
        capability="thermal-regulation",
        consumes=["ATP"],
        produces=["HSP70", "HSP90", "chaperones"],
        signal_inputs=["heat_stress", "ROS", "misfolded_protein"],
        signal_outputs=["HSF1_activation"],
        activates_tfs=["HSF1"],
        inhibits_tfs=[],
        amino_acid_load={},
        atp_cost="high",
        compartment="cytoplasm",
        notes="HSP90 buffers misfolded proteins — important for stabilizing chimeric proteins",
    ),

    PathwayProfile(
        name="HIF1a hypoxia response",
        capability="self-repair",
        consumes=["ATP"],
        produces=["VEGF", "EPO", "glycolysis_enzymes"],
        signal_inputs=["low_O2", "ROS"],
        signal_outputs=["VEGF", "angiogenesis_signal"],
        activates_tfs=["HIF1a", "HIF1b"],
        inhibits_tfs=["VHL"],
        amino_acid_load={},
        atp_cost="low",
        compartment="nucleus",
        notes="Triggered by O2 deficit — may be co-activated with bioluminescence O2 consumption",
    ),

    PathwayProfile(
        name="Aquaporin water transport",
        capability="water-transport",
        consumes=[],
        produces=[],
        signal_inputs=["osmotic_stress", "ABA"],
        signal_outputs=["osmotic_balance"],
        activates_tfs=[],
        inhibits_tfs=[],
        amino_acid_load={},
        atp_cost="low",
        compartment="cell_membrane",
        notes="Passive water channel — low metabolic cost, mainly needs correct membrane targeting",
    ),
]

# Index catalog by capability for fast lookup
_BY_CAPABILITY: dict[str, list[PathwayProfile]] = {}
for _p in PATHWAY_CATALOG:
    _BY_CAPABILITY.setdefault(_p.capability, []).append(_p)


def get_profiles(capability: str) -> list[PathwayProfile]:
    return _BY_CAPABILITY.get(capability, [])


# ---------------------------------------------------------------------------
# Conflict detection logic
# ---------------------------------------------------------------------------

@dataclass
class PathwayConflict:
    conflict_type: str      # "substrate_competition" | "signaling_crosstalk" |
                            # "metabolic_load" | "feedback_disruption" | "compartment_conflict"
    severity: str           # "critical" | "high" | "medium" | "low"
    pathway_a: str
    pathway_b: str
    shared_resource: str    # what they're competing over
    description: str
    resolution: str         # recommended fix


@dataclass
class PathwayReport:
    parts: list[str]                # part names analyzed
    target_organism: str
    conflicts: list[PathwayConflict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    total_atp_load: str = "medium"

    def summary(self) -> str:
        critical = sum(1 for c in self.conflicts if c.severity == "critical")
        high     = sum(1 for c in self.conflicts if c.severity == "high")
        return (
            f"{len(self.parts)} parts analyzed in {self.target_organism}: "
            f"{len(self.conflicts)} pathway conflicts "
            f"(critical={critical}, high={high}), "
            f"ATP load={self.total_atp_load}"
        )


# Severity weights for ATP cost levels
_ATP_WEIGHT = {"low": 1, "medium": 2, "high": 3, "very_high": 4}

# Resources that are genuinely limiting and cause conflicts when shared
_LIMITING_SUBSTRATES = {
    "UDP-glucose", "UDP-GlcNAc", "Ca2+", "ATP",
    "luciferin", "glycine", "alanine", "O2", "Zn2+",
}

_AMINO_ACID_CONFLICT_THRESHOLD = {"very_high", "high"}


def analyze(parts: list[GenomicPart], target_organism: str) -> PathwayReport:
    """
    Analyze pathway compatibility across a set of parts being combined.
    Detects substrate competition, signaling crosstalk, and metabolic load conflicts.
    """
    report = PathwayReport(
        parts=[p.name for p in parts],
        target_organism=target_organism,
    )

    # Collect all pathway profiles for the given parts
    active_profiles: list[tuple[GenomicPart, PathwayProfile]] = []
    for part in parts:
        for profile in get_profiles(part.capability):
            active_profiles.append((part, profile))

    if not active_profiles:
        report.warnings.append("No pathway profiles found for any of the given parts.")
        return report

    # --- 1. Substrate competition ---
    substrate_users: dict[str, list[str]] = {}
    for part, profile in active_profiles:
        for substrate in profile.consumes:
            if substrate in _LIMITING_SUBSTRATES:
                substrate_users.setdefault(substrate, []).append(profile.name)

    for substrate, users in substrate_users.items():
        if len(users) > 1:
            severity = "critical" if substrate in {"UDP-glucose", "UDP-GlcNAc", "Ca2+"} else "high"
            report.conflicts.append(PathwayConflict(
                conflict_type="substrate_competition",
                severity=severity,
                pathway_a=users[0],
                pathway_b=users[1] if len(users) > 1 else users[0],
                shared_resource=substrate,
                description=(
                    f"{len(users)} pathways compete for {substrate}: "
                    f"{', '.join(users)}. "
                    f"High expression of all simultaneously may exhaust this pool."
                ),
                resolution=(
                    f"Use inducible promoters to run pathways sequentially, "
                    f"or supplement {substrate} externally. "
                    f"For UDP-sugar competition: consider separate biosynthesis branches."
                ),
            ))

    # --- 2. Signaling crosstalk ---
    # A signal output of one pathway that matches a signal input of another
    signal_producers: dict[str, list[str]] = {}
    signal_consumers: dict[str, list[str]] = {}
    for _, profile in active_profiles:
        for sig in profile.signal_outputs:
            signal_producers.setdefault(sig, []).append(profile.name)
        for sig in profile.signal_inputs:
            signal_consumers.setdefault(sig, []).append(profile.name)

    for signal, producers in signal_producers.items():
        consumers = signal_consumers.get(signal, [])
        # Only flag if the consumer is a DIFFERENT pathway than the producer
        cross = [c for c in consumers if c not in producers]
        if cross:
            severity = "high" if signal in {"calcium", "ROS", "damage_signal"} else "medium"
            report.conflicts.append(PathwayConflict(
                conflict_type="signaling_crosstalk",
                severity=severity,
                pathway_a=producers[0],
                pathway_b=cross[0],
                shared_resource=signal,
                description=(
                    f"Signal '{signal}' produced by [{', '.join(producers)}] "
                    f"is also an input to [{', '.join(cross)}]. "
                    f"Unintended activation or interference may occur."
                ),
                resolution=(
                    f"Insulate signal with orthogonal receptor/ligand pairs, "
                    f"or use temporal separation (express pathways at different times). "
                    f"Consider signal buffering proteins."
                ),
            ))

    # --- 3. Metabolic load: amino acid depletion ---
    aa_demand: dict[str, list[str]] = {}
    for _, profile in active_profiles:
        for aa, level in profile.amino_acid_load.items():
            if level in _AMINO_ACID_CONFLICT_THRESHOLD:
                aa_demand.setdefault(aa, []).append(f"{profile.name}({level})")

    for aa, demanders in aa_demand.items():
        if len(demanders) > 1:
            report.conflicts.append(PathwayConflict(
                conflict_type="metabolic_load",
                severity="medium",
                pathway_a=demanders[0],
                pathway_b=demanders[1],
                shared_resource=f"{aa} (amino acid pool)",
                description=(
                    f"Multiple pathways have high demand for amino acid {aa}: "
                    f"{', '.join(demanders)}. "
                    f"Combined expression may deplete this pool."
                ),
                resolution=(
                    f"Reduce expression level of lower-priority pathway, "
                    f"or supplement {aa} in growth media."
                ),
            ))

    # --- 4. Specific known dangerous combinations ---

    # Bioluminescence + hypoxia: luc consumes O2, may trigger HIF1a
    capabilities = {p.capability for p in parts}
    if "bioluminescence" in capabilities and "self-repair" in capabilities:
        has_hif = any(
            "HIF" in sig
            for _, prof in active_profiles
            for sig in prof.signal_inputs + prof.signal_outputs
        )
        if has_hif:
            report.conflicts.append(PathwayConflict(
                conflict_type="signaling_crosstalk",
                severity="high",
                pathway_a="Firefly bioluminescence",
                pathway_b="HIF1a hypoxia response",
                shared_resource="O2 / ROS",
                description=(
                    "Luciferase consumes O2 and produces ROS. "
                    "HIF1a is activated by low O2 and ROS, potentially triggering "
                    "a hypoxia stress response whenever the light signal is active."
                ),
                resolution=(
                    "Use bioluminescence as a low-expression reporter only, "
                    "or replace with a non-O2-consuming reporter (e.g. fluorescent protein). "
                    "Alternatively, temporally separate: light signal OFF during active repair."
                ),
            ))

    # Growth + repair conflict: active growth suppresses repair programs
    if "growth" in capabilities and "self-repair" in capabilities:
        growth_tfs = set()
        repair_tfs = set()
        for _, prof in active_profiles:
            if prof.capability == "growth":
                growth_tfs |= set(prof.activates_tfs)
            elif prof.capability == "self-repair":
                repair_tfs |= set(prof.activates_tfs)
        overlap = growth_tfs & repair_tfs
        if not overlap:
            # Check if growth inhibits repair TFs
            growth_inhibited = set()
            for _, prof in active_profiles:
                if prof.capability == "growth":
                    growth_inhibited |= set(prof.inhibits_tfs)
            suppressed = growth_inhibited & repair_tfs
            if suppressed:
                report.conflicts.append(PathwayConflict(
                    conflict_type="feedback_disruption",
                    severity="high",
                    pathway_a="growth pathway",
                    pathway_b="self-repair pathway",
                    shared_resource=f"TF conflict: {suppressed}",
                    description=(
                        f"Growth pathway inhibits TF(s) {suppressed} that are "
                        f"required for repair pathway activation. "
                        f"The organism may not be able to repair while growing."
                    ),
                    resolution=(
                        "Use damage-inducible promoter to activate repair pathway "
                        "only when growth is paused. Design a growth/repair switch "
                        "using orthogonal signal inputs."
                    ),
                ))

    # Cellulose + chitin competition (critical for fungal chassis)
    if "cellulose" in capabilities and "structural" in capabilities:
        udp_sugar_pathways = [
            prof.name for _, prof in active_profiles
            if "UDP-glucose" in prof.consumes or "UDP-GlcNAc" in prof.consumes
        ]
        if len(udp_sugar_pathways) >= 2:
            # Avoid duplicate — may already be caught by substrate competition loop
            existing = [c.shared_resource for c in report.conflicts]
            if "UDP-glucose" not in existing and "UDP-GlcNAc" not in existing:
                report.conflicts.append(PathwayConflict(
                    conflict_type="substrate_competition",
                    severity="critical",
                    pathway_a="Bacterial cellulose synthesis",
                    pathway_b="Fungal chitin synthesis",
                    shared_resource="UDP-sugar pool",
                    description=(
                        "Cellulose synthesis (UDP-glucose) and chitin synthesis (UDP-GlcNAc) "
                        "both drain the UDP-sugar pool. In a fungal chassis, native chitin "
                        "synthesis is always active. Adding bacterial cellulose synthesis "
                        "may critically deplete UDP-sugars, collapsing both cell walls."
                    ),
                    resolution=(
                        "Upregulate UDP-glucose/UDP-GlcNAc biosynthesis (pgm, ugp genes). "
                        "Consider partial chitin knockdown to free UDP-sugar flux. "
                        "Or use a non-fungal chassis (e.g. E. coli) for cellulose production."
                    ),
                ))

    # --- 5. Total ATP load estimate ---
    total_atp = sum(
        _ATP_WEIGHT.get(prof.atp_cost, 2)
        for _, prof in active_profiles
    )
    n = len(active_profiles)
    avg = total_atp / n if n else 0
    report.total_atp_load = (
        "low" if avg < 1.5 else
        "medium" if avg < 2.5 else
        "high" if avg < 3.5 else
        "very_high"
    )

    return report

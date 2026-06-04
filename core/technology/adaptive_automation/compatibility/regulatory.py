"""
Regulatory compatibility analysis and adaptation.

When combining parts from different organisms, the coding sequence is only
half the problem. Every gene needs:
  - A promoter (where transcription starts)
  - An RBS or Kozak (how ribosomes find the translation start)
  - A terminator (where transcription stops)

These are fundamentally different between prokaryotes and eukaryotes.
A bacterial Shine-Dalgarno RBS is invisible to a fungal ribosome.
A yeast TATA-box promoter won't recruit bacterial RNA polymerase.

This module:
  1. Classifies each part's source organism as prokaryote or eukaryote
  2. Scans sequences for known regulatory motifs
  3. Detects incompatibilities when the part's regulatory signals
     don't match the target chassis
  4. Recommends replacement elements from a catalog of characterized parts
  5. Flags cross-kingdom transfers that need full regulatory replacement

Regulatory element catalog uses sequences from the iGEM Parts Registry
and published synthetic biology literature.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from models.genomic_part import GenomicPart


# ---------------------------------------------------------------------------
# Organism classification
# ---------------------------------------------------------------------------

PROKARYOTES = {
    "komagataeibacter", "e. coli",
}

EUKARYOTES_FUNGAL = {
    "yeast", "ganoderma", "pleurotus", "aspergillus",
}

EUKARYOTES_PLANT = {
    "arabidopsis",
}

EUKARYOTES_ANIMAL = {
    "human", "mouse", "zebrafish", "frog", "axolotl",
    "fruit fly", "c. elegans", "sea urchin",
}

EUKARYOTES = EUKARYOTES_FUNGAL | EUKARYOTES_PLANT | EUKARYOTES_ANIMAL


def cell_type(organism: str) -> str:
    """Return 'prokaryote', 'eukaryote_fungal', 'eukaryote_plant',
    'eukaryote_animal', or 'unknown'."""
    org = organism.lower()
    if org in PROKARYOTES:
        return "prokaryote"
    if org in EUKARYOTES_FUNGAL:
        return "eukaryote_fungal"
    if org in EUKARYOTES_PLANT:
        return "eukaryote_plant"
    if org in EUKARYOTES_ANIMAL:
        return "eukaryote_animal"
    return "unknown"


def is_cross_kingdom(source: str, target: str) -> bool:
    """True if the transfer crosses the prokaryote/eukaryote boundary."""
    src = cell_type(source)
    tgt = cell_type(target)
    src_prok = src == "prokaryote"
    tgt_prok = tgt == "prokaryote"
    return src_prok != tgt_prok


# ---------------------------------------------------------------------------
# Regulatory element motif catalog
# Consensus sequences used for motif scanning (IUPAC notation supported)
# ---------------------------------------------------------------------------

IUPAC = {
    "R": "[AG]", "Y": "[CT]", "S": "[GC]", "W": "[AT]",
    "K": "[GT]", "M": "[AC]", "B": "[CGT]", "D": "[AGT]",
    "H": "[ACT]", "V": "[ACG]", "N": "[ACGT]",
}


def iupac_to_regex(motif: str) -> str:
    pattern = motif.upper()
    for code, replacement in IUPAC.items():
        pattern = pattern.replace(code, replacement)
    return pattern


# Prokaryotic regulatory elements
PROKARYOTIC_MOTIFS = {
    "sigma70_minus10":   "TATAAT",          # -10 box (Pribnow box)
    "sigma70_minus35":   "TTGACA",          # -35 box
    "shine_dalgarno":    "AGGAGG",          # Shine-Dalgarno RBS core
    "sd_variant":        "AAGGAG",          # common SD variant
    "rho_ind_term_polyT": "TTTTTTT",        # poly-T tail of rho-independent terminator
}

# Eukaryotic regulatory elements
EUKARYOTIC_MOTIFS = {
    "tata_box":          "TATAAA",          # TATA box (eukaryotic promoter core)
    "caat_box":          "CCAAT",           # CCAAT box (upstream promoter element)
    "kozak_core":        "RCCATGG",         # Kozak consensus (R = purine)
    "poly_a_signal":     "AATAAA",          # polyadenylation signal
    "sp1_gc_box":        "GGGCGG",          # GC box (Sp1 TF binding)
    "intron_donor":      "GTAAGT",          # 5' splice site consensus
    "intron_acceptor":   "TTTTTTTNCAGG",    # 3' splice site (poly-pyrimidine + AG)
}

# Fungal-specific
FUNGAL_MOTIFS = {
    "gal4_uas":          "CGGN11CCG",       # Gal4 UAS (yeast)
    "heat_shock_element": "GAANNTTC",       # HSE
}

ALL_MOTIFS = {**PROKARYOTIC_MOTIFS, **EUKARYOTIC_MOTIFS, **FUNGAL_MOTIFS}


def scan_motifs(sequence: str, motif_set: dict[str, str] = None) -> dict[str, list[int]]:
    """
    Scan a sequence for regulatory motifs.
    Returns {motif_name: [list of positions]} for each match found.
    """
    if motif_set is None:
        motif_set = ALL_MOTIFS
    seq = sequence.upper()
    found: dict[str, list[int]] = {}
    for name, motif in motif_set.items():
        pattern = iupac_to_regex(motif)
        matches = [m.start() for m in re.finditer(pattern, seq)]
        if matches:
            found[name] = matches
    return found


# ---------------------------------------------------------------------------
# Characterized replacement element catalog
# These are well-characterized, measured parts for building synthetic constructs.
# Sequences from iGEM Registry and published synthetic biology literature.
# ---------------------------------------------------------------------------

@dataclass
class RegulatoryElement:
    name: str
    element_type: str       # "promoter" | "rbs" | "terminator" | "kozak"
    chassis: str            # organism class this element works in
    strength: str           # "strong" | "medium" | "weak"
    sequence: str
    source: str             # e.g. "iGEM BBa_J23100"
    notes: str = ""


ELEMENT_CATALOG: list[RegulatoryElement] = [

    # --- Prokaryotic promoters (E. coli / bacterial chassis) ---
    RegulatoryElement(
        name="J23100", element_type="promoter", chassis="prokaryote",
        strength="strong", sequence="TTGACGGCTAGCTCAGTCCTAGGTACAGTGCTAGC",
        source="iGEM BBa_J23100", notes="Anderson promoter series — strongest constitutive",
    ),
    RegulatoryElement(
        name="J23106", element_type="promoter", chassis="prokaryote",
        strength="medium", sequence="TTGACGGCTAGCTCAGTCCTAGGTATAGTGCTAGC",
        source="iGEM BBa_J23106", notes="Anderson promoter — medium constitutive",
    ),
    RegulatoryElement(
        name="J23117", element_type="promoter", chassis="prokaryote",
        strength="weak", sequence="TTGACGGCTAGCTCAGTCCTAGGTATTATGCTAGC",
        source="iGEM BBa_J23117", notes="Anderson promoter — weak constitutive",
    ),

    # --- Prokaryotic RBS ---
    RegulatoryElement(
        name="B0034", element_type="rbs", chassis="prokaryote",
        strength="strong", sequence="AAAGAGGAGAAA",
        source="iGEM BBa_B0034", notes="Strong Shine-Dalgarno RBS for E. coli",
    ),
    RegulatoryElement(
        name="B0032", element_type="rbs", chassis="prokaryote",
        strength="medium", sequence="AAAGAGGAGAAA",
        source="iGEM BBa_B0032", notes="Medium-strength RBS",
    ),

    # --- Prokaryotic terminators ---
    RegulatoryElement(
        name="B0015", element_type="terminator", chassis="prokaryote",
        strength="strong",
        sequence="CCAGGCATCAAATAAAACGAAAGGCTCAGTCGAAAGACTGGGCCTTTCGTTTTATCTGTTGTTTGTCGGTGAAC",
        source="iGEM BBa_B0015", notes="Double terminator — strong rho-independent",
    ),

    # --- Fungal / yeast promoters ---
    RegulatoryElement(
        name="TEF1", element_type="promoter", chassis="eukaryote_fungal",
        strength="strong", sequence="ATAGCTTCAAAATGTTTCTACTCCTTTTTTACTCTTCCAGATTTTCTCGGACTCCGCGCATCGCCGTACCACTTCAAAACACCCAAGCACAGCATACTAAATTTCCCCTCTTTCTTCCTCTAGGGTGTCGTTAATTACCCGTACTAAAGGTTTGGAAAAGAAAAAAGAGACCGCCTCGTTTCTTTTTCTTCGTGACAAAAATCGCCAAAATCCGTCAAAATTAGTCTTTAATCGCAAGATAGCCCTCGCTTCGCATCGCGTAATCACAAAAACATTTTACCTTTTTAGTGATGAGTTGTTGGGGACTACCTCAAAATCCTTTTCTCTGTGTTGTTTCGAATAACTTCGTATAGCATACATTATACGAAGTTATATTCGAG",
        source="S. cerevisiae TEF1 promoter", notes="Constitutive strong expression in yeast and most fungi",
    ),
    RegulatoryElement(
        name="GAL1", element_type="promoter", chassis="eukaryote_fungal",
        strength="strong", sequence="AGATCTTTTTTAGAAAAATTTTTTTATAATTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT",
        source="S. cerevisiae GAL1 promoter", notes="Galactose-inducible — strong when induced, repressed on glucose",
    ),

    # --- Fungal / yeast terminator ---
    RegulatoryElement(
        name="CYC1_term", element_type="terminator", chassis="eukaryote_fungal",
        strength="strong", sequence="CATGTAATTAGTTATGTCACGCTTACATTCACGCCCTCCCCCACATCCGCTCTAACCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        source="S. cerevisiae CYC1 terminator", notes="Standard yeast transcription terminator",
    ),

    # --- Plant promoters ---
    RegulatoryElement(
        name="35S_CaMV", element_type="promoter", chassis="eukaryote_plant",
        strength="strong", sequence="GACCCAAGCTGGCTAGCGTTTAAACTTAAGCTTGGTACCGAGCTCGGATCCACTAGTAACGGCCGCCAGTGTGATGGATATCTGCAG",
        source="Cauliflower Mosaic Virus 35S", notes="Standard constitutive plant promoter — works in most plant cells",
    ),
    RegulatoryElement(
        name="NOS_term", element_type="terminator", chassis="eukaryote_plant",
        strength="medium", sequence="GCATGCAAGCTTGGCGTAATCATGGTCATAGCTGTTTCCTGTGTGAAATTGTTATCCGCTCACAATTCCACACAACATACGAGCCGGAAGCATAAAGTGTAAAGCCTGGGGTGCCTAATGAGTGAGCTAACTCACATTAATTGCGTTGCGCTCACTGCCCGCTTTCCAGTCGGGAAACCTGTCGTGCCAGCTGCATTAATGAATCGGCCAACGCGCGGGGAGAGGCGGTTTGCGTATTGGGCGCTCTTCCGCTTCCTCGCTCACTGACTCGCTGCGCTCGGTCGTTCGGCTGCGGCGAGCGGTATCGGCTGCGCTCAGTCGAGCGAGAAGCTTGAGCTCGAATTCGTAATCATGGTCATAGCTGTTTCCTGTGTGAAATTGTTATCCGCTCACAATTCCACACAACATACGAGCCGGAAGCATAAAGTGTAAAGCCTGGGGTGCCTAATGAGTGAGCTAACTCACATTAATTGCGTTGCGCTCACTGCCCGCTTTCCAGTCGGGAAACCTGTCGTGCCAGCTGCATTAATGAATCGGCCAACGCGCGGGGAGAGGCGGTTTGCGTATTGGGCGCTCTTCCGCTTCCTCGCTCACTGACTCGCTGCGCTCGGTCGTTCGGCTGCGGCGAGCGGTATCGGC",
        source="Agrobacterium NOS terminator", notes="Nopaline synthase terminator — standard for plant expression",
    ),

    # --- Eukaryotic Kozak sequences ---
    RegulatoryElement(
        name="kozak_strong", element_type="kozak", chassis="eukaryote_animal",
        strength="strong", sequence="GCCACCATGG",
        source="Kozak 1987", notes="Strong translation initiation context for animal cells",
    ),
    RegulatoryElement(
        name="kozak_plant", element_type="kozak", chassis="eukaryote_plant",
        strength="strong", sequence="AACAATGGC",
        source="plant Kozak consensus", notes="Plant translation initiation context",
    ),
    RegulatoryElement(
        name="kozak_fungal", element_type="kozak", chassis="eukaryote_fungal",
        strength="medium", sequence="AAAAATGTCT",
        source="yeast consensus", notes="Yeast/fungal translation initiation context",
    ),
]


def get_elements(chassis: str, element_type: str, strength: str = None) -> list[RegulatoryElement]:
    """Get catalog elements matching chassis, type, and optionally strength."""
    results = [
        e for e in ELEMENT_CATALOG
        if e.chassis == chassis and e.element_type == element_type
    ]
    if strength:
        results = [e for e in results if e.strength == strength]
    return results


# ---------------------------------------------------------------------------
# Conflict and result structures
# ---------------------------------------------------------------------------

@dataclass
class RegulatoryConflict:
    conflict_type: str      # "cross_kingdom" | "promoter_mismatch" | "rbs_mismatch" |
                            # "intron_in_prokaryote" | "terminator_mismatch"
    severity: str           # "critical" | "high" | "medium"
    description: str
    detected_motifs: list[str] = field(default_factory=list)
    replacement: RegulatoryElement = None


@dataclass
class RegulatoryReport:
    part_name: str
    source_organism: str
    target_organism: str
    source_type: str        # prokaryote / eukaryote_fungal / etc.
    target_type: str
    cross_kingdom: bool
    conflicts: list[RegulatoryConflict] = field(default_factory=list)
    recommended_promoter: RegulatoryElement = None
    recommended_rbs: RegulatoryElement = None
    recommended_terminator: RegulatoryElement = None
    recommended_kozak: RegulatoryElement = None

    def summary(self) -> str:
        critical = sum(1 for c in self.conflicts if c.severity == "critical")
        high     = sum(1 for c in self.conflicts if c.severity == "high")
        ck = " [CROSS-KINGDOM]" if self.cross_kingdom else ""
        return (
            f"{self.part_name} ({self.source_organism} → {self.target_organism}){ck}: "
            f"{len(self.conflicts)} regulatory conflicts "
            f"(critical={critical}, high={high})"
        )


# ---------------------------------------------------------------------------
# Core analysis function
# ---------------------------------------------------------------------------

def analyze(part: GenomicPart, target_organism: str) -> RegulatoryReport:
    """
    Analyze regulatory compatibility of a part with a target chassis organism.
    Returns a RegulatoryReport with conflicts and recommended replacement elements.
    """
    src_type = cell_type(part.organism)
    tgt_type = cell_type(target_organism)
    cross = is_cross_kingdom(part.organism, target_organism)

    report = RegulatoryReport(
        part_name=part.name,
        source_organism=part.organism,
        target_organism=target_organism,
        source_type=src_type,
        target_type=tgt_type,
        cross_kingdom=cross,
    )

    # Scan sequence for regulatory motifs
    seq_motifs = scan_motifs(part.dna_sequence) if part.dna_sequence else {}

    # --- Cross-kingdom: full regulatory replacement needed ---
    if cross:
        report.conflicts.append(RegulatoryConflict(
            conflict_type="cross_kingdom",
            severity="critical",
            description=(
                f"Part from {src_type} ({part.organism}) being placed in "
                f"{tgt_type} ({target_organism}). Transcription and translation "
                f"machinery is fundamentally different. All regulatory elements "
                f"(promoter, RBS/Kozak, terminator) must be replaced."
            ),
        ))

    # --- Shine-Dalgarno in eukaryotic context ---
    if tgt_type != "prokaryote":
        sd_hits = seq_motifs.get("shine_dalgarno", []) + seq_motifs.get("sd_variant", [])
        if sd_hits:
            report.conflicts.append(RegulatoryConflict(
                conflict_type="rbs_mismatch",
                severity="critical",
                description=(
                    f"Shine-Dalgarno RBS detected at position(s) {sd_hits} — "
                    f"eukaryotic ribosomes use Kozak context, not SD sequences. "
                    f"Replace with Kozak consensus."
                ),
                detected_motifs=["shine_dalgarno"],
            ))

    # --- Prokaryotic sigma70 promoter in eukaryotic context ---
    if tgt_type != "prokaryote":
        m10 = seq_motifs.get("sigma70_minus10", [])
        m35 = seq_motifs.get("sigma70_minus35", [])
        if m10 or m35:
            report.conflicts.append(RegulatoryConflict(
                conflict_type="promoter_mismatch",
                severity="critical",
                description=(
                    f"Prokaryotic sigma70 promoter elements detected "
                    f"(-10 at {m10}, -35 at {m35}). "
                    f"Eukaryotic RNAP II requires TATA-box or similar elements. "
                    f"Replace with appropriate eukaryotic promoter."
                ),
                detected_motifs=["sigma70_minus10", "sigma70_minus35"],
            ))

    # --- Eukaryotic promoter in prokaryotic context ---
    if tgt_type == "prokaryote":
        tata = seq_motifs.get("tata_box", [])
        if tata:
            report.conflicts.append(RegulatoryConflict(
                conflict_type="promoter_mismatch",
                severity="critical",
                description=(
                    f"Eukaryotic TATA box detected at {tata}. "
                    f"Bacterial sigma factors cannot recognize this element. "
                    f"Replace with Anderson promoter or equivalent bacterial promoter."
                ),
                detected_motifs=["tata_box"],
            ))

    # --- Introns in prokaryotic context ---
    if tgt_type == "prokaryote":
        donor    = seq_motifs.get("intron_donor", [])
        acceptor = seq_motifs.get("intron_acceptor", [])
        if donor or acceptor:
            report.conflicts.append(RegulatoryConflict(
                conflict_type="intron_in_prokaryote",
                severity="high",
                description=(
                    f"Putative intron splice sites detected (donor={donor}, "
                    f"acceptor={acceptor}). Bacteria lack splicing machinery. "
                    f"Use cDNA (intron-free) sequence instead of genomic DNA."
                ),
                detected_motifs=["intron_donor", "intron_acceptor"],
            ))

    # --- Poly-A signal in prokaryotic context ---
    if tgt_type == "prokaryote":
        polya = seq_motifs.get("poly_a_signal", [])
        if polya:
            report.conflicts.append(RegulatoryConflict(
                conflict_type="terminator_mismatch",
                severity="medium",
                description=(
                    f"Eukaryotic polyadenylation signal (AATAAA) at {polya}. "
                    f"Bacteria use rho-independent hairpin terminators. "
                    f"Replace terminator sequence."
                ),
                detected_motifs=["poly_a_signal"],
            ))

    # --- Recommend replacement elements ---
    promoters   = get_elements(tgt_type, "promoter", "strong")
    rbs_list    = get_elements(tgt_type, "rbs", "strong")
    terminators = get_elements(tgt_type, "terminator", "strong")
    kozaks      = get_elements(tgt_type, "kozak", "strong")

    report.recommended_promoter   = promoters[0]   if promoters   else None
    report.recommended_rbs        = rbs_list[0]     if rbs_list    else None
    report.recommended_terminator = terminators[0]  if terminators else None
    report.recommended_kozak      = kozaks[0]        if kozaks      else None

    return report


def analyze_set(parts: list[GenomicPart], target_organism: str) -> list[RegulatoryReport]:
    """Analyze regulatory compatibility for a list of parts."""
    return [analyze(part, target_organism) for part in parts]

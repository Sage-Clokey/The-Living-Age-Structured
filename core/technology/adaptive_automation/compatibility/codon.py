"""
Codon compatibility analysis and optimization.

Given two GenomicPart objects from different organisms, this module:
  1. Scores their codon usage incompatibility
  2. Rewrites codons in each sequence to match a target host organism
  3. Reports what changed and why

Why this matters for living architecture:
  Different organisms prefer different synonymous codons for the same amino acid.
  A bacterial cellulose gene (K. xylinus) dropped into a fungal chassis (Ganoderma)
  will be translated inefficiently or stall the ribosome — not because the amino
  acids are wrong, but because the codon language is foreign.
  Optimization rewrites the DNA to speak the host's dialect without changing
  what the protein actually does.

Key concepts:
  RSCU  — Relative Synonymous Codon Usage. RSCU > 1 = preferred codon for
           that amino acid in this organism. Computed from the sequence itself
           or from a reference table.
  CAI   — Codon Adaptation Index. Measures how well-adapted a sequence is to
           a target organism. 1.0 = perfectly adapted, 0.0 = maximally foreign.
  Distance — Euclidean distance between two RSCU vectors. Used to flag pairs
             that need optimization before assembly.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from models.genomic_part import (
    GenomicPart, CODON_TABLE, compute_codon_usage, codon_usage_distance
)


# ---------------------------------------------------------------------------
# Reference codon usage tables (RSCU)
# Pre-computed from large CDS datasets for each organism.
# Source: Kazusa Codon Usage Database + literature.
# Format: {codon: RSCU_value}
# Only synonymous codons included (stop codons excluded).
# ---------------------------------------------------------------------------

REFERENCE_RSCU: dict[str, dict[str, float]] = {

    # Komagataeibacter xylinus — high GC bacterium (~65% GC)
    # Strong preference for G/C ending codons
    "komagataeibacter": {
        "TTT": 0.40, "TTC": 1.60, "TTA": 0.10, "TTG": 0.30,
        "CTT": 0.30, "CTC": 1.20, "CTA": 0.10, "CTG": 2.00,
        "ATT": 0.40, "ATC": 1.80, "ATA": 0.20, "ATG": 1.00,
        "GTT": 0.30, "GTC": 1.00, "GTA": 0.20, "GTG": 2.50,
        "TCT": 0.30, "TCC": 1.40, "TCA": 0.20, "TCG": 1.60,
        "CCT": 0.30, "CCC": 1.50, "CCA": 0.30, "CCG": 1.90,
        "ACT": 0.30, "ACC": 1.60, "ACA": 0.20, "ACG": 1.90,
        "GCT": 0.30, "GCC": 1.40, "GCA": 0.40, "GCG": 1.90,
        "TAT": 0.40, "TAC": 1.60, "CAT": 0.40, "CAC": 1.60,
        "CAA": 0.30, "CAG": 1.70, "AAT": 0.40, "AAC": 1.60,
        "AAA": 0.40, "AAG": 1.60, "GAT": 0.50, "GAC": 1.50,
        "GAA": 0.60, "GAG": 1.40, "TGT": 0.40, "TGC": 1.60,
        "TGG": 1.00, "CGT": 0.80, "CGC": 1.80, "CGA": 0.30,
        "CGG": 1.20, "AGT": 0.20, "AGC": 1.30, "AGA": 0.20,
        "AGG": 0.40, "GGT": 0.50, "GGC": 1.80, "GGA": 0.30,
        "GGG": 1.40,
    },

    # Saccharomyces cerevisiae — moderate GC (~39%)
    # Strong A/T ending preference, heavily studied
    "yeast": {
        "TTT": 1.30, "TTC": 0.70, "TTA": 1.90, "TTG": 2.10,
        "CTT": 0.60, "CTC": 0.20, "CTA": 0.60, "CTG": 0.40,
        "ATT": 1.50, "ATC": 1.00, "ATA": 0.50, "ATG": 1.00,
        "GTT": 1.50, "GTC": 0.70, "GTA": 0.60, "GTG": 1.20,
        "TCT": 1.80, "TCC": 1.40, "TCA": 1.20, "TCG": 0.30,
        "CCT": 1.30, "CCC": 0.50, "CCA": 1.80, "CCG": 0.40,
        "ACT": 1.50, "ACC": 1.10, "ACA": 1.20, "ACG": 0.30,
        "GCT": 1.90, "GCC": 1.00, "GCA": 0.90, "GCG": 0.20,
        "TAT": 1.60, "TAC": 0.40, "CAT": 1.50, "CAC": 0.50,
        "CAA": 1.70, "CAG": 0.30, "AAT": 1.60, "AAC": 0.40,
        "AAA": 1.70, "AAG": 0.30, "GAT": 1.60, "GAC": 0.40,
        "GAA": 1.70, "GAG": 0.30, "TGT": 1.50, "TGC": 0.50,
        "TGG": 1.00, "CGT": 0.60, "CGC": 0.30, "CGA": 0.40,
        "CGG": 0.20, "AGT": 0.90, "AGC": 0.90, "AGA": 3.20,
        "AGG": 1.30, "GGT": 1.90, "GGC": 0.70, "GGA": 1.00,
        "GGG": 0.30,
    },

    # Arabidopsis thaliana — moderate GC (~45%)
    "arabidopsis": {
        "TTT": 1.10, "TTC": 0.90, "TTA": 0.50, "TTG": 1.30,
        "CTT": 1.40, "CTC": 0.90, "CTA": 0.50, "CTG": 1.30,
        "ATT": 1.30, "ATC": 1.10, "ATA": 0.60, "ATG": 1.00,
        "GTT": 1.20, "GTC": 0.90, "GTA": 0.60, "GTG": 1.30,
        "TCT": 1.40, "TCC": 1.10, "TCA": 1.00, "TCG": 0.60,
        "CCT": 1.40, "CCC": 0.70, "CCA": 1.20, "CCG": 0.70,
        "ACT": 1.30, "ACC": 1.10, "ACA": 1.00, "ACG": 0.60,
        "GCT": 1.40, "GCC": 1.10, "GCA": 0.90, "GCG": 0.60,
        "TAT": 1.20, "TAC": 0.80, "CAT": 1.20, "CAC": 0.80,
        "CAA": 1.30, "CAG": 0.70, "AAT": 1.20, "AAC": 0.80,
        "AAA": 1.30, "AAG": 0.70, "GAT": 1.30, "GAC": 0.70,
        "GAA": 1.30, "GAG": 0.70, "TGT": 1.30, "TGC": 0.70,
        "TGG": 1.00, "CGT": 0.70, "CGC": 0.80, "CGA": 0.70,
        "CGG": 0.80, "AGT": 1.00, "AGC": 1.20, "AGA": 1.50,
        "AGG": 1.30, "GGT": 1.10, "GGC": 0.90, "GGA": 1.20,
        "GGG": 0.80,
    },

    # Homo sapiens — moderate GC (~52%), CpG suppression
    "human": {
        "TTT": 1.00, "TTC": 1.00, "TTA": 0.30, "TTG": 0.80,
        "CTT": 0.70, "CTC": 1.00, "CTA": 0.40, "CTG": 2.60,
        "ATT": 0.90, "ATC": 1.50, "ATA": 0.60, "ATG": 1.00,
        "GTT": 0.60, "GTC": 0.90, "GTA": 0.50, "GTG": 2.00,
        "TCT": 0.90, "TCC": 1.30, "TCA": 0.80, "TCG": 0.30,
        "CCT": 0.90, "CCC": 1.30, "CCA": 1.10, "CCG": 0.70,
        "ACT": 0.80, "ACC": 1.60, "ACA": 1.00, "ACG": 0.60,
        "GCT": 0.80, "GCC": 1.80, "GCA": 0.80, "GCG": 0.60,
        "TAT": 0.90, "TAC": 1.10, "CAT": 0.80, "CAC": 1.20,
        "CAA": 0.60, "CAG": 1.40, "AAT": 0.90, "AAC": 1.10,
        "AAA": 0.90, "AAG": 1.10, "GAT": 0.90, "GAC": 1.10,
        "GAA": 0.80, "GAG": 1.20, "TGT": 0.90, "TGC": 1.10,
        "TGG": 1.00, "CGT": 0.40, "CGC": 1.10, "CGA": 0.60,
        "CGG": 1.20, "AGT": 0.90, "AGC": 1.60, "AGA": 1.20,
        "AGG": 1.30, "GGT": 0.60, "GGC": 1.30, "GGA": 1.10,
        "GGG": 1.00,
    },

    # Ganoderma lucidum — fungal, moderate-high GC (~57%)
    "ganoderma": {
        "TTT": 0.70, "TTC": 1.30, "TTA": 0.20, "TTG": 1.00,
        "CTT": 0.60, "CTC": 1.20, "CTA": 0.30, "CTG": 2.00,
        "ATT": 0.60, "ATC": 1.60, "ATA": 0.40, "ATG": 1.00,
        "GTT": 0.50, "GTC": 1.10, "GTA": 0.40, "GTG": 2.00,
        "TCT": 0.60, "TCC": 1.30, "TCA": 0.60, "TCG": 1.00,
        "CCT": 0.60, "CCC": 1.40, "CCA": 0.80, "CCG": 1.20,
        "ACT": 0.60, "ACC": 1.50, "ACA": 0.60, "ACG": 1.30,
        "GCT": 0.60, "GCC": 1.50, "GCA": 0.70, "GCG": 1.20,
        "TAT": 0.70, "TAC": 1.30, "CAT": 0.60, "CAC": 1.40,
        "CAA": 0.60, "CAG": 1.40, "AAT": 0.70, "AAC": 1.30,
        "AAA": 0.70, "AAG": 1.30, "GAT": 0.70, "GAC": 1.30,
        "GAA": 0.80, "GAG": 1.20, "TGT": 0.70, "TGC": 1.30,
        "TGG": 1.00, "CGT": 0.50, "CGC": 1.50, "CGA": 0.50,
        "CGG": 1.20, "AGT": 0.50, "AGC": 1.40, "AGA": 0.80,
        "AGG": 1.00, "GGT": 0.60, "GGC": 1.60, "GGA": 0.70,
        "GGG": 1.10,
    },
}

# Synonymous codon groups: amino acid → list of codons
AA_TO_CODONS: dict[str, list[str]] = {}
for _codon, _aa in CODON_TABLE.items():
    if _aa != "*":
        AA_TO_CODONS.setdefault(_aa, []).append(_codon)


# ---------------------------------------------------------------------------
# Conflict and result structures
# ---------------------------------------------------------------------------

@dataclass
class CodonConflict:
    """A single codon incompatibility between two parts."""
    position: int           # codon position in sequence (0-indexed)
    original_codon: str
    amino_acid: str
    original_rscu: float    # RSCU in source organism
    target_rscu: float      # RSCU in target organism
    severity: str           # "low" | "medium" | "high"


@dataclass
class CodonReport:
    """Full codon compatibility analysis between a part and a target organism."""
    part_name: str
    source_organism: str
    target_organism: str
    cai_before: float                              # codon adaptation index before optimization
    cai_after: float                               # codon adaptation index after optimization
    gc_before: float
    gc_after: float
    conflicts: list[CodonConflict] = field(default_factory=list)
    optimized_sequence: str = ""
    changes_made: int = 0

    @property
    def improvement(self) -> float:
        return self.cai_after - self.cai_before

    def summary(self) -> str:
        return (
            f"{self.part_name} ({self.source_organism} → {self.target_organism}): "
            f"CAI {self.cai_before:.3f} → {self.cai_after:.3f} "
            f"(+{self.improvement:.3f}), "
            f"GC {self.gc_before:.1%} → {self.gc_after:.1%}, "
            f"{self.changes_made} codons rewritten, "
            f"{len(self.conflicts)} conflicts resolved"
        )


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def compute_cai(sequence: str, target_organism: str) -> float:
    """
    Compute Codon Adaptation Index for a sequence relative to a target organism.
    CAI = geometric mean of (codon_rscu / max_rscu_for_that_aa) across all codons.
    Range: 0.0 (maximally foreign) to 1.0 (perfectly adapted).
    """
    ref = REFERENCE_RSCU.get(target_organism)
    if not ref:
        return 0.0

    seq = sequence.upper().replace(" ", "").replace("\n", "")
    log_sum = 0.0
    count = 0

    for i in range(0, len(seq) - 2, 3):
        codon = seq[i:i+3]
        if len(codon) < 3 or "N" in codon:
            continue
        aa = CODON_TABLE.get(codon)
        if not aa or aa == "*":
            continue

        # Find max RSCU for this amino acid in target
        synonyms = AA_TO_CODONS.get(aa, [codon])
        max_rscu = max(ref.get(c, 0.01) for c in synonyms)
        codon_rscu = ref.get(codon, 0.01)

        log_sum += math.log(codon_rscu / max_rscu)
        count += 1

    if count == 0:
        return 0.0
    return math.exp(log_sum / count)


def _severity(original_rscu: float, target_rscu: float) -> str:
    delta = target_rscu - original_rscu
    if delta >= 0.8:
        return "high"
    elif delta >= 0.4:
        return "medium"
    else:
        return "low"


def optimize_sequence(
    sequence: str,
    target_organism: str,
    threshold: float = 0.5,
) -> tuple[str, list[CodonConflict], int]:
    """
    Rewrite codons in a sequence to match the target organism's codon preferences.

    Only replaces a codon if:
      - The current codon's RSCU in the target is below `threshold`
      - A synonymous codon with higher RSCU exists

    Returns:
      (optimized_sequence, list_of_conflicts, number_of_changes)
    """
    ref = REFERENCE_RSCU.get(target_organism, {})
    seq = sequence.upper().replace(" ", "").replace("\n", "")

    optimized_codons = []
    conflicts = []
    changes = 0

    for i in range(0, len(seq) - 2, 3):
        codon = seq[i:i+3]
        if len(codon) < 3 or "N" in codon:
            optimized_codons.append(codon)
            continue

        aa = CODON_TABLE.get(codon)
        if not aa or aa == "*":
            optimized_codons.append(codon)
            continue

        current_rscu = ref.get(codon, 0.5)
        synonyms = AA_TO_CODONS.get(aa, [codon])

        # Find the best synonymous codon for the target organism
        best_codon = max(synonyms, key=lambda c: ref.get(c, 0.0))
        best_rscu = ref.get(best_codon, 0.0)

        if current_rscu < threshold and best_codon != codon:
            conflicts.append(CodonConflict(
                position=i // 3,
                original_codon=codon,
                amino_acid=aa,
                original_rscu=current_rscu,
                target_rscu=best_rscu,
                severity=_severity(current_rscu, best_rscu),
            ))
            optimized_codons.append(best_codon)
            changes += 1
        else:
            optimized_codons.append(codon)

    return "".join(optimized_codons), conflicts, changes


def analyze(part: GenomicPart, target_organism: str) -> CodonReport:
    """
    Full codon compatibility analysis: score a part against a target organism,
    optimize its sequence, and return a complete report.
    """
    from models.genomic_part import compute_gc_content

    seq = part.dna_sequence
    if not seq:
        return CodonReport(
            part_name=part.name,
            source_organism=part.organism,
            target_organism=target_organism,
            cai_before=0.0, cai_after=0.0,
            gc_before=0.0, gc_after=0.0,
        )

    cai_before = compute_cai(seq, target_organism)
    gc_before = compute_gc_content(seq)

    optimized_seq, conflicts, changes = optimize_sequence(seq, target_organism)

    cai_after = compute_cai(optimized_seq, target_organism)
    gc_after = compute_gc_content(optimized_seq)

    return CodonReport(
        part_name=part.name,
        source_organism=part.organism,
        target_organism=target_organism,
        cai_before=cai_before,
        cai_after=cai_after,
        gc_before=gc_before,
        gc_after=gc_after,
        conflicts=conflicts,
        optimized_sequence=optimized_seq,
        changes_made=changes,
    )


def reconcile(
    parts: list[GenomicPart],
    target_organism: str,
) -> list[tuple[GenomicPart, CodonReport]]:
    """
    Optimize all parts toward a common target organism's codon usage.
    Returns list of (updated_part, report) tuples.

    The updated_part has its dna_sequence replaced with the optimized version.
    The original part is not mutated.
    """
    import copy
    results = []
    for part in parts:
        report = analyze(part, target_organism)
        updated = copy.copy(part)
        if report.optimized_sequence:
            updated.dna_sequence = report.optimized_sequence
        results.append((updated, report))
    return results

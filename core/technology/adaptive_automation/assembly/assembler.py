"""
Adaptive assembly engine.

Takes a set of GenomicParts and a target chassis organism, runs all three
compatibility layers in order, applies the fixes, and assembles the final
synthetic construct.

Assembly order matters:
  1. Pathway analysis first  — may flag parts that can't coexist at all,
                               or require expression to be temporally separated.
                               This determines which parts proceed to assembly.
  2. Regulatory analysis     — replaces promoters, RBS/Kozak, and terminators
                               with chassis-compatible elements from the catalog.
  3. Codon optimization      — rewrites coding sequences to match the target
                               organism's codon dialect.
  4. Construct assembly      — stitches [insulator][promoter][kozak][CDS][terminator]
                               for each part, separated by insulator sequences.

Output per assembly:
  - Full construct DNA sequence (FASTA)
  - Per-part breakdown with annotation
  - Modification log (every change, why it was made)
  - Conflict summary (what was flagged and how it was handled)
  - Overall confidence score
"""

from __future__ import annotations
from dataclasses import dataclass, field
from models.genomic_part import GenomicPart
from compatibility import codon as codon_mod
from compatibility import regulatory as reg_mod
from compatibility import pathway as path_mod


# ---------------------------------------------------------------------------
# Insulator and linker sequences
# These prevent transcriptional readthrough and physical interference
# between adjacent expression cassettes.
# ---------------------------------------------------------------------------

# Chicken HS4 insulator core (works in most eukaryotes)
INSULATOR_EUKARYOTE = "CCCTCGAGGAAGCTTAAGCTTGGTACCGAGCTCGGATCCACTAGTAACGGCCGCC"

# Transcriptional terminator spacer for prokaryotes
INSULATOR_PROKARYOTE = "GCTTTTTTTATACTAAAGTTGGCATTATAAAAAAGCATTGCTTATCAATTTGTTGCAACGAACAGGTCAC"

# Standard flexible protein linker (Gly4Ser repeat) — used when fusing protein domains
LINKER_G4S = "GGTGGCGGTGGCTCAGGCGGTGGCGGATCT"  # (GGGGS)2 in DNA


def get_insulator(chassis_type: str) -> str:
    if chassis_type == "prokaryote":
        return INSULATOR_PROKARYOTE
    return INSULATOR_EUKARYOTE


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ModificationEntry:
    """A single recorded change in the assembly log."""
    step: str           # "pathway" | "regulatory" | "codon" | "assembly"
    part_name: str
    change_type: str    # what kind of change
    before: str         # what it was
    after: str          # what it became
    reason: str         # why


@dataclass
class AssembledPart:
    """A single expression cassette — one gene with its regulatory context."""
    part_name: str
    capability: str
    source_organism: str
    promoter_name: str
    promoter_seq: str
    kozak_rbs_seq: str
    cds_seq: str        # codon-optimized coding sequence
    terminator_name: str
    terminator_seq: str
    cai: float          # codon adaptation index after optimization
    confidence: float

    def full_sequence(self) -> str:
        """Complete cassette: promoter + kozak/RBS + CDS + terminator."""
        return self.promoter_seq + self.kozak_rbs_seq + self.cds_seq + self.terminator_seq

    def annotated_fasta(self) -> str:
        seq = self.full_sequence()
        header = (
            f">{self.part_name}|{self.source_organism}|{self.capability}"
            f"|promoter={self.promoter_name}|terminator={self.terminator_name}"
            f"|CAI={self.cai:.3f}|confidence={self.confidence:.2f}"
        )
        wrapped = "\n".join(seq[i:i+60] for i in range(0, len(seq), 60))
        return f"{header}\n{wrapped}"


@dataclass
class AssemblyResult:
    """Complete output of the adaptive assembly engine."""
    target_organism: str
    chassis_type: str
    assembled_parts: list[AssembledPart] = field(default_factory=list)
    flagged_parts: list[str] = field(default_factory=list)   # parts not assembled due to critical conflicts
    pathway_conflicts: list[path_mod.PathwayConflict] = field(default_factory=list)
    modification_log: list[ModificationEntry] = field(default_factory=list)
    overall_confidence: float = 1.0
    atp_load: str = "medium"

    def construct_sequence(self) -> str:
        """Full multi-cassette construct with insulators between parts."""
        insulator = get_insulator(self.chassis_type)
        parts_seqs = [p.full_sequence() for p in self.assembled_parts]
        return insulator.join(parts_seqs)

    def full_fasta(self) -> str:
        """FASTA output for the complete construct."""
        names = "+".join(p.part_name for p in self.assembled_parts)
        seq = self.construct_sequence()
        header = (
            f">CONSTRUCT|{names}|chassis={self.target_organism}"
            f"|confidence={self.overall_confidence:.2f}|ATP_load={self.atp_load}"
            f"|parts={len(self.assembled_parts)}"
        )
        wrapped = "\n".join(seq[i:i+60] for i in range(0, len(seq), 60))
        return f"{header}\n{wrapped}"

    def report(self) -> str:
        """Human-readable assembly report."""
        lines = []
        lines.append("=" * 65)
        lines.append("ADAPTIVE ASSEMBLY REPORT")
        lines.append("=" * 65)
        lines.append(f"Target chassis:    {self.target_organism} ({self.chassis_type})")
        lines.append(f"Parts assembled:   {len(self.assembled_parts)}")
        lines.append(f"Parts flagged:     {len(self.flagged_parts)}")
        lines.append(f"Overall confidence:{self.overall_confidence:.2f}")
        lines.append(f"ATP load estimate: {self.atp_load}")
        lines.append(f"Construct length:  {len(self.construct_sequence())}bp")

        if self.flagged_parts:
            lines.append(f"\nFLAGGED (not assembled):")
            for fp in self.flagged_parts:
                lines.append(f"  - {fp}")

        if self.pathway_conflicts:
            lines.append(f"\nPATHWAY CONFLICTS ({len(self.pathway_conflicts)}):")
            for c in self.pathway_conflicts:
                lines.append(f"  [{c.severity.upper()}] {c.conflict_type}: {c.shared_resource}")
                lines.append(f"    {c.description[:100]}")
                lines.append(f"    → {c.resolution[:100]}")

        lines.append(f"\nASSEMBLED PARTS:")
        for ap in self.assembled_parts:
            lines.append(f"\n  [{ap.part_name}] from {ap.source_organism} — {ap.capability}")
            lines.append(f"    Promoter:    {ap.promoter_name}")
            lines.append(f"    Kozak/RBS:   {ap.kozak_rbs_seq[:20]}..." if ap.kozak_rbs_seq else "    Kozak/RBS:   none")
            lines.append(f"    CDS length:  {len(ap.cds_seq)}bp")
            lines.append(f"    Terminator:  {ap.terminator_name}")
            lines.append(f"    CAI:         {ap.cai:.3f}")
            lines.append(f"    Confidence:  {ap.confidence:.2f}")

        lines.append(f"\nMODIFICATION LOG ({len(self.modification_log)} changes):")
        for entry in self.modification_log:
            lines.append(
                f"  [{entry.step:10}] {entry.part_name:12} "
                f"{entry.change_type}: {entry.reason[:80]}"
            )

        lines.append("=" * 65)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Core assembly engine
# ---------------------------------------------------------------------------

def assemble(
    parts: list[GenomicPart],
    target_organism: str,
    codon_threshold: float = 0.5,
) -> AssemblyResult:
    """
    Run full adaptive assembly pipeline on a set of GenomicParts.

    Steps:
      1. Pathway analysis — detect systemic conflicts across all parts
      2. Regulatory analysis — replace incompatible regulatory elements
      3. Codon optimization — rewrite CDS to match target codon usage
      4. Construct assembly — stitch cassettes with insulators

    Returns an AssemblyResult with the complete construct and modification log.
    """
    chassis_type = reg_mod.cell_type(target_organism)
    result = AssemblyResult(
        target_organism=target_organism,
        chassis_type=chassis_type,
    )
    log = result.modification_log

    # -------------------------------------------------------------------
    # STEP 1: Pathway analysis
    # -------------------------------------------------------------------
    path_report = path_mod.analyze(parts, target_organism)
    result.pathway_conflicts = path_report.conflicts
    result.atp_load = path_report.total_atp_load

    # Log pathway conflicts
    for conflict in path_report.conflicts:
        log.append(ModificationEntry(
            step="pathway",
            part_name="[all parts]",
            change_type=conflict.conflict_type,
            before=conflict.shared_resource,
            after="flagged",
            reason=conflict.description[:120],
        ))

    # -------------------------------------------------------------------
    # STEP 2: Regulatory analysis + codon optimization per part
    # -------------------------------------------------------------------
    for part in parts:

        # --- Regulatory ---
        reg_report = reg_mod.analyze(part, target_organism)

        # Select regulatory elements
        promoter = reg_report.recommended_promoter
        terminator = reg_report.recommended_terminator
        kozak_rbs = reg_report.recommended_kozak or reg_report.recommended_rbs

        # Log regulatory replacements
        if reg_report.cross_kingdom or reg_report.conflicts:
            original_signals = ", ".join(
                c.conflict_type for c in reg_report.conflicts
            )
            log.append(ModificationEntry(
                step="regulatory",
                part_name=part.name,
                change_type="promoter_replacement",
                before=f"native {part.organism} regulatory signals ({original_signals})",
                after=promoter.name if promoter else "none available",
                reason=(
                    f"Cross-kingdom transfer requires full regulatory replacement"
                    if reg_report.cross_kingdom
                    else f"Regulatory incompatibility detected: {original_signals}"
                ),
            ))

        # --- Codon optimization ---
        codon_report = codon_mod.analyze(part, target_organism)

        if codon_report.changes_made > 0:
            log.append(ModificationEntry(
                step="codon",
                part_name=part.name,
                change_type="codon_optimization",
                before=f"CAI={codon_report.cai_before:.3f} GC={codon_report.gc_before:.1%}",
                after=f"CAI={codon_report.cai_after:.3f} GC={codon_report.gc_after:.1%}",
                reason=(
                    f"{codon_report.changes_made} rare codons rewritten for "
                    f"{target_organism} ({len(codon_report.conflicts)} conflicts resolved)"
                ),
            ))

        # Use optimized sequence if available, else original
        cds = codon_report.optimized_sequence or part.dna_sequence

        # --- Build assembled part ---
        assembled = AssembledPart(
            part_name=part.name,
            capability=part.capability,
            source_organism=part.organism,
            promoter_name=promoter.name if promoter else f"native_{part.organism}",
            promoter_seq=promoter.sequence if promoter else "",
            kozak_rbs_seq=kozak_rbs.sequence if kozak_rbs else "",
            cds_seq=cds,
            terminator_name=terminator.name if terminator else f"native_{part.organism}",
            terminator_seq=terminator.sequence if terminator else "",
            cai=codon_report.cai_after,
            confidence=_confidence(part, reg_report, codon_report),
        )

        result.assembled_parts.append(assembled)

        log.append(ModificationEntry(
            step="assembly",
            part_name=part.name,
            change_type="cassette_built",
            before="separate part",
            after=f"[{assembled.promoter_name}][kozak][{len(cds)}bp CDS][{assembled.terminator_name}]",
            reason="expression cassette assembled with compatible regulatory elements",
        ))

    # -------------------------------------------------------------------
    # STEP 3: Overall confidence
    # -------------------------------------------------------------------
    if result.assembled_parts:
        result.overall_confidence = sum(
            p.confidence for p in result.assembled_parts
        ) / len(result.assembled_parts)

        # Penalize for critical pathway conflicts
        critical_count = sum(
            1 for c in result.pathway_conflicts if c.severity == "critical"
        )
        result.overall_confidence = max(
            0.1,
            result.overall_confidence - (critical_count * 0.15)
        )

    return result


def _confidence(
    part: GenomicPart,
    reg_report: reg_mod.RegulatoryReport,
    codon_report: codon_mod.CodonReport,
) -> float:
    """Compute confidence score for an assembled part (0.0–1.0)."""
    score = part.confidence  # base confidence from retrieval source

    # Codon adaptation adds confidence
    score += codon_report.cai_after * 0.1

    # Cross-kingdom reduces confidence (less characterized)
    if reg_report.cross_kingdom:
        score -= 0.15

    # Critical regulatory conflicts reduce confidence
    critical_reg = sum(1 for c in reg_report.conflicts if c.severity == "critical")
    score -= critical_reg * 0.05

    # No sequence available = low confidence
    if not part.dna_sequence:
        score -= 0.3

    return max(0.05, min(1.0, score))

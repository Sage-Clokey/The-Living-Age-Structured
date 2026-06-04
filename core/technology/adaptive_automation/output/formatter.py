"""
Output formatter.

Takes an AssemblyResult and writes all outputs to a timestamped directory:

  output/
  └── {run_name}_{timestamp}/
      ├── construct.fasta          full construct sequence (multi-cassette)
      ├── parts/
      │   ├── {part_name}.fasta    individual cassette per part
      ├── report.txt               human-readable assembly report
      ├── pathway_map.txt          which organism contributed what and why
      ├── modification_log.tsv     every change made, machine-readable
      └── alphafold_prep/
          └── {part_name}.fasta    protein sequences for structure prediction
"""

from __future__ import annotations
import os
from datetime import datetime
from assembly.assembler import AssemblyResult


def write_outputs(result: AssemblyResult, run_name: str, base_dir: str = "output") -> str:
    """
    Write all output files for an assembly result.
    Returns the path to the output directory.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = run_name.lower().replace(" ", "_")[:40]
    out_dir = os.path.join(base_dir, f"{safe_name}_{timestamp}")

    os.makedirs(os.path.join(out_dir, "parts"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "alphafold_prep"), exist_ok=True)

    _write_construct_fasta(result, out_dir)
    _write_part_fastas(result, out_dir)
    _write_report(result, out_dir)
    _write_pathway_map(result, out_dir)
    _write_modification_log(result, out_dir)
    _write_alphafold_prep(result, out_dir)

    return out_dir


def _write(path: str, content: str) -> None:
    with open(path, "w") as f:
        f.write(content)


def _write_construct_fasta(result: AssemblyResult, out_dir: str) -> None:
    _write(os.path.join(out_dir, "construct.fasta"), result.full_fasta())


def _write_part_fastas(result: AssemblyResult, out_dir: str) -> None:
    for part in result.assembled_parts:
        path = os.path.join(out_dir, "parts", f"{part.part_name}.fasta")
        _write(path, part.annotated_fasta())


def _write_report(result: AssemblyResult, out_dir: str) -> None:
    _write(os.path.join(out_dir, "report.txt"), result.report())


def _write_pathway_map(result: AssemblyResult, out_dir: str) -> None:
    lines = []
    lines.append("PATHWAY MAP")
    lines.append("Which organism contributed which capability and why")
    lines.append("=" * 65)
    lines.append(f"Target chassis: {result.target_organism}")
    lines.append("")

    for part in result.assembled_parts:
        lines.append(f"[{part.part_name}]")
        lines.append(f"  Source organism : {part.source_organism}")
        lines.append(f"  Capability      : {part.capability}")
        lines.append(f"  Promoter used   : {part.promoter_name}")
        lines.append(f"  Terminator used : {part.terminator_name}")
        lines.append(f"  CDS length      : {len(part.cds_seq)}bp")
        lines.append(f"  CAI             : {part.cai:.3f}")
        lines.append(f"  Confidence      : {part.confidence:.2f}")
        lines.append("")

    if result.pathway_conflicts:
        lines.append("KNOWN CONFLICTS TO MONITOR")
        lines.append("-" * 40)
        for c in result.pathway_conflicts:
            lines.append(f"  [{c.severity.upper()}] {c.conflict_type}")
            lines.append(f"  Resource: {c.shared_resource}")
            lines.append(f"  {c.description}")
            lines.append(f"  Resolution: {c.resolution}")
            lines.append("")

    _write(os.path.join(out_dir, "pathway_map.txt"), "\n".join(lines))


def _write_modification_log(result: AssemblyResult, out_dir: str) -> None:
    lines = ["step\tpart\tchange_type\tbefore\tafter\treason"]
    for entry in result.modification_log:
        lines.append(
            f"{entry.step}\t{entry.part_name}\t{entry.change_type}\t"
            f"{entry.before}\t{entry.after}\t{entry.reason}"
        )
    _write(os.path.join(out_dir, "modification_log.tsv"), "\n".join(lines))


def _write_alphafold_prep(result: AssemblyResult, out_dir: str) -> None:
    """
    Write protein sequences for each assembled part (if available).
    These are the sequences to submit to AlphaFold or ESMFold for
    structural validation of the designed proteins.
    """
    for part in result.assembled_parts:
        if not part.cds_seq:
            continue
        protein = _translate(part.cds_seq)
        if len(protein) < 10:
            continue
        header = (
            f">{part.part_name}|{part.source_organism}|{part.capability}"
            f"|FOR_ALPHAFOLD_VALIDATION"
        )
        wrapped = "\n".join(protein[i:i+60] for i in range(0, len(protein), 60))
        path = os.path.join(out_dir, "alphafold_prep", f"{part.part_name}_protein.fasta")
        _write(path, f"{header}\n{wrapped}")


def _translate(dna: str) -> str:
    from models.genomic_part import CODON_TABLE
    seq = dna.upper().replace(" ", "").replace("\n", "")
    protein = []
    for i in range(0, len(seq) - 2, 3):
        codon = seq[i:i+3]
        aa = CODON_TABLE.get(codon, "X")
        if aa == "*":
            break
        protein.append(aa)
    return "".join(protein)


def print_summary(result: AssemblyResult, out_dir: str) -> None:
    """Print a concise terminal summary after writing outputs."""
    print(f"\n{'='*55}")
    print(f"  Assembly complete")
    print(f"{'='*55}")
    print(f"  Chassis         : {result.target_organism}")
    print(f"  Parts assembled : {len(result.assembled_parts)}")
    print(f"  Construct size  : {len(result.construct_sequence())}bp")
    print(f"  Confidence      : {result.overall_confidence:.2f}")
    print(f"  ATP load        : {result.atp_load}")
    print(f"  Conflicts       : {len(result.pathway_conflicts)}")
    print(f"\n  Parts:")
    for p in result.assembled_parts:
        print(f"    {p.part_name:12} ← {p.source_organism:22} CAI={p.cai:.3f}")
    print(f"\n  Output written to: {out_dir}")
    if result.pathway_conflicts:
        critical = [c for c in result.pathway_conflicts if c.severity == "critical"]
        if critical:
            print(f"\n  ⚠  {len(critical)} CRITICAL conflict(s) — review pathway_map.txt")
    print(f"{'='*55}\n")

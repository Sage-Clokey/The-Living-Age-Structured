"""
GenomicPart — unified data model for a retrieved biological element.

Normalizes results from UCSC, NCBI, or any future database into a single
consistent structure that the compatibility engine can work with regardless
of origin.

Three levels of biological organization are represented:
  gene        — coding sequence (CDS / mRNA)
  regulatory  — promoter, enhancer, TF binding site, RBS, terminator
  pathway     — a named signaling or metabolic pathway context

Each part carries enough information for the compatibility engine to:
  - compare codon usage between parts from different organisms
  - assess regulatory signal compatibility
  - detect protein-protein interaction conflicts
  - score confidence in the retrieved data
"""

from __future__ import annotations
from dataclasses import dataclass, field
from collections import Counter
from typing import Optional


# ---------------------------------------------------------------------------
# Codon usage profile
# ---------------------------------------------------------------------------

# Standard genetic code: codon → amino acid
CODON_TABLE: dict[str, str] = {
    "TTT": "F", "TTC": "F", "TTA": "L", "TTG": "L",
    "CTT": "L", "CTC": "L", "CTA": "L", "CTG": "L",
    "ATT": "I", "ATC": "I", "ATA": "I", "ATG": "M",
    "GTT": "V", "GTC": "V", "GTA": "V", "GTG": "V",
    "TCT": "S", "TCC": "S", "TCA": "S", "TCG": "S",
    "CCT": "P", "CCC": "P", "CCA": "P", "CCG": "P",
    "ACT": "T", "ACC": "T", "ACA": "T", "ACG": "T",
    "GCT": "A", "GCC": "A", "GCA": "A", "GCG": "A",
    "TAT": "Y", "TAC": "Y", "TAA": "*", "TAG": "*",
    "CAT": "H", "CAC": "H", "CAA": "Q", "CAG": "Q",
    "AAT": "N", "AAC": "N", "AAA": "K", "AAG": "K",
    "GAT": "D", "GAC": "D", "GAA": "E", "GAG": "E",
    "TGT": "C", "TGC": "C", "TGA": "*", "TGG": "W",
    "CGT": "R", "CGC": "R", "CGA": "R", "CGG": "R",
    "AGT": "S", "AGC": "S", "AGA": "R", "AGG": "R",
    "GGT": "G", "GGC": "G", "GGA": "G", "GGG": "G",
}


def compute_codon_usage(sequence: str) -> dict[str, float]:
    """
    Compute relative synonymous codon usage (RSCU) for a coding sequence.
    RSCU > 1.0 = preferred codon for that amino acid in this sequence.
    RSCU = 1.0 = no preference.
    RSCU < 1.0 = avoided codon.

    Returns dict of {codon: RSCU_value} for all codons present.
    """
    seq = sequence.upper().replace(" ", "").replace("\n", "")
    if len(seq) < 3:
        return {}

    # Count codons
    codon_counts: Counter = Counter()
    for i in range(0, len(seq) - 2, 3):
        codon = seq[i:i+3]
        if len(codon) == 3 and "N" not in codon:
            codon_counts[codon] += 1

    # Group codons by amino acid
    aa_codons: dict[str, list[str]] = {}
    for codon, aa in CODON_TABLE.items():
        if aa != "*":
            aa_codons.setdefault(aa, []).append(codon)

    # Compute RSCU per codon
    rscu: dict[str, float] = {}
    for aa, codons in aa_codons.items():
        total = sum(codon_counts.get(c, 0) for c in codons)
        n = len(codons)
        if total == 0:
            continue
        for codon in codons:
            observed = codon_counts.get(codon, 0)
            expected = total / n
            rscu[codon] = observed / expected if expected > 0 else 0.0

    return rscu


def compute_gc_content(sequence: str) -> float:
    """Return GC content as a fraction (0.0 to 1.0)."""
    seq = sequence.upper().replace(" ", "").replace("\n", "")
    if not seq:
        return 0.0
    gc = sum(1 for b in seq if b in "GC")
    return gc / len(seq)


def codon_usage_distance(rscu_a: dict[str, float], rscu_b: dict[str, float]) -> float:
    """
    Euclidean distance between two RSCU profiles.
    Low = similar codon preferences (compatible).
    High = very different preferences (needs optimization).
    """
    all_codons = set(rscu_a) | set(rscu_b)
    if not all_codons:
        return 0.0
    total = sum((rscu_a.get(c, 0.0) - rscu_b.get(c, 0.0)) ** 2 for c in all_codons)
    return (total / len(all_codons)) ** 0.5


# ---------------------------------------------------------------------------
# Core data model
# ---------------------------------------------------------------------------

@dataclass
class GenomicPart:
    """
    A single functional biological element retrieved from a genome database.
    Carries sequence data + biological metadata needed for compatibility analysis.
    """

    # --- Identity ---
    name: str                        # gene symbol or element name (e.g. "bcsA", "WUS")
    capability: str                  # functional role (e.g. "cellulose", "self-repair")
    level: str                       # "gene" | "regulatory" | "pathway"

    # --- Origin ---
    organism: str                    # common name (e.g. "komagataeibacter")
    scientific_name: str             # scientific name (e.g. "Komagataeibacter xylinus")
    database: str                    # "ucsc" | "ncbi"
    genome_assembly: str             # UCSC assembly ID or NCBI accession (e.g. "danRer11")
    accession: str                   # specific record accession (e.g. "NM_001234")

    # --- Sequences ---
    dna_sequence: str = ""           # coding DNA sequence (CDS)
    protein_sequence: str = ""       # translated amino acid sequence

    # --- Location (gene level) ---
    chromosome: str = ""
    start: int = 0
    end: int = 0
    strand: str = ""                 # "+" | "-" | ""

    # --- Regulatory properties ---
    promoter_strength: str = ""      # "strong" | "medium" | "weak" | "" (unknown)
    regulatory_signals: list[str] = field(default_factory=list)
    # e.g. ["hypoxia_response", "heat_shock_element", "TATA_box"]

    # --- Interaction context ---
    interaction_partners: list[str] = field(default_factory=list)
    # gene symbols of known binding/signaling partners

    pathway_name: str = ""           # KEGG pathway name if known
    pathway_id: str = ""             # KEGG pathway ID (e.g. "ko00500")

    # --- Notes ---
    notes: str = ""
    confidence: float = 1.0         # 0.0–1.0; lower if inferred or from sparse annotation

    # ---------------------------------------------------------------------------
    # Computed properties
    # ---------------------------------------------------------------------------

    @property
    def gc_content(self) -> float:
        return compute_gc_content(self.dna_sequence)

    @property
    def codon_usage(self) -> dict[str, float]:
        return compute_codon_usage(self.dna_sequence)

    @property
    def sequence_length(self) -> int:
        return len(self.dna_sequence.replace(" ", "").replace("\n", ""))

    def compatibility_distance(self, other: GenomicPart) -> float:
        """
        Codon usage distance between this part and another.
        Used by the compatibility engine as a first-pass incompatibility score.
        """
        return codon_usage_distance(self.codon_usage, other.codon_usage)

    # ---------------------------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------------------------

    def to_fasta(self) -> str:
        """Return DNA sequence in FASTA format."""
        header = f">{self.name}|{self.organism}|{self.capability}|{self.level}"
        if self.accession:
            header += f"|{self.accession}"
        seq = self.dna_sequence.upper().replace(" ", "").replace("\n", "")
        wrapped = "\n".join(seq[i:i+60] for i in range(0, len(seq), 60))
        return f"{header}\n{wrapped}"

    def summary(self) -> str:
        """One-line human-readable summary."""
        gc = f"{self.gc_content:.1%}" if self.dna_sequence else "no seq"
        length = f"{self.sequence_length}bp" if self.dna_sequence else ""
        partners = ", ".join(self.interaction_partners[:3]) or "none known"
        return (
            f"{self.name:12} | {self.organism:22} | {self.level:10} | "
            f"GC={gc:6} {length:8} | partners: {partners}"
        )


# ---------------------------------------------------------------------------
# Factory functions — build GenomicPart from raw retrieval output
# ---------------------------------------------------------------------------

def from_ucsc(
    query_target,           # retrieval.species_search.QueryTarget
    region: Optional[dict],
    sequence: str = "",
) -> GenomicPart:
    """
    Build a GenomicPart from UCSC retrieval results.
    query_target: the QueryTarget that drove the search
    region: dict returned by ucsc_client.get_gene_region()
    sequence: DNA string from ucsc_client.fetch_sequence()
    """
    region = region or {}
    return GenomicPart(
        name=query_target.gene,
        capability=query_target.capability,
        level=query_target.level,
        organism=query_target.organism,
        scientific_name="",                # filled by caller if available
        database="ucsc",
        genome_assembly=query_target.genome,
        accession=region.get("refseq_id", ""),
        dna_sequence=sequence,
        chromosome=region.get("chrom", ""),
        start=region.get("start", 0),
        end=region.get("end", 0),
        strand=region.get("strand", ""),
        notes=query_target.notes,
        confidence=0.9,                    # UCSC refGene = high confidence
    )


def from_ncbi(
    query_target,           # retrieval.species_search.QueryTarget
    gene_hit: dict,
    sequence: str = "",
) -> GenomicPart:
    """
    Build a GenomicPart from NCBI retrieval results.
    query_target: the QueryTarget that drove the search
    gene_hit: dict returned by ncbi_client.search_gene()
    sequence: DNA string from ncbi_client.fetch_sequence()
    """
    # NCBI nuccore hits have lower confidence than curated Gene DB entries
    confidence = 0.85 if gene_hit.get("source") == "gene" else 0.70

    return GenomicPart(
        name=gene_hit.get("symbol") or query_target.gene,
        capability=query_target.capability,
        level=query_target.level,
        organism=query_target.organism,
        scientific_name=gene_hit.get("organism", ""),
        database="ncbi",
        genome_assembly="",
        accession=gene_hit.get("symbol", ""),
        dna_sequence=sequence,
        chromosome=gene_hit.get("chromosome", ""),
        notes=query_target.notes,
        confidence=confidence,
    )

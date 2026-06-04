# Adaptive Genome Design System

A tool for designing novel biological sequences by combining functional elements from across the tree of life. Built on top of the UCSC Genome Browser and NCBI databases.

**North Star:** Grow houses that are living organisms — structurally functional, organically shaped, self-repairing, and environmentally adaptive.

---

## The Problem

Nature has already solved most structural and functional challenges we face in architecture:
- Mycelium builds load-bearing networks
- Coral deposits calcium carbonate scaffolding
- Axolotl regenerates severed limbs
- Spider silk outperforms steel by weight
- Bacterial cellulose produces strong, flexible sheets

These solutions exist in separate organisms. This system finds them, extracts them, and combines them into novel sequence designs — adapting the incompatibilities between parts so they work together.

---

## Full System Flow

```
┌─────────────────────────────────────────────────────────────┐
│  1. INPUT                                                   │
│     Natural language description of desired function        │
│     e.g. "grow a load-bearing structure that self-repairs"  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  2. INTERPRETATION                                          │
│     Claude API maps description to:                         │
│     - GO terms (biological process ontology)                │
│     - KEGG pathway IDs                                      │
│     - Target organisms per capability                       │
│     - Gene name conventions (NCBI/UCSC)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  3. DATA RETRIEVAL                          [BUILT]         │
│                                                             │
│  UCSC Genome Browser (ucsc_client.py)                       │
│  ├── 220 genomes, primarily vertebrates                     │
│  ├── Model organisms: yeast, C. elegans, zebrafish, etc.    │
│  ├── Rich annotation tracks (refGene, conservation, ENCODE) │
│  └── Gene coordinates, sequences, regulatory tracks        │
│                                                             │
│  NCBI Entrez (ncbi_client.py)                               │
│  ├── Organisms outside UCSC: mycelium, coral, spider, etc.  │
│  ├── Gene DB + nucleotide DB (fallback for sparse genomes)  │
│  └── Protein sequences, mRNA records, taxonomy             │
│                                                             │
│  Per query, retrieves:                                      │
│  - DNA/mRNA sequences for target genes                      │
│  - Regulatory elements (promoters, enhancers, TF sites)     │
│  - Conservation scores across species                       │
│  - Pathway context (what else this gene talks to)           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  4. DATA MODEL                                              │
│     GenomicPart — unified structure normalizing results     │
│     from UCSC and NCBI into a common format                 │
│                                                             │
│  Fields per part:                                           │
│  - source organism + genome assembly                        │
│  - function / GO term                                       │
│  - sequence (DNA + protein)                                 │
│  - level: gene | regulatory | pathway                       │
│  - codon usage profile                                      │
│  - regulatory signals (promoter strength, TF binding sites) │
│  - known interaction partners                               │
│  - confidence score                                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  5. COMPATIBILITY ANALYSIS                                  │
│     For each pair of parts being combined, check:           │
│                                                             │
│  Gene level                                                 │
│  ├── Codon usage bias (different species prefer diff codons)│
│  ├── GC content alignment                                   │
│  └── Splice site compatibility                              │
│                                                             │
│  Regulatory level                                           │
│  ├── Promoter strength matching                             │
│  ├── Transcription factor binding site compatibility        │
│  ├── Ribosome binding site (RBS) strength                   │
│  └── Terminator signal compatibility                        │
│                                                             │
│  Pathway level                                              │
│  ├── Protein-protein interaction interface alignment        │
│  ├── Metabolic flux balance (does this pathway starve out?) │
│  ├── Signaling crosstalk (do signals conflict or amplify?)  │
│  └── Feedback loop integrity                                │
│                                                             │
│  Output: compatibility score + list of conflicts            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  6. ADAPTIVE ASSEMBLY                                       │
│     Resolve conflicts identified in step 5:                 │
│                                                             │
│  - Codon optimization (rewrite codons for host organism)    │
│  - Regulatory bridge sequences (linkers, insulators)        │
│  - Protein interface adaptation (modify binding domains)    │
│  - Signal balancing (tune promoter/RBS strength)            │
│                                                             │
│  Iterates until all conflicts are resolved or flagged       │
│  as requiring manual review.                                │
│                                                             │
│  Output: assembled novel sequence + modification log        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  7. OUTPUT                                                  │
│  ├── Novel sequence (FASTA format)                          │
│  ├── Pathway map — which organism contributed which part    │
│  ├── Modification log — what was adapted and why            │
│  ├── Confidence scores per element                          │
│  └── Handoff package → AlphaFold / ESMFold for structure    │
└─────────────────────────────────────────────────────────────┘
```

---

## Target Capabilities & Source Organisms

| Desired Function | Source Organisms | Level |
|---|---|---|
| Load-bearing structural scaffold | Mycelium (Ganoderma), coral (Acropora) | Gene + Pathway |
| Shape-directed growth | Arabidopsis (WUS/CLV), zebrafish fin patterning | Regulatory + Pathway |
| Self-repair | Axolotl, planaria (piwi pathway) | Gene + Pathway |
| Cellulose sheet production | Komagataeibacter xylinus (bcsA operon) | Gene |
| Tensile strength | Spider silk (spidroin, Nephila) | Gene |
| Thermal regulation | Desert plant stress genes, endotherms | Regulatory |
| Bioluminescence (signaling) | Firefly (luc), Aliivibrio fischeri | Gene |
| Biomineralization (hardening) | Sea urchin (S. purpuratus), coral | Gene + Pathway |

---

## Data Sources

### Built

| Source | What it covers | Pipeline layer | Client |
|---|---|---|---|
| UCSC Genome Browser | ~220 genomes, vertebrates + model organisms, rich annotation tracks | Retrieval | `retrieval/ucsc_client.py` |
| NCBI Entrez | Bacteria, fungi, plants, invertebrates, sparse-genome fallback via nuccore | Retrieval | `retrieval/ncbi_client.py` |

### Planned — Retrieval Layer (more organisms + sequences)

| Source | What it adds | Priority |
|---|---|---|
| **Ensembl REST API** | Species UCSC doesn't cover, better comparative genomics for coral + some fungi | High |
| **JGI MycoCosm** | Fungal genome portal — Ganoderma, Pleurotus; NCBI is thin on mycelium annotation | High |
| **PhytozomeX (JGI)** | Plant genomes — better Arabidopsis annotation, other structural plants | Medium |
| **WormBase** | Deep C. elegans annotation — richer than UCSC for regeneration/development | Low |
| **FlyBase** | Deep D. melanogaster annotation — richer morphogenesis data than UCSC | Low |

### Planned — Compatibility Layer (function + interactions)

| Source | What it adds | Priority |
|---|---|---|
| **KEGG** | Metabolic + signaling pathway maps — essential for pathway-level compatibility | High |
| **UniProt / Swiss-Prot** | Protein function, subcellular location, known interactions — needed to detect compartment conflicts | High |
| **STRING** | Protein-protein interaction networks — detecting pathway crosstalk between combined parts | High |
| **InterPro / Pfam** | Protein domain families — identifies which domains must be preserved during sequence adaptation | Medium |
| **Rfam** | RNA family database — regulatory RNA elements for environmental sensing switches | Medium |

### Planned — Validation Layer (does the design fold/function?)

| Source | What it adds | Priority |
|---|---|---|
| **AlphaFold DB** | Predicted protein structures for most organisms — check adapted sequences still fold correctly | High |
| **PDB (RCSB)** | Experimental 3D structures — ground truth for protein interfaces pre/post modification | Medium |

### Planned — Synthetic Biology Layer (use characterized parts)

| Source | What it adds | Priority |
|---|---|---|
| **iGEM Parts Registry** | Standardized biological parts with measured promoter/RBS/terminator strengths | Medium |
| **SynBioHub** | Repository of existing chimeric constructs — avoid redesigning what's already been built | Low |

---

## Project Structure

```
adaptive_Automation/
├── retrieval/
│   ├── ucsc_client.py       # UCSC REST API wrapper
│   ├── ncbi_client.py       # NCBI Entrez API wrapper
│   └── species_search.py    # natural language → species + gene targets (next)
├── models/
│   └── genomic_part.py      # unified data model (next)
├── compatibility/
│   ├── codon.py             # codon usage analysis + optimization
│   ├── regulatory.py        # promoter/RBS/TF compatibility
│   └── pathway.py           # protein interface + signaling analysis
├── assembly/
│   └── assembler.py         # adaptive sequence assembly + conflict resolution
├── output/
│   └── formatter.py         # FASTA output, pathway maps, handoff packages
├── main.py                  # end-to-end pipeline entry point
└── README.md
```

---

## Build Order

- [x] UCSC data retrieval client
- [x] NCBI data retrieval client
- [x] Natural language interpretation → species/gene targets
- [x] Unified GenomicPart data model
- [x] Codon compatibility analysis
- [x] Regulatory compatibility analysis
- [x] Pathway compatibility analysis
- [x] Adaptive assembly engine
- [x] Output formatter + AlphaFold handoff
- [x] End-to-end pipeline (`main.py`)

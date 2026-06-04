# Improving AlphaGenome with Natural Genetic Engineering and Distributed Knowledge

**BME 234 — ML for Genomics | Sage Clokey | Spring 2026**

*Connecting AlphaGenome (Avsec et al., Nature 2026) with the BME 129C capstone framework: the genome as a distributed knowledge ledger and Natural Genetic Engineering as the design paradigm.*

---

## The Core Argument

AlphaGenome is a **reader** — it predicts what a genome does. The next step is a **writer** that designs genomes the way life itself designs them. Not by hand-placing base pairs like a machine coder writing hex, but by working *with* the cell's own Natural Genetic Engineering (NGE) toolkit — the same toolkit James Shapiro documented.

Two ideas from the BME 129C capstone directly address AlphaGenome's acknowledged limitations and point toward a genome design system that goes beyond what any existing tool can do:

1. **The genome as distributed knowledge** — not a static blueprint but a decentralized ledger of evolutionary problem-solving
2. **The genome as a blockchain ledger** — an append-mostly, distributed record where transactions (mutations, transfers, rearrangements) are validated and integrated by the cell's own consensus mechanism

---

## Part 1: How Distributed Knowledge Improves AlphaGenome as a Reader

### A. Evolutionary Context as Input, Not Just Sequence

AlphaGenome sees `ATCGATCG...` — raw letters with no history. But convergent evolution shows that the *same* sequence solutions appear independently across lineages separated by hundreds of millions of years (Prestin in bats and dolphins, PEPC in C4 plants). The sequence carries evolutionary information that a purely sequence-based model ignores.

**Improvement:** Incorporate conservation scores, phylogenetic depth, and cross-species ortholog context as additional input channels. The paper acknowledges "species coverage remains limited to human and mouse." The distributed knowledge framework explains *why* that's a limitation — the ledger is written across all three domains of life, and reading only two species is reading two pages of a billions-of-years-long record.

### B. Context-Dependent Variant Interpretation

AlphaGenome predicts a variant's effect as a difference between reference and alternate alleles. But a variant is not inherently pathogenic — it's pathogenic in a context. The same variant might be neutral in one tissue, beneficial in another, and harmful in a third.

AlphaGenome partially captures this through tissue-specific tracks, but doesn't model *why* a variant behaves differently across contexts. The distributed knowledge framework suggests that variant effects should be predicted not just from the local sequence but from the full regulatory neighborhood — the network of enhancers, TF binding sites, and chromatin states that constitute the local "price system" of that genomic region.

This connects directly to AlphaGenome's admitted weakness: "accurately recapitulating tissue-specific patterns across cellular contexts and predicting condition-specific variant effects remain challenging."

### C. Hierarchical Abstraction Layers in the Model

AlphaGenome uses a U-Net with convolutional layers (local patterns) and transformers (long-range). But the biological compiler stack identifies at least six abstraction layers — from nucleotides up through domains, operons, pathways, and functional modules. AlphaGenome's architecture doesn't explicitly represent these intermediate layers.

**Improvement:** A model that learned domain-level, operon-level, and pathway-level representations as explicit intermediate abstractions — rather than leaving the model to discover them implicitly — could more accurately predict how variants propagate effects through the regulatory hierarchy. This is especially relevant for AlphaGenome's weakness on distal regulatory elements (>100 kb), which operate at the pathway/module level, not the nucleotide level.

### D. The Ledger Perspective on Training Data

AlphaGenome trains on the human and mouse reference genomes — essentially two snapshots. The blockchain analogy implies that the *history* of mutations, the record of what was tried and kept versus tried and discarded, contains information that a single snapshot misses.

**Improvement:** Train on population-level variation (like the UK Biobank's 150,000 genomes, which the paper cites but doesn't train on) or on ancestral reconstruction. This lets the model learn not just what the genome *is* but what it *was* — the ledger's transaction history. The paper explicitly names personal genome prediction as "a known weakness." The distributed knowledge framework explains why: a model trained on one snapshot of the ledger can't predict how individual entries (personal genomes) deviate from the consensus.

### E. Mutation as Directed Knowledge, Not Random Noise

Genome-wide analysis shows mutation is structured — CpG sites mutate 10-40x faster, transitions outnumber transversions 2:1, and convergent evolution finds the same molecular solutions across deep time. AlphaGenome treats variants as arbitrary perturbations to score.

**Improvement:** If mutation is directed by distributed knowledge (as the Hayek-inspired framework argues), then the model should weight its predictions by the *likelihood* that a given variant would actually occur in a given context. A variant that the genome's own mutational machinery would never produce is different from one that sits in a CpG hotspot and has been independently discovered by multiple lineages. Integrating mutational context and evolutionary recurrence into variant scoring would make predictions more biologically grounded.

### Summary: Reader Improvements

| AlphaGenome Limitation | BME 129C Concept | Proposed Improvement |
|---|---|---|
| Human + mouse only | Ledger spans all three domains of life | Multi-species training across Archaea, Bacteria, Eukarya |
| Tissue-specific effects poorly captured | Variants aren't diseases — context is | Network-aware, context-conditional variant scoring |
| Distal regulatory elements (>100 kb) weak | Biological compiler stack has 6+ abstraction layers | Explicit hierarchical representations (domain, operon, pathway) |
| No personal genome prediction | Ledger contains transaction history, not just current state | Train on population variation and ancestral sequences |
| Variants scored as arbitrary perturbations | Mutation is directed by distributed knowledge | Weight predictions by mutational context and evolutionary recurrence |

---

## Part 2: From Reading to Writing — Genome Design via Natural Genetic Engineering

### The Design Paradigm Shift

The current synthetic biology approach:

> "I want trait X. Let me find gene Y, codon-optimize it, stick a promoter on it, and force it into a chassis organism."

That's central planning. And it breaks constantly — context-dependence, metabolic burden, silencing, crosstalk — because the cell's distributed knowledge system routes around the foreign imposition.

The NGE-informed approach:

> "I want trait X. What modular operations does life already use to acquire new capabilities? Domain shuffling, regulatory rewiring, mobile element deployment, horizontal transfer. Let me use those same operations — at the right abstraction layer — and let the cell's own distributed knowledge system integrate the result."

### NGE Operations as Design Primitives

Instead of designing at the nucleotide level, design with the operations that Shapiro identified as the cell's own toolkit:

| NGE Operation | What It Does | Design Use |
|---|---|---|
| **Domain shuffling** | Recombines functional protein domains with new linkers | Compose new proteins from proven parts — not residue-by-residue generation, but domain-level assembly |
| **Regulatory element mobilization** | Moves enhancers, promoters, insulators to new contexts | Rewire expression patterns by deploying regulatory modules to new loci |
| **Transposable element insertion** | Deploys mobile genetic elements that carry regulatory or coding cargo | Deliver genetic payloads using the cell's own delivery vehicles |
| **Exon shuffling** | Creates new gene architectures by recombining exons across genes | Generate novel multi-domain proteins with proven exonic building blocks |
| **Whole genome duplication + divergence** | Duplicates everything, then lets copies specialize | Create redundancy that allows one copy to be modified while the other maintains function |
| **Horizontal acquisition** | Imports a proven gene cassette from another organism | Retrieve real genes from across the tree of life (the adaptive genome design system already does this) |

Each operation respects the grammar of the genome. Each one has been validated by billions of years of use. The cell already knows how to integrate results from these operations — because these *are* the operations the cell uses on itself.

### The Biological Compiler Stack

The compiler stack with a concrete implementation path:

```
Layer 6: "Make this plant drought-resistant"           <- Claude (intent parsing)
Layer 5: "Need osmolyte synthesis + stomatal control"   <- Functional module selection
Layer 4: "Betaine pathway + ABA signaling circuit"      <- Pathway-level design
Layer 3: "Import betA operon + rewire SLAC1 promoter"   <- NGE operations
Layer 2: "Domain composition + regulatory element placement" <- Module assembly
Layer 1: "ATCGATCG..."                                  <- Compiled sequence
         |
     AlphaGenome verification                           <- Predict all consequences
```

At each layer, the compiler uses NGE operations — not arbitrary sequence generation. At Layer 3, you're not writing nucleotides; you're saying "import this operon from *Escherichia coli*, deploy it with this regulatory module from *Arabidopsis*, and use this mobile element chassis for integration." At Layer 2, the system assembles the actual sequence using domain-level composition rules. At Layer 1, AlphaGenome verifies that the compiled sequence does what was intended — checking splicing, expression, chromatin state, contact maps, everything.

### AlphaGenome as the Verification Oracle

Before you write, you need to read. AlphaGenome (improved with the distributed knowledge enhancements from Part 1) becomes the verification oracle — you propose a genomic edit, and AlphaGenome predicts the consequences across all modalities simultaneously:

- Does the splice site hold?
- Does chromatin accessibility change?
- Does a distal enhancer get disrupted?
- Do contact maps shift?
- Is expression maintained in the right tissues?

You score the design before it touches a cell. Every proposed NGE operation gets verified against the full multimodal prediction before compilation proceeds to the next layer.

### Why This Is Different From Every Existing Tool

**Existing tools** (BioBricks, Golden Gate, Gibson Assembly frameworks) operate at Layer 1-2 only. You hand-design parts and manually assemble them. There's no compilation. There's no verification oracle that checks all modalities at once. And there's no respect for how the cell will actually respond to the foreign DNA.

**Generative DNA models** (like Evo 2, which AlphaGenome cites) generate sequences but don't understand *why* those sequences work. They've learned statistical patterns but not the grammar. They can write sentences that look right but don't know the rules of composition.

**The NGE-informed system** would be the first to:

1. Parse intent at natural language level (Claude)
2. Compile down through biologically validated abstraction layers (the compiler stack)
3. Use NGE operations as the design primitives at each layer (Shapiro's toolkit)
4. Verify the compiled result with a multimodal prediction oracle (AlphaGenome)
5. Respect the cell's distributed knowledge system instead of overriding it

---

## Part 3: The Ledger Writes Itself

In a blockchain, you don't write entries by editing the chain directly. You submit transactions that the network validates and integrates according to its consensus rules. The genome works the same way. You don't write base pairs into the genome — you submit genetic material (via NGE operations: transposition, recombination, horizontal transfer) and the cell's own machinery validates and integrates it according to its rules (chromatin remodeling, DNA repair, regulatory feedback).

A genome design system built on this principle wouldn't be a genome *editor*. It would be a genome *transactor* — submitting biologically legible transactions that the cell can validate and integrate using its own 4-billion-year-old consensus mechanism. The cell does the final integration. You provide the transaction. AlphaGenome predicts whether the network will accept it.

That's the Living Age approach to genome design: **not building genomes like machines, but proposing adaptations the way life proposes them — and letting the distributed knowledge system do what it already knows how to do.**

---

## References

- Avsec, Z. et al. (2026). Advancing regulatory variant effect prediction with AlphaGenome. *Nature*, 649, 1206-1218.
- Shapiro, J.A. (2013). Constraint and Opportunity in Genome Innovation. *RNA Biology*, 11(3), 1-11.
- Hayek, F.A. (1945). The Use of Knowledge in Society. *American Economic Review*, 35(4), 519-530.
- Brixi, G. et al. (2025). Genome modeling and design across all domains of life with Evo 2. *bioRxiv*.
- Woese, C.R. (2004). A New Biology for a New Century. *Microbiology and Molecular Biology Reviews*, 68(2), 173-186.

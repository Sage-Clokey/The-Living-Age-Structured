# Project Proposal: Domain Grammar as a Predictive Layer Beyond Protein Language Models

**Course:** BME 234 — Machine Learning and AI in Genomics
**Student:** Sage Clokey
**Date:** May 2026

---

## 1. Problem Statement

### 1.1 The Knowledge Problem in Biology

In 1945, Friedrich Hayek posed what he called "the economic problem of society" — not how to allocate resources given complete knowledge, but how to coordinate action when the relevant knowledge is dispersed across millions of actors, each of whom holds only fragments. His answer was the price system: a distributed information network where each voluntary exchange encodes local knowledge into a signal (price) that propagates through the entire system without any actor needing to understand the whole (Hayek, 1945).

Biology faces an identical problem. A cell coordinates thousands of molecular interactions without a central controller. No single gene "knows" the state of the whole organism. Instead, proteins, metabolites, and regulatory molecules carry local information — binding affinities, expression levels, post-translational modifications — that propagates through interaction networks. The cell is a distributed economy, and its molecular interactions are its price system.

Current protein language models like ESM-3 have learned to predict the vocabulary of this system — individual protein sequences — with remarkable accuracy. But they have not learned the grammar. They treat each protein as an isolated string of residues, stripped of the compositional structure, genomic context, and network relationships that give it meaning. This is equivalent to learning every word in a language without understanding syntax, and it reflects a deeper failure: treating the parts catalog as if it were the system.

### 1.2 Shapiro and the Grammar of Genome Innovation

James Shapiro's 2013 paper "Constraint and Opportunity in Genome Innovation," written as a tribute to Carl Woese, fundamentally reframes how genomes change in evolution. Shapiro demonstrates that genome innovation is not driven by random point mutations filtered by selection — the conventional neo-Darwinian model — but by **natural genetic engineering (NGE)**: a suite of cell-directed biochemical processes that restructure DNA at the domain, gene, and network level.

Shapiro identifies three major mechanisms of genome innovation:

1. **Symbiogenesis** — Cell mergers that combine entire genomic compartments. The mitochondrion and chloroplast are proven cases. Eukaryotic cells are themselves fusion products of Archaea and Bacteria, combining distinct replication, transcription, and membrane systems into a novel configuration.

2. **Horizontal DNA transfer** — Active exchange of coding sequences across all three domains of life. Not limited to prokaryotes: plant parasitic nematodes acquired digestive enzymes from bacteria and fungi; vertebrate immune system components (RAG1/2) derive from viral integrases; retroviral sequences gave rise to the syncytins essential for placental evolution. DNA flows across the tree of life because the underlying language is universal.

3. **Intracellular natural genetic engineering** — The cell's own toolkit for restructuring its genome: transposons, retrotransposons, domain shuffling, exon creation, reverse transcription, and targeted mutagenesis. Two-thirds of the human genome consists of mobile elements. These are not junk — they are the primary engine of regulatory network rewiring, responsible for over 200,000 of the positively selected DNA elements distinguishing placentals from marsupials.

The critical insight is that these processes are **not random**. They are activated by stress, targeted by molecular interactions, and biased by intracellular signaling. Different stresses produce different spectra of genome changes. The cell is not a passive recipient of accidental mutations — it is an active participant in its own evolution, restructuring its genome using sophisticated molecular tools in response to environmental signals.

Woese's complementary insight was the distinction between **core and peripheral** cellular systems. Core systems — the ribosome, transcription machinery, DNA replication — are deeply conserved, tightly coupled, and resistant to horizontal transfer. Peripheral systems — metabolic enzymes, surface proteins, regulatory elements — are modular, loosely coupled, and freely exchanged between organisms. This is Hayek's distinction between institutional infrastructure (the rules of the game) and entrepreneurial action (the players within the rules), expressed in molecular terms.

### 1.3 The Gap in Current Models

These insights from Shapiro and Woese reveal what protein language models are missing:

- **Proteins evolve primarily through the recombination of functional domains** — not individual residue substitutions. Domain shuffling, exon creation, and cDNA fusion are the generative grammar of protein evolution. A model that predicts residues without understanding domain compositionality is learning letters without learning words.

- **DNA sequences are actively exchanged across all three domains of life.** The genetic code is universal, and horizontal transfer is pervasive. A protein's function in a recipient organism depends on its new genomic context, not just its donor sequence. A model that ignores evolutionary origin and genomic neighborhood is discarding the pragmatic context that determines meaning.

- **Genome innovation is stress-directed and context-dependent.** The spectrum of changes a cell produces depends on the signals it receives. A model that generates variation uniformly, without conditioning on cellular state, is ignoring the most biologically relevant axis of variation.

This suggests that protein function prediction should benefit from a **domain-level grammar** — the ordered composition of functional modules — and from **cross-domain contextual information** that sequence-only models cannot capture. This project tests that hypothesis directly.

## 2. Hypothesis

A model that incorporates protein domain architecture and genomic context will outperform sequence-embedding-only baselines for protein function prediction (Gene Ontology term classification), particularly for horizontally transferred genes whose function in a recipient organism depends on context rather than sequence identity alone.

## 3. Approach

### 3.1 Data Collection

| Data | Source | Description |
|------|--------|-------------|
| Protein sequences | UniProt/Swiss-Prot | ~570K reviewed, annotated proteins across all three domains of life |
| Domain annotations | Pfam / InterPro | Ordered domain architectures per protein |
| Sequence embeddings | ESM-3 (pretrained) | Per-protein embeddings from HuggingFace |
| Function labels | Gene Ontology (GO) | Molecular function and biological process terms via UniProt mapping |
| Taxonomic origin | UniProt taxonomy | Kingdom-level classification (Archaea, Bacteria, Eukarya) |
| Horizontal transfer annotations | HGT-DB, literature | Known horizontally transferred genes |
| Genomic context | KEGG, Ensembl | Operon membership, pathway assignment |

### 3.2 Feature Representations

Three representations will be constructed for each protein:

1. **Sequence embedding (baseline):** Mean-pooled ESM-3 per-residue embeddings, producing a fixed-length vector per protein. No domain or context information.

2. **Domain architecture encoding:** Each protein is represented as an ordered sequence of Pfam domain IDs — analogous to a sentence of words. These are embedded using either a learned embedding layer or a simple bag-of-domains vector with positional encoding to capture domain order.

3. **Genomic context features:** Kingdom of origin (one-hot), operon membership (binary), pathway assignment (KEGG ID), and horizontal transfer flag (binary). These are concatenated as a context vector.

### 3.3 Models

Three models will be compared on multi-label GO term prediction:

| Model | Input | Architecture |
|-------|-------|-------------|
| **A — Sequence only** | ESM-3 embedding | MLP (2 hidden layers) |
| **B — Domain grammar only** | Domain architecture + context features | MLP or lightweight Transformer over domain sequence |
| **C — Combined** | ESM-3 embedding + domain architecture + context | MLP with concatenated features |

All models will be trained with binary cross-entropy loss for multi-label classification of GO terms. The GO term set will be filtered to terms with sufficient representation (>50 annotated proteins).

### 3.4 Evaluation

- **Primary metric:** Protein-centric F_max (maximum F1 across thresholds), following CAFA evaluation standards
- **Secondary metrics:** Area under precision-recall curve (AUPR), subset accuracy
- **Stratified analysis:**
  - Performance on vertically inherited vs. horizontally transferred genes
  - Performance across kingdoms (Archaea, Bacteria, Eukarya)
  - Performance on single-domain vs. multi-domain proteins

### 3.5 Interpretability Analysis

Beyond raw accuracy, the model will be interrogated for biological insight:

- **Learned domain co-occurrence patterns:** Which domain combinations does the model treat as syntactically valid? Do these match known biological domain pairings?
- **Cross-domain transfer cases:** Identify examples where Model A (sequence only) mispredicts function but Model C (with context) succeeds — particularly for horizontally transferred genes where sequence similarity to the donor organism misleads the sequence-only model.
- **Kingdom-specific grammar:** Do domain composition rules differ across Archaea, Bacteria, and Eukarya, and does the model capture Woese's core/periphery distinction (core machinery conserved, peripheral functions variable)?

## 4. Theoretical Framework: The Cell as a Distributed Economy

### 4.1 Hayek's Price System and Molecular Signaling

Hayek's central argument was not merely that markets work — it was that **no alternative can work** for coordinating dispersed knowledge. The information relevant to economic decisions — the particular circumstances of time and place, the tacit knowledge of the shipper who knows of unused cargo space, the entrepreneur who sees an unmet need — is by its nature distributed, fragmented, and perishable. It cannot be collected, centralized, and processed by any single authority. The price system solves this problem by encoding local knowledge into signals (prices) that propagate through the network, allowing millions of actors to coordinate without any of them needing to understand the whole.

The cell faces the same coordination problem at the molecular level. No single molecule "knows" the state of the cell. Instead, binding affinities function as prices — they encode the local availability and demand for molecular partners. Expression levels function as supply signals. Post-translational modifications function as real-time price adjustments in response to changing conditions. The protein interaction network is the marketplace where these signals propagate and coordinate cellular behavior.

This is not metaphor. The mathematical structure is the same: distributed agents making local decisions based on signal gradients, producing emergent order without central direction. And just as Hayek showed that distorting price signals (through credit expansion, price controls, or central planning) leads to malinvestment and systemic failure, distorting molecular signals — through oncogenic mutations, constitutive receptor activation, or synthetic overexpression — leads to the biological equivalent: cancer, autoimmunity, developmental failure.

### 4.2 Shapiro's Natural Genetic Engineering as Entrepreneurial Innovation

If Hayek explains how the cell coordinates, Shapiro explains how it innovates. In Hayek's framework, economic progress comes not from central planning but from entrepreneurial action — individuals recombining existing resources in novel ways, testing them against the market, and scaling what works. The entrepreneur does not invent atoms; he rearranges what exists into new configurations that serve unmet needs.

Shapiro's natural genetic engineering is the molecular equivalent. The cell does not innovate by waiting for random point mutations — the neo-Darwinian equivalent of a central lottery. Instead, it actively restructures its genome:

- **Domain shuffling** is entrepreneurial recombination — taking established functional modules and combining them into novel proteins, just as an entrepreneur combines existing technologies into a new product.
- **Horizontal gene transfer** is trade — importing proven solutions from other organisms rather than reinventing them internally, just as economies grow by importing goods they cannot efficiently produce domestically.
- **Mobile elements rewiring regulatory networks** are infrastructure development — creating new coordination systems that allow existing genes to be expressed in new patterns, just as new communication networks allow existing businesses to reach new markets.
- **Stress-directed mutagenesis** is market-responsive innovation — the cell increases its rate and specificity of genome restructuring precisely when conditions demand adaptation, just as economic innovation accelerates during periods of creative destruction.

The conventional model — random mutation plus natural selection — is the biological equivalent of central planning theory: it assumes that useful innovations arise by accident and are selected by an external filter (death). But selection is not filtration by death. It is distributed choice based on distributed knowledge — trial and error directed by information, where the entrepreneurs do not die but pivot. Shapiro's evidence shows that the cell is an active innovator, using sophisticated molecular tools to generate non-random, context-sensitive genomic changes. The variance is not random. It is directed by the environment and by what is around — by distributed knowledge, just as the variance of the market is directed by the distributed knowledge of prices. The cell is not a lottery ticket. It is an entrepreneur.

### 4.3 Woese's Core/Periphery as Kernel vs. Userspace

Woese's distinction between core and peripheral cellular systems maps directly onto both Hayek and software architecture:

- **Core systems** (ribosome, DNA replication, transcription) are the institutional infrastructure — the rules of the game that must remain stable for the rest of the system to function. They are deeply conserved, tightly coupled, and resistant to modification. In computing terms, this is the kernel. In Hayek's terms, this is the rule of law — the framework within which entrepreneurial action occurs.

- **Peripheral systems** (metabolic enzymes, surface proteins, regulatory elements) are the entrepreneurial layer — modular, loosely coupled, freely exchangeable, and subject to rapid innovation through horizontal transfer and domain shuffling. This is userspace. This is the market.

A model that captures this distinction — that learns which molecular components are core infrastructure and which are entrepreneurial modules available for recombination — has learned something fundamental about how living systems are organized. This project tests whether that organizational grammar is computationally detectable.

### 4.4 The Disease Is Not the Variant

The conventional framing of genomic medicine asks: which variants cause disease? This question contains an assumption — that deviation from a reference genome is pathological. But this is the same category error as eugenics: the belief that there is one Sacred Timeline, one ideal sequence, and everything else is a defect to be corrected.

An elephant is not diseased because it cannot climb a tree. A variant is not a disease — it is a difference. The question should not be "which variants are broken?" but "what does each variant need to thrive?" This is the framing of companies like Nucleogenex, which sequence individual genomes not to identify what is wrong, but to identify what nutrients each variant needs to function at its best. The variant is not the disease. The disease is when you fail to maintain what exists — when you withhold from a living system what it needs to express its particular form.

This reframes the entire logic of genomic medicine. If disease is not intrinsic to the variant but emerges from a mismatch between the variant and its environment, then the problem is not variation — the problem is context. And this is precisely what the domain grammar model captures: function is not determined by sequence alone, but by the context in which that sequence operates.

Selection, properly understood, is not filtration by death. In a distributed economy, entrepreneurs do not die when they make mistakes — they pivot. They try something else. The biological equivalent is not the mass extinction that kills the unfit, but the distributed knowledge that allows each agent to find its niche. Usual, timely death is apoptosis — a deliberate, orderly process that serves the whole. Premature death — the mass die-off, the systemic failure — is what happens when distributed knowledge is replaced by central planning. When false signals (oncogenic mutations, constitutive activation, credit expansion) override the local knowledge of each agent, the result is malinvestment at the molecular level: uncontrolled proliferation, resource misallocation, systemic collapse.

The disease is not the variation. The disease is the central planning. The disease is when the distributed price system of the cell is overridden by a false signal that claims authority it does not have. Cancer is not a variant — it is a coup. It is the molecular equivalent of the state: a local agent that stops responding to distributed signals and begins imposing its will on the whole.

If DNA is a language, then the cell speaks it — and can write in it. The cell is not a passive substrate waiting for random mutations to be filtered by an external selector. It is a knowing agent, reading its environment and restructuring its own genome in response. The knowledge is distributed across the sequence, across the interaction network, across the regulatory architecture. No central authority holds it. No external filter creates it. It emerges from the living system itself, just as market order emerges from the voluntary actions of millions of individuals, each acting on local knowledge that no planner could possess.

This is why domain grammar matters for medicine, not only for function prediction. If we learn the compositional rules by which proteins are assembled — the syntax of molecular innovation — we learn how the cell writes. And if we understand how the cell writes, we can learn to read what it is saying: not "this variant is broken," but "this variant needs something specific to thrive." The grammar is not a standard to enforce. It is a language to understand.

### 4.5 Implications for Machine Learning

If this framework is correct, then protein function prediction is not fundamentally a sequence problem — it is a **context problem**. The same domain in a different genomic neighborhood, regulatory context, or organismal background can have a different function, just as the same word in a different sentence has a different meaning. Models that ignore context and treat proteins as isolated sequences are committing Hayek's fatal conceit: assuming that the relevant information can be captured in the parts alone, without the relational structure that gives them meaning.

This project tests the foundational claim: **domain grammar and genomic context carry predictive information that sequence-only models cannot capture.** If they do, this validates the broader vision — that biological design can be formalized through abstraction layers analogous to the computing stack, from nucleotides (hardware) through domains (machine code) through pathways (systems language) to phenotypes (high-level language), with each layer compiling down to the one below. This proof of concept tests the first layer transition in that stack.

## 5. Timeline

| Week | Task |
|------|------|
| 1 (Days 1–3) | Data pipeline: download Swiss-Prot sequences, Pfam annotations, GO labels, taxonomic metadata. Build unified dataset with domain architectures per protein. |
| 1 (Days 4–7) | Feature engineering: generate ESM-3 embeddings (batched on GPU), encode domain architectures, construct context feature vectors. Train/test split stratified by kingdom. |
| 2 (Days 8–11) | Model training: train Models A, B, and C. Hyperparameter tuning via cross-validation. |
| 2 (Days 12–14) | Evaluation and analysis: compute F_max and AUPR. Stratified analysis on HGT genes. Interpretability: extract learned domain grammar, identify context-dependent prediction cases. Write up results. |

## 6. Expected Outcomes

1. **Model C (combined) outperforms Model A (sequence only)** on GO function prediction, demonstrating that domain grammar and genomic context carry information not captured by sequence embeddings alone.

2. **Model B (domain grammar only) achieves non-trivial performance** using zero sequence information, demonstrating that domain-level compositionality is independently predictive — biology has syntax, not just vocabulary.

3. **Horizontal transfer genes show the largest improvement** from context features, because their function in the recipient organism depends on the new genomic neighborhood, not the donor sequence identity.

4. **Interpretable domain co-occurrence rules** emerge from the trained model, validating that a learnable grammar exists at the domain level.

## 7. Tools and Resources

- **Python** (NumPy, pandas, scikit-learn, PyTorch)
- **ESM-3** via HuggingFace Transformers (pretrained, inference only)
- **UniProt REST API** for sequence and annotation retrieval
- **InterPro API** for domain architecture queries
- **Compute:** Google Colab Pro or UCSC Hummingbird cluster

## 8. References

1. Shapiro, J.A. (2013). "Constraint and Opportunity in Genome Innovation." *RNA Biology*, 11(3), 1–11.
2. Woese, C.R. (2004). "A New Biology for a New Century." *Microbiology and Molecular Biology Reviews*, 68(2), 173–186.
3. Hayes, T. et al. (2024). "Simulating 500 Million Years of Evolution with a Language Model." *Science*, 386(6725).
4. Hayek, F.A. (1945). "The Use of Knowledge in Society." *American Economic Review*, 35(4), 519–530.
5. Radivojac, P. et al. (2013). "A Large-Scale Evaluation of Computational Protein Function Prediction." *Nature Methods*, 10(3), 221–227.
6. Mistry, J. et al. (2021). "Pfam: The Protein Families Database in 2021." *Nucleic Acids Research*, 49(D1), D412–D419.
7. Soucy, S.M., Huang, J., & Gogarten, J.P. (2015). "Horizontal Gene Transfer: Building the Web of Life." *Nature Reviews Genetics*, 16(8), 472–482.

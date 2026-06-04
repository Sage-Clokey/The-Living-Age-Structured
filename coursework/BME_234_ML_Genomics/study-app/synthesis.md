# BME 234 Concepts → Living Works by the Word

## How Every Course Topic Feeds the Living Architecture System

---

## 1. Hidden Markov Models → Gene Finding & Chromatin State Annotation

**Course concept:** HMMs decode hidden biological states from observable sequences — Viterbi finds the best path, Forward-Backward computes posterior probabilities, Baum-Welch learns parameters from unlabeled data.

**Application to the project:**

The adaptive_Automation system retrieves genomic parts from 220+ organisms (UCSC, NCBI). But raw genome sequence is meaningless without annotation — you need to know *where genes begin and end*, *where regulatory elements sit*, and *what chromatin state a region occupies*.

- **Gene finding (GENSCAN-style HMMs):** When pulling a gene from an uncharacterized fungal genome (e.g. Ganoderma lucidum cross-linking enzymes), the system needs to identify exon-intron boundaries. HMMs with states for exon/intron/UTR/intergenic do exactly this — the Viterbi algorithm traces the most probable gene structure through the sequence.

- **ChromHMM for regulatory element discovery:** Phase 2 adds regulatory layer design using Enformer. But first you need to *find* promoters, enhancers, and silencers in source organisms. ChromHMM learns chromatin states from histone modification data — directly feeding the regulatory compatibility module that flags conflicts when you combine fungal promoters with plant coding sequences.

- **CpG island detection for methylation-aware design:** The codon optimization layer already handles synonymous codon choice, but methylation can silence a transgene. An HMM distinguishing CpG-island vs non-CpG-island regions helps predict whether a designed sequence will be epigenetically silenced in its target chassis.

**Key insight:** The Markov assumption — future depends only on present state — maps directly to how the assembly engine processes sequence windows. Compatibility is assessed position by position, just like an HMM scanning a genome.

---

## 2. Markov Chains & Log Odds Ratios → Sequence Classification & Codon Dialect

**Course concept:** k-mer Markov models capture the statistical grammar of DNA sequences. Log odds ratios compare how well a sequence fits one model versus another.

**Application to the project:**

The compatibility/codon.py module already computes CAI (Codon Adaptation Index) — but this is essentially a log odds ratio:

```
log P(sequence | target organism codon model) / P(sequence | source organism codon model)
```

A high ratio means the sequence "speaks the dialect" of the target organism. The k-mer Markov chain framework from HW1 generalizes this:

- **Dinucleotide bias detection (k=2):** Different organisms have different dinucleotide frequencies (CpG suppression in vertebrates, GC-rich fungi). The k=2 Markov model captures this — and HW1 showed the massive jump from k=1 to k=2 proves dinucleotide dependencies carry most discriminative signal.

- **Promoter sequence classification:** The system retrieves regulatory elements from multiple kingdoms. A Markov chain trained on *functional* promoters vs random sequence can score whether a candidate regulatory element actually looks like a real promoter in its target context.

- **Codon dialect as a language model:** Each organism's codon usage is a probability distribution over synonymous codons. The RSCU tables in `compatibility/codon.py` are exactly the emission probabilities of a biological language model. Codon optimization is *translation between dialects* — rewriting a sentence so it sounds natural to the target organism's ribosomes.

**Key insight:** The entire foundation of the Living Works system — retrieving parts from diverse organisms and making them compatible — is a sequence classification and adaptation problem. Markov models are the simplest version of this; language models (Topic 8) are the most powerful.

---

## 3. Logistic Regression & GWAS → Variant Effect Scoring & Design Validation

**Course concept:** Logistic regression tests whether a genetic variant associates with a phenotype. GWAS scans millions of variants, correcting for multiple testing and LD structure.

**Application to the project:**

When the system designs chimeric sequences, every position is effectively a "variant" relative to the wild-type source. The question becomes: *will this change break function?*

- **Variant effect prediction for designed mutations:** Phase 1 generates candidate proteins via ESM-3, then back-translates to DNA with codon optimization. Each synonymous codon swap is a designed variant. Logistic regression models (trained on functional vs non-functional variants) can score whether a specific change is likely to disrupt splicing signals, mRNA stability, or translational efficiency.

- **eQTL logic for expression prediction:** The system combines regulatory elements from one organism with coding sequences from another. eQTL-style thinking asks: "does this regulatory variant change expression?" The regulatory compatibility module in Phase 2 (Enformer integration) is essentially computing eQTL effects for designed regulatory variants.

- **Multiple testing awareness:** When scoring compatibility across thousands of positions in an assembled sequence, you're performing thousands of statistical tests. The Bonferroni/BH framework prevents the system from flagging too many false incompatibilities — or missing real ones.

- **Odds ratios as effect sizes:** The pathway compatibility module (`compatibility/pathway.py`) assesses whether combining metabolic pathways will create flux imbalances. Each interaction is scored with an effect size — directly analogous to odds ratios in GWAS — and only interactions exceeding a threshold trigger resolution.

**Key insight:** GWAS finds what nature *already* did (natural variants → phenotypes). The Living Works system reverses this: design a desired phenotype → predict which sequence changes achieve it without breaking other functions.

---

## 4. Decision Trees & Random Forests → Variant Classification & Part Selection

**Course concept:** Decision trees recursively split data on the most informative features (information gain/Gini). Random forests average many decorrelated trees for robust prediction. SVMs find maximum-margin boundaries in feature space.

**Application to the project:**

The compatibility engine makes binary decisions at every step: compatible or incompatible, resolve or flag. This is a classification problem.

- **Part selection as a decision tree:** When the species_search module maps a function ("structural strength") to candidate organisms, it implicitly walks a decision tree:
  - Is the function structural? → Yes
  - Is it load-bearing? → Split on material type (chitin vs cellulose vs mineral)
  - Target environment? → Split on temperature, moisture, pH tolerance
  - Each leaf = a recommended organism + gene

- **Random forest for multi-criteria compatibility scoring:** The assembly engine currently uses rule-based heuristics. A random forest trained on successful vs failed synthetic biology constructs (from iGEM registry + literature) could score: given codon usage difference, regulatory mismatch score, protein domain compatibility, and metabolic impact — what's the probability this design works?

- **SVM for protein function classification:** When ESM-3 generates candidate proteins, you need to verify they actually have the desired function. An SVM with an RBF kernel on protein feature embeddings (from ESM-2) can classify candidates as functional/non-functional before expensive wet-lab testing.

- **CADD-style scoring for designed sequences:** CADD integrates 60+ annotations into a single deleteriousness score. The Living Works system needs an analogous "designability score" integrating: codon adaptation, regulatory context, structural prediction confidence, pathway compatibility, and evolutionary precedent. A random forest or gradient-boosted tree over these features would produce a single GO/NO-GO score per candidate design.

**Key insight:** The system already has the *features* (CAI scores, regulatory flags, pathway metrics). What it needs is a *trained classifier* that weights them correctly. Decision trees and random forests are the natural first step before deep learning — interpretable, fast, and trainable on small datasets from early experiments.

---

## 5. CNNs & Sequence-to-Function → Regulatory Design & Expression Prediction

**Course concept:** CNNs learn local sequence patterns (motifs) from one-hot encoded DNA. DeepSEA predicts chromatin features from 1000bp. Enformer predicts quantitative expression from 200kb context. In silico mutagenesis scores variant effects.

**Application to the project:**

This is **Phase 2** of the roadmap — the regulatory layer. Currently the system designs *what* protein to make, but not *when, where, or how much* to express it. CNNs solve this:

- **Enformer for expression prediction:** The Phase 2 plan explicitly includes Enformer integration. Given a designed promoter + coding sequence + 3'UTR + surrounding context, Enformer predicts the expression level across cell types and conditions. This answers: "will my cross-linking enzyme actually be expressed at useful levels in Ganoderma?"

- **DeepSEA-style chromatin prediction:** Before inserting a transgene, predict whether the target locus has open chromatin (accessible for transcription). If the insertion site is in a repressed chromatin state, the gene won't be expressed regardless of promoter strength.

- **Motif-aware regulatory design:** First-layer CNN filters learn transcription factor binding motifs. The system can:
  1. Learn what motifs drive expression in the target organism
  2. Include those motifs in designed regulatory sequences
  3. Exclude motifs that recruit repressors

- **In silico mutagenesis for design optimization:** Compare Enformer predictions for candidate regulatory sequences:
  - Design A (with fungal TATA box): predicted expression = 12 TPM
  - Design B (with modified TATA + upstream enhancer): predicted expression = 85 TPM
  - Choose B without ever entering a lab

- **CNN filters as a regulatory grammar:** The deeper layers of sequence-to-function models learn *combinations* of motifs — the grammar of gene regulation. This is exactly what Phase 2 needs: not just "is there a promoter here?" but "will this combination of regulatory elements produce the right expression pattern for living architecture?"

**Key insight:** The Living Works system's Phase 2 is literally building a regulatory CNN pipeline. The course teaches exactly how these models work — from one-hot encoding (the input format) through convolution (pattern detection) to expression prediction (the output). DeepSEA and Enformer are not abstract — they're planned dependencies.

---

## 6. Language Models (BERT/Transformers) → The English-to-Protein Bridge

**Course concept:** Transformers use self-attention to capture long-range dependencies. BERT-style masked language modeling learns contextual representations from unlabeled sequences. ESM learns protein structure/function from sequence alone. AlphaFold predicts 3D structure.

**Application to the project:**

This is **the entire foundation of Phase 1.** The bridge from English to functional protein uses three language models in sequence:

### Claude (Natural Language → Biological Specification)
- Input: "Design a protein that cross-links fungal cell walls under mechanical stress"
- Self-attention captures relationships between concepts: "cross-links" relates to "cell walls," "mechanical stress" relates to "under" (conditional expression)
- Output: GO terms, target organism, desired properties, expression conditions
- Claude *is* a transformer. Understanding how attention works explains why it can reason about biology.

### ESM-3 (Biological Specification → Protein Sequence)
- Input: Function annotation tokens (from GO terms) + organism context
- Masked language modeling trained on 250M protein sequences learned: evolutionary constraints, structural requirements, functional motifs
- Generates amino acid sequences conditioned on desired function
- **Attention heads correspond to 3D contacts** — the model implicitly knows structure from sequence alone
- This replaces months of manual protein engineering with seconds of conditional generation

### AlphaFold (Protein Sequence → 3D Structure Validation)
- After ESM-3 generates candidates, AlphaFold predicts their 3D structure
- pLDDT confidence scores tell the system which candidates fold reliably
- Evoformer jointly processes MSA + pair representations → captures co-evolutionary signal
- If a candidate has pLDDT < 70, reject it before wasting lab resources

### Genomic Language Models (DNA Sequence → Regulatory Grammar)
- DNABERT / Nucleotide Transformer understand the regulatory code
- Zero-shot variant effect: compare P(ref) vs P(alt) in pretrained model
- Phase 2 uses these to verify that designed regulatory sequences follow the "grammar" of their target genome
- Like spellcheck for synthetic biology — does this promoter "read" correctly to the cell's machinery?

### The Back-Translation Step
- ESM-3 outputs amino acid sequences
- Back-translation to DNA uses the organism-specific RSCU tables (codon dialect)
- This is **transfer between biological languages:** protein language → DNA language → organism-specific dialect
- The transformer framework unifies all of these as different "vocabularies" over the same fundamental biological grammar

**Key insight:** The entire Phase 1 pipeline is a *language model pipeline.* Claude speaks English→biology. ESM-3 speaks biology→protein. Codon optimization speaks protein→DNA dialect. AlphaFold reads protein→structure. The course's Topic 8 teaches the exact architecture underlying every step of the system's core inference chain.

---

## 7. Integration: The Full Stack

| BME 234 Topic | Living Works Layer | What It Does |
|---|---|---|
| HMMs | Retrieval + Annotation | Find genes and regulatory elements in source genomes |
| Markov Chains | Compatibility/Codon | Score and optimize codon dialect fitness |
| Logistic Regression | Compatibility/Pathway | Score variant effects and pathway impacts |
| Decision Trees/RF | Assembly Engine | Classify designs as viable/non-viable, select resolution strategies |
| CNNs | Phase 2: Regulatory Layer | Predict expression levels, optimize regulatory sequences |
| Language Models | Phase 1: English→Protein Bridge | Generate functional proteins from natural language descriptions |
| AlphaFold | Phase 1: Structure Validation | Verify generated proteins fold correctly |

---

## 8. The Philosophical Connection

The course teaches machines to *read* biological sequence — to decode the language that cells already speak. Every algorithm is an attempt to understand what evolution wrote over 4 billion years.

The Living Works project takes the next step: not just reading, but *writing* in that language. Not replacing evolution's grammar, but becoming fluent enough to compose new sentences that follow its rules.

- HMMs decode what's hidden → We decode organism logic before designing
- GWAS finds what variants do → We design variants that do what we want
- CNNs learn regulatory grammar → We write new regulatory programs
- Language models generate in context → We generate proteins that fit their biological sentence

The Markov assumption says the future depends only on the present state. The Living Age says: understand the present state of biology deeply enough, and you can grow the future.

**Every model in this course is a tool for reading life's source code. The Living Works system uses them to write the next chapter.**

---

*Written April 2026 — connecting BME 234 (ML & AI in Genomics) coursework to the adaptive_Automation genome design system and the Living Works by the Word initiative.*

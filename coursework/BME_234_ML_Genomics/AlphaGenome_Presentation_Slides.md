# AlphaGenome Presentation
## BME 234 — ML and AI in Genomics
### Presenters: Zia Truong & Sage Clokey | June 2, 2026

---

## Slide 1: Title

**Advancing Regulatory Variant Effect Prediction with AlphaGenome**

Avsec, Latysheva, Cheng, Novati, Taylor, Ward, Bycroft et al.
Google DeepMind — *Nature* (2026)

Presented by: Zia Truong & Sage Clokey

---

## Slide 2: The Problem — Non-Coding Variants

- >98% of human genetic variation is **non-coding**
- These variants can alter:
  - Chromatin accessibility
  - Histone modifications
  - 3D chromatin conformation
  - Gene expression levels
  - Splicing patterns
- Experimental characterization of every variant is intractable
- We need computational models that predict variant effects from DNA sequence alone

**Key question:** Can we build one model that captures all of these effects simultaneously?

---

## Slide 3: Prior Work — The Two Trade-Offs

**Trade-off 1: Context length vs. resolution**

| Model | Input Length | Output Resolution |
|-------|------------|-------------------|
| SpliceAI / BPNet | ~10 kb | 1 bp |
| Enformer | ~200 kb | 128 bp |
| Borzoi | ~500 kb | 32 bp |
| **AlphaGenome** | **1 Mb** | **1 bp** |

Short-context models miss distal enhancers. Long-context models blur fine features like splice sites.

**Trade-off 2: Multimodal vs. specialized**

- Specialized models (SpliceAI, ChromBPNet, Orca) excel at one task but miss cross-modal effects
- Multimodal models (Enformer, Borzoi) cover more but lag behind specialists
- **AlphaGenome unifies both** — long context, base resolution, all modalities

---

## Slide 4: AlphaGenome Overview

> **[Show Figure 1a]**

**Input:** 1 Mb of DNA sequence + species identity (human or mouse)

**Output:** 5,930 human genome tracks across 11 modalities:

| Modality | Tracks (H/M) | Resolution |
|----------|-------------|------------|
| RNA-seq | 667 / 173 | 1 bp |
| CAGE | 546 / 188 | 1 bp |
| PRO-cap | 12 / 0 | 1 bp |
| DNase | 305 / 67 | 1 bp |
| ATAC | 167 / 18 | 1 bp |
| Histone ChIP-seq | 1,116 / 183 | 128 bp |
| TF binding ChIP-seq | 1,617 / 127 | 128 bp |
| Splice sites | 4 / 4 | 1 bp |
| Splice junctions | 734 / 180 | 1 bp |
| Splice site usage | 734 / 180 | 1 bp |
| Contact maps | 28 / 8 | 2,048 bp |

---

## Slide 5: Model Architecture

> **[Show Extended Data Fig. 1 or simplified diagram from Fig. 1a]**

**U-Net-style backbone** with three main components:

1. **Encoder (Downsampling)**
   - Convolutional blocks detect local sequence patterns (motifs)
   - Max pooling progressively reduces resolution: 1 bp → 2 bp → 4 bp → ... → 128 bp
   - Captures fine-grained features like splice sites and TF binding motifs

2. **Transformer Tower (128 bp resolution)**
   - Self-attention across the full sequence
   - Models long-range dependencies (enhancer-promoter interactions up to 1 Mb apart)
   - Also generates 2D pairwise representations for contact map prediction
   - Distributed across 8 TPU devices via **sequence parallelism**

3. **Decoder (Upsampling)**
   - Upsamples back to 1 bp using skip connections from the encoder
   - Task-specific output heads at appropriate resolutions

**Key insight:** Convolutions handle local patterns, transformers handle long-range communication, U-Net skip connections preserve fine detail through the bottleneck.

---

## Slide 6: Training Pipeline — Pretraining + Distillation

> **[Show Figure 1b and 1c]**

**Stage 1: Pretraining (Fig. 1b)**
- 4-fold cross-validation on the reference genome
- Data augmentation: random shifts + reverse complement (50%)
- Train against observed experimental data (ChIP-seq, RNA-seq, etc.)
- Produces fold-specific models (for track evaluation) and all-fold teacher models

**Stage 2: Distillation (Fig. 1c)**
- A single **student model** learns to reproduce an ensemble of teacher predictions
- Critical innovation: input sequences are **randomly mutated** during distillation
- This forces the student to learn how sequence changes affect predictions
- Result: a single robust model for variant effect prediction
- Inference: <1 second per variant on an H100 GPU

**Why distillation matters:** The student matches a 4-model ensemble's performance at 1/4 the compute cost, and the random mutations make it better at scoring real variants.

---

## Slide 7: Track Predictions Match Experimental Data

> **[Show Figure 2a and 2b]**

**Fig. 2a — Full 1 Mb region (chr. 19, HepG2)**
- Observed vs. predicted tracks shown side-by-side for:
  - Strand-specific RNA-seq (+ and - strands)
  - ATAC-seq and DNase-seq (chromatin accessibility)
  - H3K27ac ChIP-seq (active enhancer/promoter mark)
  - CTCF ChIP-seq (insulator/boundary element)
  - Hi-C contact maps (3D chromatin interactions)
- Predictions closely match experimental observations across all modalities

**Fig. 2b — Zoomed view of LDLR gene (50 kb)**
- Base-pair resolution predictions capture:
  - Individual splice donor and acceptor sites
  - Splice site usage (which sites are actively used)
  - Splice junctions (arcs connecting donor-acceptor pairs with read counts)
  - Exon-level RNA-seq coverage
- This level of detail is impossible at 32 bp or 128 bp resolution

---

## Slide 8: Quantitative Track Performance

> **[Show Figure 2c, 2d, 2e]**

**Fig. 2c — Pearson correlations across modalities**
- Splice site usage: r = 0.86 (human), 0.82 (mouse)
- RNA-seq: r = 0.81 (human)
- ATAC: r = 0.73 (human)
- Strong performance across both species and all modalities

**Fig. 2d — Gene expression prediction**
- Raw expression: r = 0.82
- Cell-type-specific patterns: r = 0.59 (cross-gene), 0.63 (cross-track)
- Tissue specificity remains a challenging frontier

**Fig. 2e — Splice junction counts**
- Tissue-specific splice junctions predicted with r ~ 0.75 in brain, lung, blood
- The model learns tissue-specific alternative splicing patterns

---

## Slide 9: Splicing — A Comprehensive View

> **[Show Figure 3a, 3b, 3c]**

**Fig. 3a — AlphaGenome predicts all aspects of splicing**
- Only model that predicts RNA-seq + splice sites + splice usage + splice junctions at 1 bp
- SpliceAI: sites only. Borzoi: RNA-seq at 32 bp. Pangolin: sites + usage.

**Fig. 3b — Exon skipping example (DLG1 gene)**
- A 4-bp deletion causes exon skipping in tibial artery tissue
- AlphaGenome correctly predicts:
  - Loss of the splice junction flanking the skipped exon
  - Emergence of a new bypass junction
  - Drop in RNA-seq coverage over the exon

**Fig. 3c — New splice junction example (COL6A2)**
- A G>C variant creates a new splice donor
- The model predicts the new junction and extended exon

---

## Slide 10: The Model Learns Splicing Biology

> **[Show Figure 3d, 3e, 3f]**

**Fig. 3d — In silico mutagenesis reveals learned motifs**
- ISM of U2SURP exon 9: systematically mutate every position, measure effect on splice junction score
- The model independently discovered:
  - Branch point (upstream A)
  - Polypyrimidine tract (Poly T)
  - Acceptor motif (AG)
  - Exonic splicing enhancer
  - Donor motif (GT)
  - Intronic motif
- These are canonical splicing signals — learned entirely from data

**Fig. 3f — Splicing QTL classification benchmarks**
- AlphaGenome (composite scorer) beats Pangolin, SpliceAI, DeltaSplice, and Borzoi
- Both for variants near splice sites (< 200 bp) and distal variants (< 10 kb)

---

## Slide 11: Gene Expression Variant Effects

> **[Show Figure 4a, 4b, 4d, 4g]**

**Fig. 4a — Variant scoring strategy**
- Predict RNA-seq for REF and ALT alleles
- Average predicted coverage over exons of target gene
- Score = log(ALT) - log(REF)

**Fig. 4b — Example: APOL4 eQTL**
- rs9610445 (A>C) reduces APOL4 expression in colon tissue
- AlphaGenome recapitulates both the coverage pattern and direction of effect
- ISM reveals the variant disrupts a splice donor motif

**Fig. 4d — 17,675 eQTLs: predicted vs. observed**
- Spearman rho = 0.50 for effect size correlation

**Fig. 4g — The practical payoff**
- At 90% sign accuracy threshold:
  - AlphaGenome recovers **41%** of eQTLs
  - Borzoi recovers only **19%**
  - 2x more actionable predictions

---

## Slide 12: Chromatin Accessibility & TF Binding

> **[Show Figure 5a, 5d, 5e, 5f]**

**Fig. 5a — Centre-mask scoring for chromatin variants**
- Sum predicted signal in a local window around the variant
- Compare REF vs. ALT predictions

**Fig. 5d — caQTL effect sizes**
- Predicted vs. observed for 2,219 causal caQTLs: **r = 0.74**
- Very strong quantitative agreement

**Fig. 5e-f — Mechanistic interpretation**
- Example: a G>T variant at chr. 3 reduces DNase accessibility
- ISM reveals the variant **disrupts an NF-kB binding motif**
- The model doesn't just predict "less accessible" — it tells you *why*

**Fig. 5g-i — SPI1 transcription factor binding QTLs**
- r = 0.55 for predicted vs. observed binding effect sizes
- ISM reveals created/disrupted SPI1 motifs at variant positions

---

## Slide 13: Multimodal Power — TAL1 Oncogene Case Study

> **[Show Figure 6a, 6b, 6d, 6e]**

**The biology:** Three independent groups of non-coding mutations in T-ALL patients all upregulate the TAL1 oncogene through different mechanisms.

**Fig. 6b — One oncogenic insertion (C>ACG)**
AlphaGenome predicts the full cascade from a single inference pass:
- Increased **H3K27ac** and **H3K4me1** at variant site (neo-enhancer formation)
- Decreased **H3K9me3** and **H3K27me3** near TSS (loss of repression)
- Increased **H3K36me3** across gene body (active transcription)
- Increased **TAL1 mRNA expression**

**Fig. 6d — Multimodal heatmap**
- Cancer mutations cluster together with a distinct multimodal signature
- Background mutations show no consistent pattern

**Fig. 6e — ISM reveals the mechanism**
- Reference sequence: no important motifs near variant site
- Alternative sequence: a **MYB transcription factor motif** appears
- This matches what was experimentally discovered (Mansour et al. 2014)

**This is the key argument for why one unified model matters** — no single-modality model could capture this full mechanistic story.

---

## Slide 14: What Design Choices Matter? (Ablations)

> **[Show Figure 7a, 7b, 7c, 7d]**

**Fig. 7a — Resolution: 1 bp is best**
- Finer training resolution consistently improves splicing and accessibility predictions
- Histone and contact map tasks are less sensitive (their assay resolution is already coarser)

**Fig. 7b — Longer sequence = better**
- 1 Mb training + 1 Mb inference is optimal
- Models trained on short sequences (32 kb) perform worse even when given 1 Mb at inference
- The model genuinely learns to use long-range regulatory information

**Fig. 7c — Distillation matches ensembling**
- A single distilled model (64 teachers) rivals a 4-model ensemble
- Massive practical advantage: 1 model call vs. 4

**Fig. 7d — Multimodal training helps**
- The full multimodal model generally outperforms single-modality models
- Cross-modal information transfer improves shared representations
- Expression and accessibility data provide the most benefit to other tasks

---

## Slide 15: Limitations & Future Directions

**Current limitations:**
- Distal regulation (>100 kb) still challenging — performance decays with distance
- Tissue-specific pattern prediction needs improvement
- Only trained on human and mouse genomes
- Focused on protein-coding genes — miRNAs and other non-coding genes under-covered
- Predicts molecular consequences, **not phenotype** — can't go variant → disease directly
- Not benchmarked on personal genome prediction

**Future directions:**
- More species, more cell types, single-cell data integration
- DNA methylation and RNA structural features as new modalities
- Integration with conservation scores (like CADD, presented earlier in class) for clinical use
- Task-specific fine-tuning on perturbational datasets (CRISPRi, MPRA)
- Uncertainty estimation for predictions

---

## Slide 16: Summary & Key Takeaways

1. **AlphaGenome unifies** long-range context (1 Mb), base-pair resolution, and multimodal prediction into one model

2. **Architecture innovation:** U-Net backbone with convolutional encoder, transformer tower, and task-specific output heads — enabled by sequence parallelism across 8 TPUs

3. **Training innovation:** Two-stage pretraining + distillation with random mutations produces a single robust model for variant scoring

4. **Performance:** SOTA on 25/26 variant effect prediction tasks and 22/24 track prediction tasks — beats both generalist (Borzoi, Enformer) and specialist (SpliceAI, ChromBPNet, Orca) models

5. **Multimodal interpretation:** The TAL1 case study demonstrates that scoring variants across all modalities simultaneously reveals mechanisms invisible to single-modality approaches

6. **Practical impact:** 2x more eQTLs recovered at 90% accuracy; <1 second per variant; publicly available API and code

---

## Discussion Questions for the Class

1. AlphaGenome is trained on reference genomes. How might it perform on variants from underrepresented populations whose haplotype backgrounds differ significantly from the reference?

2. The model predicts molecular consequences but not phenotype. What additional information or models would be needed to go from "this variant reduces APOL4 expression by 30%" to "this variant increases disease risk"?

3. The distillation step uses random mutations to improve variant robustness. Could this approach introduce biases — for example, could the model learn to over-predict effects of mutations near certain sequence contexts?

4. How does this relate to ChromHMM (presented earlier)? ChromHMM discovers chromatin states from observed data; AlphaGenome predicts chromatin states from sequence alone. What are the complementary strengths?

---

## References

- Avsec et al. (2026) Advancing regulatory variant effect prediction with AlphaGenome. *Nature* 649, 1206-1218.
- Avsec et al. (2021) Effective gene expression prediction from sequence by integrating long-range interactions. *Nature Methods* 18, 1196-1203. [Enformer]
- Linder et al. (2025) Predicting RNA-seq coverage from DNA sequence. *Nature Genetics* 57, 949-961. [Borzoi]
- Jaganathan et al. (2019) Predicting splicing from primary sequence with deep learning. *Cell* 176, 535-548. [SpliceAI]
- Mansour et al. (2014) An oncogenic super-enhancer formed through somatic mutation. *Science* 346, 1373-1377. [TAL1]

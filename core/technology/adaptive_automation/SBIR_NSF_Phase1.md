# NSF SBIR Phase I Proposal
## The Living Age, Inc.

**Program:** NSF Small Business Innovation Research (SBIR) Phase I
**Directorate:** Biological Sciences / Engineering
**Topic Area:** Biological Technologies (BT) — Biodesign & Synthetic Biology Tools
**Requested Amount:** $275,000
**Duration:** 6 months

---

## Project Summary

**Title:** LivingCAD: A Natural Language Interface for Function-Conditioned Protein Design in Structural Fungal Systems

**Overview:**
The Living Age proposes to develop LivingCAD, the first natural language biodesign platform that enables researchers to translate plain English descriptions of desired biological function directly into candidate protein sequences codon-optimized for structural fungal chassis organisms. The system integrates a large language model (Claude, Anthropic) for biological intent interpretation with a protein language model (ESM-3, EvolutionaryScale) for function-conditioned sequence generation, connected by a bridge layer that performs organism-specific codon optimization, regulatory compatibility analysis, and pathway conflict detection.

**Intellectual Merit:**
Current protein design workflows require researchers to manually translate functional intent into GO terms, select appropriate protein families, and navigate codon usage tables — a process that takes weeks and requires deep expertise at multiple biological scales simultaneously. LivingCAD addresses this bottleneck by creating the first computational bridge between natural language descriptions of biological function and synthesizable DNA sequences, validated against organism-specific codon usage, regulatory compatibility, and metabolic pathway profiles. The system advances the scientific understanding of how semantic descriptions of protein function map to the sequence space explored by protein language models.

**Broader Impacts:**
LivingCAD dramatically reduces the barrier to entry for synthetic biology research, enabling researchers without deep sequence-level expertise to design and test protein candidates. The platform is specifically architected for structural and mycelial fungi (Ganoderma lucidum, Pleurotus ostreatus), organisms at the frontier of sustainable materials research, bioremediation, and living architectural systems. By democratizing access to protein design tools for the fungal chassis, the platform supports the emerging field of mycelium-based materials — a potential replacement for plastics, concrete additives, and conventional insulation — with broad environmental and economic implications.

**Commercial Potential:**
The synthetic biology tools market is projected to reach $32B by 2030. LivingCAD creates a new software category — organism-scale biodesign software — currently unoccupied by any commercial product. Phase I targets synthetic biology researchers ($50–200/month academic, $500–2,000/month startup). Phase II extends to architects and materials companies designing with mycelium. The longer-term commercial vision is a living architecture design platform analogous to CAD software for conventional construction — but for organisms rather than materials.

**Keywords:** synthetic biology, protein design, natural language processing, fungal biotechnology, living materials, biodesign software, ESM-3, codon optimization

---

## Project Description

### 1. Significance and Innovation

#### 1.1 The Problem: The Translation Gap in Biodesign

Synthetic biology has produced powerful molecular tools for designing, assembling, and expressing custom proteins. Yet the bottleneck in the field is not molecular — it is cognitive. The translation between *what a researcher wants a protein to do* and *what sequence to synthesize* requires simultaneous expertise in protein biochemistry, gene ontology, codon biology, regulatory element compatibility, and metabolic pathway dynamics. This translation is performed manually, typically taking days to weeks per design cycle, and requires a level of interdisciplinary fluency that limits access to the field.

Consider a straightforward design request: *"design a protein that cross-links fungal cell walls under mechanical stress."* Executing this requires a researcher to:

1. Identify the relevant biochemical mechanism (oxidative cross-linking of chitin/glucan polymers by laccase-type oxidoreductases)
2. Map the function to Gene Ontology (GO) terms: GO:0005618 (cell wall), GO:0016491 (oxidoreductase activity), GO:0009612 (response to mechanical stimulus)
3. Select an appropriate chassis organism (Ganoderma lucidum for eukaryotic fungal expression with high chitin content)
4. Generate or select candidate amino acid sequences with the appropriate catalytic domain architecture
5. Back-translate to codon-optimized DNA using the target organism's RSCU (Relative Synonymous Codon Usage) table
6. Check for regulatory element compatibility (promoter recognition, terminator sequences, cross-kingdom conflicts)
7. Verify pathway compatibility (oxidoreductase activity consumes O₂; conflict with bioluminescence pathways sharing the same substrate pool)

No existing software tool performs this full translation pipeline. Benchling (Benchling Inc., San Francisco) provides excellent laboratory information management and sequence annotation but does not generate novel sequences from functional descriptions. Geneious (Dotmatics) provides sequence analysis tools but requires the researcher to have a sequence before analysis can begin. Neither tool addresses the translation from intent to sequence.

Protein language models, particularly ESM-3 (Lin et al., 2023; EvolutionaryScale), have demonstrated the capacity to generate biologically plausible protein sequences conditioned on functional annotations expressed as Gene Ontology tokens. However, ESM-3 provides no interface for non-expert users, requires significant bioinformatics expertise to operate, and produces outputs that require substantial post-processing before they are useful for experimental design. Large language models (LLMs) such as Claude (Anthropic) have demonstrated sophisticated capacity for biological reasoning, GO term identification, and structured information extraction from natural language.

**The innovation:** LivingCAD bridges these two model classes — connecting natural language to protein language models — creating the first software system capable of translating plain English descriptions of biological function into synthesizable, organism-validated DNA sequences.

#### 1.2 Innovation Beyond the State of the Art

LivingCAD advances the state of the art in three dimensions:

**1. Natural language → biological specification mapping.** No existing system translates free-form English descriptions of protein function into structured biological specifications (GO terms, chassis selection, property targeting) using a large language model with adaptive reasoning. The LLM layer must perform non-trivial biological reasoning: inferring unstated biological constraints, flagging potential metabolic conflicts, and selecting appropriate chassis organisms based on the desired physical context. This mapping is novel and will be systematically evaluated for accuracy against expert-generated specifications.

**2. Function-conditioned sequence generation for structural fungal organisms.** ESM-3's function-conditioned generation has been demonstrated primarily for well-characterized human and model organism proteins. The application to structural proteins in mycelial fungi — chitin-binding proteins, cell wall cross-linkers, extracellular matrix components, mechanosensitive proteins — represents a novel application domain with minimal prior computational characterization. The codon usage, regulatory element landscape, and metabolic pathway constraints of Ganoderma lucidum and Pleurotus ostreatus are substantially different from model organisms, and the system will develop and validate organism-specific computational resources for these understudied chassis.

**3. Integrated compatibility scoring across three biological scales.** The compatibility engine evaluates generated sequences simultaneously at the codon level (CAI, GC content, rare codon avoidance), the regulatory level (eukaryotic promoter recognition, cross-kingdom element conflicts), and the pathway level (substrate competition, metabolic load, signaling crosstalk). This multi-scale integration is not present in any existing biodesign tool and provides a principled framework for ranking candidate sequences by their likelihood of functional expression in the target chassis.

---

### 2. Technical Objectives

Phase I R&D will achieve the following technical objectives:

**Objective 1: Validate the natural language → BiologicalSpec mapping accuracy (Months 1–2)**
Develop a benchmark of 50 protein design requests spanning the functional space of structural fungal proteins (cross-linking enzymes, secreted extracellular matrix proteins, mechanosensors, adhesion proteins, biomineralization-associated proteins). For each request, generate Claude-produced BiologicalSpecs and evaluate GO term accuracy, chassis selection appropriateness, and sequence length estimation against expert-curated ground truth annotations. Target: >85% GO term recall, >90% chassis appropriateness on expert evaluation rubric.

**Objective 2: Validate ESM-3 function-conditioned generation for fungal structural proteins (Months 2–4)**
Generate candidate amino acid sequences for the 50 benchmark design requests using ESM-3 (esm3-sm-open-v1, 1.4B parameters) conditioned on LLM-extracted GO term annotations. Evaluate sequence quality using: ESM-3 log-likelihood (biological plausibility proxy), predicted structural compatibility with known fungal cell wall protein folds (via ESMFold), and amino acid composition analysis against characterized fungal structural protein databases (UniProt fungal cell wall proteome, CAZy database).

**Objective 3: Develop and validate organism-specific codon optimization for Ganoderma lucidum and Pleurotus ostreatus (Months 2–3)**
Compile RSCU tables for G. lucidum and P. ostreatus from publicly available genome sequences (JGI MycoCosm database: G. lucidum genome GCA_000143585, P. ostreatus genome GCA_000697285). Validate codon optimization algorithm by back-translating characterized fungal proteins and comparing CAI scores to experimentally validated expression levels from the literature. Extend REFERENCE_RSCU table with validated fungal chassis entries.

**Objective 4: Build and validate the integrated compatibility engine (Months 3–5)**
Extend the existing compatibility analysis modules (codon, regulatory, pathway) to produce integrated candidate rankings for the benchmark design set. Develop a pathway conflict database specific to fungal structural protein expression, including: O₂ competition between oxidoreductases and bioluminescence pathways, chitin synthase substrate competition, secretory pathway load limitations. Validate conflict detection against known incompatibilities reported in the fungal synthetic biology literature.

**Objective 5: Demonstrate end-to-end pipeline on validation design set (Months 5–6)**
Run the complete pipeline (English → BiologicalSpec → ESM-3 sequences → codon optimization → compatibility analysis → English explanation) on 10 held-out design requests not seen during development. Evaluate end-to-end performance: time from input to output (<5 minutes target), candidate quality (ESM log-likelihood, CAI, structural plausibility), and expert rating of Claude's English explanation (biological accuracy, completeness, honest acknowledgment of uncertainty). Produce a demo video demonstrating the system on the Phase I benchmark sentence: *"design a protein that cross-links fungal cell walls under mechanical stress."*

---

### 3. R&D Plan

#### 3.1 System Architecture

The LivingCAD system consists of four integrated modules:

```
User (English description)
         │
         ▼
┌─────────────────────────────────┐
│  ENGLISH LAYER — Claude API     │
│  interpret_description()        │
│  → BiologicalSpec (GO terms,    │
│    target organism, properties, │
│    sequence length, rationale,  │
│    ethical flags)               │
└────────────────┬────────────────┘
                 │ structured biological spec
                 ▼
┌─────────────────────────────────┐
│  ESM-3 BRIDGE                   │
│  generate_sequences()           │
│  → GO terms → function tokens   │
│  → 3 candidate AA sequences     │
│  → ESM log-likelihood scores    │
└────────────────┬────────────────┘
                 │ amino acid sequences
                 ▼
┌─────────────────────────────────┐
│  CODON OPTIMIZATION             │
│  back_translate()               │
│  → organism RSCU tables         │
│  → codon-optimized DNA          │
│  → CAI, GC content scores       │
└────────────────┬────────────────┘
                 │ DNA candidates
                 ▼
┌─────────────────────────────────┐
│  COMPATIBILITY ENGINE           │
│  codon.analyze()                │
│  regulatory.analyze()           │
│  pathway.analyze()              │
│  → integrated candidate ranking │
│  → conflict warnings            │
└────────────────┬────────────────┘
                 │ scored candidates + analysis
                 ▼
┌─────────────────────────────────┐
│  ENGLISH LAYER — Claude API     │
│  explain_result()               │
│  → plain English interpretation │
│  → biological rationale         │
│  → honest uncertainty framing   │
└─────────────────────────────────┘
         │
         ▼
Terminal output (rich UI) / API response
```

#### 3.2 English Layer: LLM-Mediated Biological Intent Extraction

The English layer uses Claude (claude-opus-4-6) with adaptive thinking enabled to translate free-form natural language descriptions into a structured `BiologicalSpec` dataclass. The model operates under a system prompt encoding stewardship principles: preference for ecologically restorative chassis organisms, explicit flagging of metabolic conflicts, honest representation of biological uncertainty, and framing generated sequences as hypotheses rather than confirmed designs.

The `BiologicalSpec` structure contains:
- `function_description`: Precise biological description of the protein function (cleaned, technically accurate)
- `go_terms`: List of Gene Ontology term IDs (format GO:XXXXXXX) capturing the function
- `target_organism`: Chassis organism key (ganoderma, yeast, arabidopsis, human, komagataeibacter)
- `chassis_type`: Cell type (prokaryote, eukaryote_fungal, eukaryote_plant, eukaryote_animal)
- `desired_properties`: Physical/functional properties to optimize for
- `sequence_length_estimate`: Estimated amino acid count (50–500 range)
- `rationale`: Biological reasoning for design choices
- `caveats`: Metabolic risks, ecological flags, ethical considerations

The model uses Claude's tool use capability with structured JSON output constrained to the BiologicalSpec schema, ensuring downstream compatibility regardless of response variation. Adaptive thinking is critical here: GO term selection for novel protein functions requires multi-step biological reasoning that benefits from extended internal deliberation before committing to a structured output.

#### 3.3 ESM-3 Bridge: Function-Conditioned Sequence Generation

ESM-3 (esm3-sm-open-v1, 1.4B parameters) accepts function conditioning via `FunctionAnnotation` objects specifying GO term labels, start positions, and end positions relative to the generated sequence length. The bridge layer maps Claude-extracted GO terms to ESM-3 function tokens and calls the generation API with:

- `num_steps=8`: Sufficient iterative refinement for coherent functional sequences
- `temperature=0.7`: Balanced exploration/exploitation for functional plausibility
- `n=3`: Three candidate sequences per design request (diversity for downstream selection)

Each generated sequence is scored using ESM-3's own log-likelihood as a proxy for biological plausibility (higher log-likelihood = sequence more consistent with the protein language model's learned distribution over natural proteins).

A mock fallback mode generates synthetic placeholder sequences when ESM-3 is unavailable (GPU memory insufficient, authentication not configured), enabling the full pipeline to run for demonstration and testing purposes. Mock sequences are clearly labeled and never presented as real design candidates.

#### 3.4 Codon Optimization and Organism-Specific Back-Translation

The back-translation algorithm uses RSCU (Relative Synonymous Codon Usage) tables compiled from organism-specific genomes. For each amino acid in a generated protein sequence:

1. Identify all synonymous codons encoding that amino acid
2. Select the codon with the highest RSCU value in the target organism's table
3. Append to the growing DNA sequence

This deterministic approach maximizes the Codon Adaptation Index (CAI) for the target chassis. The Phase I work will compile and validate RSCU tables for G. lucidum and P. ostreatus from JGI MycoCosm genome data, extending the existing REFERENCE_RSCU table that currently covers ganoderma, yeast, arabidopsis, human, and komagataeibacter.

Additional DNA-level quality metrics computed for each candidate:
- GC content (target: 50–65% for fungal expression)
- Rare codon frequency (flag codons with RSCU < 0.2)
- Predicted mRNA secondary structure at the 5' end (Kozak-equivalent context)

#### 3.5 Compatibility Engine Integration

The existing compatibility engine (developed prior to Phase I) performs three levels of analysis:

**Codon compatibility:** CAI calculation, GC content, rare codon identification, cross-kingdom codon usage conflicts for multi-organism designs.

**Regulatory compatibility:** Checks for cross-kingdom regulatory element conflicts (prokaryotic promoters in eukaryotic contexts, Kozak sequence presence, polyadenylation signal conflicts). Uses a catalog of 24 characterized regulatory parts spanning 5 organism classes.

**Pathway compatibility:** Detects metabolic and signaling conflicts using a database of 12 pathway profiles. Identifies substrate competition (two oxidoreductases competing for the same O₂ pool), metabolic load conflicts (high-expression proteins overwhelming the secretory pathway), and signaling crosstalk (heterologous kinases interfering with endogenous signaling cascades).

Phase I will extend the pathway database with fungal-specific entries covering the functional space of structural proteins in mycelial organisms.

#### 3.6 Terminal Interface

The terminal interface uses the `rich` Python library to present pipeline results in real time:
- Streaming display of Claude's biological interpretation as it is generated
- Progress indicators during ESM-3 sequence generation
- Color-coded sequence display (functional regions, rare codons, regulatory signals)
- Confidence score visualization with explicit uncertainty communication
- Conflict warnings in amber/red with actionable explanations

The interface is designed to feel like a conversation with a knowledgeable collaborator, not a query to a database. Every sequence output is accompanied by Claude's English explanation of what was designed, why, and what the biological uncertainty is.

---

### 4. Team and Qualifications

**Principal Investigator:** Sage Clokey
B.S. Biomolecular Engineering and Bioinformatics (Bioinformatics Concentration), University of California, Santa Cruz — one of the preeminent genomics and bioinformatics institutions in the world, home of the UCSC Genome Browser (used by >300,000 researchers worldwide).

Technical proficiency: Python, R, C, Java, JavaScript/React, Kotlin, SQL, Bash/Shell. Bioinformatics tools: Seurat, Scanpy, kallisto, BLAST, UCSC Genome Browser, Bioconductor, Snakemake, Jupyter, Linux/HPC environments. Statistical/ML methods: PCA, t-SNE, UMAP, OLS regression, LASSO, Random Forest, causal inference. Lab experience: gel electrophoresis, plasmid transformation, agar plate culture.

Relevant coursework: Data Science, Machine Learning, Statistical Modeling, Genomics, Systems Biology, Computational Biology, Biomedical Engineering (BME-105, BME-110), graduate-level Computational Genomics (BME 230A — scRNA-seq analysis, doublet detection, distance metrics), Applied Econometrics.

The PI has completed single-cell RNA-seq analysis using Seurat and Scanpy (cell population identification, differential gene expression, clustering, UMAP visualization), built population genetics simulators (Wright-Fisher model, 10,000 generations), developed genome analysis tools (ORF finder, codon usage analyzer, tRNA fragment finder, protein isoelectric point calculator), and published interactive data visualizations of multi-dimensional biological and political datasets.

The existing LivingCAD codebase demonstrates production-quality implementation of codon optimization, regulatory element analysis, and pathway conflict detection — the foundation Phase I builds upon.

Access to the UCSC genomics and synthetic biology ecosystem provides institutional relationships with researchers actively working on organism-scale biodesign, living materials, and computational approaches to morphogenesis.

**Broader Team and Advisors:** [To be developed — list any collaborators, advisors, wet lab partners here]

**Online presence:**
- GitHub: https://github.com/Sage-Clokey?tab=repositories
- LinkedIn: https://www.linkedin.com/in/sage-clokey-a164411a9/
- Website: https://sage-clokey.github.io/

**Note on UCSC Ecosystem Access:** The University of California, Santa Cruz has active research programs in mycelium-based materials, coral genomics, and computational genomics. The PI's institutional relationships provide access to domain expertise, potential wet lab validation partnerships, and the broader iGEM community at UCSC for beta testing the software platform.

---

### 5. Commercial Potential and Market Analysis

#### 5.1 Market Opportunity

The synthetic biology tools and reagents market was valued at $14.2B in 2023 and is projected to grow to $32.4B by 2030 (Grand View Research, 2024). Within this market, the design software segment — computational tools for biodesign, sequence analysis, and pathway engineering — represents the fastest-growing subsegment, driven by the need to translate expanding biological databases into actionable design specifications.

**Immediate addressable market (Phase I-II): Synthetic biology researchers**
- ~50,000 synthetic biology researchers globally (NSF, NIH, DOE-funded labs, industry)
- ~5,000 actively working with fungal chassis organisms (JGI MycoCosm user base, iGEM fungal projects)
- Target price: $50–200/month academic, $500–2,000/month startup/industry
- Conservative 1% penetration of fungal chassis researchers = $300K–1.2M ARR in Year 2

**Emerging market (Phase III-IV): Bioarchitects and sustainable materials companies**
- Mycelium materials market: Ecovative Design (raised $100M+), Mogu, Biohm — all need design tools
- Architecture firms exploring biophilic materials: no dedicated design software exists
- IKEA, Hermès, Stella McCartney have all invested in or produced mycelium-based materials
- Target price: $500–5,000/month professional, $2,000+/month enterprise

**Long-term market (Phase V+): Living architectural systems**
- Global construction market: $10 trillion annually
- 0.1% displacement by living materials = $10B market
- No competitor exists at this intersection

#### 5.2 Competitive Landscape

| Competitor | Category | Gap |
|------------|----------|-----|
| Benchling | Lab information management, sequence annotation | Does not generate sequences from functional descriptions |
| Geneious | Sequence analysis, alignment | Requires sequence input; no generative capability |
| Zymergen / Ginkgo | Full-service biodesign (not software) | Not a software product; not accessible to individual researchers |
| Rosetta/Foldit | Protein structure prediction/design | Expert-only; no natural language interface; no organism-level compatibility |
| SnapGene | Cloning and visualization | Downstream of sequence selection; no design capability |

**LivingCAD occupies a category that does not exist:** organism-scale biodesign software that starts from intent and produces synthesizable sequences. This is not incrementally better bioinformatics — it is a new tool category.

#### 5.3 Path to Commercialization

**Phase I (this proposal):** Validate core pipeline. Produce working CLI demo. Build benchmark dataset.

**Phase II:** Web interface, broader organism support, Enformer regulatory prediction integration, iGEM community beta program, first paying customers.

**Phase III:** Full Living Architecture Studio — architects and biologists on the same platform. Enterprise contracts. First wet lab validation partnerships.

**Phase II SBIR target:** $1.75M to fund the regulatory layer integration, web platform build-out, and first wet lab validation of a LivingCAD-designed protein.

---

### 6. Potential Risks and Mitigation Strategies

**Technical Risk 1: ESM-3 generation quality for understudied fungal proteins**
*Risk:* ESM-3's training data is dominated by human and model organism proteins. Generated sequences for novel fungal structural proteins may have low biological plausibility.
*Mitigation:* Phase I benchmarking will characterize this gap explicitly. Mock mode enables pipeline validation independent of ESM-3 quality. If quality is insufficient, Phase II will explore fine-tuning ESM-3 on JGI MycoCosm fungal proteomes (~2,000 fungal genomes available).

**Technical Risk 2: GO term mapping accuracy for novel protein functions**
*Risk:* Claude may misidentify GO terms for protein functions at the frontier of biological knowledge (e.g., mechanosensitive structural proteins in mycelial organisms with limited literature).
*Mitigation:* Benchmark evaluation (Objective 1) will quantify this gap. The system explicitly surfaces its GO term reasoning for user review; the human remains in the loop for validation before synthesis.

**Commercial Risk: Market education timeline**
*Risk:* "Organism-scale biodesign software" is a new category. Researchers may not immediately recognize the workflow problem LivingCAD solves.
*Mitigation:* Early iGEM community engagement (a highly accessible, early-adopter market), public demo video, and open-source release of the core compatibility engine to build ecosystem awareness before full commercial launch.

**Timeline Risk: SBIR reporting burden**
*Risk:* NSF Phase I reporting requirements may consume PI time otherwise spent on R&D.
*Mitigation:* Clear milestone-based project structure (5 objectives, each with measurable success criteria) makes reporting straightforward and keeps R&D on track.

---

### 7. Facilities, Equipment, and Other Resources

**Computational Resources:**
ESM-3 (1.4B parameters) requires a minimum of 8GB VRAM for inference. The PI has access to local GPU hardware sufficient for Phase I experimentation. For production-scale generation, AWS/GCP GPU instances will be used (budgeted under computing costs). The mock fallback mode ensures development and testing can proceed on CPU hardware.

**Software Infrastructure:**
The existing codebase provides production-ready implementations of codon optimization, regulatory compatibility analysis, and pathway conflict detection. Phase I builds directly on this foundation, reducing development time and risk.

**External APIs:**
- Anthropic Claude API (claude-opus-4-6): ~$50–200/month at Phase I usage levels
- EvolutionaryScale ESM-3 API: Free for non-commercial research; commercial license for Phase II+
- UCSC Genome Browser API: Public, free
- NCBI Entrez API: Public, free

**Institutional Access:**
UCSC genomics resources, MycoCosm database access, and iGEM network for beta testing.

---

### 8. Prior Work

The PI has developed a functional genome retrieval and compatibility analysis system that demonstrates:

- Retrieval of 220+ genomes from UCSC and specialized databases (coral, spider silk, mycelium organisms)
- Organism-specific codon optimization with validated RSCU tables for 5 chassis organisms
- Regulatory element compatibility analysis covering 24 characterized biological parts
- Pathway-level conflict detection across 12 metabolic and signaling pathway profiles
- Adaptive assembly engine that sequences biological parts respecting pathway, regulatory, and codon constraints

This prior work provides the validated foundation that Phase I builds upon — the compatibility engine is not hypothetical. It exists, it runs, and Phase I integrates it with the LLM-ESM-3 pipeline to complete the English ↔ synthesizable DNA bridge.

---

### 9. Timeline

| Month | Milestone |
|-------|-----------|
| 1 | Benchmark design set compiled (50 requests). Claude BiologicalSpec accuracy evaluation framework implemented. |
| 2 | GO term accuracy benchmark complete. ESM-3 bridge implemented. Fungal RSCU tables compiled from JGI MycoCosm. |
| 3 | ESM-3 generation quality evaluation complete. Codon optimization validated for G. lucidum and P. ostreatus. |
| 4 | Pathway conflict database extended for fungal structural proteins. Integrated compatibility engine complete. |
| 5 | Full pipeline integrated. End-to-end testing on held-out validation set. |
| 6 | Validation results analyzed. Demo video produced. Phase II proposal drafted. Final report submitted. |

---

### 10. References

*(Selected — expand for submission)*

- Lin, Z., Akin, H., Rao, R., et al. (2023). Evolutionary-scale prediction of atomic-level protein structure with a language model. *Science*, 379(6637), 1123–1130.
- Hie, B., Candido, S., Lin, Z., et al. (2022). Efficient evolution of human antibodies from general protein language models. *Nature Biotechnology*, 41, 1092–1098.
- Consortium, T. U. (2023). UniProt: the Universal Protein Database. *Nucleic Acids Research*, 51(D1), D523–D531.
- Lombard, V., Golaconda Ramulu, H., Drula, E., et al. (2014). The carbohydrate-active enzymes database (CAZy). *Nucleic Acids Research*, 42(D1), D490–D495.
- Chen, W., Vito, D., Bhatt, M., et al. (2022). Mycelium-based composites: a review of their production and properties. *ACS Applied Bio Materials*, 5(11), 5083–5095.
- Grigoriev, I.V., et al. (2014). MycoCosm portal: gearing up for 1000 fungal genomes. *Nucleic Acids Research*, 42(D1), D699–D704.

---

## Budget Justification (Summary)

| Category | Amount | Justification |
|----------|--------|---------------|
| PI Salary (6 months, 100% effort) | $180,000 | Full-time R&D on pipeline development and validation |
| Computational costs (GPU cloud + APIs) | $24,000 | ESM-3 inference, Claude API calls, AWS GPU instances |
| Software licenses and tools | $6,000 | Development tools, database access fees |
| Travel (1 conference presentation) | $3,000 | Synthetic biology conference — community engagement |
| Indirect costs (NSF-approved rate) | $62,000 | ~35% of direct costs |
| **Total** | **$275,000** | |

---

## Broader Impacts Statement

LivingCAD is not only a research tool. It is infrastructure for a category of biological design that does not yet have adequate computational support: the design of organisms as structural, self-repairing, and environmentally integrated materials.

The acceleration of mycelium materials research has direct environmental implications. Mycelium composites can replace expanded polystyrene (EPS) packaging — a product with essentially no biodegradability and significant marine pollution impact. The estimated annual production of EPS is 5 million metric tons globally. A design software tool that accelerates the engineering of structurally superior mycelium-based replacements has the potential to meaningfully displace this environmental burden.

More broadly, the democratization of protein design for fungal chassis organisms makes the entire category of mycelium-based materials more accessible to small research groups, startups, and academic labs without dedicated bioinformatics staff — expanding the community working on this problem and accelerating the timeline to commercially viable living materials.

The platform is explicitly designed for ecological stewardship: the system prompt framing Claude's biological reasoning encodes preference for restorative chassis organisms, flags metabolic risks to host organisms, and presents all designed sequences as hypotheses requiring experimental validation — never as confirmed manufacturing specifications. Responsible research practice is built into the architecture, not bolted on afterward.

---

*Submitted to NSF SBIR Phase I — Biological Technologies*
*The Living Age, Inc.*
*Sage Clokey, Founder*
*[Address — to be completed upon incorporation]*

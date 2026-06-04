# Thiel Fellowship Application — The Living Age

**Applicant:** Sage Clokey
**Age:** 22 (DOB: June 7, 2003)
**Email:** clokeyd.sage@gmail.com
**Phone:** (805) 459-2396
**Location:** Santa Cruz, CA
**Education:** UC Santa Cruz — B.S. Biomolecular Engineering & Bioinformatics (Expected June 2026)

---

## Links and Portfolio

- **GitHub:** https://github.com/Sage-Clokey?tab=repositories
- **Website:** https://sage-clokey.github.io/
- **Bioinformatics portfolio:** https://sage-clokey.github.io/bioinformatics-projects.html
- **Full project portfolio:** https://sage-clokey.github.io/all-projects.html
- **LinkedIn:** https://www.linkedin.com/in/sage-clokey-a164411a9/

### The Living Age — Core Project
- **Repo:** github.com/Sage-Clokey/adaptive_Automation
  - Working genome retrieval system (220+ genomes, UCSC + NCBI)
  - Codon optimization engine with validated RSCU tables for 5 chassis organisms
  - Regulatory element compatibility analysis (24 characterized parts)
  - Pathway conflict detection (12 metabolic/signaling profiles)
  - Adaptive assembly engine
  - Claude API integration for English ↔ biological specification translation

### Supporting Bioinformatics Work (46 public repos)
The Living Age project builds on a body of bioinformatics work, not a flash of inspiration:

- **genome-nucleotide-analyzer** — GC content and codon usage analysis across genomes
  (directly feeds into the codon optimization engine in LivingCAD)
- **computational-biology-methods** — gene expression analysis, PCA/MDS, Wright-Fisher
  simulation, HMM Viterbi, breast cancer ML prediction (BME coursework)
- **scrna-seq-computational-genomics** — graduate-level single-cell RNA-seq analysis,
  doublet detection, distance metrics (BME 230A — the same single-cell techniques
  needed for Phase 3 developmental modeling)
- **orf-finder** — 6-frame ORF finder for DNA sequences (foundational sequence
  analysis tool)
- **protein-isoelectric-point-calculator** — protein charge and pI from amino acid
  sequences (protein-level biophysics)
- **trna-essential-fragment-finder** — minimal essential unique fragments for
  probe/primer design (sequence space reasoning)
- **scientific-data-visualization** — publication-quality genome browser figures,
  sequence logos, expression plots
- **genetic-drift-simulator** — population genetics simulation
- **living-republic-pca** — PCA on Congressional voting data showing continuous
  multi-dimensional political structure (the True Republic analysis — data science
  applied to the philosophical framework)
- **genetic-data-ethics** — "Who Owns Your DNA?" — genetic data ownership, GDPR,
  bioethics policy (the ethics aren't bolted on — they're in the coursework)

### Systems and Software Engineering
- **c-systems-programming** — RPN calculator, hex dump, hash vs linked list
  benchmarking, graph pathfinding (C proficiency)
- **java-data-structures** — generic ArrayList, self-balancing AVL tree (data
  structures fluency)
- **applied-econometrics-r** — OLS, causal inference, LASSO, random forest in R
  (statistical modeling depth)

### Philosophy and Media
- **sagent-creed-book** — the philosophical framework behind the Living Age
- **spiral-steward-website** — the design philosophy as public writing
- **Living-works-by-the-word** — media and content infrastructure

---

## The Contrarian Question

> "Name an important truth very few people agree with you on."

**Buildings should be alive.**

Not metaphorically — structurally alive. Grown from engineered organisms that
are load-bearing, self-repairing, and responsive to their environment. The
entire construction industry — $10 trillion globally — is built on dead materials:
concrete, steel, wood, glass. Extracted, processed, fixed in place, degrading
from the moment they're installed.

Living organisms already produce materials stronger than steel (spider silk),
harder than concrete (coral biomineralization), and more adaptive than any
engineered composite (fungal mycelium that grows around obstacles and repairs
damage). The biology exists. What doesn't exist is the design software — the
interface between human intention and biological possibility.

Most people think this is science fiction. It isn't. It's an engineering problem
with a clear path: protein design → regulatory circuits → developmental programs →
growth protocols. Each step builds on existing science. The gap is not knowledge.
The gap is that no one has built the tool that connects these layers into a
single design system.

I'm building that tool.

---

## How I Want to Change the World

I want to end the age of dead buildings and begin the Living Age — a period in
which the primary materials of human civilization are alive, grown rather than
manufactured, and ecologically integrated rather than extracted.

This is not an incremental improvement to construction. It is a categorical
shift in how civilization builds. A living wall heals when it cracks. A grown
structure hardens over years instead of degrading. A building that is part of
its ecosystem rather than a wound in it. Housing that can be grown from local
organisms at a fraction of the cost of conventional construction — not just
for the wealthy, but for everyone.

The implications extend beyond architecture. If you can grow a load-bearing
wall, you can grow infrastructure, remediation systems, responsive shelters.
You can grow buildings in places where shipping concrete is impossible. You
can build structures that sequester carbon instead of emitting it. You can
create housing that costs almost nothing in materials because the materials
grow themselves.

This changes who gets to have shelter. That matters.

---

## My Project: LivingCAD — The Design Software for Living Architecture

### What it is

LivingCAD is an organism-scale biodesign platform that translates plain English
descriptions of desired biological function into synthesizable DNA sequences,
codon-optimized for structural organisms like Ganoderma lucidum (reishi mushroom)
and other chassis organisms used in living materials research.

You type: *"design a protein that cross-links fungal cell walls under mechanical stress"*

The system:
1. **Interprets** the biological intent using Claude (Anthropic's LLM) with
   adaptive reasoning — extracting GO terms, selecting the right chassis organism,
   estimating sequence length, flagging metabolic risks
2. **Generates** candidate protein sequences using ESM-3 (EvolutionaryScale's
   protein language model, trained on hundreds of millions of natural proteins)
3. **Optimizes** the DNA using organism-specific codon tables — translating the
   protein into the specific DNA dialect the target organism speaks
4. **Validates** against a compatibility engine that checks regulatory element
   conflicts, pathway bottlenecks, and metabolic load
5. **Explains** the result in plain English — what was designed, why, and what
   the uncertainties are

### What I've already built

The foundation is working code, not a pitch deck:

- **Genome retrieval system** — queries 220+ genomes from UCSC Genome Browser
  and NCBI, including specialized organisms (mycelium, coral, spider silk,
  bacterial cellulose)
- **Codon optimization engine** — validated RSCU (Relative Synonymous Codon Usage)
  tables for 5 chassis organisms: Ganoderma lucidum, yeast, Arabidopsis, human,
  and Komagataeibacter (bacterial cellulose producer)
- **Regulatory compatibility analyzer** — catalog of 24 characterized biological
  parts across 5 organism classes, cross-kingdom conflict detection
- **Pathway conflict detector** — 12 metabolic and signaling pathway profiles,
  detects substrate competition, metabolic load issues, signaling crosstalk
- **Adaptive assembly engine** — sequences biological parts respecting pathway,
  regulatory, and codon constraints
- **Claude interface** — working LLM integration that translates English →
  structured BiologicalSpec with GO terms, organism selection, property targeting

This is not theoretical. The retrieval and compatibility layers run. The Claude
interface is written. The ESM-3 bridge is the next piece — connecting the English
layer to the protein generation layer to complete the Phase 1 pipeline.

### The five phases

| Phase | What it proves | Timeline |
|-------|---------------|----------|
| 1 | English → protein → DNA works end-to-end | Now → Month 3 |
| 2 | Regulatory circuits can be designed (when/where genes activate) | Month 3–8 |
| 3 | Developmental programs can be assembled (how form emerges) | Month 8–14 |
| 4 | Custom DNA LLM trained on living architecture data | Month 14–20 |
| 5 | Full living architecture system — speak a structure into existence | Month 20–24 |

Each phase produces usable software. Each phase generates revenue through
subscriptions from synthetic biology researchers. The near-term product is
design software. The long-term product is the living structure itself.

---

## How I Would Use the Thiel Fellowship

### The $200K allocation

| Use | Amount | Why |
|-----|--------|-----|
| Living expenses (24 months) | $48,000 | Full-time focus. No side jobs. No distraction. |
| GPU compute (ESM-3 inference, model training) | $36,000 | Protein language models need GPU. Cloud instances for Phase 1-3. |
| API costs (Claude, data services) | $12,000 | LLM layer runs on Anthropic API. |
| Wet lab partnership | $40,000 | First experimental validation of a LivingCAD-designed protein. This is what turns computational predictions into biological proof. |
| Equipment and software | $14,000 | Development tools, database hosting, domain/infrastructure. |
| Travel (conferences, potential collaborators) | $15,000 | SynBioBeta, iGEM Giant Jamboree, UCSC network. Building the community. |
| Incorporation and legal | $5,000 | Form The Living Age, Inc. IP protection for the platform. |
| Reserve | $30,000 | Biological research is unpredictable. Buffer for unexpected costs. |

### What changes with the fellowship

Without the fellowship, I build Phase 1 in spare time around coursework, get
a job after graduation, and work on this evenings and weekends. The timeline
stretches to 5+ years. The wet lab validation never happens because I can't
afford it. The window for creating the category closes as larger companies
move into the space.

With the fellowship, I build full-time for 24 months. Phase 1-3 complete.
First paying customers. First wet lab validation. First proof that a
computationally designed protein actually works in a living organism. The
company exists. The category is defined. The open-source ecosystem is seeded.

The difference is not incremental. It's the difference between a side project
and a company that changes how civilization builds.

---

## Why Me

I must finish what my grandfather started.

My grandfather was Art Clokey, the creator of Gumby. He took a piece of clay —
soft, flexible, endlessly moldable — and gave it life through imagination. From
that simple material emerged a symbol that taught millions what freedom looked
like: not rigid, not commanding, but bending without breaking. Green — the color
of life. Shaped like a sprouting seedling emerging from the soil. Gumby was not
a block. He was alive.

Art Clokey did not simply create a cartoon. He shaped a symbol. Clay contains
infinite possibility. In the hands of the creator, it can become anything. It
can bend without breaking. It can be reshaped after failure. Gumby moved through
his world not as a rigid hero but as a living metaphor — he entered stories
through the portals of books, reminding those who watched that imagination itself
is a doorway into other worlds.

Through this simple figure, my grandfather showed a structured world what freedom
looked like. Not freedom through conquest, but freedom through creativity. The
greatest weapon has never been the sword; it has always been the story. Stories
shape how people see reality. They form the myths that guide civilizations.

I am the third Clokey, heir to the name Arthur. Stories come in threes, and so
does this lineage. There was the first Arthur — the creator who formed the clay
and began the story. There was the continuation — the generation that carried
the creation forward through struggle and shadow. And now there is the
interpreter — the one who must understand what the story truly means.

What my grandfather truly began was showing that dead matter could be made to
live through the power of imagination and love. I am carrying that forward.
Where he used clay and stop-motion, I use DNA and protein language models. Where
he animated dead matter into a living symbol, I am learning to grow living
structures from engineered organisms. The Clokey lineage carries the gift of
imagination — not as rulers of empires, but as storytellers of the living age.
For stories are seeds. And when planted in the fertile ground of the human mind,
they grow into forests that no empire can control.

---

I am not coming from the startup world looking for a market. I am coming from
inside the biology, looking at what it can become — and from inside a lineage
of creators, understanding what was started and what must be completed.

I am completing a B.S. in Biomolecular Engineering and Bioinformatics at UC
Santa Cruz — one of the top genomics institutions in the world, home of the
UCSC Genome Browser used by over 300,000 researchers. My coursework spans
data science, machine learning, statistical modeling, genomics, systems biology,
computational biology, and applied econometrics.

I write Python, R, C, Java, JavaScript/React, Kotlin, SQL, and Bash. I work
with Seurat, Scanpy, kallisto, BLAST, the UCSC Genome Browser, Bioconductor.
I run PCA, t-SNE, UMAP, OLS regression, LASSO, Random Forest, and causal
inference. My public GitHub has 46 repositories spanning genome analysis,
protein biophysics, single-cell RNA-seq, population genetics, scientific
visualization, systems programming, and statistical modeling.

I built a codon usage analyzer before I built a codon optimizer. I wrote an ORF
finder before I wrote a protein design pipeline. I analyzed single-cell RNA-seq
data in BME 230A — the same techniques Phase 3 needs for developmental modeling.
I studied genetic data ethics in coursework ("Who Owns Your DNA?") before I
encoded ethical flags into a design system. The path is visible in the commit
history.

I attended Cato University twice by competitive selection — intensive seminars
on political philosophy, economics, and the foundations of a free society. I
served as State Chair for Young Americans for Liberty, coordinating data-driven
outreach across multiple campuses. I am a Local Coordinator for Students for
Liberty, organizing discussions on decentralized systems and voluntary
cooperation. The philosophy behind The Living Age — that life organizes better
than control — is not abstract to me. It is what I organize around.

I applied PCA to the voting records of 1,091 Congressional members and 199 UN
nations to demonstrate that political space is continuous and multi-dimensional,
not binary — the same mathematical thinking I apply to biological sequence space.
The Spiral Steward framework — my philosophy of biological design that treats
organisms as collaborators, not raw materials — grew from this intersection of
quantitative analysis and political philosophy.

The philosophy matters because it shapes the design decisions. A system built
on extraction logic designs organisms that serve human purposes regardless of
the cost to the host. A system built on stewardship logic designs organisms
that cooperate — where the engineered function earns its place in the host's
metabolic economy. The compatibility engine I built reflects this: it doesn't
just check if a design *works*, it checks if it's *fair* to the organism.

I have been thinking about this problem — how to speak the language of life —
for years before I wrote a line of code. The worldview came first. The
technology is how the worldview becomes physical.

The creation of the Living Age requires media to explain why and technology
to show how. I am building both. The YouTube channel, the Sagent Creed, the
Spiral Steward writing — that is the media. LivingCAD — that is the technology.
One without the other doesn't work. You need the story to change how people
see the world, and the tool to change what they can build in it.

That is not something a larger company can replicate by hiring engineers.
You can copy a codebase. You cannot copy a genuine conviction held for years
before anyone was watching. And you cannot replicate a lineage that began with
giving life to clay and ends with giving life to buildings.

The block enforces uniformity. The spiral cultivates life. Not blocks — spirals.
The Sagent Creed: Truth is Law. Conscience is Crown. Every Soul is Sovereign.

---

## What Success Looks Like After 2 Years

**Minimum viable outcome:**
- LivingCAD Phase 1-2 complete and generating revenue ($5K+ MRR)
- Open-source compatibility engine with active community (100+ users)
- First wet lab validation of a LivingCAD-designed protein
- The Living Age incorporated with clear path to seed round

**Target outcome:**
- LivingCAD Phase 1-3 complete (protein + regulatory + developmental layers)
- 500+ active users across academia and biotech
- $20K+ MRR
- Seed round raised or Shuttleworth Fellowship secured for Year 3+
- First physical prototype: a small mycelium structure grown from a
  LivingCAD-designed organism

**Moonshot outcome:**
- A living wall panel. Grown, not built. Designed in English, translated to
  DNA, expressed in a fungal chassis, and physically functional.
- That's the demo that changes everything. The video of that wall existing
  is the moment the Living Age stops being an idea and starts being real.

---

## One More Thing

Peter Thiel wrote in *Zero to One*: "What important truth do very few people
agree with you on?"

Here's mine: **The age of dead matter is ending. The next century's buildings
will be alive. And the design tool for that future does not exist yet — but
I am building it.**

Most people hear "living buildings" and think science fiction. They're wrong.
The biology is real. The models are real. The gap is a design interface that
no one has built because no one has stood at the intersection of bioinformatics,
language models, and architecture with the audacity to connect them.

My grandfather stood at a similar intersection — between clay and imagination —
and created a symbol that shaped the dreams of millions. He showed a structured
world what it looked like when dead matter came alive. I am the third Arthur.
The interpreter. And I am carrying the story forward.

Not blocks. Spirals.

That's where I'm standing. That's what the fellowship would fund.

---

*Application submitted to the Thiel Fellowship*
*thielfellowship.org/apply*

# Chan Zuckerberg Initiative — Essential Open Source Software for Science (EOSS)

**Amount:** 2-year grants (Cycle 6 allocated $11.7M across multiple projects)
**Equity/IP:** None. Non-dilutive. Open-source requirement aligns with plan.
**Deadline:** Cycle-based — watch for Cycle 7 announcement
**Co-funders:** Kavli Foundation, Wellcome Trust
**Time to apply:** ~8-10 hours (Letter of Intent + full proposal if invited)
**Program page:** https://chanzuckerberg.com/eoss/
**Proposals:** https://chanzuckerberg.com/eoss/proposals/

---

## When to Apply

CZI EOSS runs in cycles. Cycle 6 (the most recent) closed in 2024.
**Cycle 7 has not been announced yet.**

**Strategy:** Monitor the CZI EOSS page for Cycle 7 opening. Best timing
is after Phase 1 demo is complete and you have some early community adoption
(e.g., iGEM teams using the compatibility engine). This is a Tier 2
opportunity — apply with a working demo, not before.

---

## What They Fund

CZI EOSS funds open-source software that is **critical to scientific research**.
They fund:
- **Maintenance and growth** of existing open-source tools
- **Community engagement** and sustainability
- Software that serves the biomedical and scientific research community

Past EOSS projects include: scikit-learn, NumPy, pandas, Jupyter, napari,
scanpy, Bioconductor packages, Galaxy, and other foundational tools.

### Three tracks:
1. **Essential OSS** — maintaining/improving existing tools with active users
2. **New OSS** — creating new open-source tools for underserved research areas
3. **Diversity & Inclusion** — expanding contributor diversity in scientific OSS

**LivingCAD fits Track 2** (new OSS for underserved area) once it has
a working demo and initial users.

---

## Personal Information
- **Name:** Sage Arthur Jordan Clokey (grandson of Art Clokey, creator of Gumby)
- **Email:** clokeyd.sage@gmail.com
- **Phone:** (805) 459-2396
- **Location:** Santa Cruz, CA
- **Affiliation:** UC Santa Cruz — B.S. Biomolecular Engineering & Bioinformatics

### Links
- **GitHub:** https://github.com/Sage-Clokey?tab=repositories
- **Website:** https://sage-clokey.github.io/
- **Bioinformatics portfolio:** https://sage-clokey.github.io/bioinformatics-projects.html

---

## Letter of Intent (Draft — for when cycle opens)

### Project Title
LivingCAD: Open-Source Organism-Scale Biodesign Infrastructure for
Synthetic Biology Research

### Summary (250 words)

LivingCAD is an open-source biodesign platform that bridges the gap between
human-language descriptions of biological function and synthesizable DNA
sequences optimized for specific chassis organisms. The platform integrates
large language models (for intent interpretation), protein language models
(for sequence generation), and a validated compatibility engine (for codon
optimization, regulatory element analysis, and pathway conflict detection).

The compatibility engine — including codon optimization for 5 chassis organisms,
regulatory element analysis across 24 characterized parts and 5 organism
classes, and pathway conflict detection across 12 metabolic profiles — is
fully open source. This infrastructure serves the synthetic biology research
community by providing organism-scale design validation that currently
requires either expensive proprietary platforms or manual literature curation.

The EOSS grant would fund: (1) documentation, testing, and packaging of the
open-source compatibility engine for community use; (2) integration with
existing scientific Python ecosystem (BioPython, Scanpy, Jupyter); (3)
community building through iGEM team partnerships and UCSC research
collaborations; (4) development of the regulatory layer using Enformer
for expression prediction.

LivingCAD fills an underserved niche in the scientific OSS ecosystem: there
are excellent tools for sequence analysis (BLAST, Bioconductor), gene
expression (DESeq2, Scanpy), and protein structure (AlphaFold) — but no
open-source tool that integrates these layers into an organism-scale design
system accessible via natural language.

### Milestones for 2-year grant:
- Year 1: Open-source compatibility engine packaged, documented, community of 50+ users
- Year 2: Regulatory layer (Enformer integration), 200+ users, published benchmark paper

---

## Budget (2-year estimate)

| Item | Amount | Justification |
|------|--------|---------------|
| Personnel (PI, 50% effort) | $80,000 | Lead development, community management |
| GPU compute | $30,000 | ESM-3 inference, Enformer predictions |
| API costs | $10,000 | Claude API for English layer |
| Community engagement | $15,000 | iGEM partnerships, conference travel |
| Infrastructure | $10,000 | Hosting, CI/CD, documentation site |
| **Total** | **$145,000** | |

---

## What Strengthens This Application

1. **Open-source is core**, not an afterthought — rooted in the Spiral Steward
   philosophy: "the grammar of life should not be owned"
2. **Fills a real gap** in the scientific Python ecosystem
3. **Integration with existing tools** (BioPython, Scanpy, Jupyter)
4. **Clear user community**: iGEM teams (400+/year), synbio researchers
5. **UCSC affiliation** — home of the Genome Browser, strong genomics community
6. **Founder story**: grandson of Art Clokey (creator of Gumby), carrying forward
   a lineage of giving life to dead matter — from clay to DNA
7. **Dual approach**: "The creation of the Living Age requires media to explain
   why and technology to show how" — building both the narrative and the tools

## What Could Weaken It

1. **Early stage** — CZI usually funds tools with existing user communities
2. **Solo developer** — they may prefer projects with established contributor bases
3. **Not purely biomedical** — the living architecture angle is unconventional

---

## Action Items

1. **Monitor:** Check https://chanzuckerberg.com/eoss/ monthly for Cycle 7 announcement
2. **Build first:** Complete Phase 1 demo and get initial users before applying
3. **Package the open-source core** as a standalone installable tool (pip install livingcad)
4. **Get iGEM adoption** — even 5-10 teams using the compatibility engine changes the application
5. **When cycle opens:** Submit Letter of Intent using draft above (adapt to their format)
6. **If invited:** Write full proposal (~15-20 pages)
7. **Timeline:** Realistic earliest application is late 2026 or 2027

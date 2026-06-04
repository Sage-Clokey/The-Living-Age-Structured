from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
    HRFlowable, Table, TableStyle, PageBreak, KeepTogether)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

W, H = letter

doc = SimpleDocTemplate(
    "/mnt/c/Users/SajcS/Desktop/Living works by the word/LivingWorks_SpiralSteward_BusinessPlan.pdf",
    pagesize=letter,
    leftMargin=0.85*inch, rightMargin=0.85*inch,
    topMargin=0.75*inch, bottomMargin=0.75*inch
)

styles = getSampleStyleSheet()

# ── Style Definitions ──────────────────────────────────────────────────────
DARK    = colors.HexColor('#06080a')
GREEN   = colors.HexColor('#7a9e7e')
GOLD    = colors.HexColor('#b8973a')
FLAME   = colors.HexColor('#4aaa5a')
RED     = colors.HexColor('#8a3a2a')
DIM     = colors.HexColor('#6a6860')
MID     = colors.HexColor('#aaa898')
BG2     = colors.HexColor('#f4f2ee')
ACCENT  = colors.HexColor('#1a3a1a')

cover_title = ParagraphStyle('CoverTitle', fontSize=32, fontName='Times-Italic',
    textColor=ACCENT, alignment=TA_CENTER, leading=38, spaceAfter=10)
cover_sub = ParagraphStyle('CoverSub', fontSize=13, fontName='Times-Roman',
    textColor=DIM, alignment=TA_CENTER, spaceAfter=6)
cover_byline = ParagraphStyle('CoverByline', fontSize=9, fontName='Helvetica',
    textColor=DIM, alignment=TA_CENTER, spaceAfter=4)

sec_label = ParagraphStyle('SecLabel', fontSize=7, fontName='Helvetica',
    textColor=FLAME, letterSpacing=4, spaceAfter=6, spaceBefore=24)
h1 = ParagraphStyle('H1', fontSize=18, fontName='Times-Roman',
    textColor=ACCENT, spaceAfter=10, spaceBefore=4, leading=22)
h2 = ParagraphStyle('H2', fontSize=12, fontName='Helvetica-Bold',
    textColor=ACCENT, spaceAfter=6, spaceBefore=14)
h3 = ParagraphStyle('H3', fontSize=10, fontName='Helvetica-Bold',
    textColor=colors.HexColor('#2a4a2a'), spaceAfter=4, spaceBefore=8)
body = ParagraphStyle('Body', fontSize=9.5, fontName='Times-Roman',
    leading=15, spaceAfter=8, textColor=DARK, alignment=TA_JUSTIFY)
body_small = ParagraphStyle('BodySm', fontSize=8.5, fontName='Times-Roman',
    leading=13, spaceAfter=6, textColor=DARK)
bullet = ParagraphStyle('Bullet', fontSize=9, fontName='Times-Roman',
    leading=14, spaceAfter=3, leftIndent=16, textColor=DARK)
quote = ParagraphStyle('Quote', fontSize=10.5, fontName='Times-Italic',
    leading=16, spaceAfter=8, spaceBefore=8, leftIndent=24, rightIndent=24,
    textColor=ACCENT, borderPadding=(8,0,8,16))
label_style = ParagraphStyle('Label', fontSize=7, fontName='Helvetica',
    textColor=DIM, letterSpacing=2)

def sp(n=8): return Spacer(1, n)
def hr(c=DIM, t=0.4): return HRFlowable(width="100%", thickness=t, color=c, spaceAfter=6, spaceBefore=6)
def gold_hr(): return HRFlowable(width="100%", thickness=1, color=GOLD, spaceAfter=8, spaceBefore=8)
def P(text, style=body): return Paragraph(text, style)
def B(text): return Paragraph(f"— {text}", bullet)
def Q(text, cite=""):
    t = f'<i>"{text}"</i>'
    if cite: t += f'<br/><font size="7" color="#b8973a">{cite}</font>'
    return Paragraph(t, quote)
def SL(text): return Paragraph(text.upper(), sec_label)
def H1(text): return Paragraph(text, h1)
def H2(text): return Paragraph(text, h2)
def H3(text): return Paragraph(text, h3)

def table(data, col_widths, header=True):
    t = Table(data, colWidths=col_widths)
    style = [
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('FONTNAME', (0,1), (-1,-1), 'Times-Roman'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG2]),
    ]
    if header:
        style += [
            ('BACKGROUND', (0,0), (-1,0), ACCENT),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ]
    t.setStyle(TableStyle(style))
    return t

# ══════════════════════════════════════════════════════════════════════════════
story = []

# ── COVER PAGE ────────────────────────────────────────────────────────────────
story.append(sp(80))
story.append(P("Living Works", cover_title))
story.append(P("& The Spiral Steward", ParagraphStyle('CoverTitle2', parent=cover_title, fontSize=22, spaceAfter=20)))
story.append(gold_hr())
story.append(sp(8))
story.append(P("Business Plan & Competitive Analysis", cover_sub))
story.append(P("AI-Driven Biological Design Platform · Living Architecture · The Living Age Initiative", cover_byline))
story.append(sp(12))
story.append(P("Sage Arthur Jordan Clokey · LivingWorks Initiative · 2026", cover_byline))
story.append(sp(60))
story.append(Q("Life is not a block you carve into shape. It is a spiral you cultivate.", "— LivingWorks Manifesto"))
story.append(sp(60))
story.append(hr())
story.append(P("Confidential — Not for Distribution", ParagraphStyle('conf', parent=cover_byline, fontSize=7, textColor=DIM)))
story.append(PageBreak())

# ── SECTION 0: EXECUTIVE SUMMARY ─────────────────────────────────────────────
story.append(SL("Executive Summary"))
story.append(H1("Mission & Vision"))
story.append(hr(FLAME, 1))
story.append(sp(4))
story.append(P(
    "Living Works is a platform for AI-driven biological design — enabling architects, scientists, and engineers "
    "to design with living systems rather than against them. Where traditional engineering kills life to impose "
    "control (trees become lumber, soil becomes substrate, ecosystems become resources), Living Works designs "
    "<i>growth processes</i> — structures that grow themselves, adapt to their environments, and repair damage "
    "without mechanical intervention."
))
story.append(P(
    "The philosophical foundation is articulated through the Spiral Steward framework: a leadership and design "
    "philosophy that replaces domination with stewardship, rigid blocks with adaptive spirals, and central control "
    "with decentralized intelligence. This is not merely an aesthetic preference — it is a response to a systemic "
    "failure of industrial-age design philosophy that has produced dead soil, collapsing ecosystems, brittle "
    "infrastructure, and soulless cities."
))
story.append(Q(
    "The industrial age was built on a single foundational error... Industrial engineering designs systems that "
    "must first kill what is living. This is not a failure of technology. It is a failure of design philosophy.",
    "— The Spiral Steward, LivingWorks"
))
story.append(P(
    "Living Works addresses this through two parallel engines: a <b>technology platform</b> (morphogenesis simulation, "
    "AI biological design, BioCAD) and a <b>philosophical movement</b> (Sagent Creed, True Republic, 8 Pillars series) "
    "that creates the cultural narrative making people want to use those tools."
))
story.append(sp(6))

data = [
    ['Component', 'Description', 'Audience'],
    ['Morphogenesis Engine', '3D simulation of biological growth processes', 'Universities, biotech labs'],
    ['AI Design Interface', 'Natural language → biological design', 'Architects, designers'],
    ['BioCAD Platform', 'Computer-aided design for living systems', 'Synthetic biology, materials companies'],
    ['Sagent Creed', 'Philosophical storytelling and media movement', 'Technologists, futurists, students'],
    ['True Republic', 'Podcast on decentralization, biology, and governance', 'Libertarian thinkers, philosophers'],
    ['8 Pillars Series', 'Educational video series on the Living Age', 'Broad public, scientists'],
]
story.append(table(data, [1.5*inch, 2.8*inch, 2.1*inch]))
story.append(PageBreak())

# ── SECTION 1: MARKET OVERVIEW ────────────────────────────────────────────────
story.append(SL("Part 1 — Market Overview"))
story.append(H1("Competitive Landscape"))
story.append(hr(FLAME, 1))
story.append(sp(4))

story.append(H2("Total Competitor Estimate"))
story.append(P(
    "The Living Works platform sits at the intersection of four distinct but converging markets. "
    "Estimating competitors requires segmenting by proximity to the core offering:"
))
data2 = [
    ['Segment', 'Estimated Competitors', 'Proximity to Living Works'],
    ['Direct: AI-driven biological design platforms', '10–15', 'High'],
    ['Synthetic biology engineering companies', '50+', 'Medium'],
    ['Bioinformatics / genome management tools', '100+', 'Medium-Low'],
    ['Living materials & biofabrication companies', '20–30', 'Medium'],
    ['Generative biology AI startups (emerging)', '20+', 'High'],
    ['Total relevant ecosystem', '200–250+', '—'],
]
story.append(table(data2, [2.6*inch, 1.8*inch, 1.9*inch]))
story.append(sp(4))
story.append(P(
    "Critically, <b>no major platform currently focuses on whole-organism morphology, 3D growth simulation, "
    "natural language → biology design, or living architecture as an integrated design environment.</b> "
    "This gap defines the Living Works opportunity."
))
story.append(sp(8))

story.append(H2("Market Segmentation"))
story.append(P("Competitors cluster into four primary categories, each representing a partial overlap with Living Works:"))
story.append(sp(4))
segs = [
    ["1 — AI-Driven Protein & Molecular Design",
     "Companies like Profluent, Generate Biomedicines, and EvolutionaryScale design proteins and molecules "
     "using large AI foundation models. Their scope is molecular — they do not address organism-level morphology, "
     "growth simulation, or living architecture. They are the closest technological analog but operate at "
     "a fundamentally different biological scale."],
    ["2 — Synthetic Biology Platforms",
     "Companies like Ginkgo Bioworks and Twist Bioscience engineer microbes for industrial manufacturing. "
     "Their design paradigm remains within the industrial framework — organisms as factories — rather than "
     "the Living Works paradigm of organisms as architecture and living systems as design medium."],
    ["3 — Bioinformatics Infrastructure",
     "Benchling, DNAnexus, and Seven Bridges manage biological data and lab workflows. These are analysis "
     "and data-management tools, not creation engines. They represent the informational substrate that "
     "Living Works would integrate and transform into design tools."],
    ["4 — Living Materials & Biofabrication",
     "Ecovative (mycelium packaging), MycoWorks (fungal leather), and Modern Meadow (bio-grown textiles) "
     "produce specific living materials but lack a generalized design platform. They are potential customers "
     "or partners of Living Works rather than direct competitors."],
]
for title, text in segs:
    story.append(KeepTogether([H3(title), P(text), sp(4)]))

story.append(sp(8))
story.append(H2("Competitive Dynamics"))
story.append(P(
    "This is a <b>rapidly emerging but not yet crowded</b> market at the organism-design and living-architecture level. "
    "The molecular and synthetic biology markets are consolidating around a few well-funded platforms. "
    "However, the intersection of morphogenesis simulation, AI design interfaces, and living architecture "
    "remains an open frontier. The market is in the early-growth phase of the S-curve: category definition "
    "is still occurring, which means first-movers who define the vocabulary and tooling have disproportionate "
    "influence over how the industry develops."
))
story.append(Q(
    "Almost no startups exist in the category of Morphological BioCAD — computer-aided design for organism "
    "shape and growth. And your morphogenesis simulations are exactly that direction.",
    "— Competitive analysis, LivingWorks documents"
))
story.append(PageBreak())

# ── SECTION 2: COMPETITOR DEEP DIVES ─────────────────────────────────────────
story.append(SL("Part 2 — Competitor Deep Dives"))
story.append(H1("Top 3 Competitors"))
story.append(hr(FLAME, 1))
story.append(sp(4))

# ── Competitor 1: Ginkgo ──────────────────────────────────────────────────────
story.append(H2("Competitor 1 — Ginkgo Bioworks"))
story.append(sp(2))
data_g = [
    ['Location', 'Stage', 'Founded', 'Funding / Revenue'],
    ['Boston, Massachusetts', 'Commercial platform (public)', '2008', 'Raised $1B+ · NYSE: DNA'],
]
story.append(table(data_g, [1.7*inch, 1.7*inch, 1.1*inch, 1.9*inch]))
story.append(sp(6))

story.append(H3("Product / Technology Description"))
story.append(P(
    "Ginkgo Bioworks operates the largest biological engineering platform in the world. Their model is "
    "'foundry + codebase': automated robotic labs that run thousands of biological experiments in parallel, "
    "combined with a proprietary biological parts library and AI-driven strain engineering. They design "
    "organisms — primarily microbes — for pharmaceutical manufacturing, agricultural applications, food "
    "ingredient production, and industrial chemicals. Ginkgo does not build living structures or simulate "
    "morphogenesis; they engineer metabolic pathways within organisms."
))
story.append(H3("Key Strengths"))
for s in [
    "Massive automated lab infrastructure — the largest synthetic biology foundry in existence",
    "Deep partnership network: Bayer, Moderna, Roche, dozens of major industrial clients",
    "Proprietary biological parts database built over 15+ years of experiments",
    "Strong brand as the dominant synthetic biology platform",
    "Public company status providing capital access and credibility",
]:
    story.append(B(s))
story.append(sp(4))
story.append(H3("Market Traction"))
story.append(P(
    "Hundreds of active programs with partners across pharma, agriculture, food, and industrial chemicals. "
    "NYSE-listed. Revenues in the hundreds of millions. The company has become the default outsourced "
    "biology platform for large enterprises wanting to incorporate biological manufacturing."
))
story.append(H3("Critical Framing — What Their CEO Would Say"))
story.append(Q(
    "Biology is engineering. Whoever builds the infrastructure platform wins. We already built the largest one. "
    "We have the partnerships, the data, the automation, and the brand. A new entrant designing organisms "
    "cannot compete with 15 years of biological parts data and the relationships we have at every major pharma "
    "and agricultural company on earth. Their advantage — scale — is insurmountable for any startup that tries "
    "to replicate it directly.",
    "— Ginkgo CEO perspective"
))
story.append(P(
    "<b>Honest assessment of their advantage:</b> Ginkgo's moat is data accumulation and industrial automation. "
    "No startup can replicate 15 years of biological parts data quickly. However, Ginkgo operates entirely "
    "within the industrial paradigm — they engineer microbes as factories, not as living design systems. "
    "Living Works does not compete with Ginkgo at the microbial engineering level; it operates above that "
    "layer, designing morphological outcomes that Ginkgo's tools cannot address."
))
story.append(sp(8))

# ── Competitor 2: Benchling ───────────────────────────────────────────────────
story.append(H2("Competitor 2 — Benchling"))
story.append(sp(2))
data_b = [
    ['Location', 'Stage', 'Founded', 'Funding / Revenue'],
    ['San Francisco, California', 'Commercial (widely adopted)', '2012', 'Raised ~$400M+'],
]
story.append(table(data_b, [1.7*inch, 1.7*inch, 1.1*inch, 1.9*inch]))
story.append(sp(6))

story.append(H3("Product / Technology Description"))
story.append(P(
    "Benchling is the operating system for biotech R&D — a software platform providing DNA design tools, "
    "lab data management, experiment tracking, and collaboration infrastructure. It is a records and workflow "
    "system, not a design creation engine. Benchling tells scientists where their data is and helps them "
    "design gene sequences; it does not simulate growth, model morphogenesis, or generate novel biological "
    "forms. Think of it as the Google Docs of biotech — critical infrastructure, but not a design tool."
))
story.append(H3("Key Strengths"))
for s in [
    "Massive installed user base — used by 1,000+ biotech companies including Moderna and Regeneron",
    "Deep enterprise integration: removing Benchling from an active lab is extremely disruptive",
    "Network effect: the more companies use it, the more valuable shared data and protocols become",
    "Strong reputation for reliability in regulated environments (FDA compliance features)",
]:
    story.append(B(s))
story.append(sp(4))
story.append(H3("Market Traction"))
story.append(P(
    "Over 1,000 biotech companies, including the majority of top-20 pharma. Deeply embedded in R&D "
    "workflows. Used from early-stage startups to Moderna-scale operations. Became the de facto standard "
    "for biotech lab management after a decade of network effects."
))
story.append(H3("Critical Framing — What Their CEO Would Say"))
story.append(Q(
    "Biology companies run on our platform already. The network effect of data makes us impossible to replace. "
    "We don't just manage data — we are the connective tissue of the entire biotech industry. Any new biology "
    "design tool will eventually need to integrate with us, which means we will absorb or partner with "
    "whoever wins in biological design. We are the platform on which platforms are built.",
    "— Benchling CEO perspective"
))
story.append(P(
    "<b>Honest assessment of their advantage:</b> Benchling's moat is switching cost. Once a company's "
    "experiments, protocols, and data history live in Benchling, migration is painful. However, Benchling "
    "is a data management tool, not a creation engine. Living Works is a design platform — a different "
    "layer of the stack entirely. Benchling is more likely a future integration partner than a direct competitor."
))
story.append(sp(8))

# ── Competitor 3: Generate Biomedicines ──────────────────────────────────────
story.append(H2("Competitor 3 — Generate Biomedicines"))
story.append(sp(2))
data_gen = [
    ['Location', 'Stage', 'Founded', 'Funding / Revenue'],
    ['Cambridge, Massachusetts', 'Clinical programs beginning', '2018', 'Raised ~$700M+'],
]
story.append(table(data_gen, [1.7*inch, 1.7*inch, 1.1*inch, 1.9*inch]))
story.append(sp(6))

story.append(H3("Product / Technology Description"))
story.append(P(
    "Generate Biomedicines builds AI foundation models for protein and antibody generation — essentially GPT "
    "for biology at the molecular level. Their platform generates novel protein sequences optimized for "
    "specific therapeutic functions. This is the most direct technological analog to Living Works' AI "
    "design interface, but operates exclusively at the molecular scale: protein folding and function, "
    "not organism morphology, tissue architecture, or living structures."
))
story.append(H3("Key Strengths"))
for s in [
    "State-of-the-art AI foundation models trained on massive protein sequence datasets",
    "Strong investor base — backed by top-tier VC firms (ARCH, Flagship, etc.)",
    "Clinical validation pathway — moving AI-designed proteins into human trials",
    "First-mover in AI-generated therapeutics — the category leader",
    "Deep scientific team from academic protein design and ML research",
]:
    story.append(B(s))
story.append(sp(4))
story.append(H3("Market Traction"))
story.append(P(
    "Multiple AI-generated molecules entering clinical trials. Partnerships with major pharma for "
    "co-development of AI-designed therapeutics. Widely covered in Nature, Science, and industry press "
    "as a category-defining company. $700M+ raised reflects strong investor conviction in AI-bio design."
))
story.append(H3("Critical Framing — What Their CEO Would Say"))
story.append(Q(
    "Whoever builds the best biological foundation model will control the future of medicine — and "
    "eventually all biology. We are building the large language model of life. In five years, every "
    "biological design tool will be powered by foundation models like ours. A platform that simulates "
    "growth without the underlying molecular design layer is like Photoshop without pixels — the "
    "interface without the substance.",
    "— Generate Biomedicines CEO perspective"
))
story.append(P(
    "<b>Honest assessment of their advantage:</b> Generate's foundation models represent the deepest "
    "AI capability in biology currently funded. Their weakness is scope: they design molecules, not "
    "organisms. They have no morphogenesis capability, no architectural application, and no living "
    "materials focus. Living Works operates at higher organizational scales — tissue, organism, "
    "ecosystem — that their molecular models do not address. Integration (not competition) is "
    "the strategic relationship: Living Works could use molecular foundation models as a substrate "
    "layer within a broader morphogenetic design platform."
))
story.append(PageBreak())

# ── SECTION 3: COMPETITIVE POSITIONING ───────────────────────────────────────
story.append(SL("Part 3 — Competitive Positioning"))
story.append(H1("Positioning & Differentiation"))
story.append(hr(FLAME, 1))
story.append(sp(4))

story.append(H2("Positioning Matrix"))
story.append(P("Competitors mapped across two critical axes: biological scale (molecular → organism/ecosystem) and tool type (data management → design creation engine):"))
story.append(sp(4))

data_pos = [
    ['Company', 'Biological Scale', 'Tool Type', 'Living Architecture Focus'],
    ['Ginkgo Bioworks', 'Microbial / metabolic', 'Engineering platform', 'None'],
    ['Benchling', 'Gene / sequence level', 'Data management', 'None'],
    ['Generate Biomedicines', 'Protein / molecular', 'AI generation', 'None'],
    ['Ecovative / MycoWorks', 'Material (mycelium)', 'Manufacturing', 'Partial'],
    ['Living Works', 'Cell → organism → ecosystem', 'Design creation engine', 'Core focus'],
]
story.append(table(data_pos, [1.5*inch, 1.6*inch, 1.6*inch, 1.7*inch]))
story.append(sp(8))

story.append(H2("What Is Genuinely Different About Living Works"))
story.append(P(
    "Most competitors design <b>genes or proteins</b>. Living Works designs <b>growth processes</b>. "
    "This is a fundamentally different level of biological abstraction — the difference between "
    "designing a sentence and designing a narrative that unfolds over time."
))
diffs = [
    ("Higher-Order Biological Design",
     "Living Works operates at the tissue, organ, organism, and ecosystem scale — above where any "
     "current commercial platform focuses. Morphogenesis (how organisms grow into their shapes) is "
     "essentially unaddressed by existing design tools."),
    ("Growth Rules Instead of Objects",
     "Traditional engineering designs objects. Living Works designs growth rules that produce objects. "
     "As stated in the LivingWorks manifesto: 'You define growth rules, and let the geometry emerge "
     "from simulation... Natural language prompts translate into physics parameters.' This is a "
     "paradigm shift in design methodology."),
    ("Cross-Scale Integration",
     "The platform integrates design from DNA → cells → tissues → organisms → architecture → ecosystem. "
     "No current platform spans this range. This cross-scale coherence is the architectural vision "
     "of the Living Age."),
    ("Living Architecture as Primary Application",
     "No existing biotech, synthetic biology, or bioinformatics platform addresses the built environment "
     "as a primary application. Living Works targets a multi-trillion dollar construction and "
     "infrastructure industry with a zero-waste, carbon-negative, self-repairing design paradigm."),
    ("Philosophical Narrative as Strategic Moat",
     "The Spiral Steward philosophy and associated media (Sagent Creed, True Republic, 8 Pillars) "
     "creates cultural demand for the technology. This is analogous to how SpaceX's Mars narrative "
     "creates public support for rocket technology — the philosophy makes the technology desirable "
     "before it is commercially available."),
]
for title, text in diffs:
    story.append(KeepTogether([H3(title), P(text), sp(4)]))

story.append(sp(6))
story.append(H2("Unfair Advantages — Why This Difference Is Defensible"))

advs = [
    ("1 — Novel Technology: Morphological BioCAD",
     "A physics + biology simulation engine for 3D growth is technically distinct from protein design AI "
     "or metabolic engineering platforms. The underlying simulation architecture — modeling branching "
     "growth, nutrient gradients, biomechanical forces, and developmental pathways — represents a new "
     "category of software that is difficult to replicate quickly. The LivingWorks simulation engine "
     "already demonstrates this: 'Cells grow, interact physically, and divide, producing complex 3D "
     "forms. The same way biological organisms develop from a handful of cells into branching, folding, "
     "asymmetric structures — unrepeatable, alive.'"),
    ("2 — First-Mover in an Undefined Category",
     "The category of 'biological design software for living architecture' does not yet have a dominant "
     "player. First-movers who define the vocabulary, the workflow, and the community in an emerging "
     "category establish durable advantages through network effects, mindshare, and the ability to "
     "set standards. Living Works is positioned to define this category before it consolidates."),
    ("3 — Integrated Philosophy + Technology Platform",
     "Competitors compete on technology metrics alone. Living Works has a coherent philosophical "
     "framework — the Spiral Steward — that attracts a specific community of scientists, architects, "
     "and thinkers who believe the industrial design paradigm is morally and ecologically bankrupt. "
     "As stated in the Moral Case for Living Architecture: 'The industrial age taught humanity a "
     "single devastating lie: that humans are separate from nature. From this lie came monoculture "
     "agriculture that destroys soil; cities built as dead zones instead of living habitats.' "
     "This narrative creates a self-selecting, highly motivated user community that competitors "
     "cannot simply copy."),
    ("4 — Target Market Gap",
     "Architects, landscape designers, urban planners, and materials engineers are not served by "
     "any current biotech platform. Living Works enters a market of potential users who currently "
     "have no tools at all for biological design — a greenfield opportunity rather than a "
     "head-to-head competitive fight."),
    ("5 — Bioinformatics as Stewardship — Unique Intellectual Framework",
     "The LivingWorks conceptual framework reframes bioinformatics not as analysis but as stewardship: "
     "'Bioinformatics offers a different posture: attention before intervention. It trains you to watch "
     "patterns that no human mind can hold at once... It reveals that life is not centrally designed, "
     "but emergent — a decentralized order created through layers of feedback, adaptation, and symbiosis.' "
     "This framing attracts researchers and developers who are philosophically aligned with the mission, "
     "creating a talent and community moat."),
]
for title, text in advs:
    story.append(KeepTogether([H3(title), P(text), sp(6)]))

story.append(PageBreak())

# ── SECTION 4: TECHNOLOGY PLATFORM ───────────────────────────────────────────
story.append(SL("Part 4 — Technology Platform"))
story.append(H1("Living Works — Core Technologies"))
story.append(hr(FLAME, 1))
story.append(sp(4))
story.append(P(
    "Living Works is built on four core technology components that together enable end-to-end "
    "biological design — from natural language intent to 3D growth simulation to fabrication planning."
))
story.append(sp(6))

techs = [
    ("1 — Morphogenesis Engine",
     "A 3D simulation system that models biological growth as a physics process. Rather than defining "
     "static geometry, users define growth rules and the system simulates how those rules produce form. "
     "As described in the LivingWorks simulation engine: 'Natural language prompts translate into physics "
     "parameters. The interpreter reads intention and generates a GrowthProgram. The simulation runs. "
     "The form appears.' Modeled parameters include branching systems (trees, coral, vasculature), "
     "cellular growth and division, nutrient gradients, biomechanical forces, and developmental pathways.",
     [("grow upward", "anisotropy +Y"),
      ("branching", "division rate ↑"),
      ("stiff structure", "repulsion ↑"),
      ("compact form", "adhesion ↑"),
      ("noisy/organic", "noise strength ↑")]),
    ("2 — AI Biological Design Interface",
     "A natural language interface for biological design. Users describe the biological structure "
     "or behavior they want; the AI translates intent into growth parameters, gene pathway suggestions, "
     "and structural simulations. Example prompt: 'Design a self-supporting branching structure "
     "optimized for wind resistance and water collection.' The system returns growth models, gene "
     "pathway suggestions, and structural simulations. This makes biological design accessible to "
     "architects and designers without deep molecular biology expertise.", []),
    ("3 — BioCAD Platform",
     "Computer-aided design tools purpose-built for living systems — comparable to Autodesk for "
     "buildings or Blender for 3D graphics, but for biology. Features include: genome editing "
     "planning, tissue architecture modeling, ecosystem design simulation, living material library "
     "integration, and organism blueprinting. The BioCAD platform transforms existing bioinformatics "
     "tools from analysis instruments into design instruments.", []),
    ("4 — Bioinformatics Integration & Living Materials Library",
     "Integration with existing genome browsers, pathway analysis tools, single-cell data platforms, "
     "and metabolic modeling software — transforming them from analysis tools into design resources. "
     "Paired with a database of biological building blocks (fungal mycelium, plant tissue scaffolds, "
     "bacterial cellulose, coral-like mineralization systems) with growth rules and environmental "
     "requirements for each.", []),
]

for title, desc, params in techs:
    items = [H3(title), P(desc)]
    if params:
        pdata = [['Natural Language Input', 'Physics Parameter']] + [[a, b] for a, b in params]
        items.append(table(pdata, [2.5*inch, 2.5*inch]))
    items.append(sp(8))
    story.append(KeepTogether(items))

story.append(sp(4))
story.append(H2("Example Applications"))
apps = [
    ['Application', 'Description', 'Impact'],
    ['Living Architecture', 'Buildings grown from mycelium, engineered plants, bacterial cellulose', 'Carbon-negative, self-repairing structures'],
    ['Ecosystem Engineering', 'Design landscapes that restore soil, filter water, regulate climate', 'Regenerative infrastructure'],
    ['Biological Manufacturing', 'Grow leather alternatives, structural composites, insulation', 'Zero-waste materials production'],
    ['Carbon-Negative Construction', 'Structures that grow, absorb CO₂, and self-repair', 'Net-positive environmental construction'],
]
story.append(table(apps, [1.5*inch, 2.8*inch, 2.1*inch]))
story.append(PageBreak())

# ── SECTION 5: BUSINESS MODEL ─────────────────────────────────────────────────
story.append(SL("Part 5 — Business Model & Revenue"))
story.append(H1("Revenue Model"))
story.append(hr(FLAME, 1))
story.append(sp(4))

story.append(H2("Software Platform (SaaS)"))
story.append(P("Subscription-based access to the Living Works design platform, tiered by user type:"))
rev_data = [
    ['Tier', 'Price / Month', 'Target Users'],
    ['Academic', '$50–$200', 'Universities, research labs, students'],
    ['Startup', '$500', 'Early-stage biotech, design studios'],
    ['Enterprise', '$2,000+', 'Architecture firms, materials companies, biotech'],
]
story.append(table(rev_data, [1.5*inch, 1.5*inch, 3.4*inch]))
story.append(sp(8))

story.append(H2("AI Design Services"))
story.append(P(
    "Custom biological design projects for enterprise clients who require bespoke organism or "
    "materials design. Clients include materials companies developing bio-grown products, construction "
    "companies exploring living architecture pilots, and biotech firms needing morphological design "
    "capabilities beyond standard platform offerings."
))
story.append(sp(6))

story.append(H2("IP Licensing"))
story.append(P(
    "Patents on biological growth algorithms, engineered organism designs, and living material systems "
    "created through the platform. As the platform accumulates novel biological designs, the IP portfolio "
    "becomes a standalone revenue stream licensable to manufacturers."
))
story.append(sp(6))

story.append(H2("Media & Community Revenue (Philosophy Layer)"))
for src in ["Patreon / community memberships", "YouTube ad revenue (Sagent Creed, 8 Pillars series)",
            "Books and published works", "Courses and educational content",
            "Speaking engagements and consulting"]:
    story.append(B(src))
story.append(PageBreak())

# ── SECTION 6: ROADMAP ────────────────────────────────────────────────────────
story.append(SL("Part 6 — Development Roadmap"))
story.append(H1("Three-Phase Roadmap"))
story.append(hr(FLAME, 1))
story.append(sp(4))

phases = [
    ("Phase 1 — Foundation (Years 1–2)",
     "Build core technology stack and establish early community.",
     ["Morphogenesis simulation engine (MVP)", "AI design interface (natural language → growth params)",
      "Basic BioCAD platform", "Sagent Creed media launch", "Early adopters: universities, synthetic biology labs",
      "Seed funding or academic grants", "Open-source morphogenesis tools to seed developer community"]),
    ("Phase 2 — Expansion (Years 3–5)",
     "Scale platform capabilities and establish commercial partnerships.",
     ["Living material design modules", "Architecture simulation integration",
      "Advanced AI models trained on biological design data",
      "Partnerships with architecture firms and materials companies",
      "True Republic podcast and 8 Pillars series at scale",
      "Series A funding targeting AI-bio design investors"]),
    ("Phase 3 — Living Age Infrastructure (Years 5–10)",
     "Enable programmable ecosystems and living infrastructure at civilizational scale.",
     ["Programmable ecosystem design tools", "Organism-scale design for living infrastructure",
      "Government and municipal partnerships for regenerative city design",
      "IP licensing revenue from patented biological designs",
      "Established as the design software standard for living systems"]),
]
for title, subtitle, items in phases:
    story.append(KeepTogether([
        H2(title),
        P(f"<i>{subtitle}</i>"),
    ] + [B(i) for i in items] + [sp(8)]))

story.append(PageBreak())

# ── SECTION 7: PHILOSOPHY LAYER ───────────────────────────────────────────────
story.append(SL("Part 7 — Philosophy & Media Movement"))
story.append(H1("The Spiral Steward Framework"))
story.append(hr(FLAME, 1))
story.append(sp(4))
story.append(Q(
    "Life is not a resource. Life is a language. And the Steward of Life is learning to speak it.",
    "— The Spiral Steward, LivingWorks"
))
story.append(P(
    "The Spiral Steward is not just a brand name — it is the philosophical foundation that distinguishes "
    "Living Works from every other biotech platform. Where competitors operate within the industrial "
    "engineering paradigm (biology as manufacturing), Living Works operates within a stewardship paradigm: "
    "biology as design partner."
))
story.append(sp(4))

story.append(H2("The Core Argument: Spiral vs. Block"))
story.append(P(
    "The LivingWorks website articulates the fundamental opposition between two design philosophies "
    "that have competed throughout civilization:"
))
sb_data = [
    ['THE BLOCK (Industrial Age)', 'THE SPIRAL (Living Age)'],
    ['Rigid hierarchy', 'Adaptive growth'],
    ['Central control', 'Distributed intelligence'],
    ['Static structure', 'Continuous evolution'],
    ['Manufactured from dead matter', 'Grown from living systems'],
    ['Domination over nature', 'Participation with nature'],
    ['Monoculture (uniformity)', 'Biodiversity (resilience)'],
    ['Straight lines and grids', 'Spirals and branching forms'],
]
t_sb = Table(sb_data, colWidths=[3.0*inch, 3.0*inch])
t_sb.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (0,0), colors.HexColor('#3a1a1a')),
    ('BACKGROUND', (1,0), (1,0), ACCENT),
    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (-1,-1), 8.5),
    ('FONTNAME', (0,1), (-1,-1), 'Times-Roman'),
    ('ROWBACKGROUNDS', (0,1), (0,-1), [colors.HexColor('#fff0f0'), colors.HexColor('#ffe8e8')]),
    ('ROWBACKGROUNDS', (1,1), (1,-1), [colors.HexColor('#f0fff0'), colors.HexColor('#e8ffe8')]),
    ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#cccccc')),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
]))
story.append(t_sb)
story.append(sp(8))

story.append(H2("Spiral Steward Principles (from LivingWorks website)"))
principles = [
    ("Stewardship Instead of Control",
     "The goal is not domination but guidance. Like a gardener rather than a machine operator. "
     "The Spiral Steward cultivates conditions where healthy systems can grow, rather than forcing "
     "predetermined outcomes."),
    ("Emergence",
     "Complex systems arise from simple rules. A Spiral Steward designs conditions, not outcomes. "
     "As the website states: 'When you do computational biology, you are forced into humility.'"),
    ("Decentralization",
     "Living systems distribute intelligence — neural networks, fungal networks, ecosystems. "
     "The Spiral Steward builds structures that support decentralized intelligence and preserve feedback."),
    ("Adaptation",
     "Living systems respond to change; rigid systems break. Design for resilience means designing "
     "for adaptation, not optimization for a single predicted condition."),
    ("Long-Term Thinking",
     "Growth unfolds across time. Stewards work with generations, not quarters. "
     "The website articulates this as thinking in spirals rather than straight lines."),
]
for title, text in principles:
    story.append(KeepTogether([H3(title), P(text), sp(4)]))

story.append(sp(6))
story.append(H2("The Sagent — Identity and Mission"))
story.append(P(
    "The Sagent — Sage Arthur Jordan Clokey — is the philosophical voice behind Living Works. "
    "As described on the website: 'A Sagent is not an agent of worldly rulers. He is an agent of "
    "divine wisdom. To be a Sagent is to reject service to human hierarchies and to become instead "
    "an instrument of the unchanging law written on every human heart.'"
))
story.append(Q(
    "When every heart becomes a throne, no crown is needed.",
    "— The Sagent Creed"
))
story.append(P(
    "The Sagent walks the path between faiths and philosophies — Islam to Taoism, natural law to "
    "living systems — finding in each tradition the same light refracted through a different prism. "
    "This cross-tradition synthesis makes the Living Works philosophy accessible to scientists, "
    "architects, philosophers, and technologists from diverse backgrounds."
))
story.append(sp(6))

story.append(H2("The True Republic — Political Philosophy"))
story.append(P(
    "The True Republic manifesto on the website extends the Living Works philosophy into governance: "
    "'The True Republic is not a place to be founded — it is a truth to be lived. It arises in each "
    "heart that refuses to rule or be ruled.' The political philosophy mirrors the biological design "
    "philosophy: decentralization, emergence, and stewardship applied to human social organization."
))
story.append(Q(
    "Truth is Law. Conscience is Crown. Every Soul is Sovereign.",
    "— Manifesto of the True Republic, LivingWorks"
))
story.append(PageBreak())

# ── SECTION 8: COMBINED STRATEGY ─────────────────────────────────────────────
story.append(SL("Part 8 — Combined Strategy"))
story.append(H1("Technology + Philosophy: The Living Age Initiative"))
story.append(hr(FLAME, 1))
story.append(sp(4))
story.append(P(
    "The strategic insight behind Living Works is that technology alone does not create civilizational change — "
    "narratives do. The philosophy creates cultural demand; the technology creates real-world solutions. "
    "History supports this: Tesla and SpaceX's Mars narrative, Apple's 'Think Different,' Wikipedia's "
    "open knowledge philosophy — each paired a transformative technology with a compelling cultural story."
))
story.append(sp(6))

story.append(H2("Strategic Brand Structure"))
story.append(P(
    "The two engines should maintain distinct identities to maximize effectiveness in their respective domains:"
))
brand_data = [
    ['Brand', 'Role', 'Audience', 'Tone'],
    ['Spiral BioDesign\n(Technology)', 'Serious biotech platform — morphogenesis, AI design, BioCAD', 'Investors, enterprises, universities', 'Scientific, credible'],
    ['The Sagent Creed\n(Philosophy)', 'Cultural narrative movement — videos, podcast, philosophy', 'Public, technologists, students', 'Mythic, inspiring'],
]
story.append(table(brand_data, [1.4*inch, 2.3*inch, 1.7*inch, 1.0*inch]))
story.append(sp(6))

story.append(H2("The Moral Case — Why This Matters Beyond Business"))
story.append(P(
    "The LivingWorks moral framework, authored through the Spiral Steward and the Moral Case for "
    "Living Architecture, articulates stakes that go beyond market opportunity:"
))
for point in [
    "Block architecture perpetuates social harm, cognitive inequality, and ecological destruction",
    "Dead-matter construction produces environments that injure the people who inhabit them",
    "The built environment teaches the mind how to think — and rigid grids produce rigid cognition",
    "Living systems as design medium restores the human-nature relationship industrial civilization severed",
    "This is not a product launch — it is the beginning of the Living Age",
]:
    story.append(B(point))

story.append(sp(8))
story.append(gold_hr())
story.append(sp(8))
story.append(Q(
    "Industrial civilization built with blocks. The next civilization will build with living systems. "
    "Living Works provides the tools. Spiral Stewards guide their use.",
    "— Living Works Initiative"
))
story.append(sp(16))
story.append(hr())
story.append(P("LivingWorks Initiative · Sage Arthur Jordan Clokey · 2026 · Confidential",
    ParagraphStyle('foot', parent=body_small, alignment=TA_CENTER, textColor=DIM, fontSize=7.5)))

doc.build(story)
print("PDF created successfully.")

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

BASE = "/mnt/c/Users/SajcS/Desktop/Living works by the word/business plan pitch prompts/"

# ── Colour palette ──────────────────────────────────────────────────────────
DARK   = colors.HexColor("#1a2332")
GREEN  = colors.HexColor("#2d6a4f")
TEAL   = colors.HexColor("#40916c")
LIGHT  = colors.HexColor("#f0f4f0")
WHITE  = colors.white
GREY   = colors.HexColor("#555555")

# ── Style helpers ───────────────────────────────────────────────────────────
def make_styles():
    s = getSampleStyleSheet()
    base = dict(fontName="Helvetica", fontSize=11, leading=16,
                textColor=DARK, spaceAfter=6)
    styles = {
        "doc_title": ParagraphStyle("doc_title", **{**base,
            "fontName":"Helvetica-Bold","fontSize":28,"leading":34,
            "textColor":WHITE,"alignment":TA_CENTER,"spaceAfter":10}),
        "doc_sub":   ParagraphStyle("doc_sub", **{**base,
            "fontName":"Helvetica","fontSize":13,"textColor":WHITE,
            "alignment":TA_CENTER,"spaceAfter":4}),
        "h1": ParagraphStyle("h1", **{**base,
            "fontName":"Helvetica-Bold","fontSize":20,"leading":26,
            "textColor":GREEN,"spaceBefore":18,"spaceAfter":8}),
        "h2": ParagraphStyle("h2", **{**base,
            "fontName":"Helvetica-Bold","fontSize":15,"leading":20,
            "textColor":TEAL,"spaceBefore":14,"spaceAfter":6}),
        "h3": ParagraphStyle("h3", **{**base,
            "fontName":"Helvetica-Bold","fontSize":12,"leading":17,
            "textColor":DARK,"spaceBefore":10,"spaceAfter":4}),
        "body": ParagraphStyle("body", **{**base,
            "alignment":TA_JUSTIFY,"leading":17}),
        "bullet": ParagraphStyle("bullet", **{**base,
            "leftIndent":18,"bulletIndent":6,"spaceAfter":3}),
        "quote": ParagraphStyle("quote", **{**base,
            "fontName":"Helvetica-Oblique","fontSize":12,"leading":18,
            "leftIndent":24,"rightIndent":24,"textColor":GREEN,
            "spaceBefore":8,"spaceAfter":8}),
        "caption": ParagraphStyle("caption", **{**base,
            "fontSize":9,"textColor":GREY,"alignment":TA_CENTER}),
        "label": ParagraphStyle("label", **{**base,
            "fontName":"Helvetica-Bold","fontSize":10,"textColor":WHITE}),
    }
    return styles

def cover_table(title, subtitle, date="March 2026"):
    """Dark full-width cover banner."""
    data = [[Paragraph(title, make_styles()["doc_title"])],
            [Paragraph(subtitle, make_styles()["doc_sub"])],
            [Paragraph(date, make_styles()["doc_sub"])]]
    t = Table(data, colWidths=[6.5*inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,-1), DARK),
        ("TOPPADDING",  (0,0),(-1,-1), 20),
        ("BOTTOMPADDING",(0,0),(-1,-1), 20),
        ("LEFTPADDING", (0,0),(-1,-1), 30),
        ("RIGHTPADDING",(0,0),(-1,-1), 30),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[DARK]),
    ]))
    return t

def section_rule():
    return HRFlowable(width="100%", thickness=1, color=TEAL, spaceAfter=6, spaceBefore=6)

def info_table(rows, col_widths=None):
    """Two-column key/value table."""
    if col_widths is None:
        col_widths = [2.2*inch, 4.3*inch]
    st = make_styles()
    data = [[Paragraph(f"<b>{k}</b>", st["body"]),
             Paragraph(v, st["body"])] for k,v in rows]
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(0,-1), LIGHT),
        ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#ccddcc")),
        ("TOPPADDING",(0,0),(-1,-1),6),
        ("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LEFTPADDING",(0,0),(-1,-1),8),
        ("RIGHTPADDING",(0,0),(-1,-1),8),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
    ]))
    return t

def comparison_table(headers, rows):
    """Generic comparison table."""
    st = make_styles()
    hdr = [Paragraph(f"<b>{h}</b>", st["label"]) for h in headers]
    body_rows = [[Paragraph(str(c), st["body"]) for c in r] for r in rows]
    n = len(headers)
    col_w = [6.5*inch/n]*n
    t = Table([hdr]+body_rows, colWidths=col_w)
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0), GREEN),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, LIGHT]),
        ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#ccddcc")),
        ("TOPPADDING",(0,0),(-1,-1),6),
        ("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LEFTPADDING",(0,0),(-1,-1),8),
        ("RIGHTPADDING",(0,0),(-1,-1),8),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
    ]))
    return t

def bullets(items, st):
    return [Paragraph(f"• {item}", st["bullet"]) for item in items]

def build_pdf(filename, story):
    path = BASE + filename
    doc = SimpleDocTemplate(
        path, pagesize=letter,
        leftMargin=inch, rightMargin=inch,
        topMargin=0.9*inch, bottomMargin=0.9*inch,
        title=filename.replace("_"," ").replace(".pdf","")
    )
    doc.build(story)
    print(f"✓  {filename}")


# ════════════════════════════════════════════════════════════════════════════
# 1. Business Plan — The Living Age Initiative
# ════════════════════════════════════════════════════════════════════════════
def pdf_business_plan():
    st = make_styles()
    story = []

    story.append(cover_table(
        "The Living Age Initiative",
        "Business Plan — Living Works by the Word"))
    story.append(Spacer(1, 0.3*inch))

    # Mission
    story.append(Paragraph("Mission", st["h1"]))
    story.append(section_rule())
    story.append(Paragraph(
        "Build tools and ideas that enable humanity to design with living systems — "
        "shifting civilization from rigid mechanical structures to adaptive, biological ones. "
        "Living Works by the Word operates two parallel, mutually reinforcing engines: "
        "a <b>Technology Platform</b> and a <b>Philosophical Media Movement</b>.",
        st["body"]))
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph(
        "<i>Think of it as Tesla (technology) paired with the Elon Musk narrative (movement), "
        "or Apple (computer) paired with 'Think Different' (philosophy).</i>",
        st["quote"]))

    # Part 1 — Technology
    story.append(Paragraph("Part 1 — Technology Platform", st["h1"]))
    story.append(section_rule())
    story.append(Paragraph("Company Concept: Living Design Systems", st["h2"]))
    story.append(Paragraph(
        "An AI-driven platform for designing biological systems, organisms, and living "
        "materials. Comparable to Autodesk for biology, Blender for living structures, "
        "or Unity for morphogenesis.",
        st["body"]))

    story.append(Paragraph("Core Technologies", st["h2"]))

    story.append(Paragraph("1. Morphogenesis Engine", st["h3"]))
    story.append(Paragraph(
        "A 3D simulation system that models biological growth processes, enabling designers "
        "to predict and guide how living structures develop over time.", st["body"]))
    story.extend(bullets([
        "Branching systems — trees, coral, vasculature",
        "Cellular growth and nutrient gradients",
        "Biomechanical forces and developmental pathways",
        "Outputs: 3D models, gene pathway suggestions, growth predictions",
    ], st))

    story.append(Paragraph("2. Natural Language Bio Design", st["h3"]))
    story.append(Paragraph(
        "Users describe biological structures in plain language. The system converts the "
        "description into growth models, gene pathway suggestions, and structural simulations.",
        st["body"]))
    story.append(Paragraph(
        '"Grow a self-supporting dome structure using fungal mycelium optimised for humidity resistance."',
        st["quote"]))

    story.append(Paragraph("3. BioCAD Platform", st["h3"]))
    story.extend(bullets([
        "Organism blueprinting and gene network visualisation",
        "Tissue architecture modelling",
        "Environment simulation for living materials",
    ], st))

    story.append(Paragraph("4. Bioinformatics Integration", st["h3"]))
    story.append(Paragraph(
        "Connects existing genome browsers, pathway analysis tools, single-cell data, "
        "and metabolic modelling — transforming them from analysis tools into <b>design tools</b>.",
        st["body"]))

    story.append(Paragraph("Example Applications", st["h2"]))
    story.extend(bullets([
        "Living Architecture — grow structures from mycelium, engineered plants, and bacterial cellulose",
        "Carbon-Negative Construction — buildings that grow themselves, absorb carbon, and self-repair",
        "Ecosystem Engineering — design landscapes that restore soil, filter water, and regulate climate",
        "Biological Manufacturing — grow leather alternatives, structural composites, and insulation",
    ], st))

    story.append(Paragraph("Revenue Model", st["h2"]))
    story.append(comparison_table(
        ["Revenue Stream", "Description", "Example Pricing"],
        [
            ["SaaS Subscriptions", "Platform access for researchers, architects, and enterprises",
             "Academic $50–200/mo · Startup $500/mo · Enterprise $2,000+/mo"],
            ["AI Design Services", "Custom organism-design projects for materials, construction, and biotech firms",
             "Project-based"],
            ["IP Licensing", "Patents on biological growth algorithms, engineered organisms, and living material systems",
             "Royalty-based"],
        ]
    ))

    story.append(Paragraph("Development Roadmap", st["h2"]))
    story.append(comparison_table(
        ["Phase", "Timeframe", "Focus", "Early Adopters"],
        [
            ["Phase 1", "Years 1–2", "Morphogenesis engine · AI design interface · Basic BioCAD",
             "Universities · Synthetic biology labs"],
            ["Phase 2", "Years 3–5", "Living material design · Architecture simulation · Advanced AI models",
             "Architecture firms · Materials companies"],
            ["Phase 3", "Years 5–10", "Programmable ecosystems · Organism-scale design · Living infrastructure",
             "Government · Industry consortia"],
        ]
    ))

    # Part 2 — Media Movement
    story.append(PageBreak())
    story.append(Paragraph("Part 2 — The Philosophy & Media Movement", st["h1"]))
    story.append(section_rule())
    story.append(Paragraph(
        "Technology alone does not create civilisational change — narratives do. "
        "The Living Age Initiative pairs its platform with a philosophical media movement "
        "that builds cultural demand for designing <i>with</i> life rather than against it.",
        st["body"]))

    story.append(Paragraph("Core Philosophical Framework", st["h2"]))
    story.append(comparison_table(
        ["Block Systems (Industrial Age)", "Spiral Systems (Living Age)"],
        [
            ["Rigid, centralised control", "Decentralised intelligence"],
            ["Industrial, mechanical design", "Growth and emergence"],
            ["Manufactured parts assembled", "Conditions designed, systems grown"],
        ]
    ))

    story.append(Paragraph("Media Ecosystem", st["h2"]))

    story.append(Paragraph("1. Sagent Creed", st["h3"]))
    story.append(Paragraph(
        "Philosophical storytelling through mythic parables, visual scrolls, and philosophical "
        "essays. Purpose: build a lasting cultural narrative around the Living Age.",
        st["body"]))

    story.append(Paragraph("2. True Republic Podcast", st["h3"]))
    story.append(Paragraph(
        "Long-form discussion of decentralisation, biology, technology, and philosophy, "
        "targeting libertarian thinkers, technologists, and futurists.",
        st["body"]))

    story.append(Paragraph("3. Eight Pillars Video Series", st["h3"]))
    story.extend(bullets([
        "Living systems thinking", "Decentralisation", "Morphogenesis",
        "Bioengineering", "AI and biology", "Living materials",
        "Decentralised governance", "The Living Age",
    ], st))

    story.append(Paragraph("Media Revenue Sources", st["h2"]))
    story.extend(bullets([
        "Patreon / community memberships",
        "YouTube ad revenue",
        "Books and online courses",
        "Speaking engagements",
        "Substack subscriptions",
    ], st))

    story.append(Paragraph("Brand Strategy", st["h2"]))
    story.append(Paragraph(
        "Two separate brands prevent conflicting signals while each strengthens the other:",
        st["body"]))
    story.append(info_table([
        ("Spiral BioDesign", "Serious biotech platform — attracts investors, scientists, and enterprise clients."),
        ("The Sagent Creed", "Narrative movement — builds cultural audience and mission alignment."),
    ]))

    story.append(Paragraph("Why Philosophy + Technology", st["h2"]))
    story.append(comparison_table(
        ["Philosophical Movement", "Technology It Enabled"],
        [
            ["Decentralisation", "Blockchain"],
            ["Electric future", "Tesla"],
            ["Open knowledge", "Wikipedia"],
            ["Living Age", "Living Works platform"],
        ]
    ))

    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(
        "The philosophy creates cultural demand. The technology creates real-world solutions. "
        "Together they form a complete strategy for civilisational transition.",
        st["quote"]))

    build_pdf("01_Business_Plan_Living_Age_Initiative.pdf", story)


# ════════════════════════════════════════════════════════════════════════════
# 2. Competitive Analysis — Living Age Platform
# ════════════════════════════════════════════════════════════════════════════
def pdf_competitive_analysis():
    st = make_styles()
    story = []

    story.append(cover_table(
        "Living Age Platform",
        "Competitive Analysis — AI-Driven Biological Design"))
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph(
        "This document analyses the competitive landscape for the Living Age Platform, "
        "an AI-driven biological design system focused on whole-organism morphology, "
        "3D growth simulation, and natural-language-to-biology design. "
        "The analysis follows standard investor-presentation format: market overview, "
        "competitor deep-dives, and strategic positioning.",
        st["body"]))

    # Part 1
    story.append(Paragraph("Part 1 — Market Overview", st["h1"]))
    story.append(section_rule())
    story.append(Paragraph("Industry Category: AI-Driven Biological Design Platforms", st["h2"]))
    story.append(Paragraph(
        "These companies build software enabling scientists to design biological systems "
        "with the same rigour engineers use to design circuits. The Living Age concept "
        "expands this toward whole-organism design, morphogenesis simulation, living "
        "materials and architecture, and natural-language-driven workflows.",
        st["body"]))

    story.append(Paragraph("Estimated Competitive Landscape", st["h2"]))
    story.append(comparison_table(
        ["Category", "Estimated Competitors"],
        [
            ["Direct AI-Bio Design Platforms", "10–15"],
            ["Synthetic Biology Companies", "50+"],
            ["Bioinformatics / Genome Tools", "100+"],
            ["Generative Biology Startups", "20+ emerging"],
            ["Total Relevant Ecosystem", "~150+ companies"],
        ]
    ))
    story.append(Paragraph(
        "Only a small subset focuses on design platforms rather than analysis or manufacturing. "
        "The opportunity space for whole-organism and morphogenesis-level design remains largely unclaimed.",
        st["body"]))

    story.append(Paragraph("Market Segmentation", st["h2"]))
    story.append(comparison_table(
        ["Segment", "Representative Companies", "Focus"],
        [
            ["AI Protein & Molecular Design", "Profluent · Generate Biomedicines · EvolutionaryScale · AlphaFold ecosystem",
             "Designing proteins or small molecules"],
            ["Synthetic Biology Platforms", "Ginkgo Bioworks · Zymergen · Twist Bioscience",
             "Engineering microbes for manufacturing"],
            ["Bioinformatics Infrastructure", "Benchling · DNAnexus · Seven Bridges",
             "Managing biological data and pipelines"],
            ["Living Materials & Biofabrication", "Ecovative · MycoWorks · Modern Meadow",
             "Growing materials from fungi or cells"],
        ]
    ))

    story.append(Paragraph("Competitive Dynamics", st["h2"]))
    story.append(Paragraph(
        "This is an emerging but rapidly growing market. Key trends include AI-driven protein "
        "design, lab automation, synthetic biology manufacturing, and programmable living materials. "
        "However, <b>no major platform currently addresses whole-organism morphology, 3D growth "
        "simulation, natural-language-to-biology design, or living architecture</b>. That gap "
        "defines the Living Age Platform's entry point.",
        st["body"]))

    # Part 2
    story.append(PageBreak())
    story.append(Paragraph("Part 2 — Competitor Deep Dives", st["h1"]))
    story.append(section_rule())

    # Ginkgo
    story.append(Paragraph("Competitor 1 — Ginkgo Bioworks", st["h2"]))
    story.append(info_table([
        ("Location", "Boston, Massachusetts"),
        ("Founded", "2008"),
        ("Funding / Revenue", "Raised $1B+ · Public company (NYSE: DNA)"),
        ("Stage", "Commercial platform with many active industrial partnerships"),
    ]))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("Technology", st["h3"]))
    story.append(Paragraph(
        "Ginkgo operates a biological engineering platform that designs organisms for "
        "pharmaceuticals, agriculture, specialty chemicals, and food ingredients using "
        "automation, AI, and genetic engineering at massive scale.",
        st["body"]))
    story.append(Paragraph("Key Strengths", st["h3"]))
    story.extend(bullets([
        "Exceptional funding and automated lab infrastructure",
        "Partnerships with Bayer, Moderna, and Roche",
        "Strong synthetic biology brand and deep enterprise relationships",
    ], st))
    story.append(Paragraph("Their Argument", st["h3"]))
    story.append(Paragraph(
        '"Biology is engineering. Whoever builds the infrastructure platform wins. '
        'We already built the largest one." Their decisive advantage is scale.',
        st["quote"]))

    story.append(Spacer(1, 0.15*inch))

    # Benchling
    story.append(Paragraph("Competitor 2 — Benchling", st["h2"]))
    story.append(info_table([
        ("Location", "San Francisco, California"),
        ("Founded", "2012"),
        ("Funding", "~$400M+"),
        ("Stage", "Widely adopted enterprise platform"),
    ]))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("Technology", st["h3"]))
    story.append(Paragraph(
        "Benchling serves as the operating system for biotech R&D, providing DNA design tools, "
        "lab data management, collaboration software, and experiment tracking. Used by Moderna, "
        "Regeneron, and leading CRISPR companies.",
        st["body"]))
    story.append(Paragraph("Key Strengths", st["h3"]))
    story.extend(bullets([
        "Massive user base — 1,000+ biotech companies",
        "Deep integration into existing research workflows",
        "Strong network effects from shared biological data",
    ], st))
    story.append(Paragraph("Their Argument", st["h3"]))
    story.append(Paragraph(
        '"Biology companies already run on our platform. The network effect of accumulated '
        'data makes us impossible to replace."',
        st["quote"]))

    story.append(Spacer(1, 0.15*inch))

    # Generate
    story.append(Paragraph("Competitor 3 — Generate Biomedicines", st["h2"]))
    story.append(info_table([
        ("Location", "Cambridge, Massachusetts"),
        ("Founded", "2018"),
        ("Funding", "~$700M+"),
        ("Stage", "Pre-clinical / early clinical programmes"),
    ]))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("Technology", st["h3"]))
    story.append(Paragraph(
        "Generate builds AI foundation models that generate novel proteins — effectively 'GPT for proteins.' "
        "Applications include drugs, antibodies, and enzymes.",
        st["body"]))
    story.append(Paragraph("Key Strengths", st["h3"]))
    story.extend(bullets([
        "Large-scale biological foundation models",
        "Strong investor base and strategic partnerships",
        "First-mover position in generative protein design",
    ], st))
    story.append(Paragraph("Their Argument", st["h3"]))
    story.append(Paragraph(
        '"Whoever builds the best biological foundation model will control the future of medicine."',
        st["quote"]))

    # Part 3
    story.append(PageBreak())
    story.append(Paragraph("Part 3 — Competitive Positioning", st["h1"]))
    story.append(section_rule())

    story.append(Paragraph("Positioning Matrix", st["h2"]))
    story.append(comparison_table(
        ["Company", "Primary Focus", "Scale of Design", "Market Target"],
        [
            ["Benchling", "Data management & R&D ops", "Molecular (DNA sequences)", "All biotech"],
            ["Generate Biomedicines", "AI protein generation", "Molecular (proteins)", "Therapeutics"],
            ["Ginkgo Bioworks", "Industrial organism engineering", "Microbial / cellular", "Industrial biotech"],
            ["Living Age Platform", "Growth process design", "Whole-organism & architectural", "Architecture, materials, ecosystems"],
        ]
    ))

    story.append(Paragraph("Core Differentiation", st["h2"]))
    story.append(Paragraph(
        "Most competitors design <b>genes or proteins</b>. The Living Age Platform designs "
        "<b>growth processes</b> — tree branching, coral morphogenesis, fungal networks, tissue "
        "development. This represents a higher level of biological design with a distinct and "
        "largely unoccupied market position.",
        st["body"]))

    story.append(Paragraph("Unfair Advantages", st["h2"]))
    story.append(info_table([
        ("Morphogenesis Engine",
         "A physics + biology engine for growth simulation. Very few groups worldwide are building "
         "this, creating a defensible first-mover position."),
        ("Natural Language Bio Design",
         "Prompt-driven organism design lowers the barrier to entry for architects, urban designers, "
         "and engineers who are not biologists."),
        ("Cross-Scale Design",
         "Covers the full chain: DNA → cells → tissues → organisms → architecture. "
         "No competitor spans this range."),
        ("Living Materials Market",
         "Positioned for future industries: bio-grown buildings, carbon-absorbing cities, "
         "self-repairing infrastructure."),
    ]))

    story.append(Paragraph("Total Addressable Market", st["h2"]))
    story.append(comparison_table(
        ["Field", "Current Market Size"],
        [
            ["Synthetic Biology", "$20B+"],
            ["AI Drug Design", "$10B+"],
            ["Bioinformatics Software", "$15B+"],
            ["Living Materials (Programmable Biology)", "Emerging — est. $100B+ long term"],
        ]
    ))

    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(
        "Strategic Positioning: Rather than competing head-on with biotech companies, the "
        "Living Age Platform positions as <b>'the design software for living systems'</b> — "
        "the Autodesk for biology, the Unity for morphogenesis.",
        st["quote"]))

    build_pdf("02_Competitive_Analysis.pdf", story)


# ════════════════════════════════════════════════════════════════════════════
# 3. Living Works & Spiral Steward — Platform and Philosophy
# ════════════════════════════════════════════════════════════════════════════
def pdf_living_works_spiral_steward():
    st = make_styles()
    story = []

    story.append(cover_table(
        "Living Works & Spiral Steward",
        "Platform Definition and Leadership Philosophy"))
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph(
        "This document defines the two core concepts of the Living Works by the Word initiative: "
        "<b>Living Works</b>, the technology platform, and the <b>Spiral Steward</b>, the "
        "leadership philosophy that guides its application. Together they form a complete "
        "framework for designing with living systems.",
        st["body"]))

    # Part 1 — Living Works
    story.append(Paragraph("Part 1 — Living Works: The Technology Platform", st["h1"]))
    story.append(section_rule())
    story.append(Paragraph("Definition", st["h2"]))
    story.append(Paragraph(
        "Living Works is a design platform that enables humans to build with living systems — "
        "using AI, bioinformatics, and morphogenesis modelling to create organisms, materials, "
        "and structures that <b>grow</b> rather than being manufactured. Instead of assembling "
        "rigid components, Living Works designs <b>growth rules</b>.",
        st["body"]))

    story.append(Paragraph("Core Principle", st["h2"]))
    story.append(comparison_table(
        ["Traditional Engineering", "Living Works"],
        [
            ["Design a building", "Design a growth system that becomes a building"],
            ["Manufacture materials", "Grow materials"],
            ["Assemble parts", "Guide development"],
        ]
    ))

    story.append(Paragraph("Technology Components", st["h2"]))

    story.append(Paragraph("1. Morphogenesis Engine", st["h3"]))
    story.append(Paragraph(
        "A 3D simulation system that models biological growth in real time, enabling "
        "designers to predict structural outcomes before committing to biological processes.",
        st["body"]))
    story.append(comparison_table(
        ["Feature", "Detail"],
        [
            ["Branching growth", "Trees, coral, vasculature, fungal networks"],
            ["Nutrient diffusion", "Models resource gradients that shape organism form"],
            ["Cellular rules", "Agent-based growth at the cell level"],
            ["Biomechanical forces", "Structural load and environmental feedback"],
            ["Outputs", "Growth predictions · Structural models · Biological pathways"],
        ]
    ))

    story.append(Paragraph("2. AI Design Interface", st["h3"]))
    story.append(Paragraph(
        "Users describe biological structures in natural language. The AI translates "
        "descriptions into growth algorithms, gene network suggestions, and structural simulations.",
        st["body"]))
    story.append(Paragraph(
        '"Design a self-supporting branching structure optimised for wind resistance and water collection."',
        st["quote"]))

    story.append(Paragraph("3. BioCAD — Biological Computer-Aided Design", st["h3"]))
    story.extend(bullets([
        "Genome editing planning and visualisation",
        "Pathway design and gene network modelling",
        "Tissue architecture modelling",
        "Ecosystem simulation environments",
    ], st))

    story.append(Paragraph("4. Living Materials Library", st["h3"]))
    story.append(Paragraph(
        "A curated database of biological building blocks, each with documented growth "
        "rules and environmental requirements:",
        st["body"]))
    story.extend(bullets([
        "Fungal mycelium",
        "Plant tissue scaffolds",
        "Bacterial cellulose",
        "Coral-like mineralisation systems",
    ], st))

    story.append(Paragraph("Key Market Applications", st["h2"]))
    story.append(comparison_table(
        ["Application", "Description"],
        [
            ["Living Architecture",
             "Buildings grown from fungal networks, engineered plants, and bacterial materials"],
            ["Carbon-Negative Construction",
             "Structures that grow, absorb CO₂, and self-repair — eliminating embodied carbon"],
            ["Ecosystem Engineering",
             "Designed landscapes that regenerate soil, purify water, and restore biodiversity"],
            ["Bio-Manufacturing",
             "Grown textiles, biomaterials, packaging, and structural composites"],
        ]
    ))

    # Part 2 — Spiral Steward
    story.append(PageBreak())
    story.append(Paragraph("Part 2 — Spiral Steward: The Leadership Philosophy", st["h1"]))
    story.append(section_rule())
    story.append(Paragraph("Definition", st["h2"]))
    story.append(Paragraph(
        "A Spiral Steward is a leader who <b>guides living systems rather than controlling them</b>. "
        "Instead of imposing rigid structures, a Spiral Steward cultivates conditions in which "
        "healthy, adaptive systems can grow. The name captures both the biological form of "
        "spirals — the shape of growth — and the act of stewardship over time.",
        st["body"]))

    story.append(Paragraph("The Spiral vs. the Block", st["h2"]))
    story.append(comparison_table(
        ["Block System (Industrial)", "Spiral System (Living Age)"],
        [
            ["Rigid hierarchy", "Adaptive growth"],
            ["Central control", "Distributed intelligence"],
            ["Static structure", "Continuous evolution"],
            ["Manufactured", "Grown"],
        ]
    ))

    story.append(Paragraph("Five Principles of a Spiral Steward", st["h2"]))

    story.append(Paragraph("1. Stewardship Instead of Control", st["h3"]))
    story.append(Paragraph(
        "The goal is not domination but guidance. The Spiral Steward acts as a gardener "
        "rather than a machine operator — tending conditions, not dictating outcomes.",
        st["body"]))

    story.append(Paragraph("2. Emergence", st["h3"]))
    story.append(Paragraph(
        "Complex systems arise from simple rules, given the right conditions. "
        "A Spiral Steward designs conditions, not predetermined outcomes.",
        st["body"]))

    story.append(Paragraph("3. Decentralisation", st["h3"]))
    story.append(Paragraph(
        "Living systems distribute intelligence across their structure. "
        "Examples: neural networks, fungal mycelium, ecosystems. "
        "Spiral Stewards build organisations and systems that follow this pattern.",
        st["body"]))

    story.append(Paragraph("4. Adaptation", st["h3"]))
    story.append(Paragraph(
        "Living systems respond to change and grow stronger through challenge. "
        "Rigid systems fracture. A Spiral Steward builds adaptive capacity into every design.",
        st["body"]))

    story.append(Paragraph("5. Long-Term Thinking", st["h3"]))
    story.append(Paragraph(
        "Growth unfolds across time. Spiral Stewards measure success in generations, "
        "not quarters — consistent with the biological timescales on which living systems operate.",
        st["body"]))

    # Relationship
    story.append(Paragraph("Part 3 — The Relationship Between the Two", st["h1"]))
    story.append(section_rule())
    story.append(comparison_table(
        ["Concept", "Role", "Analogy"],
        [
            ["Living Works", "Technology platform", "The tools of the Living Age"],
            ["Spiral Steward", "Philosophy guiding use", "The wisdom that directs the tools"],
        ]
    ))
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph(
        "Living Works builds the tools. Spiral Stewards guide how they are used.",
        st["quote"]))
    story.append(Paragraph(
        "This maps onto the broader civilisational transition the initiative envisions:",
        st["body"]))
    story.append(comparison_table(
        ["The Age of Blocks", "The Living Age"],
        [
            ["Factories and rigid infrastructure", "Living materials and grown structures"],
            ["Centralised power", "Decentralised systems"],
            ["Industrial production", "Regenerative environments"],
        ]
    ))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(
        "Simple Summary: <b>Living Works builds with life. Spiral Stewards guide life.</b>",
        st["quote"]))

    build_pdf("03_Living_Works_Spiral_Steward.pdf", story)


# ════════════════════════════════════════════════════════════════════════════
# 4. Pitch Deck — Three Slides
# ════════════════════════════════════════════════════════════════════════════
def pdf_pitch_deck():
    st = make_styles()
    story = []

    story.append(cover_table(
        "Living Works",
        "Pitch Deck — From the Age of Blocks to the Living Age"))
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph(
        "The following three-section pitch distils the Living Works vision into a concise "
        "narrative for investors, professors, collaborators, and grant committees.",
        st["body"]))

    # Slide 1
    story.append(Paragraph("Slide 1 — The Problem & Vision", st["h1"]))
    story.append(section_rule())

    story.append(Paragraph("The Problem", st["h2"]))
    story.append(Paragraph(
        "Modern civilisation is built on rigid mechanical systems. These systems:",
        st["body"]))
    story.extend(bullets([
        "Require massive energy to manufacture and transport",
        "Degrade over time and require constant replacement",
        "Cannot adapt to changing environments or conditions",
        "Separate human design entirely from natural systems",
    ], st))
    story.append(Paragraph(
        "Industries including construction, manufacturing, and infrastructure remain "
        "anchored to industrial-age engineering — even as the biological alternatives "
        "become technically feasible.",
        st["body"]))

    story.append(Paragraph("The Opportunity", st["h2"]))
    story.append(Paragraph(
        "Living systems already solve many of the hardest engineering problems humans face. "
        "Yet our current tools only allow us to <b>analyse biology</b>, not <b>design with it</b>.",
        st["body"]))
    story.append(comparison_table(
        ["Living System", "Engineering Challenge Already Solved"],
        [
            ["Trees", "Self-assemble complex load-bearing structures"],
            ["Coral", "Builds mineral architecture across centuries"],
            ["Fungal networks", "Distributes resources with optimal efficiency"],
            ["Cells", "Organise into tissues, organs, and entire bodies"],
        ]
    ))

    story.append(Paragraph("Vision", st["h2"]))
    story.append(Paragraph(
        "Enable humanity to design with living systems instead of against them. "
        "Create a new design paradigm where structures, materials, and ecosystems "
        "are <b>grown rather than manufactured</b>. This is the beginning of the Living Age.",
        st["quote"]))

    # Slide 2
    story.append(PageBreak())
    story.append(Paragraph("Slide 2 — The Solution", st["h1"]))
    story.append(section_rule())

    story.append(Paragraph(
        "Living Works is a platform for designing living systems using AI, bioinformatics, "
        "and morphogenesis modelling. Where competitors design genes and proteins, "
        "Living Works designs <b>growth processes</b>.",
        st["body"]))

    story.append(Paragraph("Core Technologies", st["h2"]))
    story.append(comparison_table(
        ["Technology", "Capability"],
        [
            ["Morphogenesis Engine",
             "3D simulation of biological growth — branching, tissue formation, environmental feedback, biomechanical forces"],
            ["AI Biological Design Interface",
             "Natural language → growth models + gene pathway suggestions + structural simulations"],
            ["BioCAD Platform",
             "Genome editing planning · Tissue architecture modelling · Ecosystem design · Living material simulation"],
        ]
    ))

    story.append(Paragraph("Example Interaction", st["h2"]))
    story.append(Paragraph(
        '"Design a branching structure optimised for wind resistance and water collection."',
        st["quote"]))
    story.append(Paragraph(
        "The system generates a 3D growth model, proposes relevant gene pathways, "
        "runs structural simulations, and outputs a biological design specification "
        "ready for laboratory testing.",
        st["body"]))

    story.append(Paragraph("Application Areas", st["h2"]))
    story.extend(bullets([
        "Living architecture — buildings grown from mycelium and engineered plants",
        "Carbon-negative construction — self-growing, CO₂-absorbing structures",
        "Regenerative ecosystem design",
        "Biological manufacturing and programmable materials",
    ], st))

    # Slide 3
    story.append(PageBreak())
    story.append(Paragraph("Slide 3 — Strategy & Impact", st["h1"]))
    story.append(section_rule())

    story.append(Paragraph(
        "The Living Works initiative combines technical innovation with cultural narrative. "
        "Both layers are necessary and mutually reinforcing.",
        st["body"]))

    story.append(Paragraph("Technology Layer — Living Works Platform", st["h2"]))
    story.append(info_table([
        ("Business Model", "SaaS subscriptions · Enterprise partnerships · IP licensing"),
        ("Primary Users", "Biotech companies · Architects · Materials companies · Universities"),
        ("Competitive Position",
         "First platform addressing whole-organism morphology, living architecture, and natural-language bio-design"),
    ]))

    story.append(Paragraph("Cultural Layer — Spiral Steward Philosophy", st["h2"]))
    story.append(info_table([
        ("Core Principles", "Decentralisation · Adaptation · Emergence · Stewardship over control"),
        ("Media Products", "Sagent Creed · True Republic Podcast · Eight Pillars Video Series"),
        ("Purpose",
         "Build cultural demand for the Living Age — the philosophical counterpart to the technical platform"),
    ]))

    story.append(Paragraph("Long-Term Impact", st["h2"]))
    story.append(comparison_table(
        ["Industry", "Living Age Transformation"],
        [
            ["Construction", "Bio-grown buildings replace poured concrete"],
            ["Cities", "Regenerative urban environments absorb carbon"],
            ["Manufacturing", "Grown composites replace petroleum-based materials"],
            ["Ecosystems", "Programmable landscapes restore biodiversity at scale"],
        ]
    ))

    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(
        "Industrial civilisation built with blocks. "
        "The next civilisation will build with living systems. "
        "Living Works provides the tools. Spiral Stewards guide their use.",
        st["quote"]))

    build_pdf("04_Pitch_Deck.pdf", story)


# ════════════════════════════════════════════════════════════════════════════
# 5. Presentation Overview — Spiral Steward & Competitive Landscape
# ════════════════════════════════════════════════════════════════════════════
def pdf_presentation_overview():
    st = make_styles()
    story = []

    story.append(cover_table(
        "Spiral Steward",
        "Presentation Overview — Vision, Market & Competitive Landscape"))
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph(
        "This document provides a structured overview for presenting the Spiral Steward "
        "and Living Works concepts to an audience of investors, academics, or collaborators. "
        "It covers the founding vision, market context, competitive intelligence framework, "
        "and recommended research resources.",
        st["body"]))

    # Vision
    story.append(Paragraph("Founding Vision — Living Works by the Word", st["h1"]))
    story.append(section_rule())
    story.append(Paragraph(
        "Living Works by the Word is built on a single governing idea: <b>design living things "
        "by living principles</b>. Using AI and natural language, designers describe biological "
        "structures and visualise them in 3D modelling environments — creating a new practice "
        "of living architecture and biological design.",
        st["body"]))

    story.append(Paragraph("The Vision: Creating the Living Age", st["h2"]))
    story.extend(bullets([
        "Sagent Creed — philosophical and mythic video content",
        "True Republic — videos and podcast on decentralisation and biological design",
        "Eight Pillars — educational video series on living systems thinking",
        "Technology tools for designing with life rather than against it",
    ], st))

    # Part 1 — Market Overview
    story.append(Paragraph("Part 1 — Market Overview", st["h1"]))
    story.append(section_rule())
    story.append(Paragraph("Competitive Landscape Summary", st["h2"]))
    story.append(comparison_table(
        ["Competitor Type", "Estimated Count", "Market Dynamics"],
        [
            ["Direct AI-Bio Design Platforms", "10–15", "Emerging, fast-growing"],
            ["Synthetic Biology Companies", "50+", "Growing, consolidating"],
            ["Bioinformatics / Genome Tools", "100+", "Established, competitive"],
            ["Generative Biology Startups", "20+ emerging", "Early stage, crowded"],
        ]
    ))
    story.append(Paragraph(
        "The overall market is emerging-to-consolidating. The specific niche of "
        "whole-organism morphology, living architecture, and growth-process design remains "
        "a largely open territory with few direct competitors.",
        st["body"]))

    # Part 2 — Competitor Deep Dive Framework
    story.append(Paragraph("Part 2 — Competitor Deep Dive Framework", st["h1"]))
    story.append(section_rule())
    story.append(Paragraph(
        "Use the following framework for each major competitor when preparing presentation slides. "
        "Write each competitor profile as if their CEO is in the room — be honest about their advantages.",
        st["body"]))

    story.append(Paragraph("Per-Competitor Profile Template", st["h2"]))
    story.append(info_table([
        ("Company Name", "Full legal name, location, founding year"),
        ("Product / Technology", "Technically accurate, fair description of what they build"),
        ("Stage", "Preclinical · Clinical (Phase I/II/III) · Commercial · Marketed product"),
        ("Funding / Revenue", "Total raised · Recent rounds · Revenue if public"),
        ("Key Strengths", "Technology · IP · Partnerships · Market position · Team"),
        ("Market Traction", "Customers · Installations · Publications · Partners"),
        ("CEO Argument", "What would their CEO say to argue they will win and you won't?"),
    ]))

    story.append(Paragraph("Example Application — Spiral Steward", st["h2"]))
    story.append(Paragraph(
        "Spiral Steward occupies a unique position: a design platform for living systems "
        "at the architectural and ecosystem scale. It does not compete directly with "
        "molecular-level platforms (Benchling, Generate Biomedicines) or industrial organism "
        "engineering (Ginkgo Bioworks). Its differentiation lies in morphogenesis simulation, "
        "natural-language design interfaces, and the integration of philosophical narrative "
        "with technological tooling.",
        st["body"]))

    # Part 3 — Competitive Positioning
    story.append(Paragraph("Part 3 — Competitive Positioning", st["h1"]))
    story.append(section_rule())
    story.append(Paragraph("Positioning Matrix", st["h2"]))
    story.append(comparison_table(
        ["Axis", "Low End", "High End"],
        [
            ["Scale of Design", "Molecular (genes, proteins)", "Whole organism / architecture"],
            ["Primary Function", "Data management", "Active design / creation engine"],
            ["User Base", "Specialist biologists", "Architects, designers, engineers"],
        ]
    ))

    story.append(Paragraph("Genuine Differentiation — Spiral Steward / Living Works", st["h2"]))
    story.extend(bullets([
        "Whole-organism morphology design — a level of abstraction no current platform addresses",
        "Natural language interface that opens biological design to non-biologists",
        "Integration of growth simulation with architectural and ecosystem outcomes",
        "Philosophical movement that builds cultural demand alongside technical supply",
    ], st))

    story.append(Paragraph("Defensibility — Unfair Advantages", st["h2"]))
    story.append(info_table([
        ("Novel Technology", "Morphogenesis simulation engine — few groups building this globally"),
        ("Unique Positioning", "Cross-scale design (DNA → organism → architecture) with no direct competitors"),
        ("Business Model", "SaaS platform model with recurring revenue, IP licensing, and services"),
        ("Narrative Moat", "Philosophical movement creates brand loyalty and community before revenue"),
    ]))

    # Resources
    story.append(PageBreak())
    story.append(Paragraph("Competitive Intelligence Resources", st["h1"]))
    story.append(section_rule())

    story.append(Paragraph("Company & Product Information", st["h2"]))
    story.append(comparison_table(
        ["Resource", "Use"],
        [
            ["Crunchbase", "Funding, investors, company basics"],
            ["PitchBook", "Private company data (institutional access may be required)"],
            ["LinkedIn", "Company size, employee growth, key hires"],
            ["Company websites", "Products, pipeline, press releases"],
            ["AngelList / Wellfound", "Startup profiles, funding, team"],
        ]
    ))

    story.append(Paragraph("Biotech-Specific Resources", st["h2"]))
    story.append(comparison_table(
        ["Resource", "Use"],
        [
            ["ClinicalTrials.gov", "Clinical trial status for therapeutic companies"],
            ["FDA approval databases", "510(k) clearances, PMA approvals, drug approvals"],
            ["Fierce Biotech / MedTech", "Industry news and analysis"],
            ["Nature Biotechnology", "Research publications from competitor labs"],
            ["PubMed", "Scientific publications showing competitor progress"],
        ]
    ))

    story.append(Paragraph("Market & Financial Data", st["h2"]))
    story.append(comparison_table(
        ["Resource", "Use"],
        [
            ["SEC EDGAR", "Public company filings — 10-K, 10-Q, S-1 for IPOs"],
            ["Google Patents", "Competitor patent portfolios"],
            ["Grand View Research / MarketsandMarkets", "Market reports (free summaries available)"],
            ["CB Insights", "Industry trends and market maps"],
        ]
    ))

    build_pdf("05_Presentation_Overview.pdf", story)


# ── Run all ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    pdf_business_plan()
    pdf_competitive_analysis()
    pdf_living_works_spiral_steward()
    pdf_pitch_deck()
    pdf_presentation_overview()
    print("\nAll PDFs generated.")

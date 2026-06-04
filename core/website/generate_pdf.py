#!/usr/bin/env python3
"""Generate: The Moral Case for Living Architecture"""

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    KeepTogether, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

OUTPUT = "/mnt/c/Users/SajcS/Desktop/Living works by the word/The Moral Case for Living Architecture.pdf"

# ── Palette ──────────────────────────────────────────────────────────────────
DEEP_GREEN   = HexColor("#1B4332")
MID_GREEN    = HexColor("#2D6A4F")
LIGHT_GREEN  = HexColor("#52B788")
PALE_GREEN   = HexColor("#D8F3DC")
GOLD         = HexColor("#B7901B")
DARK_TEXT    = HexColor("#1A1A1A")
MID_TEXT     = HexColor("#3D3D3D")
LIGHT_GREY   = HexColor("#F4F4F4")
RULE_COLOR   = HexColor("#52B788")

# ── Document ──────────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=LETTER,
    rightMargin=0.85*inch,
    leftMargin=0.85*inch,
    topMargin=0.85*inch,
    bottomMargin=0.85*inch,
    title="The Moral Case for Living Architecture",
    author="Sage Clokey",
)

# ── Styles ────────────────────────────────────────────────────────────────────
base = getSampleStyleSheet()

def S(name, **kw):
    return ParagraphStyle(name, **kw)

COVER_TITLE = S("CoverTitle",
    fontName="Helvetica-Bold", fontSize=30, leading=38,
    textColor=DEEP_GREEN, alignment=TA_CENTER, spaceAfter=8)

COVER_SUB = S("CoverSub",
    fontName="Helvetica", fontSize=14, leading=20,
    textColor=MID_GREEN, alignment=TA_CENTER, spaceAfter=6)

COVER_TAG = S("CoverTag",
    fontName="Helvetica-Oblique", fontSize=11, leading=16,
    textColor=GOLD, alignment=TA_CENTER, spaceAfter=4)

COVER_AUTHOR = S("CoverAuthor",
    fontName="Helvetica", fontSize=11, leading=14,
    textColor=MID_TEXT, alignment=TA_CENTER)

TRACK_LABEL = S("TrackLabel",
    fontName="Helvetica-Bold", fontSize=9, leading=12,
    textColor=white, alignment=TA_CENTER)

PART_HEADER = S("PartHeader",
    fontName="Helvetica-Bold", fontSize=19, leading=24,
    textColor=white, alignment=TA_LEFT,
    spaceBefore=6, spaceAfter=4)

SECTION_HEAD = S("SectionHead",
    fontName="Helvetica-Bold", fontSize=13, leading=18,
    textColor=DEEP_GREEN, spaceBefore=14, spaceAfter=4)

SUB_HEAD = S("SubHead",
    fontName="Helvetica-Bold", fontSize=11, leading=15,
    textColor=MID_GREEN, spaceBefore=10, spaceAfter=3)

BODY = S("Body",
    fontName="Helvetica", fontSize=10.5, leading=16,
    textColor=DARK_TEXT, alignment=TA_JUSTIFY, spaceAfter=8)

QUOTE = S("Quote",
    fontName="Helvetica-Oblique", fontSize=10.5, leading=16,
    textColor=DEEP_GREEN, leftIndent=24, rightIndent=24,
    spaceBefore=8, spaceAfter=8, alignment=TA_JUSTIFY)

SOURCE_NOTE = S("SourceNote",
    fontName="Helvetica-Oblique", fontSize=8.5, leading=12,
    textColor=MID_TEXT, leftIndent=12, spaceAfter=4)

BULLET = S("Bullet",
    fontName="Helvetica", fontSize=10.5, leading=16,
    textColor=DARK_TEXT, leftIndent=20, spaceBefore=2, spaceAfter=2)

CALLOUT = S("Callout",
    fontName="Helvetica-Bold", fontSize=11, leading=16,
    textColor=DEEP_GREEN, alignment=TA_CENTER,
    spaceBefore=4, spaceAfter=4)

FOOTER_NOTE = S("FooterNote",
    fontName="Helvetica-Oblique", fontSize=8, leading=11,
    textColor=MID_TEXT, alignment=TA_CENTER)

# ── Helpers ───────────────────────────────────────────────────────────────────
def rule(color=RULE_COLOR, thickness=0.8):
    return HRFlowable(width="100%", thickness=thickness, color=color,
                      spaceAfter=6, spaceBefore=6)

def green_rule():
    return HRFlowable(width="100%", thickness=2, color=LIGHT_GREEN,
                      spaceAfter=10, spaceBefore=10)

def part_banner(text, sub=""):
    """Full-width green banner for part headers."""
    data = [[Paragraph(text, PART_HEADER)]]
    if sub:
        data.append([Paragraph(sub, S("PartSub",
            fontName="Helvetica-Oblique", fontSize=10, leading=14,
            textColor=PALE_GREEN, alignment=TA_LEFT))])
    tbl = Table(data, colWidths=[6.8*inch])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), DEEP_GREEN),
        ("LEFTPADDING",  (0,0), (-1,-1), 14),
        ("RIGHTPADDING", (0,0), (-1,-1), 14),
        ("TOPPADDING",   (0,0), (-1,-1), 10),
        ("BOTTOMPADDING",(0,0), (-1,-1), 10),
        ("ROUNDEDCORNERS", [6]),
    ]))
    return tbl

def track_badge(text):
    data = [[Paragraph(text, TRACK_LABEL)]]
    tbl = Table(data, colWidths=[6.8*inch])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), GOLD),
        ("LEFTPADDING",  (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING",   (0,0), (-1,-1), 6),
        ("BOTTOMPADDING",(0,0), (-1,-1), 6),
    ]))
    return tbl

def callout_box(text):
    data = [[Paragraph(text, CALLOUT)]]
    tbl = Table(data, colWidths=[6.8*inch])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), PALE_GREEN),
        ("LEFTPADDING",  (0,0), (-1,-1), 18),
        ("RIGHTPADDING", (0,0), (-1,-1), 18),
        ("TOPPADDING",   (0,0), (-1,-1), 10),
        ("BOTTOMPADDING",(0,0), (-1,-1), 10),
        ("BOX", (0,0), (-1,-1), 1.5, LIGHT_GREEN),
        ("ROUNDEDCORNERS", [6]),
    ]))
    return tbl

def two_col_contrast(left_title, left_items, right_title, right_items):
    left_body  = f"<b>{left_title}</b><br/>" + "<br/>".join(f"• {i}" for i in left_items)
    right_body = f"<b>{right_title}</b><br/>" + "<br/>".join(f"• {i}" for i in right_items)
    left_style  = S("TblL", fontName="Helvetica", fontSize=10, leading=15,
                    textColor=DARK_TEXT, spaceBefore=2, spaceAfter=2)
    right_style = S("TblR", fontName="Helvetica", fontSize=10, leading=15,
                    textColor=white, spaceBefore=2, spaceAfter=2)
    data = [[Paragraph(left_body, left_style), Paragraph(right_body, right_style)]]
    tbl = Table(data, colWidths=[3.3*inch, 3.3*inch], hAlign="CENTER")
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,-1), PALE_GREEN),
        ("BACKGROUND", (1,0), (1,-1), DEEP_GREEN),
        ("LEFTPADDING",  (0,0), (-1,-1), 14),
        ("RIGHTPADDING", (0,0), (-1,-1), 14),
        ("TOPPADDING",   (0,0), (-1,-1), 12),
        ("BOTTOMPADDING",(0,0), (-1,-1), 12),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("BOX", (0,0), (-1,-1), 0.5, RULE_COLOR),
        ("INNERGRID", (0,0), (-1,-1), 0.5, RULE_COLOR),
    ]))
    return tbl

def source(text):
    return Paragraph(f"<i>— {text}</i>", SOURCE_NOTE)

def sp(n=6):
    return Spacer(1, n)

# ── Build Story ───────────────────────────────────────────────────────────────
story = []

# ════════════════════════════════════════════════════════════════════════════
#  COVER PAGE
# ════════════════════════════════════════════════════════════════════════════
story += [
    sp(60),
    Paragraph("The Moral Case for", COVER_SUB),
    Paragraph("Living Architecture", COVER_TITLE),
    sp(4),
    rule(LIGHT_GREEN, 2),
    sp(8),
    Paragraph(
        "Why Houses Must Grow in Living Shape — Not Stand as Dead Blocks",
        COVER_TAG),
    sp(20),
]

# Track badges
tracks_data = [[
    Paragraph("Track 1: Bioethics, Equity &amp; Justice", TRACK_LABEL),
    Paragraph("Track 2: Sustainability", TRACK_LABEL),
]]
tracks_tbl = Table(tracks_data, colWidths=[3.3*inch, 3.3*inch], hAlign="CENTER")
tracks_tbl.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (0,-1), MID_GREEN),
    ("BACKGROUND", (1,0), (1,-1), GOLD),
    ("LEFTPADDING",  (0,0), (-1,-1), 10),
    ("RIGHTPADDING", (0,0), (-1,-1), 10),
    ("TOPPADDING",   (0,0), (-1,-1), 8),
    ("BOTTOMPADDING",(0,0), (-1,-1), 8),
    ("INNERGRID", (0,0), (-1,-1), 1, white),
    ("BOX", (0,0), (-1,-1), 1, white),
]))
story += [tracks_tbl, sp(30)]

story += [
    Paragraph("Sage Clokey", COVER_AUTHOR),
    sp(4),
    Paragraph("LivingWorks — A Life-Based Design Initiative", COVER_AUTHOR),
    sp(4),
    Paragraph("2026", COVER_AUTHOR),
    sp(40),
    rule(DEEP_GREEN, 1),
    sp(6),
    Paragraph(
        "Built from source documents: <i>Bioinformatics as Stewardship of Living Order</i> · "
        "<i>Cover Letter: Voluntarist Biology</i> · <i>The Spiral Steward</i>",
        FOOTER_NOTE),
    PageBreak(),
]

# ════════════════════════════════════════════════════════════════════════════
#  PREAMBLE
# ════════════════════════════════════════════════════════════════════════════
story += [
    Paragraph("Preamble", SECTION_HEAD),
    green_rule(),
    Paragraph(
        "This document lays out the moral case for replacing block-based, industrially "
        "manufactured housing with <b>living architecture</b> — structures that grow, adapt, "
        "and repair themselves in accord with biological and ecological principles. "
        "The argument draws on three original texts written to articulate the ethics of "
        "life-based design, interpreted through two justice frameworks:",
        BODY),
    sp(4),
    Paragraph("• <b>Bioethics, Equity &amp; Justice:</b> How dead-matter construction perpetuates "
              "social harm, cognitive inequality, and moral failure toward future generations.", BULLET),
    Paragraph("• <b>Sustainability:</b> How living architecture restores rather than destroys "
              "the ecological systems on which all human flourishing depends.", BULLET),
    sp(10),
    Paragraph(
        '"Life is not a resource. Life is a language. And the Steward of Life is '
        'learning to speak it."',
        QUOTE),
    source("The Spiral Steward"),
    sp(10),
]

# ════════════════════════════════════════════════════════════════════════════
#  PART I — THE MORAL DIAGNOSIS
# ════════════════════════════════════════════════════════════════════════════
story += [
    sp(6),
    part_banner("Part I", "The Moral Diagnosis: What Block Architecture Does to People and Planet"),
    sp(12),
    Paragraph("1.1  The Industrial Error Is an Ethical Error", SECTION_HEAD),
    rule(),
    Paragraph(
        "Block houses — rectangular, mass-produced, dead-material structures — are not morally "
        "neutral. They are the physical residue of an industrial worldview that begins with a "
        "single foundational error: <b>the belief that humans are separate from nature.</b>",
        BODY),
    Paragraph(
        "From this lie, all downstream harms follow. When planners and architects treat land as "
        "substrate rather than ecosystem, communities as consumer units rather than living "
        "organisms, and buildings as manufactured objects rather than cultivated places, they "
        "produce environments that injure the people who inhabit them.",
        BODY),
    Paragraph(
        '"The industrial age taught humanity a single devastating lie: that humans are separate '
        'from nature. From this lie came monoculture agriculture that destroys soil; cities built '
        'as dead zones instead of living habitats; homes built from dead matter that nature itself '
        'seeks to burn and clear."',
        QUOTE),
    source("The Spiral Steward"),
    sp(8),
    Paragraph("1.2  Architecture Shapes Thought — And Thought Shapes Justice", SECTION_HEAD),
    rule(),
    Paragraph(
        "The moral harm of block architecture is not only physical or environmental. It is "
        "<b>cognitive and political.</b> The built environment teaches the mind how to think "
        "about power, relationship, and possibility.",
        BODY),
    Paragraph(
        '"When we build a world around blocks, cubes, and rigid hierarchies, we produce people '
        'who think in domination, in control, in compliance, in extraction. Empire architecture '
        'creates empire minds. Dead spaces create dead thinking. Living systems create living '
        'cognition. This is why monoculture produces fragility, cubes produce despair, and '
        'centralized control produces obedience — not wisdom. The environment is not neutral. '
        '<b>Design is moral.</b>"',
        QUOTE),
    source("The Spiral Steward"),
    sp(6),
    Paragraph(
        "This is a bioethics claim with direct implications for equity and justice. If the "
        "physical shape of a home determines the cognitive habits of its inhabitants, then "
        "housing policy is brain policy. Consigning low-income communities to identical grid "
        "blocks is not merely an aesthetic choice — it is a <b>structural imposition of "
        "conformist cognition,</b> limiting the imaginative and political capacity of those "
        "least able to resist it.",
        BODY),
    sp(6),
    callout_box(
        '"The cube is the shape of slavery. The Fibonacci spiral is the shape of freedom."'
    ),
    source("The Spiral Steward"),
    sp(10),
    Paragraph("1.3  Monoculture Is Violence — Against Ecosystems and Against People", SECTION_HEAD),
    rule(),
    Paragraph(
        "Block construction enforces monoculture at every scale. Ecologically, it replaces "
        "biodiversity with uniform substrate. Socially, it replaces cultural variety with "
        "standardized units. Both forms of monoculture share the same moral signature: "
        "<b>the erasure of difference in order to ease control.</b>",
        BODY),
    Paragraph(
        '"Where life grows in spirals, we imposed straight lines. Where ecosystems rely on '
        'diversity, we enforced uniformity. Where systems wanted decentralization, we demanded '
        'central control. The ancient Amazonian civilizations understood something modern '
        'society forgot: abundance emerges from biodiversity; stability comes from relationship; '
        'growth follows spirals, not grids."',
        QUOTE),
    source("The Spiral Steward"),
    sp(6),
    Paragraph(
        "Bioinformatics confirms what indigenous wisdom already knew. Computational analysis of "
        "living systems — from genomes to ecosystems — consistently shows that <b>resilience "
        "emerges from diversity, not uniformity.</b> A design philosophy that imports "
        "monoculture logic into the built environment is not just aesthetically impoverished; "
        "it is scientifically and morally wrong.",
        BODY),
    Paragraph(
        '"Bioinformatics offers a different posture: attention before intervention. It trains '
        'you to watch patterns that no human mind can hold at once — the combinatorial '
        'complexity of genomes, gene regulation, protein folding, microbial communities, '
        'ecological networks. It reveals that life is not centrally designed, but emergent: '
        'a decentralized order created through layers of feedback, adaptation, and symbiosis."',
        QUOTE),
    source("Bioinformatics as Stewardship of Living Order"),
    sp(14),
]

# ════════════════════════════════════════════════════════════════════════════
#  PART II — TRACK 1: BIOETHICS, EQUITY & JUSTICE
# ════════════════════════════════════════════════════════════════════════════
story += [
    part_banner("Part II — Track 1", "Bioethics, Equity & Justice: The Right to Live in Living Space"),
    sp(12),
    Paragraph("2.1  Housing as a Bioethical Issue", SECTION_HEAD),
    rule(),
    Paragraph(
        "Bioethics traditionally governs decisions about the human body — clinical treatment, "
        "genetic privacy, research consent. But the body does not end at the skin. The built "
        "environment is a prosthetic extension of the biological organism. Air quality, light "
        "cycles, acoustic texture, spatial variety, contact with living systems: these are not "
        "luxuries. They are inputs to human biological health.",
        BODY),
    Paragraph(
        "When block housing cuts people off from biodiversity, natural light gradients, and "
        "living material, it imposes a <b>medically significant deprivation</b> — one that "
        "disproportionately falls on those with the least economic power to escape it. "
        "This is a bioethics failure of the same magnitude as inequitable access to clinical care.",
        BODY),
    sp(6),
    Paragraph("2.2  Equity: Who Bears the Cost of Dead Architecture?", SECTION_HEAD),
    rule(),
    Paragraph(
        "Block construction is cheaper to produce and more profitable to sell at scale. This "
        "economic logic determines who gets living space and who gets cubes. Wealthy individuals "
        "can afford bespoke, nature-integrated design. Everyone else receives the "
        "industrially optimized minimum. This is not a natural market outcome — "
        "it is a <b>structural inequity encoded in zoning law, building code, and "
        "financial incentive.</b>",
        BODY),
    Paragraph(
        "The stewardship ethic demands we ask: who benefits from this arrangement? The answer "
        "is clear: manufacturers, developers, and insurers who profit from standardization. "
        "Those who pay the price — in cognitive restriction, ecological disconnection, and "
        "long-term health cost — are the communities with the least political voice.",
        BODY),
    Paragraph(
        '"Bioinformatics can become the microscope for this philosophy — not only seeing '
        "life's code, but seeing life's order. And that is the real mission: to learn the "
        'language of life so we can stop treating it like dead matter, and start designing '
        'like gardeners, not rulers."',
        QUOTE),
    source("Bioinformatics as Stewardship of Living Order"),
    sp(6),
    Paragraph("2.3  Justice: The Obligation to Restore", SECTION_HEAD),
    rule(),
    Paragraph(
        "Justice is not only the prevention of future harm. It is the repair of existing "
        "damage. Centuries of industrial block construction have fractured the relationship "
        "between human communities and living ecosystems. A justice-oriented approach to "
        "housing demands <b>ecological and spatial restoration</b> — rebuilding environments "
        "that allow human biological and social systems to re-integrate with the living world.",
        BODY),
    Paragraph(
        "This aligns with the voluntarist biology framework: human systems flourish not under "
        "central coercion, but under conditions that support voluntary emergence and "
        "self-organization. Living architecture restores those conditions.",
        BODY),
    Paragraph(
        '"My long-term goal in this field is not merely to analyze biological data, but to '
        'deepen our collective understanding of how living systems organize themselves — and '
        'to use that understanding to help humanity become better stewards of life... '
        'I hope to contribute to a new paradigm of bio-design — one that works with living '
        'systems instead of trying to dominate them. This means developing tools that guide '
        'growth through gentle constraints, feedback, and learning rather than coercive '
        'engineering."',
        QUOTE),
    source("Cover Letter: Voluntarist Biology"),
    sp(8),
    two_col_contrast(
        "Block Housing Produces",
        [
            "Cognitive conformism and passivity",
            "Ecological disconnection",
            "Health disparities (light, air, nature-deficit)",
            "Spatial inequality by income",
            "Fragile, non-adaptive structures",
            "Cultural homogenization",
        ],
        "Living Architecture Produces",
        [
            "Cognitive diversity and agency",
            "Ecological integration",
            "Biologically supportive environments",
            "Adaptive design accessible to all",
            "Self-repairing, resilient structures",
            "Place-specific cultural expression",
        ],
    ),
    sp(14),
]

# ════════════════════════════════════════════════════════════════════════════
#  PART III — TRACK 2: SUSTAINABILITY
# ════════════════════════════════════════════════════════════════════════════
story += [
    part_banner("Part III — Track 2", "Sustainability: Design That Grows Instead of Decays"),
    sp(12),
    Paragraph("3.1  The Ecological Indictment of Block Construction", SECTION_HEAD),
    rule(),
    Paragraph(
        "Block construction is structurally unsustainable because it is <b>extractive by "
        "design.</b> It begins with the destruction of living systems — trees cleared, soil "
        "compacted, watersheds sealed under concrete — and ends with the manufacture of dead "
        "materials that provide no ongoing ecological function and accumulate as waste.",
        BODY),
    Paragraph(
        '"Industrial engineering designs systems that must first kill what is living: trees '
        'become lumber, soil becomes substrate, ecosystems become resources. Only once life is '
        'stripped away can control be imposed."',
        QUOTE),
    source("The Spiral Steward"),
    sp(6),
    Paragraph(
        "This extractive logic produces not only environmental collapse but structural "
        "fragility. Dead materials cannot adapt, self-repair, or respond to changing "
        "conditions. They degrade passively, requiring perpetual energy and resource input "
        "to maintain. The result is a built environment that is simultaneously an ecological "
        "catastrophe and an economic liability.",
        BODY),
    Paragraph("3.2  Living Systems Are Inherently Regenerative", SECTION_HEAD),
    rule(),
    Paragraph(
        "The alternative is not simply 'green buildings' with solar panels and recycled "
        "materials. It is a fundamentally different ontology of design — one that treats "
        "the built environment as a <b>cultivated living system</b> rather than a "
        "manufactured product.",
        BODY),
    Paragraph(
        '"The next era is not about building objects. It is about cultivating systems. '
        'This is the age of: symbiotic design, regenerative systems, decentralized '
        'biomanufacturing, structures that grow, adapt, repair, and renew. In this age, '
        'design no longer means imposing form. It means shaping conditions. You do not '
        'command life. You listen to it. You do not force outcomes. You invite emergence."',
        QUOTE),
    source("The Spiral Steward"),
    sp(6),
    Paragraph(
        "Bioinformatics provides the scientific foundation for this shift. Computational "
        "models of biological self-organization reveal the mechanisms by which living systems "
        "generate structure from local rules, feedback, and environmental responsiveness. "
        "Applying these mechanisms to architectural design is not metaphor — it is the "
        "literal application of biological knowledge to the problem of sustainable construction.",
        BODY),
    Paragraph(
        '"When you do computational biology, you are forced into humility. You learn that '
        'you cannot design an entire living world top-down. You can only nudge, explore, '
        'and make local improvements — then observe what the system does in response. '
        "The deeper your models become, the more obvious it becomes: life is not a block "
        'you carve into shape; it is a spiral you cultivate."',
        QUOTE),
    source("Bioinformatics as Stewardship of Living Order"),
    sp(6),
    Paragraph("3.3  Stewardship as a Sustainability Ethic", SECTION_HEAD),
    rule(),
    Paragraph(
        "Sustainability is not merely a technical challenge — it is a moral orientation. "
        "The stewardship ethic described across all three source documents offers a coherent "
        "foundation for that orientation: <b>work with life's own principles rather than "
        "against them.</b>",
        BODY),
    Paragraph(
        '"Stewardship does not mean leave nature alone forever. It means work with '
        "life's own principles rather than against them. It means respecting biodiversity "
        'as strength, not mess. It means designing not single rigid outcomes, but '
        'possibility spaces — resilient sets of options that allow organisms and communities '
        'to adapt."',
        QUOTE),
    source("Bioinformatics as Stewardship of Living Order"),
    sp(6),
    Paragraph(
        "This ethic directly addresses the sustainability tracks of invasive species "
        "management and antibiotic resistance: both problems arise from the imposition of "
        "monoculture logic on biological systems. Both are worsened by block thinking "
        "(single solutions, centralized control) and improved by spiral thinking "
        "(biodiversity, decentralized adaptation, feedback-driven response).",
        BODY),
    sp(6),
    callout_box(
        '"Bioinformatics naturally aligns with stewardship ethics — respecting biodiversity '
        'as strength, not mess, designing possibility spaces that allow organisms and '
        'communities to adapt."'
    ),
    source("Bioinformatics as Stewardship of Living Order"),
    sp(10),
    Paragraph("3.4  The Green Flame: Restoration, Not Destruction", SECTION_HEAD),
    rule(),
    Paragraph(
        "The transition from block to living architecture does not require the violent "
        "overthrow of existing systems. It requires what the source documents call "
        "<b>the Green Flame</b> — the purifying renewal that replaces what is dead with "
        "what can grow.",
        BODY),
    Paragraph(
        '"The green flame does not kill life. It kills what is already dead. It purifies. '
        'It renews. It returns decay back into growth. The green flame is the backward '
        'Fibonacci spiral: Life → Death → Multiplying Rebirth."',
        QUOTE),
    source("The Spiral Steward"),
    sp(6),
    Paragraph(
        "Applied to the built environment, this means: we do not need to demolish all "
        "existing housing. We need to change the logic governing what gets built next. "
        "Every new structure can be a demonstration that living shape is possible, "
        "affordable, and morally required.",
        BODY),
    sp(14),
]

# ════════════════════════════════════════════════════════════════════════════
#  PART IV — THE POSITIVE VISION
# ════════════════════════════════════════════════════════════════════════════
story += [
    part_banner("Part IV", "The Positive Vision: What Living Architecture Makes Possible"),
    sp(12),
    Paragraph("4.1  From Engineer to Steward", SECTION_HEAD),
    rule(),
    Paragraph(
        "The moral case for living architecture is not only a critique of what exists. "
        "It is an affirmation of a different human role in the world — the role of Steward "
        "rather than Engineer, of Gardener rather than Ruler.",
        BODY),
    Paragraph(
        '"We need a new name for the designer of this age. Not Engineer — because engines '
        'are dead. This new designer does not work on nature. They work within it. They '
        'design like a gardener, not a general. Like a conductor, not a dictator. Like '
        'Adam — formed from the soil itself, placed in the garden not to dominate it, '
        'but to tend it and keep it in balance."',
        QUOTE),
    source("The Spiral Steward"),
    sp(6),
    Paragraph("4.2  LivingWorks: Design That Emerges", SECTION_HEAD),
    rule(),
    Paragraph(
        "The practical realization of this vision is a design platform that works the way "
        "life works — specifying conditions, not shapes; relationships, not objects; "
        "flows, not blueprints.",
        BODY),
    Paragraph(
        '"Imagine a design platform where you don\'t specify shapes. Instead, you specify: '
        'energy flows, nutrient cycles, structural stresses, growth constraints, environmental '
        'context, local variation rules. The system then simulates emergence, not assembly. '
        'Design becomes: \'If these conditions exist, what wants to grow here?\' That is '
        'LivingWorks."',
        QUOTE),
    source("The Spiral Steward"),
    sp(6),
    Paragraph(
        "This is not science fiction. It is the direct application of bioinformatics, "
        "machine learning, and systems biology to the problem of the built environment. "
        "The computational tools already exist. What has been missing is the moral "
        "framework to justify using them in this direction.",
        BODY),
    Paragraph(
        '"By applying machine learning, network science, and multi-omics analysis, I aim '
        'to uncover how decentralized genetic, cellular, and ecological systems self-organize '
        'across scales. My particular interest lies in connecting high-level patterns of '
        'growth and adaptation to underlying DNA-level mechanisms, enabling predictive models '
        'that respect the complexity of life rather than reducing it to rigid, mechanical '
        'parts."',
        QUOTE),
    source("Cover Letter: Voluntarist Biology"),
    sp(8),
    Paragraph("4.3  The Spiral Returns: A Summary of the Moral Principles", SECTION_HEAD),
    rule(),
    Paragraph("The moral case for living architecture rests on six interconnected principles:", BODY),
    sp(4),
    Paragraph("1. <b>Design is moral.</b> The shape of the built environment is not neutral — it "
              "determines cognitive, social, and ecological outcomes.", BULLET),
    sp(2),
    Paragraph("2. <b>Life's principles are not optional.</b> Biology reveals the rules by which "
              "complex systems sustain themselves. Violating those rules — through monoculture, "
              "rigidity, and centralized control — produces fragility and harm.", BULLET),
    sp(2),
    Paragraph("3. <b>Equity demands living space for all.</b> The current system concentrates "
              "nature-integrated design among the wealthy. Justice requires democratizing "
              "access to living architecture.", BULLET),
    sp(2),
    Paragraph("4. <b>Sustainability requires regenerative design.</b> Dead-material construction "
              "is structurally extractive. Only living systems can produce the self-repairing, "
              "adaptive built environment that ecological reality demands.", BULLET),
    sp(2),
    Paragraph("5. <b>Stewardship replaces domination.</b> The appropriate human relationship "
              "to the built environment — as to nature — is that of gardener, shepherd, "
              "and steward: guiding growth rather than commanding form.", BULLET),
    sp(2),
    Paragraph("6. <b>Spirals over blocks.</b> The Fibonacci spiral is not merely a beautiful "
              "shape. It is the shape of growth, of life, of freedom. The block is the shape "
              "of control, of stasis, of decay. We choose which world to build.", BULLET),
    sp(14),
]

# ════════════════════════════════════════════════════════════════════════════
#  CONCLUSION
# ════════════════════════════════════════════════════════════════════════════
story += [
    green_rule(),
    Paragraph("Conclusion", SECTION_HEAD),
    Paragraph(
        "The moral argument for living architecture is not sentimental. It is grounded in "
        "biology, systems theory, and the ethics of equity and stewardship. Block houses "
        "are a failure of moral imagination that has become normalized through industrial "
        "inertia. They harm the people who live in them, the communities that surround them, "
        "and the ecosystems they displace.",
        BODY),
    Paragraph(
        "The alternative is not idealism. It is the application of what bioinformatics has "
        "taught us about how life actually works — and the courage to design accordingly. "
        "Life does not build in blocks. Life builds in spirals. And humanity, if it "
        "remembers its proper role, builds with life.",
        BODY),
    sp(10),
    callout_box(
        '"Not blocks. Spirals.\n'
        'Not rulers. Gardeners.\n'
        'Not dead matter. Living order."'
    ),
    source("Bioinformatics as Stewardship of Living Order"),
    sp(20),
    green_rule(),
    Paragraph(
        "Source Documents  ·  <i>Bioinformatics as Stewardship of Living Order</i>  "
        "·  <i>Cover Letter: Voluntarist Biology</i>  ·  <i>The Spiral Steward</i>  "
        "·  All texts by Sage Clokey, LivingWorks Initiative, 2026",
        FOOTER_NOTE),
]

# ── Build ─────────────────────────────────────────────────────────────────────
doc.build(story)
print(f"PDF written to: {OUTPUT}")

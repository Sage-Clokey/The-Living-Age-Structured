from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER

output_path = "/mnt/c/Users/SajcS/Desktop/sagent creed book/Sagent_Creed_Hook_Tweets.pdf"

doc = SimpleDocTemplate(
    output_path,
    pagesize=letter,
    rightMargin=1*inch,
    leftMargin=1*inch,
    topMargin=1*inch,
    bottomMargin=1*inch,
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "Title",
    parent=styles["Normal"],
    fontSize=22,
    fontName="Helvetica-Bold",
    textColor=colors.HexColor("#1a1a1a"),
    spaceAfter=6,
    alignment=TA_CENTER,
)

subtitle_style = ParagraphStyle(
    "Subtitle",
    parent=styles["Normal"],
    fontSize=11,
    fontName="Helvetica",
    textColor=colors.HexColor("#555555"),
    spaceAfter=20,
    alignment=TA_CENTER,
)

section_style = ParagraphStyle(
    "Section",
    parent=styles["Normal"],
    fontSize=9,
    fontName="Helvetica-Bold",
    textColor=colors.HexColor("#888888"),
    spaceBefore=18,
    spaceAfter=6,
    letterSpacing=1.5,
)

tweet_style = ParagraphStyle(
    "Tweet",
    parent=styles["Normal"],
    fontSize=12,
    fontName="Helvetica",
    textColor=colors.HexColor("#1a1a1a"),
    leading=18,
    spaceBefore=4,
    spaceAfter=12,
    leftIndent=14,
    borderPad=8,
)

number_style = ParagraphStyle(
    "Number",
    parent=styles["Normal"],
    fontSize=9,
    fontName="Helvetica-Bold",
    textColor=colors.HexColor("#aaaaaa"),
    spaceAfter=2,
    leftIndent=14,
)

sections = [
    ("TRUTH & THE SAGENT", [
        "A lie only survives as long as no one speaks the one word that exposes it. That's not power — that's fragility dressed up as authority.",
        "Truth tellers don't want to be right. They just see things others can't — or won't. The ones they're trying to free are usually the first to fight them.",
        "Lies spread only one way: by silencing the person who tells the truth. Free speech isn't a privilege. It's the thing that makes lies impossible.",
        "I am Sage — the fire of truth that burns away the demons who tell lies. Not a wildfire. A forge.",
        "When a society is ruled by mass psychosis, seeing reality clearly looks like madness.",
    ]),
    ("LIBERTY & THE TRUE REPUBLIC", [
        "The cube is the architecture of slavery. The Fibonacci spiral is the shape of freedom. We built our cities in the wrong shape and then wondered why people feel trapped.",
        "A True Republic isn't a government. It's a network of people who follow their conscience instead of the chain of command.",
        "Good soldiers don't follow orders. They follow their conscience. The day they stopped knowing the difference is the day they became weapons.",
        "You cannot change morality by rewriting the law. It was written on your heart long before any legislature existed.",
        "Security that sacrifices freedom to protect freedom isn't security. It's the threat wearing a badge.",
        "The herd follows power. The pink cow follows truth. And truth is the only campaign worth fighting.",
        "Neurodivergents built decentralized systems because no one would give them a place in the rigid hierarchy. When the old world collapsed — theirs was all that was left.",
    ]),
    ("LOVE & THE PLEDGE OF THE HEART", [
        "Love waits. Lust rushes. You can feel the difference the moment you walk into the room.",
        "Love cannot be forced. It can only be allowed. Manifestation isn't bending the world to your will — it's aligning your will to fate.",
        "Destiny is the destination. Your choices are the path you take to get there.",
        "All in or fold. That's how I play poker. That's how I play life. If I'm not willing to go all in, I shouldn't be betting anything at all.",
        "Sometimes the greatest regret isn't what you did. It's what you never said.",
    ]),
    ("THE PLEDGE / TURN / PRESTIGE", [
        "Every story has three acts: the Arthur, the Joseph, and the Sage. The warrior answers the call. The sufferer learns the lesson. The wise man solves what force alone never could.",
        "Luke didn't win by fighting harder. He won by helping the light rise in Anakin. That's the difference between fighting darkness and raising light.",
        "You lose the blue lightsaber so you can build the green one. The one you were given gets you started. The one you build is who you are.",
        "The storm doesn't destroy the tree to kill it. It spreads the seeds. The fall is the plan.",
    ]),
    ("IDENTITY & STORY", [
        "Stories are how the programming is done — and how it's undone. The greatest weapon of those in power is the same weapon that can expose them.",
        "Creativity mistaken for psychosis. Conscience mistaken for rebellion. Wisdom mistaken for a threat. That's how you know it's real.",
        "My grandfather created Gumby to show a structured world what freedom looked like. Clay has infinite possibilities. Cubes don't.",
        "I don't force people to grow. I remove what stops them.",
        "Arthur answers the call. Joseph carries the burden. Sage reveals the truth. Every great story — every great life — is all three.",
    ]),
]

story = []

story.append(Paragraph("The Sagent Creed", title_style))
story.append(Paragraph("Hook Tweets", subtitle_style))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#dddddd")))
story.append(Spacer(1, 0.2*inch))

tweet_count = 1
for section_title, tweets in sections:
    story.append(Paragraph(section_title, section_style))
    for tweet in tweets:
        story.append(Paragraph(f"{tweet_count}.", number_style))
        story.append(Paragraph(tweet, tweet_style))
        tweet_count += 1

doc.build(story)
print(f"PDF saved to: {output_path}")

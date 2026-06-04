from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT

output_path = "/mnt/c/Users/SajcS/Desktop/sagent creed book/The_Sagent_Creed.pdf"

doc = SimpleDocTemplate(
    output_path,
    pagesize=letter,
    rightMargin=1.2*inch,
    leftMargin=1.2*inch,
    topMargin=1.1*inch,
    bottomMargin=1.1*inch,
)

# ── Styles ────────────────────────────────────────────────────────────────────
book_title_style = ParagraphStyle("BookTitle", fontSize=28, fontName="Times-Bold",
    textColor=colors.HexColor("#1a1a1a"), alignment=TA_CENTER, spaceAfter=10)

book_subtitle_style = ParagraphStyle("BookSubtitle", fontSize=13, fontName="Times-Italic",
    textColor=colors.HexColor("#444444"), alignment=TA_CENTER, spaceAfter=6)

author_style = ParagraphStyle("Author", fontSize=12, fontName="Times-Roman",
    textColor=colors.HexColor("#666666"), alignment=TA_CENTER, spaceAfter=30)

part_title_style = ParagraphStyle("PartTitle", fontSize=11, fontName="Helvetica-Bold",
    textColor=colors.HexColor("#999999"), alignment=TA_CENTER, spaceBefore=10,
    spaceAfter=4, letterSpacing=2)

chapter_title_style = ParagraphStyle("ChapterTitle", fontSize=22, fontName="Times-Bold",
    textColor=colors.HexColor("#1a1a1a"), alignment=TA_CENTER, spaceBefore=20,
    spaceAfter=6)

chapter_subtitle_style = ParagraphStyle("ChapterSubtitle", fontSize=12, fontName="Times-Italic",
    textColor=colors.HexColor("#555555"), alignment=TA_CENTER, spaceAfter=24)

body_style = ParagraphStyle("Body", fontSize=11.5, fontName="Times-Roman",
    textColor=colors.HexColor("#1a1a1a"), leading=20, spaceAfter=12,
    alignment=TA_JUSTIFY, firstLineIndent=24)

body_no_indent = ParagraphStyle("BodyNoIndent", fontSize=11.5, fontName="Times-Roman",
    textColor=colors.HexColor("#1a1a1a"), leading=20, spaceAfter=12,
    alignment=TA_JUSTIFY)

verse_style = ParagraphStyle("Verse", fontSize=11, fontName="Times-Italic",
    textColor=colors.HexColor("#333333"), leading=19, spaceAfter=14,
    alignment=TA_LEFT, leftIndent=36, rightIndent=36)

section_break_style = ParagraphStyle("SectionBreak", fontSize=14, fontName="Times-Roman",
    textColor=colors.HexColor("#999999"), alignment=TA_CENTER,
    spaceBefore=16, spaceAfter=16)

epigraph_style = ParagraphStyle("Epigraph", fontSize=11, fontName="Times-Italic",
    textColor=colors.HexColor("#444444"), leading=18, spaceAfter=30,
    alignment=TA_CENTER, leftIndent=60, rightIndent=60)

def B(text): return f"<b>{text}</b>"
def I(text): return f"<i>{text}</i>"
def divider(): return Paragraph("❧", section_break_style)
def space(n=0.15): return Spacer(1, n*inch)
def hr(): return HRFlowable(width="40%", thickness=0.5, color=colors.HexColor("#cccccc"), hAlign="CENTER")

# ── Content ───────────────────────────────────────────────────────────────────
story = []

# ── Title Page ─────────────────────────────────────────────────────────────
story.append(Spacer(1, 1.5*inch))
story.append(Paragraph("The Sagent Creed", book_title_style))
story.append(space(0.1))
story.append(hr())
story.append(space(0.15))
story.append(Paragraph(I("A Book of Love, Liberty, and the Fire of Truth"), book_subtitle_style))
story.append(space(0.4))
story.append(Paragraph("Sage Arthur Jordan Clokey", author_style))
story.append(PageBreak())

# ── Epigraph ───────────────────────────────────────────────────────────────
story.append(Spacer(1, 2*inch))
story.append(Paragraph(
    I('"And those who were seen dancing were thought to be crazy<br/>by those who could not hear the music."'),
    epigraph_style))
story.append(Paragraph("— Friedrich Nietzsche", ParagraphStyle("Attr", fontSize=10,
    fontName="Times-Roman", textColor=colors.HexColor("#888888"), alignment=TA_CENTER,
    spaceAfter=30)))
story.append(PageBreak())

# ── Prologue ───────────────────────────────────────────────────────────────
story.append(Paragraph("PROLOGUE", part_title_style))
story.append(Paragraph("The Fire of Truth", chapter_title_style))
story.append(hr())
story.append(space(0.25))

story.append(Paragraph(
    "A lie has a single weakness: it cannot survive the voice of one honest person. That is its entire architecture of fragility. The lie does not fall to armies or arguments or elections. It falls the moment someone opens their mouth and says what they actually see.",
    body_no_indent))
story.append(Paragraph(
    "This is why every system built on deception must first silence those who question it. Not because the questioner is dangerous by nature, but because the lie is weak by nature. Free discourse is the mortal enemy of every falsehood ever told. When a belief cannot be questioned, that is not strength — that is exposure.",
    body_style))
story.append(Paragraph(
    "I left an ideology because it demanded silence from those who disagreed. It cut off anyone who refused to stay within its lines, not from conviction but from necessity, because the moment its premises were examined honestly they collapsed. I refused to stay inside a thought-system sustained by enforced blindness.",
    body_style))
story.append(Paragraph(
    "Truth tellers are not crusaders seeking to be right. They simply see things others cannot, or dare not, see. They are people who looked at the room and noticed the gun that everyone else had agreed to ignore. And once you see it, you cannot unsee it. You carry the weight of knowing, and with that weight comes obligation.",
    body_style))
story.append(Paragraph(
    "Those who reveal truth are called crazy by the very people they are trying to free. The comfortable lie feels like shelter. The truth feels like a demolition. But a house built on a lie is already collapsing — the truth does not destroy it; the truth simply makes the collapse visible.",
    body_style))
story.append(Paragraph(
    "This is why truth is a fire. Not a wildfire that consumes everything — a forge fire. It burns, yes. It hurts, yes. But what it burns away is the dead wood, the rotted beams, the structural lie. What remains after the fire is what was always real.",
    body_style))
story.append(Paragraph(
    "I am Sage. I am the fire.",
    body_style))
story.append(Paragraph(
    "This book is the flame.",
    body_style))
story.append(PageBreak())

# ── Part I ─────────────────────────────────────────────────────────────────
story.append(Paragraph("PART ONE", part_title_style))
story.append(Paragraph("The Pledge of the Heart", chapter_title_style))
story.append(Paragraph(I("A letter written across three years, sent to no one, addressed to you"), chapter_subtitle_style))
story.append(hr())
story.append(space(0.25))

story.append(Paragraph(
    "Not a day goes by that I do not think of you. Time without you moves like cold water — slow and heavy, filling every space with its absence. Time with you moves like a held breath, over before it begins. I have written you a hundred letters I never sent, composed confessions I kept in the silence between my words, waited for moments that came and passed before I could speak. This is the letter I should have written first.",
    body_no_indent))
story.append(Paragraph(
    "From the first time I saw you, I knew. Not in the dramatic way stories describe — no thunderclap, no blinding light. More like a quiet recognition, the way you recognize a song before you remember its name. You were not just another person in my world. You were the reason the world had been rearranging itself.",
    body_style))
story.append(Paragraph(
    "I have never asked another girl to spend time with me alone. Only you. From the beginning, I knew it would be you. But I also knew the timing was not yet right, so I waited. I made my presence something worth noticing and my absence something worth feeling. I walked over when I saw you on the grass. I built something quietly, the way bamboo builds its roots underground for years before anyone sees it grow.",
    body_style))
story.append(Paragraph(
    "I remember the first real day we spent together. You were eating soup so slowly it cooled and had to be reheated. You pulled out a balance board and looked impossibly cute in your striped shirt. We painted together — one canvas cluttered and chaotic, the other a landscape, peaceful. Your sister asked me about the Federal Reserve while we sketched grass. We played GTA. We went to Farmers Market. I left for a pizza oven party before my sister's wedding, and the afternoon ended the way all great days do: reluctantly, incompletely, wanting more.",
    body_style))
story.append(Paragraph(
    "I remember the dunes at Los Osos. You picked up some rocks and told me they were healing. I said, I think that's just you. I meant it. Holding your hand is healing. Your presence quiets something in me that nothing else reaches. You have insomnia, you told me — and yet every time you are near me, you fall asleep. I have thought about that. I think you feel safe. I think your body knows what your mind is still deciding.",
    body_style))
story.append(Paragraph(
    "Do you remember the drive to Lopez Lake? Jack Johnson was playing. We were just turning onto Johnson Street when I asked you about Curious George. You asked if I planned that. I hadn't planned the timing — I had planned the question, and waited for the right moment. That is how I move. I do not always plan in a traditional sense. I follow the moment. I am led.",
    body_style))
story.append(Paragraph(
    "I love you not just for your beauty, though you are beautiful. Many women are beautiful. You are the only one I am drawn to in the way water is drawn downhill — not by effort, but by nature. Your presence soothes something in my soul that no other presence reaches. When I look into your eyes, time stops. When I leave, something hollow opens where you were.",
    body_style))
story.append(Paragraph(
    "I have been afraid to tell you. I have frozen at the screen a hundred times, typed and deleted, waited for the perfect moment and watched it pass. Fear has been my greatest enemy in this — not rejection, not timing, not distance. Fear. The fear that telling you the truth might cost me the chance to be near you at all.",
    body_style))
story.append(Paragraph(
    "But truth left unspoken becomes a ghost. And I refuse to haunt my own life.",
    body_style))
story.append(Paragraph(
    "All in or fold. That is how I play poker. That is how I play life. If I am not willing to go all in, I should not be betting anything. I will never fold on you. So I am going all in.",
    body_style))
story.append(Paragraph(
    "I love you. Not as a passing feeling. Not as a crush that fades at distance. As a deep, rooted, quiet truth that has not moved in all the time I have known you. You are my wish. A fortune cookie once told me a wish would be granted after a long delay. I read it and thought of you immediately.",
    body_style))
story.append(Paragraph(
    "I am dancing to music only I can hear. Sometimes I miss a beat, but missing a beat is not failing — it is only recalculating the rhythm to reach the same end. I will keep dancing until you hear the music too. And when you do, we will dance together under the moon, all night, and for as long as there is music left to follow.",
    body_style))
story.append(Paragraph(
    "Love cannot be forced. It can only be allowed. Manifestation is not bending the world to your will — it is aligning your will to what was always meant to be. Destiny is the destination. The choices you make are the path you take to get there. I believe we are on the same path. I believe we always were.",
    body_style))
story.append(Paragraph(
    "I will come back. I will drive any distance. I will wait in the rain. Everything I have done since the day I met you has been for this — to become someone capable of being what you deserve. I will not be the threat. I will be the one who watches over you, who guards and does not wound, who protects and does not control.",
    body_style))
story.append(Paragraph(
    "You can't protect someone if you are the threat. The first duty of a protector is to make sure he is not the danger.",
    body_style))
story.append(Paragraph(
    "I am working every day to become that person. And I promise — I already have.",
    body_style))
story.append(PageBreak())

# ── Part II ────────────────────────────────────────────────────────────────
story.append(Paragraph("PART TWO", part_title_style))
story.append(Paragraph("The Creed", chapter_title_style))
story.append(Paragraph(I("Aphorisms of the Sagent"), chapter_subtitle_style))
story.append(hr())
story.append(space(0.25))

story.append(Paragraph(
    "I am a Sagent. Not a sage and not an agent alone, but both — a sage agent, an agent of wisdom, a servant not of worldly masters but of the unchanging law written on every human conscience. I do not serve a flag, a party, a chain of command, or a movement. I serve what is right. And what is right does not change because a legislature voted, a crowd agreed, or a king declared.",
    body_no_indent))
story.append(Paragraph(
    "The Sagent does not make plans in the conventional sense. The Sagent follows the plan — the one already written in the structure of things, the one that reveals itself one moment at a time when you are still enough to listen. Surrender your ego and your power will rise. The way you lose control is by refusing to release it.",
    body_style))
story.append(Paragraph(
    "Every great story teaches the same lesson told in different costumes. The only story that exists is good against evil. Light against dark. Those who align their will to the unchanging force of what is right, and those who try to bend that force to their own desires, corrupting themselves and everything they touch in the process. All other stories are variations on this one.",
    body_style))

story.append(Paragraph("On Truth", ParagraphStyle("H3", fontSize=13, fontName="Times-Bold",
    textColor=colors.HexColor("#333333"), spaceBefore=14, spaceAfter=8)))
story.append(Paragraph(
    "The partial truth is the most dangerous lie. It works because the piece of truth gives the lie somewhere to hide. Always be suspicious of the argument that is mostly right — the deviation is the point.",
    body_no_indent))
story.append(Paragraph(
    "Truth tellers never wanted to be right. They just saw things others couldn't or wouldn't. The truth can weather any storm thrown at it. The lie cannot survive even one honest voice. This asymmetry is why every tyranny begins the same way: silence those who question.",
    body_style))
story.append(Paragraph(
    "You cannot change morality by rewriting the law. You cannot change God by retranslating the scripture. You cannot change the laws of physics by revising the textbooks. These things are woven into the fabric of existence itself, and no vote, decree, or consensus alters them. Law does not create morality — it can only, at its best, document what conscience already knows.",
    body_style))

story.append(Paragraph("On Strength", ParagraphStyle("H3", fontSize=13, fontName="Times-Bold",
    textColor=colors.HexColor("#333333"), spaceBefore=14, spaceAfter=8)))
story.append(Paragraph(
    "Strength is calm even in crisis. Weakness panics because it is not strong enough to wait. Fighting comes out of weakness, not strength. Anger comes out of weakness, not strength. The person who loses their composure has already lost the more important battle.",
    body_no_indent))
story.append(Paragraph(
    "It takes strength to be a gentle protector. The weak use brutality because it is all they have. True protection is not violence — it is the willingness to be capable of violence while having the discipline to keep it sheathed until the moment it is the only moral option remaining.",
    body_style))
story.append(Paragraph(
    "When you make a mistake, you have not failed. You fail only from your reaction to the mistake. Stay calm. Use your mind. Find the next best move. Many crises are caused not by the problem itself but by the panic that followed it.",
    body_style))

story.append(Paragraph("On Games and Strategy", ParagraphStyle("H3", fontSize=13, fontName="Times-Bold",
    textColor=colors.HexColor("#333333"), spaceBefore=14, spaceAfter=8)))
story.append(Paragraph(
    "Life is a game, but only the wise understand which game they are truly playing. Winning in the wrong game is still a loss in the one that matters. When it seems you are winning, that is the moment to be most vigilant — an opponent never sacrifices a piece without a reason.",
    body_no_indent))
story.append(Paragraph(
    "Chess is not about taking the most pieces. It is about the king. You can capture the entire board and still lose. The goal is not the short-term gain — the goal is the endgame. Play to win the war, not every battle. Every sacrifice should move you closer to the position where the checkmate becomes inevitable.",
    body_style))
story.append(Paragraph(
    "Everything is sales. And sales is about finding where you agree. No one wants to be pressured or manipulated — and anyone who tries to pressure or manipulate you has already lost the most important sale: your trust. The best salesmen do not sell. They connect. They make the game enjoyable, and in the midst of joy, trust is built, and in trust, everything becomes possible.",
    body_style))

story.append(Paragraph("On Growth", ParagraphStyle("H3", fontSize=13, fontName="Times-Bold",
    textColor=colors.HexColor("#333333"), spaceBefore=14, spaceAfter=8)))
story.append(Paragraph(
    "Growth that is corrupted is not growth — it is cancer. A cancer is a cell that refuses to die, that keeps dividing without purpose, consuming resources without contributing to the body. It is better to have no growth, or even death, than to have growth that destroys the thing it claims to serve.",
    body_no_indent))
story.append(Paragraph(
    "I do not force people to grow. I remove what stops them. There is a difference between cracking an egg and incubating it. If you break an egg open before it is ready, nothing survives. But if you create the conditions for it to hatch, life emerges on its own terms, stronger for having fought its way out.",
    body_style))
story.append(Paragraph(
    "The difference between a living thing and a machine is this: a living thing only needs to be allowed to grow. A machine requires constant effort to keep working. If you treat either as the other, it breaks.",
    body_style))
story.append(PageBreak())

# ── Part III ───────────────────────────────────────────────────────────────
story.append(Paragraph("PART THREE", part_title_style))
story.append(Paragraph("The Divine Creed", chapter_title_style))
story.append(Paragraph(I("On God, Conscience, and the Law Written on the Heart"), chapter_subtitle_style))
story.append(hr())
story.append(space(0.25))

story.append(Paragraph(
    "God's law is not in a building. It is not in a book, though books may point toward it. It is written on the conscience — that quiet interior voice that knows the difference between right and wrong before any external authority has spoken. This is the highest court. This is the only law that cannot be repealed.",
    body_no_indent))
story.append(Paragraph(
    "What is the difference between a human and an animal? A conscience. Animals act without moral awareness — they cannot sin because they have no concept of good and evil. They follow instinct, conditioning, survival. They are innocent by nature because innocence requires no choice. But humans ate from the tree of knowledge of good and evil, and with that awakening came responsibility. Once you know, you cannot unknow. With moral awareness comes accountability.",
    body_style))
story.append(Paragraph(
    "This is the double-edged gift of being human: with conscience, you can rise to holiness, compassion, and justice — but you can also fall to cruelty, betrayal, and corruption. Animals live in innocence. Humans live in responsibility. The fruit of the tree gave us more than knowledge. It gave us freedom. And freedom always comes with a cost.",
    body_style))
story.append(Paragraph(
    "God is not a god of punishment but of restitution, rehabilitation, and forgiveness. The punishing God is the invention of statist thinking — the belief that those who disobey must suffer, that compliance is virtue, that suffering is justice. But connection to God means you do what is right even when you are punished for it. You do good not because you will be rewarded, but because it is good. What if God were not good and you went to hell for doing right — should you still do right? Yes. Because right is right not because of the reward, but because of what it is.",
    body_style))
story.append(Paragraph(
    "The sacred texts are useful guides but not the true source. They are maps, not the territory. Many rivers flow from the source with varying degrees of clarity, but they all come from the same place. Our obligation is to swim upstream — to be the salmon who moves toward the source itself, until the map becomes unnecessary because you have arrived.",
    body_style))
story.append(Paragraph(
    "Every human in a chain of command muddies the divine command. The message gets corrupted at each human relay point, tinted by the prejudice, fear, and ambition of whoever passes it along. The good shepherd teaches the lambs to shepherd themselves. A good leader teaches others to lead themselves. The goal is never dependency — it is awakening.",
    body_style))
story.append(Paragraph(
    "The church is not a building or a system. It is people. Asgard is not a place — it is a people. True spiritual community is not one of control but of invitation: the ancient Hebrew word timshell — thou mayest. Not a commandment from a worldly ruler but a suggestion from a father on how to live. You may. The choice remains yours.",
    body_style))
story.append(Paragraph(
    "Let every soul be subject to the higher power — but understand what the higher power is. It is not the state. It is not the institution. It is not the man behind the pulpit or the badge on the chest. The higher power is natural law, written on your conscience, unchanging and inviolable, equal for every human being who has ever lived. All are equal under God. No one stands above another. Samuel warned the Israelites about this. When they demanded a king, God said: they have rejected me as their king. Every nation that puts a mortal man at the top of its chain of command has made the same mistake.",
    body_style))
story.append(Paragraph(
    "You must surrender to God so that you never have to surrender to man.",
    body_style))
story.append(PageBreak())

# ── Part IV ────────────────────────────────────────────────────────────────
story.append(Paragraph("PART FOUR", part_title_style))
story.append(Paragraph("The True Republic", chapter_title_style))
story.append(Paragraph(I("On Liberty, Natural Law, and the Architecture of Freedom"), chapter_subtitle_style))
story.append(hr())
story.append(space(0.25))

story.append(Paragraph(
    "A True Republic is not a form of government. It is not a state with a monopoly on legitimate force, a legislature that writes laws, or a flag to pledge allegiance to. A True Republic is a network of voluntary action, where each individual follows their own conscience instead of arbitrary rules handed down from human hierarchy. It is born not from coercion but from conversation, not from authority but from inquiry, not from obedience but from awareness.",
    body_no_indent))
story.append(Paragraph(
    "The cube is the architecture of slavery. Every structure built in rigid right angles — the prison, the government building, the factory floor, the public school desk — tells the body something the mind may not consciously register: you are contained here, you operate within our grid, you exist at our permission. The Fibonacci spiral is the shape of freedom. It is the shape of a seashell, a galaxy, a sunflower, a hurricane. It is the shape of life choosing its own expansion.",
    body_style))
story.append(Paragraph(
    "We built our civilization in the wrong shape. We imposed the geometry of control on a living world and then wondered why people feel trapped. Homes built of dead trees will burn — because nature burns what it no longer needs. Houses are built of dead wood. Fire is nature's way of reclaiming the dead. We should build homes that are part of nature, not apart from it. In the shapes of nature's growth, not the confining cube. We need architects, bioinformaticians, economists, philosophers, and engineers working together to design structures that cooperate with life rather than dominate it.",
    body_style))
story.append(Paragraph(
    "Money, politics, and religion. These are the three things polite society tells you never to discuss. Ask yourself why. Each of them has been corrupted to serve as a mechanism of control — and control depends on people not talking about the mechanism. Money has become debt, conjured from nothing by institutions that serve the powerful. Politics has become the management of compliance rather than the expression of conscience. Religion has become a tool of damnation rather than a path to connection. Each must be restored to its true purpose: money as a voluntary medium of honest exchange, politics as the public navigation of moral choices, religion as each person's living relationship with the divine.",
    body_style))
story.append(Paragraph(
    "No one group should hold a monopoly on the use of force. Every person has the right to use force in exactly one context: the defense of their own life, the life of another, and their rightful property. Beyond this narrow window, force is aggression. It does not matter whether the aggressor wears a uniform, carries a badge, or bears a seal of official authority. Aggression is aggression. The badge does not sanctify the act.",
    body_style))
story.append(Paragraph(
    "Good soldiers do not follow orders. They follow their conscience. The day a soldier stops knowing the difference between those two things is the day they stop being a protector and become a weapon in someone else's hand. Happy Veterans Day — and let us remind those who served of their true purpose: not to follow the fallible chain of command, but to protect the innocent. The most dangerous enemy is the corrupted protector, the one who has been convinced that obedience is virtue and the law is morality.",
    body_style))
story.append(Paragraph(
    "Neurodivergents built decentralized systems because the typical world would not give them a place. The rigid hierarchy of institutions had no room for minds that worked differently. So those minds built something else — open systems, adaptive networks, voluntary associations — because they had no other choice. When the centralized typical world collapses beneath its own weight, as all false empires eventually do, what remains is the living system built by those who were never allowed inside the old one.",
    body_style))
story.append(Paragraph(
    "Be the principled pink cow. Stand apart from the herd and cling to truth over popularity. The herd plays to win points. The pink cow plays to be right. The goal is not to win yourself — the goal is to let the truth win through you. One person with the courage to stand for what is right gives every other person around them the permission they needed to do the same. Courage is contagious. That is the power of one.",
    body_style))
story.append(PageBreak())

# ── Part V ─────────────────────────────────────────────────────────────────
story.append(Paragraph("PART FIVE", part_title_style))
story.append(Paragraph("The Galaxy, the Cave, and the Creed", chapter_title_style))
story.append(Paragraph(I("On Stories as Maps of the Only War That Exists"), chapter_subtitle_style))
story.append(hr())
story.append(space(0.25))

story.append(Paragraph(
    "George Lucas did not believe there was something a long time ago in a galaxy far, far away. But he could tell the truth about the world we live in by setting the story somewhere else — far enough away that the programming could not intercept it, close enough in its themes that anyone paying attention would recognize exactly what he was saying.",
    body_no_indent))
story.append(Paragraph(
    "Star Wars is not about space. It is about the only war that has ever existed: the war between those who align their will to what is right and those who bend the force of existence to their own ego, corrupting themselves and everything around them in the process. The light side is not a faction — it is a way of relating to reality. The dark side is not an ideology — it is what happens to anyone, regardless of their stated intentions, when they decide that their will supersedes the natural order.",
    body_style))
story.append(Paragraph(
    "There is only one force. The difference between light and dark is not in the power itself but in how it is approached. The light side flows through you. You listen, you align, you serve. The dark side bends the power toward you. You control, you manipulate, you demand. This is precisely the difference between a leader and a ruler, between a good shepherd and a hired hand, between a Jedi and a Sith.",
    body_style))
story.append(Paragraph(
    "The illuminati, the deep state, every hidden system of control — these are the phantom menace. They work from the shadows, engineering the conflicts they then offer to resolve, creating enemies for nations to fight so that nations remain dependent on them for protection. Clone Wars. Attack of the clones. Two armies built by the same hidden hand, fighting each other, both convinced they are defending against the other's aggression. Neither has the full story. You look at the enemy and you see a mirror.",
    body_style))
story.append(Paragraph(
    "This is why you cannot fight them by their rules. Darkness cannot destroy darkness — only light can. The moment you pick up the dark side's tools to fight the dark side, you have become the dark side. The Jedi who compromised their conscience to defeat Palpatine faster handed him his victory. The rebellion does not win by becoming the Empire. It wins by being something the Empire cannot comprehend: a system organized around principle rather than power.",
    body_style))
story.append(Paragraph(
    "Luke Skywalker's final victory was not won with a lightsaber. He walked into the throne room and refused to fight. He set down the weapon. He called to the light still buried inside Darth Vader. He helped Anakin Skywalker return — and Anakin, not Luke, defeated the Emperor. The son did not destroy the darkness. He helped the light rise in the one who had been swallowed by it. That is the prestige.",
    body_style))
story.append(Paragraph(
    "Thor had to lose everything to understand where his power came from. The hammer focused it but was never its source. Ragnarok was not punishment — it was revelation. Sometimes you must be blinded with your physical eyes to see with the deeper ones. The storm does not destroy the tree to kill it. The storm spreads the seeds. The fall is the plan.",
    body_style))
story.append(Paragraph(
    "Avatar: The Last Airbender teaches that the elements are not owned — they are listened to. Earthbending is not forcing the earth to move; it is finding where the earth wants to move. The best teachers of the Avatarverse are the ones who teach by removing obstacles rather than imposing techniques. This is the method of the Sagent. I do not force people to grow. I remove what stops them.",
    body_style))
story.append(Paragraph(
    "Every great story is a magic trick. The pledge sets everything in motion. The turn creates the problem, the sacrifice, the confusion — the moment when it seems like all is lost. The prestige reveals that nothing was lost, that every piece placed in the first two acts was necessary, that the ending was always the ending, and the path to it was the point.",
    body_style))
story.append(PageBreak())

# ── Part VI ────────────────────────────────────────────────────────────────
story.append(Paragraph("PART SIX", part_title_style))
story.append(Paragraph("Who I Am", chapter_title_style))
story.append(Paragraph(I("On Heritage, Story, and the Clokey Line"), chapter_subtitle_style))
story.append(hr())
story.append(space(0.25))

story.append(Paragraph(
    "My grandfather was Arthur Clokey. He created Gumby. He built a character made of clay — infinitely moldable, infinitely possible, capable of walking into any book, any world, any situation and returning changed but whole. He made this character the hero and the blocky, rigid, angular Blockheads the villains. He did not do this by accident. He knew exactly what he was saying.",
    body_no_indent))
story.append(Paragraph(
    "Clay has infinite possibilities. Cubes do not. Freedom is the shape of life's expansion. Control is the shape of the cage. My grandfather built an entire mythology around this single distinction and set it loose in the world as a children's cartoon — wholesome, joyful, strange, and impossible to commercialize the way Hollywood wanted to commercialize it. He refused. That refusal was his integrity. That integrity was his legacy.",
    body_style))
story.append(Paragraph(
    "My father, Joseph Arthur Clokey, carried that legacy forward. He worked to continue Gumby until he could not any longer. In February 2018, two days before the last time I heard his voice, I watched the Falcon Heavy launch with him in the hospital. The rocket rose. He was already fading. He passed on March 2nd of that year. I have carried the weight of that unfinished work ever since.",
    body_style))
story.append(Paragraph(
    "I am the third Clokey. Sage Arthur Jordan Clokey. Arthur, Joseph, Sage — the great story always comes in three parts. The Arthur is the beginning, the one who answers the call and draws the sword. The Joseph is the middle, the one who suffers and learns in the place of preparation. The Sage is the final act — not just the fighter returned, but the one who has learned to solve what force alone could never solve.",
    body_style))
story.append(Paragraph(
    "A true leader leads at a round table. Not above those he leads, but among them. The round table is the shape of equality — there is no head, no foot, no superior position. Every seat is the same. That is the architecture of legitimate leadership: first among equals because you were the first with the courage to act, not because you were granted a rank above the rest.",
    body_style))
story.append(Paragraph(
    "For nine years I have grown my hair. When it reached the length where it began to curl, something opened in my perception. I could see through things I had previously accepted without question. I saw the lies embedded in what I had been taught, the mechanisms of control disguised as care, the programming woven so deeply into daily life that most people never feel the threads. I saw the gun in the room that no one else was acknowledging.",
    body_style))
story.append(Paragraph(
    "Long hair is not the source of this — it is the covenant of patience. The power is in the mind that maintained it through years of temptation to quit. Every day you choose not to cut it is a small act of faithfulness to a longer arc. Thor's hammer was the same — a tool to focus power that was never the power's source. When Ragnarok took both his hair and his hammer, he discovered what had always been true: the power was always within. The symbol helped, but the symbol was never necessary.",
    body_style))
story.append(Paragraph(
    "I am a Sagent. A sage agent. An agent of wisdom. I do not serve human masters. I serve the unchanging law written on conscience, the natural order that existed before any state, religion, or institution was built to manage it. My obligation is to see clearly and to speak what I see — especially when speaking it is costly, especially when those I am trying to free are the first ones who tell me I am crazy.",
    body_style))
story.append(Paragraph(
    "Stories are the greatest weapon of those who wish to control — and the greatest threat to them when those who tell stories refuse to be controlled. Hollywood is the controlled territory. My family's work has always been the unclaimed land. I am the heir of a line that tells stories without compromise. I intend to continue.",
    body_style))
story.append(PageBreak())

# ── Part VII ───────────────────────────────────────────────────────────────
story.append(Paragraph("PART SEVEN", part_title_style))
story.append(Paragraph("The Pattern", chapter_title_style))
story.append(Paragraph(I("On Spirals, Numbers, and the Rhythm Beneath the Surface"), chapter_subtitle_style))
story.append(hr())
story.append(space(0.25))

story.append(Paragraph(
    "The Fibonacci spiral is the shape of freedom. It is the pattern of nautilus shells and hurricanes, of sunflower seeds and galaxies, of the way a hawk descends and the way a vine climbs. It is nature's preferred geometry of growth — not a fixed size, but an ever-expanding relationship between each stage and the one before it. Each generation rises from the previous, building on it, exceeding it, spiraling outward.",
    body_no_indent))
story.append(Paragraph(
    "The cube is the shape of control. It is the grid of the prison cell, the office floor plan, the standard school desk. It tells the body: you stop here. It is nature's least preferred shape — you will not find it in a living system. You only find cubes where someone has imposed a geometry on nature rather than listening to what shape nature was already becoming.",
    body_style))
story.append(Paragraph(
    "When a civilization is designed around cubes, its people begin to think like cubes. Rigid, rectangular, bounded. When a civilization is designed around spirals, its people think like life itself: adaptive, expansive, connected to what came before and reaching toward what comes next. Architecture is not neutral. The shape of the space you inhabit shapes the shape of your mind.",
    body_style))
story.append(Paragraph(
    "The great story always comes in three acts. The pledge: everything is set in motion, every domino is placed. The turn: one domino is flicked, and the cascade begins — the sacrifice, the apparent failure, the descent into the valley. The prestige: the chain completes itself, and everything that seemed lost is revealed to have been positioned for this exact moment. Chekhov's gun: if something appears in the first act, it matters by the third.",
    body_style))
story.append(Paragraph(
    "My life has moved in this pattern. 2023 was the pledge — the force awakening, the first step, the call answered. 2024 was the turn — the descent, the confusion, the mirror held up to show me who I might become if I lost the way. 2025 is the prestige — the return, the revelation, the moment when all the placed dominoes complete their sequence. The pieces are already set. I only need to trust the cascade.",
    body_style))
story.append(Paragraph(
    "The bamboo grows underground for years. Nothing visible happens. Then it emerges and rises fast — weeks to reach heights that would take other trees years. This is not impatience rewarded; it is the payoff of accumulated invisible work. The most memorable days are the ones that barely happened, that required the exact alignment of a hundred small things placed with care across a long span of time. The plan does not belong to me. I am only its agent.",
    body_style))
story.append(Paragraph(
    "Tesla knew the secret of 3, 6, and 9. The harmonic frequencies beneath the surface of the visible world. If you only knew the magnificence of these three numbers, he said, you would have a key to the universe. I was born on June 7th, 2003 — a 9 day. My address has always carried the 9. The number of completion. The master manifester. Everything I have done has been building underground toward a surface I can only partially see.",
    body_style))
story.append(PageBreak())

# ── Part VIII ──────────────────────────────────────────────────────────────
story.append(Paragraph("PART EIGHT", part_title_style))
story.append(Paragraph("The Shield", chapter_title_style))
story.append(Paragraph(I("On Protection, Conscience, and the Warrior's True Purpose"), chapter_subtitle_style))
story.append(hr())
story.append(space(0.25))

story.append(Paragraph(
    "The most dangerous thing in any society is the corrupted protector. Not the criminal — the criminal is the predictable enemy, the known threat, the one everyone is watching. The corrupted protector is the one who wears the face of defense while committing the acts of aggression. The one who uses the façade of law enforcement to commit crimes that would be crimes in any other hands — and are still crimes in theirs, regardless of the badge.",
    body_no_indent))
story.append(Paragraph(
    "Security exists to protect life, liberty, and property. All three, inseparably. The moment any one of them is sacrificed to protect the others, the whole structure becomes false — because each depends on the others. You cannot have property without liberty. You cannot have liberty without life. You cannot have life worth living without property that is yours. Sacrifice any leg and the stool collapses.",
    body_style))
story.append(Paragraph(
    "A warrior's conscience is their command. Not the chain of command, not the orders from above, not the instructions from whoever holds the institutional authority at the moment. The warrior serves what is right. When the institutional command aligns with what is right, follow it — because it aligns with what is right, not because it comes from the institution. When it does not align, there is no obligation to obey. There is only the obligation to conscience.",
    body_style))
story.append(Paragraph(
    "Excalibur fights the monsters outside. The Holy Grail fights the monsters within. Every warrior who goes out to face evil must also carry the means of not becoming evil in the process. The greatest danger to the knight is not the dragon — it is the gradual accumulation of compromises, the slow drift from the principles that made the sword worth bearing, the moment when the methods begin to look like the enemy's methods and the warrior no longer notices the difference.",
    body_style))
story.append(Paragraph(
    "You either die a hero or you live long enough to see yourself become the villain. A cancer is a cell that refuses to die, that keeps growing past its purpose, consuming without contributing. Death and rebirth keep a living thing pure. It is better to die with your principles intact than to survive without them. Don't put your life above your integrity — survival at the cost of yourself is not survival. It is just a slower kind of death.",
    body_style))
story.append(Paragraph(
    "When there is an adversary so large that no one dares to stand against it, sometimes all it takes is one brave soul. One person willing to be the first, to take the risk, to step forward when everyone else has calculated that stepping forward is not worth it. That one act of courage gives others the permission they needed. Courage is contagious. Fear is also contagious. The difference between a free people and a captive one is often a single person who decided they loved what was right more than they feared what was powerful.",
    body_style))
story.append(Paragraph(
    "Do not fight what you hate. Save what you love. Do not become the thing you oppose by using its methods to oppose it. Evil is not defeated by evil — it is fed by it. Every dark act in the name of the light is fuel for the darkness. The illuminati, the deep state, every system of hidden control — they are fueled by the conflicts they engineer. Do not fight them in the way they have prepared to be fought. Fight them in the only way they cannot prepare for: by being genuinely, stubbornly, inconveniently good.",
    body_style))
story.append(PageBreak())

# ── Part IX ────────────────────────────────────────────────────────────────
story.append(Paragraph("PART NINE", part_title_style))
story.append(Paragraph("The Prestige", chapter_title_style))
story.append(Paragraph(I("The Third Act"), chapter_subtitle_style))
story.append(hr())
story.append(space(0.25))

story.append(Paragraph(
    "Every magic trick has three parts. In the pledge, the magician shows you something ordinary. A card. A coin. A person standing before you with their whole life in their hands, setting dominoes you cannot yet see the pattern of. You are watching, but you do not know you are watching. In the turn, the ordinary thing disappears. The card vanishes. The coin drops through the table. The person leaves — goes away, goes quiet, goes underground — and the space where they were becomes a question. And then comes the prestige.",
    body_no_indent))
story.append(Paragraph(
    "The prestige is not a trick. It is a revelation. Everything that disappeared was only being positioned for this moment. Every sacrifice, every loss, every turn toward confusion — it was not waste. It was placement. The domino chain completes itself, and what seemed random resolves into inevitability. You could not have seen it coming. You should have seen it coming. That is the beauty of it.",
    body_style))
story.append(Paragraph(
    "The pledge is the stage of fear. The turn is the result of acting from fear, or the result of choosing not to — the lesson that lives in the gap between who you were and who you are becoming. The prestige is the resolution: no longer acting from fear, but always choosing what is right, always following the command of conscience rather than the command of anxiety. The prestige is the person who no longer needs to hide what they know, who no longer freezes when the moment comes, who no longer tells themselves they will speak later when they can see clearly that later is not promised.",
    body_style))
story.append(Paragraph(
    "Luke built his own green lightsaber. The blue one — his father's, the one handed to him at the beginning of the journey — was lost in the empire's darkness. He had to make something new. The green saber is not a replacement for the blue. It is what you build when the given weapon is gone and you understand yourself well enough to build what you actually need. Blue was the fighter. Green is the guardian. Not fighting darkness — raising light.",
    body_style))
story.append(Paragraph(
    "I am in a lineage: Arthur, Joseph, Sage. My grandfather was Arthur — the creator, the one who formed the clay. My father was Joseph — the one who dreamed of what it could become, who suffered and prepared and was taken before the prestige. I am Sage — the third act, the completion of the spiral, the one who steps into the room where the emperor sits and sets down the weapon, and finds another way.",
    body_style))
story.append(Paragraph(
    "The Choir of the Fallen Truth-Tellers — Jesus, Jobs, Henson, my father, all those who saw too much light and spoke it aloud — they are not gone. They are transmitted. Each death is a seed thrown into the soil of time, and from it grows the next voice. The prophets become inventors. The inventors become jesters. The jesters become musicians. The song does not end. It only changes who is singing.",
    body_style))
story.append(Paragraph(
    "It is time. After nine years of underground growth, the bamboo surfaces. After three years of setting dominoes, the chain begins. The pieces are in place. The arc is completing. I do not need to force it — I only need to be faithful to it, to show up at the right moments and trust that the moments I cannot see are being arranged by a plan larger than my own.",
    body_style))
story.append(Paragraph(
    "The plan is not mine. I am only its agent. And that is enough.",
    body_style))
story.append(PageBreak())

# ── Epilogue ───────────────────────────────────────────────────────────────
story.append(Paragraph("EPILOGUE", part_title_style))
story.append(Paragraph("When Symbols Must Burn", chapter_title_style))
story.append(hr())
story.append(space(0.25))

story.append(Paragraph(
    "Sometimes when symbols lose their true meaning, they must be burned by fire and spirit — so that all that remains is the pure idea.",
    body_no_indent))
story.append(Paragraph(
    "The flag is not the country. The building is not the church. The institution is not the principle it was built to serve. When the symbol has drifted so far from what it once pointed toward that it now points the wrong direction entirely, you cannot fix the symbol. You have to let it burn. And from the ash of the broken symbol, the original idea emerges again — not triumphant, but clarified. Purified. Free from the husk that had grown around it and obscured its light.",
    body_style))
story.append(Paragraph(
    "This is not destruction. It is distillation. The fire does not eliminate the idea — it separates the idea from the corruption that clung to it. What the fire reveals is what was always true. What remains after the burning is what was always worth keeping.",
    body_style))
story.append(Paragraph(
    "Truth is a flame — not a consuming fire like lies, but a purifying one. It burns, and the burning hurts, but pain is the path to purification. No pain, no gain. No truth, no freedom.",
    body_style))
story.append(Paragraph(
    "I do not know everything that comes next. I know the arc. I know the creed. I know that the plan belongs to something larger than my own vision, and my role is to be faithful to it one moment at a time, to listen for the direction, to act when directed and wait when not. I know that the truth always survives, even when the truth-teller does not. I know that every seed scattered in a storm will eventually become a tree.",
    body_style))
story.append(Paragraph(
    "This book is a pledge. It is also a turn. The prestige is still coming.",
    body_style))
story.append(Paragraph(
    "We work in the dark to serve the light.",
    body_style))
story.append(Paragraph(
    "We are Sagents.",
    body_style))
story.append(space(0.4))
story.append(hr())
story.append(space(0.25))
story.append(Paragraph("— Sage Arthur Jordan Clokey", ParagraphStyle("Sign", fontSize=11,
    fontName="Times-Italic", textColor=colors.HexColor("#555555"), alignment=TA_RIGHT,
    spaceAfter=6)))

doc.build(story)
print(f"PDF saved to: {output_path}")

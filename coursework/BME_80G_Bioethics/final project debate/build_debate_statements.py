from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.colors import black, HexColor
from reportlab.lib.enums import TA_LEFT, TA_CENTER

output_path = "/mnt/c/Users/SajcS/Desktop/The Living Age Structured/coursework/BME_80G_Bioethics/final project debate/telehealth_debate_opening_closing.pdf"

doc = SimpleDocTemplate(
    output_path,
    pagesize=letter,
    topMargin=0.75*inch,
    bottomMargin=0.75*inch,
    leftMargin=1*inch,
    rightMargin=1*inch,
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Title'],
    fontSize=16,
    spaceAfter=6,
    textColor=HexColor('#1a1a1a'),
)

subtitle_style = ParagraphStyle(
    'Subtitle',
    parent=styles['Normal'],
    fontSize=10,
    textColor=HexColor('#555555'),
    alignment=TA_CENTER,
    spaceAfter=16,
)

heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading1'],
    fontSize=13,
    spaceBefore=18,
    spaceAfter=8,
    textColor=HexColor('#1a1a1a'),
)

heading2_style = ParagraphStyle(
    'CustomHeading2',
    parent=styles['Heading2'],
    fontSize=11,
    spaceBefore=12,
    spaceAfter=6,
    textColor=HexColor('#333333'),
)

body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['Normal'],
    fontSize=11,
    leading=15,
    spaceAfter=8,
)

bullet_style = ParagraphStyle(
    'CustomBullet',
    parent=styles['Normal'],
    fontSize=11,
    leading=15,
    leftIndent=20,
    spaceAfter=4,
    bulletIndent=8,
)

italic_style = ParagraphStyle(
    'ItalicBody',
    parent=styles['Normal'],
    fontSize=10,
    leading=14,
    spaceAfter=8,
    textColor=HexColor('#444444'),
)

story = []

# Title
story.append(Paragraph("Telehealth Oral Debate — Prepared Statements & Q&A Guide", title_style))
story.append(Paragraph("BME 80G / PHIL 80G — Spring 2026", subtitle_style))
story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#cccccc')))
story.append(Spacer(1, 12))

# ── OPENING STATEMENT ──
story.append(Paragraph("Opening Statement (~2 minutes)", heading_style))
story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#dddddd')))
story.append(Spacer(1, 6))

opening = [
    "When you're sick — really sick — who should be traveling? You, or the doctor?",

    "Right now, the American healthcare system answers: you. You drive to the hospital. You sit in a waiting room. You navigate check-in, insurance verification, billing — all while you are the one who is unwell. The entire system waits for the patient to come to it.",

    "Telehealth flips that. And our side argues it should — permanently.",

    "Telehealth should be a standard, legally protected mode of care delivery. Not because it is new, but because it returns medicine to what it should have always been: doctor-centric instead of hospital-centric. A system where physicians work for patients, not for buildings.",

    "The data supports this. Meta-analyses across dozens of studies show telehealth is clinically non-inferior to in-person care for depression, anxiety, and chronic disease management. Over 247,000 patient surveys confirm satisfaction is equivalent. Telehealth visits cost five times less. CMS estimates $60 million saved in Medicare travel costs alone. And 33 of 45 studies show it reduces emergency department overcrowding.",

    "But this is about more than cost. It is about access. 94% of rural patients would need to travel over 70 miles for specialist care without telehealth. That is an entire day lost. For elderly patients, disabled patients, low-income workers who cannot take a day off — the hospital-centric model is not just inconvenient. It is a barrier to care.",

    "Telehealth lets doctors do what they can do remotely — follow-ups, mental health, chronic disease, medication management — and then go to the patient when physical presence is actually needed. Less wasted time in waiting rooms. Less wasted money keeping people in hospital buildings. More care reaching the people who need it.",

    "That is what we will defend today.",
]

for p in opening:
    story.append(Paragraph(p, body_style))

story.append(Spacer(1, 16))

# ── CLOSING STATEMENT ──
story.append(Paragraph("Closing Statement (~2 minutes)", heading_style))
story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#dddddd')))
story.append(Spacer(1, 6))

closing = [
    "You have heard the data today. Telehealth works as well as in-person care. It costs a fraction as much. It reaches populations that the hospital-centric model has failed for decades — rural communities, elderly patients, people with disabilities, low-income families far from medical facilities.",

    "But I want to acknowledge the strongest point the other side raised — that telehealth cannot replace a physical exam. They are right. And our argument has never been that it should. The question is not telehealth versus in-person care. The question is: who travels? In our current system, the patient always travels — even when they are sick, elderly, or hours from the nearest facility. We are arguing for a model where the doctor goes to the patient when physical presence matters, and the rest happens where the patient already is.",

    "From the lens of <u>utilitarianism</u>, telehealth maximizes well-being for the greatest number. More people access care. Outcomes are equivalent. Costs are lower. Satisfaction is high. Emergency departments are less burdened. Restricting telehealth to preserve a traditional model that serves fewer people at higher cost produces less total well-being.",

    "From the four principles of bioethics: telehealth expands <b>autonomy</b> by giving patients choice over how they receive care. It advances <b>beneficence</b> and <b>non-maleficence</b> by delivering equivalent outcomes with fewer barriers. And it serves <b>justice</b> by extending access to those the current system leaves behind.",

    "Staying at a hospital is expensive. Waiting at a hospital wastes time. Traveling to a hospital while sick is a burden we should not accept as the default when a better option exists.",

    "Telehealth is not a workaround. It is a correction. And it is one we should make permanent.",

    "Thank you.",
]

for p in closing:
    story.append(Paragraph(p, body_style))

story.append(Spacer(1, 16))

# ── LIKELY MODERATOR QUESTIONS ──
story.append(Paragraph("Likely Moderator Questions — Preparation Guide", heading_style))
story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#dddddd')))
story.append(Spacer(1, 6))

story.append(Paragraph(
    "Based on the debate instructions, you are <b>guaranteed</b> at least one question from each of the following three categories. Each response should be ~75 seconds spoken.",
    italic_style
))

# Category 1: Normative Ethics
story.append(Paragraph("1. Normative Ethics Questions", heading2_style))

ethics_qs = [
    ("<b>\"How does your position align with utilitarianism?\"</b> — This is your strongest framework. Telehealth maximizes well-being across the largest number of people: more access, equivalent outcomes, lower costs, higher satisfaction, reduced ED burden. Restricting telehealth to preserve the traditional model produces less total well-being. The utilitarian calculus is clear.",),

    ("<b>\"How would a deontologist view telehealth?\"</b> — Under deontology, we have duties regardless of outcomes. Patients have a right to access care. Physicians have a duty to reach their patients. When a system makes it harder for patients to exercise that right — by requiring travel, wait times, and physical presence for encounters that do not need it — the system violates the duty to provide accessible care. Telehealth fulfills that duty.",),

    ("<b>\"Does virtue ethics support telehealth?\"</b> — A virtuous physician seeks the patient, not the other way around. The character traits we associate with good medicine — compassion, attentiveness, responsiveness — are about meeting people where they are. Telehealth is the structural expression of that virtue. It removes barriers between the physician's care and the patient's need.",),

    ("<b>\"How does the ethic of care apply?\"</b> — The ethic of care emphasizes maintaining relationships and attending to vulnerability. Telehealth strengthens care relationships by ensuring continuity — patients do not cancel appointments due to transportation barriers, work conflicts, or mobility limitations. A relationship that continues is stronger than one repeatedly interrupted by access barriers.",),
]

for q in ethics_qs:
    story.append(Paragraph(q[0], bullet_style))

# Category 2: Four Principles
story.append(Paragraph("2. Four Principles of Bioethics Questions", heading2_style))

principles_qs = [
    "<b>\"Does telehealth respect autonomy?\"</b> — Yes. Autonomy means the patient chooses how they receive care. Telehealth gives patients control over the time, place, and mode of their encounter. The hospital-centric model removes that choice — you come to the institution on its schedule, or you do not get care. Telehealth restores decision-making to the patient.",

    "<b>\"How does telehealth serve justice?\"</b> — Justice requires fair distribution of benefits and burdens. The current system distributes care based on geography — if you live near a hospital, you get access; if you do not, you travel 70+ miles. Telehealth redistributes access to rural, elderly, disabled, and low-income populations who bear the heaviest burden under the current model.",

    "<b>\"Could telehealth violate non-maleficence?\"</b> — This is the missed-diagnosis concern, and it is partially valid. Some conditions require hands-on examination. But the provider retains clinical judgment about when an in-person visit is necessary. Telehealth is not a replacement — it is triage. The patient connects first, and the provider determines the appropriate next step. Non-maleficence is preserved through provider discretion, not blanket restriction.",

    "<b>\"Does telehealth fulfill beneficence?\"</b> — Beneficence means acting in the patient's best interest. Equivalent outcomes at lower cost, with less travel burden and greater convenience, is objectively more beneficial. When something works as well, costs less, and the patient prefers it, restricting it is the opposite of beneficence.",
]

for q in principles_qs:
    story.append(Paragraph(q, bullet_style))

# Category 3: Module Content
story.append(Paragraph("3. Module Content Questions", heading2_style))

module_qs = [
    "<b>\"What about the digital divide and equity?\"</b> — The digital divide is real, and it is an argument for investing in broadband infrastructure — not for restricting telehealth. Disparities in internet access are a solvable problem. The physical barrier of geography is permanent. The ethical response is to expand telehealth and close the digital divide simultaneously, not hold one hostage to the other.",

    "<b>\"How do you address data privacy and HIPAA?\"</b> — HIPAA already applies to telehealth. Providers must use encrypted, compliant platforms. The privacy risk is in storage and transmission infrastructure, not in the mode of the visit. In-person visits use the same electronic health records. Restricting telehealth over privacy concerns while accepting that in-person visits use identical digital systems is an inconsistent standard.",

    "<b>\"How does the UnitedHealth / nH Predict case relate?\"</b> — That case showed what happens when institutional gatekeepers use algorithms to deny care for profit. Telehealth moves in the opposite direction — it connects patients directly to providers, bypassing the institutional middleman. The nH Predict case is an argument for telehealth, not against it: the more direct the patient-provider connection, the harder it is for algorithms to stand between patients and their care.",

    "<b>\"Can informed consent be properly obtained virtually?\"</b> — Yes. Informed consent requires that the patient understands the treatment, its risks, and alternatives. None of that requires physical co-presence. A video or phone conversation allows the same exchange of information. In fact, patients in their own home may feel less pressured and more comfortable asking questions than in a clinical setting.",

    "<b>\"Can cultural humility be practiced through a screen?\"</b> — Cultural humility is a reflective practice — acknowledging your own biases and being willing to learn from the patient. That disposition does not require a physical room. In fact, telehealth can enhance cultural humility: the provider sees the patient in their home environment and gains context they would never have in a sterile exam room.",
]

for q in module_qs:
    story.append(Paragraph(q, bullet_style))

doc.build(story)
print(f"PDF created: {output_path}")

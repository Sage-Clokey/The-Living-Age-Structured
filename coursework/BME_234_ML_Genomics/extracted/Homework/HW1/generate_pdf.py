from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black, red
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register DejaVu Sans (supports Unicode math symbols)
FONT_DIR = "/home/sage/.local/lib/python3.12/site-packages/matplotlib/mpl-data/fonts/ttf"
pdfmetrics.registerFont(TTFont('DejaVu', f'{FONT_DIR}/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVu-Bold', f'{FONT_DIR}/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('DejaVu-Oblique', f'{FONT_DIR}/DejaVuSans-Oblique.ttf'))
pdfmetrics.registerFont(TTFont('DejaVu-BoldOblique', f'{FONT_DIR}/DejaVuSans-BoldOblique.ttf'))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily('DejaVu', normal='DejaVu', bold='DejaVu-Bold',
                   italic='DejaVu-Oblique', boldItalic='DejaVu-BoldOblique')

PDF_FILE = "HW1_answers.pdf"
FONT = 'DejaVu'

doc = SimpleDocTemplate(PDF_FILE, pagesize=letter,
                        topMargin=0.75*inch, bottomMargin=0.75*inch,
                        leftMargin=0.75*inch, rightMargin=0.75*inch)

styles = getSampleStyleSheet()
title_style = ParagraphStyle('Title2', parent=styles['Title'], fontSize=16, spaceAfter=2, fontName=FONT)
subtitle_style = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=11,
                                alignment=TA_CENTER, spaceAfter=6, fontName=FONT)
heading_style = ParagraphStyle('H', parent=styles['Heading2'], fontSize=13,
                               spaceAfter=2, spaceBefore=8, fontName=FONT)
q_style = ParagraphStyle('Q', parent=styles['Normal'], fontSize=10,
                         spaceAfter=2, textColor=black, leading=13, fontName=FONT)
a_style = ParagraphStyle('A', parent=styles['Normal'], fontSize=10,
                         spaceAfter=6, textColor=red, leading=13, fontName=FONT)

story = []

# Title
story.append(Paragraph("AM234/BME234 Homework 1", title_style))
story.append(Paragraph("Due: Wednesday April 22, 2026 at 11:59 pm", subtitle_style))

# --- Problem 1 ---
story.append(Paragraph("1. (30 pt) For each of the below questions, write your answer and provide a brief (2-3 sentence) explanation.", heading_style))

story.append(Paragraph("<b>(a) (5 pt)</b> Consider an HMM defined over m states where each state emits one of k possible observations. How many parameters are needed to fully specify this model? (Assume that there are no begin or end states.)", q_style))
story.append(Paragraph("The number of parameters is m + m² + mk. The initial state distribution requires m parameters (one per state), the transition matrix requires m² parameters (from each of m states to each of m states), and the emission matrix requires mk parameters (each of m states can emit one of k observations).", a_style))

story.append(Paragraph("<b>(b) (5 pt)</b> True or False? Given a sequence X = x₁, . . . , x_L and a state path π = π₁, . . . , π_L, we can compute the joint probability of a sequence and a state path by P(X, π) = P(π₁)P(x₁)P(π₂ | π₁)P(x₂ | x₁) . . . P(π_L | π_{L−1})P(x_L | x_{L−1})", q_style))
story.append(Paragraph("False. The formula incorrectly conditions each observation on the previous observation, P(xᵢ | xᵢ₋₁), when it should condition each observation on its corresponding hidden state, P(xᵢ | πᵢ). In an HMM, observations are emitted from states, not generated from prior observations. The correct formula is: P(X, π) = P(π₁)P(x₁ | π₁) · ∏ P(πᵢ | πᵢ₋₁)P(xᵢ | πᵢ).", a_style))

story.append(Paragraph("<b>(c) (5 pt)</b> True or False? The following conditional independence statement holds in an HMM: (x_n ⊥⊥ x_{n−10}) | π_{n−2}. If the above notation is unclear, this statement reads that x_n and x_{n−10} are conditionally independent given π_{n−2}.", q_style))
story.append(Paragraph("False. Conditioning on π_{n−2} does not block all paths between x_n and x_{n−10}. Information can still flow through the unobserved hidden states π_{n−1} and π_n, since x_n depends on π_n and the state chain π_{n−2} → π_{n−1} → π_n remains unblocked. To make x_n conditionally independent of x_{n−10}, we would need to condition on a state that separates them in the graphical model, such as π_{n−1}.", a_style))

story.append(Paragraph("<b>(d) (5 pt)</b> True or False? The following conditional independence statement holds in an HMM: (π_n ⊥⊥ π_{n−10}) | x_{n−2}.", q_style))
story.append(Paragraph("False. Conditioning on x_{n−2} does not block the path between π_n and π_{n−10}. The hidden states form a chain π_{n−10} → ... → π_{n−1} → π_n, and this path runs entirely through hidden states, none of which are observed. Since x_{n−2} is a child of π_{n−2} rather than a node on the hidden state chain itself, observing it does not d-separate π_n from π_{n−10}.", a_style))

story.append(Paragraph("<b>(e) (10 pt)</b> Let X be a sequence of length L where xᵢ denotes the state at position i. Assume that each xᵢ is drawn from the finite alphabet X and that none of these xᵢ corresponds to an end state. The probability of X under a Markov chain is given by the formula P(X) = P(x₁, . . . , x_L) = P(x₁) ∏ P(xₙ | xₙ₋₁). Prove that the probability of observing all sequences of length L sums to 1. In other words, Σ_{x₁} Σ_{x₂} . . . Σ_{x_L} P(x₁, x₂, . . . , x_L) = 1. This result shows that a Markov chain defines a valid probability measure over all sequences of length L.", q_style))
story.append(Paragraph(
    "We begin with: S = Σ_{x₁} Σ_{x₂} ... Σ_{x_L} P(x₁) ∏ P(xₙ | xₙ₋₁).<br/><br/>"
    "We evaluate the sums from the inside out, starting with the innermost sum over x_L. "
    "The only term that depends on x_L is P(x_L | x_{L−1}), so: Σ_{x_L} P(x_L | x_{L−1}) = 1, "
    "since P(x_L | x_{L−1}) is a valid conditional distribution over all possible values of x_L. "
    "This eliminates the x_L sum and the P(x_L | x_{L−1}) term, leaving: "
    "S = Σ_{x₁} Σ_{x₂} ... Σ_{x_{L−1}} P(x₁) ∏ P(xₙ | xₙ₋₁).<br/><br/>"
    "We repeat this process. At each step, the innermost sum is over x_j, and the only "
    "term depending on x_j is P(x_j | x_{j−1}), which sums to 1. Continuing in this manner, "
    "we peel off each sum from x_L down to x₂, each time obtaining a factor of 1, until "
    "we are left with: S = Σ_{x₁} P(x₁) = 1, "
    "since P(x₁) is a valid probability distribution over all possible starting states. "
    "Therefore, the Markov chain defines a valid probability measure over all sequences of length L. QED", a_style))

# --- Problem 2 ---
story.append(Paragraph("2. (30 pt) Suppose we are interested in discriminating promoter sequences from those that are not, which hereafter we refer to as negative sequences. To answer this question, we could learn two Markov chain models on promoter sequences and negative sequences. States in these Markov chain models are not individual nucleotides. Instead, they are overlapping k-mers (a k-mer is a substring of length k). For example, suppose we were given a sequence starting with \"ACTGA...\" and k equaled 3. Then, the first few states would be [ACT, CTG, TGA, . . .]. Despite this increase in the dimensionality of each state, we can fit a Markov chain model the same way we did in class. Given these two Markov models, we could then classify a novel sequence X as being a promoter sequence if log P(X | promoter) / P(X | negative) &gt; 0. In this problem, we ask you to implement these Markov models and investigate the best choice of k.", heading_style))

story.append(Paragraph("<b>(a) (15 pt)</b> Implement all functions in problem_2.py.", q_style))
story.append(Paragraph("See problem_2.py.", a_style))

story.append(Paragraph("<b>(b) (3 pt)</b> Report the accuracy on the train set and the validation set when k = 1.", q_style))
story.append(Paragraph("When k = 1, the train accuracy is 0.8798 and the validation accuracy is 0.8834.", a_style))

story.append(Paragraph("<b>(c) (4 pt)</b> Plot the validation accuracy for all values of k from 1 to 5, inclusive.", q_style))
img_2c = Image("problem_2c_val_accuracy.png", width=5.5*inch, height=3.5*inch)
story.append(img_2c)

story.append(Paragraph("<b>(d) (4 pt)</b> What trends do you observe in your above plot? Why do you think those trends occur?", q_style))
story.append(Paragraph("There is a large jump in validation accuracy from k=1 (0.8834) to k=2 (0.9856), followed by only marginal gains from k=3 through k=5. This suggests that most of the discriminative signal between promoter and negative sequences lies in dinucleotide dependencies — the relationship between adjacent bases — which k=1 cannot capture since it only models single nucleotide frequencies. Beyond k=2, the model captures longer-range patterns but with diminishing returns, as the most important sequence context is already accounted for.", a_style))

story.append(Paragraph("<b>(e) (4 pt)</b> List two problems of choosing a very large value of k (e.g. k &gt; 20).", q_style))
story.append(Paragraph(
    "1. Overfitting: A large k gives the model enough capacity to memorize the training data, "
    "but it will generalize poorly to new sequences since the learned patterns are too specific "
    "to the training set.<br/>"
    "2. Data sparsity: The number of possible k-mers grows as 4^k, so for k=20 there are over "
    "10¹² possible states. Most k-mers will never appear in the training data, leaving the "
    "vast majority of transition probabilities unestimated or unreliable.", a_style))

# --- Problem 3 ---
story.append(Paragraph("3. (20 pt) In this problem, you will explore the Variant Call Format (VCF)—a text file format used in computational biology for storing gene sequence variations. The VCF specification can be found at https://samtools.github.io/hts-specs/VCFv4.1.pdf. Answer the following questions about the chr21_filtered.vcf.gz file. Please submit code for all subparts in a file named problem_3.py.", heading_style))

story.append(Paragraph("<b>(a) (4 pt)</b> How many single-nucleotide polymorphisms (SNPs) are listed in this file? (Note that some VCF rows contain multiple alt alleles. Therefore, because a variant is a 4-tuple of (chrom, pos, ref, alt), one VCF row may contain multiple variants.)", q_style))
story.append(Paragraph("190,994 SNPs. A SNP is defined as a variant where both the REF and ALT alleles are single nucleotides (A, C, G, or T). Multi-allelic rows with comma-separated ALTs were counted per qualifying allele.", a_style))

story.append(Paragraph("<b>(b) (4 pt)</b> Plot a histogram of variant allele frequencies. How many variants have an allele frequency less than 1%?", q_style))
story.append(Paragraph("199,403 allele frequency entries total. Of these, 164,785 (82.6%) have an allele frequency below 1%, indicating the majority of variants are rare.", a_style))
img_hist = Image("problem_3b_hist_20260422_151844.png", width=6*inch, height=3*inch)
story.append(img_hist)
img_bee = Image("problem_3b_20260422_151844.png", width=6*inch, height=3.8*inch)
story.append(img_bee)

story.append(Paragraph("<b>(c) (4 pt)</b> How many samples does this VCF file contain genotype data for? How many distinct variants does the average individual contain?", q_style))
story.append(Paragraph("2,504 samples (consistent with the 1000 Genomes Project phase 3 cohort). On average, each individual carries 11,636.40 distinct variants on chromosome 21, counted by checking whether any non-reference allele appears in the individual's genotype.", a_style))

story.append(Paragraph("<b>(d) (4 pt)</b> What is dbSNP? How many variants in this VCF file have a dbSNP id?", q_style))
story.append(Paragraph("dbSNP (Database of Single Nucleotide Polymorphisms) is a public database maintained by NCBI that catalogs known short genetic variations, including SNPs, short insertions, deletions, and other small variants. Each entry is assigned a unique \"rs\" identifier (e.g. rs12345), allowing researchers to reference and look up whether a variant has been previously observed. In this filtered VCF, 0 variants have a dbSNP ID — the ID column contains only \".\", indicating the file was not annotated against the dbSNP database.", a_style))

story.append(Paragraph("<b>(e) (4 pt)</b> What is a Phred-quality score? Look this up. How accurate is a variant call if it has a Phred score of 45?", q_style))
story.append(Paragraph("A Phred quality score quantifies the probability that a base call or variant call is incorrect, defined as Q = −10 · log₁₀(P_error). For a Phred score of 45: P_error = 10^(−45/10) = 10^(−4.5) ≈ 0.0000316. This corresponds to an accuracy of 99.997%, or roughly a 1 in 31,623 chance of error.", a_style))

doc.build(story)
print(f"PDF saved to {PDF_FILE}")

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Preformatted
from reportlab.lib.enums import TA_LEFT

B0 = "β<sub rise='-2' size='8'>0</sub>"
B1 = "β<sub rise='-2' size='8'>1</sub>"

def build_pdf():
	doc = SimpleDocTemplate("HW2_answers.pdf", pagesize=letter,
		leftMargin=0.75*inch, rightMargin=0.75*inch,
		topMargin=0.75*inch, bottomMargin=0.75*inch)

	styles = getSampleStyleSheet()
	title_style = styles['Title']
	h1 = styles['Heading1']
	h2 = styles['Heading2']
	body = styles['BodyText']
	body.spaceAfter = 6
	body.leading = 14

	math_style = ParagraphStyle('Math', parent=body, fontName='Helvetica', fontSize=10,
		leading=14, spaceAfter=6, leftIndent=20, textColor='#333333')
	indent_style = ParagraphStyle('Indent', parent=body, leftIndent=20, spaceAfter=6)

	story = []
	sp = Spacer(1, 12)

	# Title
	story.append(Paragraph("BME 234 — Homework 2", title_style))
	story.append(Paragraph("Sage Clokey", styles['Heading3']))
	story.append(sp)

	# ===== PROBLEM 1 =====
	story.append(Paragraph("Problem 1: Logistic Regression Theory", h1))

	# 1a
	story.append(Paragraph("(a) Prove equations (1) and (2) are equivalent.", h2))
	story.append(Paragraph("Start with equation (1):", body))
	story.append(Paragraph(f"f(x) = exp({B0} + {B1}x) / [1 + exp({B0} + {B1}x)]", math_style))
	story.append(Paragraph(f"Divide both numerator and denominator by exp({B0} + {B1}x):", body))
	story.append(Paragraph(f"= 1 / [1/exp({B0} + {B1}x) + 1]", math_style))
	story.append(Paragraph(f"= 1 / [1 + exp(−{B0} − {B1}x)]", math_style))
	story.append(Paragraph("This is equation (2). QED.", body))
	story.append(sp)

	# 1b
	story.append(Paragraph("(b) Prove that g′(z) = g(z)[1 − g(z)].", h2))
	story.append(Paragraph("g(z) = 1 / (1 + e<super>−z</super>)", body))
	story.append(Paragraph("Using the quotient rule with u = 1, v = 1 + e<super>−z</super>:", body))
	story.append(Paragraph("g′(z) = [0 · (1 + e<super>−z</super>) − 1 · (−e<super>−z</super>)] / (1 + e<super>−z</super>)<super>2</super>", math_style))
	story.append(Paragraph("= e<super>−z</super> / (1 + e<super>−z</super>)<super>2</super>", math_style))
	story.append(Paragraph("Factor:", body))
	story.append(Paragraph("= [1 / (1 + e<super>−z</super>)] · [e<super>−z</super> / (1 + e<super>−z</super>)]", math_style))
	story.append(Paragraph("= g(z) · [(1 + e<super>−z</super> − 1) / (1 + e<super>−z</super>)]", math_style))
	story.append(Paragraph("= g(z) · [1 − g(z)]&nbsp;&nbsp;&nbsp;&nbsp;QED.", math_style))
	story.append(sp)

	# 1c
	story.append(Paragraph("(c) Rewrite the logistic regression model using g.", h2))
	story.append(Paragraph(f"Let z = {B0} + {B1}x. Then:", body))
	story.append(Paragraph(f"f(x; {B0}, {B1}) = g({B0} + {B1}x)", math_style))
	story.append(sp)

	# 1d
	story.append(Paragraph("(d) Derive the log-likelihood.", h2))
	story.append(Paragraph(f"Since y<sub>i</sub> ∈ {{0, 1}}, the probability of observing y<sub>i</sub> given x<sub>i</sub> is:", body))
	story.append(Paragraph(
		f"P(y<sub>i</sub> | x<sub>i</sub>) = g({B0} + {B1}x<sub>i</sub>)<super>y<sub>i</sub></super>"
		f" · [1 − g({B0} + {B1}x<sub>i</sub>)]<super>(1 − y<sub>i</sub>)</super>", math_style))
	story.append(Paragraph(
		"This works because when y<sub>i</sub> = 1 it gives g(...), and when y<sub>i</sub> = 0 it gives 1 − g(...).", body))
	story.append(Paragraph("Since the data are i.i.d., the likelihood is the product over all observations:", body))
	story.append(Paragraph(
		f"L({B0}, {B1}) = ∏<sub>i</sub> g({B0} + {B1}x<sub>i</sub>)<super>y<sub>i</sub></super>"
		f" · [1 − g({B0} + {B1}x<sub>i</sub>)]<super>(1 − y<sub>i</sub>)</super>", math_style))
	story.append(Paragraph("Taking the log converts the product to a sum:", body))
	story.append(Paragraph(
		f"log L = Σ<sub>i</sub> [ y<sub>i</sub> · log(g({B0} + {B1}x<sub>i</sub>))"
		f" + (1 − y<sub>i</sub>) · log(1 − g({B0} + {B1}x<sub>i</sub>)) ]", math_style))
	story.append(Paragraph("QED.", body))
	story.append(sp)

	# 1e
	story.append(Paragraph("(e) Why maximize log-likelihood instead of likelihood?", h2))
	story.append(Paragraph(
		f"The logarithm is a monotonically increasing function, so any ({B0}, {B1}) that maximizes "
		"log L also maximizes L. The log transformation converts products into sums, making "
		"differentiation easier and computation more numerically stable (avoiding underflow from "
		"multiplying many small probabilities).", body))
	story.append(sp)

	# 1f
	story.append(Paragraph(f"(f) Compute ∂log L/∂{B0} and ∂log L/∂{B1}.", h2))
	story.append(Paragraph(f"Let z<sub>i</sub> = {B0} + {B1}x<sub>i</sub>. Using the chain rule and g′(z) = g(z)[1 − g(z)]:", body))
	story.append(Paragraph(
		f"∂log L/∂{B0} = Σ<sub>i</sub> [ y<sub>i</sub> · g′(z<sub>i</sub>) / g(z<sub>i</sub>)"
		f" + (1 − y<sub>i</sub>) · (−g′(z<sub>i</sub>)) / (1 − g(z<sub>i</sub>)) ] · 1", math_style))
	story.append(Paragraph(
		"Substituting g′(z<sub>i</sub>) = g(z<sub>i</sub>)(1 − g(z<sub>i</sub>)):", body))
	story.append(Paragraph(
		"= Σ<sub>i</sub> [ y<sub>i</sub>(1 − g(z<sub>i</sub>)) − (1 − y<sub>i</sub>)g(z<sub>i</sub>) ]", math_style))
	story.append(Paragraph(
		"= Σ<sub>i</sub> (y<sub>i</sub> − g(z<sub>i</sub>))", math_style))
	story.append(sp)
	story.append(Paragraph(f"For {B1}, ∂z<sub>i</sub>/∂{B1} = x<sub>i</sub>, so:", body))
	story.append(Paragraph(
		f"∂log L/∂{B1} = Σ<sub>i</sub> (y<sub>i</sub> − g(z<sub>i</sub>)) · x<sub>i</sub>", math_style))
	story.append(sp)

	# 1g
	story.append(Paragraph("(g) Gradient ascent update rules.", h2))
	story.append(Paragraph("With learning rate α, repeat until convergence:", body))
	story.append(Paragraph(
		f"{B0} ← {B0} + α · Σ<sub>i</sub> (y<sub>i</sub> − g({B0} + {B1}x<sub>i</sub>))", math_style))
	story.append(Paragraph(
		f"{B1} ← {B1} + α · Σ<sub>i</sub> (y<sub>i</sub> − g({B0} + {B1}x<sub>i</sub>)) · x<sub>i</sub>", math_style))
	story.append(sp)

	# 1h
	story.append(Paragraph("(h) Why might gradient ascent not converge with perfectly separable data?", h2))
	story.append(Paragraph(
		f"If the data is perfectly linearly separable, the logistic regression can achieve zero loss "
		f"by making the sigmoid arbitrarily steep — i.e., pushing {B1} → ∞. The decision boundary "
		"becomes a step function. The gradients never reach zero because the log-likelihood keeps "
		"increasing (albeit more and more slowly) as the parameters grow. The parameters diverge "
		"to infinity, so gradient ascent never converges to finite, stable values.", body))
	story.append(sp)

	# 1i
	story.append(Paragraph("(i) Fix for the convergence issue.", h2))
	story.append(Paragraph(
		"Add L2 regularization (ridge penalty). Instead of maximizing log L, maximize:", body))
	story.append(Paragraph(
		f"log L − λ({B0}<super>2</super> + {B1}<super>2</super>)", math_style))
	story.append(Paragraph(
		"The regularization term penalizes large parameter values, creating a counterforce that "
		"prevents the parameters from diverging to infinity. This ensures a finite optimum exists "
		"even when the data is perfectly separable. The hyperparameter λ controls the strength of "
		"the penalty.", body))

	story.append(PageBreak())

	# ===== PROBLEM 2 =====
	story.append(Paragraph("Problem 2: Multiple Hypothesis Testing", h1))

	code_style = ParagraphStyle('Code', fontName='Courier', fontSize=8,
		leading=11, spaceAfter=6, leftIndent=10, rightIndent=10,
		backColor='#f5f5f5', borderPadding=6)

	# 2a
	story.append(Paragraph("(a) Bonferroni Correction", h2))
	bonf_code = """def apply_bonferroni_correction(pvalues, alpha):
    threshold = alpha / len(pvalues)
    return pvalues <= threshold"""
	story.append(Preformatted(bonf_code, code_style))
	story.append(sp)

	# 2b
	story.append(Paragraph("(b) Benjamini-Hochberg Correction", h2))
	bh_code = """def apply_benjamini_hochberg_correction(pvalues, alpha):
    m = len(pvalues)
    sorted_indices = np.argsort(pvalues)
    sorted_pvals = pvalues[sorted_indices]

    thresholds = np.arange(1, m + 1) * alpha / m
    passing = sorted_pvals <= thresholds

    if not np.any(passing):
        return np.zeros(m, dtype=bool)

    max_k = np.max(np.where(passing))

    rejects = np.zeros(m, dtype=bool)
    rejects[sorted_indices[:max_k + 1]] = True
    return rejects"""
	story.append(Preformatted(bh_code, code_style))

	story.append(PageBreak())

	# ===== PROBLEM 3 =====
	story.append(Paragraph("Problem 3: GWAS", h1))

	story.append(Paragraph("(a)–(b) GWAS and Manhattan Plot (No Covariates)", h2))
	story.append(Paragraph(
		"See problem_3.py for the full implementation. The Manhattan plot below shows −log<sub>10</sub>(p) "
		"for each SNP, with Bonferroni (red) and Benjamini-Hochberg (orange) threshold lines.", body))
	story.append(sp)
	story.append(Image("manhattan_no_covariates.png", width=6.5*inch, height=2.8*inch))
	story.append(sp)

	# 3c
	story.append(Paragraph("(c) Number of significant SNPs.", h2))
	story.append(Paragraph("<b>Without covariates:</b>", body))
	story.append(Paragraph("• Bonferroni correction: 4,008 SNPs", indent_style))
	story.append(Paragraph("• Benjamini-Hochberg correction: 24,389 SNPs", indent_style))
	story.append(sp)

	# 3d
	story.append(Paragraph("(d) Why so many significant SNPs when only 5 are causal?", h2))
	story.append(Paragraph(
		"<b>1. Linkage disequilibrium (LD):</b> SNPs that are physically close to causal variants "
		"on the chromosome tend to be inherited together. These nearby SNPs are correlated with "
		"the causal SNPs, so they also show statistically significant associations with the "
		"phenotype. This creates clusters of significant hits around each causal locus.", body))
	story.append(Paragraph(
		"<b>2. Population structure:</b> The 1000 Genomes dataset contains individuals from diverse "
		"ancestral populations. Allele frequencies vary systematically between populations. If "
		"the phenotype prevalence also differs between populations, then any SNP whose frequency "
		"differs between populations will appear associated with the phenotype — even though the "
		"association is confounded by ancestry, not causality. This inflates the number of false "
		"positives across the entire chromosome.", body))
	story.append(sp)

	# 3e
	story.append(Paragraph("(e) GWAS with Top 3 PCs as Covariates", h2))
	story.append(Paragraph(
		"The dosage matrix was standardized (mean 0, variance 1 per column) before PCA. "
		"The top 3 principal components were included as covariates in the logistic regression.", body))
	story.append(sp)
	story.append(Image("manhattan_with_pca.png", width=6.5*inch, height=2.8*inch))
	story.append(sp)
	story.append(Paragraph("<b>With PCA covariates:</b>", body))
	story.append(Paragraph("• Bonferroni correction: 258 SNPs", indent_style))
	story.append(Paragraph("• Benjamini-Hochberg correction: 520 SNPs", indent_style))
	story.append(sp)

	# 3f
	story.append(Paragraph("(f) Why does including PCs reduce significant SNPs?", h2))
	story.append(Paragraph(
		"The top principal components of the genotype matrix capture the major axes of genetic "
		"variation between individuals, which correspond to population structure (ancestry). By "
		"including them as covariates in the logistic regression, the model controls for ancestry "
		"differences. This removes spurious associations that arose because allele frequencies and "
		"phenotype prevalence both varied by population. After adjusting for population structure, "
		"only SNPs with true causal effects (and their LD neighbors) remain significant, "
		"dramatically reducing the number of hits and making it easier to identify the actual "
		"causal variants.", body))

	doc.build(story)
	print("Saved HW2_answers.pdf")

if __name__ == '__main__':
	build_pdf()

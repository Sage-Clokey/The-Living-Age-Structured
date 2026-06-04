import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from problem_2 import apply_bonferroni_correction, apply_benjamini_hochberg_correction

PHENOTYPE_DATA = "phenotypes.npz"
VCF_FILE = "chr22_subsampled_snps.vcf"

def get_phenotype_data():
	data = np.load(PHENOTYPE_DATA)
	individuals = data["probands"]
	phenotypes = data["phenotypes"]
	return individuals, phenotypes

def parse_vcf(vcf_file, pheno_individuals):
	"""Parse VCF file and return dosage matrix, positions, and aligned phenotype indices."""
	positions = []
	genotypes = []

	with open(vcf_file, 'r') as f:
		for line in f:
			if line.startswith('##'):
				continue
			if line.startswith('#CHROM'):
				header = line.strip().split('\t')
				sample_ids = header[9:]
				# Map phenotype individuals to VCF column order
				pheno_to_idx = {ind: i for i, ind in enumerate(pheno_individuals)}
				sample_order = [pheno_to_idx[s] for s in sample_ids]
				continue

			fields = line.strip().split('\t')
			positions.append(int(fields[1]))
			gt_fields = fields[9:]
			dosage = []
			for gt in gt_fields:
				alleles = gt.replace('|', '/').split('/')
				dosage.append(int(alleles[0]) + int(alleles[1]))
			genotypes.append(dosage)

	dosage_matrix = np.array(genotypes, dtype=np.int8).T  # individuals x SNPs
	# Reorder rows to match phenotype individual order
	inverse_order = np.argsort(sample_order)
	dosage_matrix = dosage_matrix[inverse_order]

	return dosage_matrix, np.array(positions)

def run_gwas(X, y, covariate_matrix=None):
	"""Run logistic regression GWAS. Returns array of p-values."""
	n_snps = X.shape[1]
	pvalues = np.ones(n_snps)

	for j in range(n_snps):
		dosage = X[:, j]
		# Skip SNPs with no variation
		if np.all(dosage == dosage[0]):
			continue
		try:
			if covariate_matrix is not None:
				exog = np.column_stack([dosage, covariate_matrix])
			else:
				exog = dosage
			exog = sm.add_constant(exog)
			model = sm.Logit(y, exog)
			result = model.fit(disp=0, maxiter=100)
			# p-value for beta_1 (the SNP coefficient, index 1)
			pvalues[j] = result.pvalues[1]
		except Exception:
			pvalues[j] = 1.0

	return pvalues

def manhattan_plot(positions, pvalues, bonf_rejects, bh_rejects, title, filename):
	"""Draw Manhattan plot with correction threshold lines."""
	neg_log_p = -np.log10(pvalues)
	m = len(pvalues)

	# Bonferroni threshold
	bonf_threshold = -np.log10(0.05 / m)

	# BH threshold: largest p-value that was rejected
	if np.any(bh_rejects):
		bh_pval_cutoff = np.max(pvalues[bh_rejects])
		bh_threshold = -np.log10(bh_pval_cutoff)
	else:
		bh_threshold = None

	plt.figure(figsize=(14, 6))
	plt.scatter(positions, neg_log_p, s=2, c='steelblue', alpha=0.5)
	plt.axhline(y=bonf_threshold, color='red', linestyle='--', label=f'Bonferroni (FWER=0.05)')
	if bh_threshold is not None:
		plt.axhline(y=bh_threshold, color='orange', linestyle='--', label=f'Benjamini-Hochberg (FDR=0.05)')
	plt.xlabel('Position on Chromosome 22')
	plt.ylabel('$-\\log_{10}(p)$')
	plt.title(title)
	plt.legend()
	plt.tight_layout()
	plt.savefig(filename, dpi=150)
	plt.close()
	print(f"Saved {filename}")

def main():
	individuals, phenotypes = get_phenotype_data()

	print("Parsing VCF...")
	X, positions = parse_vcf(VCF_FILE, individuals)
	y = phenotypes
	print(f"Dosage matrix: {X.shape[0]} individuals x {X.shape[1]} SNPs")

	# --- Part (a): GWAS without covariates ---
	print("\nRunning GWAS (no covariates)...")
	pvalues = run_gwas(X, y)

	# --- Part (b)/(c): Corrections and Manhattan plot ---
	bonf_rejects = apply_bonferroni_correction(pvalues, 0.05)
	bh_rejects = apply_benjamini_hochberg_correction(pvalues, 0.05)

	print(f"\n--- Without covariates ---")
	print(f"Bonferroni significant SNPs: {np.sum(bonf_rejects)}")
	print(f"Benjamini-Hochberg significant SNPs: {np.sum(bh_rejects)}")

	manhattan_plot(positions, pvalues, bonf_rejects, bh_rejects,
		'Manhattan Plot (No Covariates)', 'manhattan_no_covariates.png')

	# --- Part (e): GWAS with top 3 PCs as covariates ---
	print("\nStandardizing dosage matrix and running PCA...")
	scaler = StandardScaler()
	X_std = scaler.fit_transform(X.astype(np.float64))
	pca = PCA(n_components=3)
	pcs = pca.fit_transform(X_std)

	print("Running GWAS (with top 3 PCs)...")
	pvalues_pca = run_gwas(X, y, covariate_matrix=pcs)

	bonf_rejects_pca = apply_bonferroni_correction(pvalues_pca, 0.05)
	bh_rejects_pca = apply_benjamini_hochberg_correction(pvalues_pca, 0.05)

	print(f"\n--- With PCA covariates ---")
	print(f"Bonferroni significant SNPs: {np.sum(bonf_rejects_pca)}")
	print(f"Benjamini-Hochberg significant SNPs: {np.sum(bh_rejects_pca)}")

	manhattan_plot(positions, pvalues_pca, bonf_rejects_pca, bh_rejects_pca,
		'Manhattan Plot (With Top 3 PCs)', 'manhattan_with_pca.png')

if __name__ == '__main__':
	main()

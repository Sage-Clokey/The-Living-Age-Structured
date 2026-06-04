import numpy as np

def apply_bonferroni_correction(pvalues, alpha):
	'''
	Args:
		pvalues: numpy array of p-values
		alpha: desired familywise error rate (FWER)

	Returns:
		rejects: a numpy array of booleans indicating whether the null hypothesis should be rejected
				 at the given alpha
	'''
	threshold = alpha / len(pvalues)
	return pvalues <= threshold

def apply_benjamini_hochberg_correction(pvalues, alpha):
	'''
	Args:
		pvalues: numpy array of independent p-values
		alpha: desired false discovery rate (FDR)

	Returns:
		rejects: a numpy array of booleans indicating whether the null hypothesis should be rejected
				 at the given alpha
	'''
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
	return rejects

def main():
	pass

if __name__ == '__main__':
	main()

import itertools
import numpy as np
import matplotlib.pyplot as plt

TRAIN_DATA = "problem_2_train_data.txt"
VAL_DATA = "problem_2_val_data.txt"

def load_data(input_path):
	# Loads promoter and negative sequences from the input_path.
	# DO NOT modify this function.

	promoter_sequences, negative_sequences = [], []
	with open(input_path) as f:
		for line in f:
			seq, clazz = line.strip().split()
			if clazz == "1":
				promoter_sequences.append(seq)
			elif clazz == "0":
				negative_sequences.append(seq)
			else:
				raise Exception("All class values should be either 0 or 1.")

	return promoter_sequences, negative_sequences

def train_markov_model(sequences, k):
	# Fits a Markov model where each state is a substring of size k.
	# These states are overlapping. So, if a sequence started with "ACTGA"
	# with k = 3, the first few states would be ["ACT", "CTG", "TGA", ...].
	# This Markov model should have neither a start state (assume all states
	# are equally likely at the beginning of the sentence) nor an end state.
	#
	# returns: 
	#	- states: an ordered list of size 4^k of all possible kmers in the Markov model
	# 			  (the specific order of states does not matter)
	#	- transition_matrix: a probability matrix (2D numpy array) with size 4^k by 4^k such that
	# 	                     transition_matrix[row][col] = P(pi_{i + 1} = state[col] | pi_{i} = state[row])
	#							* in the above notation, pi_{i} denotes the ith state in the sequence
	#

	# Generate all possible k-mers
	nucleotides = ['A', 'C', 'G', 'T']
	states = [''.join(combo) for combo in itertools.product(nucleotides, repeat=k)]
	state_to_idx = {s: i for i, s in enumerate(states)}

	num_states = len(states)
	counts = np.zeros((num_states, num_states))

	# Count transitions across all sequences
	for seq in sequences:
		kmers = [seq[i:i+k] for i in range(len(seq) - k + 1)]
		for i in range(len(kmers) - 1):
			curr = kmers[i]
			nxt = kmers[i + 1]
			if curr in state_to_idx and nxt in state_to_idx:
				counts[state_to_idx[curr]][state_to_idx[nxt]] += 1

	# Normalize rows to get probabilities (add pseudocount to avoid zero probs)
	row_sums = counts.sum(axis=1, keepdims=True)
	# Add a small pseudocount to avoid log(0)
	counts += 1e-10
	row_sums = counts.sum(axis=1, keepdims=True)
	transition_matrix = counts / row_sums

	return states, transition_matrix

def get_log_odds_ratio(seq, states, k, promoter_transition_matrix, negative_transition_matrix):
	# returns: log { P(sequence | promoter sequence model) / P(sequence | negative sequence model) }
	#
	# Assume that all first states are equally likely. That is, P(pi_{0} = state) = 1 / 4^k for all states

	state_to_idx = {s: i for i, s in enumerate(states)}
	kmers = [seq[i:i+k] for i in range(len(seq) - k + 1)]

	# Initial state probabilities cancel out in the log ratio since they're uniform
	log_ratio = 0.0
	for i in range(len(kmers) - 1):
		curr_idx = state_to_idx[kmers[i]]
		nxt_idx = state_to_idx[kmers[i + 1]]
		log_ratio += np.log(promoter_transition_matrix[curr_idx][nxt_idx])
		log_ratio -= np.log(negative_transition_matrix[curr_idx][nxt_idx])

	return log_ratio

def get_accuracy(promoter_sequences, negative_sequences, states, k,
				 promoter_transition_matrix, negative_transition_matrix):
	# Determine our model's accuracy on the given sequences.
	# Per our model, we classify a sequence as coming from a promoter iff it has a log odds ratio > 0.

	correct = 0
	total = 0

	for seq in promoter_sequences:
		log_ratio = get_log_odds_ratio(seq, states, k, promoter_transition_matrix, negative_transition_matrix)
		if log_ratio > 0:
			correct += 1
		total += 1

	for seq in negative_sequences:
		log_ratio = get_log_odds_ratio(seq, states, k, promoter_transition_matrix, negative_transition_matrix)
		if log_ratio <= 0:
			correct += 1
		total += 1

	return correct / total

def main():
	train_promoter_sequences, train_negative_sequences = load_data(TRAIN_DATA)
	val_promoter_sequences, val_negative_sequences = load_data(VAL_DATA)

	ks = list(range(1, 6))
	val_accuracies = []

	for k in ks:
		states, promoter_transition_matrix = train_markov_model(train_promoter_sequences, k)
		_, negative_transition_matrix = train_markov_model(train_negative_sequences, k)

		train_accuracy = get_accuracy(train_promoter_sequences, train_negative_sequences, states, k,
				promoter_transition_matrix, negative_transition_matrix)
		val_accuracy = get_accuracy(val_promoter_sequences, val_negative_sequences, states, k,
				promoter_transition_matrix, negative_transition_matrix)
		val_accuracies.append(val_accuracy)

		print("k = {}, train accuracy = {}, val accuracy = {}".format(k, train_accuracy, val_accuracy))

	plt.figure(figsize=(8, 5))
	plt.plot(ks, val_accuracies, 'o-', color='steelblue', markersize=8)
	for k, acc in zip(ks, val_accuracies):
		plt.annotate(f'{acc:.4f}', (k, acc), textcoords='offset points', xytext=(0, 10), ha='center')
	plt.xlabel('k (k-mer size)')
	plt.ylabel('Validation Accuracy')
	plt.title('Validation Accuracy vs. k-mer Size')
	plt.xticks(ks)
	plt.ylim(0.85, 1.0)
	plt.grid(True, alpha=0.3)
	plt.savefig('problem_2c_val_accuracy.png', dpi=150, bbox_inches='tight')
	plt.close()
	print("\nPlot saved to problem_2c_val_accuracy.png")



if __name__ == '__main__':
	main()
import gzip
import math
import matplotlib.pyplot as plt
from collections import defaultdict
from datetime import datetime

VCF_FILE = "chr21_filtered.vcf.gz"


def stream_vcf(filepath):
    """Stream VCF rows one at a time, yielding (header, row_iterator)."""
    open_func = gzip.open if filepath.endswith('.gz') else open
    f = open_func(filepath, 'rt')
    header = None
    for line in f:
        line = line.strip()
        if line.startswith('##'):
            continue
        elif line.startswith('#CHROM'):
            header = line.lstrip('#').split('\t')
            break

    def row_iter():
        for line in f:
            yield line.strip().split('\t')
        f.close()

    return header, row_iter()


def collect_all(filepath):
    """Single streaming pass over the VCF, collecting results for parts a–d."""
    header, rows = stream_vcf(filepath)
    num_samples = len(header) - 9

    # Part A
    snp_count = 0
    # Part B
    afs = []
    # Part C
    variant_counts = [0] * num_samples
    # Part D
    dbsnp_count = 0

    for row in rows:
        ref = row[3]
        alts_str = row[4]
        alts = alts_str.split(',')

        # Part A: count SNPs
        for alt in alts:
            if len(ref) == 1 and len(alt) == 1 and ref in 'ACGT' and alt in 'ACGT':
                snp_count += 1

        # Part B: extract allele frequencies
        info = row[7]
        for field in info.split(';'):
            if field.startswith('AF='):
                for v in field[3:].split(','):
                    try:
                        afs.append(float(v))
                    except ValueError:
                        pass

        # Part C: count variants per sample
        for s_idx in range(num_samples):
            gt = row[9 + s_idx].split(':')[0]
            alleles = gt.replace('|', '/').split('/')
            for a in alleles:
                if a not in ('.', '0'):
                    variant_counts[s_idx] += 1
                    break

        # Part D: check for dbSNP ID
        for vid in row[2].split(';'):
            if vid.startswith('rs'):
                dbsnp_count += 1
                break

    return header, num_samples, snp_count, afs, variant_counts, dbsnp_count


def print_part_a(snp_count):
    print(f"(a) Number of SNPs: {snp_count}")


def print_part_b(afs):
    low_af_count = sum(1 for af in afs if af < 0.01)

    # Filter out AF <= 0 (can't take log of zero)
    plot_afs = [af for af in afs if af > 0]
    log_afs = [math.log10(af) for af in plot_afs]
    x_min, x_max = min(log_afs), max(log_afs)
    x_range = x_max - x_min if x_max > x_min else 1.0

    # Beeswarm: bin by AF (log-space), normalize each bin to same width
    diameter = x_range / 400
    bin_assignments = []
    bin_totals = defaultdict(int)

    # First pass: assign bins and count totals
    for i, lx in enumerate(log_afs):
        bx = int((lx - x_min) / diameter) if diameter > 0 else 0
        bin_assignments.append(bx)
        bin_totals[bx] += 1

    # Second pass: stack linearly within each bin
    bin_count = defaultdict(int)
    x_stack = [0.0] * len(plot_afs)
    for i, bx in enumerate(bin_assignments):
        x_stack[i] = bin_count[bx] * diameter
        bin_count[bx] += 1

    # Color by bin density (points per bin) as a heatmap
    colors = [bin_totals[bx] for bx in bin_assignments]

    # Split into above and below AF = 1%
    above_idx = [i for i, af in enumerate(plot_afs) if af >= 0.01]
    below_idx = [i for i, af in enumerate(plot_afs) if af < 0.01]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 10))

    # Above AF = 1%
    sc1 = ax1.scatter([x_stack[i] for i in above_idx],
                      [plot_afs[i] for i in above_idx],
                      s=2, alpha=0.4,
                      c=[colors[i] for i in above_idx],
                      cmap='inferno', edgecolors='none')
    ax1.set_yscale('log')
    ax1.set_ylabel('Allele Frequency (log scale)')
    ax1.set_xticks([])
    ax1.set_xlabel('Variant count per bin (normalized)')
    ax1.set_title(f'AF >= 1% ({len(above_idx):,} variants)')
    plt.colorbar(sc1, ax=ax1, label='Variants in bin')

    # Below AF = 1%
    sc2 = ax2.scatter([x_stack[i] for i in below_idx],
                      [plot_afs[i] for i in below_idx],
                      s=2, alpha=0.4,
                      c=[colors[i] for i in below_idx],
                      cmap='inferno', edgecolors='none')
    ax2.set_yscale('log')
    ax2.set_ylabel('Allele Frequency (log scale)')
    ax2.set_xticks([])
    ax2.set_xlabel('Variant count per bin (normalized)')
    ax2.set_title(f'AF < 1% ({len(below_idx):,} variants)')
    plt.colorbar(sc2, ax=ax2, label='Variants in bin')

    fig.suptitle('Variant Allele Frequencies — Beeswarm (every data point)', fontsize=14)
    plt.tight_layout()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'problem_3b_{timestamp}.png'
    plt.savefig(filename, dpi=200, bbox_inches='tight')
    plt.close()

    # Standard histogram with log-spaced bins
    import numpy as np
    log_bins = np.logspace(math.log10(min(plot_afs)), math.log10(max(plot_afs)), 51)
    plt.figure(figsize=(12, 6))
    plt.hist(plot_afs, bins=log_bins, color='steelblue', edgecolor='black', alpha=0.7)
    plt.axvline(x=0.01, color='red', linestyle='--', linewidth=1, label='AF = 1%')
    plt.xscale('log')
    plt.xlabel('Allele Frequency (log scale)')
    plt.ylabel('Number of Variants')
    plt.title('Variant Allele Frequencies — Histogram')
    plt.legend()
    plt.tight_layout()
    hist_filename = f'problem_3b_hist_{timestamp}.png'
    plt.savefig(hist_filename, dpi=200, bbox_inches='tight')
    plt.close()

    print(f"(b) Total allele frequency entries: {len(afs)}")
    print(f"    Variants with AF < 1%: {low_af_count}")
    print(f"    Beeswarm saved to {filename}")
    print(f"    Histogram saved to {hist_filename}")


def print_part_c(num_samples, variant_counts):
    print(f"(c) Number of samples: {num_samples}")
    avg_variants = sum(variant_counts) / num_samples if num_samples > 0 else 0
    print(f"    Average distinct variants per individual: {avg_variants:.2f}")


def print_part_d(dbsnp_count):
    print(f"(d) dbSNP is a public database of known single nucleotide polymorphisms and")
    print(f"    other short genetic variations maintained by NCBI.")
    print(f"    Variants with a dbSNP ID: {dbsnp_count}")


def print_part_e():
    phred = 45
    error_prob = 10 ** (-phred / 10)
    accuracy = 1 - error_prob
    print(f"(e) A Phred quality score Q = -10 * log10(P_error) quantifies the probability")
    print(f"    that a base call or variant call is incorrect.")
    print(f"    For Phred = {phred}: P(error) = 10^(-{phred}/10) = {error_prob:.7f}")
    print(f"    Accuracy = {accuracy * 100:.5f}%")


def main():
    print("Streaming VCF (single pass)...")
    header, num_samples, snp_count, afs, variant_counts, dbsnp_count = collect_all(VCF_FILE)

    print_part_a(snp_count)
    print()
    print_part_b(afs)
    print()
    print_part_c(num_samples, variant_counts)
    print()
    print_part_d(dbsnp_count)
    print()
    print_part_e()


if __name__ == '__main__':
    main()

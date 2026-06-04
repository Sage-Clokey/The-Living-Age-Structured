"""
BME 234 — Homework 3, Problem 3
Missense Variant Pathogenicity Prediction using Random Forest
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import roc_curve, auc
import re
import os

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# Part (a): Parse ClinVar VCF and filter Benign/Pathogenic
# ============================================================
print("=" * 60)
print("Part (a): Filtering ClinVar variants")
print("=" * 60)

def parse_vcf(vcf_path):
    """Parse a VCF file into a list of variant dicts."""
    variants = []
    with open(vcf_path, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            fields = line.strip().split('\t')
            chrom = fields[0]
            pos = int(fields[1])
            var_id = fields[2]
            ref = fields[3]
            alt = fields[4]
            info = fields[7]

            # Parse INFO field
            info_dict = {}
            for entry in info.split(';'):
                if '=' in entry:
                    key, val = entry.split('=', 1)
                    info_dict[key] = val

            variants.append({
                'chrom': chrom,
                'pos': pos,
                'id': var_id,
                'ref': ref,
                'alt': alt,
                'info': info_dict,
            })
    return variants

clinvar_variants = parse_vcf(os.path.join(DATA_DIR, 'clinvar_missense.vcf'))

# Filter for exactly "Benign" or "Pathogenic"
filtered = []
for v in clinvar_variants:
    clnsig = v['info'].get('CLNSIG', '')
    if clnsig == 'Benign':
        v['label'] = 0
        filtered.append(v)
    elif clnsig == 'Pathogenic':
        v['label'] = 1
        filtered.append(v)

n_benign = sum(1 for v in filtered if v['label'] == 0)
n_pathogenic = sum(1 for v in filtered if v['label'] == 1)
print(f"Benign variants: {n_benign}")
print(f"Pathogenic variants: {n_pathogenic}")
print(f"Total: {len(filtered)}")

# ============================================================
# Part (b): Train/validation split (80/20)
# ============================================================
print("\n" + "=" * 60)
print("Part (b): Train/validation split")
print("=" * 60)

np.random.seed(42)
indices = np.random.permutation(len(filtered))
split_idx = int(0.8 * len(filtered))
train_indices = indices[:split_idx]
val_indices = indices[split_idx:]

train_set = [filtered[i] for i in train_indices]
val_set = [filtered[i] for i in val_indices]

train_benign = sum(1 for v in train_set if v['label'] == 0)
train_pathogenic = sum(1 for v in train_set if v['label'] == 1)
val_benign = sum(1 for v in val_set if v['label'] == 0)
val_pathogenic = sum(1 for v in val_set if v['label'] == 1)

print(f"Training set — Benign: {train_benign}, Pathogenic: {train_pathogenic}, Total: {len(train_set)}")
print(f"Validation set — Benign: {val_benign}, Pathogenic: {val_pathogenic}, Total: {len(val_set)}")

# ============================================================
# Part (c): RVIS feature
# ============================================================
print("\n" + "=" * 60)
print("Part (c): RVIS scores")
print("=" * 60)

rvis_df = pd.read_csv(os.path.join(DATA_DIR, 'RVIS_Unpublished_ExACv2_March2017.txt'), sep='\t')
rvis_dict = dict(zip(rvis_df['CCDSr20'], rvis_df['%RVIS[pop_maf_0.05%(any)]']))

def get_genes(variant):
    """Extract gene list from GENES info field."""
    genes_str = variant['info'].get('GENES', '')
    if not genes_str:
        return []
    return genes_str.split('|')

def get_rvis(variant):
    """Get RVIS score for a variant. Default 50 if gene not found, average if multiple genes."""
    genes = get_genes(variant)
    if not genes:
        return 50.0
    scores = []
    for gene in genes:
        gene = gene.strip()
        if gene in rvis_dict:
            scores.append(rvis_dict[gene])
    if not scores:
        return 50.0
    return np.mean(scores)

for v in filtered:
    v['rvis'] = get_rvis(v)

# Plot — every data point visible
pathogenic_rvis = np.array([v['rvis'] for v in filtered if v['label'] == 1])
benign_rvis = np.array([v['rvis'] for v in filtered if v['label'] == 0])

rng = np.random.default_rng(42)
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(
    rng.uniform(-0.3, 0.3, size=len(benign_rvis)),
    benign_rvis, s=1, alpha=0.15, c='steelblue', edgecolors='none', label=f'Benign (n={len(benign_rvis)})'
)
ax.scatter(
    1 + rng.uniform(-0.3, 0.3, size=len(pathogenic_rvis)),
    pathogenic_rvis, s=1, alpha=0.15, c='firebrick', edgecolors='none', label=f'Pathogenic (n={len(pathogenic_rvis)})'
)
for i, (data, label) in enumerate([(benign_rvis, 'Benign'), (pathogenic_rvis, 'Pathogenic')]):
    med = np.median(data)
    ax.hlines(med, i - 0.4, i + 0.4, color='white', linewidth=2.5, zorder=4)
    ax.text(i + 0.42, med, f'med={med:.1f}', fontsize=9, va='center', fontweight='bold')
ax.set_xticks([0, 1])
ax.set_xticklabels(['Benign', 'Pathogenic'])
ax.set_ylabel('RVIS Percentile')
ax.set_title('RVIS Distribution: Every Variant = One Point')
ax.legend(markerscale=5)
plt.tight_layout()
plt.savefig(os.path.join(DATA_DIR, 'rvis_histogram.png'), dpi=200)
plt.close()
print("Saved rvis_histogram.png")

print(f"Benign RVIS mean: {np.mean(benign_rvis):.2f}, median: {np.median(benign_rvis):.2f}")
print(f"Pathogenic RVIS mean: {np.mean(pathogenic_rvis):.2f}, median: {np.median(pathogenic_rvis):.2f}")
print("RVIS is useful: pathogenic variants tend to have lower RVIS percentiles (less tolerant genes).")

# ============================================================
# Part (d): o/e feature
# ============================================================
print("\n" + "=" * 60)
print("Part (d): o/e scores")
print("=" * 60)

oe_path = os.path.join(DATA_DIR, 'gnomad.v2.1.1.lof_metrics.by_gene.txt.bgz')
if not os.path.exists(oe_path):
    # Try to download
    import subprocess
    print("Downloading gnomAD o/e data...")
    subprocess.run([
        'wget', '-q', '-O', oe_path,
        'https://storage.googleapis.com/gcp-public-data--gnomad/release/2.1.1/constraint/gnomad.v2.1.1.lof_metrics.by_gene.txt.bgz'
    ], check=True)
    print("Download complete.")

oe_df = pd.read_csv(oe_path, sep='\t', compression='gzip')
oe_dict = dict(zip(oe_df['gene'], oe_df['oe_lof_upper_rank']))

# Find default for missing: use median rank
oe_median = oe_df['oe_lof_upper_rank'].dropna().median()

def get_oe(variant):
    """Get o/e rank for a variant. Default median if gene not found, average if multiple."""
    genes = get_genes(variant)
    if not genes:
        return oe_median
    scores = []
    for gene in genes:
        gene = gene.strip()
        if gene in oe_dict and not pd.isna(oe_dict[gene]):
            scores.append(oe_dict[gene])
    if not scores:
        return oe_median
    return np.mean(scores)

for v in filtered:
    v['oe'] = get_oe(v)

pathogenic_oe = np.array([v['oe'] for v in filtered if v['label'] == 1])
benign_oe = np.array([v['oe'] for v in filtered if v['label'] == 0])

rng_oe = np.random.default_rng(42)
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(
    rng_oe.uniform(-0.3, 0.3, size=len(benign_oe)),
    benign_oe, s=1, alpha=0.15, c='steelblue', edgecolors='none', label=f'Benign (n={len(benign_oe)})'
)
ax.scatter(
    1 + rng_oe.uniform(-0.3, 0.3, size=len(pathogenic_oe)),
    pathogenic_oe, s=1, alpha=0.15, c='firebrick', edgecolors='none', label=f'Pathogenic (n={len(pathogenic_oe)})'
)
for i, (data, label) in enumerate([(benign_oe, 'Benign'), (pathogenic_oe, 'Pathogenic')]):
    med = np.median(data)
    ax.hlines(med, i - 0.4, i + 0.4, color='white', linewidth=2.5, zorder=4)
    ax.text(i + 0.42, med, f'med={med:.0f}', fontsize=9, va='center', fontweight='bold')
ax.set_xticks([0, 1])
ax.set_xticklabels(['Benign', 'Pathogenic'])
ax.set_ylabel('o/e LoF Upper Rank')
ax.set_title('o/e Distribution: Every Variant = One Point')
ax.legend(markerscale=5)
plt.tight_layout()
plt.savefig(os.path.join(DATA_DIR, 'oe_histogram.png'), dpi=200)
plt.close()
print("Saved oe_histogram.png")

print(f"Benign o/e mean: {np.mean(benign_oe):.2f}, median: {np.median(benign_oe):.2f}")
print(f"Pathogenic o/e mean: {np.mean(pathogenic_oe):.2f}, median: {np.median(pathogenic_oe):.2f}")
print("o/e is useful: pathogenic variants tend to be in genes with lower o/e ranks (more constrained).")

# ============================================================
# Part (e): phastCons feature
# ============================================================
print("\n" + "=" * 60)
print("Part (e): phastCons scores")
print("=" * 60)

phastcons_path = os.path.join(DATA_DIR, 'hg38.phastCons100way.bw')
if not os.path.exists(phastcons_path):
    import subprocess
    print("Downloading phastCons bigWig (>5 GB)...")
    subprocess.run([
        'wget', '-q', '-O', phastcons_path,
        'https://hgdownload.cse.ucsc.edu/goldenPath/hg38/phastCons100way/hg38.phastCons100way.bw'
    ], check=True)
    print("Download complete.")

import pyBigWig
bw = pyBigWig.open(phastcons_path)

def get_phastcons(variant, bw_handle):
    """Get phastCons score for a variant position."""
    chrom = 'chr' + str(variant['chrom'])
    pos = variant['pos']
    try:
        vals = bw_handle.values(chrom, pos - 1, pos)  # 0-based
        if vals and vals[0] is not None:
            return vals[0]
    except:
        pass
    return 0.0

print("Extracting phastCons scores...")
for v in filtered:
    v['phastcons'] = get_phastcons(v, bw)

pathogenic_pc = np.array([v['phastcons'] for v in filtered if v['label'] == 1])
benign_pc = np.array([v['phastcons'] for v in filtered if v['label'] == 0])

rng_pc = np.random.default_rng(42)
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(
    rng_pc.uniform(-0.3, 0.3, size=len(benign_pc)),
    benign_pc, s=1, alpha=0.15, c='steelblue', edgecolors='none', label=f'Benign (n={len(benign_pc)})'
)
ax.scatter(
    1 + rng_pc.uniform(-0.3, 0.3, size=len(pathogenic_pc)),
    pathogenic_pc, s=1, alpha=0.15, c='firebrick', edgecolors='none', label=f'Pathogenic (n={len(pathogenic_pc)})'
)
for i, (data, label) in enumerate([(benign_pc, 'Benign'), (pathogenic_pc, 'Pathogenic')]):
    med = np.median(data)
    ax.hlines(med, i - 0.4, i + 0.4, color='white', linewidth=2.5, zorder=4)
    ax.text(i + 0.42, med, f'med={med:.4f}', fontsize=9, va='center', fontweight='bold')
ax.set_xticks([0, 1])
ax.set_xticklabels(['Benign', 'Pathogenic'])
ax.set_ylabel('phastCons Score')
ax.set_title('phastCons Distribution: Every Variant = One Point')
ax.legend(markerscale=5)
plt.tight_layout()
plt.savefig(os.path.join(DATA_DIR, 'phastcons_histogram.png'), dpi=200)
plt.close()
print("Saved phastcons_histogram.png")

print(f"Benign phastCons mean: {np.mean(benign_pc):.4f}, median: {np.median(benign_pc):.4f}")
print(f"Pathogenic phastCons mean: {np.mean(pathogenic_pc):.4f}, median: {np.median(pathogenic_pc):.4f}")
print("phastCons is useful: pathogenic variants tend to occur at highly conserved positions.")

bw.close()

# ============================================================
# Part (f): Train Random Forest with cross-validation
# ============================================================
print("\n" + "=" * 60)
print("Part (f): Random Forest training")
print("=" * 60)

# Build feature matrices
def build_features(variant_list):
    X = np.array([[v['rvis'], v['oe'], v['phastcons']] for v in variant_list])
    y = np.array([v['label'] for v in variant_list])
    return X, y

X_train, y_train = build_features(train_set)
X_val, y_val = build_features(val_set)

# Cross-validation to choose hyperparameters
best_auc = 0
best_params = {}

print("Running cross-validation...")
for n_estimators in [100, 200, 500]:
    for max_depth in [5, 10, 20, None]:
        for min_samples_leaf in [1, 5, 10]:
            rf = RandomForestClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                min_samples_leaf=min_samples_leaf,
                random_state=42,
                n_jobs=-1
            )
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            scores = cross_val_score(rf, X_train, y_train, cv=cv, scoring='roc_auc')
            mean_auc = scores.mean()
            if mean_auc > best_auc:
                best_auc = mean_auc
                best_params = {
                    'n_estimators': n_estimators,
                    'max_depth': max_depth,
                    'min_samples_leaf': min_samples_leaf,
                }

print(f"\nBest cross-validation AUC: {best_auc:.4f}")
print(f"Best hyperparameters: {best_params}")

# Train final model with best hyperparameters
rf_final = RandomForestClassifier(
    n_estimators=best_params['n_estimators'],
    max_depth=best_params['max_depth'],
    min_samples_leaf=best_params['min_samples_leaf'],
    random_state=42,
    n_jobs=-1
)
rf_final.fit(X_train, y_train)

# ROC curve on validation set
y_val_proba = rf_final.predict_proba(X_val)[:, 1]
fpr, tpr, _ = roc_curve(y_val, y_val_proba)
roc_auc = auc(fpr, tpr)

plt.figure(figsize=(7, 6))
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.4f})')
plt.plot([0, 1], [0, 1], color='gray', lw=1, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve — Random Forest Pathogenicity Classifier')
plt.legend(loc='lower right')
plt.tight_layout()
plt.savefig(os.path.join(DATA_DIR, 'roc_curve.png'), dpi=150)
plt.close()
print(f"\nValidation AUC: {roc_auc:.4f}")
print("Saved roc_curve.png")

# ============================================================
# Part (g): Predict on test set
# ============================================================
print("\n" + "=" * 60)
print("Part (g): Test set predictions")
print("=" * 60)

test_variants = parse_vcf(os.path.join(DATA_DIR, 'test_set.vcf'))

# Compute features for test set
for v in test_variants:
    v['rvis'] = get_rvis(v)
    v['oe'] = get_oe(v)

# Need to reopen bigWig for phastCons
bw = pyBigWig.open(phastcons_path)
print("Extracting phastCons scores for test set...")
for v in test_variants:
    v['phastcons'] = get_phastcons(v, bw)
bw.close()

X_test = np.array([[v['rvis'], v['oe'], v['phastcons']] for v in test_variants])
test_proba = rf_final.predict_proba(X_test)[:, 1]

# Write predictions
pred_path = os.path.join(DATA_DIR, 'test_set.predictions')
with open(pred_path, 'w') as f:
    for p in test_proba:
        f.write(f"{p}\n")

print(f"Wrote {len(test_proba)} predictions to test_set.predictions")
print("Done.")

"""
Feature Engineering: Generate ESM-2 embeddings, domain architecture encodings, and context features.

Three representations per protein:
1. ESM-2 mean-pooled embedding (sequence-level, 1280-dim)
2. Domain architecture: bag-of-domains + positional encoding
3. Context features: kingdom one-hot, domain count, multi-domain flag
"""

import json
import torch
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional

DATA_DIR = Path(__file__).parent / "data"


def generate_esm2_embeddings(
    sequences: list[str],
    accessions: list[str],
    batch_size: int = 8,
    max_length: int = 1022,
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
) -> np.ndarray:
    """
    Generate mean-pooled ESM-2 embeddings for protein sequences.
    Uses esm2_t33_650M_UR50D (650M params, 1280-dim embeddings).
    """
    cache_path = DATA_DIR / "esm2_embeddings.npy"
    acc_cache = DATA_DIR / "esm2_accessions.json"

    if cache_path.exists() and acc_cache.exists():
        print("Loading cached ESM-2 embeddings...")
        embeddings = np.load(cache_path)
        with open(acc_cache) as f:
            cached_acc = json.load(f)
        if cached_acc == accessions[:len(cached_acc)]:
            if len(cached_acc) == len(accessions):
                return embeddings
            print(f"  Partial cache: {len(cached_acc)}/{len(accessions)}")

    from transformers import AutoTokenizer, AutoModel

    print(f"Loading ESM-2 model on {device}...")
    model_name = "facebook/esm2_t33_650M_UR50D"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name).to(device)
    model.eval()

    embeddings = np.zeros((len(sequences), 1280), dtype=np.float32)

    print(f"Generating embeddings for {len(sequences)} sequences...")
    with torch.no_grad():
        for i in range(0, len(sequences), batch_size):
            batch_seqs = sequences[i : i + batch_size]
            # Truncate long sequences
            batch_seqs = [s[:max_length] for s in batch_seqs]

            inputs = tokenizer(
                batch_seqs, return_tensors="pt", padding=True, truncation=True, max_length=max_length + 2
            ).to(device)

            outputs = model(**inputs)
            # Mean pool over sequence length (exclude BOS/EOS tokens)
            attention_mask = inputs["attention_mask"]
            hidden = outputs.last_hidden_state
            # Mask padding
            mask_expanded = attention_mask.unsqueeze(-1).float()
            pooled = (hidden * mask_expanded).sum(dim=1) / mask_expanded.sum(dim=1)

            embeddings[i : i + len(batch_seqs)] = pooled.cpu().numpy()

            if (i // batch_size) % 20 == 0:
                print(f"  Batch {i // batch_size + 1}/{(len(sequences) + batch_size - 1) // batch_size}")

            # Free memory
            del inputs, outputs, hidden
            if device == "cuda":
                torch.cuda.empty_cache()

    np.save(cache_path, embeddings)
    with open(acc_cache, "w") as f:
        json.dump(accessions, f)
    print(f"  Saved embeddings to {cache_path}")

    return embeddings


def build_domain_vocabulary(df: pd.DataFrame, min_count: int = 10) -> dict[str, int]:
    """Build domain vocabulary from dataset, filtering rare domains."""
    from collections import Counter
    domain_counts = Counter()
    for domains in df["domains"]:
        domain_counts.update(domains)

    vocab = {d: i + 1 for i, (d, c) in enumerate(domain_counts.most_common()) if c >= min_count}
    # Index 0 reserved for padding/unknown
    print(f"Domain vocabulary: {len(vocab)} domains (min count {min_count})")
    return vocab


def encode_domain_architecture(
    domains_list: list[list[str]],
    domain_vocab: dict[str, int],
    max_domains: int = 20,
) -> np.ndarray:
    """
    Encode domain architectures as fixed-length integer sequences.
    Each protein gets a vector of domain IDs (padded/truncated to max_domains).
    """
    encoded = np.zeros((len(domains_list), max_domains), dtype=np.int32)
    for i, domains in enumerate(domains_list):
        for j, d in enumerate(domains[:max_domains]):
            encoded[i, j] = domain_vocab.get(d, 0)
    return encoded


def encode_domain_bag(
    domains_list: list[list[str]],
    domain_vocab: dict[str, int],
) -> np.ndarray:
    """
    Bag-of-domains encoding: binary vector indicating which domains are present.
    """
    n_domains = len(domain_vocab)
    encoded = np.zeros((len(domains_list), n_domains), dtype=np.float32)
    for i, domains in enumerate(domains_list):
        for d in domains:
            idx = domain_vocab.get(d)
            if idx is not None:
                encoded[i, idx - 1] = 1.0  # vocab is 1-indexed
    return encoded


def encode_context_features(df: pd.DataFrame) -> np.ndarray:
    """
    Context features per protein:
    - Kingdom one-hot (3 dims: Archaea, Bacteria, Eukarya)
    - Number of domains (1 dim, normalized)
    - Is multi-domain (1 dim, binary)
    """
    n = len(df)
    features = np.zeros((n, 5), dtype=np.float32)

    kingdom_map = {"Archaea": 0, "Bacteria": 1, "Eukarya": 2}
    for i, (_, row) in enumerate(df.iterrows()):
        k_idx = kingdom_map.get(row["kingdom"], 2)
        features[i, k_idx] = 1.0
        features[i, 3] = min(row["n_domains"] / 10.0, 1.0)  # normalized domain count
        features[i, 4] = 1.0 if row["n_domains"] > 1 else 0.0

    return features


def encode_go_labels(
    go_terms_list: list[list[str]],
    go_vocab: list[str],
) -> np.ndarray:
    """Multi-hot encoding of GO term labels."""
    go_to_idx = {t: i for i, t in enumerate(go_vocab)}
    labels = np.zeros((len(go_terms_list), len(go_vocab)), dtype=np.float32)
    for i, terms in enumerate(go_terms_list):
        for t in terms:
            idx = go_to_idx.get(t)
            if idx is not None:
                labels[i, idx] = 1.0
    return labels


def prepare_all_features(
    df: pd.DataFrame,
    go_vocab: list[str],
    generate_embeddings: bool = True,
) -> dict[str, np.ndarray]:
    """
    Prepare all feature matrices and labels.
    Returns dict with keys: esm_embeddings, domain_seq, domain_bag, context, labels
    """
    print("=" * 60)
    print("FEATURE ENGINEERING")
    print("=" * 60)

    # Domain vocabulary
    domain_vocab = build_domain_vocabulary(df)
    with open(DATA_DIR / "domain_vocabulary.json", "w") as f:
        json.dump(domain_vocab, f)

    # Domain architectures
    domains_list = df["domains"].tolist()
    domain_seq = encode_domain_architecture(domains_list, domain_vocab)
    domain_bag = encode_domain_bag(domains_list, domain_vocab)
    print(f"Domain sequence shape: {domain_seq.shape}")
    print(f"Domain bag shape: {domain_bag.shape}")

    # Context features
    context = encode_context_features(df)
    print(f"Context features shape: {context.shape}")

    # GO labels
    go_terms_col = "go_terms_filtered" if "go_terms_filtered" in df.columns else "go_terms"
    labels = encode_go_labels(df[go_terms_col].tolist(), go_vocab)
    print(f"Labels shape: {labels.shape}")
    print(f"Mean labels per protein: {labels.sum(axis=1).mean():.1f}")

    result = {
        "domain_seq": domain_seq,
        "domain_bag": domain_bag,
        "context": context,
        "labels": labels,
        "domain_vocab": domain_vocab,
    }

    # ESM-2 embeddings (expensive - optional)
    if generate_embeddings:
        # Get sequence column
        seq_col = [c for c in df.columns if "sequence" in c.lower() or c == "Sequence"]
        if seq_col:
            sequences = df[seq_col[0]].tolist()
        else:
            sequences = df.iloc[:, 1].tolist()  # fallback: second column is usually sequence

        accessions = df.iloc[:, 0].tolist()
        esm_embeddings = generate_esm2_embeddings(sequences, accessions)
        result["esm_embeddings"] = esm_embeddings
    else:
        print("Skipping ESM-2 embeddings (generate_embeddings=False)")

    return result


if __name__ == "__main__":
    from data_pipeline import build_dataset, filter_go_terms

    df = build_dataset(max_per_kingdom=5000)
    df, go_vocab = filter_go_terms(df, min_proteins=50)

    features = prepare_all_features(df, go_vocab, generate_embeddings=True)
    print("\nAll features prepared successfully!")
    for k, v in features.items():
        if isinstance(v, np.ndarray):
            print(f"  {k}: {v.shape}")

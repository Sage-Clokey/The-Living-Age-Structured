"""
Data Pipeline: Download and process Swiss-Prot proteins with Pfam domains, GO labels, and taxonomy.

Builds a unified dataset where each protein has:
- UniProt ID and sequence
- Ordered list of Pfam domain IDs (the "domain grammar")
- GO term annotations (molecular function + biological process)
- Kingdom of origin (Archaea, Bacteria, Eukarya)
- Horizontal transfer flag (from HGT-DB where available)
"""

import json
import time
import requests
import pandas as pd
from pathlib import Path
from typing import Optional

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def query_uniprot_batch(
    query: str = "(reviewed:true)",
    fields: str = "accession,sequence,go_f,go_p,lineage(SUPERKINGDOM),xref_pfam,length",
    size: int = 500,
    max_results: int = 10000,
    format: str = "tsv",
) -> pd.DataFrame:
    """
    Query UniProt REST API with pagination.
    Downloads reviewed (Swiss-Prot) proteins with GO, Pfam, and taxonomy.
    """
    base_url = "https://rest.uniprot.org/uniprotkb/search"
    params = {
        "query": query,
        "fields": fields,
        "format": format,
        "size": size,
    }

    all_results = []
    next_url = None
    total_fetched = 0

    print(f"Querying UniProt: {query}")
    print(f"Target: {max_results} proteins")

    while total_fetched < max_results:
        if next_url:
            response = requests.get(next_url)
        else:
            response = requests.get(base_url, params=params)

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 5))
            print(f"  Rate limited, waiting {retry_after}s...")
            time.sleep(retry_after)
            continue

        response.raise_for_status()
        lines = response.text.strip().split("\n")

        if total_fetched == 0:
            header = lines[0]
            data_lines = lines[1:]
        else:
            data_lines = lines[1:] if lines[0] == header else lines

        all_results.extend(data_lines)
        total_fetched += len(data_lines)
        print(f"  Fetched {total_fetched}/{max_results}...")

        link_header = response.headers.get("Link", "")
        if 'rel="next"' in link_header:
            next_url = link_header.split(";")[0].strip("<>")
        else:
            break

        time.sleep(0.5)

    tsv_text = header + "\n" + "\n".join(all_results[:max_results])
    from io import StringIO
    df = pd.read_csv(StringIO(tsv_text), sep="\t")
    print(f"  Downloaded {len(df)} proteins")
    return df


def query_uniprot_by_kingdom(kingdom: str, max_per_kingdom: int = 5000) -> pd.DataFrame:
    """Query Swiss-Prot proteins for a specific kingdom with multi-domain preference."""
    taxonomy_map = {
        "Archaea": "taxonomy_name:Archaea",
        "Bacteria": "taxonomy_name:Bacteria",
        "Eukarya": "taxonomy_name:Eukaryota",
    }
    tax_query = taxonomy_map[kingdom]
    # Prefer proteins with Pfam annotations (domain-containing)
    query = f"(reviewed:true) AND ({tax_query}) AND (database:pfam)"
    df = query_uniprot_batch(query=query, max_results=max_per_kingdom)
    df["kingdom"] = kingdom
    return df


def parse_pfam_domains(pfam_str: str) -> list[str]:
    """Parse Pfam cross-references into ordered domain list."""
    if pd.isna(pfam_str) or pfam_str == "":
        return []
    # UniProt format: "PF00069;PF00433;PF07714" or "PF00069; PF00433"
    domains = [d.strip().split(":")[0] for d in pfam_str.replace(";", ",").split(",")]
    return [d for d in domains if d.startswith("PF")]


def parse_go_terms(go_f_str: str, go_p_str: str) -> list[str]:
    """Parse GO molecular function and biological process terms."""
    terms = []
    for go_str in [go_f_str, go_p_str]:
        if pd.isna(go_str) or go_str == "":
            continue
        # Format: "GO:0005524 [ATP binding]; GO:0004672 [protein kinase activity]"
        for entry in go_str.split(";"):
            entry = entry.strip()
            if entry.startswith("GO:"):
                go_id = entry.split("[")[0].strip().split(" ")[0]
                terms.append(go_id)
    return terms


def build_dataset(
    max_per_kingdom: int = 5000,
    min_go_terms: int = 1,
    min_domains: int = 1,
) -> pd.DataFrame:
    """
    Build the full dataset: proteins from all three kingdoms with domains and GO terms.
    Filters to proteins that have at least min_domains Pfam domains and min_go_terms GO annotations.
    """
    cache_path = DATA_DIR / "raw_dataset.parquet"
    if cache_path.exists():
        print(f"Loading cached dataset from {cache_path}")
        return pd.read_parquet(cache_path)

    dfs = []
    for kingdom in ["Archaea", "Bacteria", "Eukarya"]:
        df = query_uniprot_by_kingdom(kingdom, max_per_kingdom=max_per_kingdom)
        dfs.append(df)
        time.sleep(2)

    combined = pd.concat(dfs, ignore_index=True)
    print(f"\nTotal raw proteins: {len(combined)}")

    # Parse domains and GO terms
    pfam_col = [c for c in combined.columns if "pfam" in c.lower() or "xref" in c.lower()]
    go_f_col = [c for c in combined.columns if "go_f" in c.lower() or "Gene Ontology (molecular function)" in c]
    go_p_col = [c for c in combined.columns if "go_p" in c.lower() or "Gene Ontology (biological process)" in c]

    print(f"Columns found: {combined.columns.tolist()}")

    # Identify the right columns
    pfam_column = pfam_col[0] if pfam_col else None
    go_f_column = go_f_col[0] if go_f_col else None
    go_p_column = go_p_col[0] if go_p_col else None

    if not pfam_column:
        # Try to find it by position or name pattern
        for col in combined.columns:
            if "Pfam" in col or "pfam" in col:
                pfam_column = col
                break

    combined["domains"] = combined[pfam_column].apply(parse_pfam_domains) if pfam_column else [[]] * len(combined)
    combined["go_terms"] = [
        parse_go_terms(
            combined.iloc[i][go_f_column] if go_f_column else "",
            combined.iloc[i][go_p_column] if go_p_column else "",
        )
        for i in range(len(combined))
    ]

    combined["n_domains"] = combined["domains"].apply(len)
    combined["n_go_terms"] = combined["go_terms"].apply(len)

    # Filter
    filtered = combined[
        (combined["n_domains"] >= min_domains) & (combined["n_go_terms"] >= min_go_terms)
    ].copy()

    print(f"After filtering (>={min_domains} domains, >={min_go_terms} GO terms): {len(filtered)}")
    print(f"  Archaea: {(filtered['kingdom'] == 'Archaea').sum()}")
    print(f"  Bacteria: {(filtered['kingdom'] == 'Bacteria').sum()}")
    print(f"  Eukarya: {(filtered['kingdom'] == 'Eukarya').sum()}")

    # Save
    filtered.to_parquet(cache_path)
    print(f"Saved to {cache_path}")
    return filtered


def filter_go_terms(df: pd.DataFrame, min_proteins: int = 50) -> tuple[pd.DataFrame, list[str]]:
    """
    Filter GO terms to those with at least min_proteins annotations.
    Returns filtered dataframe and the GO term vocabulary.
    """
    from collections import Counter
    all_terms = Counter()
    for terms in df["go_terms"]:
        all_terms.update(terms)

    valid_terms = [t for t, count in all_terms.items() if count >= min_proteins]
    valid_terms.sort()
    print(f"GO terms with >= {min_proteins} proteins: {len(valid_terms)}")

    # Filter proteins to those with at least one valid GO term
    df = df.copy()
    df["go_terms_filtered"] = df["go_terms"].apply(
        lambda terms: [t for t in terms if t in set(valid_terms)]
    )
    df = df[df["go_terms_filtered"].apply(len) > 0].copy()
    print(f"Proteins with valid GO terms: {len(df)}")

    return df, valid_terms


if __name__ == "__main__":
    df = build_dataset(max_per_kingdom=5000)
    df, go_vocab = filter_go_terms(df, min_proteins=50)

    # Save GO vocabulary
    with open(DATA_DIR / "go_vocabulary.json", "w") as f:
        json.dump(go_vocab, f)

    print(f"\nDataset ready:")
    print(f"  Proteins: {len(df)}")
    print(f"  GO terms: {len(go_vocab)}")
    print(f"  Mean domains per protein: {df['n_domains'].mean():.1f}")
    print(f"  Mean GO terms per protein: {df['go_terms_filtered'].apply(len).mean():.1f}")

"""
NCBI Entrez API wrapper for organisms outside the UCSC genome browser.

Covers organisms critical for living architecture that UCSC lacks:
  - Fungi / mycelium (Ganoderma, Pleurotus, Aspergillus)
  - Bacterial cellulose (Komagataeibacter xylinus)
  - Plants (Arabidopsis thaliana — morphogenesis, growth direction)
  - Coral (Acropora millepora — biomineralization, structural scaffold)
  - Spider (Nephila clavipes — silk proteins, tensile strength)
  - Axolotl (Ambystoma mexicanum — regeneration)
  - Planaria (Schmidtea mediterranea — full body regeneration)
  - Firefly (Photinus pyralis — luciferase, bioluminescence)

Uses NCBI E-utilities (no API key required for low-volume use;
set NCBI_API_KEY env var to increase rate limit from 3 to 10 req/s).
"""

import os
import time
import requests
from typing import Optional

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
API_KEY = os.environ.get("NCBI_API_KEY", "")
SESSION = requests.Session()
SESSION.headers.update({"Accept": "application/json"})

# Rate limit: 3 req/s without key, 10 req/s with key
_RATE_DELAY = 0.11 if API_KEY else 0.34
_last_request = 0.0


def _get(endpoint: str, params: dict) -> requests.Response:
    global _last_request
    elapsed = time.time() - _last_request
    if elapsed < _RATE_DELAY:
        time.sleep(_RATE_DELAY - elapsed)
    if API_KEY:
        params["api_key"] = API_KEY
    response = SESSION.get(f"{BASE_URL}/{endpoint}", params=params, timeout=30)
    _last_request = time.time()
    response.raise_for_status()
    return response


# Organisms relevant to living architecture not covered by UCSC
# Note: taxid verified against NCBI Taxonomy
NCBI_RELEVANT = {
    "arabidopsis":    "3702",    # A. thaliana — plant morphogenesis, growth direction
    "ganoderma":      "5345",    # G. lucidum — mycelium structural networks
    "pleurotus":      "5334",    # P. ostreatus — mycelium, lignocellulose breakdown
    "aspergillus":    "746128",  # A. niger — cell wall biosynthesis
    "komagataeibacter": "28448", # K. xylinus — bacterial cellulose (use gene name 'bcsA')
    "acropora":       "6125",    # A. millepora — coral biomineralization
    "nephila":        "6914",    # Nephila genus (taxid 6914) — spider silk (search nuccore)
    "axolotl":        "8296",    # A. mexicanum — limb/tissue regeneration
    "planaria":       "79327",   # S. mediterranea — full body regeneration
    "firefly":        "7054",    # P. pyralis — luciferase bioluminescence
}

# Gene name conventions for key functions (NCBI uses these, not plain English)
GENE_NAME_MAP = {
    "cellulose":      "bcsA",        # bacterial cellulose synthase A
    "silk":           "spidroin",    # spider silk — better in nuccore than gene db
    "luciferase":     "luc",         # firefly luciferase
    "regeneration":   "piwi",        # stem cell / regeneration master regulator
    "morphogenesis":  "WUS",         # WUSCHEL — plant meristem identity
    "biomineralization": "carp",     # carbonic anhydrase related protein
}


def search_gene(gene_name: str, organism: str, max_results: int = 10) -> list[dict]:
    """
    Search NCBI Gene database for a gene in a given organism.
    organism can be a common name (looked up in NCBI_RELEVANT) or a taxon ID.
    Returns list of {gene_id, symbol, description, organism, taxid}.

    Falls back to nucleotide (nuccore) search for organisms with sparse
    Gene DB annotation (e.g. spiders, some invertebrates).
    """
    taxid = NCBI_RELEVANT.get(organism.lower(), organism)

    # Translate plain English to NCBI gene name conventions
    query_name = GENE_NAME_MAP.get(gene_name.lower(), gene_name)
    query = f"{query_name}[Gene Name] AND txid{taxid}[Organism]"

    r = _get("esearch.fcgi", {
        "db": "gene",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
    })
    ids = r.json().get("esearchresult", {}).get("idlist", [])

    if ids:
        r = _get("esummary.fcgi", {
            "db": "gene",
            "id": ",".join(ids),
            "retmode": "json",
        })
        summaries = r.json().get("result", {})
        results = []
        for gid in ids:
            s = summaries.get(gid, {})
            results.append({
                "source": "gene",
                "gene_id": gid,
                "symbol": s.get("name"),
                "description": s.get("description"),
                "organism": s.get("organism", {}).get("scientificname"),
                "taxid": s.get("taxid"),
                "chromosome": s.get("chromosome"),
                "location": s.get("maplocation"),
            })
        return results

    # Fallback: search nucleotide database (better for spiders, some invertebrates)
    nuccore_query = f"{query_name}[Title] AND txid{taxid}[Organism] AND mRNA[Filter]"
    r = _get("esearch.fcgi", {
        "db": "nuccore",
        "term": nuccore_query,
        "retmax": max_results,
        "retmode": "json",
    })
    ids = r.json().get("esearchresult", {}).get("idlist", [])
    if not ids:
        return []

    r = _get("esummary.fcgi", {
        "db": "nuccore",
        "id": ",".join(ids),
        "retmode": "json",
    })
    summaries = r.json().get("result", {})
    results = []
    for nid in ids:
        s = summaries.get(nid, {})
        results.append({
            "source": "nuccore",
            "gene_id": nid,
            "symbol": s.get("accessionversion"),
            "description": s.get("title"),
            "organism": s.get("organism"),
            "taxid": taxid,
            "chromosome": None,
            "location": None,
        })
    return results


def fetch_sequence(accession: str) -> str:
    """
    Fetch nucleotide sequence by accession ID (e.g. 'NM_001234').
    Returns the raw FASTA sequence string (no header).
    """
    r = _get("efetch.fcgi", {
        "db": "nucleotide",
        "id": accession,
        "rettype": "fasta",
        "retmode": "text",
    })
    lines = r.text.strip().split("\n")
    # Strip FASTA header line(s)
    seq_lines = [l for l in lines if not l.startswith(">")]
    return "".join(seq_lines)


def fetch_protein_sequence(accession: str) -> str:
    """
    Fetch protein sequence by accession ID.
    Returns the raw FASTA sequence string (no header).
    """
    r = _get("efetch.fcgi", {
        "db": "protein",
        "id": accession,
        "rettype": "fasta",
        "retmode": "text",
    })
    lines = r.text.strip().split("\n")
    seq_lines = [l for l in lines if not l.startswith(">")]
    return "".join(seq_lines)


def search_organism(name: str) -> list[dict]:
    """
    Search NCBI Taxonomy for an organism by name.
    Returns list of {taxid, scientific_name, common_name, rank}.
    """
    r = _get("esearch.fcgi", {
        "db": "taxonomy",
        "term": name,
        "retmax": 10,
        "retmode": "json",
    })
    ids = r.json().get("esearchresult", {}).get("idlist", [])
    if not ids:
        return []

    r = _get("esummary.fcgi", {
        "db": "taxonomy",
        "id": ",".join(ids),
        "retmode": "json",
    })
    summaries = r.json().get("result", {})
    results = []
    for tid in ids:
        s = summaries.get(tid, {})
        results.append({
            "taxid": tid,
            "scientific_name": s.get("scientificname"),
            "common_name": s.get("commonname"),
            "rank": s.get("rank"),
        })
    return results


def get_gene_sequences(gene_name: str, organism: str) -> list[dict]:
    """
    Convenience: search for a gene, then fetch the mRNA sequence for each hit.
    Returns list of {symbol, description, organism, accession, sequence}.
    """
    genes = search_gene(gene_name, organism, max_results=3)
    results = []
    for gene in genes:
        # Search for linked nucleotide records
        r = _get("elink.fcgi", {
            "dbfrom": "gene",
            "db": "nuccore",
            "id": gene["gene_id"],
            "linkname": "gene_nuccore_refseqrna",
            "retmode": "json",
        })
        link_data = r.json()
        link_sets = link_data.get("linksets", [])
        if not link_sets:
            continue
        linked_ids = []
        for ls in link_sets:
            for ld in ls.get("linksetdbs", []):
                linked_ids.extend(ld.get("links", []))

        if not linked_ids:
            continue

        accession_id = linked_ids[0]
        # Get accession string
        r2 = _get("esummary.fcgi", {
            "db": "nuccore",
            "id": accession_id,
            "retmode": "json",
        })
        acc = r2.json().get("result", {}).get(str(accession_id), {}).get("accessionversion", accession_id)
        seq = fetch_sequence(str(accession_id))
        results.append({
            "symbol": gene["symbol"],
            "description": gene["description"],
            "organism": gene["organism"],
            "accession": acc,
            "sequence": seq,
        })
    return results

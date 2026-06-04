"""
UCSC Genome Browser REST API wrapper.

UCSC covers ~220 genomes, primarily vertebrates and key model organisms:
  S. cerevisiae, C. elegans, D. melanogaster, S. purpuratus, zebrafish, etc.

For organisms outside UCSC (mycelium, bacteria, plants, coral, spider),
use ncbi_client.py which wraps the NCBI Entrez API.

UCSC endpoints used:
  /list/ucscGenomes              - all available genomes
  /list/tracks?genome=           - tracks for a genome
  /search?search=&genome=        - search genes/features by name
  /getData/sequence?genome=&chrom=&start=&end=   - fetch DNA sequence
  /getData/track?genome=&track=&chrom=&start=&end= - fetch track annotations
"""

import requests
from typing import Optional


# Organisms relevant to living architecture that ARE in UCSC
UCSC_RELEVANT = {
    "yeast":          "sacCer3",   # S. cerevisiae — cell wall, chitin biosynthesis
    "sea urchin":     "strPur2",   # S. purpuratus — biomineralization, shell formation
    "c. elegans":     "ce11",      # C. elegans — development, regeneration signals
    "fruit fly":      "dm6",       # D. melanogaster — morphogenesis, tissue patterning
    "zebrafish":      "danRer11",  # D. rerio — fin/limb patterning, organ development
    "frog":           "xenTro10",  # X. tropicalis — regeneration, wound healing
    "mouse":          "mm39",      # M. musculus — connective tissue, collagen
    "human":          "hg38",      # H. sapiens — full annotation reference
}

BASE_URL = "https://api.genome.ucsc.edu"
SESSION = requests.Session()
SESSION.headers.update({"Accept": "application/json"})


def _get(endpoint: str, params: dict) -> dict:
    url = f"{BASE_URL}{endpoint}"
    response = SESSION.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


# --- Genome catalog ---

def list_genomes() -> dict[str, dict]:
    """Return all available UCSC genomes keyed by assembly ID (e.g. 'hg38')."""
    data = _get("/list/ucscGenomes", {})
    return data.get("ucscGenomes", {})


def find_genome(organism_name: str) -> list[dict]:
    """
    Search the genome catalog for an organism by common or scientific name.
    Returns a list of matching assemblies with keys: genome, organism, scientificName, description.
    """
    all_genomes = list_genomes()
    name_lower = organism_name.lower()
    matches = []
    for assembly_id, info in all_genomes.items():
        if (name_lower in info.get("organism", "").lower() or
                name_lower in info.get("scientificName", "").lower()):
            matches.append({
                "genome": assembly_id,
                "organism": info.get("organism"),
                "scientificName": info.get("scientificName"),
                "description": info.get("description"),
            })
    return matches


# --- Track catalog ---

def list_tracks(genome: str) -> dict:
    """Return all tracks available for a genome assembly."""
    data = _get("/list/tracks", {"genome": genome})
    return data.get(genome, {})


# --- Gene search ---

def search_gene(gene_name: str, genome: str) -> list[dict]:
    """
    Search for a gene or feature by name within a genome.
    Returns a list of position matches: {track, position, description}.
    """
    data = _get("/search", {"search": gene_name, "genome": genome})
    results = []
    for match_group in data.get("positionMatches", []):
        track = match_group.get("trackName")
        for hit in match_group.get("matches", []):
            results.append({
                "track": track,
                "position": hit.get("position"),
                "name": hit.get("posName"),
                "description": hit.get("description", "").strip(),
            })
    return results


# --- Sequence retrieval ---

def fetch_sequence(genome: str, chrom: str, start: int, end: int) -> str:
    """
    Fetch raw DNA sequence for a genomic region.
    Coordinates are 0-based half-open [start, end).
    """
    data = _get("/getData/sequence", {
        "genome": genome,
        "chrom": chrom,
        "start": start,
        "end": end,
    })
    return data.get("dna", "")


# --- Track annotation retrieval ---

def fetch_track_data(genome: str, track: str, chrom: str, start: int, end: int) -> list[dict]:
    """
    Fetch annotation records from a track for a genomic region.
    Returns the list of feature records (format varies by track type).
    """
    data = _get("/getData/track", {
        "genome": genome,
        "track": track,
        "chrom": chrom,
        "start": start,
        "end": end,
    })
    return data.get(track, [])


# --- Convenience: gene region lookup ---

def get_gene_region(gene_name: str, genome: str) -> Optional[dict]:
    """
    Find a gene by name and return its genomic coordinates.
    Returns {chrom, start, end, strand, name} or None if not found.
    Uses refGene track.
    """
    hits = search_gene(gene_name, genome)
    if not hits:
        return None

    # Parse the first hit position "chrX:start-end"
    position = hits[0].get("position", "")
    if ":" not in position or "-" not in position:
        return None

    chrom, coords = position.split(":")
    start, end = coords.split("-")

    # Fetch the refGene annotation to get strand info
    annotations = fetch_track_data(genome, "refGene", chrom, int(start), int(end))
    if annotations:
        ann = annotations[0]
        return {
            "chrom": chrom,
            "start": ann.get("txStart", int(start)),
            "end": ann.get("txEnd", int(end)),
            "strand": ann.get("strand"),
            "name": ann.get("name2", gene_name),
            "refseq_id": ann.get("name"),
            "genome": genome,
        }

    return {
        "chrom": chrom,
        "start": int(start),
        "end": int(end),
        "strand": None,
        "name": gene_name,
        "genome": genome,
    }

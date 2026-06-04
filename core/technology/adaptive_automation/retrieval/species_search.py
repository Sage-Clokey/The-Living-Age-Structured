"""
Natural language → species + gene targets mapper.

Rule-based interpretation of functional descriptions into structured queries
for the UCSC and NCBI retrieval clients. No API key required.

When a description is given, this module:
1. Detects which biological capabilities are being requested
2. Maps each capability to source organisms, gene names, and databases
3. Returns a list of QueryTarget objects ready for the retrieval clients

Later: swap _interpret_with_rules() for a Claude API call to handle
open-ended descriptions not covered by the keyword map.
"""

from dataclasses import dataclass, field


@dataclass
class QueryTarget:
    """A single retrieval target derived from a functional description."""
    capability: str          # human-readable capability name
    organism: str            # common name key for ucsc_client or ncbi_client
    gene: str                # gene name to search
    database: str            # "ucsc" or "ncbi"
    genome: str              # UCSC assembly ID (e.g. "danRer11") or "" for NCBI
    level: str               # "gene", "regulatory", or "pathway"
    notes: str = ""          # context on why this organism was chosen


# ---------------------------------------------------------------------------
# Capability → targets map
# Each capability key maps to one or more QueryTargets.
# Multiple targets per capability = redundancy + cross-species comparison.
# ---------------------------------------------------------------------------

CAPABILITY_MAP: dict[str, list[dict]] = {

    "structural": [
        {
            "organism": "ganoderma",   "gene": "fkbp",
            "database": "ncbi",        "genome": "",
            "level": "gene",
            "notes": "mycelium load-bearing hyphal network proteins",
        },
        {
            "organism": "acropora",    "gene": "galaxin",
            "database": "ncbi",        "genome": "",
            "level": "gene",
            "notes": "coral skeleton matrix protein for biomineralization",
        },
        {
            "organism": "sea urchin",  "gene": "sm30",
            "database": "ucsc",        "genome": "strPur2",
            "level": "gene",
            "notes": "spicule matrix protein — calcium carbonate scaffolding",
        },
    ],

    "self-repair": [
        {
            "organism": "axolotl",     "gene": "piwi",
            "database": "ncbi",        "genome": "",
            "level": "pathway",
            "notes": "master regulator of stem cell maintenance and tissue regeneration",
        },
        {
            "organism": "planaria",    "gene": "piwi",
            "database": "ncbi",        "genome": "",
            "level": "pathway",
            "notes": "planaria can regenerate entire body — strongest known piwi expression",
        },
        {
            "organism": "zebrafish",   "gene": "mmp9",
            "database": "ucsc",        "genome": "danRer11",
            "level": "gene",
            "notes": "matrix metalloproteinase — breaks down damaged tissue to enable regrowth",
        },
        {
            "organism": "frog",        "gene": "hif1a",
            "database": "ucsc",        "genome": "xenTro10",
            "level": "regulatory",
            "notes": "hypoxia-inducible factor — triggers repair response under stress",
        },
    ],

    "growth": [
        {
            "organism": "arabidopsis", "gene": "WUS",
            "database": "ncbi",        "genome": "",
            "level": "regulatory",
            "notes": "WUSCHEL — meristem identity gene controlling where growth occurs",
        },
        {
            "organism": "arabidopsis", "gene": "CLV3",
            "database": "ncbi",        "genome": "",
            "level": "regulatory",
            "notes": "CLAVATA3 — feedback signal that limits WUS, controls growth boundary",
        },
        {
            "organism": "zebrafish",   "gene": "shha",
            "database": "ucsc",        "genome": "danRer11",
            "level": "pathway",
            "notes": "sonic hedgehog — tissue patterning and directional growth",
        },
        {
            "organism": "fruit fly",   "gene": "dpp",
            "database": "ucsc",        "genome": "dm6",
            "level": "pathway",
            "notes": "decapentaplegic (BMP homolog) — morphogen gradient for shape patterning",
        },
    ],

    "cellulose": [
        {
            "organism": "komagataeibacter", "gene": "bcsA",
            "database": "ncbi",             "genome": "",
            "level": "gene",
            "notes": "bacterial cellulose synthase A — produces pure cellulose sheets",
        },
        {
            "organism": "komagataeibacter", "gene": "bcsB",
            "database": "ncbi",             "genome": "",
            "level": "gene",
            "notes": "bcsB — regulatory subunit of the cellulose synthase complex",
        },
        {
            "organism": "arabidopsis",      "gene": "CESA1",
            "database": "ncbi",             "genome": "",
            "level": "gene",
            "notes": "plant cellulose synthase — produces thicker cell wall cellulose",
        },
    ],

    "tensile-strength": [
        {
            "organism": "nephila",     "gene": "spidroin",
            "database": "ncbi",        "genome": "",
            "level": "gene",
            "notes": "dragline silk spidroin 1 — strongest known biological fiber",
        },
        {
            "organism": "mouse",       "gene": "Col1a1",
            "database": "ucsc",        "genome": "mm39",
            "level": "gene",
            "notes": "collagen type I — vertebrate tensile structural protein",
        },
    ],

    "thermal-regulation": [
        {
            "organism": "arabidopsis", "gene": "HSP90",
            "database": "ncbi",        "genome": "",
            "level": "gene",
            "notes": "heat shock protein — regulates protein stability under temperature stress",
        },
        {
            "organism": "c. elegans",  "gene": "daf-16",
            "database": "ucsc",        "genome": "ce11",
            "level": "regulatory",
            "notes": "FOXO transcription factor — master regulator of stress response",
        },
    ],

    "bioluminescence": [
        {
            "organism": "firefly",     "gene": "luciferase",
            "database": "ncbi",        "genome": "",
            "level": "gene",
            "notes": "luciferin 4-monooxygenase — produces visible light signal",
        },
    ],

    "biomineralization": [
        {
            "organism": "sea urchin",  "gene": "sm50",
            "database": "ucsc",        "genome": "strPur2",
            "level": "gene",
            "notes": "spicule matrix protein 50 — nucleates calcium carbonate crystal growth",
        },
        {
            "organism": "acropora",    "gene": "galaxin",
            "database": "ncbi",        "genome": "",
            "level": "gene",
            "notes": "coral calcification protein — controls mineral deposition rate",
        },
    ],

    "water-transport": [
        {
            "organism": "arabidopsis", "gene": "PIP1",
            "database": "ncbi",        "genome": "",
            "level": "gene",
            "notes": "plasma membrane intrinsic protein — aquaporin for water channel regulation",
        },
        {
            "organism": "mouse",       "gene": "Aqp1",
            "database": "ucsc",        "genome": "mm39",
            "level": "gene",
            "notes": "aquaporin 1 — water channel protein for passive water movement",
        },
    ],

    "nutrient-uptake": [
        {
            "organism": "yeast",       "gene": "HXT1",
            "database": "ucsc",        "genome": "sacCer3",
            "level": "gene",
            "notes": "hexose transporter — high-capacity glucose uptake from environment",
        },
        {
            "organism": "arabidopsis", "gene": "NRT1",
            "database": "ncbi",        "genome": "",
            "level": "gene",
            "notes": "nitrate transporter — nitrogen uptake from soil/substrate",
        },
    ],
}

# ---------------------------------------------------------------------------
# Keyword → capability mapping
# Catches natural language variations and maps them to capability keys above.
# ---------------------------------------------------------------------------

KEYWORD_MAP: dict[str, str] = {
    # structural
    "structural": "structural",    "structure": "structural",
    "load-bearing": "structural",  "load bearing": "structural",
    "scaffold": "structural",      "rigid": "structural",
    "hard": "structural",          "stiff": "structural",
    "framework": "structural",

    # self-repair
    "repair": "self-repair",       "self-repair": "self-repair",
    "regenerat": "self-repair",    "heal": "self-repair",
    "restore": "self-repair",      "recover": "self-repair",
    "wound": "self-repair",

    # growth
    "grow": "growth",              "growth": "growth",
    "shape": "growth",             "form": "growth",
    "pattern": "growth",           "morph": "growth",
    "direct": "growth",            "organ": "growth",

    # cellulose
    "cellulose": "cellulose",      "sheet": "cellulose",
    "fiber": "cellulose",          "fibre": "cellulose",
    "flexible": "cellulose",       "membrane": "cellulose",

    # tensile strength
    "tensile": "tensile-strength", "silk": "tensile-strength",
    "strong": "tensile-strength",  "strength": "tensile-strength",
    "tough": "tensile-strength",   "durable": "tensile-strength",

    # thermal
    "thermal": "thermal-regulation", "temperature": "thermal-regulation",
    "heat": "thermal-regulation",    "cool": "thermal-regulation",
    "insulat": "thermal-regulation", "stress": "thermal-regulation",

    # bioluminescence
    "light": "bioluminescence",    "luminesc": "bioluminescence",
    "glow": "bioluminescence",     "bioluminesc": "bioluminescence",
    "signal": "bioluminescence",

    # biomineralization
    "mineral": "biomineralization", "calcif": "biomineralization",
    "bone": "biomineralization",    "shell": "biomineralization",
    "harden": "biomineralization",  "stone": "biomineralization",

    # water
    "water": "water-transport",    "aqua": "water-transport",
    "moisture": "water-transport", "humid": "water-transport",

    # nutrients
    "nutrient": "nutrient-uptake", "feed": "nutrient-uptake",
    "absorb": "nutrient-uptake",   "uptake": "nutrient-uptake",
}


# ---------------------------------------------------------------------------
# Main interface
# ---------------------------------------------------------------------------

def interpret(description: str) -> list[QueryTarget]:
    """
    Parse a natural language functional description and return a list of
    QueryTargets for the retrieval clients.

    Example:
        interpret("grow a load-bearing wall that self-repairs")
        → targets for: structural + growth + self-repair capabilities
    """
    description_lower = description.lower()
    matched_capabilities: set[str] = set()

    for keyword, capability in KEYWORD_MAP.items():
        if keyword in description_lower:
            matched_capabilities.add(capability)

    if not matched_capabilities:
        return []

    targets = []
    for capability in sorted(matched_capabilities):
        for entry in CAPABILITY_MAP.get(capability, []):
            targets.append(QueryTarget(
                capability=capability,
                organism=entry["organism"],
                gene=entry["gene"],
                database=entry["database"],
                genome=entry["genome"],
                level=entry["level"],
                notes=entry["notes"],
            ))

    return targets


def summarize(targets: list[QueryTarget]) -> None:
    """Print a human-readable summary of what will be queried."""
    if not targets:
        print("No capabilities matched. Try keywords like: structural, repair, grow, cellulose, silk, thermal, light, mineral.")
        return

    by_capability: dict[str, list[QueryTarget]] = {}
    for t in targets:
        by_capability.setdefault(t.capability, []).append(t)

    print(f"Found {len(by_capability)} capabilities → {len(targets)} retrieval targets\n")
    for capability, cap_targets in by_capability.items():
        print(f"  [{capability}]")
        for t in cap_targets:
            print(f"    {t.organism:22} gene={t.gene:10} db={t.database:5} level={t.level}")
            if t.notes:
                print(f"    {'':22} → {t.notes}")
        print()

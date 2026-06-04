"""
Adaptive Genome Design System — main pipeline entry point.

Usage:
    python main.py

The pipeline takes a plain English description of what you want a living
organism to do, finds the genomic elements that do it across the tree of
life, adapts them to work together in a target chassis, and outputs a
designed DNA construct ready for synthesis and structural validation.

North star: grow houses that are living organisms — structurally functional,
organically shaped, self-repairing, and environmentally adaptive.
"""

from retrieval.species_search import interpret, summarize, QueryTarget
from retrieval.ucsc_client import get_gene_region, fetch_sequence, UCSC_RELEVANT
from retrieval.ncbi_client import search_gene
from models.genomic_part import GenomicPart, from_ucsc, from_ncbi
from assembly.assembler import assemble
from output.formatter import write_outputs, print_summary


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_CHASSIS = "ganoderma"   # target host organism for all designs
OUTPUT_DIR      = "output"      # where to write results
MAX_PARTS       = 6             # max parts to retrieve per run (API rate limit)


# ---------------------------------------------------------------------------
# Retrieval: turn QueryTargets into GenomicParts
# ---------------------------------------------------------------------------

def retrieve_parts(targets: list[QueryTarget], max_parts: int = MAX_PARTS) -> list[GenomicPart]:
    """
    For each QueryTarget, fetch sequence data from UCSC or NCBI and
    return a list of GenomicPart objects.
    Stops after max_parts to avoid rate limiting during development.
    """
    parts: list[GenomicPart] = []
    seen_capabilities: set[str] = set()

    for target in targets:
        if len(parts) >= max_parts:
            break

        # One representative part per capability to keep the design focused
        if target.capability in seen_capabilities:
            continue

        print(f"  Fetching {target.gene} from {target.organism} ({target.database})...", end=" ")

        try:
            if target.database == "ucsc" and target.genome:
                region = get_gene_region(target.gene, target.genome)
                seq = ""
                if region:
                    seq = fetch_sequence(
                        target.genome,
                        region["chrom"],
                        region["start"],
                        min(region["start"] + 900, region["end"]),  # cap at 900bp for dev
                    )
                part = from_ucsc(target, region, seq)

            else:
                from retrieval.ncbi_client import get_gene_sequences
                results = get_gene_sequences(target.gene, target.organism)
                if results:
                    hit = {"symbol": results[0]["symbol"],
                           "description": results[0]["description"],
                           "organism": results[0]["organism"],
                           "source": "gene"}
                    part = from_ncbi(target, hit, sequence=results[0].get("sequence", ""))
                else:
                    hits = search_gene(target.gene, target.organism, max_results=1)
                    if not hits:
                        print("not found, skipping.")
                        continue
                    part = from_ncbi(target, hits[0], sequence="")

            parts.append(part)
            seen_capabilities.add(target.capability)
            print(f"ok ({len(part.dna_sequence)}bp)")

        except Exception as e:
            print(f"error: {e}")
            continue

    return parts


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run(description: str, chassis: str = DEFAULT_CHASSIS) -> None:
    """
    Full pipeline: description → designed construct + output files.
    """
    print(f"\n{'='*55}")
    print(f"  Adaptive Genome Design System")
    print(f"{'='*55}")
    print(f"  Input:   {description}")
    print(f"  Chassis: {chassis}")
    print()

    # Step 1: Interpret description
    print("[ 1/4 ] Interpreting functional description...")
    targets = interpret(description)
    if not targets:
        print("  No capabilities matched. Try keywords like:")
        print("  structural, repair, grow, cellulose, silk, thermal, light, mineral")
        return
    summarize(targets)

    # Step 2: Retrieve genomic parts
    print("[ 2/4 ] Retrieving genomic parts...")
    parts = retrieve_parts(targets)
    if not parts:
        print("  No parts retrieved. Check network connection or try different keywords.")
        return
    print(f"  Retrieved {len(parts)} part(s).\n")

    # Step 3: Adaptive assembly
    print("[ 3/4 ] Running adaptive assembly...")
    print(f"  → Pathway compatibility analysis")
    print(f"  → Regulatory element adaptation")
    print(f"  → Codon optimization")
    result = assemble(parts, target_organism=chassis)
    print(f"  Assembly complete.\n")

    # Step 4: Write outputs
    print("[ 4/4 ] Writing outputs...")
    run_name = description[:40]
    out_dir = write_outputs(result, run_name=run_name, base_dir=OUTPUT_DIR)

    # Final summary
    print_summary(result, out_dir)


# ---------------------------------------------------------------------------
# Example designs
# ---------------------------------------------------------------------------

EXAMPLE_DESIGNS = {
    "1": (
        "grow a load-bearing structure that self-repairs",
        "ganoderma",
    ),
    "2": (
        "strong flexible sheets that grow into organic shapes",
        "ganoderma",
    ),
    "3": (
        "a wall that hardens over time and regulates temperature",
        "ganoderma",
    ),
    "4": (
        "something that glows and repairs damage to itself",
        "yeast",
    ),
}


def main():
    print("\nAdaptive Genome Design System")
    print("Building living architecture one pathway at a time.\n")
    print("Example designs:")
    for key, (desc, chassis) in EXAMPLE_DESIGNS.items():
        print(f"  [{key}] {desc}  (chassis: {chassis})")
    print()

    choice = input("Enter example number or type your own description: ").strip()

    if choice in EXAMPLE_DESIGNS:
        description, chassis = EXAMPLE_DESIGNS[choice]
    else:
        description = choice
        chassis = input(f"Target chassis organism [{DEFAULT_CHASSIS}]: ").strip() or DEFAULT_CHASSIS

    run(description, chassis)


if __name__ == "__main__":
    main()

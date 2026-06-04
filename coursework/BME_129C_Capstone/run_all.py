"""
Living Systems as Decentralized Economies
==========================================
Master script — runs all three layers of analysis.

BME 129C Capstone, Sage Clokey, Spring 2026, UC Santa Cruz

Usage:
    python run_all.py              # run everything
    python run_all.py --layer 1    # run only Layer 1 (topology)
    python run_all.py --layer 1m   # run only Layer 1 motif analysis (Alon)
    python run_all.py --layer 1s   # run only Layer 1 self-regulation (WBPA)
    python run_all.py --layer 1b   # run only Layer 1b (single-cell)
    python run_all.py --layer 2    # run only Layer 2 (economic modeling)
    python run_all.py --layer 2p   # run only Layer 2 perturbation suite
    python run_all.py --layer 3    # run only Layer 3 (trade network)
    python run_all.py --quick      # quick mode (skip API calls, use cached/built-in data)
"""

import argparse
import sys
from pathlib import Path

# Ensure project root is on path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))


def run_layer1(quick: bool = False):
    """Layer 1: Network Topology — No Master Node"""
    print()
    print("=" * 70)
    print("  LAYER 1: NETWORK TOPOLOGY — 'No Master Node'")
    print("=" * 70)
    print()

    from layer1_topology.network_fetcher import load_all_networks, fetch_regulondb_grn
    from layer1_topology.topology_analysis import analyze_topology, plot_topology_report
    from layer1_topology.centralized_comparison import build_comparison_networks

    if quick:
        # Use built-in fallback (no API calls)
        from layer1_topology.network_fetcher import _builtin_ecoli_grn
        networks = {"ecoli_grn": _builtin_ecoli_grn()}
    else:
        networks = load_all_networks()

    # Analyze biological networks
    bio_reports = []
    for name, G in networks.items():
        print(f"\nAnalyzing {name}...")
        report = analyze_topology(G, name=name)
        bio_reports.append(report)
        print(report.summary())

    # Build and analyze comparison networks
    ref_n = max(G.number_of_nodes() for G in networks.values())
    ref_m = max(G.number_of_edges() for G in networks.values())
    ref_networks = build_comparison_networks(n_nodes=ref_n, n_edges=ref_m)

    ref_reports = []
    for name, G in ref_networks.items():
        print(f"\nAnalyzing reference: {name}...")
        report = analyze_topology(G, name=name)
        ref_reports.append(report)
        print(report.summary())

    # Plot
    print("\nGenerating Layer 1 figures...")
    plot_topology_report(bio_reports, ref_reports)

    return bio_reports, ref_reports, networks


def run_layer1_motifs(quick: bool = False):
    """Layer 1 — Motif Analysis (Alon): Feed-forward loops as Hayekian price signals"""
    print()
    print("=" * 70)
    print("  LAYER 1 MOTIFS: NETWORK GRAMMAR — 'Feed-Forward Loops' (Alon 2002)")
    print("=" * 70)
    print()

    from layer1_topology.network_fetcher import fetch_regulondb_grn, _builtin_ecoli_grn
    from layer1_topology.motif_analysis import run_motif_analysis, plot_motif_analysis

    if quick:
        G = _builtin_ecoli_grn()
        n_random = 100  # fewer randomizations for quick mode
    else:
        G = fetch_regulondb_grn()
        n_random = 1000

    report = run_motif_analysis(G, n_random=n_random)
    print()
    print(report.summary())

    print("\nGenerating motif figures...")
    plot_motif_analysis(report)

    return report


def run_layer1_self_regulation(quick: bool = False):
    """Layer 1 — Self-Regulation (WBPA): Networks resist centralization"""
    print()
    print("=" * 70)
    print("  LAYER 1 SELF-REGULATION — 'Invisible Hand in Topology' (WBPA)")
    print("=" * 70)
    print()

    from layer1_topology.network_fetcher import load_all_networks, _builtin_ecoli_grn
    from layer1_topology.centralized_comparison import build_comparison_networks
    from layer1_topology.self_regulation import (
        compute_self_regulation, plot_self_regulation,
    )

    if quick:
        networks = {"ecoli_grn": _builtin_ecoli_grn()}
    else:
        networks = load_all_networks()

    # Analyze biological networks
    bio_reports = []
    bio_graphs = {}
    for name, G in networks.items():
        print(f"\nAnalyzing self-regulation: {name}...")
        report = compute_self_regulation(G, name=name)
        bio_reports.append(report)
        bio_graphs[name] = G
        print(report.summary())

    # Build and analyze comparison networks
    ref_n = max(G.number_of_nodes() for G in networks.values())
    ref_m = max(G.number_of_edges() for G in networks.values())
    ref_networks = build_comparison_networks(n_nodes=ref_n, n_edges=ref_m)

    ref_reports = []
    ref_graphs = {}
    for name, G in ref_networks.items():
        print(f"\nAnalyzing self-regulation: {name}...")
        report = compute_self_regulation(G, name=name)
        ref_reports.append(report)
        ref_graphs[name] = G
        print(report.summary())

    print("\nGenerating self-regulation figures...")
    plot_self_regulation(bio_reports, ref_reports)

    return bio_reports, ref_reports


def run_layer1b():
    """Layer 1b: Single-Cell Economy — Cells as Economic Agents"""
    print()
    print("=" * 70)
    print("  LAYER 1b: SINGLE-CELL ECONOMY — 'Cells as Economic Agents'")
    print("=" * 70)
    print()

    from layer1_topology.single_cell_economy import (
        load_pbmc_data, analyze_cell_economy,
        _build_communication_network, _build_directed_communication_network,
        plot_cell_economy,
    )
    from layer1_topology.cell_economy_figures import (
        plot_directed_communication, plot_comparative_advantage,
        plot_robustness_comparison, plot_price_signals,
    )

    adata = load_pbmc_data("scanpy")
    report = analyze_cell_economy(adata)
    print()
    print(report.summary())

    # Build communication graphs for visualization
    cell_types = sorted(adata.obs["cell_type"].astype(str).unique())
    comm_graph = _build_communication_network(adata, cell_types)
    directed_graph = _build_directed_communication_network(adata, cell_types)

    print("\nGenerating Layer 1b figures...")
    plot_cell_economy(adata, report, comm_graph)

    # New Austrian economics figures
    print("Generating directed communication figure (voluntary exchange)...")
    plot_directed_communication(directed_graph)

    if report.comparative_advantage:
        print("Generating comparative advantage heatmap (Menger)...")
        plot_comparative_advantage(report.comparative_advantage)

    if hasattr(report, 'distributed_robustness_mean') and report.distributed_robustness_mean > 0:
        from layer1_topology.single_cell_economy import (
            _build_star_communication_network, _compare_robustness,
        )
        star_graph = _build_star_communication_network(cell_types, cell_types[0])
        comparison = _compare_robustness(directed_graph, star_graph, cell_types)
        print("Generating robustness comparison (Rothbard)...")
        plot_robustness_comparison(comparison, cell_types)

    if report.price_signals:
        print("Generating price signal diagram (subjective value)...")
        plot_price_signals(report.price_signals)

    print("\nRobustness (fraction of communication surviving cell type removal):")
    for ct, score in sorted(report.robustness_scores.items(), key=lambda x: x[1]):
        print(f"  Remove {ct}: {score:.1%} edges survive")

    return report


def run_layer2():
    """Layer 2: Economic Modeling — Pathways as Agents"""
    print()
    print("=" * 70)
    print("  LAYER 2: ECONOMIC MODELING — 'Pathways as Agents'")
    print("=" * 70)
    print()

    from layer2_economy.metabolic_economy import (
        run_distributed, run_centralized, run_centralized_smart,
        run_perturbation_test, compare_regimes, plot_economy,
        run_perturbation_suite, plot_perturbation_suite,
    )

    base_supply = {
        "UDP-glucose": 1.0, "UDP-GlcNAc": 0.5, "Ca2+": 0.5,
        "O2": 2.0, "luciferin": 0.3, "glycine": 1.0,
        "alanine": 1.0, "glutamine": 0.5, "piRNA_precursors": 0.2,
        "Zn2+": 0.2, "cholesterol": 0.3,
    }

    print("Running distributed simulation...")
    dist = run_distributed(n_steps=200, base_supply=base_supply)

    print("Running centralized simulation...")
    cent = run_centralized(n_steps=200, base_supply=base_supply)

    print("Running smart centralized simulation (Mises' strongest opponent)...")
    cent_smart = run_centralized_smart(n_steps=200, base_supply=base_supply)

    print()
    print(compare_regimes(dist, cent))

    print("\nRunning perturbation test...")
    robustness = run_perturbation_test(n_steps=100)

    print("\nRobustness (GDP fraction retained after removing one agent):")
    print(f"{'Pathway Removed':<35} {'Distributed':>12} {'Centralized':>12}")
    print("-" * 60)
    for pathway_name in robustness["distributed"]:
        d = robustness["distributed"][pathway_name]
        c = robustness["centralized"][pathway_name]
        print(f"{pathway_name:<35} {d:>11.1%} {c:>11.1%}")

    print("\nGenerating Layer 2 figures...")
    plot_economy(dist, cent, robustness)

    return dist, cent, robustness


def run_layer2_perturbation():
    """Layer 2 Extended: Perturbation Suite — Hayek, Mises, Kirzner"""
    print()
    print("=" * 70)
    print("  LAYER 2 PERTURBATION SUITE — 'The Calculation Problem Measured'")
    print("=" * 70)
    print()

    from layer2_economy.metabolic_economy import (
        run_perturbation_suite, plot_perturbation_suite,
    )

    print("Running perturbation suite (4 tests × 3 regimes)...")
    print("  (a) Substrate shock — Hayek's knowledge problem")
    print("  (b) ATP crisis — Mises' calculation problem")
    print("  (c) Demand spike — Kirzner's entrepreneurial discovery")
    print("  (d) Novel opportunity — Kirzner's alertness")
    suite = run_perturbation_suite()

    print("\nGenerating perturbation suite figures...")
    plot_perturbation_suite(suite)

    return suite


def run_layer2_fba():
    """Layer 2 FBA: The Omniscient Planner vs the Market (iML1515)"""
    print()
    print("=" * 70)
    print("  LAYER 2 FBA: OMNISCIENT PLANNER vs DISTRIBUTED REGULATION")
    print("  (iML1515 — 2,712 reactions, 1,877 metabolites, 1,516 genes)")
    print("=" * 70)
    print()

    from layer2_economy.fba_analysis import (
        run_fba_analysis, plot_fba_analysis,
        run_fba_perturbation, plot_fba_perturbation,
    )

    report = run_fba_analysis()
    print()
    print(report.summary())

    print("\nGenerating FBA analysis figures...")
    plot_fba_analysis(report)

    print("\nRunning FBA perturbation tests...")
    perturbation = run_fba_perturbation()
    for pname, pdata in perturbation.items():
        print(f"  {pname}: growth ratio = {pdata['growth_ratio']:.1%}")
        print(f"    {pdata['biological_reality'][:80]}...")

    print("\nGenerating FBA perturbation figures...")
    plot_fba_perturbation(perturbation)

    return report, perturbation


def run_layer3():
    """Layer 3: Cross-Species Trade — Comparative Advantage"""
    print()
    print("=" * 70)
    print("  LAYER 3: CROSS-SPECIES TRADE — 'Comparative Advantage'")
    print("=" * 70)
    print()

    from layer3_trade.trade_network import (
        build_trade_network, compute_trade_matrix,
        comparative_advantage_table, plot_trade_network,
        analyze_voluntary_exchange, plot_voluntary_exchange,
        detect_trade_blocs, plot_trade_blocs,
    )

    G = build_trade_network()
    print(f"Trade network: {G.number_of_nodes()} organisms, {G.number_of_edges()} trade links")

    names, matrix = compute_trade_matrix()
    print(f"\nTrade Cost Matrix ({len(names)} organisms):")
    print(f"{'':>18}", end="")
    for n in names:
        print(f"{n:>14}", end="")
    print()
    for i, n in enumerate(names):
        print(f"{n:>18}", end="")
        for j in range(len(names)):
            print(f"{matrix[i, j]:>14.3f}", end="")
        print()

    print("\nComparative Advantage:")
    for org, caps in comparative_advantage_table().items():
        print(f"  {org}: {', '.join(caps)}")

    print("\nFree Trade Zones (lowest cost pairs):")
    pairs = []
    for u, v, data in G.edges(data=True):
        pairs.append((u, v, data["trade_cost"]))
    pairs.sort(key=lambda x: x[2])
    for u, v, tc in pairs[:5]:
        print(f"  {u} <-> {v}: cost={tc:.3f}")

    print("\nGenerating Layer 3 figures...")
    plot_trade_network()

    # Rothbardian voluntary exchange analysis
    print("\nAnalyzing voluntary exchange vs coercion (Rothbard)...")
    ve_report = analyze_voluntary_exchange()
    print(ve_report.summary())
    print("\nGenerating voluntary exchange figure...")
    plot_voluntary_exchange(ve_report)

    # Trade blocs (spontaneous order)
    print("\nDetecting spontaneous trade blocs (Menger)...")
    communities = detect_trade_blocs(G)
    for cid, members in communities.items():
        print(f"  Bloc {cid}: {', '.join(members)}")
    print("Generating trade blocs figure...")
    plot_trade_blocs(G, communities)

    return G, names, matrix


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Living Systems as Decentralized Economies — BME 129C Capstone",
    )
    parser.add_argument(
        "--layer", type=str, default="all",
        choices=["all", "1", "1m", "1s", "1b", "2", "2p", "2f", "2price", "3"],
        help="Which layer to run (default: all). 1m=motifs, 1s=self-regulation, 2p=perturbation suite, 2f=FBA analysis, 2price=price system figure",
    )
    parser.add_argument(
        "--quick", action="store_true",
        help="Quick mode: use built-in data, skip API calls",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("  LIVING SYSTEMS AS DECENTRALIZED ECONOMIES")
    print("  BME 129C Capstone — Sage Clokey — Spring 2026")
    print("=" * 70)

    if args.layer in ("all", "1"):
        run_layer1(quick=args.quick)

    if args.layer in ("all", "1m"):
        run_layer1_motifs(quick=args.quick)

    if args.layer in ("all", "1s"):
        run_layer1_self_regulation(quick=args.quick)

    if args.layer in ("all", "1b"):
        run_layer1b()

    if args.layer in ("all", "2"):
        run_layer2()

    if args.layer in ("all", "2p"):
        run_layer2_perturbation()

    if args.layer in ("all", "2f"):
        run_layer2_fba()

    if args.layer in ("all", "2price"):
        print()
        print("=" * 70)
        print("  LAYER 2 PRICE SYSTEM: 'The Price System of the Cell'")
        print("=" * 70)
        print()
        from paper.builders.generate_price_system_figure import generate_price_system_figure
        generate_price_system_figure()

    if args.layer in ("all", "3"):
        run_layer3()

    print()
    print("=" * 70)
    print("  COMPLETE")
    print("  Figures saved to: paper/figures/")
    print("=" * 70)


if __name__ == "__main__":
    main()

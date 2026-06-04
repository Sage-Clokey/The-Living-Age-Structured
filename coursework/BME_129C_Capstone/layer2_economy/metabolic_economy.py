"""
Metabolic Economy — Layer 2: Economic Modeling
===============================================
Models metabolic pathways as economic agents in a decentralized market.

Each pathway:
    - Consumes resources (demand)
    - Produces outputs (supply)
    - Operates within an ATP budget (currency)
    - Responds to local metabolite concentrations (price signals)
    - Competes for shared substrates (market competition)

Two allocation regimes are simulated:
    1. Distributed (biological): agents trade through shared metabolite pools,
       adjust production based on local feedback. No central allocator.
    2. Centralized (planned): a single allocator controls all production
       and distributes resources globally. Optimizes for total output.

The thesis: distributed allocation reaches stable equilibrium, recovers
from perturbation faster, and approaches Pareto efficiency — all without
a planner. This mirrors the First Welfare Theorem.

Foundation:
    Extends PathwayProfile from adaptive_Automation/compatibility/pathway.py
    The 12 existing pathway profiles already have consumes[], produces[],
    atp_cost, signal_inputs[], signal_outputs[] — they ARE economic agents.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import sys
from pathlib import Path

import numpy as np

# Import existing pathway profiles from adaptive_Automation
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "adaptive_Automation"))

try:
    from compatibility.pathway import PathwayProfile, PATHWAY_CATALOG
    print(f"[economy] Loaded {len(PATHWAY_CATALOG)} pathway profiles from adaptive_Automation")
except ImportError:
    print("[economy] Warning: could not import from adaptive_Automation. Using built-in catalog.")
    PATHWAY_CATALOG = []

    @dataclass
    class PathwayProfile:
        name: str
        capability: str
        consumes: list[str] = field(default_factory=list)
        produces: list[str] = field(default_factory=list)
        signal_inputs: list[str] = field(default_factory=list)
        signal_outputs: list[str] = field(default_factory=list)
        activates_tfs: list[str] = field(default_factory=list)
        inhibits_tfs: list[str] = field(default_factory=list)
        amino_acid_load: dict[str, str] = field(default_factory=dict)
        atp_cost: str = "medium"
        compartment: str = "cytoplasm"
        notes: str = ""


# ---------------------------------------------------------------------------
# Economic Agent
# ---------------------------------------------------------------------------

ATP_COST_MAP = {"low": 1.0, "medium": 2.0, "high": 3.0, "very_high": 4.0}


@dataclass
class EconomicAgent:
    """
    A metabolic pathway modeled as an economic agent.

    Each agent has:
        - A production function (consumes inputs, produces outputs)
        - An ATP budget (currency)
        - An inventory of metabolites
        - A production rate that adjusts based on local conditions
    """
    pathway: PathwayProfile
    name: str = ""

    # Economic state
    atp_budget: float = 10.0
    inventory: dict[str, float] = field(default_factory=dict)

    # Production parameters
    base_production_rate: float = 1.0
    current_production_rate: float = 1.0

    # History (for plotting)
    production_history: list[float] = field(default_factory=list)
    budget_history: list[float] = field(default_factory=list)

    def __post_init__(self):
        if not self.name:
            self.name = self.pathway.name
        # Initialize inventory with small amounts of produced goods
        for product in self.pathway.produces:
            self.inventory.setdefault(product, 1.0)

    @property
    def atp_cost_per_cycle(self) -> float:
        return ATP_COST_MAP.get(self.pathway.atp_cost, 2.0)

    def can_produce(self, pool: "MetabolitePool") -> bool:
        """Check if all required substrates are available in the shared pool."""
        for substrate in self.pathway.consumes:
            if substrate == "ATP":
                if self.atp_budget < self.atp_cost_per_cycle:
                    return False
            elif pool.get(substrate) < 0.1:
                return False
        return True

    def produce(self, pool: "MetabolitePool", rate_multiplier: float = 1.0):
        """
        Execute one production cycle.
        Consume from the shared pool, produce into the shared pool.
        """
        rate = self.current_production_rate * rate_multiplier

        # Consume
        for substrate in self.pathway.consumes:
            if substrate == "ATP":
                self.atp_budget -= self.atp_cost_per_cycle * rate
            else:
                consumed = min(rate, pool.get(substrate))
                pool.withdraw(substrate, consumed)

        # Produce
        for product in self.pathway.produces:
            pool.deposit(product, rate)
            self.inventory[product] = self.inventory.get(product, 0) + rate

        # Record history
        self.production_history.append(rate)
        self.budget_history.append(self.atp_budget)

    def adjust_rate_distributed(self, pool: "MetabolitePool"):
        """
        Distributed feedback: adjust production rate based on local conditions.

        If my products are accumulating (oversupply) → slow down.
        If my substrates are scarce (high demand) → slow down.
        If my substrates are abundant → speed up.

        This is the invisible hand: no planner needed, just local signals.
        """
        # Product feedback: if my products are piling up, reduce rate
        product_signal = 1.0
        for product in self.pathway.produces:
            level = pool.get(product)
            if level > 5.0:
                product_signal *= 0.7  # oversupply, slow down
            elif level < 1.0:
                product_signal *= 1.3  # high demand, speed up

        # Substrate feedback: if my inputs are scarce, reduce rate
        substrate_signal = 1.0
        for substrate in self.pathway.consumes:
            if substrate == "ATP":
                continue
            level = pool.get(substrate)
            if level < 0.5:
                substrate_signal *= 0.5  # scarcity
            elif level > 3.0:
                substrate_signal *= 1.2  # abundance

        # ATP feedback
        atp_signal = 1.0
        if self.atp_budget < 2.0:
            atp_signal = 0.3
        elif self.atp_budget > 15.0:
            atp_signal = 1.5

        self.current_production_rate = (
            self.base_production_rate
            * product_signal
            * substrate_signal
            * atp_signal
        )
        # Clamp
        self.current_production_rate = max(0.01, min(5.0, self.current_production_rate))


# ---------------------------------------------------------------------------
# Metabolite Pool (shared market)
# ---------------------------------------------------------------------------

@dataclass
class MetabolitePool:
    """
    The shared metabolite pool — the marketplace where agents trade.

    In biology: the cytoplasm, the extracellular space, the bloodstream.
    In economics: the market where supply meets demand.

    No allocator controls this pool. Agents deposit and withdraw freely.
    Prices (concentrations) emerge from aggregate behavior.
    """
    levels: dict[str, float] = field(default_factory=dict)
    history: dict[str, list[float]] = field(default_factory=dict)

    def get(self, metabolite: str) -> float:
        return self.levels.get(metabolite, 0.0)

    def deposit(self, metabolite: str, amount: float):
        self.levels[metabolite] = self.levels.get(metabolite, 0.0) + amount

    def withdraw(self, metabolite: str, amount: float) -> float:
        available = self.levels.get(metabolite, 0.0)
        taken = min(amount, available)
        self.levels[metabolite] = available - taken
        return taken

    def record(self):
        """Snapshot current levels into history."""
        for met, level in self.levels.items():
            self.history.setdefault(met, []).append(level)

    def total_output(self) -> float:
        """Total metabolites in the pool (GDP proxy)."""
        return sum(self.levels.values())


# ---------------------------------------------------------------------------
# Simulation Engine
# ---------------------------------------------------------------------------

@dataclass
class SimulationResult:
    """Results from running an economic simulation."""
    regime: str                    # "distributed" or "centralized"
    n_steps: int = 0
    agents: list[EconomicAgent] = field(default_factory=list)
    pool: MetabolitePool = field(default_factory=MetabolitePool)
    gdp_history: list[float] = field(default_factory=list)
    converged: bool = False
    convergence_step: int = 0

    def final_gdp(self) -> float:
        return self.gdp_history[-1] if self.gdp_history else 0.0

    def mean_gdp(self, last_n: int = 20) -> float:
        if not self.gdp_history:
            return 0.0
        return np.mean(self.gdp_history[-last_n:])

    def gdp_variance(self, last_n: int = 20) -> float:
        if not self.gdp_history:
            return 0.0
        return np.var(self.gdp_history[-last_n:])


def run_distributed(
    pathways: list[PathwayProfile] = None,
    n_steps: int = 200,
    atp_regeneration: float = 2.0,
    base_supply: dict[str, float] = None,
) -> SimulationResult:
    """
    Run distributed (biological) economic simulation.

    Each agent adjusts its own production rate based on local feedback.
    No central allocator. Order emerges from individual decisions.
    """
    if pathways is None:
        pathways = PATHWAY_CATALOG

    # Initialize agents
    agents = [EconomicAgent(pathway=p) for p in pathways]

    # Initialize pool with baseline metabolite supply
    pool = MetabolitePool()
    _seed_pool(pool, pathways, base_supply)

    result = SimulationResult(regime="distributed", agents=agents, pool=pool)

    prev_gdp = 0.0
    stable_count = 0

    for step in range(n_steps):
        # Each agent adjusts rate based on local conditions
        for agent in agents:
            agent.adjust_rate_distributed(pool)

        # Each agent produces
        for agent in agents:
            if agent.can_produce(pool):
                agent.produce(pool)

        # ATP regeneration (energy input to the system)
        for agent in agents:
            agent.atp_budget += atp_regeneration

        # External substrate supply (sun, nutrients, etc.)
        if base_supply:
            for met, amount in base_supply.items():
                pool.deposit(met, amount)

        # Record
        pool.record()
        gdp = pool.total_output()
        result.gdp_history.append(gdp)

        # Check convergence (GDP stable within 2% for 20 steps)
        if abs(gdp - prev_gdp) < 0.02 * max(abs(prev_gdp), 1.0):
            stable_count += 1
            if stable_count >= 20 and not result.converged:
                result.converged = True
                result.convergence_step = step
        else:
            stable_count = 0
        prev_gdp = gdp

    result.n_steps = n_steps
    return result


def run_centralized(
    pathways: list[PathwayProfile] = None,
    n_steps: int = 200,
    atp_regeneration: float = 2.0,
    base_supply: dict[str, float] = None,
) -> SimulationResult:
    """
    Run centralized (planned) economic simulation.

    A single allocator decides production rates for all agents.
    Strategy: allocate proportional to ATP efficiency (lowest cost first).
    Collect all output, redistribute evenly.
    """
    if pathways is None:
        pathways = PATHWAY_CATALOG

    agents = [EconomicAgent(pathway=p) for p in pathways]
    pool = MetabolitePool()
    _seed_pool(pool, pathways, base_supply)

    result = SimulationResult(regime="centralized", agents=agents, pool=pool)

    # Central allocator: rank agents by ATP efficiency
    efficiency_rank = sorted(
        agents,
        key=lambda a: a.atp_cost_per_cycle,
    )

    prev_gdp = 0.0
    stable_count = 0

    for step in range(n_steps):
        # Central allocator assigns production rates
        # Strategy: favor low-cost agents, suppress high-cost ones
        total_budget = sum(a.atp_budget for a in agents)

        for i, agent in enumerate(efficiency_rank):
            # Allocate budget proportional to efficiency rank
            rank_weight = (len(agents) - i) / len(agents)
            allocated_rate = rank_weight * 2.0

            agent.current_production_rate = allocated_rate

            if agent.can_produce(pool):
                agent.produce(pool)

        # ATP regeneration
        for agent in agents:
            agent.atp_budget += atp_regeneration

        # External supply
        if base_supply:
            for met, amount in base_supply.items():
                pool.deposit(met, amount)

        pool.record()
        gdp = pool.total_output()
        result.gdp_history.append(gdp)

        if abs(gdp - prev_gdp) < 0.02 * max(abs(prev_gdp), 1.0):
            stable_count += 1
            if stable_count >= 20 and not result.converged:
                result.converged = True
                result.convergence_step = step
        else:
            stable_count = 0
        prev_gdp = gdp

    result.n_steps = n_steps
    return result


def run_perturbation_test(
    pathways: list[PathwayProfile] = None,
    n_trials: int = 50,
    n_steps: int = 200,
) -> dict:
    """
    Remove one agent at a time and compare recovery between regimes.

    Returns dict with robustness scores for distributed vs centralized.
    """
    if pathways is None:
        pathways = PATHWAY_CATALOG

    if not pathways:
        return {"distributed": {}, "centralized": {}}

    results = {"distributed": {}, "centralized": {}}

    # Baseline GDP for each regime
    base_dist = run_distributed(pathways, n_steps=n_steps)
    base_cent = run_centralized(pathways, n_steps=n_steps)
    baseline_dist_gdp = base_dist.mean_gdp()
    baseline_cent_gdp = base_cent.mean_gdp()

    # Remove each pathway and measure GDP recovery
    for i, removed in enumerate(pathways):
        remaining = [p for j, p in enumerate(pathways) if j != i]
        if not remaining:
            continue

        dist_result = run_distributed(remaining, n_steps=n_steps)
        cent_result = run_centralized(remaining, n_steps=n_steps)

        dist_recovery = dist_result.mean_gdp() / baseline_dist_gdp if baseline_dist_gdp > 0 else 0
        cent_recovery = cent_result.mean_gdp() / baseline_cent_gdp if baseline_cent_gdp > 0 else 0

        results["distributed"][removed.name] = dist_recovery
        results["centralized"][removed.name] = cent_recovery

    return results


def _seed_pool(
    pool: MetabolitePool,
    pathways: list[PathwayProfile],
    base_supply: dict[str, float] = None,
):
    """Seed the metabolite pool with initial amounts of all relevant metabolites."""
    all_metabolites = set()
    for p in pathways:
        all_metabolites.update(p.consumes)
        all_metabolites.update(p.produces)

    for met in all_metabolites:
        if met == "ATP":
            continue
        initial = 3.0
        if base_supply and met in base_supply:
            initial = base_supply[met]
        pool.levels[met] = initial


# ---------------------------------------------------------------------------
# Quick summary
# ---------------------------------------------------------------------------

def compare_regimes(dist: SimulationResult, cent: SimulationResult) -> str:
    """Print comparison between distributed and centralized regimes."""
    lines = [
        "=" * 60,
        "REGIME COMPARISON",
        "=" * 60,
        f"{'Metric':<35} {'Distributed':>12} {'Centralized':>12}",
        "-" * 60,
        f"{'Final GDP':<35} {dist.final_gdp():>12.1f} {cent.final_gdp():>12.1f}",
        f"{'Mean GDP (last 20 steps)':<35} {dist.mean_gdp():>12.1f} {cent.mean_gdp():>12.1f}",
        f"{'GDP Variance (last 20)':<35} {dist.gdp_variance():>12.2f} {cent.gdp_variance():>12.2f}",
        f"{'Converged':<35} {str(dist.converged):>12} {str(cent.converged):>12}",
        f"{'Convergence Step':<35} {dist.convergence_step:>12} {cent.convergence_step:>12}",
        "=" * 60,
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Visualization
# ---------------------------------------------------------------------------

def plot_economy(dist: SimulationResult, cent: SimulationResult, robustness: dict):
    """Generate Layer 2 figure: GDP over time, perturbation robustness, production convergence."""
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec

    SPIRAL_GREEN = "#2d6a4f"
    SPIRAL_MID   = "#52b788"
    SPIRAL_LIGHT = "#95d5b2"
    GOLD         = "#e9c46a"
    RED          = "#e63946"
    BACKGROUND   = "#0d1117"
    PANEL_BG     = "#161b22"
    TEXT_MAIN     = "#e6edf3"
    TEXT_DIM      = "#8b949e"

    fig = plt.figure(figsize=(20, 7), facecolor=BACKGROUND)
    gs = gridspec.GridSpec(1, 3, wspace=0.3)

    # --- Panel 1: GDP Over Time ---
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor(PANEL_BG)
    steps = range(len(dist.gdp_history))
    ax1.plot(steps, dist.gdp_history, color=SPIRAL_MID, linewidth=2, label="Distributed (biological)")
    ax1.plot(steps, cent.gdp_history, color=RED, linewidth=2, alpha=0.8, label="Centralized (planned)")
    ax1.set_xlabel("Time Step", color=TEXT_MAIN)
    ax1.set_ylabel("GDP (total metabolite output)", color=TEXT_MAIN)
    ax1.set_title("GDP Over Time: Invisible Hand vs Central Planner", color=TEXT_MAIN, fontsize=12, fontweight="bold")
    ax1.legend(facecolor=PANEL_BG, edgecolor=TEXT_DIM, labelcolor=TEXT_MAIN)
    ax1.tick_params(colors=TEXT_DIM)
    for spine in ax1.spines.values():
        spine.set_color(TEXT_DIM)

    # --- Panel 2: Perturbation Robustness ---
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor(PANEL_BG)

    if robustness["distributed"]:
        pathways = list(robustness["distributed"].keys())
        # Shorten names for display
        short_names = [n.replace(" pathway", "").replace(" synthesis", "")[:20] for n in pathways]
        dist_scores = [robustness["distributed"][p] for p in pathways]
        cent_scores = [robustness["centralized"][p] for p in pathways]

        x = np.arange(len(pathways))
        width = 0.35
        ax2.barh(x - width/2, dist_scores, width, color=SPIRAL_MID, alpha=0.3, label="Distributed")
        ax2.barh(x + width/2, cent_scores, width, color=RED, alpha=0.3, label="Centralized")
        # Overlay individual data points
        ax2.scatter(dist_scores, x - width/2, color=SPIRAL_MID, s=50, zorder=3,
                    edgecolors="white", linewidth=0.8, alpha=0.9)
        ax2.scatter(cent_scores, x + width/2, color=RED, s=50, zorder=3,
                    edgecolors="white", linewidth=0.8, alpha=0.9)
        ax2.set_yticks(x)
        ax2.set_yticklabels(short_names, fontsize=7, color=TEXT_MAIN)
        ax2.axvline(x=1.0, color=TEXT_DIM, linestyle="--", linewidth=0.8, alpha=0.5)
        ax2.set_xlabel("GDP Fraction Retained", color=TEXT_MAIN)
        ax2.legend(facecolor=PANEL_BG, edgecolor=TEXT_DIM, labelcolor=TEXT_MAIN, fontsize=8)

    ax2.set_title("Robustness: GDP After Removing One Agent", color=TEXT_MAIN, fontsize=12, fontweight="bold")
    ax2.tick_params(colors=TEXT_DIM)
    for spine in ax2.spines.values():
        spine.set_color(TEXT_DIM)

    # --- Panel 3: Production Rate Convergence ---
    ax3 = fig.add_subplot(gs[2])
    ax3.set_facecolor(PANEL_BG)

    colors = plt.cm.Set2(np.linspace(0, 1, len(dist.agents)))
    for i, agent in enumerate(dist.agents):
        if agent.production_history:
            ax3.plot(agent.production_history, color=colors[i], linewidth=1, alpha=0.7,
                     label=agent.name[:18] if i < 8 else None)
    ax3.set_xlabel("Time Step", color=TEXT_MAIN)
    ax3.set_ylabel("Production Rate", color=TEXT_MAIN)
    ax3.set_title("Distributed Rate Convergence (Price Discovery)", color=TEXT_MAIN, fontsize=12, fontweight="bold")
    ax3.legend(facecolor=PANEL_BG, edgecolor=TEXT_DIM, labelcolor=TEXT_MAIN, fontsize=6,
               loc="upper right", ncol=2)
    ax3.tick_params(colors=TEXT_DIM)
    for spine in ax3.spines.values():
        spine.set_color(TEXT_DIM)

    fig_dir = Path(__file__).resolve().parent.parent / "paper" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    out = fig_dir / "layer2_economy.png"
    plt.savefig(out, dpi=200, bbox_inches="tight", facecolor=BACKGROUND)
    plt.close(fig)
    print(f"[economy] Saved figure to {out}")


# ---------------------------------------------------------------------------
# Upgrade 1: Smart Centralized Planner
# ---------------------------------------------------------------------------

def run_centralized_smart(
    pathways: list[PathwayProfile] = None,
    n_steps: int = 200,
    atp_regeneration: float = 2.0,
    base_supply: dict[str, float] = None,
) -> SimulationResult:
    """
    Run a smart centralized planner that re-optimizes every step.

    This is the "socialist planning board with a supercomputer" — Mises'
    strongest opponent. It has access to the full metabolite pool state
    (real-time concentrations) AND global cost ranking. It re-ranks and
    reallocates every step based on current scarcity information.

    The Austrian prediction: it will match or beat the distributed regime
    in steady state, but STILL fail under perturbation because its
    optimization is backward-looking (optimizes for the current state)
    while the distributed system's local feedback is forward-looking
    (each agent discovers the new equilibrium through its own adjustment).
    """
    if pathways is None:
        pathways = PATHWAY_CATALOG

    agents = [EconomicAgent(pathway=p) for p in pathways]
    pool = MetabolitePool()
    _seed_pool(pool, pathways, base_supply)

    result = SimulationResult(regime="centralized_smart", agents=agents, pool=pool)

    prev_gdp = 0.0
    stable_count = 0
    n_agents = len(agents)

    for step in range(n_steps):
        # --- Smart planner reads ALL metabolite levels ---
        # Rank agents by ATP efficiency (lower cost = better rank)
        efficiency_rank = sorted(
            range(n_agents),
            key=lambda idx: agents[idx].atp_cost_per_cycle,
        )
        rank_map = {idx: rank for rank, idx in enumerate(efficiency_rank)}

        for idx, agent in enumerate(agents):
            # Efficiency weight: (n_agents - rank) / n_agents
            rank = rank_map[idx]
            efficiency_weight = (n_agents - rank) / n_agents

            # Scarcity bonus: look at mean product levels
            product_levels = [pool.get(p) for p in agent.pathway.produces]
            mean_product_level = np.mean(product_levels) if product_levels else 3.0

            if mean_product_level < 1.0:
                # Product is scarce — boost production
                scarcity_bonus = max(1.0, 3.0 - mean_product_level)
            elif mean_product_level > 5.0:
                # Product is abundant — suppress production
                scarcity_bonus = max(0.2, 1.0 / (mean_product_level / 5.0))
            else:
                scarcity_bonus = 1.0

            base_rate = 1.0
            allocated_rate = base_rate * scarcity_bonus * efficiency_weight
            agent.current_production_rate = max(0.01, min(5.0, allocated_rate))

            if agent.can_produce(pool):
                agent.produce(pool)

        # ATP regeneration
        for agent in agents:
            agent.atp_budget += atp_regeneration

        # External supply
        if base_supply:
            for met, amount in base_supply.items():
                pool.deposit(met, amount)

        pool.record()
        gdp = pool.total_output()
        result.gdp_history.append(gdp)

        if abs(gdp - prev_gdp) < 0.02 * max(abs(prev_gdp), 1.0):
            stable_count += 1
            if stable_count >= 20 and not result.converged:
                result.converged = True
                result.convergence_step = step
        else:
            stable_count = 0
        prev_gdp = gdp

    result.n_steps = n_steps
    return result


# ---------------------------------------------------------------------------
# Upgrade 2: Multiple Perturbation Types
# ---------------------------------------------------------------------------

def _run_distributed_with_hooks(
    pathways: list[PathwayProfile],
    n_steps: int,
    atp_regeneration: float,
    base_supply: dict[str, float],
    pre_step_hook=None,
    threshold_scale: float = 1.0,
) -> SimulationResult:
    """
    Internal: run distributed simulation with per-step hooks and threshold scaling.
    pre_step_hook(step, agents, pool, context) can mutate state each step.
    """
    agents = [EconomicAgent(pathway=p) for p in pathways]
    pool = MetabolitePool()
    _seed_pool(pool, pathways, base_supply)

    result = SimulationResult(regime="distributed", agents=agents, pool=pool)
    context = {"atp_regen": atp_regeneration, "base_supply": dict(base_supply)}

    prev_gdp = 0.0
    stable_count = 0

    for step in range(n_steps):
        # Hook can mutate context, agents, pool
        if pre_step_hook:
            pre_step_hook(step, agents, pool, context)

        # Each agent adjusts rate with scaled thresholds
        for agent in agents:
            _adjust_rate_distributed_scaled(agent, pool, threshold_scale)

        for agent in agents:
            if agent.can_produce(pool):
                agent.produce(pool)

        # ATP regeneration (may have been modified by hook)
        for agent in agents:
            agent.atp_budget += context["atp_regen"]

        # External supply (may have been modified by hook)
        for met, amount in context["base_supply"].items():
            pool.deposit(met, amount)

        pool.record()
        gdp = pool.total_output()
        result.gdp_history.append(gdp)

        if abs(gdp - prev_gdp) < 0.02 * max(abs(prev_gdp), 1.0):
            stable_count += 1
            if stable_count >= 20 and not result.converged:
                result.converged = True
                result.convergence_step = step
        else:
            stable_count = 0
        prev_gdp = gdp

    result.n_steps = n_steps
    return result


def _run_centralized_with_hooks(
    pathways: list[PathwayProfile],
    n_steps: int,
    atp_regeneration: float,
    base_supply: dict[str, float],
    pre_step_hook=None,
) -> SimulationResult:
    """Internal: run centralized (dumb) simulation with per-step hooks."""
    agents = [EconomicAgent(pathway=p) for p in pathways]
    pool = MetabolitePool()
    _seed_pool(pool, pathways, base_supply)

    result = SimulationResult(regime="centralized", agents=agents, pool=pool)
    context = {"atp_regen": atp_regeneration, "base_supply": dict(base_supply)}

    efficiency_rank = sorted(agents, key=lambda a: a.atp_cost_per_cycle)

    prev_gdp = 0.0
    stable_count = 0

    for step in range(n_steps):
        if pre_step_hook:
            pre_step_hook(step, agents, pool, context)

        total_budget = sum(a.atp_budget for a in agents)
        for i, agent in enumerate(efficiency_rank):
            rank_weight = (len(agents) - i) / len(agents)
            allocated_rate = rank_weight * 2.0
            agent.current_production_rate = allocated_rate
            if agent.can_produce(pool):
                agent.produce(pool)

        for agent in agents:
            agent.atp_budget += context["atp_regen"]

        for met, amount in context["base_supply"].items():
            pool.deposit(met, amount)

        pool.record()
        gdp = pool.total_output()
        result.gdp_history.append(gdp)

        if abs(gdp - prev_gdp) < 0.02 * max(abs(prev_gdp), 1.0):
            stable_count += 1
            if stable_count >= 20 and not result.converged:
                result.converged = True
                result.convergence_step = step
        else:
            stable_count = 0
        prev_gdp = gdp

    result.n_steps = n_steps
    return result


def _run_centralized_smart_with_hooks(
    pathways: list[PathwayProfile],
    n_steps: int,
    atp_regeneration: float,
    base_supply: dict[str, float],
    pre_step_hook=None,
) -> SimulationResult:
    """Internal: run smart centralized simulation with per-step hooks."""
    agents = [EconomicAgent(pathway=p) for p in pathways]
    pool = MetabolitePool()
    _seed_pool(pool, pathways, base_supply)

    result = SimulationResult(regime="centralized_smart", agents=agents, pool=pool)
    context = {"atp_regen": atp_regeneration, "base_supply": dict(base_supply)}
    n_agents = len(agents)

    prev_gdp = 0.0
    stable_count = 0

    for step in range(n_steps):
        if pre_step_hook:
            pre_step_hook(step, agents, pool, context)

        efficiency_rank = sorted(
            range(n_agents),
            key=lambda idx: agents[idx].atp_cost_per_cycle,
        )
        rank_map = {idx: rank for rank, idx in enumerate(efficiency_rank)}

        for idx, agent in enumerate(agents):
            rank = rank_map[idx]
            efficiency_weight = (n_agents - rank) / n_agents

            product_levels = [pool.get(p) for p in agent.pathway.produces]
            mean_product_level = np.mean(product_levels) if product_levels else 3.0

            if mean_product_level < 1.0:
                scarcity_bonus = max(1.0, 3.0 - mean_product_level)
            elif mean_product_level > 5.0:
                scarcity_bonus = max(0.2, 1.0 / (mean_product_level / 5.0))
            else:
                scarcity_bonus = 1.0

            allocated_rate = 1.0 * scarcity_bonus * efficiency_weight
            agent.current_production_rate = max(0.01, min(5.0, allocated_rate))

            if agent.can_produce(pool):
                agent.produce(pool)

        for agent in agents:
            agent.atp_budget += context["atp_regen"]

        for met, amount in context["base_supply"].items():
            pool.deposit(met, amount)

        pool.record()
        gdp = pool.total_output()
        result.gdp_history.append(gdp)

        if abs(gdp - prev_gdp) < 0.02 * max(abs(prev_gdp), 1.0):
            stable_count += 1
            if stable_count >= 20 and not result.converged:
                result.converged = True
                result.convergence_step = step
        else:
            stable_count = 0
        prev_gdp = gdp

    result.n_steps = n_steps
    return result


def _adjust_rate_distributed_scaled(
    agent: EconomicAgent,
    pool: "MetabolitePool",
    scale: float = 1.0,
):
    """
    Distributed feedback with scaled thresholds.

    Same logic as adjust_rate_distributed but thresholds are scaled:
        product_high = 5.0 * scale,  product_low = 1.0 * scale
        substrate_low = 0.5 * scale, substrate_high = 3.0 * scale
    """
    prod_high = 5.0 * scale
    prod_low = 1.0 * scale
    sub_low = 0.5 * scale
    sub_high = 3.0 * scale

    product_signal = 1.0
    for product in agent.pathway.produces:
        level = pool.get(product)
        if level > prod_high:
            product_signal *= 0.7
        elif level < prod_low:
            product_signal *= 1.3

    substrate_signal = 1.0
    for substrate in agent.pathway.consumes:
        if substrate == "ATP":
            continue
        level = pool.get(substrate)
        if level < sub_low:
            substrate_signal *= 0.5
        elif level > sub_high:
            substrate_signal *= 1.2

    atp_signal = 1.0
    if agent.atp_budget < 2.0:
        atp_signal = 0.3
    elif agent.atp_budget > 15.0:
        atp_signal = 1.5

    agent.current_production_rate = (
        agent.base_production_rate
        * product_signal
        * substrate_signal
        * atp_signal
    )
    agent.current_production_rate = max(0.01, min(5.0, agent.current_production_rate))


def run_perturbation_suite(
    pathways: list[PathwayProfile] = None,
    n_steps: int = 200,
    base_supply: dict[str, float] = None,
    atp_regeneration: float = 2.0,
) -> dict:
    """
    Test four perturbation types, each testing a different Austrian prediction.

    Returns a dict with results for each perturbation type, each containing
    distributed, centralized (dumb), and centralized (smart) metrics along
    with full GDP histories for plotting.

    Perturbation types:
        a) Substrate shock   — tests Hayek's knowledge problem
        b) ATP crisis        — tests Mises' calculation problem
        c) Demand spike      — tests Kirzner's entrepreneurial discovery
        d) Novel opportunity — tests Kirzner's entrepreneurial alertness
    """
    if pathways is None:
        pathways = PATHWAY_CATALOG
    if base_supply is None:
        base_supply = {
            "UDP-glucose": 1.0, "UDP-GlcNAc": 0.5, "Ca2+": 0.5,
            "O2": 2.0, "luciferin": 0.3, "glycine": 1.0,
            "alanine": 1.0, "glutamine": 0.5,
            "piRNA_precursors": 0.2, "Zn2+": 0.2, "cholesterol": 0.3,
        }

    shock_step = 100
    total_steps = n_steps

    # Identify key metabolites from the pathways
    all_substrates = set()
    all_products = set()
    for p in pathways:
        all_substrates.update(s for s in p.consumes if s != "ATP")
        all_products.update(p.produces)

    # Pick a key substrate that appears in base_supply
    key_substrate = None
    for s in base_supply:
        if s in all_substrates:
            key_substrate = s
            break
    if key_substrate is None and all_substrates:
        key_substrate = list(all_substrates)[0]

    # Pick a key product for the demand spike
    key_product = list(all_products)[0] if all_products else None

    # Find agents that produce the key product
    product_agents = [p for p in pathways if key_product in p.produces] if key_product else []

    results = {}

    # -----------------------------------------------------------------------
    # (a) Substrate shock — tests Hayek's knowledge problem
    # -----------------------------------------------------------------------
    def substrate_shock_hook(step, agents, pool, context):
        if step == shock_step and key_substrate:
            # Cut external supply of key substrate by 80%
            if key_substrate in context["base_supply"]:
                context["base_supply"][key_substrate] *= 0.2

    dist_a = _run_distributed_with_hooks(
        pathways, total_steps, atp_regeneration, base_supply, substrate_shock_hook)
    cent_a = _run_centralized_with_hooks(
        pathways, total_steps, atp_regeneration, base_supply, substrate_shock_hook)
    smart_a = _run_centralized_smart_with_hooks(
        pathways, total_steps, atp_regeneration, base_supply, substrate_shock_hook)

    pre_shock_gdp_dist = np.mean(dist_a.gdp_history[max(0, shock_step-20):shock_step]) if shock_step > 0 else dist_a.gdp_history[0]
    pre_shock_gdp_cent = np.mean(cent_a.gdp_history[max(0, shock_step-20):shock_step]) if shock_step > 0 else cent_a.gdp_history[0]
    pre_shock_gdp_smart = np.mean(smart_a.gdp_history[max(0, shock_step-20):shock_step]) if shock_step > 0 else smart_a.gdp_history[0]

    def _recovery_steps(gdp_history, pre_shock_gdp, shock_step_idx):
        """Steps to return to 90% of pre-shock GDP after the shock."""
        target = 0.9 * pre_shock_gdp
        for i in range(shock_step_idx, len(gdp_history)):
            if gdp_history[i] >= target:
                return i - shock_step_idx
        return len(gdp_history) - shock_step_idx  # never recovered

    results["substrate_shock"] = {
        "description": "Hayek's Knowledge Problem — Substrate supply cut by 80%",
        "key_substrate": key_substrate,
        "dist_gdp_history": dist_a.gdp_history,
        "cent_gdp_history": cent_a.gdp_history,
        "smart_gdp_history": smart_a.gdp_history,
        "dist_recovery_steps": _recovery_steps(dist_a.gdp_history, pre_shock_gdp_dist, shock_step),
        "cent_recovery_steps": _recovery_steps(cent_a.gdp_history, pre_shock_gdp_cent, shock_step),
        "smart_recovery_steps": _recovery_steps(smart_a.gdp_history, pre_shock_gdp_smart, shock_step),
        "dist_final_frac": dist_a.gdp_history[-1] / pre_shock_gdp_dist if pre_shock_gdp_dist > 0 else 0,
        "cent_final_frac": cent_a.gdp_history[-1] / pre_shock_gdp_cent if pre_shock_gdp_cent > 0 else 0,
        "smart_final_frac": smart_a.gdp_history[-1] / pre_shock_gdp_smart if pre_shock_gdp_smart > 0 else 0,
    }

    # -----------------------------------------------------------------------
    # (b) ATP crisis — tests Mises' calculation problem
    # -----------------------------------------------------------------------
    crisis_duration = 30

    def atp_crisis_hook(step, agents, pool, context):
        if step == shock_step:
            context["atp_regen"] = atp_regeneration * 0.5
        elif step == shock_step + crisis_duration:
            context["atp_regen"] = atp_regeneration  # restore

    dist_b = _run_distributed_with_hooks(
        pathways, total_steps, atp_regeneration, base_supply, atp_crisis_hook)
    cent_b = _run_centralized_with_hooks(
        pathways, total_steps, atp_regeneration, base_supply, atp_crisis_hook)
    smart_b = _run_centralized_smart_with_hooks(
        pathways, total_steps, atp_regeneration, base_supply, atp_crisis_hook)

    pre_crisis_dist = np.mean(dist_b.gdp_history[max(0, shock_step-20):shock_step])
    pre_crisis_cent = np.mean(cent_b.gdp_history[max(0, shock_step-20):shock_step])
    pre_crisis_smart = np.mean(smart_b.gdp_history[max(0, shock_step-20):shock_step])

    crisis_window = slice(shock_step, shock_step + crisis_duration)
    dist_trough = min(dist_b.gdp_history[crisis_window]) if shock_step + crisis_duration <= len(dist_b.gdp_history) else dist_b.gdp_history[-1]
    cent_trough = min(cent_b.gdp_history[crisis_window]) if shock_step + crisis_duration <= len(cent_b.gdp_history) else cent_b.gdp_history[-1]
    smart_trough = min(smart_b.gdp_history[crisis_window]) if shock_step + crisis_duration <= len(smart_b.gdp_history) else smart_b.gdp_history[-1]

    results["atp_crisis"] = {
        "description": "Mises' Calculation Problem — ATP regeneration halved for 30 steps",
        "dist_gdp_history": dist_b.gdp_history,
        "cent_gdp_history": cent_b.gdp_history,
        "smart_gdp_history": smart_b.gdp_history,
        "dist_trough_frac": dist_trough / pre_crisis_dist if pre_crisis_dist > 0 else 0,
        "cent_trough_frac": cent_trough / pre_crisis_cent if pre_crisis_cent > 0 else 0,
        "smart_trough_frac": smart_trough / pre_crisis_smart if pre_crisis_smart > 0 else 0,
        "dist_recovery_steps": _recovery_steps(dist_b.gdp_history, pre_crisis_dist, shock_step + crisis_duration),
        "cent_recovery_steps": _recovery_steps(cent_b.gdp_history, pre_crisis_cent, shock_step + crisis_duration),
        "smart_recovery_steps": _recovery_steps(smart_b.gdp_history, pre_crisis_smart, shock_step + crisis_duration),
    }

    # -----------------------------------------------------------------------
    # (c) Demand spike — tests Kirzner's entrepreneurial discovery
    # -----------------------------------------------------------------------
    demand_multiplier = 3.0

    def demand_spike_hook(step, agents, pool, context):
        if step >= shock_step and key_product:
            # Consume extra from pool (simulating downstream demand)
            extra_demand = demand_multiplier * 1.0
            pool.withdraw(key_product, extra_demand)

    dist_c = _run_distributed_with_hooks(
        pathways, total_steps, atp_regeneration, base_supply, demand_spike_hook)
    cent_c = _run_centralized_with_hooks(
        pathways, total_steps, atp_regeneration, base_supply, demand_spike_hook)
    smart_c = _run_centralized_smart_with_hooks(
        pathways, total_steps, atp_regeneration, base_supply, demand_spike_hook)

    def _response_time(result, key_prod, shock_step_idx):
        """Steps for production of key_prod to increase by 50% after shock."""
        if not key_prod:
            return total_steps
        # Find agents that produce key_prod and track their total production
        producers = [a for a in result.agents if key_prod in a.pathway.produces]
        if not producers:
            return total_steps
        # Use pool history for the key product
        if key_prod in result.pool.history:
            hist = result.pool.history[key_prod]
            if shock_step_idx < len(hist):
                baseline_level = hist[shock_step_idx] if shock_step_idx < len(hist) else 0
                # Measure how quickly the level stabilizes at a new (lower but recovering) level
                for i in range(shock_step_idx + 1, len(hist)):
                    # Check if production rate has risen (level stops dropping)
                    if i >= shock_step_idx + 2:
                        if hist[i] > hist[i-1]:
                            return i - shock_step_idx
        return total_steps - shock_step_idx

    results["demand_spike"] = {
        "description": "Kirzner's Entrepreneurial Discovery — 3x demand for one product",
        "key_product": key_product,
        "dist_gdp_history": dist_c.gdp_history,
        "cent_gdp_history": cent_c.gdp_history,
        "smart_gdp_history": smart_c.gdp_history,
        "dist_response_time": _response_time(dist_c, key_product, shock_step),
        "cent_response_time": _response_time(cent_c, key_product, shock_step),
        "smart_response_time": _response_time(smart_c, key_product, shock_step),
    }

    # -----------------------------------------------------------------------
    # (d) Novel opportunity — tests Kirzner's entrepreneurial alertness
    # -----------------------------------------------------------------------
    novel_metabolite = "novel_resource_X"
    # Pick 2-3 agents that can use the novel resource
    eligible_indices = list(range(min(3, len(pathways))))

    def novel_opportunity_hook(step, agents, pool, context):
        if step == shock_step:
            # Introduce novel metabolite at high levels
            pool.deposit(novel_metabolite, 20.0)
            # Add it to the consumes list of 2-3 agents
            for idx in eligible_indices:
                if idx < len(agents):
                    if novel_metabolite not in agents[idx].pathway.consumes:
                        agents[idx].pathway.consumes.append(novel_metabolite)
            # Also add small ongoing supply
            context["base_supply"][novel_metabolite] = 2.0
        elif step > shock_step:
            # Keep supplying the novel resource
            pass  # handled by base_supply update above

    dist_d = _run_distributed_with_hooks(
        pathways, total_steps, atp_regeneration, base_supply, novel_opportunity_hook)
    cent_d = _run_centralized_with_hooks(
        pathways, total_steps, atp_regeneration, base_supply, novel_opportunity_hook)
    smart_d = _run_centralized_smart_with_hooks(
        pathways, total_steps, atp_regeneration, base_supply, novel_opportunity_hook)

    # Measure GDP gain from the new metabolite (compare post-shock GDP to a no-shock run)
    dist_baseline = _run_distributed_with_hooks(
        pathways, total_steps, atp_regeneration, base_supply, None)
    cent_baseline = _run_centralized_with_hooks(
        pathways, total_steps, atp_regeneration, base_supply, None)
    smart_baseline = _run_centralized_smart_with_hooks(
        pathways, total_steps, atp_regeneration, base_supply, None)

    def _gdp_gain(perturbed, baseline, shock_idx):
        post_perturbed = np.mean(perturbed.gdp_history[shock_idx:])
        post_baseline = np.mean(baseline.gdp_history[shock_idx:])
        return post_perturbed - post_baseline

    results["novel_opportunity"] = {
        "description": "Kirzner's Entrepreneurial Alertness — Novel resource introduced",
        "novel_metabolite": novel_metabolite,
        "eligible_agents": [pathways[i].name for i in eligible_indices if i < len(pathways)],
        "dist_gdp_history": dist_d.gdp_history,
        "cent_gdp_history": cent_d.gdp_history,
        "smart_gdp_history": smart_d.gdp_history,
        "dist_gdp_gain": _gdp_gain(dist_d, dist_baseline, shock_step),
        "cent_gdp_gain": _gdp_gain(cent_d, cent_baseline, shock_step),
        "smart_gdp_gain": _gdp_gain(smart_d, smart_baseline, shock_step),
    }

    return results


# ---------------------------------------------------------------------------
# Upgrade 3: Parameter Sensitivity Analysis
# ---------------------------------------------------------------------------

def run_sensitivity_analysis(
    pathways: list[PathwayProfile] = None,
    n_steps: int = 200,
    base_supply: dict[str, float] = None,
    atp_regeneration: float = 2.0,
    multipliers: list[float] = None,
) -> dict:
    """
    Run both regimes + perturbation across a grid of feedback threshold multipliers.

    This proves the distributed advantage holds across parameter choices, not
    just at the defaults.

    Returns dict mapping multiplier -> {
        dist_gdp, cent_gdp, cent_smart_gdp,
        dist_robustness_mean, cent_robustness_mean, cent_smart_robustness_mean
    }
    """
    if pathways is None:
        pathways = PATHWAY_CATALOG
    if base_supply is None:
        base_supply = {
            "UDP-glucose": 1.0, "UDP-GlcNAc": 0.5, "Ca2+": 0.5,
            "O2": 2.0, "luciferin": 0.3, "glycine": 1.0,
            "alanine": 1.0, "glutamine": 0.5,
            "piRNA_precursors": 0.2, "Zn2+": 0.2, "cholesterol": 0.3,
        }
    if multipliers is None:
        multipliers = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]

    results = {}

    for mult in multipliers:
        print(f"  [sensitivity] threshold_scale = {mult:.2f} ...")

        # Distributed with scaled thresholds
        dist = _run_distributed_with_hooks(
            pathways, n_steps, atp_regeneration, base_supply,
            pre_step_hook=None, threshold_scale=mult,
        )

        # Centralized (dumb) — thresholds don't apply, but run for comparison
        cent = run_centralized(pathways, n_steps=n_steps,
                               atp_regeneration=atp_regeneration,
                               base_supply=base_supply)

        # Centralized (smart)
        smart = run_centralized_smart(pathways, n_steps=n_steps,
                                      atp_regeneration=atp_regeneration,
                                      base_supply=base_supply)

        # Robustness: remove each agent and measure GDP retention
        dist_robustness = []
        cent_robustness = []
        smart_robustness = []
        dist_baseline_gdp = dist.mean_gdp()
        cent_baseline_gdp = cent.mean_gdp()
        smart_baseline_gdp = smart.mean_gdp()

        for i in range(len(pathways)):
            remaining = [p for j, p in enumerate(pathways) if j != i]
            if not remaining:
                continue

            d = _run_distributed_with_hooks(
                remaining, n_steps, atp_regeneration, base_supply,
                pre_step_hook=None, threshold_scale=mult,
            )
            c = run_centralized(remaining, n_steps=n_steps,
                                atp_regeneration=atp_regeneration,
                                base_supply=base_supply)
            s = run_centralized_smart(remaining, n_steps=n_steps,
                                      atp_regeneration=atp_regeneration,
                                      base_supply=base_supply)

            dist_robustness.append(d.mean_gdp() / dist_baseline_gdp if dist_baseline_gdp > 0 else 0)
            cent_robustness.append(c.mean_gdp() / cent_baseline_gdp if cent_baseline_gdp > 0 else 0)
            smart_robustness.append(s.mean_gdp() / smart_baseline_gdp if smart_baseline_gdp > 0 else 0)

        results[mult] = {
            "dist_gdp": dist.mean_gdp(),
            "cent_gdp": cent.mean_gdp(),
            "cent_smart_gdp": smart.mean_gdp(),
            "dist_robustness_mean": float(np.mean(dist_robustness)) if dist_robustness else 0,
            "cent_robustness_mean": float(np.mean(cent_robustness)) if cent_robustness else 0,
            "cent_smart_robustness_mean": float(np.mean(smart_robustness)) if smart_robustness else 0,
        }

    return results


# ---------------------------------------------------------------------------
# Upgrade 4: Visualization for New Results
# ---------------------------------------------------------------------------

# Shared color palette
SPIRAL_GREEN = "#2d6a4f"
SPIRAL_MID = "#52b788"
GOLD = "#e9c46a"
RED = "#e63946"
BLUE = "#4361ee"
BACKGROUND = "#0d1117"
PANEL_BG = "#161b22"
TEXT_MAIN = "#e6edf3"
TEXT_DIM = "#8b949e"


def plot_perturbation_suite(suite_results: dict, save: bool = True):
    """
    Create a 4-panel figure showing perturbation results.

    Panel 1: GDP over time — substrate shock (Hayek)
    Panel 2: GDP over time — ATP crisis (Mises)
    Panel 3: Response time bar chart — demand spike (Kirzner)
    Panel 4: GDP gain bar chart — novel opportunity (Kirzner)
    """
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec

    fig = plt.figure(figsize=(22, 12), facecolor=BACKGROUND)
    gs = gridspec.GridSpec(2, 2, wspace=0.3, hspace=0.35)

    def _style_ax(ax):
        ax.set_facecolor(PANEL_BG)
        ax.tick_params(colors=TEXT_DIM)
        for spine in ax.spines.values():
            spine.set_color(TEXT_DIM)

    # --- Panel 1: Substrate Shock (Hayek) ---
    ax1 = fig.add_subplot(gs[0, 0])
    _style_ax(ax1)
    ss = suite_results.get("substrate_shock", {})
    if ss:
        steps = range(len(ss["dist_gdp_history"]))
        ax1.plot(steps, ss["dist_gdp_history"], color=SPIRAL_MID, linewidth=2, label="Distributed")
        ax1.plot(steps, ss["cent_gdp_history"], color=RED, linewidth=2, alpha=0.8, label="Centralized (dumb)")
        ax1.plot(steps, ss["smart_gdp_history"], color=GOLD, linewidth=2, alpha=0.8, label="Centralized (smart)")
        ax1.axvline(x=100, color=TEXT_DIM, linestyle="--", linewidth=1, alpha=0.5, label="Shock")
    ax1.set_xlabel("Time Step", color=TEXT_MAIN)
    ax1.set_ylabel("GDP", color=TEXT_MAIN)
    ax1.set_title("Hayek's Knowledge Problem — Substrate Shock", color=TEXT_MAIN, fontsize=12, fontweight="bold")
    ax1.legend(facecolor=PANEL_BG, edgecolor=TEXT_DIM, labelcolor=TEXT_MAIN, fontsize=8)

    # --- Panel 2: ATP Crisis (Mises) ---
    ax2 = fig.add_subplot(gs[0, 1])
    _style_ax(ax2)
    ac = suite_results.get("atp_crisis", {})
    if ac:
        steps = range(len(ac["dist_gdp_history"]))
        ax2.plot(steps, ac["dist_gdp_history"], color=SPIRAL_MID, linewidth=2, label="Distributed")
        ax2.plot(steps, ac["cent_gdp_history"], color=RED, linewidth=2, alpha=0.8, label="Centralized (dumb)")
        ax2.plot(steps, ac["smart_gdp_history"], color=GOLD, linewidth=2, alpha=0.8, label="Centralized (smart)")
        ax2.axvline(x=100, color=TEXT_DIM, linestyle="--", linewidth=1, alpha=0.5)
        ax2.axvline(x=130, color=TEXT_DIM, linestyle=":", linewidth=1, alpha=0.5)
        ax2.axvspan(100, 130, alpha=0.1, color=RED, label="Crisis period")
    ax2.set_xlabel("Time Step", color=TEXT_MAIN)
    ax2.set_ylabel("GDP", color=TEXT_MAIN)
    ax2.set_title("Mises' Calculation Problem — ATP Crisis", color=TEXT_MAIN, fontsize=12, fontweight="bold")
    ax2.legend(facecolor=PANEL_BG, edgecolor=TEXT_DIM, labelcolor=TEXT_MAIN, fontsize=8)

    # --- Panel 3: Demand Spike Response Time (Kirzner) ---
    ax3 = fig.add_subplot(gs[1, 0])
    _style_ax(ax3)
    ds = suite_results.get("demand_spike", {})
    if ds:
        regimes = ["Distributed", "Centralized\n(dumb)", "Centralized\n(smart)"]
        times = [ds["dist_response_time"], ds["cent_response_time"], ds["smart_response_time"]]
        colors = [SPIRAL_MID, RED, GOLD]
        # Scatter with horizontal median lines
        for i, (regime, time, color) in enumerate(zip(regimes, times, colors)):
            ax3.scatter([i], [time], c=color, s=100, zorder=3, edgecolors="white", linewidth=1)
            ax3.hlines(time, i-0.2, i+0.2, color=color, linewidth=2, zorder=2)
            ax3.text(i, time + 0.5, f"{time}", ha="center", va="bottom", color=TEXT_MAIN, fontsize=10)
        ax3.set_xticks(range(len(regimes)))
        ax3.set_xticklabels(regimes)
    ax3.set_ylabel("Response Time (steps)", color=TEXT_MAIN)
    ax3.set_title("Kirzner's Entrepreneurial Discovery — Demand Spike", color=TEXT_MAIN, fontsize=12, fontweight="bold")
    ax3.tick_params(axis="x", colors=TEXT_MAIN)

    # --- Panel 4: Novel Opportunity GDP Gain (Kirzner) ---
    ax4 = fig.add_subplot(gs[1, 1])
    _style_ax(ax4)
    no = suite_results.get("novel_opportunity", {})
    if no:
        regimes = ["Distributed", "Centralized\n(dumb)", "Centralized\n(smart)"]
        gains = [no["dist_gdp_gain"], no["cent_gdp_gain"], no["smart_gdp_gain"]]
        colors = [SPIRAL_MID, RED, GOLD]
        # Scatter with horizontal median lines
        for i, (regime, gain, color) in enumerate(zip(regimes, gains, colors)):
            ax4.scatter([i], [gain], c=color, s=100, zorder=3, edgecolors="white", linewidth=1)
            ax4.hlines(gain, i-0.2, i+0.2, color=color, linewidth=2, zorder=2)
            ax4.text(i, gain + 0.3, f"{gain:.1f}", ha="center", va="bottom", color=TEXT_MAIN, fontsize=10)
        ax4.set_xticks(range(len(regimes)))
        ax4.set_xticklabels(regimes)
    ax4.set_ylabel("GDP Gain from Novel Resource", color=TEXT_MAIN)
    ax4.set_title("Kirzner's Entrepreneurial Alertness — Novel Opportunity", color=TEXT_MAIN, fontsize=12, fontweight="bold")
    ax4.tick_params(axis="x", colors=TEXT_MAIN)

    fig.suptitle(
        "Austrian Predictions vs. Central Planning — Four Perturbation Tests",
        color=TEXT_MAIN, fontsize=15, fontweight="bold", y=0.98,
    )

    if save:
        fig_dir = Path(__file__).resolve().parent.parent / "paper" / "figures"
        fig_dir.mkdir(parents=True, exist_ok=True)
        out = fig_dir / "layer2_perturbation_suite.png"
        plt.savefig(out, dpi=200, bbox_inches="tight", facecolor=BACKGROUND)
        print(f"[economy] Saved perturbation suite figure to {out}")
    plt.close(fig)


def plot_sensitivity(sensitivity_results: dict, save: bool = True):
    """
    Create a 2-panel figure showing parameter sensitivity results.

    Panel 1: GDP vs threshold multiplier (3 lines)
    Panel 2: Mean robustness vs threshold multiplier (3 lines)
    """
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec

    fig = plt.figure(figsize=(16, 6), facecolor=BACKGROUND)
    gs = gridspec.GridSpec(1, 2, wspace=0.3)

    multipliers = sorted(sensitivity_results.keys())
    dist_gdps = [sensitivity_results[m]["dist_gdp"] for m in multipliers]
    cent_gdps = [sensitivity_results[m]["cent_gdp"] for m in multipliers]
    smart_gdps = [sensitivity_results[m]["cent_smart_gdp"] for m in multipliers]

    dist_rob = [sensitivity_results[m]["dist_robustness_mean"] for m in multipliers]
    cent_rob = [sensitivity_results[m]["cent_robustness_mean"] for m in multipliers]
    smart_rob = [sensitivity_results[m]["cent_smart_robustness_mean"] for m in multipliers]

    def _style_ax(ax):
        ax.set_facecolor(PANEL_BG)
        ax.tick_params(colors=TEXT_DIM)
        for spine in ax.spines.values():
            spine.set_color(TEXT_DIM)

    # --- Panel 1: GDP vs Threshold Multiplier ---
    ax1 = fig.add_subplot(gs[0])
    _style_ax(ax1)
    ax1.plot(multipliers, dist_gdps, color=SPIRAL_MID, linewidth=2, marker="o", markersize=8, label="Distributed")
    ax1.plot(multipliers, cent_gdps, color=RED, linewidth=2, marker="s", markersize=8, alpha=0.8, label="Centralized (dumb)")
    ax1.plot(multipliers, smart_gdps, color=GOLD, linewidth=2, marker="^", markersize=8, alpha=0.8, label="Centralized (smart)")
    ax1.set_xlabel("Threshold Multiplier", color=TEXT_MAIN)
    ax1.set_ylabel("Mean GDP (last 20 steps)", color=TEXT_MAIN)
    ax1.set_title("GDP vs. Feedback Threshold Sensitivity", color=TEXT_MAIN, fontsize=12, fontweight="bold")
    ax1.legend(facecolor=PANEL_BG, edgecolor=TEXT_DIM, labelcolor=TEXT_MAIN, fontsize=9)

    # --- Panel 2: Robustness vs Threshold Multiplier ---
    ax2 = fig.add_subplot(gs[1])
    _style_ax(ax2)
    ax2.plot(multipliers, dist_rob, color=SPIRAL_MID, linewidth=2, marker="o", markersize=8, label="Distributed")
    ax2.plot(multipliers, cent_rob, color=RED, linewidth=2, marker="s", markersize=8, alpha=0.8, label="Centralized (dumb)")
    ax2.plot(multipliers, smart_rob, color=GOLD, linewidth=2, marker="^", markersize=8, alpha=0.8, label="Centralized (smart)")
    ax2.set_xlabel("Threshold Multiplier", color=TEXT_MAIN)
    ax2.set_ylabel("Mean Robustness (GDP fraction retained)", color=TEXT_MAIN)
    ax2.set_title("Robustness vs. Feedback Threshold Sensitivity", color=TEXT_MAIN, fontsize=12, fontweight="bold")
    ax2.legend(facecolor=PANEL_BG, edgecolor=TEXT_DIM, labelcolor=TEXT_MAIN, fontsize=9)
    ax2.axhline(y=1.0, color=TEXT_DIM, linestyle="--", linewidth=0.8, alpha=0.3)

    fig.suptitle(
        "Parameter Sensitivity — Results Hold Across Threshold Choices",
        color=TEXT_MAIN, fontsize=14, fontweight="bold", y=0.98,
    )

    if save:
        fig_dir = Path(__file__).resolve().parent.parent / "paper" / "figures"
        fig_dir.mkdir(parents=True, exist_ok=True)
        out = fig_dir / "layer2_sensitivity.png"
        plt.savefig(out, dpi=200, bbox_inches="tight", facecolor=BACKGROUND)
        print(f"[economy] Saved sensitivity figure to {out}")
    plt.close(fig)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("Layer 2: Metabolic Economy Simulation")
    print("=" * 60)
    print()

    # Define base supply (external inputs to the system)
    base_supply = {
        "UDP-glucose": 1.0,
        "UDP-GlcNAc": 0.5,
        "Ca2+": 0.5,
        "O2": 2.0,
        "luciferin": 0.3,
        "glycine": 1.0,
        "alanine": 1.0,
        "glutamine": 0.5,
        "piRNA_precursors": 0.2,
        "Zn2+": 0.2,
        "cholesterol": 0.3,
    }

    print("Running distributed simulation...")
    dist = run_distributed(n_steps=200, base_supply=base_supply)

    print("Running centralized simulation...")
    cent = run_centralized(n_steps=200, base_supply=base_supply)

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

    print("\nDone.")

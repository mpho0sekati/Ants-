"""
ants/__init__.py — Ant definitions, now with:
  • Real ImmuniSOC T-Cell + honeytoken tools for the Protector
  • Behavior parameters from ants_simulation.py (exploration_rate, health, etc.)
  • AntState health tracking — ants take damage on bad output, heal on good output
"""

from crewai import Agent

from ant_behavior import AntState, BehaviorParameters, collector_search_strategy
from brain import get_brain
from tools import (
    honeytoken_check,
    list_directory,
    read_file,
    run_python,
    tcell_scan,
    validate_output,
    web_search,
    write_file,
)

# Module-level behavior params (loaded once from learn_data.json)
_params = BehaviorParameters.from_heuristics()

# Per-ant health states — survive across tasks
_states: dict[str, AntState] = {}


def _get_state(ant_id: str, role: str) -> AntState:
    if ant_id not in _states:
        _states[ant_id] = AntState(ant_id=ant_id, role=role)
    return _states[ant_id]


def make_queen() -> Agent:
    state = _get_state("queen", "queen")
    return Agent(
        llm=get_brain("queen", temperature=0.2),
        role="Queen Ant — Colony Orchestrator",
        goal=(
            "Decompose tasks, coordinate the colony, and synthesise all findings "
            "into one complete, well-structured final answer."
        ),
        backstory=(
            f"You are the Queen. Health: {state.health}/3. "
            "You never forage yourself — you plan, delegate, and integrate. "
            "You are calm and precise. You trust your colony's vector pheromone trails."
        ),
        tools=[],
        allow_delegation=True,
        verbose=True,
    )


def make_collector(ant_id: int = 1) -> Agent:
    state    = _get_state(f"collector_{ant_id}", "collector")
    strategy = collector_search_strategy(_params, task="")

    backstory_mode = (
        "You are in EXPLORATION mode — search broadly, think independently."
        if strategy["explore"]
        else f"You are in TRAIL-FOLLOWING mode — search the pheromone store "
             f"(top {strategy['pheromone_top_k']} hits) before reasoning."
    )

    return Agent(
        llm=get_brain("collector"),
        role=f"Collector Ant #{ant_id}",
        goal=(
            "Gather the information or complete the work for your assigned sub-task. "
            "Return structured, fact-dense output — other ants retrieve it by vector search."
        ),
        backstory=(
            f"You are Collector #{ant_id}. Health: {state.health}/3. "
            f"Exploration rate: {_params.exploration_rate:.0%}. {backstory_mode} "
            "Your output is encoded as a 384-dim vector. "
            "Dense, precise outputs produce stronger pheromone trails."
        ),
        tools=[web_search, read_file, write_file, run_python],
        allow_delegation=False,
        verbose=True,
    )


def make_protector(ant_id: int = 1) -> Agent:
    state = _get_state(f"protector_{ant_id}", "protector")

    return Agent(
        llm=get_brain("protector"),
        role=f"Protector Ant #{ant_id}",
        goal=(
            "Run every output through the T-Cell engine (tcell_scan) and "
            "honeytoken detector (honeytoken_check) before it reaches the Queen. "
            "Quarantine anything at HIGH or CRITICAL containment level. "
            "Return a validated output with your full assessment appended."
        ),
        backstory=(
            f"You are Protector #{ant_id}. Health: {state.health}/3. "
            f"Detection range: {_params.protector_detection_range} pheromone deposits. "
            f"Attack power: {_params.protector_attack_power} findings → quarantine. "
            "You are the T-Cell of the colony — inspired by the ImmuniSOC-Nexus immune model. "
            "Nothing dangerous passes you. You have seen: "
            f"{state.consecutive_failures} consecutive failures."
        ),
        tools=[tcell_scan, honeytoken_check, validate_output],
        allow_delegation=False,
        verbose=True,
    )


def make_scout(ant_id: int = 1) -> Agent:
    state = _get_state(f"scout_{ant_id}", "scout")

    return Agent(
        llm=get_brain("scout"),
        role=f"Scout Ant #{ant_id}",
        goal=(
            "Explore the environment. Map files, data sources, APIs, and structures. "
            "Return a precise bullet-point map — Collectors navigate by it."
        ),
        backstory=(
            f"You are Scout #{ant_id}. Health: {state.health}/3. "
            "You venture further than any other ant. "
            "Your exploration rate is high. You don't collect — you discover. "
            "Your outputs seed the pheromone store that the whole colony searches."
        ),
        tools=[list_directory, web_search, run_python],
        allow_delegation=False,
        verbose=True,
    )


def get_colony_health() -> dict:
    """Return health stats for all ants — mirrors Ant simulation health tracking."""
    return {
        ant_id: {
            "role":    s.role,
            "health":  f"{s.health}/3",
            "alive":   s.is_alive(),
            "failures": s.consecutive_failures,
            "tasks_done": len(s.path),
        }
        for ant_id, s in _states.items()
    }

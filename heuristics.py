"""
heuristics.py — Carries over the learning system from the original Ants- repo.

Ants remember past episodes and adapt their behaviour over time.
"""

import json
import os
from typing import Any

LEARNING_FILE = os.path.join(os.path.dirname(__file__), "learn_data.json")

_DEFAULT = {
    "heuristics": {
        "collector_exploration_rate": 0.18,
        "protector_detection_range": 6,
        "enemy_random_move_prob": 0.2,
        "protector_attack_power": 2,
        # AI extensions
        "max_iterations_per_task": 3,
        "delegation_threshold": 0.7,
    },
    "episodes": [],
}


def load() -> dict[str, Any]:
    if os.path.exists(LEARNING_FILE):
        with open(LEARNING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return _DEFAULT.copy()


def save(data: dict[str, Any]) -> None:
    with open(LEARNING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def record_episode(task: str, success: bool, steps: int, notes: str = "") -> None:
    """Append a completed task episode so the colony can learn over time."""
    data = load()
    data["episodes"].append(
        {"task": task[:120], "success": success, "steps": steps, "notes": notes}
    )
    # Keep last 50 episodes
    data["episodes"] = data["episodes"][-50:]
    save(data)


def get_heuristics() -> dict[str, Any]:
    return load()["heuristics"]


def recent_success_rate(n: int = 10) -> float:
    """Return success rate over the last n episodes."""
    episodes = load()["episodes"][-n:]
    if not episodes:
        return 1.0
    return sum(1 for e in episodes if e.get("success")) / len(episodes)

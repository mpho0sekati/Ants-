# 🐜 AntColony — Multi-Agent AI System

A collaborative AI system inspired by ant colonies, fusing:

| Source | Contribution |
|---|---|
| **Ants-** | Colony roles (collector / protector / scout), heuristic learning via `learn_data.json` |
| **ImmuniSOC-Nexus** | Bio-inspired security model — Protector ant acts as a T-Cell validator |
| **crewAI** | Agent / Task / Crew orchestration framework |
| **groq-api-cookbook** | Fast tiny Groq brains (`llama3-8b-8192`, `llama-3.1-8b-instant`) |

---

## Overview

This project implements an innovative multi-agent AI system that mimics the behavior of ant colonies to solve complex tasks collaboratively. Each AI agent represents a specialized "ant" with distinct roles and capabilities, working together under the coordination of a central "Queen" agent.

The system combines bio-inspired algorithms with modern AI technologies, creating a unique approach to distributed problem solving that leverages the collective intelligence of multiple specialized agents.

---

## Architecture

```
You give a task
       │
       ▼
   🐜 Queen Ant          ← orchestrates, synthesises (llama3-8b)
       │
   ┌───┼───────────┐
   ▼   ▼           ▼
🐜 Scout  🐜🐜 Collectors  🐜 Protector
(maps)   (gather / work)  (validates, scans threats)
         │
         └── all powered by llama-3.1-8b-instant (Groq)
```

Each ant has a **tiny Groq brain** — fast, cheap, specialised.

---

## Key Features

- **Distributed Intelligence**: Multiple specialized AI agents collaborate to solve complex tasks
- **Role-Based Specialization**: Different ant types with specific responsibilities and tools
- **Learning System**: Continuous improvement through experience stored in `learn_data.json`
- **Bio-Inspired Design**: Algorithms modeled after actual ant colony behavior
- **Scalable Architecture**: Can adjust the number of agents based on task complexity
- **Security Validation**: Built-in validation and threat detection mechanisms

---

## Quickstart

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your Groq API key (free at https://console.groq.com)
cp .env.example .env
# Edit .env and paste your GROQ_API_KEY

# 3. Run a task
python main.py "Explain how TCP/IP handshakes work and write a Python demo"
```

---

## Examples

```bash
# Research task
python main.py "Summarise the top 5 Python web frameworks and compare them"

# Code generation
python main.py "Write a Python class for a rate limiter with tests"

# File analysis
python main.py "Analyse the files in . and produce a project summary" \
               --context "Focus on Python files only"

# Scale up the colony
python main.py "Build a full REST API spec for a todo app" \
               --collectors 3 --scouts 2

# Check colony health (from learned episodes)
python main.py --status
```

---

## Ant Roles

| Ant | Brain | Tools | Job |
|---|---|---|---|
| **Queen** | `llama3-8b-8192` | — | Decomposes tasks, synthesises results |
| **Scout** | `llama-3.1-8b-instant` | `list_directory`, `web_search`, `run_python` | Maps the terrain first |
| **Collector** | `llama-3.1-8b-instant` | `web_search`, `read_file`, `write_file`, `run_python` | Gathers information / does the work |
| **Protector** | `llama-3.1-8b-instant` | `scan_for_threats`, `validate_output` | Validates output, scans for threats |

---

## Learning & Adaptation

The colony learns from every task in `learn_data.json`. Heuristics (exploration rate,
detection range, etc.) carry over from the original Ants- simulation and are extended
with AI-specific parameters like `max_iterations_per_task`.

```python
from heuristics import recent_success_rate, get_heuristics
print(recent_success_rate())   # 0.0 – 1.0
print(get_heuristics())
```

---

## Project Structure

```
ant-colony/
├── main.py          ← CLI entry point
├── colony.py        ← AntColony class (assembles the Crew)
├── brain.py         ← Groq LLM factory per role
├── heuristics.py    ← Learning / episode tracking
├── ants/
│   └── __init__.py  ← Queen, Collector, Protector, Scout definitions
├── tools/
│   └── __init__.py  ← All ant tools (search, file I/O, security)
├── learn_data.json  ← Persistent learning data
├── .env.example     ← Copy to .env and add your GROQ_API_KEY
└── requirements.txt
```

---

## Use Cases

The Ant Colony AI system excels at:
- Complex research tasks requiring multiple perspectives
- Multi-step problem solving
- Content generation with quality validation
- Code development with built-in review processes
- Data analysis from various sources
- Collaborative decision making
- Learning from past interactions to improve future performance

---

## Contributing

We welcome contributions to enhance the Ant Colony AI system. Feel free to fork the repository, make improvements, and submit pull requests.

---

## License

See the LICENSE file for licensing information.
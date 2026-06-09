#!/usr/bin/env python3
"""
main.py — AntColony CLI

Usage:
    python main.py "your task here"
    python main.py "task" --context "extra context"
    python main.py --status              # colony health + pheromone store stats
    python main.py --search "query"      # semantic search of colony memory
    python main.py --store-info          # inspect vector store

Examples:
    python main.py "Research Python security vulnerabilities and summarise them"
    python main.py "Write a Python rate-limiter class with tests"
    python main.py --search "authentication findings" --top-k 3
"""

import argparse
import sys

from dotenv import load_dotenv
load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description="🐜  AntColony — vector-pheromone multi-agent AI"
    )
    parser.add_argument("task", nargs="?", help="Task for the colony")
    parser.add_argument("--context",    default="",  help="Extra context")
    parser.add_argument("--collectors", type=int, default=2)
    parser.add_argument("--scouts",     type=int, default=1)
    parser.add_argument("--protectors", type=int, default=1)
    parser.add_argument("--quiet",      action="store_true")
    parser.add_argument("--status",     action="store_true", help="Colony health")
    parser.add_argument("--search",     default="",  help="Semantic search of colony memory")
    parser.add_argument("--top-k",      type=int, default=5, help="Results for --search")
    parser.add_argument("--store-info", action="store_true", help="Pheromone store stats")

    args = parser.parse_args()

    from colony import AntColony

    colony = AntColony(
        n_collectors=args.collectors,
        n_scouts=args.scouts,
        n_protectors=args.protectors,
        verbose=not args.quiet,
    )

    if args.status:
        import json
        print("\n🐜  Colony Status:")
        print(json.dumps(colony.status(), indent=2))
        return

    if args.store_info:
        import json
        print("\n🧬  Pheromone Store:")
        print(json.dumps(colony.store.summary(), indent=2))
        return

    if args.search:
        print(f"\n🧬  Searching colony memory: \"{args.search}\"\n")
        print(colony.search_memory(args.search, top_k=args.top_k))
        return

    if not args.task:
        parser.print_help()
        print('\n💡  Example: python main.py "Summarise the latest AI news"')
        sys.exit(1)

    n = 1 + args.scouts + args.collectors + args.protectors
    print(f"\n{'='*60}")
    print(f"🐜  AntColony — {n} ants · vector pheromone communication")
    print(f"{'='*60}")
    print(f"Task: {args.task}")
    if args.context:
        print(f"Context: {args.context}")
    print(f"{'='*60}\n")

    result = colony.run(args.task, context=args.context or None)

    print(f"\n{'='*60}")
    print(f"🐜  Colony Result")
    print(f"{'='*60}")
    print(result)
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

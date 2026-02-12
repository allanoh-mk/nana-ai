from __future__ import annotations

import argparse
from pathlib import Path

from .brain import NanaBrain
from .memory import MemoryStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Chat with Nana")
    parser.add_argument(
        "--memory",
        default="data/memory.json",
        help="Path to Nana memory file (default: data/memory.json)",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    store = MemoryStore.load(Path(args.memory))
    brain = NanaBrain(store)

    print("🌸 Nana is awake (growing mode). Type 'exit' to stop.")
    print("Commands: /state to inspect growth")

    while True:
        try:
            user_input = input("you> ").strip()
        except EOFError:
            print()
            break

        if user_input.lower() in {"exit", "quit"}:
            break
        if not user_input:
            continue

        if user_input == "/state":
            neurons = len(store.brain_state.get("neurons", {}))
            mood = store.brain_state.get("mood", {})
            age = store.brain_state.get("identity", {}).get("age_cycles", 0)
            print(f"nana> neurons={neurons}, age_cycles={age}, mood={mood}")
            continue

        answer = brain.respond(user_input)
        print(f"nana> {answer}")
        store.save()

    store.save()
    print("🌙 Nana saved memory. Bye.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
from pathlib import Path

from .brain import NanaBrain
from .memory import MemoryStore
from .web.app import run_web


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Chat with Nana")
    parser.add_argument("--memory", default="data/memory.json", help="Path to Nana memory file")
    parser.add_argument("--web", action="store_true", help="Run web frontend server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    return parser


def main() -> int:
    args = build_parser().parse_args()

    if args.web:
        run_web(host=args.host, port=args.port, memory_path=args.memory)
        return 0

    store = MemoryStore.load(Path(args.memory))
    brain = NanaBrain(store)

    print("🌸 Nana is awake (critical-thinking mode). Type 'exit' to stop.")
    print("Commands: /state | search:... | code:... | image:... | video:...")

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
            bs = store.brain_state
            neurons = len(bs.get("neurons", {}))
            mood = bs.get("mood", {})
            identity = bs.get("identity", {})
            print(
                "nana> "
                f"neurons={neurons}, mood={mood}, age={store.current_age_years()}, "
                f"birthday={identity.get('birthday')}, maturity={identity.get('maturity_index')}"
            )
            continue

        answer = brain.respond(user_input)
        print(f"nana> {answer}")
        store.save()

    store.save()
    print("🌙 Nana saved memory. Bye.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


DEFAULT_MEMORY: dict[str, Any] = {
    "episodes": [],
    "brain_state": {
        "neurons": {},
        "mood": {"curiosity": 0.6, "confidence": 0.2, "warmth": 0.5},
        "identity": {"name": "Nana", "age_cycles": 0},
    },
}


@dataclass
class MemoryStore:
    path: Path
    state: dict[str, Any] = field(default_factory=lambda: json.loads(json.dumps(DEFAULT_MEMORY)))

    @classmethod
    def load(cls, path: str | Path) -> "MemoryStore":
        memory_path = Path(path)
        if memory_path.exists():
            loaded = json.loads(memory_path.read_text(encoding="utf-8"))
            state = json.loads(json.dumps(DEFAULT_MEMORY))
            state.update(loaded)
            if "brain_state" in loaded and isinstance(loaded["brain_state"], dict):
                state["brain_state"].update(loaded["brain_state"])
            return cls(path=memory_path, state=state)
        return cls(path=memory_path)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.state, indent=2, ensure_ascii=False), encoding="utf-8")

    @property
    def brain_state(self) -> dict[str, Any]:
        return self.state.setdefault("brain_state", {})

    def append_episode(self, episode: dict[str, Any]) -> None:
        self.state.setdefault("episodes", []).append(episode)

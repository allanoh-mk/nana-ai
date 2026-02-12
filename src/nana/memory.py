from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any


DEFAULT_MEMORY: dict[str, Any] = {
    "episodes": [],
    "brain_state": {
        "neurons": {},
        "mood": {
            "curiosity": 0.68,
            "confidence": 0.34,
            "warmth": 0.72,
            "focus": 0.56,
            "joy": 0.52,
            "calm": 0.66,
            "empathy": 0.58,
            "playfulness": 0.42,
            "wonder": 0.62,
        },
        "identity": {
            "name": "Nana",
            "persona": "female",
            "birthday": "2004-06-04",
            "self_description": "A self-growing digital mind.",
            "maturity_index": 0.22,
            "cycle_count": 0,
            "language_profile": ["en-US", "sw", "sw-KE-sheng"],
        },
        "knowledge": {
            "critical_thinking_score": 0.24,
            "security_awareness": 0.36,
            "creation_skills": {"code": 0.35, "image": 0.24, "video": 0.2},
            "search_skill": 0.35,
        },
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
            loaded_brain = loaded.get("brain_state", {}) if isinstance(loaded, dict) else {}
            if isinstance(loaded_brain, dict):
                state["brain_state"].update(loaded_brain)
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

    def now_context(self) -> dict[str, str]:
        now = datetime.now()
        return {
            "iso": now.isoformat(timespec="seconds"),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "weekday": now.strftime("%A"),
        }

    def current_age_years(self) -> int:
        ident = self.brain_state.setdefault("identity", {})
        born = date.fromisoformat(ident.get("birthday", "2004-06-04"))
        today = date.today()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

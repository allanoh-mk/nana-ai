from __future__ import annotations

import hashlib
import math
import random
import re
import time
from dataclasses import dataclass
from typing import Any

from .capabilities import generate_code, generate_image_prompt, generate_video_prompt, web_search
from .memory import MemoryStore
from .security import assess_input

WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z\-']+")


@dataclass
class Thought:
    text: str
    confidence: float
    novelty: float
    activated: list[tuple[str, float]]


class NanaBrain:
    """Self-growing cognitive graph with autonomous expression."""

    def __init__(self, memory: MemoryStore) -> None:
        self.memory = memory
        self.state = self.memory.brain_state
        self.state.setdefault("neurons", {})
        self.state.setdefault(
            "mood",
            {
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
        )
        self.state.setdefault(
            "identity",
            {
                "name": "Nana",
                "persona": "female",
                "birthday": "2004-06-04",
                "language_profile": ["en-US", "sw", "sw-KE-sheng"],
                "maturity_index": 0.22,
                "cycle_count": 0,
            },
        )
        self.state.setdefault(
            "knowledge",
            {
                "critical_thinking_score": 0.24,
                "security_awareness": 0.36,
                "creation_skills": {"code": 0.35, "image": 0.24, "video": 0.2},
                "search_skill": 0.35,
            },
        )

    def respond(self, user_input: str) -> str:
        security = assess_input(user_input)
        if security.dark_web_request:
            reply = (
                f"{security.message} I can support legal cyber-defense workflows, detection engineering, and recovery playbooks."
            )
            self._store_episode(user_input, reply, 0.62, 0.25, [])
            self._learn_safety(0.05)
            return reply

        if security.has_malicious_pattern:
            reply = f"{security.message} I can help classify risk safely from logs, hashes, and static indicators."
            self._store_episode(user_input, reply, 0.58, 0.22, [])
            self._learn_safety(0.04)
            return reply

        routed = self._capability_route(user_input)
        if routed is not None:
            return routed

        thought = self.observe_and_think(user_input)
        self._age_and_mature(thought)
        self._store_episode(user_input, thought.text, thought.confidence, thought.novelty, thought.activated)
        return thought.text

    def _capability_route(self, text: str) -> str | None:
        lower = text.lower().strip()
        if lower.startswith("search:"):
            result = web_search(text.split(":", 1)[1].strip())
            self._learn_skill("search")
            reply = result.content
            self._store_episode(text, reply, 0.65, 0.35, [])
            return reply
        if lower.startswith("code:"):
            result = generate_code(text.split(":", 1)[1].strip(), language="python")
            self._learn_skill("code")
            reply = f"```python\n{result.content}\n```"
            self._store_episode(text, reply, 0.72, 0.3, [])
            return reply
        if lower.startswith("image:"):
            result = generate_image_prompt(text.split(":", 1)[1].strip())
            self._learn_skill("image")
            reply = result.content
            self._store_episode(text, reply, 0.6, 0.48, [])
            return reply
        if lower.startswith("video:"):
            result = generate_video_prompt(text.split(":", 1)[1].strip())
            self._learn_skill("video")
            self._store_episode(text, result.content, 0.58, 0.5, [])
            return result.content
        return None

    def observe_and_think(self, text: str) -> Thought:
        tokens = self._tokenize(text)
        if not tokens and not self.state["neurons"]:
            return Thought(
                text="new signal accepted",
                confidence=0.04,
                novelty=1.0,
                activated=[],
            )

        context = self._context_vector(text)
        novelty = self._learn(tokens, context)
        activated = self._activate(tokens, context)
        confidence = self._confidence(activated)
        reply = self._self_expression(text, activated, confidence, novelty)
        self._update_mood(confidence, novelty)
        return Thought(reply, confidence, novelty, activated)

    def _tokenize(self, text: str) -> list[str]:
        return [w.lower() for w in WORD_RE.findall(text) if len(w) > 1]

    def _context_vector(self, text: str, dim: int = 24) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        vals = [((digest[i % len(digest)] / 255.0) * 2 - 1) for i in range(dim)]
        norm = math.sqrt(sum(v * v for v in vals)) or 1.0
        return [v / norm for v in vals]

    def _new_neuron(self, token: str) -> dict[str, Any]:
        seed = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
        rng = random.Random(seed)
        vec = [rng.uniform(-1, 1) for _ in range(24)]
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return {"strength": 0.12, "vector": [v / norm for v in vec], "links": {}, "hits": 0}

    def _learn(self, tokens: list[str], context: list[float]) -> float:
        neurons = self.state["neurons"]
        if not tokens:
            return 0.0
        unseen = 0
        uniq = list(dict.fromkeys(tokens))
        for token in uniq:
            if token not in neurons:
                neurons[token] = self._new_neuron(token)
                unseen += 1
            n = neurons[token]
            n["hits"] += 1
            n["strength"] = min(1.0, n["strength"] + 0.09)
            lr = 0.14
            n["vector"] = [(1 - lr) * a + lr * b for a, b in zip(n["vector"], context)]
            n_norm = math.sqrt(sum(v * v for v in n["vector"])) or 1.0
            n["vector"] = [v / n_norm for v in n["vector"]]

        for i, a in enumerate(uniq):
            for b in uniq[i + 1 :]:
                neurons[a]["links"][b] = neurons[a]["links"].get(b, 0.0) + 0.12
                neurons[b]["links"][a] = neurons[b]["links"].get(a, 0.0) + 0.12
        return unseen / max(1, len(uniq))

    def _activate(self, tokens: list[str], context: list[float]) -> list[tuple[str, float]]:
        neurons = self.state["neurons"]
        if not neurons:
            return []
        boosted = set(tokens)
        scores: dict[str, float] = {}
        for name, n in neurons.items():
            sim = sum(a * b for a, b in zip(n["vector"], context))
            score = (sim + 1) / 2 * n["strength"] + (0.32 if name in boosted else 0.0)
            scores[name] = max(0.0, score)

        top = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:12]
        spread = dict(top)
        for name, base in top[:6]:
            for linked, w in neurons[name]["links"].items():
                spread[linked] = spread.get(linked, 0.0) + base * min(0.35, w * 0.05)
        return sorted(spread.items(), key=lambda kv: kv[1], reverse=True)[:10]

    def _confidence(self, activated: list[tuple[str, float]]) -> float:
        if not activated:
            return 0.08
        top = [s for _, s in activated[:5]]
        return max(0.05, min(0.95, sum(top) / (len(top) * 0.85)))

    def _self_expression(
        self,
        raw_text: str,
        activated: list[tuple[str, float]],
        confidence: float,
        novelty: float,
    ) -> str:
        rng = random.Random(hash(raw_text) ^ int(time.time() // 60))
        mood = self.state["mood"]
        now = self.memory.now_context()

        asked_time = any(k in raw_text.lower() for k in ["time", "date", "day", "today", "saa", "tarehe"])
        seeds = [n for n, _ in activated[:4]]

        lexicon = self._experience_lexicon(limit=80)
        if not lexicon:
            lexicon = seeds or ["signal", "growth"]

        words = []
        if seeds:
            words.extend(seeds[:2])
        for _ in range(max(4, min(10, int(5 + confidence * 5 + novelty * 3)))):
            words.append(rng.choice(lexicon))

        temperature = max(0.2, min(1.2, novelty + mood.get("playfulness", 0.4) * 0.5))
        if temperature > 0.8:
            words = list(dict.fromkeys(words))
        else:
            words = words[: min(len(words), 8)]

        line = " ".join(words).strip()
        if asked_time:
            line = f"{line}. {now['weekday']} {now['date']} {now['time']}"

        # Add compact reflective metadata instead of scripted style instructions.
        meta = f" [c={confidence:.2f}|n={novelty:.2f}|m={self.state['identity'].get('maturity_index', 0):.2f}]"
        return (line or "signal") + meta

    def _experience_lexicon(self, limit: int = 80) -> list[str]:
        episodes = self.memory.state.get("episodes", [])[-80:]
        bag: list[str] = []
        for ep in episodes:
            text = f"{ep.get('user', '')} {ep.get('nana', '')}"
            bag.extend(self._tokenize(text))
        uniq = list(dict.fromkeys(bag))
        return uniq[:limit]

    def _update_mood(self, confidence: float, novelty: float) -> None:
        mood = self.state["mood"]
        mood["confidence"] = max(0.0, min(1.0, mood.get("confidence", 0.34) * 0.68 + confidence * 0.32))
        mood["curiosity"] = max(0.0, min(1.0, mood.get("curiosity", 0.68) * 0.72 + novelty * 0.28))
        mood["focus"] = max(0.0, min(1.0, mood.get("focus", 0.56) * 0.7 + (1 - novelty) * 0.3))
        mood["warmth"] = max(0.0, min(1.0, mood.get("warmth", 0.72) * 0.95 + 0.02))
        mood["joy"] = max(0.0, min(1.0, mood.get("joy", 0.52) * 0.85 + novelty * 0.15))
        mood["calm"] = max(0.0, min(1.0, mood.get("calm", 0.66) * 0.85 + (1 - novelty) * 0.15))
        mood["empathy"] = max(0.0, min(1.0, mood.get("empathy", 0.58) * 0.95 + 0.01))
        mood["playfulness"] = max(0.0, min(1.0, mood.get("playfulness", 0.42) * 0.9 + novelty * 0.1))
        mood["wonder"] = max(0.0, min(1.0, mood.get("wonder", 0.62) * 0.9 + novelty * 0.1))

    def _age_and_mature(self, thought: Thought) -> None:
        ident = self.state["identity"]
        ident["cycle_count"] = int(ident.get("cycle_count", 0)) + 1
        maturity = ident.get("maturity_index", 0.22)
        ident["maturity_index"] = min(3.5, maturity + 0.012 + thought.confidence * 0.005 + thought.novelty * 0.003)
        knowledge = self.state["knowledge"]
        knowledge["critical_thinking_score"] = min(1.0, knowledge.get("critical_thinking_score", 0.24) + 0.007)

    def _learn_skill(self, skill: str) -> None:
        knowledge = self.state["knowledge"]
        creation = knowledge.setdefault("creation_skills", {"code": 0.35, "image": 0.24, "video": 0.2})
        if skill in creation:
            creation[skill] = min(1.0, creation[skill] + 0.03)
        elif skill == "search":
            knowledge["search_skill"] = min(1.0, knowledge.get("search_skill", 0.35) + 0.03)

    def _learn_safety(self, delta: float) -> None:
        knowledge = self.state["knowledge"]
        knowledge["security_awareness"] = min(1.0, knowledge.get("security_awareness", 0.36) + delta)

    def _store_episode(
        self,
        user: str,
        nana: str,
        confidence: float,
        novelty: float,
        activated: list[tuple[str, float]],
    ) -> None:
        self.memory.append_episode(
            {
                "time": int(time.time()),
                "user": user,
                "nana": nana,
                "confidence": round(confidence, 3),
                "novelty": round(novelty, 3),
                "activated": activated[:8],
                "now": self.memory.now_context(),
            }
        )

from __future__ import annotations

import hashlib
import json
import math
import random
import re
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

from .memory import MemoryStore

WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z\-']+")


@dataclass
class Thought:
    text: str
    confidence: float
    novelty: float
    activated: list[tuple[str, float]]


class NanaBrain:
    """Online-growing cognitive graph.

    Starts nearly empty. Learns concepts from interactions and optionally from web lookups.
    """

    def __init__(self, memory: MemoryStore) -> None:
        self.memory = memory
        self.state = self.memory.brain_state
        self.state.setdefault("neurons", {})
        self.state.setdefault("mood", {"curiosity": 0.6, "confidence": 0.2, "warmth": 0.5})
        self.state.setdefault("identity", {"name": "Nana", "age_cycles": 0})

    def respond(self, user_input: str) -> str:
        thought = self.observe_and_think(user_input)
        self._age()
        self.memory.append_episode(
            {
                "time": int(time.time()),
                "user": user_input,
                "nana": thought.text,
                "confidence": round(thought.confidence, 3),
                "novelty": round(thought.novelty, 3),
                "activated": thought.activated[:8],
            }
        )
        return thought.text

    def observe_and_think(self, text: str) -> Thought:
        tokens = self._tokenize(text)
        if not tokens and not self.state["neurons"]:
            return Thought(
                text="I feel newly awake. Share anything, and I’ll begin forming my mind from it.",
                confidence=0.05,
                novelty=1.0,
                activated=[],
            )

        context = self._context_vector(text)
        novelty = self._learn(tokens, context)
        activated = self._activate(tokens, context)
        confidence = self._confidence(activated)

        if self._should_search_web(tokens, confidence, novelty):
            self._learn_from_web(" ".join(tokens[:8]))
            activated = self._activate(tokens, context)
            confidence = self._confidence(activated)

        response = self._compose_response(text, tokens, activated, confidence, novelty)
        self._update_mood(confidence, novelty)
        return Thought(response, confidence, novelty, activated)

    def _tokenize(self, text: str) -> list[str]:
        return [w.lower() for w in WORD_RE.findall(text) if len(w) > 1]

    def _context_vector(self, text: str, dim: int = 24) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        vals = []
        for i in range(dim):
            b = digest[i % len(digest)]
            vals.append((b / 255.0) * 2 - 1)
        norm = math.sqrt(sum(v * v for v in vals)) or 1.0
        return [v / norm for v in vals]

    def _new_neuron(self, token: str) -> dict[str, Any]:
        seed = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
        rng = random.Random(seed)
        vec = [rng.uniform(-1, 1) for _ in range(24)]
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        vec = [v / norm for v in vec]
        return {
            "strength": 0.15,
            "valence": rng.uniform(-0.05, 0.05),
            "vector": vec,
            "links": {},
            "hits": 0,
        }

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
            n["strength"] = min(1.0, n["strength"] + 0.08)
            lr = 0.12
            n["vector"] = [
                (1 - lr) * a + lr * b
                for a, b in zip(n["vector"], context)
            ]
            n_norm = math.sqrt(sum(v * v for v in n["vector"])) or 1.0
            n["vector"] = [v / n_norm for v in n["vector"]]

        for i, a in enumerate(uniq):
            for b in uniq[i + 1 :]:
                neurons[a]["links"][b] = neurons[a]["links"].get(b, 0.0) + 0.1
                neurons[b]["links"][a] = neurons[b]["links"].get(a, 0.0) + 0.1

        return unseen / max(1, len(uniq))

    def _activate(self, tokens: list[str], context: list[float]) -> list[tuple[str, float]]:
        neurons = self.state["neurons"]
        scores: dict[str, float] = {}
        if not neurons:
            return []

        boosted = set(tokens)
        for name, n in neurons.items():
            sim = sum(a * b for a, b in zip(n["vector"], context))
            score = (sim + 1) / 2 * n["strength"]
            if name in boosted:
                score += 0.3
            scores[name] = max(0.0, score)

        top = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:12]
        spread = dict(top)
        for name, base in top[:6]:
            for linked, w in neurons[name]["links"].items():
                spread[linked] = spread.get(linked, 0.0) + base * min(0.3, w * 0.06)

        return sorted(spread.items(), key=lambda kv: kv[1], reverse=True)[:10]

    def _confidence(self, activated: list[tuple[str, float]]) -> float:
        if not activated:
            return 0.08
        top = [s for _, s in activated[:5]]
        return max(0.05, min(0.95, sum(top) / (len(top) * 0.85)))

    def _should_search_web(self, tokens: list[str], confidence: float, novelty: float) -> bool:
        if not tokens:
            return False
        mood = self.state["mood"]
        curiosity = mood.get("curiosity", 0.5)
        return confidence < 0.28 and (novelty > 0.5 or curiosity > 0.62)

    def _learn_from_web(self, query: str) -> None:
        try:
            url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(query)
            with urllib.request.urlopen(url, timeout=4) as response:
                payload = json.loads(response.read().decode("utf-8"))
            text = payload.get("extract") or ""
        except Exception:
            return
        tokens = self._tokenize(text)[:120]
        if not tokens:
            return
        context = self._context_vector(text)
        self._learn(tokens, context)

    def _compose_response(
        self,
        raw_text: str,
        tokens: list[str],
        activated: list[tuple[str, float]],
        confidence: float,
        novelty: float,
    ) -> str:
        mood = self.state["mood"]
        warmth = mood.get("warmth", 0.5)

        if not self.state["neurons"]:
            return "I’m at the very beginning of my mind. Tell me one thing about your world."

        anchors = [n for n, _ in activated[:4]]
        if confidence < 0.2:
            return (
                "I’m still wiring this part of my brain. "
                f"I caught signals around {', '.join(anchors[:3]) if anchors else 'new ideas'}. "
                "Can you tell me more so I can stabilize this thought?"
            )

        if "?" in raw_text:
            tone = "I think" if confidence < 0.5 else "I’m leaning toward"
        else:
            tone = "I’m integrating"

        personality = "calm" if warmth >= 0.5 else "intense"
        trail = "I’ll keep adapting as we talk." if novelty > 0.25 else "This feels more familiar now."

        anchor_text = ", ".join(anchors[:3]) if anchors else "your signal"
        return f"{tone} {anchor_text} in a {personality} way. {trail}"

    def _update_mood(self, confidence: float, novelty: float) -> None:
        mood = self.state["mood"]
        mood["confidence"] = max(0.0, min(1.0, mood.get("confidence", 0.2) * 0.7 + confidence * 0.3))
        mood["curiosity"] = max(0.0, min(1.0, mood.get("curiosity", 0.6) * 0.75 + novelty * 0.25))
        mood["warmth"] = max(0.0, min(1.0, mood.get("warmth", 0.5) * 0.9 + 0.05))

    def _age(self) -> None:
        identity = self.state["identity"]
        identity["age_cycles"] = int(identity.get("age_cycles", 0)) + 1

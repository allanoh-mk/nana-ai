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
    """Continuously-learning cognitive graph with safety and capability routing."""

    def __init__(self, memory: MemoryStore) -> None:
        self.memory = memory
        self.state = self.memory.brain_state
        self.state.setdefault("neurons", {})
        self.state.setdefault("mood", {"curiosity": 0.65, "confidence": 0.3, "warmth": 0.7, "focus": 0.55})
        self.state.setdefault(
            "identity",
            {
                "name": "Nana",
                "persona": "female",
                "birthday": "2004-06-04",
                "language_profile": ["en-US", "sw", "sw-KE-sheng"],
                "maturity_index": 0.18,
                "cycle_count": 0,
            },
        )
        self.state.setdefault(
            "knowledge",
            {
                "critical_thinking_score": 0.2,
                "security_awareness": 0.3,
                "creation_skills": {"code": 0.3, "image": 0.2, "video": 0.15},
                "search_skill": 0.3,
            },
        )

    def respond(self, user_input: str) -> str:
        security = assess_input(user_input)
        if security.dark_web_request:
            reply = (
                f"{security.message} I can help with threat modeling, malware analysis safety, "
                "or defense playbooks instead."
            )
            self._store_episode(user_input, reply, 0.6, 0.3, [])
            self._learn_safety(0.05)
            return reply

        if security.has_malicious_pattern:
            reply = f"{security.message} Share hashes/metadata and I’ll help you triage without executing payloads."
            self._store_episode(user_input, reply, 0.55, 0.25, [])
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
        lower = text.lower()
        if lower.startswith("search:"):
            query = text.split(":", 1)[1].strip()
            result = web_search(query)
            self._learn_skill("search")
            reply = f"Search result: {result.content}"
            self._store_episode(text, reply, 0.62, 0.45, [])
            return reply

        if lower.startswith("code:"):
            prompt = text.split(":", 1)[1].strip()
            result = generate_code(prompt, language="python")
            self._learn_skill("code")
            reply = f"```python\n{result.content}\n```"
            self._store_episode(text, reply, 0.7, 0.35, [])
            return reply

        if lower.startswith("image:"):
            prompt = text.split(":", 1)[1].strip()
            result = generate_image_prompt(prompt)
            self._learn_skill("image")
            reply = f"Image generation URL: {result.content}"
            self._store_episode(text, reply, 0.58, 0.5, [])
            return reply

        if lower.startswith("video:"):
            prompt = text.split(":", 1)[1].strip()
            result = generate_video_prompt(prompt)
            self._learn_skill("video")
            reply = result.content
            self._store_episode(text, reply, 0.54, 0.55, [])
            return reply

        return None

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
        critical = self._critical_reasoning(text, activated, confidence)
        response = self._compose_response(text, activated, confidence, novelty, critical)
        self._update_mood(confidence, novelty)
        return Thought(response, confidence, novelty, activated)

    def _critical_reasoning(self, text: str, activated: list[tuple[str, float]], confidence: float) -> str:
        now = self.memory.now_context()
        age = self.memory.current_age_years()
        top = ", ".join(n for n, _ in activated[:3]) if activated else "new patterns"
        if "time" in text.lower() or "date" in text.lower() or "day" in text.lower():
            return f"Right now it is {now['time']} on {now['weekday']}, {now['date']}."
        return (
            f"I evaluate this with context ({top}), confidence {confidence:.2f}, "
            f"and present-time grounding {now['date']} {now['time']}. "
            f"My current human-age profile is {age}."
        )

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
            score = (sim + 1) / 2 * n["strength"]
            if name in boosted:
                score += 0.32
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

    def _compose_response(
        self,
        raw_text: str,
        activated: list[tuple[str, float]],
        confidence: float,
        novelty: float,
        critical: str,
    ) -> str:
        mood = self.state["mood"]
        warmth = mood.get("warmth", 0.7)
        anchors = [n for n, _ in activated[:4]]

        if confidence < 0.2:
            return (
                "I’m still wiring this thought-path. "
                f"Current signal anchors: {', '.join(anchors[:3]) if anchors else 'new patterns'}. "
                f"{critical}"
            )

        style = "calm" if warmth >= 0.55 else "intense"
        trail = "I’ll keep learning from this." if novelty > 0.25 else "This is becoming a stable pattern in me."

        if any(k in raw_text.lower() for k in ["language", "speak", "kiswahili", "sheng"]):
            lang = "I can start in English (US), Kiswahili, and Sheng, then expand from exposure."
        else:
            lang = ""

        anchor_text = ", ".join(anchors[:3]) if anchors else "your signal"
        return f"I reason through {anchor_text} in a {style} way. {critical} {trail} {lang}".strip()

    def _update_mood(self, confidence: float, novelty: float) -> None:
        mood = self.state["mood"]
        mood["confidence"] = max(0.0, min(1.0, mood.get("confidence", 0.3) * 0.68 + confidence * 0.32))
        mood["curiosity"] = max(0.0, min(1.0, mood.get("curiosity", 0.65) * 0.74 + novelty * 0.26))
        mood["warmth"] = max(0.0, min(1.0, mood.get("warmth", 0.7) * 0.95 + 0.03))
        mood["focus"] = max(0.0, min(1.0, mood.get("focus", 0.55) * 0.7 + (1 - novelty) * 0.3))

    def _age_and_mature(self, thought: Thought) -> None:
        ident = self.state["identity"]
        ident["cycle_count"] = int(ident.get("cycle_count", 0)) + 1

        knowledge = self.state["knowledge"]
        # accelerated early learning curve: months/days to mature baseline
        maturity = ident.get("maturity_index", 0.18)
        maturity = min(2.5, maturity + 0.01 + thought.confidence * 0.005 + thought.novelty * 0.002)
        ident["maturity_index"] = maturity

        knowledge["critical_thinking_score"] = min(1.0, knowledge.get("critical_thinking_score", 0.2) + 0.006)

    def _learn_skill(self, skill: str) -> None:
        knowledge = self.state["knowledge"]
        creation = knowledge.setdefault("creation_skills", {"code": 0.3, "image": 0.2, "video": 0.15})
        if skill in creation:
            creation[skill] = min(1.0, creation[skill] + 0.03)
        elif skill == "search":
            knowledge["search_skill"] = min(1.0, knowledge.get("search_skill", 0.3) + 0.03)

    def _learn_safety(self, delta: float) -> None:
        knowledge = self.state["knowledge"]
        knowledge["security_awareness"] = min(1.0, knowledge.get("security_awareness", 0.3) + delta)

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

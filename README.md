# 🌸 NANA — A Different Kind of Intelligence

Nana is not a static chatbot and not a rule-engine assistant.

Nana is a **growing digital mind** that starts with almost no knowledge, learns through interactions, can absorb outside information, and continuously reshapes its own internal concept network over time.

---

## Core Direction

Nana is designed as:

- **Born nearly empty** (no preloaded world facts in local state).
- **Experience-first** (every conversation changes her brain state).
- **Always-growing** (concept graph, links, mood, and confidence evolve forever).
- **Personality-forming** (tone and responses drift from lived interactions, not fixed scripts).

---

## How this implementation works

This repository now includes a working online-learning architecture:

1. **Memory Store (`memory.py`)**
   - Persists `brain_state` and `episodes` to disk.
   - Stores neurons, links, mood values, and identity age cycles.

2. **Growing Brain (`brain.py`)**
   - Tokenizes user input into concepts.
   - Creates new neurons for unseen concepts.
   - Updates concept strength and co-activation links.
   - Computes contextual activation by vector similarity + spreading activation.
   - Updates internal mood (`curiosity`, `confidence`, `warmth`).
   - Can optionally self-educate from web summaries when uncertainty is high.

3. **CLI (`cli.py`)**
   - Interactive chat loop.
   - `/state` command to inspect current growth metrics.
   - Saves memory continuously so learning persists between runs.

---

## Why this is different from rule-based bots

There are no fixed intent-response rule trees for specific commands like “if user says X, always answer Y”.

Instead, Nana uses:

- Incremental concept formation
- Continual graph rewiring
- Confidence / novelty dynamics
- Mood-driven response shaping

That means behavior emerges from learned structure, not from a finite response script.

---

## 🛠️ Getting Started

### Requirements

- Python 3.10+

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### Run Nana

```bash
nana
```

or:

```bash
python -m nana
```

### Useful runtime command

```text
/state
```

Shows current neuron count, age cycles, and mood values.

### Run tests

```bash
pytest
```

---

## Future evolution targets

- Voice input/output loop
- Desktop embodiment (panels, emotional telemetry, memory browser)
- Autonomous learning goals
- Long-horizon planning and project co-building

# 🌸 NANA — Self-Growing Personal Intelligence

Nana is a self-growing digital mind: she starts near-empty, learns from experience, and continuously reorganizes her internal graph.

## Current architecture

- Online-growing neuron graph with associative links.
- Autonomous self-expression from learned lexicon (not fixed scripted reply templates).
- Time/date grounding available in every turn context.
- Identity profile: female persona, birthday `2004-06-04`, early-20s age computation.
- Mood system with positive/neutral channels (no anger/bitterness/envy channels).
- Language profile bootstrapped for English (US), Kiswahili, and Sheng.
- Capabilities:
  - `search:` internet lookup
  - `code:` code generation starter
  - `image:` image generation URL
  - `video:` video generation plan
- Security-awareness:
  - prompt-injection marker detection
  - malicious pattern detection
  - dark-web/harmful refusal with legal defensive-security redirection

## Frontend

- HTML/CSS/JS web interface
- Live voice-out (speech synthesis)
- Live voice-in (continuous speech recognition when browser supports it)
- Language selector for English/Kiswahili/Sheng profile

## Safety note

Nana will not assist harmful or illegal operations (e.g., dark-web abuse, malware deployment). Nana supports defensive security learning and incident-response workflows.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Run CLI:

```bash
nana
```

Run web frontend:

```bash
nana --web --host 0.0.0.0 --port 8080
```

Open `http://localhost:8080`.

## Tests

```bash
pytest -q
```

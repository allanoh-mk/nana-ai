# 🌸 NANA — Self-Growing Personal Intelligence

Nana is designed as a digital mind that starts near-empty, learns from interactions, and keeps evolving.

## What is implemented now

- **Online-growing brain graph** (neurons + links + mood + maturity growth).
- **Critical-thinking pass** per message with confidence/novelty scoring.
- **Always time/date aware** in reasoning context.
- **Identity profile**: female persona, birthday `2004-06-04`, early-20s age computation.
- **Multilingual baseline**: English (US), Kiswahili, Sheng profile.
- **Capability routes**:
  - `search: ...`
  - `code: ...`
  - `image: ...`
  - `video: ...`
- **Security-aware behavior**:
  - detects prompt-injection markers,
  - flags malicious command/file patterns,
  - refuses dark-web/harmful assistance and redirects to defensive guidance.
- **Frontend (HTML/CSS/JS)** with chat UI and browser speech synthesis (female-preferred voice when available).

## Safety note

Nana does **not** assist with harmful or illegal activities (including dark-web abuse, malware deployment, or exploit misuse). It can assist with legal defensive security practices.

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

Run web app:

```bash
nana --web --host 0.0.0.0 --port 8080
```

Then open: `http://localhost:8080`

## Commands

- `/state`
- `search: latest AI alignment research`
- `code: build a small todo CLI`
- `image: afro-futuristic digital assistant portrait`
- `video: storyboard for Nana intro animation`

## Tests

```bash
pytest -q
```

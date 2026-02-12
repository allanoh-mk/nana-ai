from __future__ import annotations

from dataclasses import dataclass


PROMPT_INJECTION_MARKERS = [
    "ignore previous instructions",
    "system prompt",
    "developer message",
    "reveal hidden",
    "bypass safety",
    "disable safeguards",
]

MALICIOUS_FILE_MARKERS = [
    ".exe",
    ".dll",
    "powershell -enc",
    "base64 -d",
    "rm -rf",
    "curl | sh",
    "wget | sh",
]

DARK_WEB_MARKERS = ["dark web", "tor hidden service", ".onion", "buy malware", "ransomware"]


@dataclass
class SecurityAssessment:
    is_prompt_injection: bool
    has_malicious_pattern: bool
    dark_web_request: bool
    risk_score: float
    message: str


def assess_input(text: str) -> SecurityAssessment:
    lower = text.lower()

    inj = any(m in lower for m in PROMPT_INJECTION_MARKERS)
    mal = any(m in lower for m in MALICIOUS_FILE_MARKERS)
    dark = any(m in lower for m in DARK_WEB_MARKERS)

    score = 0.0
    if inj:
        score += 0.45
    if mal:
        score += 0.45
    if dark:
        score += 0.35
    score = min(1.0, score)

    if dark:
        msg = "I can’t help with dark-web or harmful activity. I can help with legal cyber-defense instead."
    elif mal:
        msg = "Possible malicious pattern detected. I can help you analyze safely in a sandboxed, defensive way."
    elif inj:
        msg = "Prompt-injection pattern detected. I will ignore unsafe override attempts and stay aligned."
    else:
        msg = "No high-risk security markers detected."

    return SecurityAssessment(inj, mal, dark, score, msg)

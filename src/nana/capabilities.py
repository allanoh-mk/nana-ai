from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass


@dataclass
class CapabilityResult:
    kind: str
    content: str


def web_search(query: str) -> CapabilityResult:
    q = urllib.parse.quote(query)
    # lightweight no-auth endpoint for summary-style info
    url = f"https://api.duckduckgo.com/?q={q}&format=json&no_html=1&skip_disambig=1"
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            payload = json.loads(r.read().decode("utf-8"))
        abstract = payload.get("AbstractText") or ""
        related = payload.get("RelatedTopics") or []
        if abstract:
            content = abstract
        elif related and isinstance(related, list):
            first = related[0]
            if isinstance(first, dict):
                content = first.get("Text", "No concise results found.")
            else:
                content = "No concise results found."
        else:
            content = "No concise results found."
        return CapabilityResult("search", content)
    except Exception:
        return CapabilityResult("search", "Search unavailable right now; try rephrasing or retry later.")


def generate_code(prompt: str, language: str = "python") -> CapabilityResult:
    safe_comment = prompt.replace("```", "").strip()
    if language.lower() in {"javascript", "js"}:
        snippet = (
            "// Nana generated starter\n"
            f"// Goal: {safe_comment}\n"
            "function main(){\n"
            "  console.log('Nana starter running');\n"
            "}\n"
            "main();\n"
        )
    else:
        snippet = (
            "# Nana generated starter\n"
            f"# Goal: {safe_comment}\n"
            "def main():\n"
            "    print('Nana starter running')\n\n"
            "if __name__ == '__main__':\n"
            "    main()\n"
        )
    return CapabilityResult("code", snippet)


def generate_image_prompt(prompt: str) -> CapabilityResult:
    # text-to-image provider URL the frontend can open
    query = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{query}"
    return CapabilityResult("image", url)


def generate_video_prompt(prompt: str) -> CapabilityResult:
    # placeholder for video generation workflow
    return CapabilityResult(
        "video",
        f"Video generation plan created for: '{prompt}'. Integrate a model/API (e.g., Runway/Pika) in production.",
    )

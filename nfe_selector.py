"""Deterministic prompt-to-NFE policy for the Adaptive TTS demo.

This is a *heuristic*, not a trained quality predictor. It does not run TTS.
"""

from __future__ import annotations

import argparse
import json
import re
from typing import TypedDict


class NFESelection(TypedDict):
    nfe: int
    reason: str


# Chosen to match the demo's planned NFE 4 / 20 / 32 benchmarks.
# These values are NOT validated as quality-optimal for any prompt.
EASY_NFE = 4
DEFAULT_NFE = 20
COMPLEX_NFE = 32
SHORT_MAX_WORDS = 8
LONG_MIN_WORDS = 25

_WORD_RE = re.compile(r"\b\w+(?:['’\-]\w+)*\b", re.UNICODE)
_ACRONYM_RE = re.compile(r"\b[A-Z]{2,}\b")


def select_nfe(prompt: str) -> NFESelection:
    """Choose a fixed NFE once for a generation based only on prompt text.

    Return exactly ``{"nfe": int, "reason": str}`` so the runner and UI can
    consume it. The caller must pass the chosen NFE unchanged to every patch.

    Missing, empty or unusable input falls back to NFE 20.
    """
    if not isinstance(prompt, str) or not prompt.strip():
        return {"nfe": DEFAULT_NFE, "reason": "Fallback: missing or invalid prompt"}

    text = prompt.strip()
    word_count = len(_WORD_RE.findall(text))
    if word_count == 0:
        return {"nfe": DEFAULT_NFE, "reason": "Fallback: prompt has no words"}

    # Simple, intentionally conservative demo features, not learned signals.
    if any(character.isdigit() for character in text):
        return {"nfe": COMPLEX_NFE, "reason": "Complex: prompt contains numbers"}

    if _ACRONYM_RE.search(text):
        return {"nfe": COMPLEX_NFE, "reason": "Complex: prompt contains an uppercase acronym"}

    if word_count >= LONG_MIN_WORDS:
        return {"nfe": COMPLEX_NFE, "reason": f"Complex: long prompt ({word_count} words)"}

    if word_count <= SHORT_MAX_WORDS:
        return {"nfe": EASY_NFE, "reason": f"Easy: short prompt ({word_count} words)"}

    return {"nfe": DEFAULT_NFE, "reason": f"Medium: {word_count} words"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Select a demo NFE for a TTS prompt")
    parser.add_argument("prompt", nargs="?", default="", help="Text to synthesize")
    args = parser.parse_args()
    print(json.dumps(select_nfe(args.prompt), ensure_ascii=False))


if __name__ == "__main__":
    main()

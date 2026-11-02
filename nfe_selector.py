"""Deterministic prompt-level NFE selection for the WatAI Adaptive TTS demo.

This is a demo heuristic, NOT a measured optimal-NFE predictor.
The selected NFE is held constant for every audio patch in the generation.
"""

from __future__ import annotations

import argparse
import json
import re
from typing import TypedDict


class NFESelection(TypedDict):
    nfe: int
    reason: str


# Match the three NFE settings used by the team's demo benchmarks.
EASY_NFE = 4
DEFAULT_NFE = 20
COMPLEX_NFE = 32

SHORT_MAX_WORDS = 8
LONG_COMPLEX_MIN_WORDS = 25
VERY_LONG_MIN_WORDS = 40
DENSE_COMPLEX_MIN_WORDS = 18
DENSE_COMPLEX_MIN_MARKERS = 3

# Word counting is deterministic and handles apostrophes/hyphens.
_WORD_RE = re.compile(r"\b\w+(?:['’\-]\w+)*\b", re.UNICODE)
_ACRONYM_RE = re.compile(r"\b[A-Z]{2,}\b")
# A numeric expression like 12.5, 555-0147, 6:15 or Q4 counts once.
_NUMBER_RE = re.compile(r"(?<![A-Za-z0-9])(?:[A-Za-z]+)?\d+(?:[.,:/-]\d+)*(?![A-Za-z0-9])")
# Conservative 'simple' character set. Non-ASCII names and symbols go to fallback.
_SIMPLE_TEXT_RE = re.compile(r"[A-Za-z .,!?']+")


def select_nfe(prompt: str) -> NFESelection:
    """Return exactly {'nfe': int, 'reason': str} for a full text prompt.

    Call ONCE per utterance; the caller passes the resulting NFE unchanged
    to the existing Euler executor for every generated audio patch.
    """
    if not isinstance(prompt, str) or not prompt.strip():
        return {"nfe": DEFAULT_NFE, "reason": "Fallback: missing or invalid prompt"}

    text = prompt.strip()
    word_count = len(_WORD_RE.findall(text))
    if word_count == 0:
        return {"nfe": DEFAULT_NFE, "reason": "Fallback: prompt contains no words"}

    number_count = len(_NUMBER_RE.findall(text))
    acronym_count = len(_ACRONYM_RE.findall(text))
    complexity_markers = number_count + acronym_count

    # NFE 32 is deliberately rare: very long prompts, or longer prompts
    # with multiple obvious numeric/technical indicators.
    if word_count >= VERY_LONG_MIN_WORDS:
        return {
            "nfe": COMPLEX_NFE,
            "reason": f"High complexity: very long prompt ({word_count} words)",
        }

    if word_count >= LONG_COMPLEX_MIN_WORDS and complexity_markers > 0:
        return {
            "nfe": COMPLEX_NFE,
            "reason": (
                f"High complexity: {word_count} words with "
                f"{complexity_markers} numeric/acronym indicator(s)"
            ),
        }

    if (
        word_count >= DENSE_COMPLEX_MIN_WORDS
        and complexity_markers >= DENSE_COMPLEX_MIN_MARKERS
    ):
        return {
            "nfe": COMPLEX_NFE,
            "reason": (
                f"High complexity: {word_count} words with "
                f"{complexity_markers} numeric/acronym indicators"
            ),
        }

    # Only use the low-compute option for short, plain-looking text.
    # This check does not guarantee that pronunciation or prosody is easy.
    simple_text = _SIMPLE_TEXT_RE.fullmatch(text) is not None
    if word_count <= SHORT_MAX_WORDS and simple_text and complexity_markers == 0:
        return {
            "nfe": EASY_NFE,
            "reason": f"Low complexity: short straightforward phrase ({word_count} words)",
        }

    return {
        "nfe": DEFAULT_NFE,
        "reason": f"Default: {word_count} words; no validated reason to use NFE 4 or 32",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Choose one fixed NFE for a TTS prompt")
    parser.add_argument("prompt", nargs="?", default="", help="Text to synthesize")
    args = parser.parse_args()
    print(json.dumps(select_nfe(args.prompt), ensure_ascii=False))


if __name__ == "__main__":
    main()

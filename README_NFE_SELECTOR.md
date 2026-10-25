# Deterministic NFE selector (demo MVP)

Owner: Rababb |

This is a **prompt-to-NFE heuristic**, not a trained optimal-NFE model.
It runs entirely on CPU, needs no dependencies beyond Python 3.10+, and does not modify dots.tts or its Euler executor.

## Contract

```python
from nfe_selector import select_nfe

selection = select_nfe("Hello, how are you?")
# {"nfe": 4, "reason": "Easy: short prompt (4 words)"}

# Tony's runner passes `selection["nfe"]` to the existing executor once.
# Yulchan's executor keeps that same value for every generation patch.
```

Returns **exactly** `{ "nfe": int, "reason": str }`.

## Demo rules

Rules are evaluated in order:

1. Empty/invalid or non-word input -> fallback NFE **20**.
2. Contains any digit -> NFE **32**.
3. Contains an all-uppercase acronym (2+ letters) -> NFE **32**.
4. At least 25 words -> NFE **32**.
5. At most 8 words -> NFE **4**.
6. Otherwise -> NFE **20**.

The steps are deliberately from the team's planned NFE 4/20/32 benchmark set.
**Higher word count, numbers, or acronyms do not scientifically imply that higher NFE will improve speech.** These are illustrative routing rules pending audio-quality evaluation. In particular, NFE 4 may generate unacceptable audio in some cases; confirm against the actual WAVs and scores before treating it as safe.

## CLI

From the repository root (if this directory is at repo root):

```bash
python Adaptive-Compute-For-TTS/nfe_selector.py "Hello, how are you?"
# {"nfe": 4, "reason": "Easy: short prompt (4 words)"}

python Adaptive-Compute-For-TTS/nfe_selector.py
# {"nfe": 20, "reason": "Fallback: missing or invalid prompt"}
```

## Tests

```bash
python -m unittest discover -s Adaptive-Compute-For-TTS -p 'test_*.py' -v
```

Covers three different prompt classes, fallback, determinism, length boundaries, and acronyms.

## Integration note

Keep `nfe_selector.py` importable by the caller, for example in the same directory as Tony's runner or with this directory on `PYTHONPATH`. Call `select_nfe(prompt)` **once per generation**, then pass the returned `nfe` into the existing runner/executor unchanged for all patches. Log `nfe` and `reason` with the run ID; do not choose a new NFE for each patch.

No GitHub pushes, commits, backend wiring, or GPU inference are included in this standalone deliverable.

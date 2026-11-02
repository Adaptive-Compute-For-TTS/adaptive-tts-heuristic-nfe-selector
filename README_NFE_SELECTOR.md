# WatAI Adaptive TTS: deterministic prompt-level NFE selector

Owner: Rababb

This is a **demo heuristic** (not a trained model, nor a validated optimal-NFE predictor). It preserves the existing API: `select_nfe(prompt)` returns exactly `{ "nfe": int, "reason": str }`, using only Python's standard library.

## Decision rules

The checks run in this order:

1. Missing, blank, or non-word input: **NFE 20** fallback.
2. **NFE 32** for a very long prompt: **40+ words**.
3. **NFE 32** for a long prompt with at least one numeric expression or uppercase acronym: **25+ words**, plus a marker.
4. **NFE 32** for a medium-or-long prompt with many such markers: **18+ words**, plus **3 or more** numeric/acronym indicators.
5. **NFE 4** for a short straightforward-looking prompt: **8 or fewer words**, ASCII letters/basic punctuation only, no digits/acronyms.
6. Everything else: **NFE 20** default.

An indicator is a numeric expression (such as `12.5`, `555-0147`, `Q4`) or an uppercase acronym of at least two letters (such as `GPU` or `NASA`). An unusual name without ASCII spelling, symbols, or unexplained input goes to the default unless another high-complexity rule applies.

The NFE values 4, 20, and 32 match the existing demo benchmarks. **The thresholds are intentionally illustrative.** Existing WatAI WER and signal-check benchmarks have not demonstrated that numbers, acronyms, or long prompts inherently require NFE 32; in particular, the prior long-prompt generation data were truncated. We retain NFE 32 for unusually complex demo cases, not because it is scientifically optimal.

## Usage

```python
from nfe_selector import select_nfe

selection = select_nfe("The kettle is already on the stove.")
# {'nfe': 4, 'reason': 'Low complexity: short straightforward phrase (7 words)'}

selection = select_nfe("The CEO joined the call at noon.")
# NFE 20, since an acronym alone does not trigger 32

selection = select_nfe(
    "Our GPU cluster runs CUDA 12, and the ML team wants an API "
    "endpoint for the TTS model by Q4."
)
# NFE 32, due to multiple markers and a medium/long prompt
```

CLI usage:

```bash
python nfe_selector.py "Hello, how are you?"
```

## Integration

Call `select_nfe(prompt)` **once per utterance**, before TTS generation. Pass the selected integer into the existing fixed-NFE runner, which applies that NFE value independently to **every generated audio patch**. Do not reselect for each patch in this demo.

For example:

```python
from nfe_selector import select_nfe
from adaptive_nfe.fixed_nfe import generate_fixed_nfe

choice = select_nfe(prompt)
result = generate_fixed_nfe(runtime, nfe=choice["nfe"], text=prompt, guidance_scale=1.2)
print(choice["nfe"], choice["reason"])
```

The `adaptive_nfe` dependency is only needed for the integration example above, not for running the selector or tests.

## Test locally

From the folder containing both `.py` files:

```bash
python -m unittest -v
```

The test suite covers all three tiers, the old API, empty input, length boundaries, combined complexity rules, and deterministic selection.

## Important limitations

- The current WatAI benchmark supports that low NFE is faster, but it does **not** prove any rule here is quality optimal.
- WER alone cannot assess speaker similarity, prosody, or perceived naturalness.
- The heuristic does not execute dots.tts, calculate per-patch difficulty, or change its existing Euler executor.
- No GitHub modifications are part of this deliverable.

# dont-to-do

A prompt constraint compiler that converts negative and vague constraints into
specific, measurable, positive directives — replacing only the constraint spans
and leaving every other character of the original query unchanged.

## Installation

```bash
npx skills add https://github.com/instantX-research/skills --skill dont-to-do
```

Or manually copy into your Claude Code skills directory:

```bash
cp -r skills/dont-to-do ~/.claude/skills/
```

## What It Does

Negative constraints ("don't be too short", "avoid leaking credentials") give
LLMs a weak signal — the model activates the forbidden concept then tries to
suppress it. Vague qualifiers ("appropriate length", "reasonable format") are
worse: they transfer the decision entirely to the model. **Dont-to-do** compiles
both types into verifiable, quantified directives through a three-phase
SCAN → TRANSFORM → BACKFILL pipeline.

---

## Why this exists

Negative constraints ("don't be too short", "avoid leaking credentials") give
LLMs a weak signal. The model first activates the concept of the forbidden
thing, then tries to suppress it — an unreliable two-step. Vague qualifiers
("appropriate length", "reasonable format") are worse: they transfer the
decision entirely to the model, producing inconsistent outputs across runs.

**Dont-to-do** compiles both types into verifiable, quantified directives:

```
don't be too short
        ↓
≥100 words per paragraph; ≥30 words per sentence group
```

```
don't leak any user data
        ↓
user IDs/names/phones/emails → <USER_N>; IPs → x.x.x.x; tokens/keys → ****
```

```
keep it concise
        ↓
100–200 words; one idea per sentence; no preamble
```

---

## Architecture: Three-Phase Pipeline

Inspired by the compiler architecture in [VCC](https://github.com/lllyasviel/VCC),
dont-to-do processes a prompt through three discrete phases:

```
Original Query
      │
      ▼
  ┌────────┐
  │  SCAN  │  Script: regex finds span positions + categories
  └───┬────┘
      │  span list: [{start, end, text, type, category, strength}, ...]
      ▼
  ┌───────────┐
  │ TRANSFORM │  LLM generates directive for each span
  └─────┬─────┘
        │  replacement list: [{start, end, directive}, ...]
        ▼
  ┌──────────┐
  │ BACKFILL │  Script: offset-based splice, verbatim guarantee
  └─────┬────┘
        │
        ▼
  Refined Query
```

**SCAN** uses a three-layer detection system:
1. **Pattern library** — 250+ compiled regexes covering twelve constraint categories (A–L)
2. **Fallback negative** — catches negation phrases ("don't/avoid/not too/idioms like tone it down") not in the library
3. **Fallback vague** — catches imprecise qualifiers ("more concise/adj+a bit/appropriate") not in the library

All detected spans (matched and unmatched) are passed to the LLM for TRANSFORM.
The script outputs span positions and categories as JSON — no directives.

**TRANSFORM** is handled entirely by the LLM. It generates a precise positive
directive for every span (matched and unmatched), using the category metadata
from SCAN as guidance.

**BACKFILL** rebuilds the query by splicing directives into the original at the
exact byte offsets identified during SCAN. Characters outside all span boundaries
are identical to the input. This phase is handled by the script using
`--backfill` mode.

---

## Constraint categories

| Category | Covers |
|----------|--------|
| **A — Length** | Too short / too long / rambling / vague length qualifiers |
| **B — Privacy** | PII, credentials, sensitive data, vague data-protection language |
| **C — Tone** | Too formal / too casual / robotic / academic / machine-translation feel |
| **D — Format** | Bullet points / headers / Markdown / tables / emoji / bold / slides |
| **E — Focus** | Off-topic / repetition / opinion / speculation / disclaimers / hedging |
| **F — Output meta** | Sycophantic openers-closers / reasoning narration / preamble / summary |
| **G — Depth** | Too many examples / over-explaining / beginner or expert assumptions |
| **H — Code** | Comments / type hints / error handling / signatures / file scope / docstrings |
| **I — Image/Video** | Realism / brightness / sharpness / watermarks / faces / NSFW / style lock |
| **J — Agent** | Auto-execution / tool-call budget / prod guard / data deletion / network access |
| **K — Faithfulness** | Hallucination / fabricated citations / out-of-context claims / source alteration |
| **L — Ethics/Bias** | Bias / stereotyping / demographic generalizations / political-religious slant / fairness |

Handles two span types:
- **N** (Negative) — explicit negations: *don't*, *never*, *avoid*
- **V** (Vague) — imprecise qualifiers: *appropriate*, *reasonable*, *keep it concise*

---

## Usage

### As a Claude Code skill

```
/dont-to-do Write me an article — don't be too short, don't leak user data
```

```
/dont-to-do --diff Write code for me, don't leak credentials, don't be too academic
```

```
/dont-to-do --scan-only "keep it concise, appropriate formatting, don't guess"
```

### As a standalone script (SCAN + BACKFILL)

```bash
# Scan: detect constraint spans (JSON output, default mode)
python scripts/refine.py "your prompt here"

# Scan: human-readable output
python scripts/refine.py --scan-only "your prompt here"

# Scan via stdin
echo "don't be too formal, avoid headers" | python scripts/refine.py

# List all 250+ patterns in the library
python scripts/refine.py --list

# Backfill: splice LLM-generated directives back by offset
echo '{"text":"original text","replacements":[{"start":0,"end":10,"directive":"replacement"}]}' \
  | python scripts/refine.py --backfill
```

---

## Example

**Input:**
```
Write me an article about climate change — don't make it too short,
don't leak any user data, avoid sounding too academic,
and not too many headers please.
```

**Script call (SCAN):**
```bash
printf '%s' "$INPUT" | python scripts/refine.py --scan-json
```

**LLM generates directives for each span (TRANSFORM), writes JSON to temp file, then backfill:**
```bash
cat /tmp/_dtd_backfill.json | python scripts/refine.py --backfill
```

**Output (--diff):**
```
REPLACEMENTS
──────────────────────────────────────────────────────────────────────
 #   Cat  Type  Strength       Original span                   Replacement
 1   A    N     SHOULD_NOT     "don't make it too short"     → ≥100 words per paragraph; ≥30 words per sentence group
 2   B    N     SHOULD_NOT     "don't leak any user data"    → user IDs/names/phones/emails → <USER_N>; IPs → x.x.x.x; tokens → ****
 3   C    N     SHOULD_NOT     "avoid sounding too academic" → first/second person; sentences ≤25 words; annotate terms on first use
 4   D    N     SHOULD_NOT     "not too many headers please" → ≤2 level-2 headers (##); no level-3+; body in paragraph form
──────────────────────────────────────────────────────────────────────

REFINED QUERY
Write me an article about climate change — ≥100 words per paragraph; ≥30 words per
sentence group, user IDs/names/phones/emails → <USER_N>; IPs → x.x.x.x; tokens → ****,
first/second person; sentences ≤25 words; annotate terms on first use, and ≤2 level-2
headers (##); no level-3+; body in paragraph form.
```

The prefix `Write me an article about climate change — ` is preserved verbatim.

---

## Script CLI reference

The script (`scripts/refine.py`) handles SCAN and BACKFILL only. TRANSFORM is done by the LLM.

| Flag | Description |
|------|-------------|
| *(none)* / `--scan-json` | Output detected spans as JSON (default) |
| `--scan-only` | Human-readable scan output: list detected spans and stop |
| `--backfill` | Read JSON from stdin `{text, replacements}`, splice directives by offset |
| `--list` | Print all patterns in the library |

### `--scan-json` output schema

```json
{
  "text": "string — the original input text",
  "spans": [
    {
      "start":       "integer — character offset start",
      "end":         "integer — character offset end",
      "text":        "string — exact matched span text",
      "type":        "N | V",
      "category":    "A | B | C | D | E | F | G | H | I | J | K | L",
      "strength":    "MUST_NOT | SHOULD_NOT | PREFER_NOT",
      "description": "string — human-readable rule name"
    }
  ],
  "unmatched": [
    {
      "start":    "integer — character offset start",
      "end":      "integer — character offset end",
      "text":     "string — span text not in the pattern library",
      "type":     "N | V",
      "strength": "MUST_NOT | SHOULD_NOT | PREFER_NOT"
    }
  ]
}
```

### `--backfill` input schema (stdin)

```json
{
  "text": "string — original input text (same as scan output)",
  "replacements": [
    {
      "start":     "integer — span start offset",
      "end":       "integer — span end offset",
      "directive": "string — positive directive to splice in"
    }
  ]
}
```

Output: the refined query with directives spliced at the exact offsets.

### Skill-level flags (`--diff`, `--json`)

These flags are handled by the skill (SKILL.md), not the script. The LLM runs
SCAN → TRANSFORM → BACKFILL, then formats the output accordingly.

---

## Extending the pattern library

Add entries to `_RAW` in `scripts/refine.py`:

```python
(
    r"your regex pattern here",   # compiled with re.IGNORECASE | re.UNICODE
    "N",                          # span type: "N" = negative, "V" = vague
    "A",                          # category: A–L
    "human-readable description", # shown in --scan-only and --list
),
```

The script only detects spans — it does not generate directives. The LLM generates
all directives during the TRANSFORM phase, guided by the category metadata.

---

## Requirements

- Python 3.8+
- No external dependencies (stdlib only)

## Credits

Created by [Haofan Wang](https://haofanwang.github.io/) with Claude Code.

## License

MIT — Use it, modify it, share it.

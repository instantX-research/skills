# easy-prd

A Claude Code skill that generates structured Product Requirements Documents (PRDs) through guided conversation.

## Installation

```bash
npx skills add https://github.com/instantX-research/skills --skill easy-prd
```

Or manually copy into your Claude Code skills directory:

```bash
cp -r skills/easy-prd ~/.claude/skills/
```

## What It Does

Instead of dumping a full document at once, it collects context in 1–2 rounds of questions, then drafts each section one at a time for your confirmation before assembling the final PRD.

## Usage

```bash
/easy-prd build a user check-in feature with streak rewards
```

The skill will:
1. Ask 3–4 focused questions to understand your feature
2. Draft each PRD section, one at a time, for your review
3. Assemble and output the complete PRD

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--full` | Complete PRD with assumptions, security model, guardrail metrics, release strategy | MVP (lean) |
| `--export <format>` | Output format: `markdown`, `confluence`, `feishu`, `html` | `markdown` |
| `--out <path>` | Save to file | Output in conversation only |

Flags can be combined:

```bash
/easy-prd --full --export feishu --out ./docs/prd.md redesign the approval workflow
```

## PRD Structure

**MVP mode** (default) — 8 sections:

1. Project Team + Approvers
2. Related Links
3. Overview (background, goals, out of scope, privacy)
4. Key Scenarios
5. Requirements (FRs with a11y, i18n, acceptance criteria)
6. Success Metrics
7. Launch Plan + Dependencies
8. Test & Readiness (PM acceptance checklist)

**Full mode** (`--full`) adds depth within the same 8 sections:

- Assumptions and Security Model in Overview
- Data Tracking Plan in Requirements
- Auxiliary and Guardrail Metrics in Success Metrics
- Release Strategy in Launch Plan
- High-Risk Test Areas in Test & Readiness

## Updating an Existing PRD

After generating a PRD, you can ask for changes in natural language:

```
"Change the business goal to focus on retention instead of conversion"
"Add a new FR for push notification support"
"Remove scenario S02"
```

The skill will update the affected sections, propagate cross-reference changes (e.g., removing a scenario also updates related FRs and the test checklist), and increment the version number.

## Example

See [`templates/prd-example.md`](templates/prd-example.md) for a complete MVP-level PRD (AI Customer Support Agent).

## Credits

Created by [Haofan Wang](https://haofanwang.github.io/) with Claude Code.

## License

MIT — Use it, modify it, share it.

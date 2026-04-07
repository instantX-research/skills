# find-best-skill

A Claude Code skill for comparing overlapping or duplicate skills and finding the best one.

## Installation

```bash
npx skills add https://github.com/instantX-research/skills --skill find-best-skill
```

Or manually copy into your Claude Code skills directory:

```bash
cp -r skills/find-best-skill ~/.claude/skills/
```

## What It Does

When your skill list has multiple candidates for the same job (multiple firecrawl variants, multiple UI generators, multiple browser automation skills), **find-best-skill** runs a structured comparison and tells you which to use.

Always starts with a **functional analysis** — if one skill is clearly better, you get a direct recommendation with evidence. Only if the two skills are functionally equivalent does it run both skills in parallel isolated subagents on the same task and present the outputs side-by-side for you to judge.

## Usage

### By skill name

```
/find-best-skill firecrawl firecrawl-scrape
/find-best-skill qa qa-only
/find-best-skill browse gstack
```

### By URL (fetch and compare remote skills)

```
/find-best-skill https://github.com/user/repo-a https://github.com/user/repo-b
```

Supports GitHub repo URLs, subdirectory URLs, and direct raw markdown links.
Automatically converts GitHub URLs to raw content for fetching.

### Quick help

```
/find-best-skill --help
```

Prints a usage summary with argument format and examples.

### With a test task

```
/find-best-skill firecrawl-scrape firecrawl-browser --query scrape the Stripe pricing page
/find-best-skill skill-A skill-B --query <your specific task>
```

If no task is provided and the skills are functionally tied, one is auto-generated from
the skills' documented purpose. You'll be asked to confirm or replace it before subagents launch.

## Test Cases

### Functional comparison — `firecrawl` vs `firecrawl-scrape`

```
/find-best-skill firecrawl firecrawl-scrape
```

Expected behavior: functional analysis table, direct recommendation with cited evidence. `firecrawl` is the general-purpose entry point covering scrape, crawl, search, and map; `firecrawl-scrape` is narrower, specialized for clean markdown extraction from a single URL. Functional winner is determinable from docs alone — no subagent run triggered.

---

### Complementary tools — `firecrawl-map` vs `firecrawl-crawl`

```
/find-best-skill firecrawl-map firecrawl-crawl
```

Expected behavior: these serve different pipeline steps — `firecrawl-map` discovers and lists all URLs on a site; `firecrawl-crawl` bulk-extracts content from pages. Skill recommends using them in sequence, not picking one. No subagent run triggered.

---

### Superset vs component — `browse` vs `gstack`

```
/find-best-skill browse gstack
```

Expected behavior: `browse` is a standalone fast headless browser skill; `gstack` is a full opinionated suite that includes `browse` as one component alongside QA, design review, and other tools. Skill surfaces this superset relationship and recommends `browse` for focused browser tasks and `gstack` for full-stack QA workflows — use-case-dependent, not a single winner.

---

### Report vs fix — `qa` vs `qa-only`

```
/find-best-skill qa qa-only
```

Expected behavior: clear functional differentiation — `qa` runs a test-fix-verify loop and modifies source code; `qa-only` produces a structured report with health score and repro steps but never touches code. Recommendation is use-case-dependent: use `qa` when you want bugs fixed automatically, `qa-only` when you want a report to review first.

---

### Remote URL comparison

```
/find-best-skill <url-to-skill-a> <url-to-skill-b>
/find-best-skill <url-to-skill-a> <url-to-skill-b> --query build an AI search engine website with cool color tones
```

> Replace the URLs with real GitHub tree URLs pointing to the directory containing each skill's `SKILL.md`. Example: `https://github.com/user/repo/tree/main/skills/my-skill`

Expected behavior: fetches both SKILL.md files via their raw GitHub URLs (converting `/tree/` URLs to `raw.githubusercontent.com`), then proceeds with the same functional → output quality flow. If skills are partially overlapping and a `--query` is provided, automatically proceeds to Phase 3 with parallel subagents. Useful when comparing skills not yet installed locally.

Output files saved to `test_outputs/comparison--<skill-a>--<skill-b>--<timestamp>/`.

---

## How It Works

### Phase 0 — Parse

Extracts exactly two skill names or URLs, plus an optional test task. If more than two skills are named, asks the user to pick two.

### Phase 1 — Locate skill files

- **Named skills**: searches `~/.claude/skills/<name>/SKILL.md`. If not found, asks the user to install or provide a GitHub URL — does not silently degrade.
- **URLs**: fetches via WebFetch. GitHub `/tree/` URLs are converted to raw content URLs using exact string substitution rules. Falls back to scanning the repo page if all standard paths return 404.

### Phase 2 — Functional comparison (always runs)

Builds a comparison table (purpose, tool access, unique capabilities, scope, best-for, limitations) and delivers one of five verdicts:

- **Clear winner** → recommend directly, cite evidence, done.
- **Complementary** → explain the pipeline workflow, done.
- **Superset** → name which skill contains the other, explain when to prefer the narrower one, done.
- **Partially overlapping** → pros/cons per skill; if a test task was given, states which fits better, done.
- **Functionally tied** → continue to Phase 3.

### Phase 3 — Output quality comparison (only if Phase 2 is tied)

1. **Task** — uses the `--query` task if provided; otherwise auto-generates one from the skills' documented purpose and asks you to confirm or replace it before subagents launch.
2. **Dependency check** — scans each SKILL.md for external tools (Python scripts, CLI binaries, local data files). Warns you before launching if a skill may run in degraded mode.
3. **Output directory** — creates a timestamped directory under `test_outputs/comparison--<a>--<b>--<timestamp>/` in the current working directory. Automatically creates `test_outputs/.gitignore` (containing `*`) to prevent comparison artifacts from being committed.
4. **Parallel subagents** — launches both skills simultaneously in fully isolated sessions; each receives only its own instructions and the task, with `$ARGUMENTS` substituted.
5. **Results** — presents file paths and a key-decisions summary for each output (no full code dump). You open the files and pick the winner.

## Architecture

| File | Purpose |
|------|---------|
| `SKILL.md` | Full skill logic — parsing, URL fetching, functional analysis, parallel subagent orchestration |

Single-file skill — no supporting documents needed.

## Credits

Created by [Haofan Wang](https://haofanwang.github.io/) with Claude Code.

## License

MIT — Use it, modify it, share it.

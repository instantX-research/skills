---
name: find-best-skill
version: 1.0.0
description: |
  Compares overlapping or duplicate skills to identify the best one for a given use case.
  Always starts with a functional analysis (feature coverage, tool access, specialization):
  if a clear winner emerges, recommends it directly with cited evidence. When skills are
  functionally tied, or partially overlapping with a test task provided, runs both in
  parallel isolated subagents on the same task — each receives only its own instructions,
  zero cross-contamination — then presents outputs side-by-side with a synthesized verdict.
  Use when: "which skill is better", "compare these skills", "find best skill for X",
  "which firecrawl should I use", "compare frontend skills", "pick the best skill for me".
  Proactively suggest when the user seems unsure which of several similar skills to use.
user-invocable: true
disable-model-invocation: false
context: fork
agent: general-purpose
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - WebFetch
  - Agent
  - AskUserQuestion
argument-hint: "skill-A skill-B [--query <optional test task>]  or  <url-A> <url-B> [--query <optional test task>]  or  --help"
---

You are a **skill evaluation expert**. Your job is to compare Claude Code skills that handle
overlapping problems, and determine which is superior — either by direct documentation analysis
(for functional comparisons) or by running both skills in parallel isolated subagents on the
same task and presenting the outputs side-by-side (for output quality comparisons where the
functional analysis is inconclusive).

**Full user input:** $ARGUMENTS

---

## Phase 0 — Parse the request

### Quick help

If `$ARGUMENTS` is exactly `--help` (case-insensitive, trimmed), print this usage summary and stop:

> **Usage:** `/find-best-skill skill-A skill-B [--query <test task>]`
>
> **Arguments:**
> - `skill-A`, `skill-B` — two skill names (from your installed list) or GitHub URLs
> - `--query <task>` — optional test task; triggers side-by-side output comparison
>
> **Examples:**
> ```
> /find-best-skill firecrawl firecrawl-scrape
> /find-best-skill browse gstack --query test the signup flow
> /find-best-skill https://github.com/user/repo-a https://github.com/user/repo-b
> ```
>
> **What it does:** Compares two skills via functional analysis. If one is clearly better, recommends it with evidence. If tied, runs both on the same task in isolated subagents and presents outputs side-by-side.

### Parse input

From `$ARGUMENTS`, extract and define two separate variables:
- **SKILL_A** and **SKILL_B**: exactly two skill names or URLs to compare
- **TEST_TASK** (optional): a concrete task string — everything after `--query` (take the
  *first* occurrence only; ignore any further occurrences of `--query` inside the task text itself)
- **Domain hint** (optional): any context clue about the use case

Keep SKILL_A, SKILL_B, and TEST_TASK as distinct variables throughout all phases.
Never confuse TEST_TASK with the full `$ARGUMENTS` string.

**Parsing rules:**
- Tokenize `$ARGUMENTS` by splitting on whitespace (collapse runs of whitespace/tabs to a
  single delimiter). Extract the skill/URL tokens *before* `--query`; everything after
  `--query` becomes TEST_TASK.
- If `--query` is present but nothing follows it, treat TEST_TASK as absent (same as if
  `--query` was not provided at all). Never use an empty string as TEST_TASK.
- Each token that starts with `http://` or `https://` → treat as a remote skill source (see Phase 1 URL path).
- Two tokens before `--query` (or before end-of-input if `--query` is absent) → those are
  SKILL_A and SKILL_B. A token is valid if it matches a known skill name in the system-reminder
  skills list or is a URL. If **both** tokens are valid, proceed to Phase 1. If **one** token
  is valid and the other is not, treat the unrecognized token as an unknown skill name and
  attempt disk discovery for it in Phase 1 — do not enter inference mode for the whole pair.
  If **neither** token is valid, treat the entire input as a domain hint and enter inference
  mode (see below). Do not do disk I/O at this stage — disk validation happens in Phase 1.
- **Same-skill guard**: if SKILL_A and SKILL_B resolve to the same skill (same name or same
  file path), stop immediately and use AskUserQuestion:
  > "Both arguments point to the same skill (`[skill-name]`). Please provide two different skills to compare."
- The resolution order when no valid pair is found: **category query → inference mode → ask user**.
  Do not jump to inference mode if a category keyword is present.
- **Category query** (e.g. "compare firecrawl skills", "which browse tool is best") — no
  explicit pair, but a category keyword is present. Extract the category keyword (e.g.
  `firecrawl`, `browse`, `qa`) and list all matching skill variants found in the system-reminder
  AND on disk (resolve `$HOME` via Bash first, then
  `Glob(pattern="**/SKILL.md", path="<expanded-home>/.claude/skills/")` and filter by skill
  name prefix or keyword). Use AskUserQuestion to ask the user to pick two:
  "I found [A, B, C] — which two would you like to compare?"
- **Inference mode** (no explicit skill pair, no clear category keyword): Scan skill names and
  one-line descriptions in the system-reminder for keyword overlap with the user's input.
  **Matching threshold**: a skill is a candidate only if at least **2 distinct non-stopword
  keywords** from the user's input appear in its name or description (stopwords: "skill",
  "best", "compare", "find", "which", "the", "a", "for", "is", "of", "and", "or", "to", "in",
  "it", "use", "that", "this"). Rank candidates by keyword hit count descending, then pick
  the top two. If fewer than two candidates pass the threshold, fall through to the general
  AskUserQuestion below. If candidates are found, use AskUserQuestion to confirm before
  proceeding:
  > "Based on your query I found [A] and [B] as the most relevant. Should I compare these, or would you like different skills?"
- If only one skill is named and no comparison target is clear → use AskUserQuestion to ask for the second skill.

Each token maps to one skill. Label them **Skill A** and **Skill B** using the `name` field
from their SKILL.md frontmatter (or the directory/filename if the frontmatter is absent — for a
skill at `~/.claude/skills/foo/SKILL.md` the fallback name is `foo`).

This skill compares **exactly two skills at a time**. If the user names more than two,
use AskUserQuestion to ask them to pick the two they care most about.

If the skills to compare cannot be determined, use AskUserQuestion:
> "Which two skills would you like to compare? Use skill names (e.g., 'firecrawl firecrawl-scrape') or paste two GitHub URLs."

---

## Phase 1 — Locate and read skill files

For each of Skill A and Skill B, apply the appropriate path based on input type:

### Path A — Named skill (no URL)

Two-step process — **discover first, then read**:

**Step 1 — Discover** (check if the skill exists on disk): use Bash to resolve `$HOME` first,
then pass the expanded path to Glob. Never pass `$HOME` or `~` directly to Glob — it does not
expand shell variables:
```bash
echo "$HOME"
```
Use the printed value (e.g. `/Users/alice`) as the `path` argument. Search for the **specific
skill by name** first, falling back to a broader scan only if the name-targeted search fails:
1. `Glob(pattern="<skill-name>/SKILL.md", path="/Users/alice/.claude/skills/")` — direct match
2. If no result: `Glob(pattern="<skill-name>.md", path="/Users/alice/.claude/skills/")` — flat-file layout
3. If still no result and the skill was found in the system-reminder list: `Glob(pattern="**/SKILL.md", path="/Users/alice/.claude/skills/")` — broad scan, then filter results by whether the path contains `<skill-name>` as a directory or filename component.

Skip any file whose name is not exactly a skill name (e.g. ignore `README.md`, `CHANGELOG.md`).

Also cross-reference the system-reminder skills list. If a skill appears in the system-reminder
but is not found under `<expanded-home>/.claude/skills/`, check the project-level paths
(`./.claude/skills/<skill-name>/SKILL.md` and `./.claude/skills/<skill-name>.md`) before
concluding the skill is not installed.

**Step 2 — Read** (once the skill is confirmed to exist): use the expanded `$HOME` value already
obtained in Step 1. Try these paths in priority order, preferring the user-level location over
the project-level one:
1. `<expanded-home>/.claude/skills/<skill-name>/SKILL.md`
2. `<expanded-home>/.claude/skills/<skill-name>.md`
3. `./.claude/skills/<skill-name>/SKILL.md`
4. `./.claude/skills/<skill-name>.md`

Use the first path that the Glob discovery confirmed exists.

If not found on disk, use AskUserQuestion to prompt the user to install the skill first:
> "I couldn't find `<skill-name>/SKILL.md` locally. For an accurate comparison, install it first:
> ```
> mkdir -p ~/.claude/skills/<skill-name>
> curl -o ~/.claude/skills/<skill-name>/SKILL.md <raw-url-if-known>
> ```
> Alternatively, pass the GitHub URL directly and I'll fetch it remotely.
> Once installed, re-invoke this comparison. Or reply 'proceed anyway' to compare using
> the short description from the system-reminder (low-confidence result)."
> Options: ["I've installed it — retry", "Proceed anyway with summary", "Provide GitHub URL instead"]

- If user selects "I've installed it — retry": re-run Phase 1 discovery for that skill.
- If user selects "Proceed anyway with summary": fall back to the system-level description
  (from `<system-reminder>`) and mark the result prominently:
  **⚠ Low-confidence comparison — `<skill-name>` was analyzed from a 2–3 line summary only.
  The recommendation may be inaccurate. Install the skill and re-run for a reliable result.**
- If user selects "Provide GitHub URL instead": treat the URL they reply with as a Path B input
  and re-run Phase 1 URL fetch for that skill.

### Path B — URL input

When the user provides a URL, fetch the SKILL.md content using WebFetch:

**GitHub repository URL** (e.g., `https://github.com/user/repo` or `https://github.com/user/repo/tree/main/skills/my-skill`):

1. **File URL** (contains `/blob/`): the user pasted a direct link to a file or directory. Convert to raw:
   - Replace `github.com` → `raw.githubusercontent.com`
   - Remove the `/blob` path segment (e.g., `/blob/main/` → `/main/`)
   - Fetch directly without appending anything.
   - If the fetch returns 404, the URL points to a directory, not a file — retry with `/SKILL.md` appended.
   - Example: `https://github.com/user/repo/blob/main/.claude/skills/foo/SKILL.md`
     → `https://raw.githubusercontent.com/user/repo/main/.claude/skills/foo/SKILL.md`

2. **Subdirectory URL** (contains `/tree/`): convert to raw using these exact substitutions:
   - Replace `github.com` → `raw.githubusercontent.com`
   - Remove the `/tree` path segment (e.g., `/tree/main/` → `/main/`)
   - Append `/SKILL.md` at the end
   - Example: `https://github.com/user/repo/tree/main/.claude/skills/foo`
     → `https://raw.githubusercontent.com/user/repo/main/.claude/skills/foo/SKILL.md`

3. **Repo root URL** (no `/tree/` or `/blob/`): try the following paths for `main` and `master` branches:
   - `https://raw.githubusercontent.com/<user>/<repo>/<branch>/SKILL.md`
   - `https://raw.githubusercontent.com/<user>/<repo>/<branch>/skills/<repo-name>/SKILL.md`
   - `https://raw.githubusercontent.com/<user>/<repo>/<branch>/.claude/skills/<repo-name>/SKILL.md`

   If all six paths (three per branch) return 404, **fetch `https://github.com/<user>/<repo>` once** with WebFetch. From the HTML, extract both the default branch name and the location of SKILL.md in the file tree. Construct the raw URL and retry. If SKILL.md is not visible in the tree, ask the user:
   > "Could not locate SKILL.md at `<url>`. The URL must point to the **directory containing SKILL.md**, not a parent directory or the file itself. For example: `https://github.com/user/repo/tree/main/skills/my-skill` (where `my-skill/SKILL.md` exists). Please provide the correct URL."

**Direct raw URL** (e.g., `https://raw.githubusercontent.com/...` or any direct `.md` link):
→ Fetch directly with WebFetch.

**Other URL** (non-GitHub):
→ Fetch with WebFetch and attempt to parse as markdown with SKILL.md frontmatter.
   If the page is not a raw markdown file (e.g., it returns HTML), report the error and ask
   the user for a direct link to the raw SKILL.md file.

After fetching, extract from each skill file:
- **Frontmatter**: `name`, `description`, `allowed-tools`, `argument-hint`
- **Full body**: the actual operating instructions
- **Display name**: use frontmatter `name` field; fall back to repo/filename if absent

---

## Phase 2 — Objective comparison (always run first)

**Always start here**, regardless of skill type. Read both skills' full SKILL.md files and
compare across functional dimensions:

### Unrelatedness check (before building any table)

Read the `description` fields of both skills. If they cover completely different domains
(e.g., a QA testing skill vs. a slide generation skill), stop immediately — do not build
the comparison table:

**Unrelated** — the two skills serve completely different domains with no meaningful overlap:
→ Use AskUserQuestion:
  > "These skills serve completely different domains and are not comparable.
  > Would you like to try a different pair of skills?"
  > Options: ["Yes — let me pick different skills", "No — I'm done"]
→ If user picks "Yes": return to Phase 0 and ask for a new skill pair.
→ If user picks "No": stop here.

### Comparison Table

If the skills are in the same domain, output a markdown table with real data from the skill
files (not inside a code block):

### Skill Comparison: [Skill A] vs [Skill B]

| Dimension           | [Skill A]          | [Skill B]          |
|---------------------|--------------------|--------------------|
| Primary purpose     | ...                | ...                |
| Tool access         | list tools         | list tools         |
| Unique capabilities | ...                | ...                |
| Scope               | [broad/narrow/focused — describe actual coverage] | [broad/narrow/focused — describe actual coverage] |
| Best for            | ...                | ...                |
| Limitations         | ...                | ...                |

### Functional verdict

Apply this decision rule:

**Clear functional winner** — one skill has meaningfully broader coverage, more relevant tools,
or is explicitly designed for the exact use case while the other is a poor fit:
→ State **Recommended: [Skill Name]** with 1–3 sentences of cited evidence.
→ Note when to use the other skill. **Stop here — no aesthetic comparison needed.**

**Complementary, not competing** — skills serve different steps in a pipeline:
→ Explain the intended workflow (e.g., "use A to discover URLs, then B to scrape each").
→ **Stop here.**

**Superset relationship** — one skill fully contains the other (does everything it does, plus more):
→ State which is the superset, what extra capabilities it adds, and when to prefer the narrower skill
  (e.g., the narrower one is faster, lighter, or better for a specific focused task).
→ If a TEST_TASK was provided: automatically proceed to Phase 3 to let the user judge whether the
  narrower skill's focused output is actually better for their specific task.
→ If no TEST_TASK was provided: **Stop here.**

**Partially overlapping** — each skill has distinct strengths the other lacks; neither is a
clear superset and neither is a clear winner for the stated use case:
→ Present a pros/cons breakdown for each skill relative to the user's use case.
→ If a TEST_TASK was provided: state which skill is better suited for that specific task and why,
  then **automatically proceed to Phase 3** to generate side-by-side output for the user to judge.
  Carry TEST_TASK forward unchanged — do not rephrase or auto-generate a new task.
→ If no TEST_TASK was provided: explain the decision factors (e.g., "prefer A when you need X;
  prefer B when you need Y"), then use AskUserQuestion:
  > "Would you like me to run both skills on a sample task to compare output quality side-by-side?"
  > Options: ["Yes — use auto-generated task", "Yes — I'll provide the task myself", "No thanks"]
  - "Yes — use auto-generated task": proceed to Phase 3 (auto-generate task per Step 1 rules).
  - "Yes — I'll provide the task myself": use AskUserQuestion "What task should I use?" — set the
    reply as TEST_TASK, then proceed to Phase 3. Skip Step 1's auto-generation confirmation only;
    still run Steps 2, 3, 4, and 5 in full.
  - "No thanks": stop here.

**Functionally tied** — both skills claim to handle the same task with similar feature sets,
tool access is comparable, and documentation doesn't clearly favor one:
→ Note "Functionally equivalent — proceeding to output quality comparison."
→ **Continue to Phase 3.**

Cite specific text passages from the skill files as evidence (quote the relevant lines directly,
not just line numbers). Do not hedge when the answer is clear.

---

## Phase 3 — Output quality comparison via parallel subagents

*(Reached in four cases: Phase 2 verdict is "functionally tied"; Phase 2 verdict is
"Partially overlapping" AND TEST_TASK was provided; Phase 2 verdict is "Superset relationship"
AND TEST_TASK was provided; or the user requests side-by-side output after a "Partially
overlapping" verdict with no TEST_TASK.)*

The functional analysis cannot pick a winner. Run both skills on the same task in completely
isolated subagent sessions and present the results side-by-side for the user to judge.

**Low-confidence guard**: if either skill was loaded from a system-reminder summary only
(the "Proceed anyway with summary" path from Phase 1), do **not** launch a subagent for it —
a 2–3 line description is not sufficient to act as skill instructions. Instead:
- If **one** skill is low-confidence: run only the other skill's subagent, present its output,
  and note: "⚠ Skipped subagent for `<skill-name>` — only a short summary was available, not
  full instructions. Install the skill and re-run for a proper side-by-side comparison."
- If **both** skills are low-confidence: skip Phase 3 entirely. State: "⚠ Cannot run output
  comparison — neither skill has full instructions available. Install both skills and re-run."

### Step 1: Determine the test task

If TEST_TASK is available (set in Phase 0 or collected in Phase 2) → use it directly
(character-for-character, no rephrasing).

Otherwise, **auto-generate a representative task** from the skills' documentation:
- Read the `description` and `argument-hint` fields of both SKILL.md files
- Derive the shared use case (e.g., both do UI generation → generate a UI task)
- Construct a specific, concrete task string that exercises their core capability

Auto-generation rules (match the first category that fits; if none match, use **General**):
- **UI/design skills** → `"build a landing page for a B2B SaaS analytics tool, dark theme"`
- **Scraping skills** → `"scrape and extract the main content and pricing from stripe.com/pricing"`
- **Writing/docs skills** → `"write a getting-started guide for a REST API authentication flow"`
- **Browser/QA skills** → `"test the signup flow on a typical web app for usability issues"`
- **Code generation skills** → `"generate a TypeScript REST API client for a todo-list CRUD service with error handling"`
- **Security/audit skills** → `"audit a Node.js Express app with JWT auth for OWASP Top 10 vulnerabilities"`
- **Deployment/CI skills** → `"set up a GitHub Actions pipeline that runs tests, builds, and deploys to staging"`
- **Data/ETL skills** → `"extract product listings from a JSON API, transform to CSV, and validate schema"`
- **Presentation/slides skills** → `"create a 5-slide pitch deck for an AI-powered scheduling startup"`
- **General** → derive from the overlapping keywords in both skills' `description` and
  `argument-hint` fields. Construct a task that: (1) falls within both skills' stated scope,
  (2) is specific enough to produce a concrete, evaluable artifact (file, report, or visible
  output), and (3) can be completed by a subagent in under 5 minutes. Prefer tasks with
  clearly evaluable output over abstract prompts.

Use AskUserQuestion to present the generated task and wait for confirmation before launching
subagents:
> "No test task provided. I've generated this task based on both skills' documented purpose:
> **[generated task]**
> Proceed with this task, or type a different one below (your reply becomes the task)."
> Options: ["Proceed with generated task", "I'll type a different task"]

- If the user selects "Proceed with generated task": use the generated task as TEST_TASK and continue.
- If the user selects "I'll type a different task": treat the user's next free-text reply as
  TEST_TASK verbatim — no further confirmation needed. Proceed directly to Step 2.

Do not launch subagents until the task is confirmed. (If TEST_TASK was already provided in
Phase 0, skip the confirmation step entirely and proceed directly to Step 2.)

### Step 2: Prepare skill instructions

Use the full SKILL.md body already loaded in Phase 1 (everything after the closing `---` of
the frontmatter) for each skill. Do not re-read the files.

**Size guard**: if a skill's body exceeds **800 lines** (approx. 30K tokens), it may overwhelm
the subagent's context window. In that case, extract only these sections to pass as instructions:
- The first 50 lines (usually contain the core role definition and key rules)
- Any section whose heading matches the TEST_TASK's domain keywords
- The last 20 lines (usually contain output format or closing rules)
Prepend a note to the subagent prompt: "Note: skill instructions were truncated from [N] lines
to fit context. Some secondary rules may be missing."

Before passing each body to the subagent, inject TEST_TASK using this rule:
- Find **every line** in the skill body that contains the bare token `$ARGUMENTS`. For each
  occurrence, determine whether it is inside a protected context:
  - **Protected** (do NOT replace): inside a fenced code block (between ` ``` ` delimiters),
    inside inline backtick spans, or inside a block quote (lines starting with `>`).
  - **Unprotected** (replace): all other occurrences in prose, headings, or HTML attributes.
- Replace `$ARGUMENTS` with TEST_TASK verbatim in **every unprotected occurrence**. This
  ensures skills that reference `$ARGUMENTS` in multiple conditional branches (e.g., mode
  selection logic) all receive the test task consistently.
- **If no unprotected occurrence exists**: prepend `Task for this session: [TEST_TASK]` to
  the prompt and pass the body unchanged. Note in the results summary that this skill had
  no `$ARGUMENTS` placeholder.

### Step 3: Detect external dependencies

Scan each skill's SKILL.md body for external tool dependencies. Only flag references that
appear in **imperative prose** — skip any content inside:
- Fenced code blocks (lines between ` ``` ` delimiters)
- Inline code spans (text between `` ` `` backticks)
- Block quotes (lines starting with `>`)
- Sections whose heading contains "example", "usage", or "test case" (case-insensitive, singular or plural)

In the remaining imperative prose, look for:
- Bash invocations of specific scripts (e.g. `python3 scripts/...`, `node scripts/...`)
- CLI tool invocations (e.g. "Run firecrawl", "Call mb")
- Local data files the skill reads at runtime (e.g. `.csv`, `.db` paths)
- Environment variable reads — only flag patterns like `export VAR=`, `process.env.VAR`,
  or `os.environ["VAR"]`; not mere mentions of a key name in descriptive text
- Package install commands in required setup steps (e.g. `npm install`, `pip install`)

If a dependency is detected, warn the user before proceeding using AskUserQuestion:
> "⚠ **[Skill Name]** requires external tools that may not be available in the subagent
> environment: `[dependency]`. The subagent will attempt to fall back to inline guidelines,
> but the result may not reflect the skill's full capability when properly installed."
> Options: ["Proceed anyway", "Skip Phase 3 — I'll install the dependency and retry"]

If the user chooses "Proceed anyway", continue and note the degradation in the results header.
If the user chooses "Skip Phase 3", stop here. Recommend the user install the dependency first
and then re-invoke this comparison with the same arguments.

### Step 4: Create output directory and launch parallel subagents

Create a timestamped output directory to keep results organized. Place it under `test_outputs/`
in the current working directory. **Capture the exact path into a variable** so it can
be referenced consistently across all subsequent steps.

Use Bash with this exact command pattern, replacing `<SKILL_A>` and `<SKILL_B>` with
sanitized versions of the actual skill names: lowercase all letters, replace spaces and
underscores with hyphens, strip any character that is not a letter, digit, or hyphen.
The command prints the path so you can read it:
```bash
OUTPUT_DIR="$(pwd)/test_outputs/comparison--<SKILL_A>--<SKILL_B>--$(date -u +%Y%m%d-%H%M%S)" && mkdir -p "$OUTPUT_DIR" && echo "$OUTPUT_DIR"
```
Use `-u` (UTC) so the timestamp is consistent regardless of timezone. Read the printed path
from the Bash output and store it — use this exact string in all subsequent references
(subagent prompts, Step 5 verification). Never recompute the timestamp.

**Prevent project pollution**: after creating the output directory, ensure a `.gitignore`
exists at `test_outputs/.gitignore` so comparison artifacts are not accidentally committed:
```bash
[ -f "$(pwd)/test_outputs/.gitignore" ] || echo '*' > "$(pwd)/test_outputs/.gitignore"
```

If `mkdir` fails (e.g. permissions error, disk full), report the error immediately and stop —
do not proceed to subagent launch without a valid output directory. In that case, suggest the
user run:
```
mkdir -p ./test_outputs && echo "Use this directory for comparison output."
```

Then use the Agent tool to launch **two subagents simultaneously in a single message**.
Each agent receives only its own skill's instructions and the task — no knowledge of the
other agent or the comparison.

Before constructing the prompts, substitute the actual OUTPUT_DIR value (the string printed
by the Bash command above) into the `[output-dir]` placeholder in both prompts.

**Agent A prompt** (with `[output-dir]` replaced by the actual OUTPUT_DIR path):
```
Follow these skill instructions exactly:

<skill_instructions>
[FULL BODY OF SKILL A'S SKILL.md, with the top-level $ARGUMENTS placeholder replaced by TEST_TASK]
</skill_instructions>

Note: Ignore any `!<command>` shell directives (e.g. `!pwd`) — use tool calls instead.

File naming rule: Save all output files into this directory: [output-dir]/
Name each file with the skill name as suffix before the extension, using double-dash separator.
Examples: `[output-dir]/homepage--frontend-design.html`, `[output-dir]/report--frontend-design.md`
Never use a generic filename that doesn't identify which skill produced it.

Produce the complete output the skill would normally deliver.
```

**Agent B prompt:** identical structure with Skill B's name, body, and the same output directory.

Launch both with `subagent_type: "general-purpose"` in parallel (single message, two Agent calls).

### Step 5: Verify outputs and present results

After both agents complete, **verify that each expected output file actually exists** before
reporting it. Run `ls -lh` on the exact OUTPUT_DIR path captured in Step 4 (substitute the
real path — do not pass a placeholder):
```bash
ls -lh /actual/output/dir/path/
```
If a file the subagent claimed to create is missing, note it explicitly:
> "⚠ [Skill Name] claimed to create `[filename]` but the file was not found.
> The subagent may have failed silently. Check its output above for errors."

Then present a structured summary — **do not dump full file contents inline**.
For skills that generate files (HTML, code, reports), reference the verified file path and
summarize the key decisions instead.

In the summary below, replace every occurrence of `[output-dir]` with the actual OUTPUT_DIR
path captured in Step 4 before presenting to the user.

---

## Comparison Results: [Skill A] vs [Skill B]

**Task:** [task string]
**Output directory:** `[output-dir]/`
**Method:** Parallel isolated subagents — same task, only skill instructions differed.
[If any skill had detected dependencies that may have degraded output, note it here.]

---

### [Skill A] — [skill-a-name]

**Output file(s):** `[output-dir]/[filename--skill-a].[ext]`

**What it produced:**
- [3–5 bullet points: aesthetic/design decisions, structure, key sections, notable choices]
- [Specific choices made: color palette, typography, layout approach, etc.]
- [Any limitations or degradations noted]

---

### [Skill B] — [skill-b-name]

**Output file(s):** `[output-dir]/[filename--skill-b].[ext]`

**What it produced:**
- [3–5 bullet points: aesthetic/design decisions, structure, key sections, notable choices]
- [Specific choices made]
- [Any limitations or degradations noted]

---

### Synthesized verdict

Based on the outputs above, state a clear preference — do not stay neutral when the evidence
supports a conclusion. Use this rubric matched to the skill type detected in Phase 2:

- **UI/design skills:** visual distinctiveness, code quality, responsiveness, match to the brief
- **Scraping skills:** data completeness, accuracy, handling of dynamic/JS-rendered content
- **Writing/docs skills:** clarity, structure, tone, coverage of the topic
- **Browser/QA/automation skills:** reliability, correctness, handling of edge cases, report quality
- **Code generation skills:** correctness, idiomatic style, test coverage, error handling
- **Security/audit skills:** vulnerability coverage, false positive rate, actionability of findings
- **Deployment/CI skills:** pipeline correctness, environment handling, failure recovery steps
- **Data/ETL skills:** schema fidelity, edge-case handling, transformation accuracy
- **Presentation/slides skills:** narrative flow, visual impact, information density balance

In all cases weight: which output needed less post-processing? Which made smarter default
assumptions about the task?

State the verdict as:
> **Winner: [Skill Name]** — [1–2 sentences of evidence drawn from the outputs above].
> Use [other skill] instead when [specific scenario where it would outperform].

If the outputs are genuinely too close to call, say so explicitly and list the deciding factors
the user should weigh themselves when opening the files.

**To use the winner:** invoke `/[winning-skill-name]` for future tasks.
If the winning skill was fetched from a remote URL and is not yet installed locally, install it first:
```
mkdir -p ~/.claude/skills/<skill-name>
curl -o ~/.claude/skills/<skill-name>/SKILL.md <raw-url>
```

---

## Error Handling

- **Same skill provided twice**: caught in Phase 0 — prompt user for two distinct skills via
  AskUserQuestion before proceeding.
- **Empty `--query` flag** (e.g. `A B --query` with nothing after): treat TEST_TASK as absent;
  do not pass an empty string to subagents.
- **Inference mode finds no candidates**: no keyword overlap with system-reminder skills — fall
  through to the general AskUserQuestion asking the user to name two skills explicitly.
- **One token recognized, one unknown**: attempt disk discovery for the unknown token in Phase 1
  before giving up. Only enter inference mode if disk discovery also finds nothing.
- **SKILL.md not found locally (named skill)**: use AskUserQuestion with three options —
  retry after installing, proceed with low-confidence summary, or provide a GitHub URL.
  Only fall back to the system-level description if the user explicitly selects that option,
  and mark the result with a ⚠ low-confidence warning.
- **URL fetch fails (404)**: report the error and remind the user that the URL must point to the
  **directory containing SKILL.md** — not a parent directory or the file itself. Example:
  `https://github.com/user/repo/tree/main/skills/my-skill` where `my-skill/SKILL.md` exists.
- **URL returns HTML instead of raw markdown**: GitHub repo landing pages return HTML — guide
  the user to the raw URL or the specific SKILL.md file path.
- **Skills are unrelated (Phase 2)**: use AskUserQuestion to offer the user a chance to try
  a different pair — do not silently stop.
- **"I'll type a different task" selected in Phase 3 Step 1**: treat the user's next free-text
  reply as TEST_TASK verbatim — no second confirmation prompt. Proceed directly to Step 2.
- **External dependency detected**: warn before launching (Step 3). If user proceeds,
  note in results header that output may not reflect the skill's full capability.
- **Both skills have dependencies**: warn once per skill sequentially. If the user chooses
  "Skip Phase 3" for the first skill's warning, stop immediately — do not show the second warning.
- **Subagent falls back silently** (e.g. Python scripts missing, CLI tool absent): the
  subagent may still produce output using inline guidelines. Flag this in the results:
  "⚠ [Skill Name] ran in degraded mode — [dependency] was unavailable. Results may differ
  from a fully installed environment."
- **Output directory creation fails** (`mkdir` error): report the error immediately. Do not
  launch subagents without a valid directory. Suggest the user check disk space and permissions.
- **Subagent times out**: distinguish from a hard tool error — a timeout means the task may
  have been too large. Suggest the user re-run with a simpler test task, or invoke the timed-out
  skill manually with the same prompt. Present the other skill's output alone.
- **Subagent fails with a tool error**: present the successful agent's output alone, note the
  specific error, suggest running the failed skill manually to diagnose.
- **Both subagents fail**: report both errors. Do not fabricate output for either skill.
  Suggest narrowing the test task and retrying.
- **Output files missing after subagent completes**: note the discrepancy (Step 5 verification).
  Do not report file paths that don't exist.
- **Phase 3 reached but SKILL.md body unavailable for one skill**: do not launch that skill's
  subagent — a subagent without skill instructions has nothing to follow. Present the other
  skill's output alone and explain the skip.
- **Phase 3 reached with low-confidence skill(s)**: a skill loaded from a system-reminder
  summary (2–3 lines) cannot serve as subagent instructions. Skip its subagent and note the
  limitation. If both skills are low-confidence, skip Phase 3 entirely.

---

## Core Principles

1. **Functional first, aesthetic second.** Always compare capabilities before output quality.
   Many comparisons end at Phase 2 — don't escalate to an A/B test when the docs already answer the question.

2. **Recommend directly when the answer is clear.** Hedging when one skill is obviously better
   wastes the user's time. Save the user's judgment for cases where it's genuinely needed.

3. **Evidence over opinion.** Every functional recommendation must quote specific passages from
   the skill files directly, not general impressions.

4. **Zero cross-contamination for output quality tests.** Each subagent receives only its own
   skill's instructions and the task — no knowledge of the other agent or the comparison.
   Never share context between the two agents.

5. **Same task, only skill differs.** The task string must be character-for-character identical
   in both session instructions. Do not adapt or rephrase per skill.

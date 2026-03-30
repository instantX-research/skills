# Skills

A collection of **Claude Code / agent skills**. Each skill lives under `skills/<name>/` with a `SKILL.md` as entry point.

## Skills

| Skill | Description |
|-------|-------------|
| [`web-search`](skills/web-search/) | Intelligent web search skill that autonomously decides whether a query requires web search. Searches for text content or reference images with quality filtering. |
| [`commit-poet`](skills/commit-poet/) | Turn git commit messages into poetry. Reads the diff, auto-selects a poem style based on change complexity. Supports haiku, modern verse, Shakespearean sonnet, and opus. |
| [`easy-prd`](skills/easy-prd/) | Generate structured PRDs via guided conversation. Supports lean MVP and full modes with iterative Q&A and section-by-section confirmation. |
| [`brand-quill`](skills/brand-quill/) | Rewrites everyday text into the aesthetic voice of iconic brands (MUJI, Apple, Aesop, Patagonia, etc.). Supports ZH/EN/JA multilingual output with scene-specific styles. |
| [`frontend-ui-clone`](skills/frontend-ui-clone/) | Pixel-perfect website cloner. Given a URL, reproduces the page as a single self-contained HTML file using browser rendering + DOM extraction. |
| [`frontend-ui`](skills/frontend-ui/) | High-aesthetic frontend UI generator. Analyzes reference URLs or screenshots to extract design DNA, generates production-ready UI with the polish of Linear, Vercel, Stripe, etc. |
| [`find-best-skill`](skills/find-best-skill/) | Compares overlapping skills to identify the best one for a given use case. Performs functional analysis and optionally runs parallel tests. |


## Installation

### Install all skills

```bash
# Clone the repo
git clone https://github.com/instantX-research/skills.git

# Copy all skills to your Claude Code skills directory
cp -r skills/skills/* ~/.claude/skills/
```

### Install a single skill

```bash
# Example: install only frontend-ui
mkdir -p ~/.claude/skills/frontend-ui
cp -r skills/skills/frontend-ui/* ~/.claude/skills/frontend-ui/
```

### Install from GitHub (without cloning)

```bash
# Replace <skill-name> with: frontend-ui, frontend-ui-clone, easy-prd, find-best-skill, brand-quill, commit-poet, or web-search
SKILL=frontend-ui
mkdir -p ~/.claude/skills/$SKILL
curl -fsSL "https://raw.githubusercontent.com/instantX-research/skills/main/skills/$SKILL/SKILL.md" \
  -o ~/.claude/skills/$SKILL/SKILL.md
```

> **Note:** `frontend-ui` has a `knowledge/` directory with additional files. Use the full clone or `cp -r` method to include them.

### Verify installation

```bash
ls ~/.claude/skills/
```

After installation, skills are available as slash commands in Claude Code (e.g., `/frontend-ui`, `/easy-prd`).

## Credits

Created by [Haofan Wang](https://haofanwang.github.io/) with Claude Code.

## License

MIT — Use it, modify it, share it.

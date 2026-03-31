# commit-poet

A Claude Code skill that turns your git commits into poetry.

## Installation

```bash
npx skills add https://github.com/instantX-research/skills --skill commit-poet
```

Or manually copy into your Claude Code skills directory:

```bash
cp -r skills/commit-poet ~/.claude/skills/
```

## What It Does

Reads your `git diff`, understands the semantic meaning of your changes, and rewrites the commit message as a poem. **Auto-selects the best style based on diff complexity**, or you can pick one manually. Supports four styles:

| Style | Format | Best for |
|-------|--------|----------|
| 🌸 Haiku | 5-7-5 syllables, one vivid moment | Bug fixes, single-file changes |
| 🌙 Modern | Free verse, 3-6 lines | Anything — maximally expressive |
| 🪶 Sonnet | Shakespearean 14-line iambic pentameter | Meaningful features, migrations |
| 🏛️ Opus | Epic formal verse, 8-16 lines, grandiose | Major refactors, heroic changes |

## Usage

```bash
# Auto-select style based on diff complexity
/commit-poet

# Force a specific style
/commit-poet --style sonnet

# Preview without committing
/commit-poet --dry-run
```

## Output example

```
🪶 The gates stood open, any soul could pass,
   No challenge issued, neither key nor name...
   So auth.ts now guards what once was free,
   And only trusted callers hold the key.

feat: add JWT authentication middleware
```

## How it works

1. Reads the staged diff (or unstaged if nothing is staged)
2. Analyzes: what changed, why, and what's the "emotional arc"
3. **Auto-selects style** based on complexity (or uses `--style` if specified):
   - 🌸 Haiku — typo, config tweak, 1-2 files (<20 lines)
   - 🌙 Modern — bug fix, small feature, 2-5 files (20-100 lines)
   - 🪶 Sonnet — new feature, migration, 5-10 files (100-500 lines)
   - 🏛️ Opus — major rewrite, architecture overhaul, 10+ files (500+ lines)
4. Composes a poem that reflects the actual change
5. Keeps a plain-language summary line for `git log` searchability

## Notes

- The plain summary line ensures your `git log --oneline` stays useful
- Poems are never generic filler — they reference real files and functions from your diff

## Credits

Created by [Haofan Wang](https://haofanwang.github.io/) with Claude Code.

## License

MIT — Use it, modify it, share it.

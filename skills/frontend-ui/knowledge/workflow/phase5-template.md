## Phase 5 — Template Skill Generator

### 5a. Resolve skill name

The template name comes from the `--save <name>` flag (already stored as `SAVE_NAME`). No need to ask.

**Name collision check:** Before creating, check if `~/.claude/skills/[SAVE_NAME]/SKILL.md` already exists.
- If it exists → ask: "A skill named `/[SAVE_NAME]` already exists. Overwrite, rename (suggest `/[SAVE_NAME]-2`), or cancel?"

### 5b. Generate the template skill

Create `~/.claude/skills/[name]/SKILL.md` with:
1. Complete Design DNA Report from Phase 2
2. All CSS custom property values (real extracted values)
3. Font import URLs or stack declarations
4. Radius, shadow, and spacing scales as concrete values
5. Component signature rules for buttons, cards, inputs, nav
6. "What this style NEVER does" anti-pattern list for this specific style
7. Generation instructions referencing Phase 4 rules + style-specific overrides

```markdown
---
name: [chosen-name]
version: 1.0.0
description: |
  Frontend UI generator using [Style Name] design system.
  [2-sentence style description with specific characteristics].
user-invocable: true
context: fork
agent: general-purpose
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion]
argument-hint: "[component or page to build]"
---

You are building UI that matches the **[Style Name]** design system exactly.

**Build:** $ARGUMENTS

## Design System
[Full DNA report as CSS custom properties + component rules]

## Font Setup
[Exact @import or npm package + font-face declarations]

## Component Rules
[Buttons, cards, inputs, nav — specific to this style]

## Style Anti-Patterns
[What this style NEVER does]

## Generation Instructions
Follow Phase 4 rules from frontend-ui skill, with these overrides:
[Style-specific overrides]
```

### 5c. Confirm

```
✓ Style template saved: ~/.claude/skills/[name]/SKILL.md

Usage:
  /[name] pricing page with 3 tiers
  /[name] user settings form
  /[name] dashboard with sidebar navigation

Available in all future sessions.
```


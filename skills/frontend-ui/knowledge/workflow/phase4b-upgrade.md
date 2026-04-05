## Phase 4b — Upgrade Mode (Mode D — sibling path to Phase 4)

Triggered exclusively by Mode D. Does NOT flow through Phase 4 or Phase 4.5 first.
Improve existing code without rewriting from scratch. Work with the existing tech stack.

---

## Step 0 — Directory handling (skip if single file or pasted code)

If the user provided a directory path instead of a single file:

**0a. Discover files:**
Use Glob to find all frontend files: `**/*.{html,tsx,jsx,vue,svelte,css}` within the directory.
Exclude files matching these patterns:
- `node_modules/`, `dist/`, `build/`, `.next/`, `out/`
- `*.test.*`, `*.spec.*`, `*.stories.*`, `*.d.ts`
- Config files: `tailwind.config.*`, `postcss.config.*`, `vite.config.*`, `next.config.*`

**0b. Classify and order files:**
Read each discovered file (first 50 lines is enough for classification). Sort into upgrade order:

| Priority | Category | Examples | Rationale |
|----------|----------|----------|-----------|
| 1 | Shared tokens / global styles | `globals.css`, `variables.css`, `tokens.css`, `theme.ts` | Foundation — other files depend on these |
| 2 | Layout / shell components | `Layout.tsx`, `Header.tsx`, `Nav.tsx`, `Sidebar.tsx`, `Footer.tsx` | Structural — wraps everything else |
| 3 | Reusable UI components | `Button.tsx`, `Card.tsx`, `Input.tsx`, `Modal.tsx` | Shared — used by pages |
| 4 | Page-level components / routes | `page.tsx`, `Home.tsx`, `Dashboard.tsx`, `index.html` | Consumers — benefit from earlier fixes |

**0c. Present the plan:**
Show the user a summary before starting:
```
Found [N] frontend files in [directory]:

Upgrade order:
1. [tokens/globals] — file1.css, file2.ts
2. [layout/shell]   — Layout.tsx, Header.tsx
3. [components]     — Button.tsx, Card.tsx
4. [pages]          — page.tsx, Dashboard.tsx

Skipped: [list any excluded files and why]
```

**0d. Upgrade each file sequentially:**
For each file in order, run Step 1 → Step 2 → save (in-place). Do NOT run Phase 4.5 evaluation after each file — instead, run it once at the end after all files are upgraded.

**Cross-file consistency rules:**
- Token values established in Priority 1 files must be reused (not redefined) in later files
- If a shared component's API changes during upgrade (e.g., new props), update all consumers
- Maintain consistent spacing scale, color tokens, and type scale across all files
- If upgrading a CSS file introduces new custom properties, grep for hardcoded values of the same color/size in other files and replace them with the new token

Proceed to Step 1 for each file in the upgrade order.

---

## Step 1 — Pre-audit triage

Before loading upgrade-audit.md, assess what you are working with. Answer internally:

**1a. What is the existing tech stack?**
- Framework: plain HTML/CSS, React, Vue, Next.js, other?
- Styling: Tailwind, CSS Modules, plain CSS, styled-components?
- State presence: static page vs. interactive components?

Preserve whatever stack is present. Upgrade within it, do not switch frameworks.

**1b. What is the upgrade scope?**

Run this classifier on the existing code:

| Signal | Finding |
|--------|---------|
| No CSS custom properties / no `:root {}` token layer | Missing foundation — P1 fix first |
| Hardcoded hex values scattered across CSS rules | Token migration needed — P2 |
| `margin: 0 auto` or arbitrary padding values | Spacing system missing — P2 |
| Generic Inter throughout, all same weight | Typography upgrade needed — P3 |
| No hover/focus states on interactive elements | Accessibility gap — P0 |
| No responsive design / fixed pixel widths | Mobile-first pass needed — P1 |
| Centered stock-photo hero with gradient overlay | Hero archetype upgrade — P3 |
| Equal-column feature grid | Layout rethink needed — P3 |

**1c. Rewrite vs. improve decision:**

- **Improve (default):** Fix issues in-place. Preserve component structure, class names where possible, existing content.
- **Strategic rebuild (rare):** Only when ≥ 4 of the following are true AND the user has explicitly indicated they want significant visual change:
  - No token layer whatsoever (every value hardcoded)
  - No semantic HTML (`<div>` soup throughout)
  - No responsive design at all
  - Fundamental layout structure conflicts with the target archetype
  - Existing code is fewer than 150 lines (rebuild cost is low)

**Default is always improve.** If rebuild is warranted, state clearly: "The existing structure has significant foundational issues. I recommend rebuilding with the same content — this is faster than patching." Then confirm with the user before proceeding.

---

## Step 2 — Load and apply upgrade-audit.md

→ Load `knowledge/implementation/upgrade-audit.md`. Apply fixes in P1→P10 priority order.

**Upgrade sequencing rule:** Fix foundation before aesthetics.
1. Fix broken accessibility (missing focus states, contrast failures) — always first
2. Add token layer if missing — enables everything else
3. Fix spacing + grid alignment
4. Upgrade typography (scale, weight hierarchy, letter-spacing)
5. Improve visual design (color, depth, surface treatments)
6. Add motion and interaction delight (only after structure is solid)

**Scope constraint:** If the user said "make it look better" without specifying scope, apply P1–P5 only. Reserve P6–P10 for when the user asks for a "full redesign" or "make it great."

**Preserve intent:** If the existing code has a specific color or font that appears deliberate (matches a brand, was clearly chosen intentionally), ask before changing it. Do not replace the user's design decisions without permission.

---

## Step 3 — Run Phase 4.5 in STANDARD mode

After completing all applicable fixes:

→ Load `knowledge/workflow/phase4-generation.md` and run Phase 4.5 in **STANDARD mode** (full scoring, full Design Report) and show the Design Report.

The Design Report for an upgrade should note:
- Which P-level issues were found and fixed
- What was deliberately preserved from the original
- What the weighted score improved from (estimated) → to (after fixes)
- Any remaining P2/P3 items deferred for a future pass

**Directory upgrade — final evaluation:**
When upgrading a directory, run Phase 4.5 once after all files are done. The Design Report should include:
- Total files upgraded and their categories
- Cross-file consistency check: token reuse, spacing scale, type scale consistency
- Per-file summary: which P-level issues were found and fixed
- Any remaining issues deferred for a future pass

**Output path for Mode D:** The `$(pwd)/test_outputs/` rule applies only to new page generation. For upgrades:
- If the user provided a file path → save back to that same path (in-place upgrade)
- If the user provided a directory → save each file back to its original path (in-place upgrade)
- If the code was pasted inline (no file path) → save to `$(pwd)/test_outputs/upgrade-[slug].html` with the same collision numbering rule. Ensure `$(pwd)/test_outputs/.gitignore` exists (containing `*`).

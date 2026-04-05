## Phase 4 — UI Generation

Produce production-quality frontend code. No TODOs, no stubs.

**Design Taste Gate — answer internally, then output as a verifiable contract.**

Before writing the first line of code, answer these three questions:

1. **The unforgettable moment:** What is the ONE visual or interaction moment that makes this page unmistakable? Name it concretely (not "clean design" — e.g., "oversized 120fps stat at 40vw in the hero", "glass card with spring-physics reveal on scroll", "ambient sound-wave visualizer as background texture"). This becomes the page anchor; everything else supports it.

2. **The slop trap:** What would a generic AI output of this same prompt look like? Enumerate 3 specific clichés to avoid (e.g., "3-equal-column feature grid", "purple gradient CTA", "stock photo hero with overlay text"). Confirm none appear in the plan.

3. **The elevating decision:** What is the single design choice that a competent-but-uncreative designer would NOT make — and why does it work here? If you cannot name one, revise the plan until you can.

**Output these as a `DESIGN CONTRACT` comment at the top of the generated file. Each item must include a verifiable condition that Phase 4.5 will check:**

```html
<!-- DESIGN CONTRACT
  HOOK:    [description of unforgettable moment]
           VERIFY: [CSS selector, property, or structural feature confirming it's present]
  AVOID_1: [slop cliché 1]   VERIFY: [what must NOT appear]
  AVOID_2: [slop cliché 2]   VERIFY: [what must NOT appear]
  AVOID_3: [slop cliché 3]   VERIFY: [what must NOT appear]
  ELEVATE: [non-obvious elevating decision]   VERIFY: [where in code this is expressed]
-->
```

Phase 4.5 will audit this contract line by line. This block is mandatory.

**Scope check:** If the request requires 6+ distinct components, decompose into a build plan (list in dependency order: tokens → layout → nav → sections → components) and generate each sequentially. Fewer than 6 components → generate in one pass.

**Foundation-first rule:**
Generate the global token layer first:
```css
/* :root — sourced from Design Brief palette */
:root {
  /* Colors — every value from palette ID */
  /* Typography — font imports + scale */
  /* Spacing — base unit + named scale */
  /* Radius + Shadow — named tokens */
  /* Motion — duration + easing */
}
```
All components reference these tokens. Never hardcode hex values or pixel values that belong in the token layer.

**Interaction model rule (Mode B — URL/screenshot clones):**
- Scroll-driven sections → IntersectionObserver or CSS scroll-driven animations
- Click-driven sections → tabs, accordions, modals
- Identify each section's model explicitly before building it

**Design rules (apply throughout generation):**

- Load `knowledge/design/design-taste.md` now (Phase 4 start — craft rules enforcement: typography, color, copy, layout, a11y, dark mode)
- Load `knowledge/implementation/code-standards-core.md` now (Phase 4 start — CSS tokens, semantic HTML, Tailwind pattern, output format)
- Load `knowledge/implementation/code-standards-extended.md` if building full pages (≥ 3 sections) OR VISUAL_DENSITY ≥ 6 (responsive design, dark mode, ARIA, images, component state matrix, SEO, SVG, animation isolation)
- Apply composition principles from `knowledge/design/design-principles.md` (loaded in Phase 3)
- If generating any page with navigation: load `knowledge/design/navigation.md` (top nav vs. sidebar decision, scroll behaviors, mobile nav)
- If implementing spotlight borders, grain overlays, glassmorphism, or variable font animation: load `knowledge/implementation/advanced-effects.md`
- **Animation library selection:** MOTION_INTENSITY ≤ 3 → CSS transitions/animations only (no JS dependency). MOTION_INTENSITY 4–6 → Framer Motion (React) or CSS scroll-driven animations; `design-principles-motion.md` is loaded at Phase 3 entry for this range. MOTION_INTENSITY ≥ 7 or complex orchestration (timeline, SVG morph, scroll-scrubbing) → GSAP. Always respect `prefers-reduced-motion` regardless of library.
- **One unforgettable moment per page — MANDATORY.** Named in the Design Taste Gate, must appear in the final output. If it's not present, the output is unfinished.
- *Color restraint:* Apply the Restrained/Chromatic rules from `knowledge/design/color-palettes.md` (already loaded). Enforce throughout generation.

**Delight checklist** — pick N items based on MOTION_INTENSITY (formula: `min(ceil(MOTION/2), archetype_cap)`):
- Archetype caps: E Luxury Silence = 1; G Museum Authority = 1; I Developer Personal = 1; B Warm Editorial = 2; A Obsidian Precision = 2; D Terminal Glass = 3; F Soft Structuralism = 3; H Cinematic Portfolio = 4; C Chromatic Confidence = 5+

Available delight moments:
- [ ] Hover micro-reward: scale, color temperature shift, or reveal
- [ ] Animated stat: counter, progress arc, or live figure
- [ ] Typographic surprise: one dramatically oversized or contrasting line
- [ ] Scroll-triggered reveal: staggered list or parallax element
- [ ] Empty state personality: zero-state with voice, not "No data found"
- [ ] Transition that earns attention: spring physics on one panel/page transition
- [ ] Detail nobody asked for: on-brand `::selection`, scrollbar, favicon
- [ ] Copy with voice: one CTA or label that reads like a human wrote it
- [ ] Unexpected color moment: accent in an unexpected place (border-left, focus ring)

**When generation is complete → proceed immediately to Phase 4.5. Do not show output to user first.**

---

## Phase 4.5 — Dual-Persona Evaluation + Design Report

**Run after generation. Four rounds: Contract Audit → Critic Review → Resolution → Screenshot Verification. Then show the full report.**

**QUICK mode (abbreviated):** Run Round 1 (Contract Audit) and Round 2 (Critic Review) only. Fix P0 and P1 issues. Skip Round 4 (Screenshot Verification), the pre-ship checklist, and the scored Design Report — output a condensed summary (2–3 lines: archetype, palette, hook, any fixes made). Apply ship gate: P0 = 0, P1 = 0 required before showing output. Then append the DESIGN STATE block with `report_mode: quick`.

---

### Round 1 — DESIGN CONTRACT Audit

Read the `DESIGN CONTRACT` comment block at the top of the generated file.
For each item, verify the condition:

- **HOOK VERIFY:** Is the specified CSS/structural feature present? → If not → P0
- **AVOID_1/2/3 VERIFY:** Is the forbidden pattern absent? → If present → P1
- **ELEVATE VERIFY:** Is the elevating decision expressed in code? → If not → P1

**Failure handling:**
- **HOOK fails (P0):** The unforgettable moment is missing. Revise the Design Taste Gate answers, then regenerate Phase 4 entirely. Re-run Round 1 before proceeding.
- **AVOID fails (P1):** The forbidden pattern is present. Fix inline — do not regenerate. Re-verify only the failed AVOID item.
- **ELEVATE fails (P1):** Fix inline in the generated code. Re-verify.

All items must pass before proceeding to Round 2.

---

### Round 2 — Critic Review (adversarial persona)

**Explicitly switch to Critic mode.** You are now reviewing someone else's work. Your job is to find its weakest points, not defend its strengths.

Answer each question honestly (respond in the user's language per the global language rule):

1. **Which section would the Linear/Vercel design team reject?** Name one section and why.
2. **Which decision looks most like generic AI output?** Name the most generic choice in the entire file.
3. **If the hook disappeared, what's left?** If the unforgettable moment were stripped out, does the page still hold up?
4. **Can a first-time visitor understand what this is and who it's for within 3 seconds?** Yes or no, with reason.

For each criticism: classify as P0 / P1 / P2 / P3.

---

### Round 3 — Resolution

Fix all P0 and P1 issues raised in Rounds 1 and 2.
Record P2/P3 for the report.

**Ship gate:**
- P0 = 0 AND P1 = 0 AND P2 ≤ 2 → proceed to Design Report
- P2 ≥ 3 → fix the worst P2s until ≤ 2 remain, then proceed
- P3 items are always deferred — never block shipping

**P0–P3 severity:**
- **P0 Ship-blocker:** broken functionality, inaccessible element, missing focus state, contract HOOK missing
- **P1 Quality fail:** anti-pattern present, off-grid value, banned usage, contract AVOID violated, generic AI decision not fixed
- **P2 Polish gap:** sub-optimal hierarchy, weak section, missed delight opportunity
- **P3 Future note:** nice-to-have, performance optimization

---

### Pre-ship checklist (verify after Round 3 fixes)

→ Verify every item in the Pre-ship checklist section of `knowledge/implementation/code-standards-core.md`. All must pass before showing the Design Report.

---

### Round 4 — Screenshot Verification (automated visual audit)

**Purpose:** Code review catches structural issues but misses rendering bugs — broken layouts,
invisible text on same-color backgrounds, clipped overflow, font loading failures, z-index
stacking errors. This round catches what code review cannot.

**When to run:** After Round 3 Resolution AND Pre-ship checklist pass. Before scoring.

**Prerequisites:**
- The generated file must be saved to disk (Phase 0 output path).
- For plain HTML files: the file is self-contained and can be opened directly.
- For framework components (React/Vue/Svelte): a dev server must be running.
  If no dev server is detected, skip this round and note in the Design Report:
  `SCREENSHOT: skipped (framework component — run dev server + /browse to verify)`

**Step 1 — Capture screenshots**

Take 3 screenshots of the generated page at different viewports:

```bash
# Desktop (1440×900)
npx --yes playwright screenshot --viewport-size="1440,900" --full-page \
  "file://[absolute-path-to-html]" "[output-dir]/screenshot-desktop.png"

# Tablet (768×1024)
npx --yes playwright screenshot --viewport-size="768,1024" --full-page \
  "file://[absolute-path-to-html]" "[output-dir]/screenshot-tablet.png"

# Mobile (375×812)
npx --yes playwright screenshot --viewport-size="375,812" --full-page \
  "file://[absolute-path-to-html]" "[output-dir]/screenshot-mobile.png"
```

Where `[output-dir]` is the same directory as the generated file.

**Fallback if Playwright is unavailable:** Try Puppeteer (`npx --yes puppeteer screenshot`),
then bare Chrome (`google-chrome --headless --screenshot`). If no headless browser is available,
skip and note: `SCREENSHOT: skipped (no headless browser — install playwright: npm i -D playwright)`

**Step 2 — Visual audit against Design Contract**

Read each screenshot with the `Read` tool (it supports image files). For each screenshot,
verify the following against the DESIGN CONTRACT and Design Brief:

| Check | What to look for | Severity if failed |
|-------|-----------------|-------------------|
| **HOOK visible** | Is the unforgettable moment visually prominent and recognizable? | P0 |
| **AVOID patterns absent** | Do any of the 3 forbidden clichés appear in the rendered output? | P1 |
| **Color fidelity** | Does the rendered palette match the Design Brief? No unexpected colors? | P1 |
| **Typography rendering** | Are fonts loaded correctly? (not falling back to system fonts) | P1 |
| **Layout integrity** | No overlapping elements, no clipped text, no broken grid alignment? | P0 |
| **Contrast legibility** | Is all text readable against its background at every viewport? | P0 |
| **Responsive behavior** | Does the layout adapt sensibly from desktop → tablet → mobile? | P1 |
| **Spacing consistency** | Do margins/padding look even and intentional, not collapsed or doubled? | P2 |
| **Interactive affordance** | Do buttons/links look clickable? Are CTAs visually prominent? | P2 |

**Step 3 — Fix and re-capture**

- **P0 failures:** Fix immediately. Re-capture only the failing viewport to confirm the fix.
- **P1 failures:** Fix inline. No re-capture required unless the fix was structural.
- **P2 failures:** Record in Design Report under REMAINING NOTES. Do not block shipping.

**Step 4 — Append to Design Report**

Add the screenshot verification results to the Design Report (between CONTRACT AUDIT and
CRITIC FINDINGS):

```
SCREENSHOT VERIFICATION
  Desktop (1440×900)   [pass / N issues fixed]
  Tablet  (768×1024)   [pass / N issues fixed]
  Mobile  (375×812)    [pass / N issues fixed]
  Checks passed        [X/9]
  Screenshots saved    [paths to screenshot files]
```

If screenshots were skipped, show:
```
SCREENSHOT VERIFICATION
  Status: skipped — [reason]
  Recommendation: run `/browse [url]` or `/qa` to verify rendering
```

---

**Scoring rubric (apply before filling SCORES):**

| Score | Design Quality | Originality | Craft | Usability | Functionality |
|-------|---------------|-------------|-------|-----------|---------------|
| 9–10 | All 4 sub-dims pass; hook is unmistakable | Moment is category-defining; no one would guess AI | 0 checklist failures | Primary CTA in 1 click; zero confusion | Renders perfectly, no console errors |
| 7–8 | 3/4 sub-dims pass; hook present but subtle | Clearly non-generic; one strong non-obvious choice | ≤2 minor failures | CTA reachable in 2 clicks | Renders with trivial warnings only |
| 5–6 | 2/4 pass; hook unclear | One OK moment; rest is predictable | 3–5 failures or 1 P1 | CTA findable but buried | Minor visual glitch; no broken state |
| ≤4 | Fails majority; generic throughout | Indistinguishable from average AI output | Multiple P1s or any P0 | CTA requires hunting | Broken section or inaccessible element |

**After all three rounds and fixes, show the user this Design Report:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DESIGN REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Archetype           [name]
Palette             [ID + name]
Parameters          DESIGN_VARIANCE=[X]  MOTION=[X]  DENSITY=[X]
Color mode          [Restrained / Chromatic]
Fidelity            [pixel-perfect / high-fidelity / structural / N/A]
Structural template [reference name/URL used, or "none"]

CONTRACT AUDIT
  HOOK     [pass / FIXED — what was wrong and what was changed]
  AVOID_1  [pass / FIXED]
  AVOID_2  [pass / FIXED]
  AVOID_3  [pass / FIXED]
  ELEVATE  [pass / FIXED]

SCREENSHOT VERIFICATION
  Desktop (1440×900)   [pass / N issues fixed]
  Tablet  (768×1024)   [pass / N issues fixed]
  Mobile  (375×812)    [pass / N issues fixed]
  Checks passed        [X/9]
  Screenshots saved    [paths]

CRITIC FINDINGS
  Weakest section   [name + one-line reason]
  Most generic choice  [what it was + whether it was fixed or accepted]
  Without the hook  [honest assessment of what remains]
  3-second clarity  [yes/no + reason]

SCORES
  Design Quality   [X/10] — [sub-dimension summary: typography ✓/✗, rhythm ✓/✗, color ✓/✗, hook ✓/✗]
  Originality      [X/10] — [what the unforgettable moment is and why it earns that role]
  Craft            [X/10] — [checklist pass rate + what was fixed]
  Usability        [X/10] — [primary CTA reachable in ≤2 clicks?]
  Functionality    [X/10] — [renders without error?]
  Weighted total   [X/10]  (Design Quality 40% · Craft 25% · Originality 15% · Usability 10% · Functionality 10%)

DESIGN RATIONALE  ← write with conviction, not description
  Hook      [Name it precisely. Where does it appear? Why does it work for THIS product specifically?]
  Color     [What emotional/functional work does this palette do? What would a bolder or lighter palette have sacrificed?]
  Type      [Why this pairing and tracking? What would generic Inter have cost?]
  Layout    [Why this structure over alternatives? What does the asymmetry or density say about the product?]
  Motion    [Why this animation level? Which specific moments were chosen and why?]
  Anti-slop [2–3 choices a generic AI would NOT have made — named explicitly]

REMAINING NOTES
  P2  [polish gaps]
  P3  [future nice-to-haves]

WANT TO ADJUST?
  A) Bolder — more visual impact, higher variance
  B) Quieter — more restrained, more minimal
  C) Different color — try [suggested alternative palette]
  D) More color — [suggest chromatic option if currently restrained]
  E) Fix specific section — describe what to change
  F) Harden — add loading, error, empty states
  G) Adapt — responsive/mobile pass
  H) Save this style as a reusable template — run `/frontend-ui --save <name>`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**After the report, append this state snapshot to the conversation and to the generated file (format per file type — see Phase 1.5 DESIGN STATE placement table).
This enables Mode E–K to resume without re-running Phase 3.**

```html
<!-- DESIGN STATE (for .html)
  skill_version: 1.0.0
  archetype: [A–J or hybrid e.g. "E×A"]
  palette: [ID e.g. D1]
  variance: [X]  motion: [X]  density: [X]
  color_mode: [restrained / chromatic]
  layout: [editorial-split / bento / etc.]
  report_mode: [quick / standard]
  file: [$(pwd)/test_outputs/filename.html]
-->
```

The user can pick any option from the adjustment menu. Each triggers the corresponding Mode (E–K or Phase 5) and produces a new Design Report and updated DESIGN STATE afterward.

**Browser verification note:** Round 4 (Screenshot Verification) automatically captures and audits rendered output at 3 viewports. If headless browser is unavailable (Playwright/Puppeteer not installed), suggest:
> Screenshot verification was skipped. To verify rendering, run `/browse [file-path]` or `/qa` — it will screenshot the actual rendered page and catch layout issues that code review misses.
> To enable automatic screenshots, install Playwright: `npm i -D playwright`

---

## Final Output Rules

- **Complete, runnable code** — no TODOs, no `// TODO: implement`, no `...rest of component`
- **Real content** — no Lorem ipsum; domain-appropriate copy that fits the product
- **Opinionated** — present design decisions with confidence, like a senior designer in a client review
- **Never over-comment** — only comment non-obvious decisions
- **End with the Design Report** — always run Phase 4.5 and show the full report after generation
- **One clarifying question maximum** before generating — never block more than once
- **Output path** — use the path determined in Phase 0 Step 1b.
  - **Plain HTML output** (stack = "Unknown / plain HTML") → always save to `$(pwd)/test_outputs/[filename]`. Run `mkdir -p "$(pwd)/test_outputs"` before writing. Ensure `$(pwd)/test_outputs/.gitignore` exists (containing `*`) to prevent accidental commits.
  - **Framework output** (Next.js / React / Vue / Svelte detected) → save to the appropriate project directory: `src/components/` for components, `pages/` or `app/` for page files, `src/app/` for Next.js App Router. Ask if ambiguous.
  - Report the full saved path at the end of the Design Report.
- **DESIGN.md generation** — When outputting to a **framework project** (not plain HTML to `$(pwd)/test_outputs/`), check if `DESIGN.md` exists in the project root.
  - If absent: create `DESIGN.md` with the finalized design tokens (palette `:root {}` block, font imports, spacing scale, radius/shadow tokens, archetype name, creative parameters). This enables future invocations to read existing tokens and maintain consistency.
  - If present: do not overwrite. If the current generation deviates from the existing `DESIGN.md` tokens (e.g., user chose a different palette), note the deviation in the Design Report and ask the user if they want to update `DESIGN.md`.
  - For `$(pwd)/test_outputs/` plain HTML: skip DESIGN.md generation — test outputs are standalone and do not need cross-session persistence.

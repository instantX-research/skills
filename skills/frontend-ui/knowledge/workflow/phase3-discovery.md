## Phase 3 — Progressive Disclosure

→ Load `knowledge/design/design-principles.md` now (Phase 3 start — core composition, typography, color, spacing, depth, motion basics).

**Conditional loads — evaluate after archetype and creative params are locked:**
→ Load `knowledge/design/design-principles-advanced.md` if DESIGN_VARIANCE ≥ 6 OR archetype is H, C, or G.
→ Load `knowledge/design/design-principles-motion.md` if MOTION_INTENSITY ≥ 4.
→ Load `knowledge/design/design-principles-ux.md` if component count ≥ 4 OR output includes forms, data tables, or complex navigation.

**Decision tree: Scene → Archetype → Palette → Layout.**
This is a tree, not a linear interview. Each step informs the next, and many branches auto-resolve without asking the user. Ask only when genuine ambiguity exists that the user must resolve.

**Fast path (non-thin input):** If Scene is clear AND at least one archetype is inferable from `$ARGUMENTS`, skip the interview entirely.

**Reference-case lookup (safest strategy):** Before synthesizing the Design Brief, use `knowledge/references/reference-sites.md` (already loaded in Phase 1 for Mode B; load now if arriving from Mode A) to find the closest matching reference case for the inferred scene + archetype. If a match exists, use that reference's proven structure as the generation template — replace only names, copy, and user-specific details (blur or use placeholder text for anything not supplied by the user). State the structural template in the Design Brief. If no close match exists, synthesize from scratch as before.

Present:

```
Here's my plan — confirm or adjust:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Design Brief (draft)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Scene               [inferred]
Archetype           [inferred + one-line rationale]
Palette             [auto-selected from archetype]
Color mode          Restrained
Layout              [inferred from scene]
Fidelity            [pixel-perfect / high-fidelity / structural — from Phase 2-pre, or "N/A" for Mode A (text description)]
Structural template [reference name/URL matched from reference-sites.md, or "none — synthesized from scratch"]
Creative params     DESIGN_VARIANCE=[X] MOTION=[X] DENSITY=[X]
Unforgettable hook  [specific visual/interaction moment, not a generic description]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
A) Generate now  B) Change archetype  C) Change palette  D) Change layout
```

**Thin input detection — 5-signal binary checklist (objective, not subjective):**

Check each signal as yes (1) or no (0):

| Signal | Yes if… |
|--------|---------|
| A Page type | $ARGUMENTS contains a recognizable page type word: "homepage", "landing", "dashboard", "login", "blog", "portfolio", "pricing", "onboarding", "product page", "academic homepage", "lab site", "research profile", "institutional homepage", "university site", "government portal", "corporate homepage", "directory", "hub", "aggregator", "catalog", etc. |
| B Industry / domain | A specific industry or domain is inferable: tech, fintech, fashion, healthcare, food, education, gaming, government, public sector, etc. |
| C Target audience | A user type is mentioned or strongly implied: "developers", "consumers", "enterprise", "creatives", "students", "researchers", "faculty", "staff", "alumni", "visitors", "citizens", etc. |
| D Visual style / mood | A style word or brand reference is present: "minimal", "bold", "dark", "warm", "luxury", "like Linear", "Apple-style", etc. |
| E Color preference | A color is named OR user explicitly defers ("you decide", "up to you") |

Score ≥ 3 → **non-thin** (fast path)
Score ≤ 2 → **thin** (run Steps 1–4 in sequence)

---

### Step 1 — Scene

**Purpose:** determine what we're building. Drives archetype pre-filtering.

Ask with `AskUserQuestion` (or infer from `$ARGUMENTS` if clear):

```
What is this interface / website for?

A) Product website / landing page — public-facing, driving signups or purchases
B) SaaS app UI — a tool or dashboard users work in daily
C) Content / blog / docs site — reading and information display
D) E-commerce / brand page — product showcase, purchase conversion
E) Personal site / portfolio — showcasing an individual or team
F) Academic homepage / lab site — faculty, student, or research group profile
G) Institutional homepage / organization root site — university, company, government, nonprofit, or department serving multiple audiences
H) Aggregation / directory / offer hub — curated products, partner offers, roundups, tool libraries, or resource collections
I) Developer documentation / open source project site — API reference, SDK docs, framework homepage, OSS project page
J) Other — briefly describe your scenario
```

*(Skip if `$ARGUMENTS` makes the answer obvious.)*

**Scene → archetype pre-filter + default layout (used by Steps 2 and 4):**

| Scene | Primary archetypes | Exclude | Default layout |
|-------|--------------------|---------|----------------|
| A Product / landing | A Obsidian, C Chromatic, F Soft Structuralism | G Museum, H Cinematic | Editorial Split or Z-Axis Cascade |
| B SaaS app | A Obsidian, D Terminal, F Soft Structuralism | G Museum, H Cinematic | Asymmetric Bento |
| C Content / blog / docs | B Warm Editorial, I Developer, A Obsidian | C Chromatic, D Terminal | Quiet Stack *(auto-resolve — skip Step 4)* |
| D E-commerce | C Chromatic, E Luxury, H Cinematic | G Museum, I Developer | Asymmetric Bento |
| E Portfolio (creative) | H Cinematic | G Museum | Broken Grid *(auto-resolve — skip Step 4)* |
| E Portfolio (tech) | I Developer | G Museum | Quiet Stack *(auto-resolve — skip Step 4)* |
| F Academic / research homepage | G Museum, I Developer, B Warm Editorial | C Chromatic, H Cinematic | Quiet Stack *(auto-resolve — skip Step 4)* |
| G Institutional / organization homepage | G Museum, A Obsidian, B Warm Editorial | C Chromatic, H Cinematic | Institutional Matrix *(auto-resolve — skip Step 4)* |
| H Aggregation / directory / offer hub | A Obsidian, F Soft Structuralism, B Warm Editorial | G Museum, H Cinematic | Aggregation Rail *(auto-resolve — skip Step 4)* |
| I Developer docs / OSS project | A Obsidian, D Terminal, I Developer | G Museum, E Luxury | Dense Command *(auto-resolve — skip Step 4)* |
| J Other | Ask for industry; apply above | — | Ask in Step 4 |

---

### Step 2 — Aesthetic Archetype

**Purpose:** lock in the visual personality.

**First: check product category novelty.**

Is this a product category with established visual conventions?
- **Established** (SaaS, fintech, e-commerce, portfolio, docs, dashboard, academic / research homepage, institutional homepage, aggregation / directory / offer hub, developer documentation, open source project site) → use Archetype path below
- **Novel** (wearables, spatial computing, brain-computer interfaces, biotech, consumer hardware, speculative products) → use First Principles path below

---

→ Load `knowledge/design/visual-archetypes.md` for the full A–J descriptions, First Principles Path, and live reference URLs.

**First Principles Path (novel categories only):** see `knowledge/design/visual-archetypes.md` — 5-dimension spectrum prompts and hybrid synthesis method.

**Archetype Path (established categories):**

Present only the 2–3 pre-filtered options from Step 1.

Ask with `AskUserQuestion` (show only relevant options, never the full A–J list):

> Which visual direction fits best?
> *[Show only the 2–3 relevant archetypes with one-line description from `knowledge/design/visual-archetypes.md`, plus J) Custom]*

**After archetype is locked:** auto-assign Creative Parameters from the canonical table at the top of this skill. Do not ask the user about DESIGN_VARIANCE / MOTION_INTENSITY / VISUAL_DENSITY. Then proceed to Step 3.

---

### Step 3 — Palette Selection

**Purpose:** pick the specific palette from the archetype's options. The archetype already determined the color temperature family — this step picks the exact variant.

**Color restraint rule:** → See "Color System: Restrained vs. Chromatic" in `knowledge/design/color-palettes.md` (canonical definition). Default is always Restrained unless user opts in with a trigger word.

**Auto-resolve conditions (skip the question entirely):**
- User specified a color or style in `$ARGUMENTS` → match to closest palette, state the match
- Archetype has only one logical option for the scene (e.g., archetype G → L7 Zen Ink is almost always right) → auto-select and note it in the Brief

**When to ask:** When the archetype has 2–4 meaningfully different palette options (e.g., Archetype A has dark precision options D1/D4/D7 that differ in warmth and accent character).

Ask with `AskUserQuestion` (show only the chosen archetype's palette options, 2–4 choices):

```
Which color variant fits best?
[Show the archetype's specific palettes with one-line descriptions]

Z) You decide — pick what works best for the product
```

**Palette options per archetype:** → See "Archetype → Palette Quick Reference" table in `knowledge/design/color-palettes.md` (already loaded).

**After palette is selected:** embed the full `:root {}` CSS custom property block from `knowledge/design/color-palettes.md` into the generation context.

---

### Step 4 — Layout Pattern (conditional)

**Purpose:** confirm the structural approach before generating.

**Auto-resolve rule:** Use the default layout from the Scene → Default layout table in Step 1.
- If the table shows *(auto-resolve — skip Step 4)* → use that layout, do not ask.
- Only ask when: (a) Scene is A, B, D, or I, AND (b) `$ARGUMENTS` doesn't already imply a layout.

When asking, show only the 2–3 options plausible for the scene:

```
Layout structure:

A) Asymmetric Bento — variable-size tiles, mixed aspect ratios [default for SaaS/product]
B) Editorial Split — large type left, media right, alternating [marketing/storytelling]
C) Z-Axis Cascade — elements at different depths, overlapping [premium product]
D) Dense Command — compact rows, data-table foundation [dev tools/dashboards]
E) Quiet Stack — single column, extreme whitespace [editorial/blogs]
F) Broken Grid — elements bleed columns, diagonal flow [creative/agency]
G) Institutional Matrix — utility nav + hero + audience shortcuts + feature/news rows [universities, government, company root sites]
H) Aggregation Rail — hero + logo cloud + category chips + dense card rails [curated offers, resource hubs, directories]
```

*(Also skip if `$ARGUMENTS` implies the layout directly, e.g., "dashboard" → D, "blog post" → E, "university homepage" → G, "tool directory" → H.)*

---

### Design Brief Synthesis

→ Load `knowledge/design/industry-patterns.md` and apply the row matching the product type (industry-specific color/type/effect overrides).
→ If output is a full page (≥ 3 sections): load `knowledge/design/page-sections.md` (landing page section anatomy).
→ If output includes a dashboard, charts, or data tables: load `knowledge/design/data-visualization.md` (chart type matrix, KPI cards, dashboard layout).

After all steps are confirmed (or inferred), output this block before generating:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Design Brief
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Scene               [from Step 1]
Archetype           [from Step 2]
Color system        [from Step 3] — Restrained or Chromatic
Palette             [ID + name, e.g. "D1 Linear Void"]
Layout              [from Step 4]
Fidelity            [pixel-perfect / high-fidelity / structural / N/A]
Structural template [reference name/URL from reference-sites.md, or "none — synthesized from scratch"]
Creative params     DESIGN_VARIANCE=[X] MOTION=[X] DENSITY=[X]
Unforgettable hook  [the one visual/interaction moment that makes this unmistakable]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Starting generation →
```

**Next step — load and execute Phase 4:**
→ Load `knowledge/workflow/phase4-generation.md` → Phase 4 (UI Generation).
Exception: if you entered Phase 3 via **Mode C** (save style), skip Phase 4 and go to Phase 5 instead → Load `knowledge/workflow/phase5-template.md`.

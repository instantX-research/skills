# frontend-ui

A Claude Code skill for generating high-aesthetic, production-ready frontend UIs — from scratch, from reference URLs, or by redesigning existing pages.

## Installation

```bash
npx skills add https://github.com/instantX-research/skills --skill frontend-ui
```

Or manually copy into your Claude Code skills directory:

```bash
cp -r skills/frontend-ui ~/.claude/skills/
```

## What It Does

**frontend-ui** acts as a principal product designer + senior frontend engineer. It analyzes real design systems, extracts visual DNA from reference sites, and enforces a pre-ship checklist covering visual craft, interaction quality, responsive layout, accessibility, and SEO.

Taste is calibrated against modern product sites, AI-native products, academic/research homepages, and institutional homepages. The full reference sets and routing logic live in `SKILL.md`.

## The Frontend Skill Family

This skill is part of a three-skill pipeline. Each skill handles a different stage of the website-to-product workflow:

```
                ┌─────────────────────┐
                │   frontend-ui       │  Generate from scratch
                │   (design + code)   │  "Build a landing page for..."
                └─────────────────────┘

                ┌─────────────────────┐
  URL ────────► │  frontend-ui-clone  │ ────────► clone.html
                │  (pixel-perfect)    │           (single file)
                └─────────────────────┘
                                                      │
                                                      ▼
                                          ┌─────────────────────┐
                                          │  frontend-reactor   │ ────────► Next.js project
                                          │  (componentize)     │           (npm run dev)
                                          └─────────────────────┘
```

| Skill | Role | Input | Output |
|-------|------|-------|--------|
| **frontend-ui** | Design + generate new UI from scratch | Text description, reference URL, screenshot | Production-ready HTML/TSX |
| [**frontend-ui-clone**](../frontend-ui-clone/) | Pixel-perfect website cloning | URL | Self-contained `.html` file |
| [**frontend-reactor**](../frontend-reactor/) | Convert static HTML to React project | Clone `.html` file(s) or URL | Runnable Next.js project |

**Typical workflows:**

- **Clone & convert:** `/frontend-ui-clone https://linear.app` → `/frontend-reactor clone-linear.html`
- **Clone multiple pages, then convert:** Clone several pages → `/frontend-reactor clone-linear*.html`
- **URL shortcut:** `/frontend-reactor https://linear.app` (auto-clones homepage, then converts)
- **Design from scratch:** `/frontend-ui a SaaS landing page` (no cloning — generates original UI)

### Key Features

- **4 primary modes** — Generate from text (A), clone a reference URL/file (B), save a style as a reusable skill (C), or upgrade existing code (D).
- **7 refinement passes** — After any generation: Bolder (E), Quieter (F), Delight (G), Harden states (H), Responsive (I), Typeset (J), Arrange layout (K).
- **Guided discovery** — Light inputs trigger a short interview for purpose, audience, tone, and visual direction.
- **Design DNA** — Extracts color tokens, type scale, spacing rhythm, motion, and component patterns from references.
- **Curated palettes** — Multiple preset families (dark, light, bold, special, editorial). No purple-gradient-on-white defaults.
- **Anti–AI-slop** — Real design systems, typographic craft, 8px grid discipline.
- **Unforgettable hook** — At least one scroll-stopping moment per output, defined before generation.
- **Self-evaluation gate** — Checklist across visual, interaction, mobile, a11y, and SEO before delivery.
- **Template saving** — Package a style as a standalone `/[name]` skill for later use.

## Usage

All flags are optional and composable. The only required input for Mode A is a text description.

```
/frontend-ui [--ref <url-or-path>] [--save <name>] [--upgrade] [description]
```

---

### Mode A — Generate from text description

No flags required — just describe what to build. If the scene matches a known category (e.g. academic homepage, museum site, SaaS landing page), the skill automatically looks up curated reference sites and extracts structural patterns before generating — no URL needed.

```
/frontend-ui a landing page for an AI productivity tool targeting developers
/frontend-ui an academic homepage for a computer vision professor
/frontend-ui an institutional homepage for a research university
/frontend-ui an aggregation site for AI tools with categories and featured picks
/frontend-ui a SaaS dashboard for a project management tool
```

---

### Mode B — Clone a reference (`--ref`)

Pass a URL or local file path via `--ref`. The skill extracts design DNA (colors, type, spacing, motion) and generates a new page in that visual style.

```
# Clone from URL
/frontend-ui --ref https://linear.app build a project management landing page
/frontend-ui --ref https://lumalabs.ai build an AI video product page
/frontend-ui --ref https://resend.com build a developer tool marketing page
/frontend-ui --ref https://www.sainingxie.com build an academic homepage

# Clone from local file
/frontend-ui --ref ./mockup.png build a dashboard in this style
/frontend-ui --ref ./designs/hero.jpg build a landing page
```

---

### Mode C — Save style as reusable skill (`--save`)

Extracts the design system and packages it as a standalone `/[name]` skill for future use.

```
# From a reference URL
/frontend-ui --ref https://resend.com --save resend-brand

# From a local screenshot
/frontend-ui --ref ./mockup.png --save my-dark-theme

# From a text description (no reference)
/frontend-ui --save editorial-dark a high-contrast serif editorial theme
```

Then use anywhere: `/resend-brand build a pricing page`.

---

### Mode D — Upgrade existing code (`--upgrade`)

Improves existing HTML/TSX/Vue code in priority order: token layer → typography → spacing → interaction states → motion. Accepts a single file or an entire directory.

```
# From a file path
/frontend-ui --upgrade ./components/Hero.tsx
/frontend-ui --upgrade ./landing.html

# From a directory — upgrades all frontend files in dependency order
/frontend-ui --upgrade ./components/
/frontend-ui --upgrade ./src/app/dashboard/

# From pasted code (saves to test_outputs/)
/frontend-ui --upgrade
[paste code below]
```

When given a directory, the skill discovers all frontend files, sorts them by dependency (tokens → layout → components → pages), and upgrades each in-place while maintaining cross-file consistency.

---

### Refinement passes (E–K) — applied after any generation

These require a prior generation in the same session (or a `DESIGN STATE` block).

```
bolder           → E: more visual impact, higher variance
quieter          → F: more restrained, more minimal
delight          → G: inject personality and surprise moments
harden           → H: add loading, error, and empty states
adapt            → I: responsive/mobile layout pass
fix typography   → J: type hierarchy and scale only
fix layout       → K: spacing and grid alignment only
```

Multiple passes can be combined: `bolder AND adapt`.

## Aesthetic archetypes (summary)

| Archetype | Character | Typical palette |
|-----------|-----------|-----------------|
| A — Obsidian Precision | Systematic, data-forward | Near-black + electric accent |
| B — Warm Editorial | Human, typographic | Off-white + serif + sage/rust |
| C — Chromatic Confidence | Bold, saturated | Rich fill + white knockout |
| D — Terminal Glass | Developer aesthetic | Dark glass + neon/coral |
| E — Luxury Silence | Premium restraint | White/bone + one muted accent |
| F — Soft Structuralism | Structured warmth | Stone + rounded geometry + pastel |
| G — Museum Authority | Institutional, archival, authoritative | Warm white + serif + restrained accent |
| H — Cinematic Portfolio | Expressive, project-led | Dark or bone + display-led contrast |
| I — Developer Personal | Text-first, precise | Monochrome or near-mono editorial palette |
| J — Custom | Flexible hybrid for novel categories | Derived from user description |

Full mapping, parameter values, and dark mode table are in `SKILL.md` and `knowledge/design/visual-archetypes.md`.

## File layout (progressive disclosure)

All files are lazy-loaded — the skill reads each file only when it enters the phase that needs it. SKILL.md is the only file always loaded; everything else is on-demand.

```
frontend-ui/
├── SKILL.md                                    # Router — persona, creative params, Phase 0–1.5
├── README.md
└── knowledge/
    ├── workflow/                               # Phase instructions — loaded at phase entry
    │   ├── phase2-dna.md                      # Phase 2: DNA extraction from URL/screenshot
    │   ├── phase3-discovery.md                # Phase 3: scene→archetype→palette→layout, Design Brief
    │   ├── phase4-generation.md               # Phase 4: UI generation + Phase 4.5 evaluation + Design Report
    │   ├── phase4b-upgrade.md                 # Phase 4b: upgrade mode (Mode D)
    │   └── phase5-template.md                 # Phase 5: save style as reusable template skill
    ├── references/                             # External site data — URLs for WebFetch research
    │   ├── reference-sites.md                 # Curated URLs by scene type with extraction notes
    │   └── brand-references.md                # Brand DNA, layout signatures, motion signatures + URLs
    ├── design/                                 # Design knowledge — decisions made before writing code
    │   ├── visual-archetypes.md               # A–J archetype descriptions, motion styles, dark mode table
    │   ├── color-palettes.md                  # 26 CSS token palettes + restrained vs. chromatic system
    │   ├── design-principles.md               # Core: composition, typography, color theory, spacing, depth, motion basics
    │   ├── design-principles-advanced.md      # Conditional: hero archetypes, visual rhythm, illustration, unforgettable moments
    │   ├── design-principles-motion.md        # Conditional: animation orchestration, performance budget (MOTION ≥ 4)
    │   ├── design-principles-ux.md            # Conditional: Nielsen's heuristics, forms, data display, navigation, microcopy
    │   ├── design-taste.md                    # Prescriptive craft rules + copy/microcopy standards
    │   ├── industry-patterns.md               # Industry-specific design overrides + section anatomy guides
    │   ├── page-sections.md                   # Landing page section anatomy: features, pricing, social proof, footer
    │   ├── data-visualization.md              # Chart types, KPI cards, dashboard layout, data color rules
    │   └── navigation.md                      # Top nav, sidebar, mobile nav, tabs, breadcrumbs, search
    └── implementation/                         # Code generation and quality gates
        ├── code-standards-core.md             # Always-loaded: CSS tokens, semantic HTML, Tailwind pattern, output format + pre-ship checklist
        ├── code-standards-extended.md         # Conditional: responsive, dark mode, ARIA, images, component states, SEO, SVG
        ├── advanced-effects.md                # Spotlight borders, grain overlays, glassmorphism, variable font animation
        └── upgrade-audit.md                   # P1–P10 upgrade priorities for existing code
```

| File | Loaded at |
|------|-----------|
| `SKILL.md` | Always (router + creative params) |
| `knowledge/workflow/phase2-dna.md` | Mode B / Mode C with URL — at Phase 2 entry |
| `knowledge/workflow/phase3-discovery.md` | Mode A / B / C — at Phase 3 entry |
| `knowledge/workflow/phase4-generation.md` | All generation paths — at Phase 4 entry |
| `knowledge/workflow/phase4b-upgrade.md` | Mode D — at Phase 4b entry |
| `knowledge/workflow/phase5-template.md` | Mode C — at Phase 5 entry |
| `knowledge/references/reference-sites.md` | Phase 1 — when optional scene references are needed |
| `knowledge/references/brand-references.md` | Phase 2b — DNA extraction from a reference URL |
| `knowledge/design/design-principles.md` | Phase 3 start — core composition guidance |
| `knowledge/design/design-principles-advanced.md` | Phase 3 — when DESIGN_VARIANCE ≥ 6 or archetype H/C/G |
| `knowledge/design/design-principles-motion.md` | Phase 3 — when MOTION_INTENSITY ≥ 4 |
| `knowledge/design/design-principles-ux.md` | Phase 3 — when component count ≥ 4 or forms/data/nav |
| `knowledge/design/visual-archetypes.md` | Phase 3 Step 2 — archetype selection |
| `knowledge/design/color-palettes.md` | Phase 3 Step 3 — palette selection |
| `knowledge/design/industry-patterns.md` | Phase 3 Design Brief Synthesis |
| `knowledge/design/page-sections.md` | Phase 3 — full page (≥ 3 sections) |
| `knowledge/design/data-visualization.md` | Phase 3 — dashboard, charts, or data tables |
| `knowledge/design/navigation.md` | Phase 4 — any page with navigation |
| `knowledge/design/design-taste.md` | Phase 4 start — craft rules enforcement |
| `knowledge/implementation/code-standards-core.md` | Phase 4 start — always (CSS tokens, HTML, Tailwind) + Phase 4.5 pre-ship checklist |
| `knowledge/implementation/code-standards-extended.md` | Phase 4 — full pages ≥ 3 sections or DENSITY ≥ 6 or component count ≥ 6 |
| `knowledge/implementation/advanced-effects.md` | Phase 4 — spotlight borders, grain, glassmorphism, variable fonts |
| `knowledge/implementation/upgrade-audit.md` | Phase 4b — Mode D (upgrade existing) only |

## Credits

Created by [Haofan Wang](https://haofanwang.github.io/) with Claude Code.

## License

MIT — Use it, modify it, share it.

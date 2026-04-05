# frontend-reactor

A Claude Code skill that converts cloned website HTML files into production-ready React/Next.js projects with proper component architecture, CSS decomposition, routing, and working interactivity.

## Installation

```bash
npx skills add https://github.com/instantX-research/skills --skill frontend-reactor
```

Or manually copy into your Claude Code skills directory:

```bash
cp -r skills/frontend-reactor ~/.claude/skills/
```

## What It Does

**frontend-reactor** takes static HTML files (typically produced by [`frontend-ui-clone`](#the-frontend-skill-family)) and transforms them into fully scaffolded React/Next.js projects. It parses semantic sections, decomposes CSS, generates typed components, wires up routing and navigation, and restores interactive behaviors — all verified by a real `npm run build`.

```
Clone HTML ──► Section mapping ──► CSS decomposition ──► JSX components ──► Next.js scaffold ──► Build & verify
```

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
| [**frontend-ui**](../frontend-ui/) | Design + generate new UI from scratch | Text description, reference URL, screenshot | Production-ready HTML/TSX |
| [**frontend-ui-clone**](../frontend-ui-clone/) | Pixel-perfect website cloning | URL | Self-contained `.html` file |
| **frontend-reactor** | Convert static HTML to React project | Clone `.html` file(s) or URL | Runnable Next.js project |

**Typical workflows:**

- **Clone & convert:** `/frontend-ui-clone https://linear.app` → `/frontend-reactor clone-linear.html`
- **Clone multiple pages, then convert:** Clone several pages → `/frontend-reactor clone-linear*.html`
- **URL shortcut:** `/frontend-reactor https://linear.app` (auto-clones homepage, then converts)
- **Design from scratch:** `/frontend-ui a SaaS landing page` (no cloning — generates original UI)

## Usage

```
/frontend-reactor <clone-file.html ... | URL> [--css tailwind|modules|global] [--framework nextjs|vite] [--simple] [--output ./my-project]
```

Or ask naturally:

- "Convert this clone to React"
- "Turn clone-linear.html into a Next.js project"
- "Make a real project from these HTML files"
- "Rebuild https://example.com as React components"

---

### Mode A — Single clone file

Pass one `.html` file. Outputs a single-route React project.

```
/frontend-reactor test_outputs/clone-linear.html
/frontend-reactor clone-stripe.html --css tailwind
```

### Mode B — Multiple clone files

Pass multiple files or a glob pattern. Outputs a multi-route project with shared Navbar/Footer and cross-page navigation.

```
/frontend-reactor test_outputs/clone-linear*.html
/frontend-reactor clone-home.html clone-pricing.html clone-about.html
```

Cross-page deduplication automatically detects shared components (>85% similarity) and extracts them into `components/shared/`.

### Mode C — URL input

Pass a URL directly. The skill auto-clones the homepage via `frontend-ui-clone`, discovers all interactive elements with Playwright, and converts to a single-route React project. All internal links point back to the original site.

```
/frontend-reactor https://linear.app
/frontend-reactor https://resend.com --css tailwind --output ./my-resend
```

### --simple mode

Skip React entirely. Splits the clone into clean HTML + external CSS + empty JS scaffold.

```
/frontend-reactor clone-linear.html --simple
```

Output: `results/split-[domain]/index.html` + `styles.css` + `scripts.js`

## Options

| Flag | Values | Default | Effect |
|------|--------|---------|--------|
| `--css` | `tailwind`, `modules`, `global` | `global` | CSS strategy |
| `--framework` | `nextjs`, `vite` | `nextjs` | Output framework |
| `--simple` | (flag) | off | Non-React: clean HTML + CSS split |
| `--download-assets` | (flag) | off | Download images/fonts to `public/` |
| `--output` | path | `results/reactor-[domain]/` | Custom output directory |

## Conversion Pipeline

### Phase 1 — HTML Analysis & Section Mapping

Parses clone HTML and identifies semantic sections using priority signals:

1. HTML5 semantic tags (`<nav>`, `<header>`, `<section>`, `<footer>`)
2. ARIA roles
3. Class name patterns (`*hero*` → Hero, `*pricing*` → Pricing)
4. ID attributes
5. Structural position (first child → Navbar, last child → Footer)

Extracts a link map classifying every `<a href>` as internal, anchor, external, or mail/tel.

### Phase 2 — CSS Decomposition

Extracts CSS from the clone's `<style>` block in strict order:

1. `@import` rules → `@property` declarations → `:root` design tokens
2. `@layer` rules → `@font-face` rules → base element selectors
3. `@keyframes` animations → shared utilities → fix overrides

CSS strategy selection:
- **Global** (default) — safest for clones; preserves cascade ordering
- **Tailwind** — auto-detected from `@property --tw-*`, `@layer base`, Tailwind class patterns
- **CSS Modules** — only when explicitly requested via `--css modules`

### Phase 3 — React Component Generation

- HTML → JSX conversion (`class` → `className`, self-closing tags, style objects, SVG attributes)
- Link conversion (Mode A: plain `<a>`, Mode B: Next.js `<Link>`, Mode C: absolute URLs to original site)
- SVG icon extraction (icons ≤48px appearing 2+ times → `components/icons.tsx`)
- Interactivity restoration in priority order:

| Priority | Pattern | Implementation |
|----------|---------|----------------|
| 1 | Dropdown / mobile nav | `useState` + click-outside handler |
| 2 | Anchor scroll links | `scrollIntoView({ behavior: 'smooth' })` |
| 3 | Accordions / FAQ | `useState` expand/collapse + height transition |
| 4 | Tabs | `useState` active tab + panel show/hide |
| 5 | Forms | `useState` + `onChange` + `onSubmit` |
| 6 | Modals / popups | `useState` toggle + backdrop close |
| 7 | Carousels / sliders | `useState` slide position + CSS transform |

### Phase 4 — Project Scaffolding

Initializes a Next.js or Vite project and writes files in dependency order:

```
globals.css → tailwind.config.ts → next.config.mjs → icons.tsx
→ shared components → page components → layout.tsx → page routes
```

Handles font conversion (Google Fonts → `next/font/google`) and asset referencing.

### Phase 5 — Build Verification

Runs `npm run build` and auto-fixes common errors (up to 3 rounds):
- `class` → `className`, unclosed tags, missing imports
- `usePathname` in server components → add `'use client'`
- Image hostnames → add to `next.config.mjs` remotePatterns

## Output

Projects are written to `results/reactor-[domain]/`:

```
results/reactor-linear/
├── app/
│   ├── layout.tsx              # Root layout with Navbar, Footer, fonts
│   ├── page.tsx                # Homepage
│   ├── globals.css             # All extracted CSS + design tokens
│   └── pricing/
│       └── page.tsx            # Sub-routes (Mode B)
├── components/
│   ├── shared/
│   │   ├── Navbar.tsx          # Shared across pages, with active state
│   │   └── Footer.tsx
│   ├── home/
│   │   ├── Hero.tsx
│   │   ├── Features.tsx
│   │   └── CTA.tsx
│   └── icons.tsx               # Extracted SVG icons
├── public/                     # Downloaded assets (if --download-assets)
├── next.config.mjs
├── package.json
└── tsconfig.json
```

## Key Principles

1. **CSS safety first** — when unsure which component a CSS rule belongs to, keep it in globals.css
2. **Preserve fidelity** — the React project should render identically to the clone HTML
3. **Progressive enhancement** — start with static output, then layer interactivity
4. **Minimal dependencies** — no animation/form/utility libraries unless the clone requires them

## Requirements

For Mode C (URL input), **Playwright** is required:

```bash
pip install playwright
playwright install chromium
```

Modes A and B work with any clone HTML file — no external tools needed.

## File Layout

```
frontend-reactor/
├── SKILL.md                              # Conversion pipeline — all 5 phases
├── README.md
└── knowledge/
    ├── component-detection.md            # Section identification rules and signals
    ├── css-extraction.md                 # CSS splitting and classification
    ├── html-to-jsx.md                    # HTML → JSX conversion rules
    ├── interactivity.md                  # Interactive pattern detection and restoration
    ├── nextjs-scaffold.md                # Project templates and scaffolding
    └── site-discovery.md                 # Playwright crawling patterns (Mode C)
```

## Credits

Created by [Haofan Wang](https://haofanwang.github.io/) with Claude Code.

## License

MIT — Use it, modify it, share it.

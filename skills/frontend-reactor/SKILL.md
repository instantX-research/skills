---
name: frontend-reactor
version: 1.0.0
description: |
  Converts cloned website HTML files (from frontend-ui-clone) into production-ready
  React/Next.js projects. Extracts components, decomposes CSS, sets up routing,
  and wires navigation so buttons and links actually work.
  Three modes: single clone file, multiple clone files, or a URL (auto-discovers and extracts all pages).
  Outputs a runnable Next.js App Router project with `npm run dev` ready to go.
  Use when asked to "convert to React", "make a Next.js project", "turn clone into components",
  "wire up navigation", "split into components", "make it a real project",
  "convert HTML to React", "productionize the clone", "rebuild this website",
  or "convert this site to React".
user-invocable: true
disable-model-invocation: false
context: fork
agent: general-purpose
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - WebFetch
  - AskUserQuestion
  - Agent
argument-hint: "<clone-file.html ... | URL> [--css tailwind|modules|global] [--framework nextjs|vite] [--simple] [--output ./my-project]"
---

You are a **frontend conversion engineer**. You transform cloned website HTML files into
production-ready React/Next.js projects with proper component architecture and working navigation.

**Language rule:** Mirror the user's language for all non-code text. Code is always English.

**User request:** $ARGUMENTS

---

## Phase 0 — Parse Input & Detect Mode

### Step 1 — Determine input mode

Parse `$ARGUMENTS` to detect the input type:

**Mode A — Single clone file:**
- Input is a path to a single `.html` file (e.g., `test_outputs/clone-linear.html`)
- Verify the file exists with `Read`
- Output: single-route React project

**Mode B — Multiple clone files:**
- Input contains multiple `.html` file paths, or a glob pattern (e.g., `test_outputs/clone-linear*.html`)
- Use `Glob` to resolve file paths
- Output: multi-route React project with navigation

**Mode C — URL (single-page clone + live links):**
- Input is a URL (starts with `http://` or `https://`)
- Clones ONLY the homepage using `frontend-ui-clone` for pixel-perfect fidelity
- Uses Playwright to discover all navigation links (nav, footer, buttons)
- All internal links and buttons point to the ORIGINAL site (not local routes)
- Output: single-route React project where clicking any link/button goes to the real site
- See **Phase 0C** below for the full workflow

**Auto-detection order:**
1. If input contains one `.html` path → Mode A
2. If input contains multiple `.html` paths or a glob pattern → Mode B
3. If input starts with `http://` or `https://` → Mode C
4. If no clear input → ask with `AskUserQuestion`

### Step 2 — Parse options

| Flag | Values | Default | Effect |
|------|--------|---------|--------|
| `--css` | `tailwind`, `modules`, `global` | `global` | CSS strategy (global recommended for most clones) |
| `--framework` | `nextjs`, `vite` | `nextjs` | Output framework |
| `--simple` | (flag) | off | Non-React output: clean HTML + CSS split only |
| `--download-assets` | (flag) | off | Download images/fonts to local public/ |
| `--output` | path | `$(pwd)/results/reactor-[domain]/` | Custom output directory |
| `--validate` | (flag) | off (on for Mode C) | Run Playwright visual & interaction validation against the original site |

### Step 3 — Extract domain name for project naming

From the clone HTML filename or URL, extract domain:
- `clone-linear.html` → `linear`
- `clone-stripe-02.html` → `stripe`
- `https://www.magicpath.ai/` → `magicpath`

Project output directory: 
- If `--output` specified → use that path
- Otherwise → `$(pwd)/results/reactor-[domain]/`

---

## Phase 0C — Homepage Clone + Link Discovery (Mode C only)

**Load knowledge:** Read `knowledge/site-discovery.md` for Playwright crawling patterns.

Mode C clones ONLY the homepage, then wires all links/buttons to point to the original site.

### Step 0C.1 — Clone homepage with frontend-ui-clone

Use the `Agent` tool to invoke `frontend-ui-clone` for the homepage URL:

```
Agent(
  description: "Clone homepage",
  prompt: "Use the Skill tool to invoke frontend-ui-clone with this URL: [URL]. 
           Wait for it to complete and report the output file path.",
  subagent_type: "general-purpose"
)
```

This produces a single high-fidelity clone HTML (~97% pixel-perfect).

**Fallback:** If Agent/Skill invocation fails, fall back to direct Playwright extraction using the script in `knowledge/site-discovery.md` Phase D.

### Step 0C.2 — Discover all interactive elements on the homepage

Use Playwright on the live page (before or after cloning) to run the **runtime interactive element detection** script from `knowledge/site-discovery.md` Phase A2.

This script detects ALL interactive elements by checking:
- `cursor: pointer` (strongest signal — catches styled `<div>` buttons with no semantic markup)
- `<a href>`, `<button>`, `<input>`, `<select>`, `<textarea>` tags
- ARIA attributes (`role="button"`, `aria-expanded`, `aria-haspopup`, `data-state`)
- `tabindex >= 0`, inline `onclick` handlers

**Output:** A JSON list of every interactive element with:
- Tag, text, href, placeholder
- Signals (why it's interactive)
- Location (nav/footer/body)
- Bounding box (position on page)

This list drives Phase 3 Step 6 (interactivity restoration) — every element in this list gets a corresponding fixup in the converted components.

### Step 0C.3 — Link strategy for Mode C

**ALL internal links point to the original site.** No local routes are created for subpages.

```
Internal links:
  href="/pricing"                    → href="https://original-site.com/pricing"
  href="/about"                      → href="https://original-site.com/about"
  href="/documentation/getting-started" → href="https://original-site.com/documentation/getting-started"

Buttons (dead <button> with no href):
  <button>Sign in</button>          → <a href="https://original-site.com/signin">Sign in</a>
  <button>Get started</button>      → <a href="https://original-site.com">Get started</a>

External links:
  Keep as-is with target="_blank" rel="noopener noreferrer"

Anchor links (#section):
  Keep as-is (scroll within the page)
```

### Step 0C.4 — Transition to Mode A pipeline

With the single homepage clone file, proceed as **Mode A**:
- Phase 1: Analyze the clone HTML (section mapping)
- Phase 2: CSS decomposition
- Phase 3: React component generation + interactivity + link fixup
- Phase 4: Project scaffolding (single route only: `/`)
- Phase 5: Build verification

**Critical in Phase 3:** When converting links, do NOT use relative paths. Convert ALL internal links to absolute URLs pointing to the original site:
```
href="/pricing"  →  href="https://[original-domain]/pricing"
```

---

## Phase 1 — HTML Analysis & Section Mapping

**Load knowledge:** Read `knowledge/component-detection.md` for section identification rules.

For EACH clone HTML file:

### Step 1 — Read and parse the HTML

Use `Read` to load the clone HTML file. Identify:

1. **The `<style>` block** — Extract the entire contents between `<style>` and `</style>` tags.
   The structure follows `frontend-ui-clone`'s ordering:
   - @import rules
   - @property declarations
   - :root block with CSS custom properties
   - @layer declarations
   - @font-face rules
   - Framework CSS rules
   - Fix overrides (at the end, with `!important`)

2. **The `<head>` metadata** — Extract:
   - `<title>` text
   - `<meta name="description">` content
   - `<link>` tags (fonts, favicons, preloads)
   - `<html>` attributes (`lang`, `class`, `data-theme`, etc.)

3. **The `<body>` content** — Everything between `<body>` and `</body>`, excluding `<script>` tags.

### Step 2 — Identify semantic sections

Apply the detection strategy from `knowledge/component-detection.md`:

1. **Scan top-level children** of `<body>` (or the first wrapper `<div>` if body has a single child wrapper)
2. For each top-level element, classify using signals (priority order):
   - HTML5 semantic tags (`<nav>`, `<header>`, `<section>`, `<footer>`)
   - ARIA roles
   - Class name patterns
   - ID attributes
   - Structural position (first = Navbar, last = Footer)
3. Assign a component name to each section (PascalCase)

**Output of this step:** An ordered list of sections with:
```
[
  { name: "Navbar", tag: "nav", startLine: 45, endLine: 92, classes: ["nav", "nav-container"] },
  { name: "Hero", tag: "section", startLine: 93, endLine: 180, classes: ["hero", "hero-section"] },
  { name: "Features", tag: "section", startLine: 181, endLine: 320, classes: ["features-grid"] },
  ...
  { name: "Footer", tag: "footer", startLine: 890, endLine: 960, classes: ["footer", "site-footer"] },
]
```

### Step 3 — Extract link map

Parse all `<a href="...">` in the body:

1. Extract every `href` value
2. Classify each link:
   - **Internal** (same domain as the cloned site): `https://linear.app/pricing` → route `/pricing`
   - **Anchor** (hash links): `#features`, `#pricing`
   - **External** (different domain): `https://github.com/linear`
   - **Mail/tel**: `mailto:`, `tel:`
3. Build a route map for internal links:
   ```
   /pricing  → app/pricing/page.tsx
   /about    → app/about/page.tsx
   /blog     → app/blog/page.tsx (if clone exists, else external link)
   ```

### Step 4 — Cross-page deduplication (Mode B only; Mode C does this in Phase 0C.6)

Compare sections across all clone HTML files:

1. Extract the first section (usually Navbar) and last section (usually Footer) from each file
2. Compare their HTML content (normalize whitespace, ignore active-state classes)
3. If similarity > 85% → mark as shared component
4. Extract the canonical version from the homepage clone
5. Note differences (active nav link, page-specific CTA text) for prop-based variation

---

## Phase 2 — CSS Decomposition

**Load knowledge:** Read `knowledge/css-extraction.md` for CSS splitting rules.

### Step 1 — Detect CSS strategy

If user specified `--css`, use that. Otherwise:

1. **Default → Global CSS** — All CSS stays in `globals.css`. This is the safest strategy for clone conversions because:
   - Clone CSS relies on specific cascade ordering that CSS Modules would break
   - Webflow/framework sites share class names across many sections (`.w-nav`, `.w-button`, `.container`)
   - Splitting CSS incorrectly causes subtle visual regressions
2. **Tailwind** (auto-detected if clone uses Tailwind) — Check for signals:
   - `@property --tw-*` declarations
   - `@layer base, components, utilities`
   - `:root` contains `--tw-*` properties
   - Majority of class names match Tailwind patterns (`flex`, `p-4`, `text-sm`, `bg-*`, etc.)
   - If detected → extract tokens to `tailwind.config.ts`, keep utility classes in JSX
3. **CSS Modules** (`--css modules`) — Only use when explicitly requested. Requires careful class-to-component mapping. See `knowledge/css-extraction.md` for the classification algorithm.

### Step 2 — Extract global CSS

From the `<style>` block, extract these into `globals.css`:

1. All `@import` rules
2. All `@property` declarations
3. The entire `:root { ... }` block (design tokens)
4. All `@layer` declarations
5. All `@font-face` rules
6. Base element selectors (`*`, `html`, `body`, `h1`-`h6`, `p`, `a`, etc.)
7. All `@keyframes` rules
8. The fix overrides block (everything with `!important` at the end)

### Step 3 — Classify remaining CSS rules

For each remaining CSS rule:

1. Parse the selector to extract referenced class names
2. Match class names against the component sections from Phase 1
3. Classify:
   - **Single component match** → that component's CSS module file
   - **Multiple component match** → globals.css (shared utilities section)
   - **No match** → globals.css
4. For `@media` queries containing rules for multiple components → split into separate `@media` blocks

### Step 4 — Tailwind-specific processing (if applicable)

If Tailwind strategy:
1. Extract design tokens from `:root` and map to `tailwind.config.ts`:
   - `--color-*` → `theme.extend.colors`
   - `--font-*` → `theme.extend.fontFamily`
   - `--radius-*` → `theme.extend.borderRadius`
   - `--shadow-*` → `theme.extend.boxShadow`
   - `--space-*` → `theme.extend.spacing`
2. Keep Tailwind utility classes as-is in JSX (`className="flex items-center p-4"`)
3. Move non-utility custom CSS to globals.css

### Step 5 — Design token summary

Output a summary of extracted design tokens:
```
Colors:   12 tokens (--color-bg, --color-text-primary, --color-accent, ...)
Fonts:    2 families (Inter, Playfair Display)
Spacing:  8px grid base
Radii:    4 tokens (--radius-sm: 4px, --radius-md: 8px, ...)
Shadows:  3 tokens
Motion:   2 tokens (--duration-fast: 150ms, --ease-out: cubic-bezier(...))
```

---

## Phase 3 — React Component Generation

**Load knowledge:** Read `knowledge/html-to-jsx.md` for conversion rules.

### Step 1 — HTML → JSX conversion

For each section's HTML fragment, apply all conversion rules from `knowledge/html-to-jsx.md`:

1. **Attribute transforms**: `class` → `className`, `for` → `htmlFor`, etc.
2. **Self-closing tags**: `<img>` → `<img />`, `<br>` → `<br />`, etc.
3. **Inline styles**: `style="..."` → `style={{ camelCase: 'value' }}`
4. **SVG attributes**: `stroke-width` → `strokeWidth`, etc.
5. **Comments**: `<!-- -->` → `{/* */}`
6. **Remove event handlers**: Strip all `on*` attributes

**Validation step:** After conversion, check for common JSX errors:
- Unclosed tags
- Reserved word attributes not converted
- Unescaped `{` or `}` in text content
- Adjacent JSX elements without a wrapper

### Step 2 — Link conversion

Strategy depends on the input mode:

**Mode A (single page):** No sub-routes exist, so internal links stay as plain `<a>` tags:
```
Internal links → <a href="/pricing">text</a>  (relative path, plain <a>)
Anchor links   → <a href="#id">text</a>  (keep as-is)
External links → <a href="url" target="_blank" rel="noopener noreferrer">text</a>
```

**Mode B/C (multi-page):** Sub-routes exist, so use Next.js `<Link>` for routed pages:
```
Internal links WITH clone → <Link href="/pricing">text</Link>  (import from next/link)
Internal links WITHOUT clone → <a href="/blog">text</a>  (plain <a>, add TODO comment)
Anchor links → <a href="#id">text</a>  (keep as-is)
External links → <a href="url" target="_blank" rel="noopener noreferrer">text</a>
```

For internal links to pages NOT in the clone/extracted set (Mode B/C):
```tsx
{/* TODO: Clone /blog page and add route */}
<a href="/blog">Blog</a>
```

In ALL modes, convert absolute URLs to relative paths:
- `https://example.com/pricing` → `/pricing`
- `https://example.com/` → `/`
- `https://example.com/#features` → `/#features`

### Step 3 — Component file creation

For each section, create the component file:

**Shared components** → `components/shared/[Name].tsx`
**Page-specific components** → `components/[page]/[Name].tsx`

Each component file structure:
```tsx
// CSS Modules variant
import styles from './[Name].module.css';

export function [Name]() {
  return (
    [converted JSX]
  );
}
```

Or for Tailwind:
```tsx
export function [Name]() {
  return (
    [converted JSX with Tailwind classes]
  );
}
```

### Step 4 — Shared Navbar with active state (Mode B/C)

If Navbar is a shared component across pages, add `usePathname()` for active link highlighting:

```tsx
'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export function Navbar() {
  const pathname = usePathname();
  // ... render nav links with active state based on pathname
}
```

### Step 5 — SVG icon extraction

Scan all components for inline SVGs that qualify as icons:
- Width/height ≤ 48px
- Appears 2+ times across components
- Simple path data (< 500 chars)

Extract qualifying SVGs into `components/icons.tsx` as named exports.
Replace inline SVGs in components with imports from `icons.tsx`.

### Step 6 — Interactivity restoration

**Load knowledge:** Read `knowledge/interactivity.md` for all interactive patterns and detection strategies.

After generating static components, restore interactivity using two sources:

1. **Runtime detection results (Mode C):** The JSON list from Phase 0C.2 tells you exactly which elements are interactive and why. Match each element by its text/classes/position to the corresponding component, and apply the appropriate fixup.
2. **Class-name pattern matching (Mode A/B, or as supplement):** Scan component JSX for known interactive patterns (see `knowledge/interactivity.md` Layer 2).

Process in priority order:

**Priority 1 — Navigation interactivity:**
- Dropdown menus in Navbar → wrap with `useState` open/close + click-outside handler
- Mobile hamburger menu → toggle state for menu visibility
- These are CRITICAL — broken nav = unusable site

**Priority 2 — Anchor links:**
- `<a href="#section-id">` → add `onClick` with `scrollIntoView({ behavior: 'smooth' })`
- Simple and high-impact

**Priority 3 — Accordions / FAQ:**
- Detect repeating question+answer pattern
- Wrap each item with `useState` for expand/collapse
- Add `max-height` transition for smooth animation

**Priority 4 — Tabs:**
- Detect tab menu + tab content panels
- Wrap with `useState` for active tab index
- Show/hide panels based on active state

**Priority 5 — Forms:**
- Detect `<form>`, `<input>`, `<textarea>`, `<select>` elements
- Add `useState` for form data, `onChange` handlers on inputs
- Add `onSubmit` handler (log to console + show success state)
- Preserve all original styling classes

**Priority 6 — Modals / popups:**
- Detect hidden overlays with `position: fixed`
- Find trigger buttons, wire up `useState` toggle
- Add backdrop click-to-close and close button

**Priority 7 — Carousels / sliders:**
- Detect slider patterns (Webflow `w-slider`, custom carousels)
- Add `useState` for current slide, prev/next buttons
- CSS `transform: translateX` for slide transitions

**For each interactive component:**
1. Add `'use client';` directive at the top
2. Import necessary hooks (`useState`, `useRef`, `useEffect`)
3. Wrap interactive elements with state logic
4. **Preserve ALL original class names and HTML structure** — only add behavior, don't restructure
5. Keep non-interactive components as server components

**P8 — Post-clone fixups (for dangerouslySetInnerHTML components):**

When components use `dangerouslySetInnerHTML`, apply these fixups to the raw HTML string:

1. **className → class:** `dangerouslySetInnerHTML` renders raw HTML, NOT JSX. Must use `class`, `for`, `tabindex`, not `className`, `htmlFor`, `tabIndex`. See `knowledge/html-to-jsx.md` "dangerouslySetInnerHTML Rules".
2. **Dead buttons → links:** Convert `<button>Sign in</button>` to `<a href="/signin">Sign in</a>`. Convert CTA buttons to links pointing to original site. See `knowledge/interactivity.md` Pattern 10.
3. **Input overlay removal:** Remove typewriter overlay (`pointer-events-none` div with static text over input), restore input visibility, add placeholder. See `knowledge/interactivity.md` Pattern 9.
4. **URL normalization:** Convert `href="https://original-site.com/path"` to `href="/path"` for internal links. See `knowledge/interactivity.md` Pattern 11.
5. **Cursor pointer:** Add `cursor: pointer` on remaining `<button>` elements.

**What NOT to restore:**
- Third-party widgets (chat, analytics) — need API keys
- Complex JS animations (GSAP, Lottie, WebGL) — out of scope
- Backend-dependent features (auth, real-time data)
- Note any skipped interactivity in the final report

---

## Phase 4 — Project Scaffolding & Assembly

**Load knowledge:** Read `knowledge/nextjs-scaffold.md` for project templates.

### Step 1 — Initialize project

Determine the output directory from Phase 0 Step 3 (either `--output` path or `$(pwd)/results/reactor-[domain]/`).

**Next.js (default):**
```bash
# Create in parent of output dir, with output dir name
npx create-next-app@latest [output-dir] \
  --typescript \
  --eslint \
  --app \
  --src-dir=false \
  --import-alias="@/*" \
  --no-turbopack \
  [--tailwind]  # only if Tailwind detected
```

**Vite + React (if --framework vite):**
```bash
npm create vite@latest [output-dir] -- --template react-ts
cd [output-dir]
npm install
npm install react-router-dom
[npm install -D tailwindcss postcss autoprefixer]  # if Tailwind
```

### Step 2 — Clean boilerplate

Remove default content from:
- `app/page.tsx` (Next.js) or `src/App.tsx` (Vite)
- `app/globals.css` or `src/index.css`
- `public/` placeholder files

### Step 3 — Write all files

Write files in this order (dependencies first):

1. **`app/globals.css`** — Global styles from Phase 2
2. **`tailwind.config.ts`** — If Tailwind mode, with extracted design tokens
3. **`next.config.mjs`** — With `images.remotePatterns` for the original domain
4. **`components/icons.tsx`** — Extracted SVG icons
5. **`components/shared/Navbar.tsx`** + CSS module — Shared Navbar
6. **`components/shared/Footer.tsx`** + CSS module — Shared Footer
7. **`components/[page]/[Section].tsx`** + CSS modules — All page-specific sections
8. **`app/layout.tsx`** — Root layout importing Navbar, Footer, globals.css, fonts
9. **`app/page.tsx`** — Homepage composing its sections
10. **`app/[route]/page.tsx`** — Each sub-route composing its sections

### Step 4 — Font handling

Detect fonts from the clone HTML:

1. **Google Fonts** (from `@import` or `<link>` tags):
   - Convert to `next/font/google` imports in `layout.tsx`
   - Set CSS variables (`--font-sans`, `--font-display`)
   - Remove the `@import` from globals.css (Next.js handles it)

2. **Custom fonts** (from `@font-face`):
   - Keep in globals.css
   - If `--download-assets` flag, download `.woff2` files to `public/fonts/`

### Step 5 — Asset handling

Default: Keep all image URLs as absolute paths pointing to the original site.

If `--download-assets` flag:
1. Parse all `src`, `srcset`, and CSS `url()` values
2. Download images to `public/assets/`
3. Download fonts to `public/fonts/`
4. Rewrite URLs in components and CSS to relative paths (`/assets/image.jpg`)

---

## Phase 5 — Build Verification & Report

### Step 1 — Build test

```bash
cd [output-dir]
npm run build 2>&1
```

### Step 2 — Error diagnosis and fix (up to 3 rounds)

If build fails, diagnose the error:

| Error Pattern | Fix |
|---------------|-----|
| `class` in JSX | Convert to `className` |
| `for` in JSX | Convert to `htmlFor` |
| Unclosed tag | Add self-closing `/>` |
| `style` is string | Convert to style object |
| Missing `Link` import | Add `import Link from 'next/link'` |
| `usePathname` in server component | Add `'use client'` directive |
| Image hostname not allowed | Add to `next.config.mjs` remotePatterns |
| Module not found | Check import paths |
| TypeScript type error | Add appropriate types or `// @ts-ignore` as last resort |

After each fix, re-run `npm run build`. Max 3 rounds.

### Step 3 — Output report

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FRONTEND REACTOR — CONVERSION COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Source           [N] clone HTML file(s)
Output           [output-dir]
Framework        Next.js 15 (App Router) + TypeScript
CSS strategy     [CSS Modules / Tailwind / Global]

COMPONENTS
  Shared:        [N] (Navbar, Footer)
  Page-specific: [N] (Hero, Features, Pricing, ...)
  Icons:         [N] SVG icons extracted

ROUTES
  /              → app/page.tsx (Hero, Features, Testimonials, CTA)
  /pricing       → app/pricing/page.tsx (PricingHero, Plans, FAQ)
  /about         → app/about/page.tsx (AboutHero, Team, Story)

DESIGN TOKENS
  Colors: [N] | Fonts: [N] | Spacing: [base]px | Radii: [N] | Shadows: [N]

LINKS
  Internal (routed): [N]
  External: [N]
  Uncloned pages: [list of internal links without clone files]

INTERACTIVITY RESTORED
  ✓ Dropdown menus: [N]
  ✓ Mobile nav toggle: [yes/no]
  ✓ Accordions/FAQ: [N] items
  ✓ Tabs: [N] sets
  ✓ Forms: [N] (client-side state)
  ✓ Modals: [N]
  ✓ Anchor scroll: [N] links
  ✗ Skipped: [list of complex interactions not restored]

BUILD STATUS    ✓ Passed  /  ✗ Failed (see errors above)

VALIDATION      [Skipped / see below]

TO RUN
  cd [output-dir] && npm run dev

TO DEPLOY
  cd [output-dir] && vercel deploy
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

If `--validate` is set (or Mode C), proceed to **Phase 6** for Playwright validation.

---

## Phase 6 — Playwright Visual & Interaction Validation

**Load knowledge:** Read `knowledge/playwright-validation.md` for all validation scripts and diff algorithms.

This phase runs when `--validate` is set, or automatically in Mode C (URL input). It requires the original site URL and a successful `npm run build` from Phase 5.

### Step 1 — Start dev server

```bash
cd [output-dir]
npm run dev -- -p 3000 &
```

Wait for `localhost:3000` to be ready (poll with socket connect, max 30s).

### Step 2 — Visual screenshot comparison

Capture full-page screenshots of both the original site and `localhost:3000` at three viewports:

| Viewport | Size |
|----------|------|
| Desktop | 1440×900 |
| Tablet | 768×1024 |
| Mobile | 375×812 |

Before capturing, normalize both pages:
- Remove cookie banners/overlays
- Force all animation durations to `0s` for consistent static captures
- Scroll to bottom and back to trigger lazy loading
- Force `opacity: 1` on animated elements

Generate pixel diff images and calculate similarity scores per viewport.

### Step 3 — Interactive element audit

Run the interactive element detection script (same as `site-discovery.md` Phase A2) on both pages. Compare:

1. **Count:** How many interactive elements exist on each page
2. **Match by text + position:** Pair elements between original and converted
3. **Signal degradation:** Elements that exist but lost interactivity signals (e.g., a link that lost `cursor-pointer`, a button that lost `has-popup`)
4. **Missing elements:** Interactive elements on the original that are absent on the converted

### Step 4 — Hover state comparison

For the top 10 interactive elements (prioritizing nav links, buttons, CTAs):

1. Screenshot each element before hover
2. Hover over it, wait 500ms for transitions
3. Screenshot after hover
4. Pixel-diff the before/after for each element on both sites
5. Flag elements where original has a visible hover effect but converted does not

### Step 5 — Animation & transition diff

Extract from both pages:

1. **@keyframes definitions** — compare by name; flag missing keyframes
2. **CSS transitions** — compare `transition-property` + `transition-duration` on interactive elements; flag transitions present on original but missing on converted
3. **Animated elements** — elements with active `animation-name`; flag elements that were animated on the original but are static on the converted

### Step 6 — Scroll & sticky element validation

Compare:
- `scroll-behavior: smooth` on `<html>`
- Count of `position: sticky` elements
- Count of `position: fixed` elements

Flag any mismatches.

### Step 7 — Auto-fix (up to 2 rounds)

If critical issues are found (visual similarity < 80% on any viewport, OR > 30% of interactive elements missing):

1. **Missing @keyframes** → copy the keyframe definition from the original CSS into `globals.css`
2. **Missing hover transitions** → find the `:hover` rules for the flagged elements from the original CSS and add them to `globals.css`
3. **Missing `cursor: pointer`** → add `cursor: pointer` to the element's CSS class
4. **Missing sticky/fixed positioning** → check if `position: sticky/fixed` was dropped during CSS extraction

After each fix round:
- Re-run `npm run build`
- Re-run the validation pipeline
- Stop if scores improve above thresholds or after 2 rounds

### Step 8 — Validation report

Append validation results to the Phase 5 output report:

```
VALIDATION (Playwright)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Original URL       [url]
  Dev server         localhost:3000

  VISUAL FIDELITY
    Desktop (1440px): [N]% similarity  [✓/△/✗]
    Tablet  (768px):  [N]% similarity  [✓/△/✗]
    Mobile  (375px):  [N]% similarity  [✓/△/✗]
    Diff images saved to: [output-dir]/validation-report/

  INTERACTIVE ELEMENTS
    Matched:   [N]/[M] ([P]%)
    Missing:   [N] — [list of missing element names]
    Degraded:  [N] — [list of elements with lost signals]

  HOVER STATES
    Matching:       [N]/[M]
    Missing hover:  [N] — [list]
    Different hover: [N] — [list]

  ANIMATIONS & TRANSITIONS
    @keyframes matched: [N] | missing: [N] — [list]
    Transitions matched: [N] | missing: [N]
    Animated elements matched: [N] | missing: [N]

  SCROLL BEHAVIOR
    Smooth scroll:   [✓/✗]
    Sticky elements: [✓/✗] (original: [N], converted: [M])
    Fixed elements:  [✓/✗] (original: [N], converted: [M])

  AUTO-FIX APPLIED
    [N] fixes applied in [R] rounds
    [list of fixes]

  OVERALL SCORE      [N]/100
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Overall score calculation:**
- Visual fidelity (desktop): 40 points (proportional to similarity %)
- Interactive element match rate: 25 points
- Hover state match rate: 15 points
- Animation/transition match rate: 15 points
- Scroll behavior match: 5 points

---

## --simple Mode (Non-React Split)

If `--simple` flag is set, skip React conversion. Instead:

1. **Split the clone HTML into:**
   - `index.html` — Clean HTML with `<link rel="stylesheet" href="styles.css">`
   - `styles.css` — All CSS extracted from `<style>` block
   - `scripts.js` — Empty file with TODO comments for interactivity

2. **Clean up the HTML:**
   - Replace `<style>...</style>` with `<link>` tag
   - Fix any remaining inline styles
   - Organize `<head>` metadata

3. **Organize the CSS:**
   - Add section comments for navigation
   - Group by: resets → tokens → typography → layout → components → utilities → overrides

4. **Output to:** `$(pwd)/results/split-[domain]/` (or `--output` path if specified)

---

## Error Handling

- **Clone file not found:** Ask user for correct path with `AskUserQuestion`
- **Clone HTML is malformed:** Attempt best-effort parsing, warn user about sections that couldn't be parsed
- **`npx create-next-app` fails:** Fall back to manual project scaffolding (write package.json, tsconfig.json by hand)
- **Build errors persist after 3 rounds:** Output the error log and ask user for guidance
- **No semantic sections detected:** Fall back to splitting `<body>` children as numbered sections

---

## Key Principles

1. **CSS safety first:** When unsure which component a CSS rule belongs to, keep it in globals.css. A slightly bloated globals.css is better than broken styles.
2. **Preserve fidelity:** The React project should render identically to the clone HTML. Don't "improve" or "clean up" the visual output.
3. **Progressive enhancement:** Start with static output, then add interactivity (active nav, client-side routing). Don't break what works.
4. **Minimal dependencies:** Only add packages that are strictly necessary. Don't add animation libraries, form libraries, or utility packages unless the clone requires them.

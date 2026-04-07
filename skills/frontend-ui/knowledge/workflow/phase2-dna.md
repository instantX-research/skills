## Phase 2 — Design DNA Extraction (Mode B only — URL/screenshot provided)

Extract a complete design system from the reference.

**Input type branch — resolve first:**
- `REF` starts with `http` → run 2-pre (fidelity), then 2a (fetch `REF`), then 2b (analysis)
- `REF` is a local file path → skip 2-pre and 2a; default fidelity = High-fidelity; proceed directly to 2b using visual analysis of the file

---

### 2-pre. Fidelity level (URL inputs only)

Ask with `AskUserQuestion` (skip if user already specified):
> What fidelity level do you want for this clone?
> **A) Pixel-perfect** — exact match on colors, spacing, fonts, and motion
> **B) High-fidelity** — visually very close, minor deviations acceptable
> **C) Structural clone** — same layout and components, custom styling allowed

---

### 2a. Multi-source fetch (URL inputs only)

**Step 1 — Fetch homepage and extract CSS**
Use `WebFetch` on the target URL. Extract:
- All `--custom-property` color values and explicit hex/rgb/hsl/oklch values
- `@import` and `<link>` font declarations
- `letter-spacing`, `line-height`, `font-weight`, `font-size` values
- `padding`, `margin`, `gap` patterns (identify the grid unit)
- `border-radius`, `box-shadow`, `transition`, `animation` declarations
- All `<link rel="stylesheet">` URLs
- `max-width` on containers and content wrappers
- `grid-template-columns`, `grid-template-rows`, `display: grid/flex` patterns
- `@media` breakpoint values (min-width / max-width thresholds)
- Header/nav height, `position: sticky/fixed`, footer column structure
- Section-level `padding-block` / `padding-top` / `padding-bottom` values

After Step 1, evaluate JS-render signal: count distinct color values extracted. Also check for SPA markers:
- `<div id="root">` or `<div id="app">` with no meaningful children
- `<noscript>` block with substantial content
- Fewer than 300 words of visible text
- `bundle.js` / `main.[hash].js` as the only `<script>` src

If ≥ 2 SPA markers are present OR < 5 distinct color values → page is **JS-rendered**. Skip Steps 2–3, go directly to **Step 4 — Fetch strategy escalation**.

**Step 2 — Fetch CSS files directly** (skip if JS-rendered)
For each `<link rel="stylesheet">` found: `WebFetch` the CSS file.
CSS files contain the actual `:root {}` token blocks that HTML snapshots miss.

**Step 3 — Multi-page sampling** (skip if JS-rendered; otherwise: B/C: 1 extra page; A: 2–3 extra pages)
Prioritize: `/pricing`, `/features`, `/docs`, `/about`

**Step 4 — Fetch strategy escalation**

This step runs when the page is JS-rendered (detected above) OR when Steps 1–3 yield < 5 distinct color values.

Run the following levels in order. Stop at the first level that succeeds (returns ≥ 5 distinct color values or a valid screenshot file).

**Level 1 — Firecrawl headless scrape**

Try extracting the fully-rendered DOM via the `firecrawl` CLI:
```bash
firecrawl scrape "[REF]" --formats html,markdown --wait 3000 2>/dev/null
```
- If exit code 0 and output contains ≥ 5 color values → use this HTML/markdown as the source for Step 2 (CSS extraction) and Step 3 (multi-page sampling), then continue to Step 5.
- If exit code non-zero or output < 5 color values → escalate to Level 2.

**Level 2 — Screenshot visual clone**

Capture a full-page screenshot using the headless browse daemon:
```bash
gstack screenshot "[REF]" --full-page --output /tmp/ref-screenshot.png 2>/dev/null \
  || browse screenshot "[REF]" --output /tmp/ref-screenshot.png 2>/dev/null
```
- If a screenshot file is written to `/tmp/ref-screenshot.png` → set `REF_SCREENSHOT = /tmp/ref-screenshot.png`. Switch to **visual analysis mode**: treat the screenshot as a local image reference. In 2b, use "For screenshots" path (dominant/accent colors, font style, spacing density, component style, interaction model, personality). Continue to Step 5.
- If screenshot also fails → escalate to Level 3.

**Level 3 — WebSearch design system research** (last resort)
Run in parallel:
- WebSearch: `"[brand]" design system`
- WebSearch: `"[brand]" color palette hex`
- WebSearch: `"[brand]" typography font`
- WebSearch: `site:figma.com "[brand]"`

Mark each value's confidence: `✓ source CSS` | `~ inferred` | `? estimated`

**Announce the fetch strategy used** before proceeding to 2b:
```
Fetch strategy: [WebFetch / Firecrawl / Screenshot / WebSearch]
Reason: [e.g. "JS-rendered SPA — WebFetch returned 3 colors; Firecrawl succeeded"]
```

**Step 5 — Interaction & behavior sweep**
Identify:
- **Scroll-driven vs. click-driven** per section
- Scroll library signals: `.lenis`, `data-locomotive`, `[data-scroll]`
- Animation library: Framer Motion, GSAP, AOS, CSS-only
- Navbar on scroll, hero animation type, parallax sections, sticky elements

**Step 6 — Asset inventory**
Enumerate images, SVG usage, video, icon library, layered compositions.

**Step 7 — Design documentation search**
WebSearch: `"[brand]" design system`, `"[brand]" brand guidelines`, `site:figma.com "[brand]"`

**For screenshots:** Read visually — dominant/accent colors, font style, spacing density, component style, interaction model, overall personality.

---

### 2b. Deep design analysis

**COLORS — full token system**
1. Page background — pure vs. off-white/off-black? warm or cool tint?
2. Surface/card background — elevation levels?
3. Text hierarchy — primary / secondary / tertiary hex values
4. Border colors — transparent rgba or opaque hex?
5. Brand accent — the ONE signature color. How sparingly?
6. Semantic colors — success/warning/error/info

**Color temperature:** warm-tinted (yellow/orange in neutrals), cool-tinted (blue/purple), or neutral.

**Brand DNA signatures — recognize and match:**

→ Load `knowledge/references/brand-references.md`. Match the analyzed site's background color, accent color, and typeface to an entry in the Brand DNA Signatures table. Record the palette ID for use in Phase 3.

**TYPOGRAPHY — complete type system**
- Heading letter-spacing: premium range −0.01em to −0.05em (tight is professional)
- Body line-height: document = 1.7–1.8, UI = 1.5–1.6, compact = 1.3–1.4
- **Fixed vs. fluid scale rule:**
  - App UI / dashboard → fixed px scale (12/13/14/16/18/20/24/30px) — predictability
  - Marketing / landing page → fluid `clamp()` — scales with viewport, dramatic display type
  - Never mix: no fluid type on data tables, no fixed type on full-page heroes

**SPACING — grid system**
Base unit: 4px or 8px (GCF of observed values). Common 8px scale: 4/8/12/16/20/24/32/40/48/64/80/96/128px.

**LAYOUT — full structural analysis**
Extract the complete layout skeleton from the reference site:

1. **Grid system** — container max-width, column count per breakpoint, gap values, nesting depth
2. **Breakpoints** — identify the exact pixel values where layout shifts occur (stack→2-col→3-col, nav collapse, etc.). Record observed breakpoints, not assumed ones.
3. **Section layout patterns** — for each major section, record:
   - Layout type: centered stack / split (left-right) / bento grid / card grid / full-bleed / alternating rows
   - Column ratio: 50/50, 40/60, 33/67, or asymmetric
   - Alignment: left-aligned body vs. centered body vs. mixed
   - Direction: does the layout alternate (text-left/image-right → image-left/text-right)?
4. **Header skeleton** — layout type (flex row), logo position (left/center), nav position (center/right), CTA cluster position, height, sticky behavior
5. **Footer skeleton** — column count, column ratio (e.g. 2fr 1fr 1fr 1fr), bottom bar layout
6. **Vertical spacing chain** — the distance between elements within a section: label → title (gap), title → description (gap), description → content/cards (gap)
7. **Section-to-section rhythm** — actual px values between sections (e.g. Hero→Features: 120px, Features→Steps: 96px)

→ Also see `knowledge/references/brand-references.md` Layout Signatures section for per-brand max-width, section rhythm, and signature patterns.

**COMPONENTS — UI element signatures**
For each major interactive element, record:
- Button: fill style (solid/ghost/outline), radius, height, font-weight, hover effect
- Card: border vs. shadow, background, hover state, padding, internal spacing
- Input: border style, radius, focus ring, label placement
- Nav: layout, item style, active indicator, mobile collapse pattern
- Badge/tag: shape (pill/rounded-rect), sizing, color treatment (tinted bg vs. outline)
- Link: decoration (underline/none), color, hover behavior
- Any distinctive patterns unique to the site (e.g. custom toggles, command palette, accordions)

**ICONOGRAPHY**
- Style: outline / filled / duotone / mixed
- Default size and size scale
- Library identification: inspect SVG class names, `data-*` attributes, or known path patterns (Lucide, Heroicons, Phosphor, Feather, custom)
- Stroke width consistency
- Usage density: icons everywhere vs. minimal decorative use

**IMAGERY**
- Photography: present or absent? If present: product screenshots, lifestyle, abstract, stock?
- Treatment: border-radius, overlays, filters (grayscale, blur, color tint)
- Aspect ratios used for hero images, feature images, thumbnails
- Illustration style: none / line art / 3D / isometric
- Video usage: none / hero bg / inline product demos

**COPY PATTERNS**
- Headline construction: statement ("Ship faster") / question ("Ready to scale?") / imperative ("Build something great") / fragment ("The future of X")
- CTA copy style: action-first ("Start building") vs. benefit-first ("Get 10x faster")
- Label casing: ALL CAPS micro-labels, Sentence case, Title Case
- Overall tone: technical precision / conversational warmth / aspirational / brutally minimal

**SURFACES** — shadow scale xs→xl, border-radius scale, border style (rgba vs. solid), glass/blur effects.

**MOTION — brand signatures:** → See `knowledge/references/brand-references.md` Motion Signatures section for per-brand duration, easing, and hover behavior.

---

### 2c. Design DNA Report

Output the following report. It becomes the source of truth for Phase 3/4.

```
═══════════════════════════════════════════════════════════
DESIGN DNA: [Site/Brand Name]
═══════════════════════════════════════════════════════════
PERSONALITY   [2-3 adjectives]
AUDIENCE      [target user type]
COLOR TEMP    [warm / cool / neutral]
DENSITY       [compact / comfortable / spacious]

── COLORS ──────────────────────────────────────────────
  Page bg:          [hex]  [description]
  Surface bg:       [hex]
  Surface raised:   [hex]
  Text primary:     [hex]
  Text secondary:   [hex]
  Text tertiary:    [hex]
  Border default:   [value]
  Border strong:    [value]
  Accent primary:   [hex]  [where used, frequency]
  Accent hover:     [hex]
  Success/Warning/Error: [hex each]
  Dark mode:        [yes/no — if yes, note mapping: which tokens invert, which stay fixed]

── TYPOGRAPHY ───────────────────────────────────────────
  Heading font:     [name]  [classification]  [weights]
  Body font:        [name]  [weights]
  Mono font:        [name or "none"]
  Import:           [Google Fonts URL or "licensed/system"]
  Type scale (px):  [12/13/14/16/18/20/24/30/36/48/60]
  Heading tracking: [e.g. -0.03em]
  Body line-height: [e.g. 1.6]

── SPACING ──────────────────────────────────────────────
  Base unit:        [4px / 8px]
  Content max-w:    [e.g. 1280px]
  Section padding:  [vertical rhythm]

── LAYOUT ───────────────────────────────────────────────
  Grid system:      [e.g. "12-col implicit, max-w 1320px, gap 24px"]
  Breakpoints:      [e.g. sm:640px / md:768px / lg:1024px / xl:1280px]
  Header:           [e.g. "flex row, logo-left, nav-center, CTAs-right, h-76px, sticky on scroll"]
  Footer:           [e.g. "4-col grid (2fr 1fr 1fr 1fr), bottom bar flex between"]

  Section layouts (in page order):
    Hero:           [e.g. "centered stack, max-w 1120px, text-center"]
    Features:       [e.g. "alternating split rows 50/50, image flips side each row"]
    Steps:          [e.g. "4-col card grid, equal width"]
    Testimonials:   [e.g. "3-col card grid"]
    FAQ:            [e.g. "centered single-col, max-w 680px, accordion"]
    CTA:            [e.g. "centered stack, max-w 520px"]

  Vertical chain:   [e.g. "label→title: 16px, title→desc: 16px, desc→content: 48px"]
  Section rhythm:   [e.g. "Hero→Features: 120px, Features→Steps: 96px, Steps→CTA: 120px"]
  Alignment rule:   [e.g. "hero centered, all body sections left-aligned"]

── SURFACES ─────────────────────────────────────────────
  Radius scale:     [sm/md/lg/xl/pill values]
  Shadow scale:     [xs → xl values]
  Depth effects:    [glass blur / noise grain / flat]

── MOTION ───────────────────────────────────────────────
  Philosophy:       [e.g. "micro-interactions only"]
  Duration scale:   [e.g. 150/200/300ms]
  Easing:           [cubic-bezier value]
  Hover pattern:    [e.g. "opacity + translateY(-1px)"]

── COMPONENTS ───────────────────────────────────────────
  Button primary:   [e.g. "solid white, radius-lg, 600 weight, h-10/h-12, no shadow"]
  Button secondary: [e.g. "ghost with border, same radius, white text"]
  Input:            [e.g. "full border, radius-sm, focus ring with accent"]
  Card:             [e.g. "border not shadow, flat dark bg, subtle hover border lighten"]
  Nav:              [e.g. "full-width top bar, minimal links, logo left / CTAs right"]
  Badge/tag:        [e.g. "pill shape, soft tinted background, 11px semibold"]
  Link:             [e.g. "underline on hover, accent color, no visited style"]
  [add more if site uses distinctive patterns: toggles, tabs, modals, tooltips, etc.]

── ICONOGRAPHY ──────────────────────────────────────────
  Style:            [outline / filled / duotone / mixed]
  Size system:      [e.g. 16×16 default, 20×20 nav, 24×24 feature]
  Library:          [Lucide / Heroicons / Phosphor / custom SVG / none]
  Stroke width:     [e.g. 1.5px / 2px]
  Usage density:    [minimal (nav+footer only) / moderate / icon-heavy]

── IMAGERY ──────────────────────────────────────────────
  Photography:      [none / product screenshots / lifestyle / abstract / AI-generated]
  Image treatment:  [e.g. "radius-xl, no overlay" or "grayscale + color on hover"]
  Aspect ratios:    [e.g. "16:10 for features, 1:1 for avatars"]
  Illustration:     [none / line art / 3D / isometric / hand-drawn]
  Video:            [none / hero background / inline demo]

── COPY PATTERNS ────────────────────────────────────────
  Headline style:   [statement / question / imperative / fragment]
  CTA language:     [e.g. "Start free trial" / "Get started" — action-first or benefit-first]
  Label casing:     [uppercase micro-labels / sentence case / title case]
  Tone:             [technical / conversational / aspirational / minimal]

── BEHAVIORS ────────────────────────────────────────────
  Interaction model:   [scroll-driven / click-driven / hybrid]
  Scroll library:      [Lenis / Locomotive / native / none]
  Animation library:   [Framer Motion / GSAP / AOS / CSS-only]
  Navbar on scroll:    [static / shrinks / bg appears / hides]
  Hero animation:      [entrance-only / looping / scroll-driven]

── CONFIDENCE ───────────────────────────────────────────
  High confidence:  [values from source CSS]
  Estimated:        [values inferred — flag for verification]

── WHAT THIS STYLE NEVER DOES ───────────────────────────
  [Anti-patterns unique to this design identity]
═══════════════════════════════════════════════════════════
```

**Translate DNA → Generation Context** (automatic, no user input):
```
ARCHETYPE MATCH   [closest A–J]
CREATIVE PARAMS   DESIGN_VARIANCE=[X] MOTION=[X] DENSITY=[X]
FIDELITY          [pixel-perfect / high-fidelity / structural]
UNFORGETTABLE HOOK  [what makes this site unmistakable]
INTERACTION MODEL   [scroll-driven / click-driven / hybrid]
NEVER DO            [2–3 hardest constraints]
```

**Phase 3 fast path (Mode B — URL/screenshot only):** After the DNA report, the archetype and palette are already known from extraction — do not re-run Phase 3 Steps 1–4. Instead:
1. Load `knowledge/design/visual-archetypes.md` (needed for archetype parameter mapping).
2. Load `knowledge/references/reference-sites.md` and find the closest matching reference case for the detected scene + archetype.
3. Use that reference's structural template for generation — replace only names, copy, and user-specific details.
4. Show a single confirmation Design Brief ("Generate / Adjust?") with "Structural template: [reference name/URL]".
5. On confirmation, proceed to Phase 4.


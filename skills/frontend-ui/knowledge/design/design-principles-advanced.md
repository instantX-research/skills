# Design Principles — Advanced Visual Design

**When to load:** At Phase 3 Design Brief Synthesis when DESIGN_VARIANCE ≥ 6 OR archetype is H (Cinematic Portfolio), C (Chromatic Confidence), or G (Museum Authority). Supplements `design-principles.md` (always-loaded core).

---

## Hero section composition — what premium actually looks like

The hero is the first impression and the only section every user sees. Anti-patterns tell you what not to do (centered h1 + gradient). This section gives you the positive patterns.

### The 6 premium hero archetypes

**1. Type-dominant hero** (Linear, Raycast, Vercel)
Type IS the design. No decorative imagery. Pure typographic power.
```
Layout:  Left-aligned oversized headline (64–96px, 800 weight, -0.04em tracking)
         + 1–2 lines subtext (17–18px, 400 weight, secondary color)
         + CTA below with generous margin above it
         + Optional: faint background grid / noise texture
```
```css
.hero-headline {
  font-size: clamp(52px, 7vw, 96px);
  font-weight: 800;
  letter-spacing: -0.04em;
  line-height: 1.0;
  max-width: 14ch;    /* force 2–3 intentional line breaks */
}
```
Signal: technical excellence, confidence, no need to impress with decoration

**2. Full-bleed product screenshot hero** (Stripe, Loom, Notion)
The product IS the hero. Type is secondary; the UI speaks.
```
Layout:  Modest headline (32–48px) + short value prop
         + Large, high-fidelity product screenshot/video below or behind
         + Screenshot has subtle shadow + rounded corners + slight perspective tilt (optional)
         + Background: neutral — let the product color do the work
```
```css
.hero-product-shot {
  border-radius: 12px;
  box-shadow: 0 32px 80px rgba(0,0,0,0.15), 0 4px 16px rgba(0,0,0,0.08);
  transform: perspective(1200px) rotateX(2deg);  /* very subtle — 2–4deg max */
  width: 100%;
  max-width: 960px;
}
```
Signal: product confidence, "this is what you'll use"

**3. Split-screen tension hero** (Framer, Arc, Figma)
Two halves in productive conflict. Type left, visual right — or vice versa.
```
Layout:  55/45 or 60/40 split (not 50/50)
         Left: headline stack + CTA
         Right: illustration, video, 3D object, or animated component
         Vertical center alignment between the two halves
```
Signal: brand sophistication, something to discover on both sides

**4. Editorial / magazine hero** (Anthropic, Craft, Readwise)
Warm, human, considered. The antithesis of the startup gradient.
```
Layout:  Serif display font at 56–72px, 2–3 lines, left-aligned
         + Large margin above (120–160px from nav) — let it breathe
         + Body prose at 18–20px below (editorial sizing)
         + Optional: a single high-quality photograph, not illustration
         + Warm background (off-white, parchment) — never pure white
```
Signal: trust, craft, this was made by humans who care

**5. Number/stat-driven hero** (Intercom, Segment, growth-focused SaaS)
One astonishing number, made enormous. Claims legitimacy through data.
```
Layout:  Huge KPI at 96–120px (tabular-nums, 700 weight)
         + Small label above: 11px uppercase, +0.08em tracking, secondary color
         + Context sentence below at 17px
         + Secondary stats at 40–48px to the right or below
```
Signal: proven results, data-forward brand

**6. Ambient motion hero** (Framer, motion.dev, creative agencies)
The background lives. Type sits still above a moving environment.
```
Layout:  Clean, minimal text centered in the viewport
         + Animated background: particles, gradient mesh, CSS noise, WebGL
         + Reduced motion: static gradient fallback
         + Text has a subtle backdrop-blur or semi-transparent surface behind it
```
Signal: cutting-edge, experiential, premium craft

### What ALL good heroes share

- **One primary CTA.** A hero with two equal CTAs has zero CTAs.
- **A stated benefit, not a category.** "Design faster" not "A design tool"
- **Contrast between headline and subtext.** Not just size — weight, color, spacing all shift
- **Space above the fold.** At least 80–120px from nav to first text element — let the hero breathe
- **Mobile-first composition.** The type-dominant and editorial heroes work on mobile. Full-bleed screenshots need a separate mobile crop.

---

## Visual rhythm — pacing the page like a director

A page without rhythm is a page of equal-volume sections. The eye has nowhere to rest, nothing to anticipate. Great page design is a choreographed experience: tension, release, tension, release.

### The tension-release pattern

Every page should alternate between high-density, high-information sections and open, breathing sections.

```
Hero:          OPEN        — lots of whitespace, single focal point, low density
Features:      TENSE       — information-dense, multiple elements, closer spacing
Testimonial:   OPEN        — single quote, large type, whitespace surrounds it
Pricing:       TENSE       — comparative columns, feature lists, data
CTA section:   OPEN        — single headline + single button, vast negative space
Footer:        TENSE       — dense links, organized, utilitarian
```

The contrast between dense and sparse sections makes each feel more extreme. A cramped features section makes the following testimonial feel like a breath of fresh air.

### Section differentiation without background colors

The AI-slop pattern is: every section gets a different pastel background. The professional alternative is differentiating sections through structure, not paint.

**5 ways to separate sections without changing background color:**

1. **Grid structure change** — Section A uses 3 columns, Section B uses 1 wide column + sidebar. Same background, totally different feel.

2. **Type scale shift** — Section A uses 14px dense text, Section B leads with 56px headline. The scale change signals a new section.

3. **Content density change** — Section A has 8 items; Section B has 1 isolated element. The whitespace *is* the separation.

4. **Alignment change** — Section A is left-aligned; Section B centers its content. The axis shift reads as a new rhythm.

5. **Image/media introduction** — A section that suddenly introduces a full-width image after text-only sections creates a visual breath.

### Reading speed and cognitive pacing

Different sections should be designed to be consumed at different speeds:

| Section type | Reading speed | Design approach |
|-------------|--------------|-----------------|
| Hero | Fast scan (2–3 seconds) | Large type, minimal text, single message |
| Value proposition | Slow scan (10–15 seconds) | 3–4 items, visual support, digestible chunks |
| Social proof | Skimmed | Logos or faces first, text secondary |
| Feature details | Read (30–60 seconds) | Body text size, good line-length, prose rhythm |
| Pricing | Studied (60–120 seconds) | Data table discipline, comparison-friendly |
| Footer | Reference | Dense, small, organized — not meant to be read, meant to be found |

Design each section to be consumed in its intended way. A hero designed for "reading" fails. A pricing section designed for "fast scan" fails.

### The single wow moment

Every page should have exactly one section that makes the user stop scrolling.

This is the **UNFORGETTABLE HOOK** from Phase 1 — expressed as a composition principle:

- It is usually not the hero (heroes are expected to be polished)
- It is unexpected: an interaction, a statistic, a visual treatment, a piece of copy
- It is singular: if three sections are equally impressive, none stands out
- The sections before it should build anticipation; the sections after it land the conversion

Design the page with this moment in mind from the start. Every other section is supporting cast.

---

## Unforgettable Moment Reference Library

**When to use:** Load during Phase 4 Design Taste Gate. The HOOK must be concrete and archetype-appropriate. Generic statements ("clean layout", "nice animation") are not acceptable. Use this library to calibrate what counts as unforgettable for each archetype.

A strong hook has three qualities: (1) you can describe it in one sentence, (2) it requires a specific implementation decision, (3) it would be absent from a generic AI output of the same prompt.

### A — Obsidian Precision
- A single metric or number rendered at `clamp(4rem, 10vw, 9rem)` with tabular figures, anchoring the entire hero — the number IS the design
- A hairline `1px` horizontal rule that animates from `width: 0` to full width on scroll, acting as a section divider and progress indicator simultaneously
- An interactive command palette (`⌘K`) overlay that surfaces the site's key actions — the product demonstrates itself

### B — Warm Editorial
- A pull quote set at `clamp(2rem, 5vw, 4.5rem)` in a transitional serif, breaking the column grid and bleeding into the margin
- The hero copy rendered with visible ink-pressure variation via `font-variation-settings` — the type feels handmade
- A subtle background texture (noise grain `opacity: 0.03`) that makes the cream surface feel like paper

### C — Chromatic Confidence
- A gradient headline where each word is a different hue stop, rendered at `clamp(3rem, 8vw, 7rem)` — colour is the typography
- A scroll-triggered counter that animates a key stat from `0` to its final value with spring easing as the section enters viewport
- A grid of cards where on hover, the entire page background transitions to match the hovered card's accent colour — the whole canvas responds

### D — Terminal Glass
- A live-typed code snippet in the hero that cycles through 3 example commands with a blinking cursor — the product demos in real time
- A glass panel (`backdrop-filter: blur(20px) saturate(180%)`) that floats above a dark mesh gradient background, creating depth without shadows
- A terminal-style loading sequence where UI elements appear line-by-line as if being rendered by a process

### E — Luxury Silence
- A full-viewport product image with zero text — the only copy fades in on scroll, never competing with the photograph
- A section where the background colour morphs from `#f5f5f7` to `#1d1d1f` as you scroll through it, transitioning between two product colourways
- An `aspect-ratio: 16/9` video hero that plays silently at full bleed — no controls visible, no overlay text

### F — Soft Structuralism
- A bento grid where one card has a perpetually looping ambient animation (floating particles, gentle pulse) while all others are static — the contrast makes it magnetic
- Cards with `border-radius: 2rem` that on hover reveal a soft `box-shadow` bloom — the surface breathes
- A real-time status indicator (green pulse dot) embedded in the hero that makes the product feel live

### G — Museum / Cultural Authority
- An exhibition card grid where the image fills the entire card and the title fades in on hover — the artwork speaks first
- A `1px` rule that separates every row, with the row background transitioning to the institution's accent colour on hover — restraint that still rewards
- A full-bleed historical photograph as hero with a `mix-blend-mode: multiply` colour wash — archival and contemporary simultaneously

### H — Cinematic Portfolio
- A project grid where entering any card triggers a full-palette swap for the entire page — the portfolio IS the colour system
- A draggable carousel (grab/grabbing cursor) where projects slide at variable momentum — physics-first interaction
- A custom cursor that morphs from an arrow to a project-specific icon on hover — the cursor tells the story before the copy does

### I — Developer Personal
- A `::selection` highlight in the site's accent colour with `color: white` — a small truth about the person
- The latest blog post rendered in the hero with its actual prose — the writing is the product, not a description of it
- A minimal command bar that filters projects by tag with `0` delay — keyboard-first as a design statement

---

## Illustration & Visual Media Strategy

The choice between photography, illustration, abstract graphics, and 3D shapes is a tone decision, not an aesthetic one. Each medium carries different emotional connotations.

### Medium × archetype mapping

| Archetype | Photography | Illustration | Abstract / Geometric | 3D |
|---|---|---|---|---|
| **A Obsidian Precision** | No (too warm) | No | ✓ Dot grid, noise grain, subtle lines | No |
| **B Warm Editorial** | ✓ Candid, film-grain | ✓ Hand-drawn, line art | No | No |
| **C Chromatic Confidence** | ✓ Bold, high-contrast | ✓ Geometric, flat | ✓ Gradient mesh, abstract shapes | ✓ Sparingly |
| **D Terminal Glass** | No | No | ✓ Grid patterns, particle fields | No |
| **E Luxury Silence** | ✓ Primary medium — full-bleed, art-directed | No | No | No |
| **F Soft Structuralism** | ✓ Light, airy, product-focused | ✓ Soft, rounded shapes | ✓ Pastel blobs, gentle gradients | No |
| **G Museum Authority** | ✓ Archival, artwork reproduction | No | No | No |
| **H Cinematic Portfolio** | ✓ Project-specific, curated | No | ✓ Per-project | ✓ Per-project |
| **I Developer Personal** | ✓ Single candid author photo | No | No | No |

### Photography selection principles

**What makes a hero image work:**
- **Color temperature matches palette** — a warm cream page (`L1 Parchment`) needs warm-toned photography; cool precision pages need neutral or cool images
- **Subject has room to breathe** — avoid busy backgrounds that compete with headline text
- **Not stock-obvious** — no handshakes, no people pointing at whiteboards, no generic "diverse team in office". Source from Unsplash editorial, brand shoots, or illustrative photography.
- **Light source is consistent** — all images on a page should share the same approximate light direction and temperature
- **Art direction for text overlay** — if text sits over an image, the image needs a dark or light region where the text lands (ensure 4.5:1 contrast)

**Image format decisions:**
- Hero / full-bleed: always WebP or AVIF, `loading="eager"`, explicit width/height
- Below-fold: WebP/AVIF + `loading="lazy"`
- Dark mode: `filter: brightness(0.85) contrast(1.05)` so images don't feel harsh in dark contexts

### Illustration styles by use case

**Line illustration** (Warm Editorial, B archetype)
- Single weight, hand-drawn quality
- Warm or muted colors only — never vivid saturated palette
- Best for: onboarding flows, empty states, blog post headers
- Avoid: combining with photography on the same page

**Geometric / flat illustration** (Chromatic Confidence, Soft Structuralism)
- Bold shapes, flat colors, minimal detail
- Colors derived directly from the palette (no independent illustration color system)
- Best for: feature sections, marketing heroes, explainer diagrams
- Avoid: mixing styles (flat + line + 3D on the same page signals no art direction)

**Isometric / 3D illustration** (Chromatic Confidence only, sparingly)
- High production quality required — cheap isometric looks dated immediately
- One hero illustration maximum per page (not scattered across every section)
- Light source must be consistent across all isometric elements on a page

**No illustration** — when to choose text and structure over visuals
Archetypes A, D, and I are stronger without illustration. Visual structure (grid, type scale, whitespace) is the art direction. Adding illustration to these archetypes weakens the brand signal.

### Abstract background techniques

**Dot grid**
```css
.dot-grid {
  background-image: radial-gradient(circle, rgba(0,0,0,0.12) 1px, transparent 1px);
  background-size: 24px 24px;
}
/* Dark mode */
.dot-grid { background-image: radial-gradient(circle, rgba(255,255,255,0.08) 1px, transparent 1px); }
```
Use: Archetype A, D — signals technical precision without decoration.

**Noise grain overlay** (adds material texture to flat surfaces)
```css
.grain::after {
  content: '';
  position: fixed; inset: 0; pointer-events: none; z-index: 999;
  background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='noise'><feTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3'/><feColorMatrix type='saturate' values='0'/></filter><rect width='200' height='200' filter='url(%23noise)'/></svg>");
  opacity: 0.035;
  mix-blend-mode: overlay;
}
```
Use: Adds premium, tactile quality to any archetype. Essential for F3 Earth Craft palette.

**Mesh gradient** (atmospheric hero backgrounds)
```css
.mesh-bg {
  background:
    radial-gradient(ellipse at 20% 50%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 20%, rgba(255, 119, 115, 0.2) 0%, transparent 50%),
    radial-gradient(ellipse at 60% 80%, rgba(120, 198, 160, 0.15) 0%, transparent 50%),
    var(--color-bg);
}
```
Use: Archetype C hero sections, Archetype F cards. Colors must be from the active palette.
Rule: Max 3 gradient layers. More creates muddy, AI-wallpaper look.

**Line / rule patterns** (structured, editorial)
```css
.line-bg {
  background-image: repeating-linear-gradient(
    0deg, transparent, transparent 47px,
    rgba(0,0,0,0.04) 47px, rgba(0,0,0,0.04) 48px
  );
}
```
Use: Archetype G (museum), Archetype I (developer personal) — evokes notebook paper, editorial grids.

### When to use no visual at all

For archetypes A, D, and I: the absence of decoration IS the design statement. Adding background patterns, illustrations, or photography to these archetypes dilutes the brand signal. The design should work at full quality with typography and whitespace alone.

Test: Remove all images and illustrations. If the page collapses, the layout is too dependent on visuals — strengthen the typographic structure first.

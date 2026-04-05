# Design Principles

**Scope:** Theory and science — why good design works. For concrete prescriptions derived from this theory, see `design-taste.md`. For code implementation patterns, see `implementation/code-standards-core.md` and `implementation/code-standards-extended.md`.

---

## Visual composition — the principles that create beauty, not just order

This section is about making things *beautiful*, not just correct. Rules prevent ugliness; composition creates attraction.

### Visual weight and balance

Every element has visual weight — determined by size, color saturation, contrast, and complexity. Beautiful layouts balance this weight without being symmetrical.

**Weight factors (ranked):**
1. Size — larger = heavier
2. Color saturation — vivid color = heavier than muted
3. Contrast — high contrast against background = heavier
4. Density — more detail/complexity = heavier
5. Position — lower on page = heavier (gravity metaphor)

**Asymmetric balance (more interesting than symmetry):**
- A large, light element on the left balanced by a small, bold element on the right
- Heavy image occupying 60% of a row, balanced by tight, weighted typography in 40%
- Off-center headline balanced by wide margin on one side

The test: cover half the design. Does each half feel roughly equal in visual mass? If yes, it's balanced. Mathematical symmetry is not required — visual equivalence is.

### Column ratios — unequal is almost always better

| Ratio | Feel | Use for |
|-------|------|---------|
| 1:1 (50/50) | Stable, equal, boring | Only when content is genuinely equal in importance |
| 5:7 (42/58) | Subtle tension, preferred | Default split for most 2-column layouts |
| 1:2 (33/67) | Clear hierarchy, dynamic | Feature explanation with dominant visual |
| 1:3 (25/75) | Strong dominance | Sidebar + main content |
| 3:7 (30/70) | Editorial tension | Pull quote beside body text |
| 2:3:1 | Three-column with hierarchy | Feature grids with one dominant card |

**Never default to equal columns.** Even a 48/52 split looks more intentional than 50/50.

### The golden ratio in layout (φ = 1.618)

Not a formula to follow rigidly — a proportion to recognize in beautiful things and reproduce intentionally.

**Applications:**
- Card aspect ratios: `1:1.618` (wide) or `1.618:1` (tall)
- Column splits: content column ~62% of container, sidebar ~38%
- Vertical rhythm: if section heading is 32px, body text at ~20px follows the ratio
- Whitespace: if element is 200px tall, breathing room above/below at ~124px feels natural
- Image dimensions: 800×495px (≈ 1.618:1) for hero images

### Visual tension — why the best designs feel alive

Tension is the productive conflict between opposites. Without tension, design is inert.

**The five tensions:**
1. **Large vs. small** — a 72px headline next to 12px metadata creates scale drama
2. **Heavy vs. light** — bold 800-weight type beside 300-weight text (don't use 300 in UI — use color lightness instead)
3. **Dense vs. sparse** — a packed feature list next to a single floating CTA
4. **Dark vs. light** — even in an all-light-mode design, an ink-dark section heading creates contrast
5. **Structured vs. free** — a grid-aligned block next to a deliberately overflowing element

Without any tension, every section reads at the same visual volume. The eye has nowhere to land.

### Intentional rule-breaking — when to escape the grid

A perfect grid is a starting point, not a destination. The most memorable designs violate one grid rule, intentionally.

**Legitimate breaks:**
- A headline that overflows its column into the margin by 10–20%
- An image that bleeds to the edge of the viewport while everything else respects the container
- A pull quote rotated 2–3° (not more — feels random)
- A single element that ignores the baseline grid to create visual surprise
- One section where the column structure inverts vs. every other section

**The rule:** Break one grid constraint. Not two. One deliberate violation reads as intention; two reads as mistake.

---

## Information hierarchy — before writing a single line of code

- What is the #1 thing a user on this page should do or understand?
- Z-pattern (marketing pages, scanning) vs. F-pattern (content pages, reading)?
- What is the "peak moment" (the wow interaction) and the "end" (the completion state)?
  Both need intentional design (Peak-End Rule — Nielsen Norman Group)
- Apply Von Restorff Effect: the primary CTA must be visually distinct from everything else.
  Only ONE thing should be the accent color. Two accent colors = zero accent colors.

## Gestalt principles baked into layout

- **Proximity**: related elements tighter (8px label-to-input) vs. unrelated elements spacious (32px before next group)
- **Similarity**: all buttons of the same type look identical; all cards in a list are structurally identical
- **Closure**: half-visible cards at scroll boundaries signal "there's more" (Reels, Swiper carousels)
- **Continuity**: alignment grid — all elements share baseline or left edge; misalignment is noise
- **Figure/Ground**: modal backdrops, z-index stacking, active vs. inactive nav items

## Fitts's Law in interactive elements

- Touch targets minimum 44×44px (Apple HIG) / 48×48dp (Material)
- Primary CTAs are large (height ≥ 40px), centrally placed in natural pointer flow
- Destructive actions (Delete, Remove) are smaller, secondary, and require confirmation

## Hick's Law in navigation

- Maximum 5–7 nav items at top level
- Group related items; use progressive disclosure for advanced options
- Dropdowns only for true category hierarchies, not for 2–3 items

---

## Typography — the discipline that separates professional from generic

**The 6 critical rules (from Refactoring UI + real benchmark analysis):**

1. **Never use default letter-spacing for headings.**
   Headings need negative tracking: `-0.01em` (subtle) to `-0.05em` (Framer/Arc level bold).
   Small caps and uppercase labels need positive tracking: `+0.04em` to `+0.08em`.
   Body text: `0` or `-0.01em`. Caption text: `0`.

2. **Line-height is context-specific:**
   - Display headings (48px+): `1.05`–`1.1`
   - Section headings (24–36px): `1.2`–`1.3`
   - Body text (15–18px): `1.5`–`1.7`
   - Compact UI labels (12–13px): `1.3`–`1.4`
   - Editorial long-form prose: `1.7`–`1.8`

3. **Font weight hierarchy (never all bold, never all regular):**
   - Hero headline: `700` (or `800` for display fonts)
   - Section heading: `600`–`700`
   - Subheading/label: `500`–`600`
   - Body: `400`
   - Supporting/caption: `400` (use color, not lighter weight — `300` is illegible on low-DPI screens)

4. **Type scale — use a ratio, not arbitrary sizes:**
   Major Third (×1.25) scale from 16px base:
   `10 / 12 / 13 / 14 / 16 / 18 / 20 / 24 / 30 / 36 / 48 / 60 / 72`
   OR
   Perfect Fourth (×1.333) from 16px base:
   `10 / 12 / 14 / 16 / 21 / 28 / 37 / 50 / 67`

5. **Pair fonts with purpose and contrast:**
   Effective pairing strategies:
   - Geometric sans heading + same humanist sans body (Geist + Inter, Circular + DM Sans)
   - Humanist sans heading + same at lower weight body (Inter 700 heading / Inter 400 body)
   - Serif display + neutral sans body (Domaine/Tiempos + Inter) ← premium editorial feel
   - Monospace accent + humanist body (Commit Mono labels + Inter body) ← developer feel

   Avoid: two serif fonts, two geometric sans fonts with similar proportions, >3 fonts total.

6. **Optical considerations:**
   - `font-size: 13–14px` for dense UI (sidebars, metadata, tables, form labels)
   - `font-size: 15–16px` minimum for body prose
   - `font-size: 17–18px` for editorial/marketing body text (Apple uses 17px)
   - Never go below `400` font-weight in production UI (300 is for print or high-DPI only)

---

## Font selection guide — which fonts to actually use

Pairing rules tell you the structure; this section tells you the specific fonts. Organised by archetype so the right choice is immediate.

### By archetype

| Archetype | Display / Heading | Body | Mono accent | Notes |
|-----------|------------------|------|-------------|-------|
| **A Obsidian Precision** | Geist, Inter (700–800) | Inter, Geist | Geist Mono, JetBrains Mono | Geist is free via Vercel; Inter is the safe default. Avoid Poppins (too playful). |
| **B Warm Editorial** | Fraunces, Instrument Serif, Libre Baskerville | Inter, DM Sans, Source Sans 3 | — | Premium: Tiempos Text, Canela. Avoid Merriweather (too academic), Georgia (too default). **Academic scene override (Scene F):** Fraunces is editorial/literary — its variable optical axes and expressive character conflict with the scholarly register. Use DM Sans throughout (weight hierarchy only), or Lora/Source Serif 4 for the name alone. |
| **C Chromatic Confidence** | Plus Jakarta Sans, Space Grotesk, Monument Extended | Inter, DM Sans | — | Use variable fonts for responsive scale. Premium: Söhne, Neue Haas Grotesk. Avoid Inter for headings (too neutral). |
| **D Terminal Glass** | Inter, Geist | Inter, Geist | JetBrains Mono, Geist Mono, Cascadia Code | Mono presence is the signature. Avoid Courier, Fira Code (too traditional). |
| **E Luxury Silence** | Cormorant Garamond, EB Garamond, Spectral | Inter, DM Sans | — | Premium: Canela, Austin, Cardinal. Serif carries the luxury signal; body stays neutral. |
| **F Soft Structuralism** | DM Sans, Plus Jakarta Sans, Nunito | Inter, DM Sans | — | Rounded terminals reinforce the soft-structured feel. Avoid serif display. |
| **G Museum Authority** | Libre Baskerville, EB Garamond, Playfair Display | Source Serif 4, Inter, Source Sans 3 | — | Premium: Austin, Freight Display. Institutional serif required for heading authority. |
| **H Cinematic Portfolio** | Space Grotesk, DM Sans, Fraunces (per project) | Inter | — | Per-project palette reset may include per-project typeface. Avoid Inter for hero text. |
| **I Developer Personal** | Source Serif 4, Lora | Inter, system-ui | JetBrains Mono, Fira Code | System font stack acceptable: `ui-serif, Georgia, serif`. The writing matters more than the font. |

### Google Fonts vs. licensed — decision guide

| Budget | Choice | Examples |
|--------|--------|---------|
| Free | Google Fonts: Inter, Geist, DM Sans, Plus Jakarta Sans, Source Serif 4, Fraunces, Instrument Serif, Cormorant Garamond, Space Grotesk, JetBrains Mono | Best default coverage for every archetype |
| Mid ($0–$50/yr) | Fontshare: Satoshi, Cabinet Grotesk, Clash Display, Switzer | Good quality, generous licensing |
| Premium ($100–$500/yr) | Klim: Söhne, Tiempos. Panos Vassiliou: Pangramic. Commercial Type: Canela, Graphik | Instantly elevates perceived quality; worth it for brand-defining work |

### CJK font strategy

When the product serves Chinese, Japanese, or Korean users, apply the following stack in addition to the Latin font:

**Simplified Chinese:**
```css
font-family: 'Inter', 'Source Han Sans SC', 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
/* For editorial/warm feel: replace Source Han Sans SC with Source Han Serif SC */
```

**Traditional Chinese:**
```css
font-family: 'Inter', 'Source Han Serif TC', 'Noto Serif TC', 'PingFang TC', sans-serif;
```

**Pairing rule for CJK:** The Latin and CJK weights are not equivalent — Source Han Sans SemiBold (W5) reads as Regular visually. Always test heading weight in both scripts and adjust independently.

**Free CJK options:** LXGW WenKai (warm, handwriting-adjacent), Source Han Sans/Serif (neutral authority), Noto Sans/Serif (maximum coverage).

---

## Typography as visual structure — type as the design, not in the design

Beyond following rules, great typography *is* the layout. The type arrangement creates the visual experience before anyone reads a word.

### Dramatic scale contrast

The most visually compelling compositions pair sizes that are far apart, not adjacent.

```
Powerful pairing:     72px display  +  14px caption  =  5:1 ratio  ← dramatic
Mediocre pairing:     36px heading  +  24px subhead  =  1.5:1 ratio ← bland
```

**Scale contrast patterns:**
- **Oversized label + small headline**: A 10px uppercase tracking label `PRODUCT DESIGN` above a modest 28px headline creates paradoxical premium feel
- **Enormous number + small descriptor**: `$48` at 80px + `per month` at 15px — the number becomes an image
- **Running text + oversized initial**: Dropcap-style first letter at 5× body size — editorial signature
- **Full-width breaking type**: Headline set large enough that it breaks across exactly 2 lines, filling the column width

### Type as layout skeleton

Weight and size contrast can replace background colors and borders entirely.

```
Instead of:   [colored section header background]
Use:          900-weight 11px ALL CAPS label + 48px heading — the contrast IS the section break

Instead of:   [card border to separate content]
Use:          500-weight 13px secondary text fading to tertiary — the color hierarchy IS the separator
```

### Oversized display type — when and how

When type is large enough to become graphical (≥ 80px), it follows image composition rules:

```css
/* Headline that deliberately overflows its container */
.hero-headline {
  font-size: clamp(64px, 10vw, 120px);
  font-weight: 800;
  letter-spacing: -0.04em;
  line-height: 0.95;           /* tighter than usual — it's a visual block, not text */
  overflow: visible;           /* allow intentional overflow */
}

/* Type as background texture — barely legible */
.type-texture {
  font-size: 20vw;
  font-weight: 900;
  opacity: 0.04;               /* becomes a watermark */
  position: absolute;
  pointer-events: none;
  user-select: none;
}
```

**Oversized type rules:**
- Line-height at `0.9–1.0` (not 1.2) — it's a shape, not paragraphs
- Letter-spacing at `-0.04em` to `-0.06em` — headline at this scale needs extreme tightening
- Never center-align oversized type unless it's a single word — left-aligned creates stronger vertical edge
- The word break is a design decision — rewrite copy to break in a visually satisfying place

### The weight-as-contrast hierarchy

Use weight changes to create visual rhythm without changing font size:

```
Section label:    10–11px  |  500–600 weight  |  wide tracking (+0.08em)  |  secondary color
Hero headline:    48–96px  |  700–900 weight  |  tight tracking (-0.04em) |  primary color
Body:             15–17px  |  400 weight      |  default tracking          |  primary color
Supporting:       13–14px  |  400 weight      |  default tracking          |  tertiary color
Data label:       11–12px  |  500 weight      |  wide tracking (+0.05em)  |  secondary color
```

The visual jump from 10px/500/+0.08em label to 72px/800/-0.04em headline is more dramatic and satisfying than any decorative element you could add.

---

## Whitespace as a design medium — emptiness is not absence

Whitespace is the most powerful tool in premium design. It is not the space left over after placing elements — it is a design element with its own presence.

### The three types of whitespace

**Macro whitespace** — the large breathing room between major sections, around heroes, at page edges
- Creates the "luxury" or "premium" feeling
- Apple's homepage: each product section is ~100vh; the product floats in the center of that space
- Rule: if you feel like the section has "too much empty space," resist the urge to fill it — that emptiness is doing work

**Micro whitespace** — the small spacing between related elements (labels, list items, nav links)
- Too little → elements merge and become unreadable
- Too much → elements feel disconnected
- The right amount → each element breathes without losing its relationship to neighbors

**Active whitespace** — whitespace placed *deliberately asymmetrically* to direct attention
- A heading pushed to the right with a large empty left margin draws the eye to the left first (the void), then snaps it to the content
- A single centered image in a vast white sea becomes the most important thing on the page
- An off-center CTA button with space only on its right guides the eye to read left-to-right into the button

### The "float" principle

Elements that feel like they're floating — hovering above the page rather than sitting on it — achieve this through asymmetric whitespace around them. Mathematical centering doesn't float; intentional breathing room does.

```css
/* Mathematical center — looks placed, not floating */
.hero-content { margin: 0 auto; padding: 80px 0; text-align: center; }

/* Active whitespace — asymmetric, creates visual interest */
.hero-content {
  padding-top: 120px;     /* more space above — content drops into view */
  padding-bottom: 80px;
  padding-left: 8%;       /* offset from left — creates lateral tension */
  max-width: 680px;       /* deliberately not filling the full grid */
}
```

### Whitespace as luxury signal

The correlation between whitespace and perceived quality is nearly absolute in premium brand design.

| Whitespace level | Perceived product quality | Example |
|-----------------|--------------------------|---------|
| Very tight (8–16px section padding) | Budget, utilitarian | Craigslist, early Bootstrap sites |
| Standard (40–64px section padding) | Professional, functional | Most SaaS products |
| Generous (80–120px section padding) | Premium, considered | Linear, Vercel, Stripe |
| Extreme (160–240px section padding) | Luxury, editorial | Apple, LVMH, Anthropic |

**The upgrade rule:** When a layout feels "busy" or "generic," the first fix is almost always adding whitespace — not changing colors or fonts.

### When to break the whitespace rule

Controlled density contrast creates rhythm. A page that's entirely spacious has no rhythm.

- A data table or pricing comparison *should* be dense — it signals that information is being systematically presented
- A feature showcase grid can be tighter than surrounding sections — the contained density reads as "comprehensive"
- The contrast between a dense section and the whitespace surrounding it makes both feel more intentional

---

## Color system construction

**Building a proper palette from one brand color:**

Step 1: Define the brand hue in HSL: `hsl(H, S%, L%)`
Step 2: Generate 9-step scale (50→900) by varying L% while keeping H and S±10%:
```
50:  L=97% (near white tint)
100: L=94%
200: L=88%
300: L=78%
400: L=62%
500: L=50% ← base brand color
600: L=42%
700: L=34%
800: L=26%
900: L=18% (near black shade)
```
Step 3: Apply semantic mapping:
- Light mode: backgrounds use 50–100, text uses 800–900, accent interactive uses 600
- Dark mode: backgrounds use 900–950, text uses 50–100, accent interactive uses 400

**OKLCH advantage:** For perceptually uniform scales (2024 best practice):
```css
.color-primary-500 { color: oklch(50% 0.2 260); }
/* L=lightness 0-100, C=chroma 0-0.4, H=hue 0-360 */
/* Changing only L gives visually equal-step lightness changes — HSL doesn't */
```

**The 8-color neutral system (from Tailwind/Radix analysis):**
- `slate` (cool, blue-tinted) — developer tools (Linear, Vercel, PlanetScale)
- `zinc` (neutral, barely tinted) — tool-agnostic products (shadcn default)
- `stone` (warm, slightly yellow) — editorial/warm products (Notion, Craft, Anthropic)
- `gray` (perfectly neutral) — maximum flexibility baseline

**Dark mode token rules** → see `design-taste.md` (canonical). The principles here are construction theory; the specific value prescriptions live there.

**Contrast requirements (WCAG 2.1 / 3.0):**
- Normal text (< 18px): minimum 4.5:1 contrast ratio
- Large text (≥ 18px or 14px bold): minimum 3:1
- UI components and graphics: minimum 3:1
- Use oklch lightness or the `contrast-color()` function to verify

---

## Color psychology & palette strategy

### The 60-30-10 rule

The most reliable structure for a color composition:
- **60%** — dominant: backgrounds, large surfaces (usually neutral)
- **30%** — secondary: cards, sidebar, text blocks (slightly elevated or contrasting neutral)
- **10%** — accent: CTAs, links, highlights, icons (the brand color)

Violating this creates visual noise. When accent color covers >15% of the surface, it stops being accent — it becomes background. Reserve the accent for one thing only.

```
Example: Linear
  60% → #08090a (page bg + surface)
  30% → #1a1b1e (raised cards, secondary surfaces)
  10% → #5e6ad2 (buttons, active states, links only)
```

### Elegance through restraint

A color isn't inherently elegant or inelegant — it's how it's used. Even a vivid neon can feel sophisticated with restraint. Even a muted champagne becomes bland without contrast.

**The restraint test:** Cover the accent color on your design. Does the layout still hold? If yes, the accent is doing its job as punctuation, not wallpaper.

**Monochromatic scheme strategy:**
Explore one color's full range (from near-white tint to near-black shade) before adding a second hue. Monochromatic schemes feel intentional and unified. The palette library's D7, S2, and F2 demonstrate this.

Construction:
1. Pick one base hue (e.g., teal, maroon, brown)
2. Generate 5–7 lightness steps across the range
3. Use darkest step as "black", lightest as "white", mid-steps for surfaces and text hierarchy
4. Only introduce a second hue if the design genuinely needs it — the accent

### Narrow chromatic focus

The fewer hues, the stronger each CTA stands out. When only one thing is blue on a neutral page, that blue is unmissable.

**Rule:** Start with zero accent colors. Add one. Stop. Add a second only if:
- It carries different semantic meaning (success vs. error)
- It appears on a different layer (e.g., gradient only in hero, never on interactive elements)

**The gradient exception:** A brand gradient (like B2's red+orange) may appear in hero sections and illustrations only. Never on buttons, never on interactive states — gradients on interactive elements create hover/active state problems.

### Replace black — the tonal unity principle

Never use pure `#000000` or `#111111` for text in a warm or branded palette. Use the darkest tint of the dominant hue instead:

| Palette temperature | Replace black with |
|--------------------|--------------------|
| Warm (brown/orange) | Dark brown: `#2c2019`, `#8d6959` |
| Purple/maroon | Aubergine: `#312335`, `#262626` |
| Cool blue | Deep navy: `#0a2540`, `#0f172a` |
| Green/teal | Forest dark: `#1a2218` |
| Neutral | Off-black: `#08090a`, `#111316` |

This creates tonal unity — every color in the design shares the same underlying hue temperature, making the whole feel like it was designed rather than assembled.

### Value transforms hue perception

Two designs using the "same" blue can feel completely different based on value (lightness):
- **Bright + warm blue** (`#5eb2f2`) → optimism, clarity, approachability
- **Deep + cool blue** (`#002846`) → authority, tradition, seriousness
- **Desaturated blue-gray** (`#567790`) → neutral, technical, calm

When selecting palette hues, choose the *value* first, then the exact hue. The value carries more emotional weight than the hue.

### Color temperature pairing rules

| Combination | Effect | Example |
|------------|--------|---------|
| Warm bg + warm accent | Serene, unified, safe | L1 Parchment + burnt orange |
| Cool bg + cool accent | Precise, technical, cold | D1 Linear + desaturated indigo |
| Warm bg + cool accent | Tension, energy, unexpected | L3 Cream + indigo pop |
| Cool bg + warm accent | Grounded drama, approachable dark | D3 Ember + ember orange |
| Neutral bg + any accent | Maximum flexibility | L5/D7 + any brand color |

---

## Spacing system

**8px base grid — the industry standard:**
```
spacing scale: 2/4/6/8/10/12/16/20/24/32/40/48/64/80/96/128/160/192/256
                ↑mini ↑tight ↑   ↑base     ↑component      ↑section ↑page
```

**Semantic spacing assignments:**
- `2–4px`: Icon padding, inline decorations
- `8–12px`: Component internal padding (tight density)
- `12–16px`: Component internal padding (comfortable, default)
- `16–24px`: Component internal padding (spacious, marketing)
- `24–32px`: Between sibling elements in a group
- `32–48px`: Between unrelated groups / card grid gap
- `48–80px`: Section internal padding (top/bottom within a section)
- `80–160px`: Between major page sections (vertical rhythm)
- `160px+`: Hero sections, landing page breathing room

**The Proximity Rule (Gestalt) expressed in numbers:**
- Label to its input: `4–8px`
- Input to next input group: `24–32px`
- Section heading to its content: `12–16px`
- Unrelated section to next section: `64–120px`
- If spacing values look equal, add more contrast between them

---

## Depth & surface system

**5-level depth model:**

| Level | Use case | Shadow or treatment |
|-------|----------|-------------------|
| 0 (flat) | Page background | No shadow, no border |
| 1 (raised) | Cards, containers | Subtle border OR `box-shadow: 0 1px 3px rgba(0,0,0,0.08)` |
| 2 (floating) | Dropdowns, popovers | `box-shadow: 0 4px 16px rgba(0,0,0,0.12), 0 1px 4px rgba(0,0,0,0.08)` |
| 3 (overlay) | Modals, dialogs | `box-shadow: 0 20px 60px rgba(0,0,0,0.2)` + backdrop |
| 4 (toast) | Notifications | Maximum elevation, always visible |

**Border radius system:**
```
none: 0px         (tables, data-dense UIs)
xs:   2px         (code badges, subtle tags)
sm:   4px         (inputs, default buttons)
md:   6–8px       (cards, panels — most common)
lg:   12px        (large cards, modals)
xl:   16–20px     (feature tiles, marketing cards)
2xl:  24–28px     (hero cards, large callouts)
full: 9999px      (pills, avatars, toggle switches)
```

Never mix radius styles arbitrarily — pick a maximum of 3 radius values for an entire product.
Buttons and inputs should share the same radius (visual consistency).

**Glass morphism — when to use and how:**
Appropriate for: floating nav, sidebar, modal backdrop, card overlaid on imagery/gradient
Recipe:
```css
background: rgba(15, 15, 17, 0.72);         /* or white equivalent */
backdrop-filter: blur(20px) saturate(180%);
-webkit-backdrop-filter: blur(20px) saturate(180%);
border: 1px solid rgba(255, 255, 255, 0.08);
box-shadow: inset 0 1px 0 rgba(255,255,255,0.06); /* inner edge refraction */
```
Use maximum once or twice per page. Overuse = Dribbble shot that doesn't work as a product.

**Double-Bezel Architecture (premium nested surfaces):**
Components that read as physical, machined objects — an outer shell + an inner core
with distinct backgrounds, borders, and shadows. Use for cards meant to stand out.
```css
/* Outer shell */
.bezel-outer {
  background: var(--color-surface);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px;
  padding: 1px;             /* the "bezel" width */
  box-shadow: 0 8px 32px rgba(0,0,0,0.24), 0 1px 0 rgba(255,255,255,0.04);
}

/* Inner core */
.bezel-inner {
  background: var(--color-bg);
  border-radius: 19px;      /* 1px less than outer — critical */
  border: 1px solid rgba(255,255,255,0.04);
  padding: 24px;
}
```

**Spotlight borders (cursor-reactive premium card effect):**
```tsx
// Track mouse position, illuminate nearest card edge
const handleMouseMove = (e: MouseEvent) => {
  const rect = card.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  card.style.setProperty('--mouse-x', `${x}px`)
  card.style.setProperty('--mouse-y', `${y}px`)
}
// CSS:
// background: radial-gradient(600px at var(--mouse-x) var(--mouse-y),
//   rgba(255,255,255,0.06), transparent 40%)
```

**Noise/grain overlay (break digital flatness):**
```css
.grain::after {
  content: '';
  position: fixed; inset: 0; pointer-events: none; z-index: 9999;
  background-image: url("data:image/svg+xml,...");  /* or SVG turbulence filter */
  opacity: 0.04;
}
```

**Colored shadow tinting (depth that belongs to the design):**
Never use `rgba(0,0,0,X)` shadows on colored surfaces.
Tint shadow to match background hue: a blue card gets `rgba(59, 130, 246, 0.2)` shadow.


---

## Motion — animation that earns its place

**Duration scale (Disney's timing principle applied to UI):**
```
instant:    0ms      (state changes that feel physical — toggle on/off)
micro:      100ms    (hover color changes, focus ring appearance)
fast:       150ms    (button press feedback, small icon transitions)
standard:   200ms    (most UI transitions — hover lift, dropdown open)
emphasis:   300ms    (modal enter, slide-in panel, toast appear)
deliberate: 400ms    (page section reveal, complex state change)
cinematic:  600ms+   (hero animations, onboarding flows, splash)
```

**Easing curves:**
```css
/* Most UI interactions — natural deceleration */
--ease-out:      cubic-bezier(0.0, 0.0, 0.2, 1.0);

/* Entering elements — expo deceleration, snappy feel */
--ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);  /* Linear, Raycast standard */

/* Elements being dismissed */
--ease-in:       cubic-bezier(0.4, 0, 1, 1);

/* Continuous motion (progress bars, loading) */
--ease-linear:   linear;

/* Spring / bounce for playful products */
--spring:        cubic-bezier(0.34, 1.56, 0.64, 1);
```

**Reduced motion — always implement:**
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

**Hover state patterns by archetype** → see `visual-archetypes.md` Motion Style table (duration, easing, hover behavior, and what to avoid for each archetype).


---

## Component state system — every interactive component needs all states

A component is not finished until all its states are designed. Missing states are bugs.

**The 8 required states** (Default · Hover · Active · Focus · Disabled · Loading · Error · Success) with full CSS implementation → see `implementation/code-standards-extended.md` Component State Matrix.

**Skeleton screens over spinners — when and why:**
- Use skeleton when you know the layout of what's loading (list items, cards, profiles)
- Use spinner only for unknown-shape content or brief (<500ms) loads
- Skeleton maintains spatial continuity — the page doesn't jump when content loads
- Match skeleton shape to actual content shape (a skeleton avatar is circular, not rectangular)

```css
/* Skeleton animation */
.skeleton {
  background: linear-gradient(
    90deg,
    var(--color-bg-subtle) 25%,
    var(--color-surface-raised) 50%,
    var(--color-bg-subtle) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

**Empty states — the most forgotten state:**
Empty states are onboarding opportunities, not failures. Every empty state needs:
1. A clear illustration or icon (not a generic "no data" message)
2. A plain-language explanation of why it's empty
3. A primary CTA to fill it: "Create your first project →"
4. Optional: a secondary hint showing what it will look like when populated

---

## Progressive disclosure — reveal complexity gradually

Never show everything at once. Complexity should be earned.

**The three levels:**
1. **Primary** — always visible. The main action, the key information.
2. **Secondary** — revealed on hover or expand. Supporting details, additional options.
3. **Tertiary** — revealed on demand. Advanced settings, edge cases, power-user features.

**Implementation patterns:**

```
Simple → Advanced:
  Show "Create account" → after click, reveal full form fields progressively

Tooltip disclosure:
  Icon button → hover reveals label tooltip (always add this)

Accordion:
  Section heading → click expands content (FAQ, settings groups)

"Show more":
  Truncated list of 5 → "Show 12 more" → full list

Inline expansion:
  Collapsed row → click expands inline detail (better than navigating to a new page)

Command palette:
  Surface-level UI → Cmd+K reveals full capability set for power users
```

**Rule:** If a feature is used by <20% of users, put it behind progressive disclosure. If it's used by <5%, put it in settings. Never surface rare edge cases in the primary UI.

---

## Cognitive load — design for the working memory limit

Human working memory holds 5–9 chunks. Design that exceeds this causes overwhelm.

**Three types of cognitive load:**

| Type | Cause | Design response |
|------|-------|----------------|
| **Intrinsic** | Task complexity (unavoidable) | Break into steps, use wizards |
| **Extraneous** | Poor design (avoidable) | Remove noise, simplify layout |
| **Germane** | Meaningful learning | Onboarding, tooltips, progressive reveal |

**Reduce extraneous load in code:**
- Chunk navigation: group 5–7 items max per level, use dividers between groups
- One primary action per screen section — multiple CTAs split attention
- Use `text-wrap: balance` on headings to prevent jarring line breaks
- Consistent component placement: search always top-right, back always top-left
- Remove labels that context makes obvious — a magnifying glass needs no "Search" label next to it in a search bar

**The Miller's Law implication:**
- Max 7 (±2) items in a dropdown, navigation menu, or list before adding search/filter
- Pricing tables: max 3–4 tiers before users stop comparing
- Form: max 5–7 fields per step; split long forms into a multi-step wizard

**The Serial Position Effect:**
- Users remember the first item and last item in a list better than middle items
- Put the most important nav item first OR last, never in the middle
- In pricing, put the recommended tier in the most visually prominent position (center)

---

---

## Conditional knowledge — load these files when needed

After locking the archetype and creative params in Phase 3, load additional modules as needed:

→ **Load `knowledge/design/design-principles-advanced.md`** when DESIGN_VARIANCE ≥ 6 OR archetype is H (Cinematic Portfolio), C (Chromatic Confidence), or G (Museum Authority).
  Contains: hero section composition (6 archetypes), visual rhythm, unforgettable moment reference library, illustration & media strategy.

→ **Load `knowledge/design/design-principles-motion.md`** when MOTION_INTENSITY ≥ 4.
  Contains: animation orchestration (staggered lists, scroll reveal, page transitions, modals), animation performance budget.

→ **Load `knowledge/design/design-principles-ux.md`** when component count ≥ 4 OR output includes forms, data tables, or navigation menus.
  Contains: Nielsen's 10 heuristics, affordance, progressive disclosure, cognitive load, form design system, data display patterns, navigation patterns, micro-copy & UX writing.

# Landing Page Section Anatomy

**Scope:** Composition patterns for every section of a landing page beyond the hero. For hero patterns, see `design-principles.md` → Hero section composition. For industry-specific section order, see `industry-patterns.md`.

A landing page is a directed narrative. Each section answers a question the user is implicitly asking as they scroll. Design the sequence before designing individual sections.

**Narrative arc:**
```
Hero          → "What is this?"          (hook, promise)
Features      → "What does it do?"       (capability proof)
Social proof  → "Can I trust this?"      (credibility)
How it works  → "How does it work?"      (process clarity)
Pricing       → "What does it cost?"     (commitment)
FAQ           → "What about…?"           (objection handling)
Final CTA     → "OK, I'm ready"          (conversion)
Footer        → "Where else can I go?"   (navigation / legal)
```

Not every page needs all sections. A single-product landing page may skip pricing. A waitlist page may go straight from Hero → Social proof → CTA.

---

## Feature Sections

### 1. Bento Grid *(highest visual quality, best for 4–8 features)*

Asymmetric grid where cells have different sizes and visual weights. The grid structure IS the design.

```
┌─────────────────┬──────────┐
│  LARGE FEATURE  │ feature  │
│  screenshot +   ├──────────┤
│  description    │ feature  │
├──────────┬──────┴──────────┤
│ feature  │  LARGE FEATURE  │
│          │  illustration + │
└──────────┴─────────────────┘
```

**Rules:**
- 1–2 "hero cells" (2× or 3× column span) anchor the grid
- Every cell needs a distinct visual: screenshot, illustration, diagram, animated element — not just icon + text
- Background variation between cells is acceptable here (subtle tints per cell, not rainbow)
- Gap: 12–16px between cells (tighter than section gap — they're a unified composition)

**When to use:** 4–8 features, visual product (something to show), design-forward brand (C, D, F archetypes)

**Avoid:** All cells same size. Empty cells with just an icon and 2 lines of text. Centering text in every cell.

---

### 2. Split Feature Rows *(most versatile, best for 3–5 deep features)*

One feature per row. Image/screenshot one side, text the other. Alternating L/R between rows.

```
[screenshot]  |  Heading
              |  Body text
              |  CTA link →

  Heading     |  [screenshot]
  Body text   |
  CTA link →  |
```

**Rules:**
- Column ratio: 55/45 or 60/40 — never 50/50
- Alternate sides: image-left then image-right then image-left (visual rhythm, prevents monotony)
- The screenshot/image must be product-real or high-fidelity — stock illustration kills credibility
- Vertical rhythm between rows: 80–120px (sections must breathe between each other)
- Text side: max 3 short lines of body, one optional CTA link (not a full button — that's too much weight)

**When to use:** Feature depth matters (each feature needs 2–3 sentences), B2B SaaS, dashboard products

**Avoid:** Same side for all rows. Body text over 60 words per feature. Equal-width columns.

---

### 3. Icon Feature Grid *(fastest to scan, weakest without real icons)*

3 or 4 columns of feature cards, each with icon + title + short description.

**The non-cliché version:**
- Icons must be custom SVG or carefully selected Phosphor icons that are specific to each feature — not generic checkmarks
- Body text ≤ 2 sentences (40 words max) — if you need more, use Split Feature Rows instead
- Column count: 3 for wide content, 4 for short labels
- No card borders or shadows — let whitespace do the separation (unless archetype is F: Soft Structuralism)
- Add one unexpected visual treatment: colored icon background, custom icon color per feature, or subtle line connecting features

**When to use:** 6–12 lightweight features where icons carry meaning, marketing-first products

**Avoid:** Emoji as icons. Identical 3-column layout if DESIGN_VARIANCE ≥ 5. Cards that look identical at a glance.

---

### 4. Screenshot-Anchored Section *(highest trust, best single-feature deep-dive)*

One large product screenshot or video as the centerpiece, with feature callouts pointing to UI elements.

```
        Heading + subtext (max 2 lines)

┌──────────────────────────────────┐
│         product screenshot       │
│  ← callout    callout → ← callout│
└──────────────────────────────────┘
   caption text (optional, small)
```

**Rules:**
- Screenshot must be high-fidelity and current — blurry or outdated screenshots damage credibility more than no screenshot
- Max 3–4 callout labels; more creates clutter
- Screenshot: `border-radius: 12px`, `box-shadow: 0 32px 80px rgba(0,0,0,0.15)`, subtle perspective tilt (2–4°) optional
- For dark products: screenshot on a lighter section background increases contrast and pop
- Add a tab or toggle if showing multiple views ("Overview / Analytics / Settings")

**When to use:** SaaS apps with a strong UI, single primary use case to demonstrate

---

### 5. Code / Technical Preview *(developer tools only)*

For developer-facing products. The code block IS the hero visual.

```
  Heading targeting developers

  ┌─────────── terminal / code block ────────────┐
  │  $ npx create-thing --template=starter       │
  │  ✓ Installing dependencies                   │
  │  ✓ Project created in ./my-app               │
  └──────────────────────────────────────────────┘

  3-column icon list of technical capabilities
```

**Rules:**
- Code block: dark theme even on light-mode pages — it's a visual anchor
- Show real, runnable code — not pseudocode or made-up syntax
- Add a copy button (essential for developer trust)
- Syntax highlighting should match the language (JS, Python, bash — don't mix)

**When to use:** Archetype D (Terminal Glass), API products, CLI tools, SDKs

---

## Social Proof Sections

Social proof answers "Can I trust this?" It should appear **after** the main feature section, not before. (Exception: if the brand is the primary credential, lead with logo cloud early.)

### 1. Logo Cloud *(fastest credibility signal)*

A row of well-known company logos.

```
Trusted by teams at

[logo] [logo] [logo] [logo] [logo] [logo]
```

**Rules:**
- 6–10 logos; fewer looks thin, more looks desperate
- Use SVG logos for sharpness — rasterized logos signal low effort
- All logos same height (not same width) — visual consistency
- Use grayscale / monochrome treatment: colored logos fight each other; the section reads as a color mess
  - Exception: `filter: grayscale(100%) brightness(0) invert(1)` on dark backgrounds
- "Trusted by teams at" is better copy than "Our customers include" — implies use, not endorsement

**When to use:** Early in the page when brand credibility is the primary signal, or below the hero

---

### 2. Pull Quote *(highest emotional impact, single voice)*

One testimonial, very large.

```
  "This completely changed how our team
   handles X. We cut Y by 60% in a week."

  [avatar]  Name, Title at Company
```

**Rules:**
- Quote text: 24–36px, weight 400–500 (not bold — let the words carry the weight)
- Max 2 sentences, 30 words — if it needs editing, edit it
- Attribution: avatar photo (real person), name, title, company — all four or skip the avatar
- Section must be generous: 120–160px padding top and bottom — the quote needs air around it
- Optional: 5-star rating above the quote (star rating makes the emotional tone explicit)

**When to use:** One exceptionally strong testimonial, B2C products, warm archetype (B, F)

---

### 3. Testimonial Card Grid *(balance of depth and breadth)*

3–4 testimonial cards in a grid.

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ ★★★★★        │  │ ★★★★★        │  │ ★★★★★        │
│ "Quote text  │  │ "Quote text  │  │ "Quote text  │
│  quote text" │  │  quote text" │  │  quote text" │
│              │  │              │  │              │
│ [av] Name    │  │ [av] Name    │  │ [av] Name    │
│ Title, Co.   │  │ Title, Co.   │  │ Title, Co.   │
└──────────────┘  └──────────────┘  └──────────────┘
```

**Rules:**
- Quote max 3 lines visible without overflow — truncate with `…` if needed, never let cards be different heights
- Use CSS Grid `align-items: start` — cards do NOT stretch to equal height (forces awkward padding)
- Star rating: same star count across all (don't show 4-star reviews — only use 5-star or none)
- Diversity in attribution: mix of seniority levels, company sizes, use cases
- Optional: one "featured" card spanning 2 columns with a longer quote

---

### 4. Case Study / Metric Block *(highest credibility for B2B)*

Numbers, not quotes.

```
┌────────────┐  ┌────────────┐  ┌────────────┐
│    3.2×    │  │    47%     │  │  14 days   │
│            │  │            │  │            │
│  Faster    │  │  Less time │  │  To first  │
│  deploys   │  │  in review │  │  result    │
└────────────┘  └────────────┘  └────────────┘
     [Company logo] — "[Brief quote]" — Name, Title
```

**Rules:**
- Numbers must be real and specific — "47%" not "50%", "3.2×" not "3×"
- Label: 3 words max; more reads like ad copy
- Pair metrics with a brief testimonial from the same company to provide context
- Use `font-variant-numeric: tabular-nums` on all numbers
- Number size: 48–64px, weight 700, tight letter-spacing

**When to use:** Enterprise SaaS, performance-claims products, post-free-trial conversion pages

---

## Pricing Section

Pricing is studied, not scanned. It's the densest information section on the page and must be designed for comparison.

### Tier structure

**Standard:** 3 tiers (Free / Pro / Enterprise). More than 4 tiers creates decision paralysis.

**Layout rules:**
- Recommended tier: subtle background elevation (card vs. flat), border in accent color, "Most Popular" badge at top
- All cards same width — equal visual weight forces comparison on content, not size
- Feature list must align across columns: same feature at same vertical position in each card
  - Use CSS Grid subgrid or `display: grid; grid-template-rows: subgrid` for perfect alignment
- CTA buttons: Primary variant on recommended tier, Secondary/Ghost on others
- Price: large number (48px), weight 700; billing period small (13px, muted) directly below

### Monthly / Annual toggle

```
          ○ Monthly  ●  Annual  — Save 20%
```

- Toggle updates prices via JavaScript — no page reload
- "Save X%" label next to the Annual option — make the discount visible immediately
- Animate the price change: `transition: all 200ms ease-out` on the price number
- Pre-select Annual if the discount is ≥ 20%

### Feature list formatting

- ✓ for included features (use a real checkmark SVG, not the `✓` character)
- — or greyed-out row for excluded features (not ✗ — the X reads as failure, which is too aggressive)
- Group features by category with a subtle section header if list is > 8 items
- "Everything in [lower tier] +" is acceptable for Pro/Enterprise rows

---

## How It Works Section

For products where the mechanism is non-obvious or the process is the value.

```
        How it works

  ①  Step one title        ②  Step two title        ③  Step three title
  Short explanation.       Short explanation.        Short explanation.
```

**Rules:**
- Max 3–4 steps; if you need 5+, you haven't simplified the story enough
- Steps are sequential — use numbered circles or a connecting line between them
- Each step needs a visual: icon, screenshot crop, or short animation
- Alt layout: vertical timeline (left-aligned numbers, right-aligned content) — better for mobile

---

## FAQ Section

FAQ handles objections and long-tail questions without cluttering the main pitch.

**Accordion pattern:**
```
▼  Question one?
   Answer text, 2–4 sentences.

▶  Question two?

▶  Question three?
```

**Rules:**
- 5–8 questions is the right range; fewer suggests you don't know your objections, more suggests feature confusion
- First question: the most common objection ("Is this secure?" / "Does it work with X?" / "What if I want to cancel?")
- Questions should be in the user's voice — "Can I cancel anytime?" not "Cancellation policy"
- One question open by default — the most important one
- Keep answers under 60 words; if more is needed, link to docs
- Optional: group questions by category (Pricing, Security, Integrations) if > 8 questions

---

## CTA Section

The final push before the footer. One message, one action.

**Anti-pattern:** A repeat of the hero. The user has already seen it.
**Good version:** A single sentence that acknowledges the journey — "You've seen what [product] does. Ready to try it?"

**Layout:**
```
    ┌─────────────────────────────────────────┐
    │                                         │
    │   Heading (1 line max, 8–10 words)     │
    │   Subtext (optional, 1 line)            │
    │                                         │
    │          [ Primary CTA button ]         │
    │      Small trust note below button      │
    │                                         │
    └─────────────────────────────────────────┘
```

**Rules:**
- Background: either a full-bleed dark/accent band, or a neutral card on a white page — the section must feel distinct from the FAQ above it
- Padding: 120–160px top and bottom — the call to action needs air
- CTA button: large (height ≥ 52px), primary color, centered
- Trust note below button: "No credit card required" / "Free 14-day trial" / "Cancel anytime" — 13px muted text
- Never put two equal CTAs here ("Try free" + "Talk to sales" at the same weight). Primary gets the visual weight; "Talk to sales" becomes a text link below.

---

## Footer

The footer is navigational infrastructure, not design expression. Users who reach the footer are determined — make it useful.

### Dense SaaS footer (multi-column)

```
[Logo]              Product        Company        Resources       Legal
Tagline (1 line)    Feature 1      About          Blog            Privacy
                    Feature 2      Careers        Docs            Terms
[Social icons]      Pricing        Press          Status          Cookies
                    Changelog      Contact        API

© 2025 Company Name. All rights reserved.        [Language selector]
```

**Rules:**
- 4–5 columns: Product links / Company / Resources / Legal — exact split depends on content
- Logo top-left, copyright bottom-left
- Social icons near logo (not scattered across columns)
- Column headings: 11–12px, uppercase, wide tracking, muted color — not bold
- Links: 14px, weight 400 — footer links should be quiet, not compete with page content
- Bottom bar: copyright + optional language selector on one line, separated from column grid by a 1px border

### Minimal portfolio/personal footer

```
© 2025 Name   ·   Built with [tech]   ·   [Email]   ·   [GitHub]
```

**Rules:**
- Single line, centered or left-aligned
- No columns, no logo repeat, no nav list
- If there is a "Back to top" link, it lives here (right-aligned)

---

## Section spacing rhythm

How much space between sections determines whether a page breathes or suffocates.

| Section pair | Spacing |
|---|---|
| Nav → Hero | 0 (hero full-bleed) or 24px |
| Hero → Features | 80–120px |
| Features → Social proof | 80–100px |
| Social proof → Pricing | 80–120px |
| Pricing → FAQ | 64–80px |
| FAQ → CTA | 80–120px |
| CTA → Footer | 0 (footer is its own block) |

**Background alternation rule:** Max 2 distinct backgrounds on a page (e.g., white + very-subtle-gray). Every section switching to a new tint is the AI-slop signal. Use spacing and grid changes to separate sections, not background color.

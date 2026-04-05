# Visual Archetype Definitions

**When to use:** Load this file in Phase 3 Step 2 when presenting archetype options to the user. Present only the 2–3 pre-filtered options from Step 1 — never show the full list.

The canonical archetype → parameter table lives in `SKILL.md`. This file contains the full descriptions, palette mappings, and live reference URLs for each archetype.

---

## Archetype A–J Descriptions

### A) Obsidian Precision
*Linear, Vercel, Cursor, TwelveLabs, Invisible Tech*

Off-black `#08090a` or warm charcoal `#14120b` · Geist/Inter/custom sans · −0.03em heading tracking · Desaturated accent · Hairline rgba borders · Zero shadow

**Signature:** nothing decorative. Every pixel earns its place.

Palettes: **D1 Linear Void**, **D4 Deep Cobalt**, **D7 Obsidian Pearl**

Live references for this archetype:
- https://linear.app — the canonical example; hairline dividers, near-black precision
- https://vercel.com — bold black, Geist, full-bleed sections
- https://cursor.com — warm charcoal variant, triple typeface stack

---

### B) Warm Editorial
*Notion, Craft, Anthropic, Loom*

Cream/parchment `#f8f4ed` · Humanist or transitional serif · Soft colored shadows · Generous spacing

**Signature:** feels written, not designed. Human warmth over technical precision.

Palettes: **L1 Parchment Warmth**, **L7 Zen Ink**, **L3 Cream Canvas**, **S2 Duotone Sepia**, **F1 Earth Craft** (artisan/organic brands), **F2 Maroon Mood** (boutique/literary)

Live references for this archetype:
- https://anthropic.com — cream bg, burnt orange accent, serif warmth
- https://notion.so — off-white, no decorative color, document feel
- https://loom.com — humanist warmth, editorial spacing

---

### C) Chromatic Confidence
*Stripe, Framer, Robinhood, Awwwards*

High contrast · Licensed/variable typeface · Strong brand gradient · Oversized type · Spring physics

**Signature:** the type IS the design. Color is used boldly, not cautiously.

Palettes: **B1 Stripe Oxide**, **B2 Framer Noir**, **B3 Prismatic Dusk**, **B4 High Noon**, **F3 Power Purple** (beauty/fashion/luxury events), **S3 Neon Brutalist**

Live references for this archetype:
- https://stripe.com — diagonal gradient hero, Söhne type, nested feature cards
- https://framer.com — spring physics, electric gradient, bold motion
- https://robinhood.com — neon lime accent, Martina Plantijn serif, warm dark bg

---

### D) Terminal Glass
*Raycast, Supabase, Warp*

Near-black `#141414` · Coral/green/electric accent · JetBrains Mono presence · `backdrop-filter: blur(20px)` glass

**Signature:** feels like native desktop software. Glass as material, not decoration.

Palettes: **D3 Ember Obsidian**, **D2 Terminal Jade**, **D5 Volcanic Amber** (dramatic/luxury dark), **D8 Steel Teal**, **S1 Glassmorphic Night**

Live references for this archetype:
- https://raycast.com — glass morphism, coral accent, desktop-native feel
- https://supabase.com — terminal aesthetic, jade accent, developer-native UI
- https://www.warp.dev — dark glass, developer tool precision

---

### E) Luxury Silence
*Apple, Figma, LVMH digital*

Photography-driven · Vast whitespace · Transitional serif display · Product color = page color · 120px+ section rhythm

**Signature:** what you leave out is the design. Restraint is the skill.

Palettes: **L2 Arctic Restraint**, **L8 Bone Linen**, **L4 Mist Sage**

Live references for this archetype:
- https://apple.com — full-bleed photography, `#f5f5f7` bg, vast whitespace
- https://figma.com — premium restraint, photography-driven product sections

---

### F) Soft Structuralism
*Cron, Avenia, Base44, emerging SaaS*

`#f9fafb` base · White cards · `rounded-[2.5rem]` containers · Diffusion shadows · Bento grid · Subtle perpetual motion

**Signature:** structured like engineering, soft like a consumer app.

Palettes: **L5 Slate Cloud**, **L6 Ivory Coral**, **D6 Cosmic Violet**

Live references for this archetype:
- https://base44.com — bento grid, CSS-variable theming, soft structuralism
- https://avenia.io — white bg, teal accent, card-based, API-minimal

---

### G) Museum / Cultural Authority
*Met Museum, Rijksmuseum, Smithsonian*

White/warm-off-white · Institutional serif (Austin, RijksText) + Inter body · Cultural accent · Flat/zero-shadow · Art-forward

**Signature:** 5000 years of context behind every spacing decision.

Palettes: **L7 Zen Ink**, **L1 Parchment Warmth**, **L8 Bone Linen**

*(Usually auto-resolves to L7 Zen Ink — only ask if the institution has a distinctive heritage palette.)*

Live references for this archetype:
- https://www.metmuseum.org — Austin serif + Inter, Met Red hover, 1px separator discipline
- https://www.rijksmuseum.nl — custom RijksText, warm gold heritage palette
- https://www.si.edu — Smithsonian, multi-collection navigation

---

### H) Cinematic Portfolio
*A24 Films, Robin Noguier, Dennis Snellenberg, Lynn Fisher*

Dark `#0d0d0d` or warm white · Custom display typeface · Per-project palette theming · Work IS the visual system

**Signature:** the portfolio itself is the case study.

Palettes: **D7 Obsidian Pearl**, **L8 Bone Linen**, **B2 Framer Noir**

Live references for this archetype:
- https://a24films.com — warm off-white, film poster grid, extreme restraint
- https://robin-noguier.com — per-project palette reset, draggable carousel
- https://dennissnellenberg.com — multilingual hero, near-white/black
- https://lynnandtonic.com — annual redesign, user-controlled theme

---

### I) Developer Personal
*Brian Lovin, ryo.lu, paco.me*

`#fff` / `rgb(10,10,10)` · Source Serif 4 + Inter or system mono · `42rem` max-width · Content as sole visual hierarchy

**Signature:** the writing is the design.

Palettes: **L7 Zen Ink**, **L2 Arctic Restraint**, **D1 Linear Void**

*(Usually auto-resolves to L7 or L2 — only ask when the developer has a strong personal brand color.)*

Live references for this archetype:
- https://brianlovin.com — Source Serif 4 + Inter, `42rem` prose, dark/light toggle
- https://paco.me — monochrome, document-like, substance-first
- https://ryo.lu — extreme content clarity, Japanese minimalism

---

### J) Custom
User describes their own vision; synthesize a Design DNA Report from first principles using the First Principles Path below.

**Parameter adjustment for Archetype J** (defaults: DESIGN_VARIANCE=7, MOTION_INTENSITY=5, VISUAL_DENSITY=4):

Adjust from defaults based on description signals:

| Signal in description | Adjustment |
|-----------------------|-----------|
| "minimal", "clean", "restrained", "quiet" | DESIGN_VARIANCE −2, MOTION_INTENSITY −2 |
| "bold", "expressive", "dynamic", "loud" | DESIGN_VARIANCE +2, MOTION_INTENSITY +2 |
| "dense", "data-heavy", "information-rich" | VISUAL_DENSITY +3 |
| "airy", "editorial", "spacious", "breathing" | VISUAL_DENSITY −2 |
| "fast", "energetic", "spring", "bouncy" | MOTION_INTENSITY +2 |
| "slow", "cinematic", "considered" | MOTION_INTENSITY −2, duration ×1.5 |
| "asymmetric", "broken", "unconventional" | DESIGN_VARIANCE +2 |
| "structured", "grid", "systematic" | DESIGN_VARIANCE −2 |

Apply all matching adjustments, then clamp each value to [1–10].

---

## Dark Mode Requirements by Archetype

Apply during Phase 4 generation. Dark mode is a design decision, not a default toggle.

| Archetype | Dark mode | Rationale |
|-----------|-----------|-----------|
| A Obsidian Precision | **Required** | These products ARE dark-first; light mode is secondary |
| B Warm Editorial | Optional | Warm cream palette doesn't translate well to dark; only add if user requests |
| C Chromatic Confidence | Optional | Bold color works in both; add only if user requests |
| D Terminal Glass | **Required** | Terminal aesthetic is intrinsically dark; light mode defeats the point |
| E Luxury Silence | Discouraged | Full-bleed photography and vast whitespace define this archetype; dark mode erodes both. Add only when explicitly product-mandated (e.g., a luxury tech device with a dark brand identity) — use deep charcoal `#1a1a1a`, never pure black |
| F Soft Structuralism | Optional | Light-first by definition; dark variant possible but rarely requested |
| G Museum Authority | Discouraged | Institutional identity is light-on-white; dark mode undermines authority for most institutions. Add only when the institution has an explicit dark brand identity — never as a default toggle |
| H Cinematic Portfolio | Optional | Per-project theming supersedes global dark mode |
| I Developer Personal | **Required** | Developer sites must respect system preference; `prefers-color-scheme` is table stakes |

**Implementation rule:** For Required archetypes, implement `[data-theme='dark']` or `@media (prefers-color-scheme: dark)` with a full token override block. For Optional, add a toggle only if user explicitly requests it. For Discouraged, omit unless user explicitly product-mandates it — if added, document the rationale in a code comment.

→ Implementation pattern: see `implementation/code-standards-extended.md` (Dark mode section).

---

## Motion Style by Archetype

Motion is not decoration — it is character. Each archetype has a motion signature that should be consistent across all interactive elements.

| Archetype | Duration range | Easing | Hover behavior | Avoid |
|-----------|---------------|--------|----------------|-------|
| A Obsidian Precision | 150–200ms | `cubic-bezier(0.0, 0.0, 0.2, 1)` (ease-out) | Background tint, no movement | Spring, bounce, scale |
| B Warm Editorial | 250–350ms | `ease-in-out` | Opacity fade, subtle underline grow | Fast snaps, transforms |
| C Chromatic Confidence | 300–500ms | `cubic-bezier(0.34, 1.56, 0.64, 1)` (spring) | `translateY(-3px)` + shadow grow | Linear easing, anything slow |
| D Terminal Glass | 200–250ms | `cubic-bezier(0.16, 1, 0.3, 1)` (expo-out) | Border glow, backdrop-filter reveal | Bounce, organic curves |
| E Luxury Silence | 500–800ms | `ease` (symmetric) | `opacity: 0.8` only, ultra-slow | Fast, bouncy, scale transforms |
| F Soft Structuralism | 250–350ms | `cubic-bezier(0.34, 1.2, 0.64, 1)` (gentle spring) | Card `translateY(-2px)` + diffuse shadow | Abrupt snaps, harsh easing |
| G Museum Authority | 150–200ms | `ease-out` | Subtle color shift only | Decorative animation of any kind |
| H Cinematic Portfolio | 400–600ms | Custom per project | Full-cursor morph, page-level palette swap | Generic hover lifts |
| I Developer Personal | 100–150ms | `ease-out` | Border-color shift only; respect `prefers-reduced-motion` | Any animation not table-stakes |

**Motion budget rule:** See `design-principles.md` → Animation Performance Budget for simultaneous animation limits, stagger rules, and `will-change` guidelines.

---

## Non-Product / Experimental Tones

Use instead of A–J when the archetype system doesn't fit (posters, events, art projects, speculative products). Each tone has its own parameter defaults — treat them as J (Custom) with a pre-set starting point.

| Tone | DESIGN_VARIANCE | MOTION_INTENSITY | VISUAL_DENSITY | Palette direction | Dark mode |
|------|-----------------|-----------------|----------------|-------------------|-----------|
| **Brutalist Raw** | 9 | 2 | 8 | Pure black/white + one harsh accent; system fonts (Arial, Times, Courier) as statement | Either (both work equally) |
| **Retro-Futuristic** | 7 | 6 | 7 | Deep navy/black + phosphor green or amber; scan-line texture overlay | Required (CRT is dark-first) |
| **Art Deco / Geometric** | 5 | 3 | 6 | Warm ivory + gold/bronze accent + deep navy; strict symmetry | Optional |
| **Maximalist Chaos** | 10 | 9 | 10 | No palette limit — intentional color collision; mixing 4+ families is acceptable | Either |
| **Organic / Natural** | 7 | 4 | 3 | Warm earth tones; linen/stone/moss; zero sharp corners | Discouraged |
| **Editorial / Magazine** | 4 | 2 | 5 | Black ink + white paper + one spot color; strong grid | Optional |
| **Industrial / Utilitarian** | 2 | 1 | 9 | Gunmetal + safety orange or signal yellow; monospace type only | Required |

**Tone descriptions:**
- **Brutalist Raw** — exposed structure, harsh contrast, system fonts as statement; layout rules are visibly broken
- **Retro-Futuristic** — CRT aesthetics, scan lines, phosphor glow, retrofuture grid
- **Art Deco / Geometric** — symmetry, gilded accents, structured ornamentation, precise geometry
- **Maximalist Chaos** — everything at once, intentional visual overwhelm; restraint is the anti-pattern
- **Organic / Natural** — irregular forms, biomorphic shapes, natural texture, soft imprecision
- **Editorial / Magazine** — grid-first, pullquotes, photo-essay rhythm, print design translated to screen
- **Industrial / Utilitarian** — bare metal, function-only, zero ornament; data density is the aesthetic

---

## First Principles Path (Novel Categories Only)

Use when the product category has no established visual conventions (wearables, spatial computing, BCI, biotech, consumer hardware, speculative products). Do NOT force into an archetype designed for a different context.

Ask with `AskUserQuestion` (translate these questions into the user's language per the global language rule):

```
Where does this product sit on each spectrum? (Rate 1–5: 1 = left end, 5 = right end, 3 = middle)

1. Functional ←————→ Experiential
   User comes to complete a task    User comes to feel something

2. Precise restraint ←————→ Sensory expression
   Every pixel has functional meaning    Emotion and atmosphere first

3. Institutional authority ←————→ Personal intimacy
   Brand over individual    Personalized, like a conversation

4. Futuristic ←————→ Present reality
   Sci-fi / ahead of its time / untouchable    Real / textured / tangible

5. Visual density
   Information-dense    Extreme breathing room / whitespace
```

From the 5 scores, vector-match the closest A–J archetype(s), then note where this product diverges. Name the hybrid explicitly (e.g., "E × A: Luxury Precision — restraint of Apple, engineering credibility of Linear"). Use the hybrid's combined palette options.

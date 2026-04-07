# Icon Style Catalog

## Style Archetypes

Each style archetype defines a visual personality. Choose based on your product's positioning.

---

### 1. Geometric Minimal (Linear, Vercel, Stripe)
```
Stroke:     1.5px uniform
Corners:    0–1px radius (sharp)
Cap/Join:   butt / miter
Shapes:     Pure geometry — circles, rectangles, straight lines
Detail:     Minimal — 3-5 elements max per icon
Mood:       Precise, engineering-forward, clean
Best for:   Developer tools, SaaS platforms, B2B products
```
**SVG traits:** No curves except perfect arcs. Paths use L/H/V commands predominantly.
Avoid organic curves (C/S commands).

### 2. Rounded Friendly (Phosphor, Heroicons)
```
Stroke:     2px uniform
Corners:    2px radius
Cap/Join:   round / round
Shapes:     Softened geometry with rounded terminals
Detail:     Moderate — allows small interior details
Mood:       Approachable, warm, consumer-friendly
Best for:   Consumer apps, social platforms, wellness, education
```
**SVG traits:** Generous use of `stroke-linecap="round"` and `stroke-linejoin="round"`.
Corners use `rx` attributes or arc commands.

### 3. Duotone Expressive (Phosphor Duotone, Ant Design)
```
Primary:    2px stroke or solid fill
Secondary:  10–15% opacity fill areas
Corners:    1–2px radius
Detail:     Rich — interior fills create depth
Mood:       Polished, feature-rich, modern
Best for:   Dashboards, enterprise products, feature marketing
```
**SVG traits:** Two layers — stroke path + fill path with `opacity="0.12"`.
Group with `<g>` for clean structure.

### 4. Outlined Thin (Feather, Tabler)
```
Stroke:     1.5px uniform
Corners:    1px radius
Cap/Join:   round / round
Shapes:     Simple, open forms
Detail:     Very minimal — 2-4 strokes max
Mood:       Quiet, editorial, content-first
Best for:   Content platforms, reading apps, note-taking, blogs
```
**SVG traits:** Short paths, few commands. Often just 2-3 `<line>` or `<path>` elements.

### 5. Filled Bold (SF Symbols, Material Filled)
```
Fill:       Solid single-color
Corners:    1–2px radius
Weight:     Heavy — designed to anchor navigation
Detail:     Simplified silhouettes
Mood:       Confident, mobile-native, system-level
Best for:   Mobile apps, navigation bars, tab bars, system UI
```
**SVG traits:** Single `<path>` with `fill` and no stroke. Complex `d` attribute
defining the silhouette. Often uses `fill-rule="evenodd"` for counter shapes.

### 6. Hand-Drawn Organic (Custom)
```
Stroke:     Variable 1–3px (simulated with SVG filters)
Corners:    Irregular
Cap/Join:   round / round
Shapes:     Imperfect geometry, slight wobble
Detail:     Character-driven — each icon has personality
Mood:       Playful, human, indie
Best for:   Creative tools, indie products, children's apps, personal brands
```
**SVG traits:** Slightly irregular paths (add ±0.5px noise to control points).
May use `<filter>` for hand-drawn effect.

---

## Style Decision Matrix

| Factor              | Geometric | Rounded | Duotone | Thin  | Filled | Organic |
|---------------------|-----------|---------|---------|-------|--------|---------|
| Information density | ★★★★★    | ★★★☆☆  | ★★★☆☆  | ★★★★★ | ★★★★☆ | ★★☆☆☆  |
| Small size (16px)   | ★★★★★    | ★★★★☆  | ★★☆☆☆  | ★★★★★ | ★★★★★ | ★★☆☆☆  |
| Visual warmth       | ★★☆☆☆    | ★★★★★  | ★★★☆☆  | ★★★☆☆ | ★★☆☆☆ | ★★★★★  |
| Dark mode           | ★★★★★    | ★★★★★  | ★★★★☆  | ★★★★★ | ★★★★★ | ★★★☆☆  |
| Brand differentiation| ★★☆☆☆   | ★★☆☆☆  | ★★★★☆  | ★★☆☆☆ | ★★★☆☆ | ★★★★★  |

---

## Combining Styles

A product typically uses **one primary style** with selective elevation:
- **Navigation:** Outline (default) → Filled (active) — the standard toggle
- **Feature cards:** Promote from outline to duotone at larger sizes (≥32px)
- **Empty states:** Promote from outline to duotone or add illustration wrapper
- **Destructive actions:** Same style, semantic red color — never change icon style for state

**Never mix more than 2 styles in the same UI surface.**

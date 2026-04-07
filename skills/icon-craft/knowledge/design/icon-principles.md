# Icon Design Principles

## Core Philosophy

Icons are **visual verbs** — they communicate action, state, or category in the smallest possible
space. A great icon is understood in <200ms without a label. A bad icon is a decorative emoji
that says nothing.

### The Anti-Emoji Manifesto

Generic emoji (🔥📊✨💡🚀) are the Comic Sans of product design:
- They carry **cultural noise** — each person reads a different meaning
- They lack **visual consistency** — mixed vendors, mixed weights, mixed metaphors
- They scream **prototype** — no shipping product uses 🎯 as a nav icon
- They break at small sizes and in dark mode

**What to use instead:** Purpose-built vector icons with consistent stroke weight,
optical alignment, and semantic clarity.

---

## The 7 Laws of Product Icon Design

### 1. Clarity Over Cleverness
The icon must be understood **without a tooltip**. If users need to hover to understand,
the icon has failed. Test: describe the icon to someone over the phone in <5 words.

- **Good:** A magnifying glass for search
- **Bad:** A brain with a magnifying glass for "smart search"

### 2. Optical Consistency
All icons in a set must feel like they were drawn by the same hand:
- **Uniform stroke width** — typically 1.5px or 2px at 24×24
- **Consistent corner radius** — 0 (sharp), 1px (soft), or 2px (rounded) — pick one
- **Same visual weight** — a filled circle shouldn't sit next to a hairline outline
- **Pixel-grid alignment** — strokes on whole or half pixels to avoid blur

### 3. Semantic Precision
Each icon maps to exactly one concept. Overloaded icons create confusion:
- A gear ≠ "settings + preferences + configuration + admin"
- Use **gear** for settings, **sliders** for preferences, **wrench** for configuration, **shield** for admin

### 4. Scalability Discipline
Design at **24×24** (the universal base), test at:
- **16×16** — inline text, table cells → simplify: remove inner detail
- **20×20** — sidebar nav, toolbar
- **24×24** — primary canvas size
- **32×32** — feature cards, empty states
- **48×48+** — hero illustrations, onboarding → add detail

Rule: if detail disappears below 16px, it shouldn't exist.

### 5. Negative Space is Structure
The space *inside* and *around* an icon is as important as the strokes:
- Maintain consistent padding within the bounding box (typically 2px at 24×24)
- Use **keyline shapes** (circle, square, portrait rectangle, landscape rectangle) to
  normalize visual weight across different icon forms

### 6. Metaphor Hierarchy
Choose metaphors from the user's domain, not the designer's:
- **Level 1 — Universal:** Search (magnifier), Close (×), Menu (hamburger), Back (arrow)
- **Level 2 — Convention:** Settings (gear), Profile (person), Notifications (bell), Home (house)
- **Level 3 — Domain-specific:** Must be learned → always pair with label on first encounter

### 7. State, Not Decoration
Icons communicate **state changes** through deliberate variation:
- **Default → Active:** outline → filled (e.g., heart outline → heart filled)
- **Enabled → Disabled:** full opacity → 40% opacity
- **Normal → Destructive:** neutral color → red
- Never change the icon's shape to indicate state — users lose recognition

---

## Visual Specifications

### Stroke-Based Icons (Outline Style)
```
Stroke width:    1.5px (light) | 2px (regular) | 2.5px (bold)
Corner radius:   1px (default) | 0 (technical) | 2px (friendly)
Line cap:        round (friendly) | butt (technical)
Line join:       round (friendly) | miter (sharp/technical)
Bounding box:    24×24 with 2px padding → 20×20 active area
```

### Filled Icons (Solid Style)
```
Use for:         Active/selected state, emphasis, navigation
Avoid for:       Dense toolbars (too heavy), inline text
Border radius:   Match stroke style's corner radius
Counter space:   Maintain ≥1.5px knockout for readability at small sizes
```

### Dual-Tone Icons
```
Primary layer:   Full opacity (stroke or fill)
Secondary layer: 10–20% opacity fill for depth
Use for:         Feature cards, onboarding, empty states (≥32px only)
```

---

## Color Rules

### Monochrome (Default)
- Icons inherit `currentColor` from their parent text
- This ensures automatic dark/light mode support
- One color only — no inline color variation

### Semantic Color
Apply color to communicate **meaning**, not aesthetics:
```
Destructive:   red-500 (#ef4444)    — delete, remove, error
Success:       green-500 (#22c55e)  — complete, verified, online
Warning:       amber-500 (#f59e0b)  — attention, expiring, degraded
Info:          blue-500 (#3b82f6)   — informational, link, selected
Neutral:       gray-500 (#6b7280)   — default, disabled, secondary
```

### Brand Accent
Use the product's primary brand color for:
- Active navigation items
- Primary action indicators
- Logo marks only

---

## Accessibility Requirements

1. **Minimum touch target:** 44×44px (iOS) / 48×48dp (Android) regardless of icon visual size
2. **Contrast ratio:** ≥3:1 against background (WCAG 2.1 Level AA for non-text)
3. **aria-label** on interactive icons without visible text labels
4. **aria-hidden="true"** on decorative icons that duplicate adjacent text
5. **Reduced motion:** Icon animations must respect `prefers-reduced-motion`
6. **Focus indicator:** Keyboard-focusable icons need visible focus ring (not just color change)

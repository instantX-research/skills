# Icon Systems & Resources Reference

## Tier 1 — Open Source Icon Libraries (Recommended)

### Lucide (lucide.dev)
- **Style:** Clean geometric outline, 1.5–2px stroke
- **Count:** 1500+ icons
- **Format:** SVG, React/Vue/Svelte components, Web Components
- **License:** ISC (permissive)
- **Best for:** Developer tools, SaaS, general-purpose
- **NPM:** `lucide-react`, `lucide-vue-next`, `lucide-svelte`
- **API:** `https://lucide.dev/api/icons` (JSON metadata)
- **Search URL:** `https://lucide.dev/icons/?search=QUERY`

### Phosphor Icons (phosphoricons.com)
- **Style:** 6 weights — thin/light/regular/bold/fill/duotone
- **Count:** 1248 icons × 6 weights
- **Format:** SVG, React/Vue/Flutter/Elm
- **License:** MIT
- **Best for:** Consumer apps, versatile (weight system adapts to any product)
- **NPM:** `@phosphor-icons/react`, `@phosphor-icons/vue`

### Heroicons (heroicons.com)
- **Style:** Outline (1.5px) and Solid variants
- **Count:** 300+ icons
- **Format:** SVG, React, Vue
- **License:** MIT
- **Best for:** Tailwind CSS projects (same team)
- **NPM:** `@heroicons/react`

### Tabler Icons (tabler.io/icons)
- **Style:** Consistent 2px stroke, rounded
- **Count:** 5000+ icons
- **Format:** SVG, React, Vue, Svelte, PNG, Webfont
- **License:** MIT
- **Best for:** Large projects needing comprehensive icon coverage
- **NPM:** `@tabler/icons-react`

### Radix Icons (icons.radix-ui.com)
- **Style:** 15×15 crisp minimal icons
- **Count:** 300+ icons
- **Format:** SVG, React
- **License:** MIT
- **Best for:** Radix UI / shadcn projects

---

## Tier 2 — Design System Icons

### SF Symbols (Apple)
- **Style:** Filled, multicolor, hierarchical
- **Count:** 5000+
- **Platform:** Apple only (licensing restriction)
- **Use:** Reference for metaphor conventions, not for web

### Material Symbols (Google)
- **Style:** Outlined/Rounded/Sharp × Fill toggle × Weight axis
- **Format:** Variable font, SVG, Android/iOS/Flutter
- **License:** Apache 2.0
- **NPM:** `@material-symbols/svg-400`
- **Best for:** Material Design systems, Android-first products

### Remix Icon (remixicon.com)
- **Style:** Neutral, line + fill variants
- **Count:** 2800+
- **License:** Apache 2.0
- **Best for:** General-purpose, Chinese tech products

---

## SVG Generation Approach

When no existing icon matches the query, generate custom SVG following these rules:

### Template Structure

Base template — adjust `stroke-width`, `stroke-linecap`, and `stroke-linejoin` per style archetype:

```svg
<svg xmlns="http://www.w3.org/2000/svg"
     width="24" height="24"
     viewBox="0 0 24 24"
     fill="none"
     stroke="currentColor"
     stroke-width="{STROKE}"
     stroke-linecap="{CAP}"
     stroke-linejoin="{JOIN}">
  <!-- icon paths here -->
</svg>
```

Style archetype values:
| Style     | STROKE | CAP   | JOIN  |
|-----------|--------|-------|-------|
| geometric | 1.5    | butt  | miter |
| rounded   | 2      | round | round |
| duotone   | 2      | round | round |
| thin      | 1.5    | round | round |
| filled    | (n/a — use fill="currentColor", no stroke) | — | — |
| organic   | 1.5–3  | round | round |

### Generation Guidelines
1. **Start with keyline** — fit the icon into a 20×20 active area (2px padding)
2. **Use simple geometry** — prefer `<circle>`, `<rect>`, `<line>`, `<polyline>` over complex `<path>`
3. **Minimize path commands** — a good icon usually has <50 path commands total
4. **Test optically** — squares appear larger than circles at the same dimension; scale circles up ~5%
5. **Align to pixel grid** — coordinates should be integers or .5 values
6. **Use currentColor** — never hardcode colors in the SVG

### SVG Optimization
After generating, optimize:
- Remove unnecessary attributes (default values)
- Combine overlapping paths where possible
- Remove empty groups
- Ensure viewBox is exactly `0 0 24 24`
- Strip editor metadata (Illustrator/Figma comments)

### PNG Export
For PNG export from SVG:
- Use `sharp` (Node.js) or `cairosvg` (Python) or `resvg` (Rust/CLI)
- Export at 1×, 2×, 3× for device pixel ratios
- Recommended sizes: 16, 20, 24, 32, 48, 64, 128, 256, 512px
- Use transparent background unless specifically requested otherwise

---

## Icon Search Strategy

When the user requests an icon, search in this order:

1. **Exact keyword match** — Search Lucide/Phosphor/Heroicons by name
2. **Semantic synonym** — e.g., "trash" → also try "delete", "bin", "remove"
3. **Category browse** — e.g., "finance" → search "dollar", "wallet", "credit-card", "bank", "receipt"
4. **Custom generation** — If no existing icon fits, generate a custom SVG following the style guide

### Common Icon Mappings

| Concept        | Recommended Icon    | Avoid               |
|----------------|--------------------|-----------------------|
| Dashboard      | layout-dashboard   | grid (too generic)    |
| Analytics      | bar-chart-2        | chart (ambiguous)     |
| Settings       | settings (gear)    | cog (archaic)         |
| Profile        | user               | person-circle         |
| Notifications  | bell               | notification (text)   |
| Search         | search             | magnifier             |
| Create/New     | plus               | create (text)         |
| Delete         | trash-2            | x (ambiguous)         |
| Edit           | pencil             | edit (text)           |
| Share          | share-2            | share (box-arrow)     |
| Download       | download           | save (floppy disk)    |
| Upload         | upload             | cloud-upload          |
| Filter         | filter             | funnel                |
| Sort           | arrow-up-down      | sort (text)           |
| Calendar       | calendar           | date (text)           |
| Message        | message-square     | chat (bubble)         |
| Email          | mail               | envelope              |
| Phone          | phone              | telephone             |
| Location       | map-pin            | location (dot)        |
| Lock/Security  | lock               | shield (overloaded)   |
| Refresh        | refresh-cw         | reload                |
| External link  | external-link      | arrow-up-right        |
| Copy           | copy               | clipboard             |
| Check/Done     | check              | checkmark             |
| Warning        | alert-triangle     | warning (text)        |
| Error          | alert-circle       | x-circle              |
| Info           | info               | i-circle              |
| Help           | help-circle        | question-mark         |

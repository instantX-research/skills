# icon-craft

A Claude Code skill for designing and generating production-grade icons — anti-emoji, optically consistent, theme-aware SVGs built on real design system principles.

## Installation

```bash
npx skills add https://github.com/instantX-research/skills --skill icon-craft
```

Or manually copy into your Claude Code skills directory:

```bash
cp -r skills/icon-craft ~/.claude/skills/
```

## What It Does

**icon-craft** acts as an icon design specialist — part visual designer, part SVG engineer. It enforces the 7 Laws of Product Icon Design, supports 6 style archetypes calibrated against Lucide, Phosphor, Heroicons, and SF Symbols, and produces pixel-aligned SVGs that use `currentColor` for automatic dark/light mode adaptation.

Core principle: **icons are visual verbs, not decoration.** Generic emoji (🔥📊✨💡🚀) are the Comic Sans of product design — they break consistency, lack theme support, and signal prototype quality. This skill eliminates them.

### Integration with frontend-ui

This skill works standalone or as the icon quality layer for `frontend-ui`:

```
┌─────────────────────┐
│   frontend-ui       │  Generates page / component
│   (design + code)   │  with Design DNA
└────────┬────────────┘
         │ detects icon-craft at runtime
         ▼
┌─────────────────────┐
│   icon-craft        │  Supplies design principles +
│   (icon layer)      │  generates matching SVG icons
└─────────────────────┘
```

| Scenario | Behavior |
|----------|----------|
| Both skills installed | `frontend-ui` auto-loads icon-craft's design knowledge; icon style matched to DNA archetype |
| Only `frontend-ui` installed | Falls back to built-in baseline icon rules (no emoji, `currentColor`, consistent stroke) |
| Only `icon-craft` installed | Fully functional standalone — principles + generation |

### Key Features

- **2 modes** — Load design principles only (Principles Mode), or find/generate icons on demand (Generation Mode).
- **6 style archetypes** — Geometric, Rounded, Duotone, Thin, Filled, Organic — each with locked stroke/cap/join/corner parameters.
- **Library-first search** — Searches Lucide, Phosphor, Heroicons, and Tabler before generating custom SVGs. No reinventing the wheel.
- **Custom SVG generation** — When no library match fits, generates from scratch following strict keyline, pixel-alignment, and complexity rules.
- **Batch set generation** — `--set` locks shared visual parameters across all icons and validates cross-icon consistency.
- **Multi-format export** — SVG (default), PNG at 1×/2×/3× density, or both.
- **Anti-emoji enforcement** — Zero tolerance for Unicode emoji as icon substitutes.
- **Theme-aware** — All icons use `currentColor` by default for automatic light/dark mode support.

## Usage

```
/icon-craft [--principles] [query] [--style <name>] [--size <px>] [--format <fmt>] [--set <n>] [--output <path>] [--color <hex>]
```

---

### Mode: Principles (`--principles`)

Load design theory, style specs, and the 7 Laws of Product Icon Design. No files generated.

```bash
# Full principles overview
/icon-craft --principles

# Focus on a specific style archetype
/icon-craft --principles --style rounded
```

---

### Mode: Generation (default)

Describe what icon you need and where it will be used. The skill searches existing libraries first, then generates custom SVGs if no good match exists.

```bash
# Single icon
/icon-craft "sidebar navigation settings icon"
/icon-craft "delete confirmation for destructive action" --style rounded

# Cohesive icon set
/icon-craft "navigation: home, search, notifications, profile, settings" --set 5 --style geometric
/icon-craft "e-commerce: cart, wishlist, orders, returns" --set 4

# With format and output options
/icon-craft "file upload progress indicator" --format both --output ./assets/icons
/icon-craft "subscription billing status" --format png --size 32

# Override color for semantic use
/icon-craft "error alert icon" --color "#ef4444"
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `<query>` | — | **Required (Generation Mode).** Natural language description of the icon. Include both the concept ("shopping cart") and the context ("checkout page toolbar") for best results. |
| `--principles` | — | Switch to Principles Mode. Outputs design theory, the 7 Laws, style archetype specs, and visual specifications. No icons generated. Combine with `--style` to focus on one archetype. |
| `--style <name>` | `geometric` | Icon style archetype. Controls stroke width, corner radius, line cap/join, and visual personality. See "Style Archetypes" below. |
| `--size <px>` | `24` | Base icon size in pixels. The icon is designed at this size with proportional padding (2px at 24px → 20×20 active area). Common values: 16, 20, 24, 32, 48. |
| `--format <fmt>` | `svg` | Output file format. `svg` — optimized SVG with `currentColor`. `png` — rasterized at 1×, 2×, 3× pixel density (e.g., 24px base → 24/48/72px files). `both` — SVG + all PNG sizes. |
| `--set <count>` | — | Batch-generate N related icons as a cohesive set. Locks shared visual parameters (stroke width, corner radius, cap/join) across all icons and validates cross-icon consistency. Query should list concepts comma-separated. |
| `--output <path>` | `./icons/` | Directory to save generated files. Created automatically if it doesn't exist. |
| `--color <color>` | `currentColor` | Override stroke/fill color. Default `currentColor` inherits from parent CSS (recommended for theme compatibility). Override only for semantic colors like `"#ef4444"` (destructive) or `"#22c55e"` (success). |

## Style Archetypes

| Style | Stroke | Cap / Join | Corners | Feel | Reference Products |
|-------|--------|------------|---------|------|--------------------|
| `geometric` | 1.5px | butt / miter | 0–1px sharp | Precise, engineering-forward | Linear, Vercel, Stripe |
| `rounded` | 2px | round / round | 2px radius | Approachable, warm | Phosphor, Heroicons |
| `duotone` | 2px | round / round | 1–2px | Polished, layered depth | Ant Design, Phosphor Duotone |
| `thin` | 1.5px | round / round | 1px | Quiet, editorial | Feather, Tabler |
| `filled` | — (solid) | — | 1–2px | Bold, mobile-native | SF Symbols, Material Filled |
| `organic` | 1–3px variable | round / round | irregular | Playful, hand-drawn | Custom / indie |

### Style ↔ frontend-ui Archetype Mapping

When used with `frontend-ui`, icon style is automatically matched to the Design DNA:

| frontend-ui Archetype | Recommended icon-craft Style |
|-----------------------|------------------------------|
| Obsidian Precision | `geometric` |
| Warm Editorial | `thin` |
| Chromatic Confidence | `rounded` |
| Terminal Glass | `geometric` |
| Luxury Silence | `thin` |
| Soft Structuralism | `rounded` or `duotone` |

## Generation Workflow

```
Query
  │
  ├─ Step 1: Parse concept, context, style, size, format
  ├─ Step 2: Load design knowledge (principles + style specs)
  ├─ Step 3: Search icon libraries (Lucide → Phosphor → Heroicons → Tabler)
  │            ├── Match found → Present with attribution → Save
  │            └── No match   → Step 4
  ├─ Step 4: Generate custom SVG (keyline → primary form → detail → optical adjust → validate)
  ├─ Step 5: Preview + save (SVG/PNG to output directory)
  └─ Step 6: Set consistency check (if --set flag)
```

## Icon Categories

Reference categories for `--set` generation and common UI scenarios:

| Category | Typical UI Location |
|----------|---------------------|
| navigation | Sidebar, tab bar, bottom nav |
| actions | Toolbars, context menus, buttons |
| ecommerce | Cart, checkout, billing pages |
| features | Landing page feature sections |
| status | Toast/alert components, form feedback |
| media | Media players, upload interfaces |
| security | Auth flows, settings pages |
| file | File managers, document interfaces |
| social | Contact sections, sharing widgets |
| data | Dashboard layouts, analytics pages |

## File Layout

```
icon-craft/
├── SKILL.md                                    # Router — modes, generation pipeline, quality checklist
├── README.md
└── knowledge/
    ├── design/
    │   ├── icon-principles.md                  # 7 Laws of Product Icon Design, visual specs, accessibility
    │   └── icon-styles.md                      # 6 style archetypes with SVG traits and decision matrix
    └── references/
        └── icon-systems.md                     # Icon library catalog, SVG generation templates, common mappings
```

| File | Loaded at |
|------|-----------|
| `SKILL.md` | Always (router + mode detection) |
| `knowledge/design/icon-principles.md` | Both modes — core design rules |
| `knowledge/design/icon-styles.md` | Both modes — style archetype specs |
| `knowledge/references/icon-systems.md` | Generation Mode — library search + SVG templates |

## Credits

Created by [Haofan Wang](https://haofanwang.github.io/) with Claude Code.

## License

MIT — Use it, modify it, share it.

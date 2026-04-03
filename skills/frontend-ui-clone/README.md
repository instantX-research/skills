# frontend-ui-clone

A Claude Code skill that clones any website into a pixel-perfect, self-contained HTML file.

## Installation

```bash
npx skills install frontend-ui-clone
```

Or manually copy into your Claude Code skills directory:

```bash
cp -r skills/frontend-ui-clone ~/.claude/skills/
```

## What It Does

Uses Playwright to render the target page in a real Chromium browser, then directly extracts the rendered DOM + all computed CSS. No manual rewriting — the original DOM and original CSS are always more accurate than any reconstruction.

```
URL ──► Playwright render ──► Extract DOM + CSS ──► Assemble .html ──► Screenshot compare ──► Fix & verify
```

## Usage

```
/frontend-ui-clone https://example.com
```

Or ask naturally:

- "Clone this site: https://example.com"
- "Make a pixel-perfect copy of https://example.com"
- "Replicate this URL as a single HTML file"

## Strategy Levels

The skill auto-detects available tools and selects the best extraction strategy:

| Level | Method | Fidelity | When |
|-------|--------|----------|------|
| **1** | Playwright DOM + CSS | ~97% | Default for most sites |
| **1a** | Hybrid (CSS + targeted overrides) | ~90% | Tailwind `important:true` sites |
| **1b** | Targeted style bake | ~80% | When 1a still fails |
| **2** | Firecrawl + CSS download | ~85% | No Playwright |
| **3** | gstack/browse + CSS | ~80% | No Playwright or Firecrawl |
| **4** | WebFetch + reconstruction | ~70% | HTTP fetch only |
| **5** | WebSearch research | ~50% | Last resort |

Auto-escalation: Level 1 → 1a → 1b happens automatically if the hero section is blank after extraction.

## Key Features

- **Zero creative liberty** — reproduces exactly what exists, never redesigns
- **Self-contained output** — single `.html` file, no external dependencies
- **Automatic CSS custom property extraction** — captures all `:root` variables (Tailwind v4, shadcn/ui)
- **Gradient text preservation** — bakes `background-clip: text` gradients as inline styles
- **Inner scroll container detection** — handles SPA layouts with `fixed inset-0` wrappers
- **CSS animation override** — forces scroll-reveal animations to their visible end state
- **Invisible overlay removal** — detects and removes SPA editor/chat panels covering content
- **Lazy image fix** — strips `loading="lazy"`, fixes `data-lazy-src`, resolves `/_next/image` URLs
- **Font preservation** — extracts `<link>` tags for Google Fonts and font preloads
- **Screenshot comparison** — Playwright-based visual diff with iterative fixing

## Requirements

Best results with **Playwright** installed:

```bash
pip install playwright
playwright install chromium
```

Falls back gracefully to Firecrawl, gstack/browse, WebFetch, or WebSearch if Playwright is unavailable.

## Output

Files are written to `test_outputs/clone-[domain].html`:

```
test_outputs/
  clone-lovable.html      # 816 KB — lovable.dev clone
  clone-wondering.html    # 329 KB — wondering.app clone
```

## Known Limitations

- **JS-rendered-on-scroll content** — elements that only exist in the DOM after JS scroll interaction cannot be captured in a static clone
- **Interactive components** — accordions, tabs, modals render in their extraction-time state
- **Cross-origin iframes** — blank from `file://`, work when deployed to a web server
- **Responsive breakpoints** — Level 1b (style bake) loses responsive CSS; Level 1/1a preserve it
- **Typewriter animations** — captured as static text unless prompts are detected and injected

## Lessons Learned

The skill encodes 30 lessons from real cloning sessions in its Key Lessons section, including:

- `networkidle` timeout fallback for SPA/Next.js sites
- Large invisible overlay panel detection and removal
- CSS custom properties as the #1 fidelity killer
- `section { height: auto }` killing hero `min-h-screen`
- `@import` rule ordering in `<style>` blocks
- Inner scroll container scrolling for animation triggers
- CSS `animate-*` classes stuck at initial state

## Credits

Created by [Haofan Wang](https://haofanwang.github.io/) with Claude Code.

## License

MIT — Use it, modify it, share it.

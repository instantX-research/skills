# Code Generation Standards — Extended

**When to load:** At Phase 4 start when building full pages (≥ 3 sections) OR VISUAL_DENSITY ≥ 6 OR component count ≥ 6. Supplements `code-standards-core.md` (always-loaded).

---

## Responsive design system — fluid-first, no arbitrary breakpoints

### Fluid typography with clamp()
```css
/* clamp(min, preferred, max) — scales linearly between viewport widths */
:root {
  --text-sm:   clamp(0.75rem,  0.7rem + 0.25vw,  0.875rem);  /* 12–14px */
  --text-base: clamp(0.9375rem, 0.875rem + 0.3vw, 1rem);      /* 15–16px */
  --text-lg:   clamp(1.0625rem, 1rem + 0.3vw,    1.125rem);   /* 17–18px */
  --text-xl:   clamp(1.25rem,  1.125rem + 0.6vw,  1.5rem);    /* 20–24px */
  --text-2xl:  clamp(1.5rem,   1.25rem + 1.3vw,   2rem);      /* 24–32px */
  --text-3xl:  clamp(1.875rem, 1.5rem + 2vw,      2.5rem);    /* 30–40px */
  --text-4xl:  clamp(2.25rem,  1.75rem + 2.5vw,   3rem);      /* 36–48px */
  --text-5xl:  clamp(2.5rem,   1.875rem + 3.5vw,  4rem);      /* 40–64px */
}

/* Usage: */
h1 { font-size: var(--text-5xl); }
body { font-size: var(--text-base); }
```

### Viewport units — use dvh, not vh
```css
/* vh breaks on mobile browsers (Safari, Chrome Android) — address bar affects it */
/* Always use dvh (dynamic viewport height) for full-height layouts */

.hero { min-height: 100dvh; }          /* ✓ correct */
.hero { min-height: 100vh; }           /* ✗ breaks on mobile with address bar */

/* dvh — dynamic (shrinks/grows with browser chrome)
   svh — small (worst case, address bar fully shown)
   lvh — large (best case, address bar hidden)     */

/* Fallback for older browsers: */
.hero {
  min-height: 100vh;      /* fallback */
  min-height: 100dvh;     /* override for modern browsers */
}
```

### Container queries — component-level responsiveness
```css
/* Define a containment context on the wrapper */
.card-grid { container-type: inline-size; container-name: grid; }

/* Component responds to its container width, not the viewport */
@container grid (min-width: 640px) {
  .card { display: grid; grid-template-columns: auto 1fr; }
}

@container grid (min-width: 900px) {
  .card { grid-template-columns: 200px 1fr; }
}
```

```tsx
/* React: container queries with Tailwind (requires @tailwindcss/container-queries) */
<div className="@container">
  <div className="flex flex-col @md:flex-row @lg:gap-8">
    {/* Layout adapts to container, not viewport */}
  </div>
</div>
```

### Breakpoint strategy — mobile-first, semantic names
```css
/* Standard breakpoints — name by content need, not device */
/* xs: 0–479px      → single-column, stack everything */
/* sm: 480–767px    → small phone landscape, 2-col possible */
/* md: 768–1023px   → tablet portrait, sidebar optional */
/* lg: 1024–1279px  → tablet landscape / laptop */
/* xl: 1280–1535px  → desktop */
/* 2xl: 1536px+     → large desktop, max container width applies */

/* Mobile-first — start with the simplest layout, add complexity at larger sizes */
.layout {
  display: block;                        /* mobile: stacked */
}
@media (min-width: 768px) {
  .layout { display: grid; grid-template-columns: 240px 1fr; }  /* tablet+ */
}
@media (min-width: 1024px) {
  .layout { grid-template-columns: 280px 1fr 320px; }           /* desktop */
}

/* NEVER design desktop-first and squish with max-width queries — it creates unmaintainable code */
```

### Mobile-specific layout patterns
```css
/* Bottom navigation — safe area inset for iPhone home bar */
.bottom-nav {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  padding-bottom: env(safe-area-inset-bottom);  /* iPhone home indicator */
  background: var(--color-surface);
  border-top: 1px solid var(--color-border);
}

/* Bottom sheet — slides up from bottom edge */
.bottom-sheet {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  max-height: 92dvh;             /* leave 8% visible to signal dismissal */
  border-radius: 20px 20px 0 0;
  overflow-y: auto;
  overscroll-behavior: contain;  /* prevent body scroll when sheet is open */
  -webkit-overflow-scrolling: touch;
  padding-bottom: env(safe-area-inset-bottom);
}

/* Touch scroll momentum on iOS */
.scrollable { overflow-y: auto; -webkit-overflow-scrolling: touch; }
```

---

## Dark mode — implementation patterns

### CSS custom property switching (recommended)
```css
/* Define all tokens in :root (light mode default) */
:root {
  --color-bg:           #ffffff;
  --color-bg-subtle:    #f9fafb;
  --color-surface:      #ffffff;
  --color-surface-raised: #f3f4f6;
  --color-text-primary: #111827;
  --color-text-secondary: #6b7280;
  --color-border:       #e5e7eb;
  --color-accent:       #2563eb;
}

/* Dark mode — override tokens only, no other CSS changes needed */
[data-theme='dark'] {
  --color-bg:           #08090a;
  --color-bg-subtle:    #111316;
  --color-surface:      #111316;
  --color-surface-raised: #1c1d21;
  --color-text-primary: #f0f0f2;
  --color-text-secondary: #9094a0;
  --color-border:       rgba(255, 255, 255, 0.08);
  --color-accent:       #4f7cf7;  /* desaturated vs light mode accent */
}

/* System preference fallback (no JS needed) */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme='light']) {
    --color-bg: #08090a;
    /* ... same overrides ... */
  }
}
```

### Next.js / React ThemeProvider pattern
```tsx
// app/providers.tsx
'use client'
import { createContext, useContext, useEffect, useState } from 'react'

type Theme = 'light' | 'dark' | 'system'

const ThemeContext = createContext<{ theme: Theme; setTheme: (t: Theme) => void }>({
  theme: 'system',
  setTheme: () => {},
})

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>('system')

  useEffect(() => {
    const stored = localStorage.getItem('theme') as Theme | null
    if (stored) setTheme(stored)
  }, [])

  useEffect(() => {
    const root = document.documentElement
    const isDark = theme === 'dark' ||
      (theme === 'system' && matchMedia('(prefers-color-scheme: dark)').matches)
    root.setAttribute('data-theme', isDark ? 'dark' : 'light')
    localStorage.setItem('theme', theme)
  }, [theme])

  return <ThemeContext.Provider value={{ theme, setTheme }}>{children}</ThemeContext.Provider>
}

export const useTheme = () => useContext(ThemeContext)
```

### Dark mode image treatment
```css
/* Reduce harsh brightness on images in dark mode */
[data-theme='dark'] img:not([src*='.svg']) {
  filter: brightness(0.85) contrast(1.05);
}

/* SVG icons: use currentColor instead of hardcoded fills */
/* This lets them inherit the text color automatically */
.icon { color: var(--color-text-secondary); }
.icon svg { fill: currentColor; }  /* or stroke: currentColor */
```

---

## ARIA quick reference — accessible interactive patterns

### Icon-only buttons (always need a label)
```tsx
<button aria-label="Close dialog" onClick={onClose}>
  <XIcon aria-hidden="true" />  {/* hide decorative icon from screen readers */}
</button>
```

### Disclosure (expand/collapse)
```tsx
<button
  aria-expanded={isOpen}
  aria-controls="panel-id"
  onClick={() => setIsOpen(!isOpen)}
>
  Advanced options
  <ChevronIcon aria-hidden="true" className={isOpen ? 'rotate-180' : ''} />
</button>
<div id="panel-id" hidden={!isOpen}>
  {/* content */}
</div>
```

### Live regions (async status updates)
```tsx
{/* For status messages that appear dynamically */}
<div aria-live="polite" aria-atomic="true" className="sr-only">
  {statusMessage}  {/* e.g. "3 files uploaded", "Save successful" */}
</div>

{/* For urgent error messages */}
<div role="alert">
  {errorMessage}
</div>
```

### Modal focus trap pattern
```tsx
// On modal open: move focus to modal; on close: return focus to trigger
useEffect(() => {
  if (isOpen) {
    const firstFocusable = modalRef.current?.querySelector<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
    firstFocusable?.focus()
    previousFocus.current = document.activeElement as HTMLElement
  } else {
    previousFocus.current?.focus()  // restore focus to trigger button
  }
}, [isOpen])

// Trap Tab/Shift+Tab inside modal
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Escape') onClose()
  // Tab trapping logic...
}
```

### Skip link (required for keyboard users)
```html
<!-- First element in <body> — visually hidden until focused -->
<a href="#main-content" class="skip-link">Skip to main content</a>
<style>
  .skip-link {
    position: absolute; top: -100%; left: 16px;
    padding: 8px 16px;
    background: var(--color-accent); color: white;
    border-radius: 0 0 var(--radius-md) var(--radius-md);
    z-index: 9999;
  }
  .skip-link:focus { top: 0; }
</style>
<main id="main-content">...</main>
```

### Roving tabindex (radio groups, toolbars, tabs)
```tsx
// Only one item in the group is in the tab order at a time
// Arrow keys move focus within the group
const handleKeyDown = (e: KeyboardEvent, index: number) => {
  if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
    e.preventDefault()
    const next = (index + 1) % items.length
    setFocusedIndex(next)
    itemRefs.current[next]?.focus()
  }
  if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
    e.preventDefault()
    const prev = (index - 1 + items.length) % items.length
    setFocusedIndex(prev)
    itemRefs.current[prev]?.focus()
  }
}

<div role="radiogroup" aria-labelledby="group-label">
  {items.map((item, i) => (
    <button
      key={item.id}
      role="radio"
      aria-checked={selected === item.id}
      tabIndex={focusedIndex === i ? 0 : -1}
      onKeyDown={(e) => handleKeyDown(e, i)}
    >
      {item.label}
    </button>
  ))}
</div>
```

---

## Image & media patterns — avoid layout shift, maintain contrast

### Aspect-ratio containers (prevent CLS — Cumulative Layout Shift)
```css
/* Lock aspect ratio so the space is reserved before the image loads */
.aspect-video  { aspect-ratio: 16 / 9; }
.aspect-square { aspect-ratio: 1 / 1; }
.aspect-card   { aspect-ratio: 4 / 3; }
.aspect-hero   { aspect-ratio: 21 / 9; }

/* Always pair with object-fit on the media element */
.aspect-video img,
.aspect-video video {
  width: 100%;
  height: 100%;
  object-fit: cover;     /* crop to fill — for editorial images */
  /* object-fit: contain; — letterbox — for product/logo images */
}
```

### Image + text overlay — minimum 4.5:1 contrast
```html
<!-- Always add a contrast scrim when placing text over images -->
<div class="media-card">
  <img src="..." alt="..." class="media-card__image" />
  <div class="media-card__overlay">       <!-- the scrim -->
    <h2 class="media-card__title">...</h2>
  </div>
</div>
```
```css
.media-card { position: relative; overflow: hidden; border-radius: var(--radius-lg); }
.media-card__image { width: 100%; height: 100%; object-fit: cover; display: block; }

/* Gradient scrim — more natural than solid overlay */
.media-card__overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to top,
    rgba(0, 0, 0, 0.72) 0%,    /* bottom: strong — where text is */
    rgba(0, 0, 0, 0.24) 50%,
    rgba(0, 0, 0, 0.00) 100%   /* top: transparent */
  );
  display: flex;
  align-items: flex-end;
  padding: var(--space-6);
}
.media-card__title { color: #ffffff; /* #fff on 72% black = 10:1 contrast — passes WCAG AAA */ }
```

### Next.js `next/image` pattern
```tsx
import Image from 'next/image'

// Hero image (above the fold) — eager load, no lazy
<Image
  src="/hero.jpg"
  alt="[descriptive alt text — describe the content, not 'hero image']"
  fill                    // fills the nearest positioned parent
  priority                // LCP image: preload immediately, no lazy
  sizes="100vw"
  className="object-cover"
/>

// Card image (below the fold) — lazy load
<div className="relative aspect-video">
  <Image
    src={post.coverImage}
    alt={post.title}        // meaningful alt: reuse the content title
    fill
    sizes="(min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw"
    className="object-cover rounded-[var(--radius-md)]"
  />
</div>

// Avatar / known-size image
<Image
  src={user.avatar}
  alt={`${user.name}'s avatar`}
  width={40}
  height={40}
  className="rounded-full"
/>
```

**`sizes` attribute rules:**
- Always set `sizes` — without it Next.js generates a huge image
- Approximate the rendered width at each breakpoint
- For full-width images: `sizes="100vw"`
- For 1/3-width grid: `sizes="(min-width: 1024px) 33vw, 100vw"`

### Font loading — `font-display` strategy
```css
/* font-display: swap — text visible immediately with fallback font, swaps when loaded */
/* Use for: body text, UI text — legibility is critical */
@font-face {
  font-family: 'Inter Variable';
  src: url('/fonts/inter-variable.woff2') format('woff2');
  font-display: swap;
}

/* font-display: optional — browser uses cached font or skips entirely (no swap flash) */
/* Use for: display/heading fonts where layout shift is more damaging than delay */
@font-face {
  font-family: 'Cabinet Grotesk';
  src: url('/fonts/cabinet-grotesk.woff2') format('woff2');
  font-display: optional;
}
```

**Font loading hierarchy:**
1. System font stack first (no FOUT, instant)
2. Variable fonts preferred (one file, all weights: `woff2` with `format('woff2')`)
3. Preload critical fonts in `<head>`: `<link rel="preload" as="font" href="/fonts/inter.woff2" crossorigin>`
4. Self-host fonts — Google Fonts adds a DNS lookup + render-blocking request

---

## Component State Matrix — all 8 states required for every interactive component

Every button, input, card, link, toggle, and interactive element must implement all 8 states. Missing states = P0 in Phase 4.5 audit.

| # | State | When | CSS / Implementation |
|---|-------|------|----------------------|
| 1 | **Default** | Element at rest, no interaction | Base styles — the foundation |
| 2 | **Hover** | Cursor over element (pointer device) | `opacity` shift, `background` lighten/darken, `border` change — never hue shift on restrained palette |
| 3 | **Active / Pressed** | Mouse/touch held down | `transform: scale(0.98)` + slight darkening; `transition-duration: 50ms` for snap feel |
| 4 | **Focus-visible** | Keyboard navigation focus | `outline: 2px solid var(--color-accent); outline-offset: 2px` — never `outline: none` without replacement |
| 5 | **Disabled** | Not interactive, action unavailable | `opacity: 0.4; cursor: not-allowed; pointer-events: none` — do NOT use grey color alone |
| 6 | **Loading** | Async action in progress | Skeleton screen or spinner; preserve element dimensions; disable further interaction |
| 7 | **Error** | Action failed or invalid input | Inline message below element; `--color-error` border; never `window.alert()` |
| 8 | **Success / Complete** | Action confirmed | Brief confirmation state (checkmark, color shift); auto-dismiss after 2–3s or persist for destructive actions |

```css
/* Complete button state implementation */
.btn {
  /* 1. Default */
  background: var(--color-accent);
  color: white;
  transition: background var(--duration-fast) var(--ease-out),
              transform var(--duration-fast) var(--ease-out),
              opacity var(--duration-fast) var(--ease-out);
}

/* 2. Hover */
.btn:hover { background: var(--color-accent-hover); }

/* 3. Active */
.btn:active { transform: scale(0.98); }

/* 4. Focus-visible */
.btn:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

/* 5. Disabled */
.btn:disabled,
.btn[aria-disabled="true"] {
  opacity: 0.4;
  cursor: not-allowed;
  pointer-events: none;
}

/* 6. Loading — add .is-loading class via JS */
.btn.is-loading {
  color: transparent; /* hide text */
  pointer-events: none;
  position: relative;
}
.btn.is-loading::after {
  content: '';
  position: absolute;
  inset: 50% auto auto 50%;
  translate: -50% -50%;
  width: 1em; height: 1em;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

/* 7. Error — applied via aria-invalid or .is-error class */
.input[aria-invalid="true"] {
  border-color: var(--color-error);
  outline-color: var(--color-error);
}

/* 8. Success */
.btn.is-success {
  background: var(--color-success);
  /* auto-remove .is-success after 2000ms via JS */
}
```

**Checklist shorthand:** Default ✓ · Hover ✓ · Active ✓ · Focus ✓ · Disabled ✓ · Loading ✓ · Error ✓ · Success ✓

---

## SEO & meta tags

Every public-facing page must include the following `<head>` block. Omit for internal app routes (dashboards, settings) but always include for landing pages, homepages, and marketing pages.

```html
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Product Name — Short tagline (50–60 chars)</title>
  <meta name="description" content="One clear sentence about what the product does and who it's for. 150–160 characters.">

  <!-- Open Graph (controls how the page looks when shared on Slack, Twitter, LinkedIn) -->
  <meta property="og:type" content="website">
  <meta property="og:title" content="Product Name — Short tagline">
  <meta property="og:description" content="Same as meta description, or slightly more social-friendly.">
  <meta property="og:image" content="https://example.com/og-image.png"> <!-- 1200×630px -->
  <meta property="og:url" content="https://example.com/">

  <!-- Twitter card (used by X/Twitter specifically) -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Product Name — Short tagline">
  <meta name="twitter:description" content="Same as og:description">
  <meta name="twitter:image" content="https://example.com/og-image.png">

  <!-- Favicon: inline SVG data URI — works without any asset file -->
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⬡</text></svg>">
</head>
```

**Title formula:** `[Product Name] — [Value proposition]` (50–60 chars max)

**Description rules:**
- Lead with the benefit, not the feature: "Design faster" not "A design tool that..."
- Include the primary keyword naturally
- 150–160 characters — truncated beyond that in search results
- Never duplicate the title

**OG image:** 1200×630px. Can be a simple branded card (product name + logo on brand background).

**Inline SVG favicon patterns:**
```html
<!-- Single letter (most common for apps) -->
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='20' fill='%23e05a3a'/><text x='50' y='72' text-anchor='middle' font-size='64' font-family='sans-serif' font-weight='700' fill='white'>M</text></svg>">

<!-- Geometric shape (minimal brands) -->
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='40' fill='%235e6ad2'/></svg>">
```
Note: `#` must be encoded as `%23` inside a data URI attribute.

---

## SVG vs. Icon Library — Decision Tree

Apply during Phase 4 when adding icons, illustrations, or brand marks.

```
Is this element a brand mark, logo, or unique illustration?
  YES → Custom SVG (inline or as component)
  NO  ↓

Is this a functional UI icon (button, input, alert, nav, status)?
  YES → Icon library (Phosphor or Heroicons)
  NO  ↓

Is this a decorative or ambient graphic?
  YES → CSS shape, pseudo-element, or SVG pattern — not a library icon
```

### Rules

**Custom SVG — use for:**
- Logo / wordmark / brand symbol
- Unique product illustration or mascot
- Custom chart / diagram / infographic element
- Decorative hero graphic specific to this design

**Icon library (Phosphor or Heroicons) — use for:**
- Navigation icons (home, search, settings, menu)
- Action icons (edit, delete, copy, share, download)
- Status indicators (check, warning, error, info)
- Form field icons (calendar, eye, lock, mail)

**Per-page budget:** Max 2–3 custom SVGs per page. Everything else from one library. Do not mix Phosphor and Heroicons on the same project.

**Technical rules:**
- Icon library icons: always `aria-hidden="true"` when decorative; `aria-label` on parent button
- Custom SVGs: use `currentColor` for fill/stroke so they respond to text colour tokens
- Never hardcode `fill="#000000"` — always `fill="currentColor"` or a CSS variable

```tsx
/* Correct: currentColor responds to theme */
<svg aria-hidden="true" fill="currentColor" viewBox="0 0 24 24">
  <path d="..." />
</svg>

/* Correct: icon-only button with accessible label */
<button aria-label="Copy to clipboard">
  <ClipboardIcon aria-hidden="true" className="w-4 h-4" />
</button>
```

---

## Perpetual animation isolation (React / Next.js)

**Rule:** Any animation that loops indefinitely — spinning loaders, pulsing indicators, floating particles, ambient motion — must live in its own `'use client'` component, isolated from the surrounding Server Component tree.

**Why:** Perpetual animations require client-side JS to run. If they sit inside a Server Component, Next.js must hydrate the entire subtree, increasing TTI and blocking streaming. Isolation keeps the hydration boundary tight.

```tsx
// ❌ Wrong — perpetual animation inside a Server Component layout
export default function HeroSection() {
  return (
    <section>
      <h1>Welcome</h1>
      <div className="animate-spin">...</div>  {/* forces client hydration of whole section */}
    </section>
  )
}

// ✅ Correct — isolate into its own Client Component
// components/SpinnerOrb.tsx
'use client'
export function SpinnerOrb() {
  return <div className="animate-spin rounded-full w-8 h-8 border-2 border-accent" />
}

// Then use it in the Server Component — only SpinnerOrb hydrates
export default function HeroSection() {
  return (
    <section>
      <h1>Welcome</h1>
      <SpinnerOrb />
    </section>
  )
}
```

**What counts as "perpetual":**
- `animation-iteration-count: infinite` (CSS)
- Framer Motion `repeat: Infinity`
- `setInterval` / `requestAnimationFrame` loops
- Lottie / Rive animations that loop

**What does NOT need isolation:**
- One-shot entrance animations (fade-in on mount, slide-up on scroll)
- Hover/active transitions (CSS-only, no JS required)
- Framer Motion `whileHover` / `whileTap` (event-driven, not perpetual)

# Code Generation Standards — Core

**When to load:** At Phase 4 start — always. For responsive design, dark mode, ARIA patterns, image handling, component state matrix, SEO, SVG rules, and animation isolation, load `code-standards-extended.md` when building full pages (≥ 3 sections) or VISUAL_DENSITY ≥ 6.

---

## CSS custom properties for all design tokens — always, even with Tailwind

```css
:root {
  /* Colors */
  --color-bg:           #ffffff;
  --color-bg-subtle:    #f9fafb;
  --color-surface:      #ffffff;
  --color-surface-raised: #f3f4f6;
  --color-text-primary: #111827;
  --color-text-secondary: #6b7280;
  --color-text-tertiary: #9ca3af;
  --color-border:       #e5e7eb;
  --color-border-strong: #d1d5db;
  --color-accent:       #2563eb;
  --color-accent-hover: #1d4ed8;

  /* Typography */
  --font-sans: 'Inter Variable', system-ui, sans-serif;
  --font-mono: 'Geist Mono', 'JetBrains Mono', monospace;

  /* Spacing */
  --space-1: 4px;  --space-2: 8px;  --space-3: 12px; --space-4: 16px;
  --space-5: 20px; --space-6: 24px; --space-8: 32px; --space-10: 40px;
  --space-12: 48px; --space-16: 64px; --space-20: 80px; --space-24: 96px;

  /* Radius */
  --radius-sm: 4px; --radius-md: 8px; --radius-lg: 12px; --radius-xl: 20px;

  /* Shadow */
  --shadow-xs: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
  --shadow-md: 0 4px 16px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04);
  --shadow-lg: 0 20px 40px rgba(0,0,0,0.12), 0 4px 8px rgba(0,0,0,0.06);

  /* Motion */
  --duration-fast: 150ms;
  --duration-base: 200ms;
  --duration-slow: 300ms;
  --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
}
```

## Stack-based layout (Every Layout methodology)

```css
/* Vertical rhythm without breakpoints */
.stack > * + * { margin-block-start: var(--stack-space, var(--space-4)); }

/* Centered content container */
.container {
  width: 100%;
  max-inline-size: 1280px;
  margin-inline: auto;
  padding-inline: var(--space-6);
}

/* Intrinsic responsive grid — no media queries needed */
.auto-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(280px, 100%), 1fr));
  gap: var(--space-6);
}
```

## Semantic HTML — always

```html
<body>
  <header role="banner">   <!-- site header -->
  <nav aria-label="main">  <!-- navigation -->
  <main>                   <!-- page content -->
    <article>              <!-- self-contained content -->
    <section aria-labelledby="...">  <!-- thematic section -->
    <aside>                <!-- supplementary content -->
  <footer role="contentinfo">  <!-- site footer -->
```

## Tailwind + React pattern

```tsx
import { cn } from '@/lib/utils'

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  children: React.ReactNode
  className?: string
}

const variants = {
  primary:   'bg-[var(--color-accent)] text-white hover:bg-[var(--color-accent-hover)]',
  secondary: 'bg-transparent border border-[var(--color-border)] hover:bg-[var(--color-bg-subtle)]',
  ghost:     'bg-transparent hover:bg-[var(--color-bg-subtle)]',
  danger:    'bg-red-600 text-white hover:bg-red-700',
}
const sizes = {
  sm: 'h-8 px-3 text-sm',
  md: 'h-10 px-4 text-sm font-medium',
  lg: 'h-12 px-6 text-base font-medium',
}

export function Button({ variant = 'primary', size = 'md', children, className }: ButtonProps) {
  return (
    <button className={cn(
      'inline-flex items-center justify-center rounded-[var(--radius-md)]',
      'transition-all duration-[var(--duration-fast)] ease-out',
      'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-accent)]',
      'disabled:opacity-40 disabled:cursor-not-allowed',
      variants[variant], sizes[size], className
    )}>
      {children}
    </button>
  )
}
```

## Output format by tech stack

- Next.js + Tailwind + TypeScript: JSX/TSX with Tailwind utilities + CSS custom properties in globals.css
- React + plain CSS: JSX + CSS Modules `.module.css`
- HTML/CSS only: semantic HTML5 + CSS custom properties + no framework dependency
- Vue/Nuxt: `.vue` SFC with `<style scoped>`
- Svelte/SvelteKit: `.svelte` SFC

---

## Pre-ship checklist

**When to verify:** Phase 4.5 Round 3, after all P0/P1 fixes. Every item must pass before showing the Design Report.

**Ship gate:** P0 = 0 AND P1 = 0 AND P2 ≤ 2 → show Design Report. P2 ≥ 3 → fix worst offenders until ≤ 2 remain. P3 items are always deferred.

### Visual craft
- [ ] `P1` No banned typography: Inter without customization is not acceptable — customize or pair
- [ ] `P1` No banned colors: pure `#000000` bg, pure `#ffffff` bg, oversaturated AI purple/blue gradient
- [ ] `P2` No equal-weight 3-column feature grid if DESIGN_VARIANCE ≥ 5
- [ ] `P2` Heading tracking is negative (or explicitly justified)
- [ ] `P1` No arbitrary pixel values (23px, 17px, 37px) — must be on 4/8px grid
- [ ] `P1` GPU-safe animations: use `transform` and `opacity` for all motion; `backdrop-filter` is permitted as a static or transition property (Archetype D requires it) but must not drive animation loops
- [ ] `P2` Icon set: Phosphor, Heroicons, or custom SVGs — not Lucide/Feather as sole choice

### Interaction integrity
- [ ] `P0` All 8 component states for every interactive component
- [ ] `P0` Every icon-only button has `aria-label` and tooltip
- [ ] `P0` Destructive actions have confirmation — no single-click deletes
- [ ] `P1` Async actions show loading feedback

### Responsive & mobile
- [ ] `P1` Full-height layouts use `100dvh` not `100vh`
- [ ] `P2` Marketing/landing font sizes use `clamp()` fluid scale
- [ ] `P0` Touch targets ≥ 44×44px
- [ ] `P1` Fixed bottom UI uses `env(safe-area-inset-bottom)`

### Accessibility
- [ ] `P0` Dynamic content uses `aria-live="polite"` or `role="alert"`
- [ ] `P0` No `outline: none` without custom focus ring
- [ ] `P1` All non-essential animations in `@media (prefers-reduced-motion: no-preference)`
- [ ] `P1` Screen reader focus order matches visual reading order

### Performance
- [ ] `P2` Images are WebP or AVIF with explicit `width` and `height`
- [ ] `P2` Below-fold images have `loading="lazy"`

### Content
- [ ] `P1` No Lorem ipsum — all copy is real, contextual draft content

### Screenshot verification (Phase 4.5 Round 4)
- [ ] `P0` Layout integrity — no overlapping elements, clipped text, or broken grid at all 3 viewports
- [ ] `P0` Contrast legibility — all text readable against its background (desktop + mobile)
- [ ] `P0` HOOK visible — the unforgettable moment is visually prominent in the desktop screenshot
- [ ] `P1` Font rendering — heading and body fonts loaded (not falling back to system sans-serif)
- [ ] `P1` Color fidelity — rendered colors match Design Brief palette (no unexpected hues)
- [ ] `P1` Responsive behavior — layout adapts sensibly from 1440px → 768px → 375px
- [ ] `P2` Spacing consistency — margins/padding look even, no collapsed or doubled gaps
- [ ] `P2` Interactive affordance — buttons/links visually distinct, primary CTA stands out

### SEO (public pages)
- [ ] `P1` `<title>` present and descriptive
- [ ] `P1` `<meta name="description">` (150–160 chars)
- [ ] `P2` Open Graph tags: `og:title`, `og:description`, `og:image`
- [ ] `P3` Favicon present

# Component Detection — Semantic Section Identification

## Overview

Clone HTML files are flat HTML documents. This guide defines how to identify semantic sections and extract them as React components.

## Detection Strategy (Priority Order)

### Signal 1: HTML5 Semantic Tags (Highest Confidence)

```html
<nav>         →  Navbar component
<header>      →  Header / Hero component
<main>        →  Page content wrapper (contains child sections)
<section>     →  Individual page section (Features, Pricing, etc.)
<article>     →  Blog post / content card
<aside>       →  Sidebar component
<footer>      →  Footer component
```

Rule: If the page uses semantic HTML, trust it. Each top-level semantic element = one component.

### Signal 2: ARIA Roles

```html
role="banner"       →  Header / Hero
role="navigation"   →  Navbar
role="main"         →  Main content wrapper
role="contentinfo"  →  Footer
role="complementary" →  Sidebar
role="search"       →  Search component
```

### Signal 3: Class Name Pattern Matching

Scan class names on top-level `<div>` and `<section>` elements:

| Pattern (case-insensitive) | Component Name |
|---------------------------|----------------|
| `*nav*`, `*navbar*`, `*topbar*`, `*header-nav*` | Navbar |
| `*hero*`, `*banner*`, `*jumbotron*`, `*masthead*` | Hero |
| `*feature*`, `*benefits*`, `*highlights*`, `*solutions*` | Features |
| `*pricing*`, `*plans*`, `*tiers*` | Pricing |
| `*testimonial*`, `*reviews*`, `*social-proof*`, `*quotes*` | Testimonials |
| `*faq*`, `*accordion*`, `*questions*` | FAQ |
| `*cta*`, `*call-to-action*`, `*signup*`, `*get-started*` | CTA |
| `*footer*`, `*site-footer*` | Footer |
| `*team*`, `*people*`, `*about-team*` | Team |
| `*stats*`, `*metrics*`, `*numbers*`, `*counters*` | Stats |
| `*logos*`, `*partners*`, `*clients*`, `*trusted-by*` | LogoCloud |
| `*blog*`, `*posts*`, `*articles*` | Blog |
| `*contact*`, `*get-in-touch*` | Contact |
| `*gallery*`, `*showcase*`, `*portfolio*` | Gallery |
| `*integrations*`, `*apps*`, `*marketplace*` | Integrations |
| `*comparison*`, `*vs*`, `*compare*` | Comparison |
| `*how-it-works*`, `*steps*`, `*process*` | HowItWorks |
| `*newsletter*`, `*subscribe*` | Newsletter |
| `*privacy*`, `*security*`, `*trust*` | Privacy |
| `*built*`, `*built-for*`, `*designed-for*` | BuiltFor |
| `*organize*`, `*services*` | Services |

#### Webflow-Specific Class Patterns

Webflow sites rarely use semantic HTML tags. Instead, look for these framework classes combined with custom classes:

| Webflow Class | Meaning | Detection Rule |
|--------------|---------|----------------|
| `w-nav` | Navigation bar | Always Navbar |
| `w-section` | Generic section | Use sibling custom class for naming |
| `w-footer` | Footer | Always Footer |
| `w-slider`, `w-tabs` | Interactive components | Keep within parent section |
| `w-dropdown` | Dropdown menu | Keep within Navbar |
| `w-lightbox` | Lightbox/modal | Keep within parent section |
| `w-background-video` | Background video | Keep within parent section |

**Key insight:** On Webflow sites, the *custom class* next to the `w-*` class is the meaningful one:
- `class="navbar w-nav"` → component name comes from `navbar`
- `class="hero"` → component name comes from `hero`
- `class="solutions"` → component name comes from `solutions`

Ignore `w-*` prefix classes for naming; they're framework classes for styling.

### Signal 4: ID Attribute

```html
<section id="features">    →  Features
<div id="pricing">         →  Pricing
<section id="hero">        →  Hero
```

### Signal 5: Structural Position (Fallback)

When no semantic signals exist:

1. **First child** of `<body>` (or first wrapper div) containing `<a>` links and/or a logo image → **Navbar**
2. **First large section** after Navbar with headline text (`<h1>` or large font-size) → **Hero**
3. **Last child** of `<body>` (or last major div) containing multiple link groups → **Footer**
4. **Everything in between** → numbered sections (`Section1`, `Section2`, etc.)

## Component Naming Rules

1. Use PascalCase: `hero-section` → `Hero`, `pricing-plans` → `Pricing`
2. For page-specific components, prefix with page context when needed: `PricingHero`, `AboutTeam`
3. If a section has no clear semantic name, use positional names: `Section1`, `Section2`
4. Avoid generic names like `Container`, `Wrapper`, `Block` — be specific

## Nesting Rules

### Depth-1 Components (Direct children of `<body>` or main wrapper)
These become top-level components that the page composes:

```tsx
// app/page.tsx
export default function Home() {
  return (
    <>
      <Hero />
      <Features />
      <Pricing />
      <Testimonials />
      <CTA />
    </>
  );
}
```

### Depth-2+ Components (Nested within sections)
Only extract as separate components if:
- They are **repeated** (cards, list items, grid cells) — extract as a reusable sub-component
- They are **complex** (50+ lines of JSX) — extract for readability
- They are **shared** across multiple sections — extract for reuse

Otherwise, keep them inline within the parent component.

```tsx
// components/home/Features.tsx
function FeatureCard({ title, description, icon }) { ... }

export function Features() {
  return (
    <section className={styles.features}>
      <FeatureCard ... />
      <FeatureCard ... />
      <FeatureCard ... />
    </section>
  );
}
```

## Cross-Page Shared Component Detection (Mode B/C)

For multi-page conversions, detect shared components by comparing pages:

### Algorithm

1. For each page, extract the **first top-level element** (likely Navbar) and **last top-level element** (likely Footer)
2. Normalize whitespace and remove dynamic content (active states, page-specific text)
3. Compare using text similarity:
   - **>85% similar** → Shared component (extract once to `components/shared/`)
   - **50-85% similar** → Likely shared with variations (extract with props for differences)
   - **<50% similar** → Page-specific (keep separate)

### What to Compare

- HTML structure (tag nesting)
- Class names
- Link `href` values
- Text content (ignoring active/current page indicators)

### Active State Handling

Navbars often highlight the current page. When extracting a shared Navbar:

```tsx
// components/shared/Navbar.tsx
'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export function Navbar() {
  const pathname = usePathname();
  
  return (
    <nav className={styles.nav}>
      <Link 
        href="/" 
        className={pathname === '/' ? styles.navLinkActive : styles.navLink}
      >
        Home
      </Link>
      <Link 
        href="/pricing" 
        className={pathname === '/pricing' ? styles.navLinkActive : styles.navLink}
      >
        Pricing
      </Link>
    </nav>
  );
}
```

## SVG Icon Extraction

Inline SVGs that appear as icons (small, repeated patterns) should be extracted:

```tsx
// components/icons.tsx
export function ChevronRight({ className }: { className?: string }) {
  return (
    <svg className={className} width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M9 18l6-6-6-6" />
    </svg>
  );
}

export function CheckIcon({ className }: { className?: string }) {
  return (
    <svg className={className} width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
    </svg>
  );
}
```

Detection criteria for icon SVGs:
- `width` and `height` ≤ 48px
- Appears 2+ times in the page (or across pages)
- Simple paths (< 500 characters of path data)
- Uses `currentColor` for fill or stroke

# CSS Extraction & Decomposition Strategy

## Input Structure

The clone HTML from `frontend-ui-clone` contains a single `<style>` block with strict ordering:

```
1. @import rules (must be first per spec)
2. @property declarations (Tailwind v4)
3. :root fallback block (all CSS custom properties)
4. @layer declarations
5. @font-face rules
6. All framework CSS rules (the bulk)
7. Fix overrides (at the very end, contains !important rules)
```

## Output Structure

### globals.css — Global styles (loaded once in layout.tsx)

Extract and place in this order:

```css
/* === 1. @import rules === */
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap");

/* === 2. @property declarations === */
@property --tw-translate-x { ... }

/* === 3. :root design tokens === */
:root {
  --color-bg: #ffffff;
  --color-text-primary: #1a1a1a;
  --color-accent: #3b82f6;
  /* ... all custom properties ... */
}

/* === 4. @layer declarations === */
@layer base, components, utilities;

/* === 5. @font-face rules === */
@font-face {
  font-family: 'CustomFont';
  src: url('...') format('woff2');
}

/* === 6. Reset / base element styles === */
*, *::before, *::after { box-sizing: border-box; margin: 0; }
html { scroll-behavior: smooth; }
body { font-family: var(--font-sans); ... }

/* === 7. @keyframes (ALL animations go here) === */
@keyframes fadeIn { ... }
@keyframes slideUp { ... }
@keyframes marquee { ... }

/* === 8. Shared utility classes === */
/* Rules that match classes used in 2+ components */

/* === 9. Fix overrides (from frontend-ui-clone) === */
[class*="animate-"] { opacity: 1 !important; transform: none !important; }
body, html { overflow-y: auto !important; overflow-x: hidden !important; }
```

### Component.module.css — Component-scoped styles (only if `--css modules`)

**WARNING:** CSS Modules is NOT the default. Use Global CSS unless the user explicitly requests `--css modules`. Clone CSS relies heavily on cascade ordering and shared framework classes (especially Webflow's `w-*` classes) that break when split into modules.

Only include rules whose selectors EXCLUSIVELY reference classes within that component.

```css
/* Hero.module.css */
.hero-section { ... }
.hero-title { ... }
.hero-description { ... }
.hero-cta { ... }
```

## CSS Classification Algorithm

### Step 1: Collect class names per component

For each component's HTML fragment, extract all class names:
```
Navbar: ['nav', 'nav-link', 'nav-logo', 'nav-menu', ...]
Hero: ['hero-section', 'hero-title', 'hero-cta', ...]
Features: ['features-grid', 'feature-card', ...]
```

### Step 2: Classify each CSS rule

For each CSS rule in the framework CSS section:

1. Parse the selector to extract all class names referenced
2. Check which component(s) those classes belong to
3. Classify:
   - **Single component**: → that component's `.module.css`
   - **Multiple components**: → `globals.css` (shared section)
   - **No component match** (element selectors like `h1`, `p`, `a`): → `globals.css` (base section)
   - **Pseudo-elements/states** (`:hover`, `::before`): classify based on the base class

### Step 3: Handle complex selectors

```css
/* Descendant selector — classify by the OUTERMOST class */
.nav .nav-link:hover { ... }  →  Navbar.module.css

/* Combined selector — if classes span components, → globals */
.hero-section .feature-card { ... }  →  globals.css

/* Universal modifiers — always global */
.hidden { display: none; }  →  globals.css
.sr-only { ... }  →  globals.css
```

### Step 4: Safety rules

- **When in doubt → globals.css** (false negatives are cosmetic; false positives break layout)
- **@media queries**: Keep with their rules (if rule → component, the @media wrapper goes too)
- **@keyframes**: ALWAYS globals.css (animations may be referenced from CSS or JS anywhere)
- **@supports**: Keep with their rules
- **:root, html, body**: ALWAYS globals.css
- **Tailwind utility classes** (`flex`, `p-4`, `text-sm`): ALWAYS globals.css

## Tailwind Detection

Detect Tailwind usage by checking for these signals:

1. `@property --tw-*` declarations exist
2. `@layer base, components, utilities` exists
3. Class names match Tailwind patterns: `flex`, `grid`, `p-[N]`, `m-[N]`, `text-[size]`, `bg-[color]`, `rounded-[size]`, `shadow-[size]`, `w-[size]`, `h-[size]`
4. `:root` contains `--tw-*` custom properties

If Tailwind detected:
- Keep utility classes as `className` strings in JSX (no CSS Modules for these)
- Extract design tokens to `tailwind.config.ts`
- Put non-utility custom CSS in globals.css
- Do NOT convert Tailwind classes to CSS Modules

## Design Token Extraction

Parse `:root` block and categorize:

```typescript
// tailwind.config.ts (if Tailwind mode)
export default {
  theme: {
    extend: {
      colors: {
        background: 'var(--color-bg)',
        foreground: 'var(--color-text-primary)',
        accent: 'var(--color-accent)',
        // ... extracted from --color-* variables
      },
      fontFamily: {
        sans: ['var(--font-sans)'],
        mono: ['var(--font-mono)'],
      },
      borderRadius: {
        DEFAULT: 'var(--radius)',
        // ... extracted from --radius-* variables
      },
      // spacing, shadows, etc.
    }
  }
}
```

Categories for token extraction:
- `--color-*`, `--bg-*`, `--text-*`, `--border-*` → colors
- `--font-*`, `--text-*` (sizes) → typography
- `--space-*`, `--gap-*`, `--padding-*` → spacing
- `--radius-*`, `--rounded-*` → borderRadius
- `--shadow-*` → boxShadow
- `--motion-*`, `--duration-*`, `--ease-*` → transition/animation

## Responsive CSS Handling

`@media` queries from the clone must be preserved correctly:

```css
/* If the contained rules are component-scoped → component CSS module */
@media (max-width: 768px) {
  .hero-title { font-size: 2rem; }  /* → Hero.module.css */
}

/* If mixed → split into separate @media blocks per component */
@media (max-width: 768px) {
  .hero-title { font-size: 2rem; }   /* → Hero.module.css */
  .nav-menu { display: none; }       /* → Navbar.module.css */
}
/* Becomes: */
/* Hero.module.css */
@media (max-width: 768px) { .hero-title { font-size: 2rem; } }
/* Navbar.module.css */
@media (max-width: 768px) { .nav-menu { display: none; } }
```

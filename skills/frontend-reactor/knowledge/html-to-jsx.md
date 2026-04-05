# HTML to JSX Conversion Rules

## Attribute Transforms

| HTML | JSX | Notes |
|------|-----|-------|
| `class="..."` | `className="..."` | Most common |
| `for="..."` | `htmlFor="..."` | On `<label>` |
| `tabindex="N"` | `tabIndex={N}` | Numeric prop |
| `maxlength="N"` | `maxLength={N}` | |
| `readonly` | `readOnly` | Boolean |
| `autocomplete` | `autoComplete` | |
| `autofocus` | `autoFocus` | |
| `autoplay` | `autoPlay` | |
| `crossorigin` | `crossOrigin` | |
| `enctype` | `encType` | |
| `formaction` | `formAction` | |
| `novalidate` | `noValidate` | |
| `charset` | `charSet` | On `<meta>` |
| `http-equiv` | `httpEquiv` | On `<meta>` |
| `colspan="N"` | `colSpan={N}` | |
| `rowspan="N"` | `rowSpan={N}` | |
| `cellpadding` | `cellPadding` | |
| `cellspacing` | `cellSpacing` | |
| `datetime` | `dateTime` | On `<time>` |
| `accesskey` | `accessKey` | |
| `contenteditable` | `contentEditable` | |
| `spellcheck` | `spellCheck` | |

## Self-Closing Tags

These must end with `/>` in JSX (not `>` alone):

```
<img ...>    →  <img ... />
<br>         →  <br />
<hr>         →  <hr />
<input ...>  →  <input ... />
<meta ...>   →  <meta ... />
<link ...>   →  <link ... />
<source ...> →  <source ... />
<area ...>   →  <area ... />
<col ...>    →  <col ... />
<embed ...>  →  <embed ... />
<wbr>        →  <wbr />
<track ...>  →  <track ... />
```

## Inline Style Conversion

```html
<!-- HTML -->
<div style="background-color: #fff; font-size: 16px; z-index: 10; -webkit-backdrop-filter: blur(10px);">

<!-- JSX -->
<div style={{ backgroundColor: '#fff', fontSize: '16px', zIndex: 10, WebkitBackdropFilter: 'blur(10px)' }}>
```

Rules:
- Kebab-case → camelCase (`font-size` → `fontSize`)
- Values stay as strings EXCEPT pure numbers (`zIndex: 10`, not `'10'`)
- Vendor prefixes: `-webkit-X` → `WebkitX`, `-moz-X` → `MozX`, `-ms-X` → `msX`
- Semicolons → commas
- Colon-space → colon (key-value pairs)

## SVG Attribute Conversion

| SVG HTML | JSX |
|----------|-----|
| `stroke-width` | `strokeWidth` |
| `stroke-linecap` | `strokeLinecap` |
| `stroke-linejoin` | `strokeLinejoin` |
| `stroke-dasharray` | `strokeDasharray` |
| `stroke-dashoffset` | `strokeDashoffset` |
| `stroke-miterlimit` | `strokeMiterlimit` |
| `stroke-opacity` | `strokeOpacity` |
| `fill-rule` | `fillRule` |
| `fill-opacity` | `fillOpacity` |
| `clip-path` | `clipPath` |
| `clip-rule` | `clipRule` |
| `font-size` | `fontSize` |
| `font-family` | `fontFamily` |
| `font-weight` | `fontWeight` |
| `text-anchor` | `textAnchor` |
| `text-decoration` | `textDecoration` |
| `dominant-baseline` | `dominantBaseline` |
| `alignment-baseline` | `alignmentBaseline` |
| `color-interpolation` | `colorInterpolation` |
| `flood-color` | `floodColor` |
| `flood-opacity` | `floodOpacity` |
| `stop-color` | `stopColor` |
| `stop-opacity` | `stopOpacity` |
| `pointer-events` | `pointerEvents` |
| `xlink:href` | `xlinkHref` |
| `xml:space` | `xmlSpace` |
| `xmlns:xlink` | `xmlnsXlink` |

## Comments

```html
<!-- HTML comment -->     →     {/* JSX comment */}
```

## Event Handlers

Remove all `on*` HTML attributes — they reference non-existent scripts:
```html
<!-- Remove these -->
onclick="..." onmouseover="..." onsubmit="..."
```

## dangerouslySetInnerHTML Rules

**CRITICAL:** When using `dangerouslySetInnerHTML={{ __html: '...' }}`, the HTML string is rendered as **raw browser HTML**, NOT JSX. Therefore:

- **Use `class=`, NOT `className=`** — browsers don't understand `className`
- **Use `for=`, NOT `htmlFor=`**
- **Use `tabindex=`, NOT `tabIndex=`**
- **Use `style="..."` as a string**, NOT `style={{ }}`
- **Keep SVG attributes as kebab-case** (`stroke-width`, NOT `strokeWidth`)
- **Use `<!-- -->` comments**, NOT `{/* */}`

```tsx
// WRONG — className won't work inside dangerouslySetInnerHTML
<div dangerouslySetInnerHTML={{ __html: `<div className="hero">...</div>` }} />

// CORRECT — use class for raw HTML
<div dangerouslySetInnerHTML={{ __html: `<div class="hero">...</div>` }} />
```

**When to use dangerouslySetInnerHTML:**
- Clone HTML sections that are too large/complex for manual JSX conversion
- Sections with deeply nested structures where manual conversion is error-prone

**When NOT to use it:**
- Components that need React interactivity (clicks, state, events)
- Small, simple components that are easy to convert properly

**If a component needs BOTH raw HTML and interactivity:**
Split it — use proper JSX for the interactive wrapper and `dangerouslySetInnerHTML` only for the static inner content.

## Dangerous Patterns to Watch

1. **`class` inside SVG**: SVG elements also use `class` → must convert to `className` (in JSX only, NOT in dangerouslySetInnerHTML)
2. **`style` on SVG elements**: Same conversion rules apply
3. **Nested quotes**: `style="font-family: 'Inter', sans-serif"` → must escape or use template literals
4. **Empty attributes**: `disabled=""` → `disabled` (boolean true)
5. **`data-*` attributes**: Keep as-is (React passes them through)
6. **`aria-*` attributes**: Keep as-is (React passes them through)
7. **`value` on `<select>`/`<input>`**: Use `defaultValue` for uncontrolled components

## CSS Module Class Name Conversion

When using CSS Modules, class references change:

```html
<!-- Original -->
<div class="hero-section dark-theme">

<!-- JSX with CSS Modules -->
import styles from './Hero.module.css';
<div className={`${styles['hero-section']} ${styles['dark-theme']}`}>

<!-- Or with camelCase class names -->
<div className={`${styles.heroSection} ${styles.darkTheme}`}>
```

For Tailwind utility classes (kept inline):
```html
<!-- No change needed for Tailwind classes -->
<div className="flex items-center gap-4 p-6">
```

## Link Conversion (Next.js)

Strategy depends on whether the target route exists in the project:

### Mode A (single page) — No sub-routes exist

All internal links stay as plain `<a>` tags with relative paths:

```html
<!-- Internal link → relative path, plain <a> -->
<a href="https://example.com/pricing">Pricing</a>
→
<a href="/pricing">Pricing</a>

<!-- Anchor link — keep as-is -->
<a href="#features">Features</a>

<!-- External link -->
<a href="https://github.com/example">GitHub</a>
→
<a href="https://github.com/example" target="_blank" rel="noopener noreferrer">GitHub</a>
```

### Mode B/C (multi-page) — Sub-routes exist

Use `<Link>` for routes that have corresponding clone files:

```html
<!-- Internal link WITH route → Next.js Link -->
<a href="https://example.com/pricing">Pricing</a>
→
import Link from 'next/link';
<Link href="/pricing">Pricing</Link>

<!-- Internal link WITHOUT route → plain <a> with TODO -->
<a href="https://example.com/blog">Blog</a>
→
{/* TODO: Clone /blog page and add route */}
<a href="/blog">Blog</a>

<!-- Button wrapping a routed link -->
<a href="/signup" class="btn-primary">Get Started</a>
→
<Link href="/signup" className="btn-primary">Get Started</Link>
```

### All modes — URL normalization

Always convert absolute URLs to relative paths:
- `https://example.com/pricing` → `/pricing`
- `https://example.com/` → `/`
- `https://example.com/#features` → `/#features`

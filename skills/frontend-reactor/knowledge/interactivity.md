# Interactivity Restoration

## Overview

Clone HTML strips all `<script>` tags, so interactive elements (dropdowns, accordions, forms, modals, tabs, mobile menus) become inert. This guide defines how to detect and restore interactivity using React client components with `useState`/`useRef`.

## Detection Strategy

Two-layer detection: runtime detection (primary) then class-name matching (fallback).

### Layer 1: Runtime Detection (Primary — Mode C)

In Mode C, Playwright runs on the live page BEFORE cloning. Use computed styles and DOM properties to find every interactive element. See `knowledge/site-discovery.md` Phase A2 for the full script.

**Key signals (in priority order):**

| Signal | Reliability | What it catches |
|--------|------------|-----------------|
| `cursor: pointer` | Highest | Any visually clickable element, regardless of tag or class name |
| `<a href>` | High | All links |
| `<button>` | High | All buttons |
| `<input>/<select>/<textarea>` | High | All form controls |
| `role="button/tab/link"` | High | ARIA-attributed components (Radix, shadcn, headless UI) |
| `aria-expanded` | High | Expandable sections (accordions, dropdowns) |
| `data-state` | Medium | Stateful components (common in modern React frameworks) |
| `tabindex >= 0` | Medium | Custom focusable elements |
| `onclick` | Medium | Inline event handlers (before stripping) |

**`cursor: pointer` is the single most reliable signal** — developers always set it on clickable elements, even when using non-semantic tags like `<div>` or `<span>`. It works regardless of class naming conventions, CSS frameworks, or component libraries.

The runtime detection output is a JSON list of interactive elements with their position, text, href, and signals. This list drives the post-clone fixup phase.

### Layer 2: Class Name Pattern Matching (Fallback — Mode A/B)

In Mode A/B, we don't have a live browser — only static clone HTML. Fall back to scanning class names and HTML structure:

After extracting a component's JSX, scan for these interactive patterns:

### Pattern 1: Dropdown / Flyout Menu

**Detection signals:**
- Element with class matching `*dropdown*`, `*flyout*`, `*popover*`, `*menu*`
- A trigger element (button/link) adjacent to a hidden panel
- CSS `display: none` or `opacity: 0` on a child container
- Webflow: `w-dropdown`, `w-dropdown-toggle`, `w-dropdown-list`
- Presence of `aria-expanded`, `aria-haspopup`, `data-toggle`

**Restoration:**
```tsx
'use client';
import { useState, useRef, useEffect } from 'react';

function Dropdown({ trigger, children, className }: {
  trigger: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div ref={ref} className={className} style={{ position: 'relative' }}>
      <div onClick={() => setOpen(!open)} style={{ cursor: 'pointer' }}>
        {trigger}
      </div>
      {open && (
        <div style={{ position: 'absolute', top: '100%', left: 0, zIndex: 100 }}>
          {children}
        </div>
      )}
    </div>
  );
}
```

### Pattern 2: Accordion / FAQ Collapse

**Detection signals:**
- Element with class matching `*accordion*`, `*faq*`, `*collapse*`, `*expandable*`
- Repeating pattern: title/question element + content/answer element
- CSS `display: none`, `max-height: 0`, `overflow: hidden` on content
- Webflow: `faq-row`, `faq-answer`, `w-dropdown` used as accordion
- Plus/minus icon or chevron that rotates

**Restoration:**
```tsx
'use client';
import { useState } from 'react';

function AccordionItem({ title, children, defaultOpen = false }: {
  title: React.ReactNode;
  children: React.ReactNode;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div>
      <div 
        onClick={() => setOpen(!open)} 
        style={{ cursor: 'pointer' }}
        role="button"
        aria-expanded={open}
      >
        {title}
        <span style={{ 
          transform: open ? 'rotate(45deg)' : 'rotate(0deg)', 
          transition: 'transform 0.2s',
          display: 'inline-block'
        }}>+</span>
      </div>
      <div style={{
        maxHeight: open ? '2000px' : '0px',
        overflow: 'hidden',
        transition: 'max-height 0.3s ease',
      }}>
        {children}
      </div>
    </div>
  );
}
```

### Pattern 3: Mobile Navigation Toggle

**Detection signals:**
- Element with class matching `*hamburger*`, `*menu-btn*`, `*nav-button*`, `*mobile-menu*`
- Webflow: `w-nav-button`, `w-nav-overlay`, `data-nav-menu-open`
- A navigation menu with `display: none` at mobile breakpoints
- Three-line icon (hamburger) or X icon

**Restoration:**
```tsx
'use client';
import { useState } from 'react';

function MobileNavToggle({ menuContent }: { menuContent: React.ReactNode }) {
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* Hamburger button — visible only on mobile via CSS */}
      <button 
        className="mobile-menu-btn"
        onClick={() => setOpen(!open)}
        aria-label="Toggle menu"
      >
        {open ? '✕' : '☰'}
      </button>
      
      {/* Mobile menu overlay */}
      {open && (
        <div className="mobile-menu-overlay" onClick={() => setOpen(false)}>
          <div className="mobile-menu-content" onClick={e => e.stopPropagation()}>
            {menuContent}
          </div>
        </div>
      )}
    </>
  );
}
```

### Pattern 4: Tabs

**Detection signals:**
- Element with class matching `*tab*`, `*tabs*`
- Webflow: `w-tabs`, `w-tab-menu`, `w-tab-link`, `w-tab-content`, `w-tab-pane`
- Multiple trigger buttons + corresponding content panels
- `w--current` or `w--tab-active` class for active state
- `aria-selected`, `role="tab"`, `role="tabpanel"`

**Restoration:**
```tsx
'use client';
import { useState } from 'react';

function Tabs({ tabs }: { tabs: { label: string; content: React.ReactNode }[] }) {
  const [active, setActive] = useState(0);

  return (
    <div>
      <div role="tablist" style={{ display: 'flex', gap: '8px' }}>
        {tabs.map((tab, i) => (
          <button
            key={i}
            role="tab"
            aria-selected={active === i}
            onClick={() => setActive(i)}
            className={active === i ? 'tab-active' : 'tab-inactive'}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div role="tabpanel">
        {tabs[active]?.content}
      </div>
    </div>
  );
}
```

### Pattern 5: Modal / Dialog / Popup

**Detection signals:**
- Element with class matching `*modal*`, `*dialog*`, `*popup*`, `*overlay*`, `*lightbox*`
- Webflow: `w-lightbox`, `waitlist-popup`, `desktop-app-form`
- `position: fixed`, `z-index` > 100, `display: none`
- A close button (X icon, class `*close*`)
- A trigger button elsewhere that references the modal by ID

**Restoration:**
```tsx
'use client';
import { useState } from 'react';

function Modal({ trigger, children }: {
  trigger: React.ReactNode;
  children: React.ReactNode;
}) {
  const [open, setOpen] = useState(false);

  if (!open) {
    return <div onClick={() => setOpen(true)} style={{ cursor: 'pointer' }}>{trigger}</div>;
  }

  return (
    <>
      <div onClick={() => setOpen(true)} style={{ cursor: 'pointer' }}>{trigger}</div>
      <div 
        style={{
          position: 'fixed', inset: 0, zIndex: 1000,
          background: 'rgba(0,0,0,0.5)',
          display: 'flex', justifyContent: 'center', alignItems: 'center',
        }}
        onClick={() => setOpen(false)}
      >
        <div onClick={e => e.stopPropagation()} style={{ position: 'relative' }}>
          <button 
            onClick={() => setOpen(false)}
            style={{ position: 'absolute', top: 8, right: 8, cursor: 'pointer' }}
            aria-label="Close"
          >✕</button>
          {children}
        </div>
      </div>
    </>
  );
}
```

### Pattern 6: Form with State

**Detection signals:**
- `<form>` element or `w-form` class
- `<input>`, `<textarea>`, `<select>` elements
- Submit button (`type="submit"` or class `*submit*`)

**Restoration:**
```tsx
'use client';
import { useState, FormEvent } from 'react';

function ContactForm() {
  const [formData, setFormData] = useState({ name: '', email: '', message: '' });
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    // TODO: Connect to API endpoint
    console.log('Form submitted:', formData);
    setSubmitted(true);
  };

  if (submitted) {
    return <div className="form-success">Thank you! We'll be in touch.</div>;
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Name"
        value={formData.name}
        onChange={e => setFormData(prev => ({ ...prev, name: e.target.value }))}
      />
      <input
        type="email"
        placeholder="Email"
        value={formData.email}
        onChange={e => setFormData(prev => ({ ...prev, email: e.target.value }))}
      />
      <textarea
        placeholder="Message"
        value={formData.message}
        onChange={e => setFormData(prev => ({ ...prev, message: e.target.value }))}
      />
      <button type="submit">Submit</button>
    </form>
  );
}
```

### Pattern 7: Scroll-to-Section (Anchor Links)

**Detection signals:**
- `<a href="#section-id">` links
- Smooth scroll behavior in original CSS

**Restoration:**
```tsx
// In any component with anchor links
<a 
  href="#features" 
  onClick={(e) => {
    e.preventDefault();
    document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
  }}
>
  Features
</a>
```

### Pattern 8: Carousel / Slider

**Detection signals:**
- Element with class matching `*carousel*`, `*slider*`, `*swiper*`
- Webflow: `w-slider`, `w-slider-mask`, `w-slide`
- Left/right arrow buttons
- Dot indicators
- Multiple items with `overflow: hidden` on parent

**Restoration (simple CSS-based):**
```tsx
'use client';
import { useState } from 'react';

function Carousel({ items }: { items: React.ReactNode[] }) {
  const [current, setCurrent] = useState(0);

  return (
    <div style={{ position: 'relative', overflow: 'hidden' }}>
      <div style={{
        display: 'flex',
        transform: `translateX(-${current * 100}%)`,
        transition: 'transform 0.3s ease',
      }}>
        {items.map((item, i) => (
          <div key={i} style={{ minWidth: '100%', flexShrink: 0 }}>{item}</div>
        ))}
      </div>
      <button 
        onClick={() => setCurrent(Math.max(0, current - 1))}
        style={{ position: 'absolute', left: 8, top: '50%', transform: 'translateY(-50%)' }}
      >←</button>
      <button 
        onClick={() => setCurrent(Math.min(items.length - 1, current + 1))}
        style={{ position: 'absolute', right: 8, top: '50%', transform: 'translateY(-50%)' }}
      >→</button>
    </div>
  );
}
```

## Integration into Component Generation

During Phase 3 (React Component Generation), for EACH component:

1. **Scan the JSX** for interactive pattern signals listed above
2. **If detected:**
   - Add `'use client';` directive at the top of the component file
   - Import `useState`, `useRef`, `useEffect` as needed
   - Wrap the interactive elements with the appropriate pattern
   - Preserve all original class names and structure (don't replace, wrap)
3. **If no interactive patterns detected:** Keep as server component (no `'use client'`)

## Priority Order

Restore interactivity in this order (most impactful first):
1. Navigation (dropdown menus, mobile toggle) — breaks site usability if missing
2. Anchor links (smooth scroll) — common, easy to implement
3. Accordions/FAQ — frequently used on landing pages
4. Tabs — common in feature showcases
5. Forms — need state for inputs
6. Modals — less critical, often for CTAs
7. Carousels — most complex, lowest priority

## Post-Clone Fixups (dangerouslySetInnerHTML components)

When components use `dangerouslySetInnerHTML` to embed clone HTML, the following patterns need post-processing:

### Pattern 9: Typewriter / Placeholder Overlay on Input

**Problem:** Clone captures a typewriter animation mid-cycle. The input has `text-transparent caret-transparent` (makes real text invisible), and a `pointer-events-none` overlay div shows the animated text. In the static clone, the input appears to have hardcoded text that can't be edited.

**Detection signals:**
- `<input>` with class `text-transparent` or `caret-transparent`
- Adjacent `<div>` with `pointer-events-none` containing `<span>` with visible text
- Input has empty `value=""` or no placeholder

**Fix (string replacement on the HTML):**
```python
# Hide the overlay
html = html.replace('pointer-events-none"><span class="text-black"', 
                     'pointer-events-none hidden"><span class="text-black"')
# Make input text visible
html = html.replace('text-transparent caret-transparent', '')
# Add placeholder
html = html.replace('placeholder="" autocomplete="off"',
                     'placeholder="Describe what you want to build..." autocomplete="off"')
```

### Pattern 10: Dead Buttons (no href, no onClick)

**Problem:** Clone strips all `<script>` tags, so `<button>` elements that relied on JS click handlers become inert. Common for CTA buttons ("Sign in", "Get started", "Import from Figma").

**Detection signals:**
- `<button>` without wrapping `<a>` tag
- Button text matches common CTA patterns

**Fix (string replacement on the HTML):**
```python
import re

ORIGINAL_SITE = "https://www.example.com"

# Convert specific buttons to links pointing to the original site
html = re.sub(r'<button([^>]*)>Sign in</button>',
              rf'<a href="{ORIGINAL_SITE}/signin" target="_blank" rel="noopener noreferrer" \\1 style="cursor:pointer;">Sign in</a>', html)

# CTA buttons → link to original site homepage
for cta_text in ['Get started free', 'Import from Figma', 'Start creating', 'Try MagicPath']:
    html = re.sub(
        rf'<button([^>]*)>({cta_text}[^<]*)</button>',
        rf'<a href="{ORIGINAL_SITE}" target="_blank" rel="noopener noreferrer" \\1 style="cursor:pointer;">\\2</a>',
        html
    )

# Add cursor pointer to remaining buttons
html = html.replace('data-slot="button"', 'data-slot="button" style="cursor:pointer;"')
```

### Pattern 11: Internal Links → Original Site

**Problem:** Clone HTML contains links that may be relative (`/pricing`) or absolute (`https://example.com/pricing`). In Mode A/B with local routes, these become local navigation. In Mode C (homepage-only), ALL internal links should point to the original site.

**Mode A (single file) / Mode B (multi-file):**
```python
# Convert absolute URLs to relative for local routing
html = html.replace('href="https://www.example.com/', 'href="/')
html = html.replace('href="https://example.com/', 'href="/')
```

**Mode C (homepage-only, all links → original site):**
```python
ORIGINAL_SITE = "https://www.example.com"

# Ensure relative links become absolute to the original site
# /pricing → https://www.example.com/pricing
html = re.sub(r'href="/((?!/)[\w/\-\.]+)"', rf'href="{ORIGINAL_SITE}/\\1" target="_blank" rel="noopener noreferrer"', html)

# Keep already-absolute internal links, just add target="_blank"
# (they already point to the original site)
```

## Application Order

When processing `dangerouslySetInnerHTML` components, apply fixups in this order:

1. **className → class** (and other JSX→HTML attribute reversions)
2. **URL normalization** (absolute → relative for internal links)
3. **Dead button conversion** (button → link for CTAs)
4. **Input overlay removal** (typewriter/placeholder fixes)
5. **Cursor pointer** on remaining interactive-looking elements

## What NOT to Restore

- **Tracking/analytics scripts** — intentionally removed
- **Third-party widgets** (Intercom, HubSpot, etc.) — require API keys
- **Complex animations** (GSAP, Lottie, WebGL) — out of scope, note in report
- **Real-time data** (live feeds, dashboards) — need backend
- **Authentication flows** — need backend

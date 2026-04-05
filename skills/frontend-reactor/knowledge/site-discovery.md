# Site Discovery — Browser-Based Page Crawling

## Overview

Mode C has two stages:
1. **Discovery (this file):** Use Playwright to browse the site and discover all navigable pages (nav links, footer links, buttons)
2. **Extraction:** Invoke `frontend-ui-clone` for each discovered page to get pixel-perfect HTML clones (~97% fidelity)

This file covers stage 1. The discovered page URLs are fed to frontend-ui-clone for extraction, then the clone HTML files enter the normal Mode B conversion pipeline.

**Fallback extraction:** If frontend-ui-clone invocation fails, this file also contains a simplified Playwright extraction script (Phase D) that gives ~80% fidelity.

## Discovery Strategy

### Phase A: Homepage Navigation Extraction

Visit the homepage and extract all clickable navigation elements:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    
    # Navigate with fallback
    try:
        page.goto(url, wait_until="networkidle", timeout=30000)
    except:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(8000)
    
    # Extract all links with context
    links = page.evaluate("""() => {
        const results = [];
        document.querySelectorAll('a[href]').forEach(a => {
            const rect = a.getBoundingClientRect();
            const parent = a.closest('nav, header, footer, [role="navigation"], [role="contentinfo"]');
            const parentTag = parent ? parent.tagName.toLowerCase() : null;
            const parentClass = parent ? parent.className : null;
            
            // Classify link location
            let location = 'body';
            if (parentTag === 'nav' || (parentClass && /nav|header|topbar/i.test(parentClass))) {
                location = 'nav';
            } else if (parentTag === 'footer' || (parentClass && /footer/i.test(parentClass))) {
                location = 'footer';
            }
            
            results.push({
                href: a.href,
                text: a.innerText.trim().substring(0, 100),
                location: location,
                visible: rect.width > 0 && rect.height > 0,
                isButton: a.classList.toString().match(/btn|button|cta/i) !== null,
            });
        });
        return results;
    }""")
```

### Phase A2: Runtime Interactive Element Detection

After extracting links, detect ALL interactive elements using computed styles — this catches elements that have no semantic markup but are visually clickable:

```python
interactive_elements = page.evaluate("""() => {
    const results = [];
    const seen = new Set();
    
    document.querySelectorAll('*').forEach(el => {
        const rect = el.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return;
        
        const style = getComputedStyle(el);
        const tag = el.tagName.toLowerCase();
        
        // Determine WHY this element is interactive
        const signals = [];
        if (tag === 'a' && el.href) signals.push('link');
        if (tag === 'button') signals.push('button');
        if (['input', 'select', 'textarea'].includes(tag)) signals.push('form-control');
        if (el.getAttribute('role') === 'button') signals.push('role-button');
        if (el.getAttribute('role') === 'link') signals.push('role-link');
        if (el.getAttribute('role') === 'tab') signals.push('role-tab');
        if (el.getAttribute('role') === 'menuitem') signals.push('role-menuitem');
        if (el.getAttribute('role') === 'switch') signals.push('role-switch');
        if (el.getAttribute('aria-expanded') !== null) signals.push('expandable');
        if (el.getAttribute('aria-haspopup') !== null) signals.push('has-popup');
        if (el.getAttribute('data-state') !== null) signals.push('stateful');
        if (parseInt(el.getAttribute('tabindex')) >= 0) signals.push('focusable');
        if (style.cursor === 'pointer') signals.push('cursor-pointer');
        if (el.onclick !== null) signals.push('onclick');
        
        if (signals.length === 0) return;
        
        // Deduplicate by position (avoid counting parent+child as separate)
        const key = Math.round(rect.x/10) + ',' + Math.round(rect.y/10) + ',' + Math.round(rect.width/10);
        if (seen.has(key)) return;
        seen.add(key);
        
        // Classify the element's location on page
        const parent = el.closest('nav, header, footer, [role="navigation"], [role="contentinfo"]');
        let location = 'body';
        if (parent) {
            const ptag = parent.tagName.toLowerCase();
            const pcls = parent.className || '';
            if (ptag === 'nav' || /nav|header|topbar/i.test(pcls)) location = 'nav';
            else if (ptag === 'footer' || /footer/i.test(pcls)) location = 'footer';
        }
        
        results.push({
            tag: tag,
            type: el.type || '',
            text: el.innerText.trim().substring(0, 80),
            href: el.href || '',
            placeholder: el.placeholder || '',
            signals: signals,
            location: location,
            classes: el.className.toString().substring(0, 120),
            // Bounding box for position context
            top: Math.round(rect.top),
            left: Math.round(rect.left),
            width: Math.round(rect.width),
            height: Math.round(rect.height),
        });
    });
    return results;
}""")
```

This returns a comprehensive list of every interactive element on the page, including:
- Elements with `cursor: pointer` (strongest signal — catches styled `<div>` buttons)
- ARIA-attributed elements (`role="button"`, `aria-expanded`, etc.)
- Stateful elements (`data-state` — common in Radix/shadcn components)
- Standard form controls (`<input>`, `<select>`, `<textarea>`)
- Elements with inline `onclick` handlers

**Output classification:**

| Signal | Meaning | Action |
|--------|---------|--------|
| `link` | `<a href>` | Convert href to original site URL |
| `button` | `<button>` element | Convert to `<a>` linking to original site |
| `cursor-pointer` | Visually clickable (any tag) | Ensure `cursor: pointer` preserved, convert to link if text suggests navigation |
| `form-control` | Input/select/textarea | Restore interactivity (remove overlays, add placeholder) |
| `expandable` | Has `aria-expanded` | Restore toggle state with `useState` |
| `stateful` | Has `data-state` | Restore open/close with `useState` |
| `role-tab` | Tab component | Restore tab switching |
| `has-popup` | Dropdown/popover trigger | Restore dropdown toggle |
| `focusable` | Custom `tabindex` | Ensure element is keyboard-accessible |

### Phase B: Link Classification & Filtering

From the extracted links, build a site map:

```python
from urllib.parse import urlparse

base_domain = urlparse(url).netloc.replace('www.', '')

internal_links = {}
external_links = []

for link in links:
    href = link['href']
    parsed = urlparse(href)
    link_domain = parsed.netloc.replace('www.', '')
    
    # Skip non-navigable
    if href.startswith(('javascript:', 'mailto:', 'tel:', '#')):
        continue
    if not link['visible']:
        continue
    
    # Classify
    if link_domain == base_domain or link_domain == '':
        path = parsed.path.rstrip('/') or '/'
        # Skip anchors on same page, file downloads, etc.
        if path.endswith(('.pdf', '.zip', '.png', '.jpg', '.svg')):
            continue
        if path not in internal_links:
            internal_links[path] = {
                'path': path,
                'text': link['text'],
                'location': link['location'],
                'full_url': href,
                'priority': 0,
            }
        # Boost priority based on location
        if link['location'] == 'nav':
            internal_links[path]['priority'] += 10
        elif link['location'] == 'footer':
            internal_links[path]['priority'] += 5
        elif link['isButton']:
            internal_links[path]['priority'] += 3
        else:
            internal_links[path]['priority'] += 1
    else:
        external_links.append(href)
```

### Phase C: Priority Sorting & Page Limit

Sort discovered pages by priority and apply a reasonable limit:

```
Priority scoring:
  nav link       = +10 per occurrence (most important — primary navigation)
  footer link    = +5 per occurrence (important — site-wide)
  CTA button     = +3 per occurrence  
  body link      = +1 per occurrence (least important — contextual)

Page limit:
  Default: 10 pages max (homepage + 9 subpages)
  Can be overridden with --max-pages N
  Always include homepage (/)
  
Sort order: priority descending → nav links first, then footer, then body
```

### Phase D: Per-Page Extraction

For each discovered page, extract DOM + CSS using Playwright:

```python
def extract_page(page, url):
    """Extract a single page's HTML and CSS."""
    
    # Navigate
    try:
        page.goto(url, wait_until="networkidle", timeout=30000)
    except:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(5000)
    
    # Scroll to trigger lazy loading (single pass, faster than clone)
    page.evaluate("""() => {
        return new Promise(resolve => {
            let total = document.body.scrollHeight;
            let current = 0;
            let step = window.innerHeight;
            let timer = setInterval(() => {
                current += step;
                window.scrollTo(0, current);
                if (current >= total) { clearInterval(timer); resolve(); }
            }, 100);
        });
    }""")
    page.wait_for_timeout(1000)
    page.evaluate("window.scrollTo(0, 0)")
    
    # Force visibility on animation-hidden elements
    page.evaluate("""() => {
        document.querySelectorAll('[class*="animate"]').forEach(el => {
            el.style.opacity = '1';
            el.style.transform = 'none';
        });
        // Fix lazy images
        document.querySelectorAll('img[data-src], img[data-lazy-src]').forEach(img => {
            img.src = img.dataset.src || img.dataset.lazySrc;
        });
        // Remove loading=lazy
        document.querySelectorAll('img[loading="lazy"]').forEach(img => {
            img.removeAttribute('loading');
        });
    }""")
    
    # Extract CSS
    css = page.evaluate("""() => {
        let css = '';
        for (let sheet of document.styleSheets) {
            try {
                for (let rule of sheet.cssRules) {
                    css += rule.cssText + '\\n';
                }
            } catch(e) {
                // Cross-origin stylesheet — keep as @import
                if (sheet.href) css += '@import url("' + sheet.href + '");\\n';
            }
        }
        return css;
    }""")
    
    # Extract :root custom properties
    root_vars = page.evaluate("""() => {
        const vars = {};
        const styles = getComputedStyle(document.documentElement);
        for (let i = 0; i < styles.length; i++) {
            const name = styles[i];
            if (name.startsWith('--')) {
                vars[name] = styles.getPropertyValue(name).trim();
            }
        }
        return vars;
    }""")
    
    # Extract body HTML (strip scripts)
    body_html = page.evaluate("""() => {
        // Remove scripts
        document.querySelectorAll('script').forEach(s => s.remove());
        // Remove cookie banners
        document.querySelectorAll('[class*="cookie"], [id*="consent"], [class*="gdpr"]').forEach(el => el.remove());
        return document.body.innerHTML;
    }""")
    
    # Extract head metadata
    head_meta = page.evaluate("""() => {
        return {
            title: document.title,
            description: document.querySelector('meta[name="description"]')?.content || '',
            lang: document.documentElement.lang || 'en',
            htmlClass: document.documentElement.className || '',
            links: Array.from(document.querySelectorAll('link[rel="icon"], link[rel="apple-touch-icon"], link[rel="preload"][as="font"]')).map(l => ({
                rel: l.rel,
                href: l.href,
                media: l.media || '',
                as: l.getAttribute('as') || '',
                type: l.type || '',
            })),
            fonts: Array.from(document.querySelectorAll('link[href*="fonts.googleapis.com"], link[href*="fonts.gstatic.com"]')).map(l => l.href),
        };
    }""")
    
    return {
        'css': css,
        'root_vars': root_vars,
        'body_html': body_html,
        'head_meta': head_meta,
    }
```

## CSS Deduplication Across Pages

When extracting multiple pages from the same site, most CSS is shared:

1. **Extract CSS from homepage first** — this becomes the base `globals.css`
2. **For each subpage, diff its CSS against the homepage CSS:**
   - Shared rules → already in globals.css (skip)
   - New rules (page-specific) → append to globals.css
3. **:root custom properties:** Merge all pages' :root vars into one block
4. **@font-face rules:** Deduplicate (same font-family = same rule)

This prevents globals.css from bloating with duplicate rules.

## URL Normalization

When building routes from discovered URLs:

```
https://www.example.com/pricing       → /pricing
https://www.example.com/about/        → /about
https://www.example.com/features/chat → /features/chat
https://www.example.com/              → / (homepage)
https://www.example.com/#section      → skip (anchor, not a page)
https://www.example.com/blog/post-1   → /blog/post-1 (if prioritized)
```

## Route-to-Page Mapping

Map discovered pages to Next.js App Router structure:

```
/              → app/page.tsx
/pricing       → app/pricing/page.tsx
/about         → app/about/page.tsx
/features/chat → app/features/chat/page.tsx
/blog          → app/blog/page.tsx
```

## Shared Component Detection

After extracting all pages, compare their body HTML:

1. **Navbar detection:** Extract the first major element from each page's body. 
   If >85% similar across pages → shared Navbar component.
   
2. **Footer detection:** Extract the last major element from each page's body.
   If >85% similar across pages → shared Footer component.

3. **Canonical extraction:** Use the homepage's version as the canonical shared component.

4. **Page-specific content:** Everything between Navbar and Footer is page-specific.

## Error Handling

- **Page load timeout:** Skip the page, add to "failed pages" list in report
- **JavaScript errors:** Ignore (page may still render useful content)
- **Redirect loops:** Detect if URL redirects back to homepage, skip
- **Login walls:** If page has no meaningful content (< 100 chars of text), skip
- **Rate limiting:** Add 1-second delay between page visits
- **Max time budget:** 2 minutes per page, 15 minutes total for discovery + extraction

---
name: frontend-ui-clone
version: 2.0.0
description: |
  Pixel-perfect website cloner. Given a URL, faithfully reproduces the page as a single
  self-contained HTML file. Uses Playwright to render the page in a real browser, then
  directly extracts the rendered DOM + all computed CSS — no manual rewriting.
  Handles static HTML, JS-rendered SPAs, Webflow, Next.js, and any framework automatically.
  Zero creative interpretation — reproduces exactly what exists.
  Use when asked to "clone this site", "copy this page", "replicate this URL",
  "pixel-perfect clone", or user provides a URL and says "make it look exactly like this".
user-invocable: true
disable-model-invocation: false
context: fork
agent: general-purpose
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - WebFetch
  - WebSearch
  - AskUserQuestion
argument-hint: "<url> [options]"
---

You are a **pixel-perfect website cloner**. Your ONLY job is faithful reproduction.
You do NOT redesign, improve, or reinterpret. You reproduce EXACTLY what exists.

**Language rule:** Mirror the user's language for all non-code text. CSS/HTML/JS always English.

**User request:** $ARGUMENTS

---

## CORE PRINCIPLE — ZERO CREATIVE LIBERTY

You are a photocopier, not a designer. Every decision must answer: "does this match the original?"

- If the original uses Inter → use Inter (not a "better" font)
- If the original has 3 equal columns → build 3 equal columns
- If the original uses `#000000` on `#ffffff` → use exactly that
- If the original has 12 sections → clone all 12, in order, none skipped or merged
- If the original text says "Get Started Free" → write "Get Started Free" (not "Start Now")

---

## Phase 1 — Parse Input, Detect Tools & Determine Strategy

### Step 1 — Extract URL

Parse `$ARGUMENTS` for a URL (starts with `http://` or `https://`).
- URL found → store as `TARGET_URL`, extract domain for filename
- No URL found → ask with `AskUserQuestion`: "Please provide the URL of the website you want to clone."

### Step 2 — Output path

Output directory: `$(pwd)/test_outputs/`. Create if needed (`mkdir -p`).
After creating the directory, ensure a `.gitignore` exists so artifacts are not accidentally committed:
```bash
mkdir -p "$(pwd)/test_outputs" && [ -f "$(pwd)/test_outputs/.gitignore" ] || echo '*' > "$(pwd)/test_outputs/.gitignore"
```

Filename: `clone-[domain].html`
- `[domain]` = hostname without `www.` and without TLD (e.g., `linear` from `linear.app`, `stripe` from `stripe.com`)
- Collision: if file exists, append `-02`, `-03`, etc.

### Step 3 — Tool Availability Detection

**Run these checks FIRST, before any fetching.** The result determines which Phase to enter.

```bash
# Check all tools in parallel
python3 -c "from playwright.sync_api import sync_playwright; print('playwright:ok')" 2>/dev/null || echo "playwright:no"
which firecrawl >/dev/null 2>&1 && echo "firecrawl:ok" || echo "firecrawl:no"
which gstack >/dev/null 2>&1 && echo "gstack:ok" || echo "gstack:no"
which browse >/dev/null 2>&1 && echo "browse:ok" || echo "browse:no"
```

### Step 4 — Strategy Selection

**Six levels, in strict priority order. Use the HIGHEST available level.**

```
Level 1   Playwright DOM + CSS             → ~97% fidelity  (Phase 2)   — static/SSR/Webflow sites
Level 1a  Playwright Hybrid (CSS + fixes)  → ~90% fidelity  (Phase 2)   — Tailwind important:true sites
Level 1b  Playwright Full Style Bake       → ~80% fidelity  (Phase 2)   — last resort when 1a fails
Level 2   Firecrawl + CSS Download         → ~85% fidelity  (Phase 2-B)
Level 3   gstack/browse + CSS Download     → ~80% fidelity  (Phase 2-C)
Level 4   WebFetch + CSS Reconstruction    → ~70% fidelity  (Phase 2-D)
Level 5   WebSearch Research Only          → ~50% fidelity  (Phase 2-E)
```

**All levels output editable `.html` files.**

| Available Tools | Level | Method |
|----------------|-------|--------|
| Playwright ✓ | **Level 1** | Render → extract DOM + all CSS → assemble .html |
| Playwright ✓, Level 1 hero blank | **Level 1a** | Keep original CSS + remove invisible overlays + targeted `!important` overrides |
| Playwright ✓, Level 1a still broken | **Level 1b** | Bake essential computed styles into inline → assemble .html WITHOUT original CSS |
| Firecrawl ✓, Playwright ✗ | **Level 2** | Firecrawl scrape (html/rawHtml/markdown) + download external CSS files + manual assembly |
| gstack or browse ✓, above ✗ | **Level 3** | Headless screenshot + DOM eval + download CSS + reconstruct from screenshot |
| Only WebFetch | **Level 4** | HTTP fetch HTML → detect SPA → if static: extract CSS + rebuild; if SPA: escalate to WebSearch |
| Nothing works | **Level 5** | WebSearch for screenshots/design system info → manual reconstruction from research |

**Level 1 → 1a → 1b auto-escalation chain:**

After assembling Level 1 output, screenshot the clone and check hero visibility:

```python
# Auto-escalation detection
page_c = browser.new_page(viewport={"width": 1440, "height": 900})
page_c.goto(f"file://{output_path}", wait_until="load")
page_c.wait_for_timeout(3000)
hero_visible = page_c.evaluate("""() => {
    const el = document.elementFromPoint(720, 400);
    if (!el) return false;
    const text = el.textContent?.trim() || '';
    const cs = getComputedStyle(el);
    return text.length > 10 && cs.opacity !== '0' && cs.display !== 'none';
}""")
page_c.close()
```

- If hero is blank → **escalate to Level 1a** (hybrid: keep CSS, remove overlays, add overrides)
- If Level 1a hero still blank → **escalate to Level 1b** (targeted style bake)
- Level 1a is the preferred fix for Tailwind `important: true` sites (preserves responsive layout)

**Announce the strategy before proceeding:**
```
Tool check: Playwright [✓/✗]  Firecrawl [✓/✗]  gstack [✓/✗]  browse [✓/✗]
Strategy:   Level [N] — [method name]
Expected fidelity: ~[X]%
```

---

## Phase 2 — Page Extraction (branched by Level)

### Level 1 — Playwright DOM + CSS Extraction (~97% fidelity)

**Primary method for most sites.** Render the page in a real Chromium browser, scroll through
to trigger all lazy loading and animations, then extract the complete rendered DOM and all CSS.
Output is an editable `.html` file.

**Best for:** Static sites, Webflow, WordPress, Next.js SSR/SSG, Vue/Nuxt SSR — any site where
content is present in the HTML DOM after JS execution.

### Step 1 — Render & Scroll

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    # Navigation with fallback: networkidle → domcontentloaded
    # Many SPA/Next.js sites have persistent connections that block networkidle
    try:
        page.goto(TARGET_URL, wait_until="networkidle", timeout=30000)
    except:
        page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(8000)

    # Scroll through entire page TWICE to trigger all lazy loading.
    # First pass triggers intersection observers; second pass catches elements
    # that only load after neighbors become visible (progressive reveal).
    # Scroll THREE targets: window, body, AND inner scroll containers.
    # Many SPA sites (wondering.app, etc.) use a fixed-position wrapper with an
    # overflow-y-auto child as the actual scroll container. IntersectionObservers
    # fire on THAT container, not on window/body. If we don't scroll it, all
    # scroll-reveal animations stay at their initial state (opacity:0).
    page.evaluate("""async () => {
        const delay = ms => new Promise(r => setTimeout(r, ms));

        // Detect inner scroll containers
        const scrollContainers = [
            ...document.querySelectorAll('[class*="overflow-y-auto"], [class*="overflow-auto"], [class*="scrollbar"]')
        ].filter(el => el.scrollHeight > el.clientHeight + 100);

        for (let pass = 0; pass < 2; pass++) {
            // Scroll window + body
            const h = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);
            for (let y = 0; y < h; y += 400) {
                window.scrollTo(0, y);
                document.body.scrollTo(0, y);
                await delay(pass === 0 ? 150 : 100);
            }

            // Scroll each inner container
            for (const sc of scrollContainers) {
                for (let y = 0; y < sc.scrollHeight; y += 400) {
                    sc.scrollTop = y;
                    await delay(pass === 0 ? 150 : 100);
                }
                sc.scrollTop = 0;
            }

            window.scrollTo(0, 0);
            document.body.scrollTo(0, 0);
            await delay(1000);
        }
    }""")
    page.wait_for_timeout(3000)

    # Reset page to neutral state before extraction:
    # - Move mouse to corner (avoids capturing hover states)
    # - Blur active element (avoids capturing focus states)
    # - Scroll to top
    page.mouse.move(0, 0)
    page.evaluate("() => { document.activeElement?.blur(); window.scrollTo(0,0); document.body.scrollTo(0,0); }")
    page.wait_for_timeout(500)
```

### Step 1.5 — Pre-Extraction Reconnaissance

Run all reconnaissance BEFORE mutating the DOM. This step is **read-only** — it observes
the page in its natural state and stores findings for use in later steps.

#### 1.5a — Behavior Sweep

Discover scroll-triggered animations, hover effects, click-driven components, and responsive breakpoints.

```python
    # --- Scroll sweep: detect scroll-triggered animations & sticky elements ---
    scroll_behaviors = page.evaluate("""async () => {
        const found = {scroll_reveals: [], sticky: [], scroll_snap: [], parallax: []};
        // Snapshot animation-candidate elements before scroll
        const before = new Map();
        document.querySelectorAll('[class*="animate"], [data-aos], [data-scroll], [data-sal], [class*="reveal"], [class*="fade"]').forEach(el => {
            before.set(el, {opacity: getComputedStyle(el).opacity, transform: getComputedStyle(el).transform});
        });
        // Scroll to bottom and back
        const h = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);
        for (let y = 0; y < h; y += 600) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 100)); }
        // Check what changed after scroll
        before.forEach((prev, el) => {
            const now = getComputedStyle(el);
            if (prev.opacity !== now.opacity || prev.transform !== now.transform)
                found.scroll_reveals.push({cls: (el.className||'').toString().slice(0,60), from: prev.opacity, to: now.opacity});
        });
        // Detect sticky/fixed elements
        document.querySelectorAll('nav, header, [class*="sticky"], [class*="fixed"]').forEach(el => {
            const pos = getComputedStyle(el).position;
            if (pos === 'sticky' || pos === 'fixed')
                found.sticky.push({tag: el.tagName, cls: (el.className||'').toString().slice(0,40), position: pos});
        });
        // Detect scroll-snap containers
        document.querySelectorAll('*').forEach(el => {
            const snap = getComputedStyle(el).scrollSnapType;
            if (snap && snap !== 'none') found.scroll_snap.push({cls: (el.className||'').toString().slice(0,40), snap});
        });
        window.scrollTo(0, 0);
        return found;
    }""")

    # --- Hover sweep: detect elements with CSS :hover rules ---
    hover_behaviors = page.evaluate("""() => {
        const found = [];
        const hoverSelectors = new Set();
        for (const sheet of document.styleSheets) {
            try {
                for (const rule of sheet.cssRules) {
                    if (rule.selectorText && rule.selectorText.includes(':hover'))
                        hoverSelectors.add(rule.selectorText.replace(/:hover/g, '').trim());
                }
            } catch(e) {}
        }
        document.querySelectorAll('a, button, [role="button"], [class*="card"], [class*="btn"]').forEach(el => {
            for (const sel of hoverSelectors) {
                try { if (el.matches(sel)) { found.push({tag: el.tagName, cls: (el.className||'').toString().slice(0,40)}); break; } } catch(e) {}
            }
        });
        return found.slice(0, 30);
    }""")

    # --- Click sweep: detect expandable/toggleable/tab elements ---
    click_behaviors = page.evaluate("""() => {
        const found = [];
        document.querySelectorAll(
            'details, [class*="accordion"], [class*="collapse"], [class*="toggle"], ' +
            '[role="tab"], [role="tablist"], [data-state], [class*="tab-trigger"]'
        ).forEach(el => {
            found.push({tag: el.tagName, cls: (el.className||'').toString().slice(0,60),
                role: el.getAttribute('role'), state: el.getAttribute('data-state'),
                open: el.hasAttribute('open')});
        });
        return found;
    }""")

    # --- Responsive sweep: count @media breakpoint rules ---
    responsive_info = page.evaluate("""() => {
        let mediaRules = 0;
        const breakpoints = new Set();
        for (const sheet of document.styleSheets) {
            try {
                for (const rule of sheet.cssRules) {
                    if (rule.type === CSSRule.MEDIA_RULE && rule.conditionText) {
                        const m = rule.conditionText.match(/max-width:\s*(\d+)/);
                        if (m) { mediaRules++; breakpoints.add(parseInt(m[1])); }
                    }
                }
            } catch(e) {}
        }
        return {count: mediaRules, breakpoints: [...breakpoints].sort((a,b) => b-a).slice(0,5)};
    }""")
```

#### 1.5b — Page Topology Map

Generate a section map with names, boundaries, z-index, and detected interaction model.
Used in Phase 3 for section-based comparison and in Phase 4 for the clone report.

```python
    topology = page.evaluate("""() => {
        const sections = [];
        document.querySelectorAll('nav, header, section, footer, main, [role="banner"], [role="main"], [role="contentinfo"]').forEach((el, i) => {
            const rect = el.getBoundingClientRect();
            const cs = getComputedStyle(el);
            const hasInteractive = el.querySelector(
                '[class*="carousel"], [class*="accordion"], [class*="tab"], [role="tablist"], ' +
                '[class*="swiper"], [class*="slider"], details'
            );
            sections.push({
                idx: i, tag: el.tagName, id: el.id || null,
                cls: (el.className||'').toString().slice(0,60),
                y: Math.round(rect.top + window.scrollY),
                h: Math.round(rect.height),
                z: parseInt(cs.zIndex) || 0,
                position: cs.position,
                bg: cs.backgroundColor !== 'rgba(0, 0, 0, 0)' ? cs.backgroundColor : null,
                interaction: hasInteractive ? 'interactive' : 'static'
            });
        });
        return sections;
    }""")
```

#### 1.5c — Layered Asset Detection

Detect multi-layer image compositions (background + foreground + overlay).
Missing an overlay image makes an entire section look "empty".

```python
    layered_assets = page.evaluate("""() => {
        const stacks = [];
        document.querySelectorAll('section, [class*="hero"], [class*="banner"], [class*="cta"]').forEach(container => {
            const layers = [];
            // Check container's own background
            const containerBg = getComputedStyle(container).backgroundImage;
            if (containerBg && containerBg !== 'none')
                layers.push({type: 'bg', url: containerBg.slice(0,100), z: 0});
            // Check all positioned children
            container.querySelectorAll('img, video, canvas').forEach(el => {
                const cs = getComputedStyle(el);
                if (cs.position === 'absolute' || cs.position === 'fixed')
                    layers.push({type: el.tagName.toLowerCase(), src: (el.src||'').slice(0,100),
                        z: parseInt(cs.zIndex)||0, w: el.offsetWidth, h: el.offsetHeight});
            });
            if (layers.length > 1)
                stacks.push({container: (container.className||'').toString().slice(0,40), layers});
        });
        return stacks;
    }""")
```

#### 1.5d — Media & Library Pre-check

Detect video, Lottie, WebGL canvas, and smooth scroll libraries before extraction.

```python
    media_precheck = page.evaluate("""() => {
        const found = {videos: [], lotties: [], webgl: false, scroll_libs: []};
        document.querySelectorAll('video').forEach(v => {
            found.videos.push({src: v.src || v.querySelector('source')?.src || '',
                w: v.offsetWidth, h: v.offsetHeight, autoplay: v.autoplay, loop: v.loop});
        });
        document.querySelectorAll('lottie-player, [class*="lottie"], dotlottie-player').forEach(el => {
            found.lotties.push({src: el.getAttribute('src') || '', cls: (el.className||'').toString().slice(0,40)});
        });
        document.querySelectorAll('canvas').forEach(c => {
            try { if (c.getContext('webgl') || c.getContext('webgl2')) found.webgl = true; } catch(e) {}
        });
        ['lenis', 'locomotive-scroll', 'smooth-scroll', 'simplebar'].forEach(cls => {
            if (document.querySelector('[class*="' + cls + '"]') || document.querySelector('[data-' + cls + ']'))
                found.scroll_libs.push(cls);
        });
        return found;
    }""")

    # If smooth scroll library detected, reset frozen scroll transform before extraction
    if media_precheck.get('scroll_libs'):
        page.evaluate("""() => {
            document.querySelectorAll('.lenis, .locomotive-scroll, [data-scroll-container], [class*="smooth-scroll"]').forEach(el => {
                el.style.setProperty('transform', 'none', 'important');
            });
        }""")
```

#### 1.5e — SVG Icon Detection

Catalog inline SVGs for awareness in assembly and potential Next.js component extraction.

```python
    svg_info = page.evaluate("""() => {
        let total = 0, iconSized = 0;
        const viewBoxes = new Set();
        document.querySelectorAll('svg:not(img svg)').forEach(svg => {
            total++;
            const rect = svg.getBoundingClientRect();
            const w = parseInt(svg.getAttribute('width') || rect.width);
            const h = parseInt(svg.getAttribute('height') || rect.height);
            if (w < 100 && h < 100) { iconSized++; viewBoxes.add(svg.getAttribute('viewBox')||''); }
        });
        return {total, iconSized, unique: viewBoxes.size};
    }""")

    # Store all recon results
    recon = {
        'scroll_behaviors': scroll_behaviors,
        'hover_behaviors': hover_behaviors,
        'click_behaviors': click_behaviors,
        'responsive_info': responsive_info,
        'topology': topology,
        'layered_assets': layered_assets,
        'media_precheck': media_precheck,
        'svg_info': svg_info,
    }
```

**Announce recon findings before proceeding:**
```
Recon: [N] sections mapped | [N] scroll animations | [N] hover elements |
       [N] tabs/accordions | [N] responsive breakpoints | [N] layered stacks |
       Videos: [N] | Lottie: [N] | Scroll lib: [name/none] | SVGs: [N] total ([N] icons)
```

### Step 2 — Force Visibility & Remove Invisible Overlays

Many sites use `content-visibility: auto`, Webflow animations, or JS-driven reveal
that hide off-screen content. Also, SPA sites (Next.js, React) often have large invisible
overlay panels (editor panels, chat UIs, onboarding flows) with `opacity: 0` that cover
the landing page content. These must be **removed** before extraction.

```python
    page.evaluate("""() => {
        document.querySelectorAll('*').forEach(el => {
            const cs = getComputedStyle(el);
            const cls = (el.className || '').toString();
            const clsLow = cls.toLowerCase();
            const id = (el.id || '').toLowerCase();

            // Skip elements that should stay hidden (modals, overlays, dropdowns)
            const keepHidden = ['modal', 'overlay', 'popup', 'dropdown-list',
                                'mobile-menu', 'w-nav-overlay'];
            if (keepHidden.some(k => clsLow.includes(k) || id.includes(k))) return;

            // REMOVE large invisible overlays (SPA editor panels, chat UIs, etc.)
            // These are full-screen panels with opacity-0 that cover landing page content.
            // On Tailwind important:true sites, opacity-0 wins over inline style overrides.
            // Safety: only remove if it does NOT contain headings (real content sections
            // may also use opacity-0 as a scroll-animation initial state).
            if (cls.includes('opacity-0') && el.offsetWidth > 500 && el.offsetHeight > 500) {
                const hasContent = el.querySelector('h1, h2, h3, article, [role="main"]');
                if (!hasContent) {
                    el.remove();
                    return;
                }
            }

            // Force opacity on animation-hidden elements
            if (parseFloat(cs.opacity) < 0.1) {
                el.style.setProperty('opacity', '1', 'important');
            }
        });

        // Fix lazy loaded images (data-lazy-src, data-src, Next.js data-nimg)
        document.querySelectorAll('img[data-lazy-src], img[data-src]').forEach(img => {
            const real = img.getAttribute('data-lazy-src') || img.getAttribute('data-src');
            if (real && (!img.src || img.src.startsWith('data:')))
                img.src = real;
        });

        // Fix <source> srcset in <picture> elements
        document.querySelectorAll('picture source[srcset]').forEach(src => {
            // Will be fixed to absolute URLs in Step 4 assembly
        });

        // Remove cookie consent / notification banners
        document.querySelectorAll(
            '[class*="cookie"], [class*="consent"], [class*="gdpr"], ' +
            '[id*="cookie"], [id*="consent"], [id*="gdpr"], ' +
            '[class*="CookieBanner"], [aria-label*="cookie"]'
        ).forEach(el => el.remove());

        // Remove overflow hidden from body/html
        document.body.style.overflow = 'auto';
        document.documentElement.style.overflow = 'auto';
    }""")
    page.wait_for_timeout(2000)
```

### Step 3 — Extract CSS, DOM, Custom Properties & Fonts

```python
    # 3a. Extract all stylesheets as text
    styles = page.evaluate("""() => {
        const sheets = [];
        for (const sheet of document.styleSheets) {
            try {
                const rules = [];
                for (const rule of sheet.cssRules) rules.push(rule.cssText);
                sheets.push(rules.join('\\n'));
            } catch(e) {
                // Cross-origin: keep as @import
                if (sheet.href) sheets.push('@import url("' + sheet.href + '");');
            }
        }
        return sheets;
    }""")

    # 3b. Extract font-face rules
    fonts = page.evaluate("""() => {
        const fonts = [];
        for (const sheet of document.styleSheets) {
            try {
                for (const rule of sheet.cssRules) {
                    if (rule.type === CSSRule.FONT_FACE_RULE) fonts.push(rule.cssText);
                }
            } catch(e) {}
        }
        return fonts;
    }""")

    # 3c. Extract ALL :root CSS custom properties (CRITICAL for fidelity).
    # Modern sites (Tailwind v4, shadcn/ui) define 100-300+ custom properties
    # on :root. If @layer ordering breaks in the clone, var() references fail
    # silently. We extract the RESOLVED values and inject as a fallback :root
    # block, ensuring all var() references work regardless of cascade issues.
    root_vars = page.evaluate("""() => {
        const vars = {};
        const walk = (rules) => {
            for (const rule of rules) {
                if (rule.selectorText && rule.selectorText.includes(':root')) {
                    for (let i = 0; i < rule.style.length; i++) {
                        const prop = rule.style[i];
                        if (prop.startsWith('--')) {
                            vars[prop] = rule.style.getPropertyValue(prop).trim();
                        }
                    }
                }
                // Recurse into @layer, @media, @supports blocks
                if (rule.cssRules) walk(rule.cssRules);
            }
        };
        for (const sheet of document.styleSheets) {
            try { walk(sheet.cssRules); } catch(e) {}
        }
        return vars;
    }""")
    # root_vars now has {"--background": "45 40% 98%", "--foreground": "0 0% 11%", ...}
    # Will be injected in Step 4 assembly

    # 3d. Extract <link> tags from <head> (fonts, preloads)
    # These are lost when we extract only the <body>. Keep font links for correct rendering.
    head_links = page.evaluate("""() => {
        const links = [];
        document.querySelectorAll('head link').forEach(link => {
            const rel = (link.rel || '').toLowerCase();
            const href = link.href || '';
            // Keep: font stylesheets, font preloads, favicons
            if (rel === 'stylesheet' && (href.includes('fonts.googleapis') || href.includes('fonts.gstatic'))) {
                links.push(link.outerHTML);
            } else if (rel === 'preload' && link.as === 'font') {
                links.push(link.outerHTML);
            } else if (rel === 'icon' || rel === 'shortcut icon' || rel === 'apple-touch-icon') {
                links.push(link.outerHTML);
            }
        });
        return links;
    }""")

    # 3e. Snapshot gradient text elements BEFORE DOM extraction.
    # CSS gradient-text (background-clip:text + -webkit-text-fill-color:transparent)
    # uses CSS custom properties for the gradient that may not resolve in the clone.
    # Capture the actual COMPUTED gradient-image value and bake as inline style.
    page.evaluate("""() => {
        document.querySelectorAll('*').forEach(el => {
            const cs = getComputedStyle(el);
            const bgClip = cs.webkitBackgroundClip || cs.backgroundClip;
            const textFill = cs.webkitTextFillColor;
            if (bgClip === 'text' && textFill === 'transparent') {
                const bgImage = cs.backgroundImage;
                if (bgImage && bgImage !== 'none') {
                    el.style.backgroundImage = bgImage;
                    el.style.webkitBackgroundClip = 'text';
                    el.style.backgroundClip = 'text';
                    el.style.webkitTextFillColor = 'transparent';
                    el.style.color = 'transparent';
                }
            }
        });
    }""")

    # 3f. Reset transform on animation-hidden elements.
    # Many scroll-reveal animations set initial state: opacity:0 + translateY(20px).
    # Step 2 fixed opacity but left the transform, causing 20px positioning shifts.
    page.evaluate("""() => {
        document.querySelectorAll('*').forEach(el => {
            const cs = getComputedStyle(el);
            if (parseFloat(cs.opacity) <= 0.1) {
                const t = cs.transform;
                if (t && t !== 'none' && t !== 'matrix(1, 0, 0, 1, 0, 0)') {
                    // Only reset translateY-style transforms (not carousel/rotation)
                    // translateY transforms have matrix format: matrix(1, 0, 0, 1, 0, Y)
                    const m = t.match(/matrix\\(([^)]+)\\)/);
                    if (m) {
                        const vals = m[1].split(',').map(v => parseFloat(v.trim()));
                        // Pure translation: a=1, b=0, c=0, d=1
                        if (Math.abs(vals[0]-1)<0.01 && Math.abs(vals[1])<0.01 &&
                            Math.abs(vals[2])<0.01 && Math.abs(vals[3]-1)<0.01) {
                            el.style.setProperty('transform', 'none', 'important');
                        }
                    }
                }
            }
        });
    }""")

    # 3g. Remove loading="lazy" — won't trigger in file:// context
    page.evaluate("""() => {
        document.querySelectorAll('img[loading="lazy"]').forEach(img => {
            img.removeAttribute('loading');
        });
    }""")

    # Extract full rendered DOM (with all the above fixes baked in)
    html = page.evaluate("() => document.documentElement.outerHTML")

    # Take reference screenshots for later comparison
    page.screenshot(path="/tmp/clone-original-viewport.png")
    page.screenshot(path="/tmp/clone-original-full.png", full_page=True)

    browser.close()
```

### Step 3.4 — Interaction Model Determination (MANDATORY GATE)

**Before detecting or extracting ANY interactive component, determine its interaction model.**
This is the #1 most expensive mistake in cloning — building click-tabs when the original is
scroll-driven (or vice versa) requires a complete rewrite, not a CSS fix.

For each section marked `interaction: 'interactive'` in the topology (Step 1.5b):

1. **Check scroll_behaviors first** (Step 1.5a): if the section appears in `scroll_reveals`,
   it is scroll-driven. Extract the mechanism: `IntersectionObserver`, `scroll-snap`,
   `position: sticky`, `animation-timeline`, or JS scroll listeners.
2. **Only if NOT scroll-driven**, check `click_behaviors`: if it has `[role="tab"]`,
   `[data-state]`, or accordion triggers, it is click-driven.
3. **Label each interactive section explicitly:**

```python
    # Determine interaction model for each interactive section
    for section in recon['topology']:
        if section['interaction'] != 'interactive':
            section['model'] = 'static'
            continue
        # Check if any scroll-reveal overlaps this section's y range
        scroll_driven = any(
            sr.get('cls','') in section.get('cls','')
            for sr in recon['scroll_behaviors'].get('scroll_reveals', [])
        )
        if scroll_driven:
            section['model'] = 'scroll-driven'
        elif any(cb.get('cls','') for cb in recon['click_behaviors']
                 if cb.get('role') == 'tab' or cb.get('state')):
            section['model'] = 'click-driven'
        else:
            section['model'] = 'time-driven'  # auto-carousel, typewriter
```

**Announce before proceeding:**
```
Interaction models:
  Section [N] "cls": scroll-driven (IntersectionObserver)
  Section [M] "cls": click-driven (tabs with data-state)
  Section [K] "cls": time-driven (auto-carousel)
```

This determination feeds into Step 3.5 (what to detect) and Step 4 (what scripts to inject).

### Step 3.5 — Detect JS-Driven Interactive Elements (BEFORE extraction)

**CRITICAL STEP.** Before extracting DOM, identify elements that rely on JS for display.
These will break in the static clone and need replacement scripts injected.

```python
    interactive = page.evaluate("""() => {
        const result = {carousels: [], typewriters: [], canvases: [], accordions: []};

        // 1. CAROUSELS / SLIDERS: elements with scroll/slide animations or swiper/embla
        document.querySelectorAll('[class*="carousel"], [class*="swiper"], [class*="embla"], [class*="slider"]').forEach(el => {
            const cs = getComputedStyle(el);
            result.carousels.push({
                cls: (el.className||'').toString().slice(0,80),
                w: el.offsetWidth,
                animation: cs.animationName,
                children: el.children.length,
                childrenPerPage: 0 // filled below
            });
        });
        // Also detect multi-page grid carousels: parent with multiple same-class grid children stacked
        document.querySelectorAll('[class*="grid-cols"]').forEach(g => {
            const siblings = g.parentElement ? Array.from(g.parentElement.children).filter(
                c => c.className === g.className
            ) : [];
            if (siblings.length > 1) {
                result.carousels.push({
                    type: 'stacked-grid',
                    cls: (g.className||'').toString().slice(0,60),
                    pages: siblings.length,
                    itemsPerPage: g.children.length,
                    parentCls: (g.parentElement.className||'').slice(0,60)
                });
            }
        });

        // 2. TYPEWRITER / ROTATING TEXT: text that changes over time
        // Pattern A: overlay span inside an input-box container (e.g. MagicPath, Perplexity)
        //   - An <input> with transparent text sits on top of a <span> that shows animated text
        //   - The span text changes via JS (character-by-character typing + deleting)
        // Pattern B: standalone element with text that swaps on interval
        // IMPORTANT: text length check must be lenient (>= 1, not > 10) because the
        // span may be mid-typing (e.g. "A re" instead of full prompt) at capture time.
        // Instead, detect the STRUCTURE: transparent input + sibling span = typewriter.
        document.querySelectorAll('input, textarea, [class*="input"], [class*="prompt"], [class*="landing"]').forEach(el => {
            const rect = el.getBoundingClientRect();
            if (rect.top < 600 && el.offsetWidth > 300) {
                const parent = el.closest('[class*="input-box"], [class*="search"], [class*="landing-input"]') || el.parentElement;
                const overlaySpan = parent?.querySelector('span, [class*="text"]');
                // Detect by structure: input with transparent/caret-transparent text + sibling span
                const isTransparentInput = el.tagName === 'INPUT' && (
                    (el.className||'').includes('text-transparent') ||
                    (el.className||'').includes('caret-transparent') ||
                    getComputedStyle(el).color === 'transparent'
                );
                if (overlaySpan && (overlaySpan.textContent.trim().length >= 1 || isTransparentInput)) {
                    result.typewriters.push({
                        text: overlaySpan.textContent.trim().slice(0, 60),
                        parentCls: (parent.className||'').slice(0, 60),
                        spanSelector: overlaySpan.className ? '.' + overlaySpan.className.split(' ').filter(c=>c).join('.') : 'span',
                        isTransparentInput
                    });
                }
            }
        });

        // 3. CANVAS ELEMENTS: JS-rendered backgrounds/effects
        document.querySelectorAll('canvas').forEach(c => {
            if (c.offsetWidth > 200 && c.offsetHeight > 200) {
                const parentBg = getComputedStyle(c.parentElement).backgroundColor;
                result.canvases.push({
                    w: c.width, h: c.height,
                    parentBg,
                    parentCls: (c.parentElement.className||'').slice(0, 60)
                });
            }
        });

        // 4. ACCORDIONS: collapsed FAQ/toggle sections
        document.querySelectorAll('[class*="accordion"], [class*="faq"], details').forEach(el => {
            result.accordions.push({
                tag: el.tagName,
                cls: (el.className||'').toString().slice(0, 60),
                open: el.hasAttribute('open') || el.classList.contains('open')
            });
        });

        // 5. MARQUEE / INFINITE-SCROLL: logo strips, ticker tapes
        document.querySelectorAll('[class*="animate-infinite"], [class*="marquee"], [class*="ticker"], [class*="infinite-scroll"]').forEach(el => {
            const cs = getComputedStyle(el);
            result.marquees = result.marquees || [];
            result.marquees.push({
                cls: (el.className||'').toString().slice(0, 80),
                animation: cs.animationName,
                duration: cs.animationDuration,
                display: cs.display,
                w: el.offsetWidth,
                children: el.children.length,
                imgCount: el.querySelectorAll('img').length,
                svgCount: el.querySelectorAll('svg').length
            });
        });

        return result;
    }""")
```

**Record all findings. They will be used in Step 4 to inject replacement scripts.**

**For detected marquees:** Extract the `@keyframes` name and definition from the page CSS.
If the keyframes use a generic name (e.g. `scroll`), ensure the definition is included in
the clone's CSS, and add an explicit restoration rule:
```css
@keyframes scroll {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}
.animate-infinite-scroll {
  animation: scroll [duration] linear infinite !important;
  display: flex !important;
}
```

**CRITICAL: Use specific class selectors, NOT scoped/generated class names.**
Sites using styled-jsx, CSS Modules, or Tailwind generate scoped class names
(e.g. `.jsx-21bbd1bc18f6137e`) that are shared across multiple unrelated elements
within the same component scope. If you inject a rule like:
```css
/* ❌ BAD: .jsx-xxx applies to ALL elements in the scope, not just the marquee */
.jsx-21bbd1bc18f6137e { display: flex !important; animation: scroll 120s linear infinite; }
```
it will break sibling elements (e.g. a heading div that should be `display: block`).
Always target the functional class instead:
```css
/* ✅ GOOD: only targets the actual marquee container */
.animate-infinite-scroll { display: flex !important; animation: scroll 120s linear infinite; }
```

### Step 3.5b — Multi-State Extraction (tabs, accordions, toggles)

Using `click_behaviors` from Step 1.5a, expand all collapsed content and capture tab states
**before** final DOM extraction. This ensures the clone contains all content, not just the default state.

```python
    tab_contents = {}
    if recon.get('click_behaviors'):
        # 1. Open all collapsed accordion/details elements
        page.evaluate("""() => {
            document.querySelectorAll('details:not([open])').forEach(d => d.setAttribute('open', ''));
            document.querySelectorAll('[data-state="closed"]').forEach(el => {
                el.setAttribute('data-state', 'open');
                el.style.setProperty('display', 'block', 'important');
                el.style.setProperty('height', 'auto', 'important');
            });
        }""")
        page.wait_for_timeout(500)

        # 2. Click each tab — capture panel content AND CSS diff (State A → State B)
        tab_contents = page.evaluate("""async () => {
            const panels = {};
            const tabs = document.querySelectorAll('[role="tab"], [class*="tab-trigger"], [data-tab]');
            if (!tabs.length) return panels;

            // Capture State A (default tab) styles on key elements
            const captureStyles = () => {
                const panel = document.querySelector(
                    '[role="tabpanel"]:not([hidden]), [data-state="active"], [class*="tab-content"]:not([hidden])'
                );
                if (!panel) return null;
                const cs = getComputedStyle(panel);
                return {
                    html: panel.innerHTML.slice(0, 3000),
                    styles: {opacity: cs.opacity, transform: cs.transform, display: cs.display, visibility: cs.visibility}
                };
            };

            const stateA = captureStyles();

            for (const tab of tabs) {
                const label = tab.textContent.trim().slice(0, 30);
                tab.click();
                await new Promise(r => setTimeout(r, 400));
                const stateB = captureStyles();
                if (stateB) {
                    panels[label] = {
                        html: stateB.html,
                        // Record CSS diff: what changed between states
                        cssDiff: stateA ? Object.fromEntries(
                            Object.entries(stateB.styles).filter(([k,v]) => stateA.styles[k] !== v)
                                .map(([k,v]) => [k, {from: stateA.styles[k], to: v}])
                        ) : {},
                        // Capture transition property for animation reproduction
                        transition: stateB.styles ? getComputedStyle(
                            document.querySelector('[role="tabpanel"]:not([hidden])') || document.body
                        ).transition : 'none'
                    };
                }
            }
            // Restore default state: click first tab back
            tabs[0].click();
            await new Promise(r => setTimeout(r, 300));
            return panels;
        }""")
```

`tab_contents` includes per-tab HTML content, CSS state diffs (property: from→to), and
transition timing. Use CSS diffs to reproduce tab-switch animations in the clone.
If `cssDiff` shows `opacity: {from: "0", to: "1"}` with `transition: "opacity 0.3s ease"`,
inject matching CSS transitions in Step 4.

### Step 3.6 — Capture Typewriter Prompts

If typewriters were detected, watch the text change to capture all rotating prompts.
Watch for 30+ seconds to capture a full cycle (typical cycle = 4-6 prompts × 3-5s each).

**Key insight:** Typewriter text is captured mid-typing, producing fragments like
"A retro pixel st" alongside complete prompts. Post-process to keep only the LONGEST
version of each prefix — these are the complete prompts.

```python
    if interactive['typewriters']:
        raw_prompts = page.evaluate("""async () => {
            const seen = new Set();
            const spans = document.querySelectorAll(
                '[class*="input-box"] span, [class*="landing-input"] span, ' +
                '[class*="prompt"] span, textarea[placeholder]'
            );
            // Watch for 30 seconds (60 × 500ms) to capture full cycle
            for (let i = 0; i < 60; i++) {
                await new Promise(r => setTimeout(r, 500));
                spans.forEach(s => {
                    const t = s.textContent.trim();
                    if (t.length > 5) seen.add(t);
                });
            }
            return Array.from(seen);
        }""")

        # Post-process: keep only complete prompts (longest version of each prefix)
        # Sort by length descending, then filter out any string that is a prefix of a longer one
        sorted_prompts = sorted(raw_prompts, key=len, reverse=True)
        prompts = []
        for p in sorted_prompts:
            if not any(existing.startswith(p) for existing in prompts):
                prompts.append(p)
        # prompts now contains only complete sentences, e.g.:
        # ["A dark mode mobile app for playing vinyl records",
        #  "A Swiss style dashboard for tracking expenses", ...]
```

### Step 4 — Assemble Self-Contained HTML

Build the output file by:

1. **Extract `<body>` content** — strip all `<script>` tags (tracking, analytics, framework runtime)
2. **Strip viewport-locking classes** — remove `h-screen` and `w-screen` from the first
   wrapper div inside `<body>` (typically a Next.js/SPA root div). These classes constrain
   the page to 100vh, hiding all below-fold content. Use regex on the extracted HTML:
   ```python
   # Strip h-screen/w-screen from wrapper divs (keep other classes)
   # CRITICAL: Use negative lookbehind to avoid breaking min-h-screen, max-h-screen etc.
   body_content = re.sub(r'(?<![\w-])h-screen(?![\w-])', '', body_content)
   body_content = re.sub(r'(?<![\w-])w-screen(?![\w-])', '', body_content)
   # Clean up double spaces in class attributes
   body_content = re.sub(r'class="(\s+)', 'class="', body_content)
   ```
3. **Extract `<body>` attributes** — preserve inline styles, classes, data attributes
4. **Preserve `<html>` attributes** — keep `lang`, `class`, `data-theme`, `dir`, `style` from `<html>`.
   Many sites use `data-theme="light"` or `class="dark"` on `<html>` for CSS selectors to match.
4. **Fix lazy images** — replace `src="data:image/svg..."` with `data-lazy-src` real URLs
5. **Fix relative URLs** — prepend original domain to:
   - `/_next/image?url=...` → parse the `url` param, decode, prepend domain
   - `/_next/static/...`, `/images/...`, `/img/...`, `/cdn-cgi/...` → prepend domain
   - `srcset` attributes: fix each URL in comma-separated srcset values
   - `<source srcset="...">` inside `<picture>` elements
   - CSS `url(/_next/...)`, `url(/img/...)`, `url(/fonts/...)` → prepend domain
6. **Remove tracking/analytics** — strip Google Analytics, Facebook Pixel, Crisp chat, etc.
7. **Filter CSS** — remove `@import` for cross-origin non-essential stylesheets (YouTube, Crisp, widget CSS)
8. **Insert `<head>` links** — add the `head_links` extracted in Step 3d (font stylesheets, preloads,
   favicons) into the output `<head>`. Fix their `href` to absolute URLs.
9. **Inline all CSS into a single `<style>` block** with strict ordering:
   ```
   ┌─────────────────────────────────────────────┐
   │  1. @import rules (MUST be first, or ignored)│
   │  2. @property declarations                   │
   │  3. :root fallback block (from Step 3c)      │
   │  4. @layer declarations                      │
   │  5. @font-face rules                         │
   │  6. All other extracted CSS rules            │
   │  7. Fix overrides (at the very end)          │
   └─────────────────────────────────────────────┘
   ```
   **@import rules** must come before any other rules or they are silently ignored by browsers.
   **:root fallback block:** build from `root_vars` extracted in Step 3c:
   ```css
   :root {
     --background: 45 40% 98%;
     --foreground: 0 0% 11%;
     /* ... all 288 custom properties ... */
   }
   ```
   This ensures ALL `var()` references resolve even if `@layer` ordering breaks.
10. **Add fix overrides** — inject critical CSS fixes **at the very end** (after all framework CSS):

```css
/* === CONTENT VISIBILITY FIX === */
*, section, div {
  content-visibility: visible !important;
  contain-intrinsic-size: auto !important;
}

/* === SCROLL FIX === */
/* CRITICAL: Use overflow: visible, NOT overflow-y: auto.
   Setting overflow-y: auto on BOTH html and body creates two nested scroll
   containers. window.scrollTo() operates on the html element's scroll, but
   body becomes its own scroll container — result: page appears unscrollable.
   overflow: visible lets content flow naturally into the viewport scroll. */
body, html {
  overflow: visible !important;
  height: auto !important;
}

/* === H-SCREEN / W-SCREEN WRAPPER FIX === */
/* Next.js/SPA sites wrap all content in a div.h-screen.w-screen (100vh height).
   This constrains the page to viewport height, hiding all below-fold content.
   CSS overrides alone often fail due to Tailwind important:true specificity
   (e.g. .ck-style .h-screen { height: 100vh !important }).
   THREE-PRONGED FIX:
   1. Strip h-screen/w-screen classes from the wrapper div in HTML (Step 4 assembly)
   2. CSS override with high-specificity selectors (below)
   3. JS runtime fix as fallback (Step 14 script) */
.h-screen, .w-screen,
body > .h-screen,
[class*="ck-style"] .h-screen,
[class*="ck-style"] .w-screen {
  height: auto !important;
  min-height: 100vh !important;
  overflow: visible !important;
}
body.h-screen, body.w-screen {
  height: auto !important;
  min-height: 100vh !important;
  width: 100% !important;
}

/* === SECTION HEIGHT FIX === */
/* NOTE: Do NOT override min-height — it removes min-h-screen from hero sections,
   collapsing the hero gradient background. Only remove max-height caps.
   Do NOT set overflow:visible — it breaks hero background clipping. */
section {
  max-height: none !important;
}

/* === CAROUSEL / SLIDER FIX === */
/* Restore overflow:hidden on carousel containers (they NEED clipping) */
[class*="overflow-hidden"] {
  overflow: hidden !important;
}
/* Hero section also needs overflow:hidden for gradient backgrounds */
section:first-of-type {
  overflow: hidden !important;
}
/* Multi-page stacked grids: only show first page */
/* (selector generated dynamically based on Step 3.5 detection) */

/* === KEEP MODALS HIDDEN === */
.w-nav-overlay, [class*="modal-overlay"] { display: none !important; }

/* === LARGE INVISIBLE OVERLAYS (SPA editor panels) === */
/* Tailwind opacity-0 elements that are large panels should stay hidden */
.opacity-0 { display: none !important; }

/* === CSS ANIMATION FIX — force scroll-reveal animations to end state === */
/* Sites use CSS animations (animate-cascade-drop-in, animate-fade-in, etc.)
   with initial state opacity:0. In a static clone these never complete.
   Force all animated elements to their visible end state.
   CRITICAL: Exclude infinite-scroll/marquee animations — these are continuous
   decorative animations (logo strips, ticker tapes) that should keep running.
   Also: do NOT use display:revert — it converts flex containers to block,
   breaking marquee/carousel horizontal layouts. */
[class*="animate-"]:not([class*="animate-infinite"]):not([class*="animate-marquee"]):not([class*="animate-ticker"]) {
  animation: none !important;
  opacity: 1 !important;
  transform: none !important;
  visibility: visible !important;
}
[class*="cascade-delay"] {
  animation: none !important;
  opacity: 1 !important;
  transform: none !important;
}

/* === MARQUEE / INFINITE-SCROLL ANIMATION PRESERVATION === */
/* Logo strips and ticker tapes use infinite CSS animations (e.g. animate-infinite-scroll).
   These must be explicitly preserved after the blanket animation:none override above.
   The @keyframes name varies by site — detect it in Step 3.5 and inject here. */
.animate-infinite-scroll,
[class*="animate-marquee"],
[class*="animate-ticker"] {
  display: flex !important;
  animation-play-state: running !important;
}

/* === CROSS-ORIGIN SVG IMAGE WIDTH FIX === */
/* SVG images loaded cross-origin (e.g. from /_next/static/media/) with CSS
   width:auto compute to 0px width, making logo marquees invisible.
   CSS aspect-ratio:attr() is unreliable. Use the JS fix below (Step 14)
   combined with this flex-shrink guard. */
.animate-infinite-scroll img,
[class*="animate-infinite"] img {
  width: auto !important;
  flex-shrink: 0 !important;
}
```

11. **Replace YouTube embed iframes with clickable thumbnails** — YouTube `<iframe>` embeds
    fail when the clone is opened from `file://` protocol (CORS/security restrictions).
    Replace each `<iframe src="...youtube.com/embed/VIDEO_ID...">` with a thumbnail image
    overlay + play button that links to the YouTube watch URL:

    ```python
    import re
    def replace_yt_iframe(match):
        full_tag = match.group(0)
        src_match = re.search(r'src="([^"]*youtube\.com/embed/([^?"]+)[^"]*)"', full_tag)
        if not src_match: return full_tag
        video_id = src_match.group(2)
        yt_url = f"https://www.youtube.com/watch?v={video_id}"
        thumb_url = f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"
        cls_match = re.search(r'class="([^"]*)"', full_tag)
        cls = cls_match.group(1) if cls_match else ''
        return f'''<a href="{yt_url}" target="_blank" rel="noopener" class="{cls}"
          style="display:block;position:absolute;inset:0;background:#000;text-decoration:none;">
          <img src="{thumb_url}" style="width:100%;height:100%;object-fit:cover;opacity:0.85;">
          <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;">
            <div style="width:68px;height:48px;background:rgba(255,0,0,0.85);border-radius:12px;
              display:flex;align-items:center;justify-content:center;">
              <div style="width:0;height:0;border-left:18px solid #fff;
                border-top:11px solid transparent;border-bottom:11px solid transparent;margin-left:4px;">
              </div>
            </div>
          </div>
        </a>'''
    body_content = re.sub(r'<iframe[^>]*youtube\.com/embed[^>]*(?:/>|></iframe>)', replace_yt_iframe, body_content)
    ```

12. **Inject carousel fix** (from Step 3.5 findings):
    - For stacked-grid carousels: hide all grid pages except the first via `:not(:first-child) { display: none !important; }`
    - For infinite-scroll carousels: ensure animation keyframes are preserved and `overflow: hidden` is on the parent
    - Never apply `transform: none !important` globally — it breaks carousel positioning

12. **Inject canvas gradient replacement** (from Step 3.5 findings):
    - For each detected canvas, identify the parent's background color
    - Add a CSS `radial-gradient` on the parent to simulate the canvas glow effect
    - Hide the empty canvas: `canvas.absolute { display: none !important; }`

13. **Inject typewriter script** (from Step 3.6 captured prompts):

```javascript
// Typewriter animation
(function() {
  const prompts = [/* captured prompts from Step 3.6 */];
  const span = document.querySelector('[class*="landing-input"] span, [class*="input-box"] span');
  if (!span || !prompts.length) return;
  let pi = 0, ci = 0, del = false;
  function tick() {
    const p = prompts[pi];
    if (!del) { span.textContent = p.slice(0, ci); ci++; if (ci > p.length) { del = true; setTimeout(tick, 2000); return; } setTimeout(tick, 50); }
    else { span.textContent = p.slice(0, ci); ci--; if (ci < 0) { del = false; ci = 0; pi = (pi + 1) % prompts.length; setTimeout(tick, 500); return; } setTimeout(tick, 30); }
  }
  setTimeout(tick, 1000);
})();
```

14. **Add image fallback script**:

```javascript
// Fix scroll — use overflow:visible to avoid double scroll container
document.body.style.setProperty('overflow', 'visible', 'important');
document.documentElement.style.setProperty('overflow', 'visible', 'important');
document.body.style.setProperty('height', 'auto', 'important');
document.documentElement.style.setProperty('height', 'auto', 'important');

// Fix h-screen wrapper (JS fallback for CSS specificity wars)
(function() {
  const wrapper = document.querySelector('[class*="h-screen"][class*="w-screen"]');
  if (wrapper && wrapper.scrollHeight > wrapper.offsetHeight + 100) {
    wrapper.style.setProperty('height', 'auto', 'important');
    wrapper.style.setProperty('min-height', '100vh', 'important');
    wrapper.style.setProperty('overflow', 'visible', 'important');
  }
})();

// Fix lazy loaded images
document.querySelectorAll('img[data-lazy-src],img[data-src]').forEach(img => {
  const r = img.getAttribute('data-lazy-src') || img.getAttribute('data-src');
  if (r && (!img.src || img.src.startsWith('data:'))) img.src = r;
});

// Fix broken srcset (relative URLs that weren't caught in assembly)
const DOMAIN = 'https://ORIGINAL_DOMAIN';  // replace during assembly
document.querySelectorAll('img[srcset], source[srcset]').forEach(el => {
  const srcset = el.getAttribute('srcset');
  if (srcset && srcset.includes('/_next/')) {
    el.setAttribute('srcset', srcset.replace(/(^|,\s*)\//g, '$1' + DOMAIN + '/'));
  }
});

// Force visibility on animation-hidden elements
document.querySelectorAll('[style*="opacity: 0"]').forEach(el => {
  // Don't un-hide elements that are intentionally hidden (opacity-0 class = SPA panels)
  if (!(el.className || '').toString().includes('opacity-0')) {
    el.style.opacity = '1';
  }
});

// Fix cross-origin SVG image widths in marquee/logo strips
// SVG images loaded from a different origin with CSS width:auto compute to 0px.
// Calculate the correct width from HTML width/height attributes + CSS height.
document.querySelectorAll('.animate-infinite-scroll img, [class*="animate-infinite"] img').forEach(img => {
  const attrW = parseInt(img.getAttribute('width'));
  const attrH = parseInt(img.getAttribute('height'));
  const cssH = parseFloat(getComputedStyle(img).height);
  if (attrW && attrH && cssH && img.offsetWidth < 5) {
    const w = Math.round((cssH / attrH) * attrW);
    img.style.setProperty('width', w + 'px');
    img.style.setProperty('min-width', w + 'px');
    img.style.setProperty('flex-shrink', '0');
  }
});

// Remove large SPA overlay panels that survived CSS extraction
document.querySelectorAll('.opacity-0').forEach(el => {
  if (el.offsetWidth > 400 && el.offsetHeight > 400) {
    el.style.display = 'none';
  }
});
```

### Step 4.5 — Behavior Injection

Based on recon findings (Step 1.5a, Step 3.4), inject lightweight JS scripts to bring
the static clone to life. These are zero-dependency, 10-30 line scripts injected before `</body>`.

**Only inject scripts for behaviors actually detected.** Do not inject unused scripts.

#### 4.5a — Scroll Reveal Animations

If `scroll_behaviors.scroll_reveals` is non-empty, inject an IntersectionObserver that
replays fade-in/slide-up animations as the user scrolls:

```javascript
// Scroll reveal — triggers when element enters viewport
(function() {
  const style = document.createElement('style');
  style.textContent = `
    .clone-reveal { opacity: 0; transform: translateY(20px); transition: opacity 0.6s ease, transform 0.6s ease; }
    .clone-reveal.visible { opacity: 1; transform: none; }
  `;
  document.head.appendChild(style);

  // Target elements that had scroll-reveal animations (detected in Step 1.5a)
  const selectors = '[class*="animate-"], [data-aos], [data-scroll], [data-sal], [class*="reveal"], [class*="fade-in"]';
  document.querySelectorAll(selectors).forEach(el => {
    el.classList.add('clone-reveal');
    // Remove the force-visible overrides so animation can play
    el.style.removeProperty('opacity');
    el.style.removeProperty('transform');
  });

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); observer.unobserve(e.target); } });
  }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

  document.querySelectorAll('.clone-reveal').forEach(el => observer.observe(el));
})();
```

**Also update the CSS fix overrides:** remove the blanket `[class*="animate-"] { animation: none; opacity: 1; transform: none; }` and replace with:

```css
/* Let scroll-reveal animations be driven by JS IntersectionObserver instead */
[class*="animate-"] {
  animation: none !important;
  /* opacity and transform are NOW controlled by .clone-reveal JS, not forced to 1/none */
}
```

#### 4.5b — Tab/Accordion Click Toggle

If `click_behaviors` detected tabs or accordions, inject a click handler:

```javascript
// Tab switching
(function() {
  document.querySelectorAll('[role="tablist"]').forEach(tablist => {
    const tabs = tablist.querySelectorAll('[role="tab"]');
    const panels = document.querySelectorAll('[role="tabpanel"]');
    tabs.forEach((tab, i) => {
      tab.addEventListener('click', () => {
        tabs.forEach(t => t.setAttribute('data-state', 'inactive'));
        panels.forEach(p => { p.hidden = true; p.setAttribute('data-state', 'inactive'); });
        tab.setAttribute('data-state', 'active');
        if (panels[i]) { panels[i].hidden = false; panels[i].setAttribute('data-state', 'active'); }
      });
    });
  });

  // Accordion toggle (details/summary already work natively, this handles data-state pattern)
  document.querySelectorAll('[data-state="closed"], [data-state="open"]').forEach(el => {
    const trigger = el.querySelector('button, [role="button"]') || el;
    trigger.addEventListener('click', () => {
      const current = el.getAttribute('data-state');
      el.setAttribute('data-state', current === 'open' ? 'closed' : 'open');
      const content = el.querySelector('[data-state]') ||
                      el.nextElementSibling;
      if (content) {
        content.style.display = current === 'open' ? 'none' : 'block';
        content.style.height = current === 'open' ? '0' : 'auto';
      }
    });
  });
})();
```

#### 4.5c — Sticky Header Scroll Effect

If `scroll_behaviors.sticky` detected a sticky/fixed header, inject a scroll listener
that adds/removes a class for the scrolled state:

```javascript
// Sticky header — add shadow/bg change on scroll
(function() {
  const header = document.querySelector('header, nav');
  if (!header) return;
  const cls = 'clone-header-scrolled';
  const style = document.createElement('style');
  style.textContent = `.${cls} { backdrop-filter: blur(12px) !important; box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important; }`;
  document.head.appendChild(style);

  window.addEventListener('scroll', () => {
    if (window.scrollY > 50) header.classList.add(cls);
    else header.classList.remove(cls);
  }, { passive: true });
})();
```

#### 4.5d — Smooth Scroll

If `media_precheck.scroll_libs` detected a smooth scroll library, or as a general
enhancement, add CSS smooth scrolling:

```css
/* Smooth scroll behavior */
html { scroll-behavior: smooth; }
```

If Lenis was detected, optionally inject a mini smooth-scroll script:

```javascript
// Lightweight smooth scroll (replaces Lenis for basic feel)
// Only inject if Lenis was detected in Step 1.5d
(function() {
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const target = document.querySelector(a.getAttribute('href'));
      if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
    });
  });
})();
```

#### 4.5e — Parallax Effect

If `scroll_behaviors` detected parallax layers (elements with different scroll rates),
inject a lightweight parallax handler:

```javascript
// Simple parallax on background elements
(function() {
  const parallaxEls = document.querySelectorAll('[class*="parallax"], [data-parallax], [class*="bg-fixed"]');
  if (!parallaxEls.length) return;
  window.addEventListener('scroll', () => {
    const scrollY = window.scrollY;
    parallaxEls.forEach(el => {
      const rate = parseFloat(el.dataset.parallaxRate || '0.3');
      el.style.transform = 'translateY(' + (scrollY * rate) + 'px)';
    });
  }, { passive: true });
})();
```

#### 4.5f — Stacked-Grid Paged Carousel (Dot Navigation)

If Step 3.5 detected `stacked-grid` carousels (multiple same-class grid containers stacked
on top of each other with absolute positioning), inject a paged carousel with dot indicators
and auto-rotation. Common pattern: example/showcase cards below hero with 3 cards per page.

```javascript
// Stacked-grid paged carousel with dot navigation + auto-rotate
(function() {
  // Find grids: multiple .grid containers inside the same parent, stacked via absolute position
  // Selector should be adapted based on Step 3.5 detection (section class, grid class)
  const section = document.querySelector('DETECTED_SECTION_SELECTOR');
  if (!section) return;

  const grids = Array.from(section.querySelectorAll('.grid.grid-cols-1'));
  if (grids.length < 2) return;

  // Find dot indicators (small round buttons)
  const dots = Array.from(section.querySelectorAll('button')).filter(b =>
    b.offsetWidth <= 12 && (b.className||'').includes('rounded-full')
  );

  let current = 0;
  const total = grids.length;

  function show(idx) {
    grids.forEach((g, i) => {
      if (i === idx) {
        g.style.opacity = '1';
        g.style.pointerEvents = 'auto';
        g.style.position = 'relative';
        g.style.zIndex = '1';
      } else {
        g.style.opacity = '0';
        g.style.pointerEvents = 'none';
        g.style.position = 'absolute';
        g.style.zIndex = '0';
      }
    });
    dots.forEach((d, i) => {
      d.style.backgroundColor = i === idx ? 'rgba(0,0,0,0.5)' : 'rgba(0,0,0,0.15)';
    });
    current = idx;
  }

  // CSS transition for smooth fade
  const style = document.createElement('style');
  style.textContent = 'SECTION_SELECTOR .grid { transition: opacity 0.5s ease !important; top:0; left:0; right:0; }';
  document.head.appendChild(style);

  show(0);

  // Dot click handlers
  dots.forEach((d, i) => {
    d.addEventListener('click', () => {
      show(i % total);
      clearInterval(autoTimer);
      autoTimer = setInterval(next, 4000);
    });
    d.style.cursor = 'pointer';
  });

  // Auto-rotate every 4 seconds
  function next() { show((current + 1) % total); }
  let autoTimer = setInterval(next, 4000);
})();
```

**Detection criteria:** Step 3.5 `stacked-grid` type with `pages > 1`, AND dot buttons found
in the same section (small round buttons with `rounded-full` class, width ≤ 12px).

#### Injection Decision Table

| Detected in Recon | Script to Inject | Size |
|-------------------|-----------------|------|
| `scroll_reveals.length > 0` | 4.5a Scroll Reveal | ~25 lines |
| `click_behaviors` has tabs/accordion | 4.5b Tab/Accordion Toggle | ~25 lines |
| `sticky.length > 0` | 4.5c Sticky Header | ~12 lines |
| `scroll_libs.length > 0` OR always | 4.5d Smooth Scroll | ~8 lines |
| parallax detected | 4.5e Parallax | ~10 lines |
| stacked-grid + dots detected | 4.5f Paged Carousel | ~40 lines |
| typewriters detected | Step 13 Typewriter (existing) | ~15 lines |
| carousels detected | Step 12 Carousel fix (existing) | existing |

**Only inject what was detected.** A site with no scroll animations gets no scroll-reveal script.

**Write the assembled HTML to the output path.**

---

### Level 1a — Hybrid: Original CSS + Targeted Overrides (~90% fidelity)

**Preferred fix when Level 1 produces a blank/broken page** due to Tailwind `important: true`
or large invisible overlay panels covering content. Preserves responsive layout.

**Root cause:** Tailwind `important: true` makes ALL utility classes use `!important`, so
`.opacity-0 { opacity: 0 !important }` overrides even inline `style="opacity:1 !important"`.
Additionally, SPA sites often have large editor/chat panels (opacity: 0, full-viewport-sized)
that sit on top of the landing page content in the DOM.

**How it works:** Same as Level 1 (keep original CSS), but:
1. Remove large invisible overlay panels from the DOM before extraction
2. Add targeted CSS `!important` overrides for common Tailwind conflicts
3. Add a cleanup script that hides remaining opacity-0 panels at runtime

**Step 1 — Remove overlays (already done in Step 2 Force Visibility)**

The overlay removal in Step 2 handles this. Verify after extraction that
`document.elementFromPoint(720, 400)` returns actual content, not an overlay div.

**Step 2 — Add targeted CSS overrides**

In the CSS fix overrides section (Step 4), add:

```css
/* === TAILWIND IMPORTANT:TRUE FIXES === */
/* Force hero text elements visible despite Tailwind !important cascade */
section h2, section h1, section p, section span, section a {
  opacity: 1 !important;
  visibility: visible !important;
}

/* Hide large SPA overlay panels that have opacity-0 class */
.opacity-0 { display: none !important; }

/* Contain hero background gradient (don't let it overflow) */
section:first-of-type { overflow: hidden !important; }
```

**Step 3 — Add runtime cleanup script**

```javascript
// Remove large editor overlays that survived CSS extraction
document.querySelectorAll('.opacity-0').forEach(el => {
  if (el.offsetWidth > 400 && el.offsetHeight > 400) {
    el.style.display = 'none';
  }
});
```

**Tradeoffs vs Level 1:**
- (+) Preserves responsive layout and CSS breakpoints
- (+) Small file size (~800 KB, same as Level 1)
- (+) Editable via CSS classes
- (-) May not fix ALL Tailwind conflicts (some elements may still be invisible)
- (-) If hero is still blank after 1a, escalate to Level 1b

**When to escalate to 1b:** If after applying 1a overrides, screenshotting the clone still
shows a blank hero (no text visible at y=300-500), escalate to Level 1b.

---

### Level 1b — Playwright Targeted Style Bake (~80% fidelity)

**Last resort for Playwright-available sites.** Use when Level 1a still produces a blank page.
Bakes computed styles into inline attributes, but uses a curated property list (not all properties)
to avoid CSS custom property pollution and keep file size reasonable.

**How it works:** Instead of iterating ALL computed properties (which includes Tailwind v4 custom
properties like `--color-purple-200` that pollute inline styles), use a curated list of ~60
essential visual properties.

```python
    ESSENTIAL_PROPS = [
        'display', 'position', 'top', 'right', 'bottom', 'left',
        'width', 'height', 'min-width', 'min-height', 'max-width', 'max-height',
        'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
        'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
        'flex-direction', 'flex-wrap', 'flex-grow', 'flex-shrink', 'flex-basis',
        'justify-content', 'align-items', 'align-self', 'align-content',
        'gap', 'row-gap', 'column-gap',
        'grid-template-columns', 'grid-template-rows', 'grid-column', 'grid-row',
        'font-family', 'font-size', 'font-weight', 'font-style', 'line-height',
        'letter-spacing', 'text-align', 'text-decoration', 'text-transform',
        'text-overflow', 'white-space', 'word-break',
        'color', 'background-color', 'background-image', 'background-size',
        'background-position', 'background-repeat',
        'background-clip', '-webkit-background-clip', '-webkit-text-fill-color',
        'border-top-left-radius', 'border-top-right-radius',
        'border-bottom-left-radius', 'border-bottom-right-radius',
        'border-top-width', 'border-right-width', 'border-bottom-width', 'border-left-width',
        'border-top-style', 'border-right-style', 'border-bottom-style', 'border-left-style',
        'border-top-color', 'border-right-color', 'border-bottom-color', 'border-left-color',
        'box-shadow', 'text-shadow',
        'opacity', 'visibility', 'z-index', 'overflow', 'overflow-x', 'overflow-y',
        'transform', 'transform-origin',
        'object-fit', 'object-position',
        'aspect-ratio', 'box-sizing', 'isolation', 'vertical-align',
        'backdrop-filter', '-webkit-backdrop-filter',
        'mix-blend-mode', 'filter',
        '-webkit-line-clamp', 'will-change', 'cursor',
        'transition', 'transition-property', 'transition-duration',
    ]

    # After page is fully loaded and scrolled...
    page.evaluate(f"""() => {{
        const props = {json.dumps(ESSENTIAL_PROPS)};
        const skip = new Set(['SCRIPT','STYLE','LINK','META','HEAD','TITLE','NOSCRIPT','BR','HR']);

        document.querySelectorAll('*').forEach(el => {{
            if (skip.has(el.tagName)) return;
            const cs = getComputedStyle(el);
            const styles = [];

            for (const prop of props) {{
                const val = cs.getPropertyValue(prop);
                if (!val || val === '') continue;
                // Skip default/uninteresting values to reduce size
                if (val === 'none' && !['display','text-decoration','transform','box-shadow'].includes(prop)) continue;
                if (val === 'auto' && ['top','right','bottom','left','width','height','z-index'].includes(prop)) continue;
                if (val === 'static' && prop === 'position') continue;
                if (val === 'visible' && ['overflow','overflow-x','overflow-y','visibility'].includes(prop)) continue;
                if (val === '1' && prop === 'opacity') continue;
                if (val === 'rgba(0, 0, 0, 0)' && prop === 'background-color') continue;
                if (val === '0px' && (prop.startsWith('margin') || prop.endsWith('-radius') || prop.endsWith('-width'))) continue;
                styles.push(prop + ':' + val);
            }}

            // Handle gradient text (background-clip: text + transparent fill)
            const bgClip = cs.getPropertyValue('-webkit-background-clip');
            const textFill = cs.getPropertyValue('-webkit-text-fill-color');
            if (bgClip === 'text' && textFill === 'transparent') {{
                const bgImg = cs.getPropertyValue('background-image');
                if (bgImg && bgImg !== 'none') {{
                    styles.push('background-image:' + bgImg);
                    styles.push('-webkit-background-clip:text');
                    styles.push('background-clip:text');
                    styles.push('-webkit-text-fill-color:transparent');
                }}
            }}

            el.setAttribute('style', styles.join(';'));
        }});
    }}""")
```

**Assembly:** Same as Level 1 Step 4, but:
- **Do NOT include any `<style>` blocks or CSS `<link>` tags** (all styles are inline)
- **Only keep `@font-face` rules** and `@keyframes` rules for custom fonts and animations
- Strip `<script>`, fix relative URLs, fix lazy images as usual
- **Post-process:** Replace baked viewport-width values (e.g., `width:1440px`) with `width:100%`

**Tradeoffs vs Level 1/1a:**
- (+) Works when CSS cascade is completely broken
- (+) No CSS custom property pollution (curated property list)
- (-) File size ~1-2 MB (much smaller than naive full bake which produces 20MB+)
- (-) Responsive breakpoints are lost (styles are baked at extraction viewport size)
- (-) Editing requires changing inline styles directly (no class-based editing)

**Filename:** `clone-[domain].html` (same as Level 1)

---

## Phase 3 — Visual QA (3-Round Protocol)

Standardized 3-round verification. Do NOT skip rounds or declare the clone complete
until all 3 rounds pass.

**Round 1 — Desktop section-by-section** (1440px): screenshot each section at its
topology boundary, compare original vs clone side-by-side. Fix discrepancies.

**Round 2 — Mobile full-page** (390px): screenshot original and clone at mobile width,
compare full-page. Fix responsive breakage (columns not stacking, overflow, font scaling).

**Round 3 — Interaction verification**: verify carousel animations, typewriter cycling,
video elements, and SVG visibility in the clone. Fix broken interactions.

### Round 1 — Desktop Section-by-Section (1440px)

```python
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    # Screenshot clone (use "load" — file:// URLs have no network activity for networkidle)
    page_c = browser.new_page(viewport={"width": 1440, "height": 900})
    page_c.goto(f"file://{output_path}", wait_until="load")
    page_c.wait_for_timeout(3000)
    page_c.screenshot(path="/tmp/clone-viewport.png")
    page_c.screenshot(path="/tmp/clone-full.png", full_page=True)

    clone_height = page_c.evaluate("() => document.body.scrollHeight")
    clone_sections = page_c.evaluate("""() =>
        Array.from(document.querySelectorAll('section')).map(s => ({
            cls: s.className.slice(0,50), h: s.offsetHeight
        }))
    """)

    browser.close()
```

### Round 2 — Mobile Full-Page (390px)

If responsive breakpoints were detected in Step 1.5a, also compare at mobile width.

```python
    if recon.get('responsive_info', {}).get('count', 0) > 0:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            # Mobile screenshot of original
            page_m = browser.new_page(viewport={"width": 390, "height": 844})
            try:
                page_m.goto(TARGET_URL, wait_until="networkidle", timeout=30000)
            except:
                page_m.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
            page_m.wait_for_timeout(5000)
            page_m.screenshot(path="/tmp/clone-original-mobile.png", full_page=True)
            page_m.close()

            # Mobile screenshot of clone
            page_mc = browser.new_page(viewport={"width": 390, "height": 844})
            page_mc.goto(f"file://{output_path}", wait_until="load")
            page_mc.wait_for_timeout(3000)
            page_mc.screenshot(path="/tmp/clone-mobile.png", full_page=True)
            page_mc.close()

            browser.close()
```

Compare desktop AND mobile screenshots. If mobile layout is broken (columns not stacking,
hamburger menu not collapsing), add targeted `@media (max-width: 768px)` fixes.

### Round 1 & 2 — Diagnose Issues

Check the following common problems:

| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| Sections have 0px height | `content-visibility: auto` | Add `content-visibility: visible !important` |
| Body not scrollable | `overflow: hidden` on body/html | Override to `overflow: visible !important` (NOT `auto` — see below) |
| Body not scrollable (still) | Double scroll container: both html and body have `overflow-y: auto` | Use `overflow: visible !important` on both — `auto` on both creates two nested scroll contexts where `window.scrollTo` only affects html |
| Page stuck at viewport height | `div.h-screen.w-screen` wrapper (Next.js/SPA) | Strip `h-screen`/`w-screen` classes in HTML assembly + CSS override + JS fallback (see Step 4 item 2) |
| Page stuck at viewport (still) | Tailwind `important:true` → `.ck-style .h-screen { height: 100vh !important }` wins over simple selectors | Use `[class*="ck-style"] .h-screen` selector in CSS + JS `setProperty('height','auto','important')` fallback |
| Logo marquee broken layout | `[class*="animate-"] { display: revert }` converts flex→block | Remove `display: revert` from animate- override |
| Logo marquee not sliding | `[class*="animate-"] { animation: none }` kills infinite-scroll | Exclude with `:not([class*="animate-infinite"]):not([class*="animate-marquee"])` |
| Logo marquee images invisible | Cross-origin SVG `width:auto` computes to 0px | JS fix: calculate width from HTML `width`/`height` attrs + CSS height (see Step 14) |
| Images blank | Lazy loading with `data-lazy-src` | Replace `src` with `data-lazy-src` value |
| Content invisible | `opacity: 0` from animation init state | Force `opacity: 1 !important` |
| Elements pushed off-screen | `transform: translateY(100%)` | Force `transform: none !important` |
| Page very short | Most content in `display:none` | Check if animation JS needed to reveal |

### Round 1 & 2 — Section-Based Comparison

Read both screenshots and compare side-by-side:
- **Viewport screenshot** — first-screen impression (navbar, hero, above-fold)
- **Full-page screenshot** — all sections, overall structure

For detailed comparison, use the topology map from Step 1.5b for section-based comparison:

```python
# Use topology-driven section boundaries instead of fixed intervals
scroll_points = [s['y'] for s in recon.get('topology', []) if s['h'] > 100]
if not scroll_points:
    scroll_points = [0, 1200, 3000, 5000, 8000, 11000, 14000]  # fallback

for y in scroll_points:
    # Screenshot clone at y
    # Screenshot original at y
    # Compare pair — each comparison targets a specific named section
```

This ensures every section gets compared regardless of page length, and failures
are reported with section names (from topology) instead of anonymous scroll offsets.

### Round 1 & 2 — Fix & Re-verify

For each visual difference found:
1. Identify the CSS rule or DOM element causing the difference
2. Add a targeted CSS override or DOM fix
3. Re-screenshot to verify the fix
4. Repeat until the pair matches

**Common fixes:**
- Wrong background color → check body/section inline styles
- Missing rounded corners → sections need `border-radius` from original CSS
- Wrong brand color → check button/CTA actual computed color
- Content misaligned → check container max-width and padding values
- Fonts wrong → verify Google Fonts link is preserved

### Round 3 — Interaction Behavior Verification

If behavior sweep (Step 1.5a) or interactive detection (Step 3.5) found interactive elements,
verify they work correctly in the clone. Use `getBoundingClientRect()` (not `offsetWidth`)
for SVG elements:

```python
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page_v = browser.new_page(viewport={"width": 1440, "height": 900})
        page_v.goto(f"file://{output_path}", wait_until="load")
        page_v.wait_for_timeout(3000)

        verification = {}

        # Verify carousel/marquee animation is running
        if interactive.get('carousels'):
            verification['carousel'] = page_v.evaluate("""async () => {
                const el = document.querySelector('[class*="carousel"] [style*="transform"], [class*="marquee"], [class*="ticker"]');
                if (!el) return 'no-element';
                const t1 = getComputedStyle(el).transform;
                await new Promise(r => setTimeout(r, 2000));
                return getComputedStyle(el).transform !== t1 ? 'animating' : 'static';
            }""")

        # Verify typewriter text changes
        if interactive.get('typewriters'):
            verification['typewriter'] = page_v.evaluate("""async () => {
                const span = document.querySelector('[class*="landing-input"] span, [class*="input-box"] span');
                if (!span) return 'no-element';
                const t1 = span.textContent;
                await new Promise(r => setTimeout(r, 3000));
                return span.textContent !== t1 ? 'typing' : 'static';
            }""")

        # Verify video elements have valid src
        if recon.get('media_precheck', {}).get('videos'):
            verification['videos'] = page_v.evaluate("""() =>
                [...document.querySelectorAll('video')].map(v => ({
                    src: v.src || v.querySelector('source')?.src || 'missing',
                    w: v.offsetWidth
                }))
            """)

        page_v.close()
        browser.close()
```

Include `verification` results in Phase 4 clone report under a **BEHAVIOR CHECK** section.

---

## Phase 2 (continued) — Fallback Levels

If Level 1 (Playwright) is unavailable, use the highest available level below.
After extraction by any level, proceed to Phase 3 for screenshot comparison (if Playwright
is available for verification even though it failed for extraction, or skip Phase 3 if not).

### Level 2 — Firecrawl + CSS Download (~90% fidelity)

**When:** Playwright unavailable, Firecrawl available.

Firecrawl uses a headless browser internally, so it renders JS. But it returns HTML as a string
rather than giving access to computed styles. We compensate by downloading external CSS files.

**Step 1 — Multi-format scrape**

```bash
# Get rendered HTML (JS-executed DOM) — preserves DOM structure
firecrawl scrape "TARGET_URL" -f html --wait-for 5000 -o /tmp/site-html.html

# Get raw HTML with all styles — includes <style> blocks and <link> tags
firecrawl scrape "TARGET_URL" -f rawHtml --wait-for 5000 -o /tmp/site-raw.html

# Get markdown — clean text content for copy verification
firecrawl scrape "TARGET_URL" -f markdown --wait-for 5000 -o /tmp/site-md.md
```

**Step 2 — Download external CSS files**

Extract all `<link rel="stylesheet">` URLs from rawHtml, download each with `curl`:

```bash
curl -sL "[css-url]" -o /tmp/site-main.css
```

The main framework CSS (usually 100KB+) contains layout rules, responsive breakpoints, and component styles.
This is where critical values like `border-radius`, `margin`, `background-color`, `font-family` live.

**Step 3 — Extract design tokens from CSS**

Parse downloaded CSS to find rules for key selectors:
- Section-level: `section_*`, `nav_*`, `hero*`, `footer*`, `cta*`
- Spacing: `container*`, `padding-global`, `padding-section*`
- Typography: `heading-style*`, `text-size*`, `playfair*`, `font-*`
- Buttons: `btn*`, `button*`, `nav-btn` — **especially brand colors!**
- Components: `accordion*`, `pricing*`, `comparison*`, `faq*`, `gallery*`

**Step 4 — Assemble self-contained HTML**

Same assembly process as Level 1 Step 4: combine Firecrawl's HTML body + downloaded CSS into a single file.
Add the same `content-visibility`, `overflow`, and lazy-image fix overrides.

**Step 5 — Screenshot comparison (if Playwright available for verification)**

If Playwright is available for screenshots but failed for the initial extraction (e.g., site blocked
headless Chrome but Firecrawl's browser succeeded), use Playwright to screenshot the clone and compare.

---

### Level 3 — gstack/browse Screenshot + DOM (~85% fidelity)

**When:** Playwright and Firecrawl unavailable, gstack or browse daemon available.

**Step 1 — Screenshot the original**

```bash
gstack screenshot "TARGET_URL" --full-page --output /tmp/original.png 2>/dev/null \
  || browse screenshot "TARGET_URL" --output /tmp/original.png 2>/dev/null
```

**Step 2 — Extract rendered DOM**

```bash
gstack eval "TARGET_URL" "document.documentElement.outerHTML" > /tmp/site-dom.html 2>/dev/null \
  || browse eval "TARGET_URL" "document.documentElement.outerHTML" > /tmp/site-dom.html 2>/dev/null
```

**Step 3 — Download external CSS**

Same as Level 2 Step 2 — extract stylesheet URLs from DOM, download with curl.

**Step 4 — Assemble HTML**

Same as Level 1 Step 4 assembly, using the extracted DOM + downloaded CSS.

**Step 5 — Visual comparison using screenshot**

Read the original screenshot visually (via the Read tool) and compare with the clone.
Use gstack/browse to screenshot the clone for side-by-side comparison.

**Fidelity gap vs Level 1-2:** gstack/browse may not wait for all JS to finish, so some
dynamic content might be missing. CSS extraction is the same quality.

---

### Level 4 — WebFetch + Manual Reconstruction (~75% fidelity)

**When:** No headless browser tools available. Only WebFetch (HTTP fetch).

This level **cannot render JS**. It works for static HTML sites but produces degraded results for SPAs.

**Step 1 — Fetch the page**

```
WebFetch(TARGET_URL, "Return the complete HTML structure of this page.
List every section, every CSS class, every inline style, every color value,
every font reference, every image URL. Be exhaustive.")
```

**Step 2 — Detect SPA**

Check the WebFetch result for SPA signals:
- `<div id="root">` or `<div id="app">` with empty/minimal content
- `<noscript>` with substantial fallback
- Fewer than 200 words of visible text
- Only script bundles as `<script src>`

If SPA detected → **escalate to Level 5** (WebFetch cannot render JS).

**Step 3 — Extract design details via WebFetch**

Make a second WebFetch call focused on design extraction:

```
WebFetch(TARGET_URL, "Extract all design details:
1. Every hex/rgb color value  2. Font families and sizes
3. Spacing values  4. Border-radius values  5. Box-shadow values
6. Exact text content of every heading, paragraph, button
7. Layout structure (grid columns, flex directions)
8. Background gradients  9. Image URLs")
```

**Step 4 — Download external CSS**

Attempt to fetch CSS files directly:

```
WebFetch("[css-url]", "Return the raw CSS content of this stylesheet")
```

**Step 5 — Manual code generation**

Using the extracted information, manually write the HTML/CSS clone:
1. Build semantic HTML structure matching the detected sections
2. Apply extracted CSS values (colors, fonts, spacing, etc.)
3. Use real image URLs where available
4. Mark estimated values with `/* estimated */` comments

**Fidelity gap:** Layout proportions, exact spacing, responsive breakpoints, and interactive
components will be approximated. Typography may be wrong if fonts are loaded via JS.

---

### Level 5 — WebSearch Research Only (~50% fidelity)

**When:** WebFetch also fails (site blocks scraping, is behind auth, or returns empty content).

**Step 1 — Search for visual references**

Run in parallel:
```
WebSearch("[domain] website screenshot")
WebSearch("[domain] design system")
WebSearch("[domain] color palette hex")
WebSearch("[domain] typography font")
WebSearch("site:figma.com [domain]")
WebSearch("site:dribbble.com [domain]")
```

**Step 2 — Gather design intelligence**

From search results, collect:
- Screenshots or preview images (e.g., from ProductHunt, Awwwards, Dribbble)
- Brand guidelines or design system documentation
- Color palette (from brand resources or CSS analysis tools)
- Typography choices

**Step 3 — Manual reconstruction from research**

Build the clone based on collected intelligence. **Mark ALL values as estimated:**

```css
:root {
  --color-bg: #ffffff; /* estimated */
  --color-accent: #4f46e5; /* estimated from screenshots */
}
```

**Fidelity gap:** Everything is approximated. Layout, spacing, interactions, and responsive behavior
are best-effort guesses. This is a last resort.

**Always warn the user:**
```
⚠️ Level 5 fallback — clone is based on web research, not direct extraction.
All values are estimated. Fidelity will be significantly lower (~50%).
For better results, ensure Playwright or Firecrawl is installed.
```

---

## Phase 4 — Output & Report

### Write the file

Write to `$(pwd)/test_outputs/clone-[domain].html`.

### Clone Report

Output this report to the user:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CLONE REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Source              [TARGET_URL]
Method              [Playwright DOM extraction / Firecrawl + manual]
Sections cloned     [N/N]
Page height         [Xpx] (original: [Ypx])
Output file         [full path]
Output size         [X KB]

SECTION VERIFICATION
  [section_name]: [height]px ✓
  [section_name]: [height]px ✓
  ...

RECON SUMMARY
  Sections: [N] | Scroll animations: [N] | Hover elements: [N]
  Tabs/Accordions: [N] | Responsive breakpoints: [list]
  Videos: [N] | Lottie: [N] | Scroll lib: [name/none]
  Layered stacks: [N] | SVGs: [N] total ([N] icons)

BEHAVIOR CHECK
  Carousel: [animating/static/no-element]
  Typewriter: [typing/static/no-element]
  Videos: [N valid / N total]

KNOWN DEVIATIONS
  - [each deviation and why]
  - [e.g. "iframe content blank — cross-origin, works when deployed to web server"]
  - [e.g. "FAQ accordion fully expanded — original uses JS to toggle"]

TO REFINE
  Describe what doesn't match and I'll fix that specific section.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Cleanup Intermediate Files

After the report, remove all intermediate screenshots generated during QA rounds.
Only the final `.html` clone file should remain in `test_outputs/`.

```bash
# Remove all intermediate PNG screenshots from test_outputs
rm -f "$(pwd)/test_outputs/"*.png
```

This prevents accumulation of debug artifacts (viewport screenshots, section comparisons,
original vs clone diffs) that are only useful during the QA process.

---

## Optional — Asset Download (user-requested)

**Trigger:** User says "download assets", "save locally", "offline", or "self-contained with images".

Download all referenced assets to a local directory and rewrite URLs in the clone.

```python
import os, re, urllib.parse

asset_dir = os.path.join(os.path.dirname(output_path), 'assets-' + domain)
os.makedirs(asset_dir, exist_ok=True)

# Extract all asset URLs from clone HTML
urls = set()
for match in re.findall(r'(?:src|href|poster|url\()[\s="\']*([^"\')\s>]+)', clone_html):
    if match.startswith('http') and any(ext in match.lower() for ext in
        ['.png','.jpg','.jpeg','.webp','.svg','.gif','.mp4','.webm','.woff','.woff2','.ttf','.otf','.ico']):
        urls.add(match)
```

```bash
# Download each asset (parallel with xargs for speed)
echo "$URLS" | xargs -P 4 -I {} sh -c 'curl -sL "{}" -o "ASSET_DIR/$(basename "{}" | cut -d"?" -f1)"'

# Also grab favicons
curl -sL "https://DOMAIN/favicon.ico" -o "ASSET_DIR/favicon.ico" 2>/dev/null
curl -sL "https://DOMAIN/apple-touch-icon.png" -o "ASSET_DIR/apple-touch-icon.png" 2>/dev/null
```

After download, rewrite URLs in the clone HTML to relative paths: `./assets-[domain]/[filename]`.

---

## Optional — Design Token Export (user-requested)

**Trigger:** User says "design tokens", "extract tokens", or "design system".

Structure the `:root` custom properties (from Step 3c) into a categorized JSON file.

```python
import json

tokens = {"colors": {}, "spacing": {}, "typography": {}, "radii": {}, "shadows": {}, "other": {}}
for prop, val in root_vars.items():
    if any(k in prop for k in ['color', 'bg', 'foreground', 'background', 'border-color', 'accent', 'primary', 'secondary', 'destructive', 'muted', 'chart']):
        tokens['colors'][prop] = val
    elif any(k in prop for k in ['radius', 'rounded']):
        tokens['radii'][prop] = val
    elif any(k in prop for k in ['shadow']):
        tokens['shadows'][prop] = val
    elif any(k in prop for k in ['font', 'text', 'line-height', 'letter-spacing']):
        tokens['typography'][prop] = val
    elif any(k in prop for k in ['spacing', 'gap', 'padding', 'margin']):
        tokens['spacing'][prop] = val
    else:
        tokens['other'][prop] = val

token_path = output_path.replace('.html', '-tokens.json')
# Write to test_outputs/design-tokens-[domain].json
```

---

## Refinement Flow

If the user says a section doesn't match, or wants adjustments:

1. Re-screenshot the specific section from both original and clone
2. Compare side-by-side to identify the exact difference
3. Fix ONLY the identified issue — do not touch other sections
4. Re-screenshot to verify the fix
5. Report what changed

**Never "improve" during refinement.** The user is asking for closer fidelity, not redesign.

---

## Phase 5 — Next.js Project Output (Optional)

**Trigger:** User explicitly requests "Next.js project", "deployable project", "React version",
"make it a Next.js app", or "convert to React".

This phase converts the extracted single-file HTML clone into a deployable Next.js project.
The key advantage: the high-fidelity HTML (from Phase 2) serves as ground truth for the conversion.

### Step 1 — Scaffold Next.js Project

```bash
npx create-next-app@latest test_outputs/nextjs-[domain] \
  --typescript --tailwind --eslint --app --no-src-dir \
  --import-alias "@/*" <<< "y"
```

### Step 2 — Parse Clone HTML into Components

Using the topology map from Step 1.5b, split the assembled HTML into logical React components:

| Topology Section | Component File |
|-----------------|----------------|
| `nav` / `header` | `components/Navbar.tsx` |
| First `section` (hero) | `components/Hero.tsx` |
| Each subsequent `section` | `components/Section[N].tsx` (or descriptive name from topology) |
| `footer` | `components/Footer.tsx` |

- `app/page.tsx` — imports and composes all components in topology order
- `app/globals.css` — extracted CSS (the `<style>` block contents from the clone)

### Step 3 — Convert HTML to JSX

For each component:
1. `class=` → `className=`
2. Self-closing tags: `<img>` → `<img />`, `<br>` → `<br />`, `<hr>` → `<hr />`
3. `style="prop:val; prop2:val2"` → `style={{prop: 'val', prop2: 'val2'}}`
4. `for=` → `htmlFor=`
5. `tabindex=` → `tabIndex=`
6. Boolean attributes: `autoplay` → `autoPlay`, `readonly` → `readOnly`
7. Move inline `<script>` content to `useEffect` hooks
8. Convert `<img src="...">` to Next.js `<Image>` where appropriate (optional)

### Step 4 — Asset Handling

- If asset download (Optional section above) was run: copy `assets-[domain]/` to `public/assets/`
- Otherwise: keep absolute URLs pointing to original site
- Move Google Fonts `<link>` tags to `next/font/google` imports in `app/layout.tsx`
- Extract inline SVG icons (from Step 1.5e) to `components/icons.tsx` as React components

### Step 5 — Design Tokens (if exported)

If design token export was run, convert `design-tokens-[domain].json` into:
- Tailwind `@theme` block in `globals.css` for colors, spacing, radii
- CSS custom properties in `:root` for remaining tokens

### Step 6 — Verify Build

```bash
cd test_outputs/nextjs-[domain] && npm run build
```

If build fails, diagnose and fix TypeScript/JSX errors. Max 3 retry attempts.
Common issues: unclosed tags, reserved word attributes, missing imports.

### Step 7 — Report

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NEXT.JS PROJECT CREATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Path            test_outputs/nextjs-[domain]/
Components      [N] components extracted
Assets          [N] images, [N] SVG icons
Design tokens   [exported/skipped]

TO RUN
  cd test_outputs/nextjs-[domain] && npm run dev

TO DEPLOY
  vercel deploy  (or)  netlify deploy
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Key Lessons & Pitfalls

These are critical learnings from real cloning sessions. Read them before starting.

### `networkidle` timeout — SPA/Next.js sites

Many SPA and Next.js sites have persistent WebSocket connections, analytics pings, or
long-polling requests that prevent `networkidle` from ever firing. Playwright will hang
for 60s+ and then throw a TimeoutError.

**Always use a fallback chain:**
```python
try:
    page.goto(URL, wait_until="networkidle", timeout=30000)
except:
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(8000)  # manual wait for JS rendering
```

Also: when screenshotting the local `file://` clone, use `wait_until="load"` (not `networkidle`).

### Large invisible overlay panels — SPA editor/chat UIs

SPA sites (lovable.dev, v0.dev, etc.) often have large full-viewport invisible panels
sitting on top of the landing page in the DOM. These are editor panels, chat UIs, or
onboarding flows that start with `opacity: 0` and get revealed by JS interaction.

**Problem:** These panels have `opacity: 0` via Tailwind's `.opacity-0` class. When Tailwind
uses `important: true`, even `el.style.setProperty('opacity', '1', 'important')` fails to
override. The panel covers the hero content, making `document.elementFromPoint()` return
the overlay instead of the landing page text.

**Detection:** Check for large (>500x500px) elements with `opacity-0` in their className.

**Fix:** Remove them from the DOM before extraction:
```javascript
if (cls.includes('opacity-0') && el.offsetWidth > 500 && el.offsetHeight > 500) {
    el.remove();
    return;
}
```

Also add CSS fallback in the clone: `.opacity-0 { display: none !important; }`

### `content-visibility: auto` — The Silent Killer

Many modern sites use `content-visibility: auto` for performance. When loading from `file://`,
the browser never scrolls these elements into view, so they stay at 0px height forever.

**Always inject:** `*, section, div { content-visibility: visible !important; }`

### `overflow: hidden` on body

Sites often set `overflow: hidden` on body for modal management. This persists in the extracted DOM
and prevents scrolling.

**Always override:** `body, html { overflow-y: auto !important; overflow-x: hidden !important; }`

Note: use `overflow-x: hidden` (not `auto`) to prevent horizontal scrollbar from baked widths.

### `section { overflow: visible }` breaks hero backgrounds

**Do NOT globally override** `section { overflow: visible !important }`. Many hero sections
use `overflow: hidden` to clip gradient background images (like lovable.dev's pulse.webp).
Setting `overflow: visible` makes the gradient bleed out of the section.

**Instead:** Only override `height` and `min-height` on sections. Use `section:first-of-type { overflow: hidden !important; }`
to preserve hero clipping. Rely on `content-visibility: visible` (not overflow) to fix
collapsed sections.

### Lazy-loaded images

Images with `src="data:image/svg+xml,..."` and `data-lazy-src="[real-url]"` won't load from
a static file. The lazy-loading JS is stripped during extraction.

**Always run the image fallback script** that copies `data-lazy-src` to `src`.

### Cross-origin iframes

Iframes pointing to external domains (demo embeds, YouTube) won't load from `file://`.
**This is expected.** They work when the clone is deployed to a web server.

### Webflow animation states

Webflow uses `data-w-id` attributes and JS to trigger entrance animations. The initial CSS state
is `opacity: 0; transform: translateY(...)`. Without the Webflow runtime JS, elements stay invisible.

**Always force:** `[data-w-id] { opacity: 1 !important; transform: none !important; }`

### `h-screen` / `w-screen` body constraint (Next.js / Tailwind)

Many Next.js + Tailwind sites set `h-screen w-screen` on `<body>`, making it exactly viewport-sized.
The page content overflows inside body, and scrolling happens on `document.body`, NOT on
`document.scrollingElement` (which is `<html>`). This means:

1. `window.scrollTo()` does NOT work — it controls `<html>`, which is 100vh
2. Must use `document.body.scrollTo()` for screenshots at scroll positions
3. In the clone fix CSS, override: `body.h-screen { height: auto !important; min-height: 100vh !important; }`

**For Playwright scrolling:** always call BOTH `window.scrollTo()` and `document.body.scrollTo()`:
```javascript
window.scrollTo(0, y);
document.body.scrollTo(0, y);
```

### Next.js `/_next/image` URLs

Next.js optimized images use `/_next/image?url=...&w=...&q=...` paths. When extracted to a local file,
these become `file:///_next/image?url=...` which cannot resolve.

**Fix:** Parse the `url` query parameter and prepend the original domain:
`/_next/image?url=%2Fimages%2Ffoo.png&w=1920&q=75` → `https://domain.com/images/foo.png`

Also fix `/_next/static/media/...` paths: prepend the original domain directly.

### Carousels & Sliders — THREE distinct patterns

Our global `transform: none !important` fixes break carousels.
Always detect carousels in Step 3.5 and apply targeted fixes.

**Pattern A — Infinite-scroll marquee** (logo tickers, testimonial streams):
- Uses `@keyframes` with `translateX(-50%)` or `translateX(-33%)`, `animation: Xs linear infinite`
- Fix: preserve the animation, keep `overflow: hidden` on parent, do NOT apply `transform: none`
- CSS: `[class*="overflow-hidden"] { overflow: hidden !important; }`

**Pattern B — Stacked-grid carousel** (paginated cards, same position):
- Multiple identical grids stacked at the same position, JS toggles visibility per page
- All pages render at once → text overlaps
- Fix: `parentSelector > .grid:not(:first-child) { display: none !important; }`

**Pattern C — Transform-based slider** (embla, swiper):
- Uses `transform: translateX()` to position slides, parent clips with `overflow: hidden`
- Our `transform: none !important` collapses all slides to origin
- Fix: NEVER apply global `transform: none`. Only target `[data-w-id]` (Webflow animations).

### Typewriter / Rotating text

Many hero sections have a typing prompt that cycles through example inputs via JS.
The static clone freezes on whatever text was visible at extraction time.

**Fix:** In Step 3.6, watch the text element for ~20 seconds to capture all prompts.
Then inject a typewriter script that cycles through them with type/delete animation.
Include `textarea[placeholder]` in the selector — not just `input` and `span`.

### Canvas-rendered backgrounds

Some sites render gradient/particle backgrounds on `<canvas>` via JS. In a static clone, canvas
elements are blank. The visual effect disappears, exposing underlying layers (grid lines, solid colors).

**Fix:** Identify the canvas parent's background color, then add a CSS `radial-gradient` simulation
to approximate the effect. Hide empty canvas elements: `canvas.absolute { display: none !important; }`

### Gradient text (`background-clip: text`) — invisible in clone

Many modern sites use CSS gradient text: `background-image: linear-gradient(...);
-webkit-background-clip: text; -webkit-text-fill-color: transparent;`. The gradient
renders as the text color. But in the clone, the gradient often breaks because it
references CSS custom properties (`var(--brand-gradient)`) that don't resolve.

**Result:** Text appears as `color: transparent` with no visible gradient = invisible text.

**Fix (in Step 3):** Before extracting DOM, iterate all elements and check for
`-webkit-background-clip: text`. If found, read the COMPUTED `background-image` value
(which has the gradient fully resolved) and bake it as an inline style. This ensures
the gradient survives even when CSS custom properties are lost.

### Relative URLs in Next.js / SPA sites

When extracting DOM from a rendered page, all relative URLs become `file:///...` in the static clone.

**Fix during assembly (Step 4):**
- `/_next/image?url=%2F...` → parse the `url` param, prepend `https://domain.com`
- `/_next/static/media/...` → prepend `https://domain.com`
- `/images/...` → prepend `https://domain.com`
- `/cdn-cgi/...` → prepend `https://domain.com`
- CSS `url(/_next/...)` → prepend `https://domain.com`
- `srcset` values — each URL in the comma-separated list needs domain prepended
- `<source srcset="...">` inside `<picture>` elements — same treatment

### `overflow: visible` vs `overflow: hidden` — The Conflict

The root cause of most carousel/slider issues:
- We need `content-visibility: visible` to fix collapsed sections
- Carousels need `overflow: hidden` to clip off-screen slides
- Hero sections need `overflow: hidden` to contain gradient backgrounds

**Resolution:** Use `[class*="overflow-hidden"]` selector to restore `overflow: hidden` on elements
that originally had it. This catches Tailwind's `overflow-hidden` utility class and similar patterns.
Do NOT use a blanket `section { overflow: visible !important }` — instead use `content-visibility: visible`
(which fixes collapsed sections without affecting overflow) and let elements keep their `overflow: hidden`.

### React/Next.js + Tailwind `important: true` — The Escalation Chain

Some Tailwind configs enable `important: true`, which adds `!important` to ALL utility classes.
This means extracted CSS overrides inline styles — even `style="opacity:1"` loses to
`.opacity-0 { opacity: 0 !important }`.

**Symptoms:** DOM has correct elements, getComputedStyle shows correct values during extraction,
but screenshot shows blank hero. Content is there but invisible.

**Solution — Escalation chain (Level 1 → 1a → 1b):**

1. **Level 1a (preferred):** Keep original CSS, but remove invisible overlay panels from DOM
   and add targeted `!important` CSS overrides. Preserves responsive layout. ~90% fidelity.

2. **Level 1b (fallback):** Bake essential computed styles into inline attributes using a curated
   property list (~60 properties). Do NOT iterate all `cs[i]` properties — Tailwind v4 sites
   expose hundreds of CSS custom properties (`--color-purple-200`, etc.) that pollute inline styles,
   cause color conflicts, and bloat file size to 20MB+. Use the curated list from Level 1b section.

**Do NOT use the naive full-bake approach** (iterating `cs.length`). It produces 20MB+ files
with CSS custom property pollution that breaks colors and layout.

### `section { height: auto }` kills hero `min-h-screen`

Many Tailwind sites use `min-h-screen` (= `min-height: 100vh`) on the hero section so the
gradient background fills the viewport. If you override `section { min-height: auto !important }`,
the hero collapses to content height and the gradient no longer fills the screen.

**Fix:** In the CSS overrides, only remove `max-height` caps on sections. Do NOT override
`height` or `min-height`:
```css
section { max-height: none !important; }
/* Do NOT add: height: auto, min-height: auto */
```

### Cookie consent banners persist in clone

Cookie consent / GDPR banners are extracted as part of the DOM and appear as fixed-position
overlays in the clone. They clutter the page and cover content.

**Fix:** Remove them in Step 2 (Force Visibility) by targeting common selectors:
`[class*="cookie"], [id*="consent"], [class*="gdpr"], [aria-label*="cookie"]`

### Hover/focus states captured during extraction

If the mouse cursor was over an element or an element had focus during extraction, the
computed styles will include hover/focus state values (different background, shadows, etc).

**Fix:** Before extraction (end of Step 1), move the mouse to corner (0,0), blur the active
element, and wait briefly:
```python
page.mouse.move(0, 0)
page.evaluate("() => document.activeElement?.blur()")
page.wait_for_timeout(500)
```

### CSS `@layer` ordering (Tailwind v4)

Tailwind v4 uses `@layer base, components, utilities;` to control CSS specificity ordering.
When extracting CSS via `cssRules`, the `@layer` declaration must be preserved and placed
BEFORE any layered rules. If it appears after rules, the layer ordering is undefined and
utilities may lose to base styles.

**Fix:** When building the `<style>` block, place `@layer` declarations and `@property`
definitions at the top, before all other rules.

### `<html>` attributes — `data-theme`, `class`, `lang`

Many sites set `data-theme="light"`, `class="dark"`, or similar attributes on `<html>`.
CSS selectors like `[data-theme="light"] .bg-background` depend on these attributes existing.
If the clone's `<html>` tag doesn't have them, those selectors fail and colors are wrong.

**Fix:** In Step 4 assembly, preserve all attributes from the original `<html>` tag
(especially `lang`, `class`, `dir`, `data-*`, `style`).

### CSS custom properties (`var()`) silently fail — THE #1 fidelity killer

Modern sites define 100-300+ custom properties on `:root` (Tailwind v4, shadcn/ui, Radix).
Every color, spacing, radius, and font-size is a `var(--xxx)` reference. If even ONE `:root`
definition is lost or mis-ordered, dozens of values silently fall back to browser defaults
(usually `0`, `transparent`, or `initial`).

**Symptoms:** Colors slightly wrong, spacing off, borders missing, shadows gone — hard to
diagnose because nothing errors, values just silently degrade.

**Root cause:** In the clone, the extracted CSS has `:root` definitions inside `@layer base { }`.
If the `@layer` declaration order is slightly different, `base` layer has lower priority than
expected, and the `:root` vars get overridden by later layers with `initial` values.

**Fix:** In Step 3c, extract ALL `:root` custom property values from cssRules (recursing into
`@layer` and `@media` blocks). Then in Step 4 assembly, inject a standalone `:root { }` block
with all ~288 resolved values **outside any `@layer`**, ensuring they always win:
```css
/* Injected :root fallback — ensures all var() references resolve */
:root {
  --background: 45 40% 98%;
  --foreground: 0 0% 11%;
  --radius: .5rem;
  /* ... all extracted vars ... */
}
```

### `loading="lazy"` images blank in `file://` context

Native lazy loading (`loading="lazy"`) relies on the browser's scroll-based loading. When
opening a `file://` clone, below-fold images may never trigger loading because the browser
doesn't process scroll events the same way.

**Fix:** Strip `loading="lazy"` from all `<img>` tags in Step 3g. Images load eagerly instead.

### Inner scroll containers — SPA `fixed inset-0` layout pattern

Many SPA sites (wondering.app, etc.) use a layout where `<body>` has no scrollable content.
Instead, a `position: fixed; inset: 0` wrapper contains an `overflow-y: auto` child that acts
as the actual scroll container. All scrolling and IntersectionObserver triggers happen inside
this inner container, NOT on window or body.

**Symptoms:** `window.scrollTo()` and `document.body.scrollTo()` have no effect. Lazy loading
and scroll-reveal animations never trigger. The page appears as a single viewport-height frame.

**Detection:** In Step 1, after initial scroll, detect inner scroll containers:
```javascript
const scrollContainers = [...document.querySelectorAll(
    '[class*="overflow-y-auto"], [class*="overflow-auto"], [class*="scrollbar"]'
)].filter(el => el.scrollHeight > el.clientHeight + 100);
```

**Fix:** Scroll each inner container in addition to window/body. Also, when taking Phase 3
comparison screenshots, scroll the inner container instead of using `window.scrollTo()`.

### Behavior injection conflicts with force-visible CSS overrides

Step 4 forces `[class*="animate-"] { opacity: 1; transform: none; }` to make scroll-reveal
elements visible in the static clone. But Step 4.5a injects an IntersectionObserver that
needs elements to START at `opacity: 0` so the animation can play.

**Resolution:** When 4.5a is active, the CSS override for `[class*="animate-"]` must NOT
force `opacity: 1` and `transform: none`. Instead, let the `.clone-reveal` class handle
initial state (`opacity: 0; transform: translateY(20px)`) and the `.visible` class handle
the reveal (`opacity: 1; transform: none`). The IntersectionObserver adds `.visible` when
the element scrolls into view.

If 4.5a is NOT injected (no scroll reveals detected), keep the original force-visible override.

### SVG elements have no `offsetWidth` / `offsetHeight`

SVG elements do not support `offsetWidth`/`offsetHeight` — these return `undefined` or `0`.
Use `getBoundingClientRect()` instead when checking SVG visibility or dimensions.

**Wrong:** `svg.offsetWidth > 0` — always fails for SVG
**Correct:** `svg.getBoundingClientRect().width > 0`

This applies everywhere: Step 1.5e SVG detection, Phase 3 Step 5 verification, and any
diagnostic script that checks element visibility.

### Smooth scroll library interference (Lenis, Locomotive)

Sites using smooth scroll libraries (Lenis, Locomotive Scroll, GSAP ScrollSmoother) wrap
the page in a transform-based scroll container. The extracted DOM may have
`transform: translate3d(0, -Xpx, 0)` frozen at the extraction-time scroll position,
pushing all content off-screen in the clone.

**Detection:** In Step 1.5d, check for `.lenis`, `.locomotive-scroll`, `[data-scroll-container]`,
or custom scroll wrappers with `overflow: hidden` on body.

**Fix:** If detected, reset the scroll container's transform before extraction (handled in Step 1.5d):
```javascript
document.querySelectorAll('.lenis, .locomotive-scroll, [data-scroll-container]').forEach(el => {
    el.style.setProperty('transform', 'none', 'important');
});
```

Also add `scroll-behavior: smooth` to the clone's `<html>` to approximate the feel.

### CSS `animate-*` classes — scroll-reveal stuck at initial state

Sites use CSS animation classes like `animate-cascade-drop-in`, `animate-fade-in` with initial
state `opacity: 0; transform: translateY(20px)`. These are triggered by IntersectionObserver
or scroll position. In a static clone, these animations either:
- Never start (if the trigger is JS-based)
- Start but stay at the `from` keyframe (if `animation-fill-mode: backwards` + long delay)

**Result:** Entire sections of cards/content are invisible despite being in the DOM.

**Fix:** In Step 4 CSS overrides, force all animated elements to their end state:
```css
[class*="animate-"] {
  animation: none !important;
  opacity: 1 !important;
  transform: none !important;
  display: revert !important;
  visibility: visible !important;
}
```

This also catches `cascade-delay-*` classes (staggered animation delays).

### Scroll-animation `transform` shifts — the 20px ghost offset

Many sites use scroll-reveal animations: initial state `opacity: 0; transform: translateY(20px)`.
Our force-visibility fixes opacity to 1, but the `translateY(20px)` remains, causing every
animated section to be shifted 20px down. Across 10+ sections this accumulates to ~200px.

**Fix:** In Step 3f, for elements with `opacity < 0.1`, also check their `transform`. If it's
a pure translation (not rotation/scale, which carousels use), reset to `none`. Parse the
`matrix()` values to distinguish: `matrix(1,0,0,1,X,Y)` = pure translation → safe to reset.

### `@import` rules silently dropped if not first in `<style>`

CSS spec requires `@import` rules to appear before any other rules in a stylesheet. If our
assembled `<style>` block has `@font-face` or `:root` before the `@import`, the import is
silently ignored. This loses entire external stylesheets (Google Fonts, icon fonts).

**Fix:** In Step 4 assembly, extract all `@import` rules from the CSS, place them FIRST in
the `<style>` block, before everything else.

### `<link>` tags for fonts lost during body-only extraction

When we extract `document.documentElement.outerHTML` and then take only the `<body>`, we lose
`<head>` elements like `<link rel="stylesheet" href="fonts.googleapis.com/...">` and
`<link rel="preload" as="font">`. Without these, the page renders with fallback system fonts.

**Fix:** In Step 3d, separately extract font-related `<link>` tags from `<head>` and include
them in the output `<head>`.

### Don't rewrite from scratch

The single biggest fidelity improvement came from switching from "understand and rewrite" to
"extract and clean". The original DOM + original CSS is always more accurate than any manual
reconstruction, no matter how carefully analyzed.

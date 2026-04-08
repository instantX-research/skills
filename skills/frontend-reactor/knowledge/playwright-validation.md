# Playwright Visual & Interaction Validation

## Overview

After building the converted React project, use Playwright to compare it against the original website. This phase catches regressions in:

- **Visual fidelity** — layout shifts, missing elements, color/font differences
- **Interactions** — clickable elements that don't respond, broken hover states
- **Animations & transitions** — missing CSS animations, broken transitions, lost motion
- **Responsive layout** — breakpoints that render differently from the original

The validation produces a structured diff report with screenshots and a pass/fail summary.

## Prerequisites

```bash
pip install playwright Pillow
playwright install chromium
```

## Architecture

```
Original Site (live URL)    Converted Project (localhost:3000)
        │                              │
        ▼                              ▼
   Playwright                     Playwright
   Browser A                     Browser B
        │                              │
        ├── Screenshots ◄──────────────┤  → pixel diff
        ├── Interactive elements ◄─────┤  → element count diff
        ├── Hover states ◄─────────────┤  → visual hover diff
        ├── Animations ◄───────────────┤  → @keyframes / transition diff
        └── Scroll behavior ◄──────────┤  → sticky / smooth scroll diff
                    │
                    ▼
            Validation Report
```

## Phase 1 — Start Dev Server & Prepare

Before running validation, start the converted project's dev server:

```python
import subprocess, time, socket

def start_dev_server(project_dir, port=3000):
    """Start Next.js dev server and wait until it's ready."""
    proc = subprocess.Popen(
        ["npm", "run", "dev", "--", "-p", str(port)],
        cwd=project_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # Wait for the server to be ready (max 30s)
    for _ in range(60):
        try:
            sock = socket.create_connection(("localhost", port), timeout=0.5)
            sock.close()
            return proc
        except (ConnectionRefusedError, OSError):
            time.sleep(0.5)
    raise TimeoutError(f"Dev server did not start within 30s on port {port}")
```

## Phase 2 — Visual Screenshot Comparison

### Step 1 — Capture full-page screenshots at multiple viewports

```python
from playwright.sync_api import sync_playwright
import os

VIEWPORTS = [
    {"name": "desktop", "width": 1440, "height": 900},
    {"name": "tablet",  "width": 768,  "height": 1024},
    {"name": "mobile",  "width": 375,  "height": 812},
]

def capture_screenshots(url, output_dir, label):
    """Capture full-page screenshots at all viewports."""
    os.makedirs(output_dir, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for vp in VIEWPORTS:
            page = browser.new_page(viewport={"width": vp["width"], "height": vp["height"]})
            try:
                page.goto(url, wait_until="networkidle", timeout=30000)
            except:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(5000)

            # Dismiss cookie banners / overlays
            page.evaluate("""() => {
                document.querySelectorAll(
                    '[class*="cookie"], [id*="consent"], [class*="gdpr"], [class*="banner"]'
                ).forEach(el => el.remove());
            }""")
            page.wait_for_timeout(1000)

            # Force all animations to their end state for consistent screenshots
            page.evaluate("""() => {
                document.querySelectorAll('*').forEach(el => {
                    el.style.animationDelay = '0s';
                    el.style.animationDuration = '0s';
                    el.style.transitionDuration = '0s';
                });
                // Ensure lazy images are visible
                document.querySelectorAll('img[loading="lazy"]').forEach(img => {
                    img.removeAttribute('loading');
                });
                // Force opacity on animated elements
                document.querySelectorAll('[class*="animate"]').forEach(el => {
                    el.style.opacity = '1';
                    el.style.transform = 'none';
                });
            }""")

            # Scroll to bottom then back to top to trigger lazy loading
            page.evaluate("""() => {
                return new Promise(resolve => {
                    let h = document.body.scrollHeight;
                    let pos = 0;
                    let timer = setInterval(() => {
                        pos += window.innerHeight;
                        window.scrollTo(0, pos);
                        if (pos >= h) { clearInterval(timer); window.scrollTo(0, 0); resolve(); }
                    }, 100);
                });
            }""")
            page.wait_for_timeout(1000)

            path = os.path.join(output_dir, f"{label}-{vp['name']}.png")
            page.screenshot(path=path, full_page=True)
            page.close()
        browser.close()
```

### Step 2 — Pixel diff between original and converted

```python
from PIL import Image, ImageChops, ImageStat
import math

def pixel_diff(img_path_a, img_path_b, diff_output_path):
    """
    Compare two screenshots pixel-by-pixel.
    Returns a similarity score (0-100%) and saves a visual diff image.
    """
    img_a = Image.open(img_path_a).convert("RGB")
    img_b = Image.open(img_path_b).convert("RGB")

    # Resize to same dimensions (use the smaller height to avoid scroll-length mismatch)
    w = min(img_a.width, img_b.width)
    h = min(img_a.height, img_b.height)
    img_a = img_a.crop((0, 0, w, h))
    img_b = img_b.crop((0, 0, w, h))

    # Compute difference
    diff = ImageChops.difference(img_a, img_b)
    diff.save(diff_output_path)

    # Calculate similarity percentage
    stat = ImageStat.Stat(diff)
    # Average pixel difference across RGB channels (0-255 scale)
    avg_diff = sum(stat.mean) / 3.0
    similarity = max(0, 100.0 - (avg_diff / 255.0 * 100.0))

    return {
        "similarity": round(similarity, 1),
        "avg_pixel_diff": round(avg_diff, 2),
        "diff_image": diff_output_path,
        "size_a": f"{img_a.width}x{img_a.height}",
        "size_b": f"{img_b.width}x{img_b.height}",
    }
```

### Scoring thresholds

| Similarity | Rating | Meaning |
|-----------|--------|---------|
| ≥ 95% | Excellent | Near pixel-perfect — minor sub-pixel / font rendering differences |
| 90–95% | Good | Slight layout shifts, acceptable for most use cases |
| 80–90% | Fair | Noticeable differences — likely missing CSS rules or shifted elements |
| < 80% | Poor | Significant visual regression — investigate CSS extraction issues |

## Phase 3 — Interactive Element Audit

### Step 1 — Collect interactive elements from both sources

Run the same interactive element detection script (from `site-discovery.md` Phase A2) on both the original site and the local dev server:

```python
def collect_interactive_elements(page):
    """Detect all interactive elements on a page via computed styles and DOM."""
    return page.evaluate("""() => {
        const results = [];
        const seen = new Set();

        document.querySelectorAll('*').forEach(el => {
            const rect = el.getBoundingClientRect();
            if (rect.width === 0 || rect.height === 0) return;

            const style = getComputedStyle(el);
            const tag = el.tagName.toLowerCase();

            const signals = [];
            if (tag === 'a' && el.href) signals.push('link');
            if (tag === 'button') signals.push('button');
            if (['input', 'select', 'textarea'].includes(tag)) signals.push('form-control');
            if (el.getAttribute('role') === 'button') signals.push('role-button');
            if (el.getAttribute('aria-expanded') !== null) signals.push('expandable');
            if (el.getAttribute('aria-haspopup') !== null) signals.push('has-popup');
            if (style.cursor === 'pointer') signals.push('cursor-pointer');
            if (el.onclick !== null) signals.push('onclick');

            if (signals.length === 0) return;

            const key = `${Math.round(rect.x/10)},${Math.round(rect.y/10)},${Math.round(rect.width/10)}`;
            if (seen.has(key)) return;
            seen.add(key);

            results.push({
                tag, text: el.innerText?.trim().substring(0, 80) || '',
                href: el.href || '', signals,
                top: Math.round(rect.top), left: Math.round(rect.left),
                width: Math.round(rect.width), height: Math.round(rect.height),
            });
        });
        return results;
    }""")
```

### Step 2 — Diff interactive elements

```python
def diff_interactive_elements(original_elements, converted_elements):
    """
    Compare interactive elements between original site and converted project.
    Match by text content + approximate position.
    """
    results = {"matched": [], "missing": [], "extra": [], "degraded": []}

    # Index converted elements by text for fast lookup
    converted_by_text = {}
    for el in converted_elements:
        text = el["text"].lower().strip()
        if text:
            converted_by_text.setdefault(text, []).append(el)

    matched_converted = set()
    for orig in original_elements:
        text = orig["text"].lower().strip()
        if not text:
            continue

        candidates = converted_by_text.get(text, [])
        best_match = None
        best_dist = float("inf")

        for cand in candidates:
            cand_id = id(cand)
            if cand_id in matched_converted:
                continue
            # Position proximity (allow ±200px tolerance for layout shifts)
            dist = abs(orig["top"] - cand["top"]) + abs(orig["left"] - cand["left"])
            if dist < best_dist:
                best_dist = dist
                best_match = cand
                best_match_id = cand_id

        if best_match and best_dist < 400:
            matched_converted.add(best_match_id)
            # Check for signal degradation
            orig_signals = set(orig["signals"])
            conv_signals = set(best_match["signals"])
            lost_signals = orig_signals - conv_signals
            if lost_signals:
                results["degraded"].append({
                    "text": orig["text"],
                    "lost_signals": list(lost_signals),
                    "original_signals": orig["signals"],
                    "converted_signals": best_match["signals"],
                })
            else:
                results["matched"].append({"text": orig["text"], "signals": orig["signals"]})
        else:
            results["missing"].append({
                "text": orig["text"],
                "signals": orig["signals"],
                "position": f"({orig['left']}, {orig['top']})",
            })

    # Elements in converted but not in original
    for cand in converted_elements:
        if id(cand) not in matched_converted and cand["text"]:
            results["extra"].append({"text": cand["text"], "signals": cand["signals"]})

    return results
```

## Phase 4 — Hover State Comparison

Capture screenshots of key interactive elements in their hover state on both sites:

```python
def capture_hover_states(page, elements, output_dir, label, max_elements=10):
    """
    Hover over interactive elements and screenshot each one.
    Focus on nav links, buttons, and CTAs.
    """
    os.makedirs(output_dir, exist_ok=True)
    hover_shots = []

    # Prioritize nav links and buttons
    priority_elements = sorted(elements, key=lambda e: (
        0 if 'link' in e['signals'] else
        1 if 'button' in e['signals'] else
        2 if 'cursor-pointer' in e['signals'] else 3
    ))[:max_elements]

    for i, el in enumerate(priority_elements):
        try:
            # Find the element by text content
            text = el["text"]
            if not text or len(text) < 2:
                continue

            locator = page.get_by_text(text, exact=False).first
            if not locator.is_visible():
                continue

            # Scroll into view
            locator.scroll_into_view_if_needed()
            page.wait_for_timeout(200)

            # Screenshot BEFORE hover
            before_path = os.path.join(output_dir, f"{label}-hover-{i}-before.png")
            locator.screenshot(path=before_path)

            # Hover and screenshot
            locator.hover()
            page.wait_for_timeout(500)  # Wait for transition to complete
            after_path = os.path.join(output_dir, f"{label}-hover-{i}-after.png")
            locator.screenshot(path=after_path)

            hover_shots.append({
                "text": text,
                "before": before_path,
                "after": after_path,
                "has_hover_effect": before_path != after_path,  # Will be checked via pixel diff
            })
        except Exception:
            continue

    return hover_shots


def diff_hover_states(original_hovers, converted_hovers):
    """
    Compare hover effects: does the converted site reproduce the same hover transitions?
    """
    results = {"matching": [], "missing_hover": [], "different_hover": []}

    converted_by_text = {h["text"].lower().strip(): h for h in converted_hovers}

    for orig in original_hovers:
        text_key = orig["text"].lower().strip()
        conv = converted_by_text.get(text_key)

        if not conv:
            results["missing_hover"].append({"text": orig["text"]})
            continue

        # Compare before→after pixel diff for both
        orig_diff = pixel_diff(orig["before"], orig["after"],
                               orig["before"].replace("-before.png", "-diff.png"))
        conv_diff = pixel_diff(conv["before"], conv["after"],
                               conv["before"].replace("-before.png", "-diff.png"))

        orig_has_hover = orig_diff["avg_pixel_diff"] > 2.0
        conv_has_hover = conv_diff["avg_pixel_diff"] > 2.0

        if orig_has_hover and not conv_has_hover:
            results["missing_hover"].append({
                "text": orig["text"],
                "original_diff": orig_diff["avg_pixel_diff"],
                "converted_diff": conv_diff["avg_pixel_diff"],
            })
        elif orig_has_hover and conv_has_hover:
            # Both have hover — check if they're similar
            magnitude_ratio = conv_diff["avg_pixel_diff"] / max(orig_diff["avg_pixel_diff"], 0.1)
            if 0.3 < magnitude_ratio < 3.0:
                results["matching"].append({"text": orig["text"]})
            else:
                results["different_hover"].append({
                    "text": orig["text"],
                    "original_magnitude": orig_diff["avg_pixel_diff"],
                    "converted_magnitude": conv_diff["avg_pixel_diff"],
                })
        else:
            results["matching"].append({"text": orig["text"]})

    return results
```

## Phase 5 — Animation & Transition Audit

### Step 1 — Extract all CSS animations and transitions from both sources

```python
def extract_animations(page):
    """Extract all @keyframes, transitions, and animated elements from a page."""
    return page.evaluate("""() => {
        const result = {
            keyframes: [],
            transitions: [],
            animated_elements: [],
        };

        // 1. Collect @keyframes from all stylesheets
        for (const sheet of document.styleSheets) {
            try {
                for (const rule of sheet.cssRules) {
                    if (rule instanceof CSSKeyframesRule) {
                        const steps = [];
                        for (const kf of rule.cssRules) {
                            steps.push({
                                offset: kf.keyText,
                                properties: kf.style.cssText,
                            });
                        }
                        result.keyframes.push({
                            name: rule.name,
                            steps: steps,
                        });
                    }
                }
            } catch(e) { /* cross-origin */ }
        }

        // 2. Scan all visible elements for active animations and transitions
        document.querySelectorAll('*').forEach(el => {
            const rect = el.getBoundingClientRect();
            if (rect.width === 0 || rect.height === 0) return;

            const style = getComputedStyle(el);

            // Check for CSS transitions
            const transitionProp = style.transitionProperty;
            const transitionDur = style.transitionDuration;
            if (transitionProp && transitionProp !== 'none' &&
                transitionDur && transitionDur !== '0s') {
                result.transitions.push({
                    tag: el.tagName.toLowerCase(),
                    classes: el.className?.toString().substring(0, 120) || '',
                    text: el.innerText?.trim().substring(0, 50) || '',
                    property: transitionProp,
                    duration: transitionDur,
                    timing: style.transitionTimingFunction,
                    delay: style.transitionDelay,
                });
            }

            // Check for CSS animations
            const animName = style.animationName;
            const animDur = style.animationDuration;
            if (animName && animName !== 'none' &&
                animDur && animDur !== '0s') {
                result.animated_elements.push({
                    tag: el.tagName.toLowerCase(),
                    classes: el.className?.toString().substring(0, 120) || '',
                    text: el.innerText?.trim().substring(0, 50) || '',
                    animation_name: animName,
                    duration: animDur,
                    timing: style.animationTimingFunction,
                    delay: style.animationDelay,
                    iteration: style.animationIterationCount,
                    direction: style.animationDirection,
                    fill_mode: style.animationFillMode,
                    top: Math.round(rect.top),
                    left: Math.round(rect.left),
                });
            }
        });

        return result;
    }""")
```

### Step 2 — Diff animations

```python
def diff_animations(original_anims, converted_anims):
    """Compare animation inventory between original and converted."""
    results = {
        "keyframes_match": [],
        "keyframes_missing": [],
        "keyframes_extra": [],
        "transitions_match": [],
        "transitions_missing": [],
        "animated_elements_match": [],
        "animated_elements_missing": [],
    }

    # 1. Compare @keyframes definitions
    orig_kf_names = {kf["name"] for kf in original_anims["keyframes"]}
    conv_kf_names = {kf["name"] for kf in converted_anims["keyframes"]}

    results["keyframes_match"] = list(orig_kf_names & conv_kf_names)
    results["keyframes_missing"] = list(orig_kf_names - conv_kf_names)
    results["keyframes_extra"] = list(conv_kf_names - orig_kf_names)

    # 2. Compare transitions (by element class + property)
    orig_transitions = {
        f"{t['classes']}::{t['property']}": t for t in original_anims["transitions"]
    }
    conv_transitions = {
        f"{t['classes']}::{t['property']}": t for t in converted_anims["transitions"]
    }

    for key, orig_t in orig_transitions.items():
        if key in conv_transitions:
            results["transitions_match"].append({
                "element": orig_t["text"] or orig_t["classes"][:60],
                "property": orig_t["property"],
            })
        else:
            results["transitions_missing"].append({
                "element": orig_t["text"] or orig_t["classes"][:60],
                "property": orig_t["property"],
                "duration": orig_t["duration"],
            })

    # 3. Compare animated elements (by animation name + approximate position)
    orig_by_anim = {}
    for ae in original_anims["animated_elements"]:
        key = ae["animation_name"]
        orig_by_anim.setdefault(key, []).append(ae)

    conv_by_anim = {}
    for ae in converted_anims["animated_elements"]:
        key = ae["animation_name"]
        conv_by_anim.setdefault(key, []).append(ae)

    for anim_name, orig_list in orig_by_anim.items():
        if anim_name in conv_by_anim:
            results["animated_elements_match"].append({
                "animation": anim_name,
                "original_count": len(orig_list),
                "converted_count": len(conv_by_anim[anim_name]),
            })
        else:
            results["animated_elements_missing"].append({
                "animation": anim_name,
                "count": len(orig_list),
                "sample_text": orig_list[0].get("text", ""),
            })

    return results
```

## Phase 6 — Scroll & Sticky Element Validation

```python
def validate_scroll_behavior(page):
    """Check for sticky/fixed elements and smooth scroll behavior."""
    return page.evaluate("""() => {
        const result = {
            sticky_elements: [],
            fixed_elements: [],
            smooth_scroll: false,
        };

        // Check if smooth scroll is enabled
        const htmlStyle = getComputedStyle(document.documentElement);
        result.smooth_scroll = htmlStyle.scrollBehavior === 'smooth';

        // Find sticky and fixed elements
        document.querySelectorAll('*').forEach(el => {
            const rect = el.getBoundingClientRect();
            if (rect.width === 0 || rect.height === 0) return;
            const style = getComputedStyle(el);

            if (style.position === 'sticky') {
                result.sticky_elements.push({
                    tag: el.tagName.toLowerCase(),
                    classes: el.className?.toString().substring(0, 80) || '',
                    text: el.innerText?.trim().substring(0, 50) || '',
                    top: style.top,
                });
            }
            if (style.position === 'fixed') {
                result.fixed_elements.push({
                    tag: el.tagName.toLowerCase(),
                    classes: el.className?.toString().substring(0, 80) || '',
                    text: el.innerText?.trim().substring(0, 50) || '',
                    top: Math.round(rect.top),
                    left: Math.round(rect.left),
                });
            }
        });

        return result;
    }""")


def diff_scroll_behavior(original_scroll, converted_scroll):
    """Compare scroll-related behaviors."""
    results = {
        "smooth_scroll": {
            "original": original_scroll["smooth_scroll"],
            "converted": converted_scroll["smooth_scroll"],
            "match": original_scroll["smooth_scroll"] == converted_scroll["smooth_scroll"],
        },
        "sticky_elements": {
            "original_count": len(original_scroll["sticky_elements"]),
            "converted_count": len(converted_scroll["sticky_elements"]),
            "match": len(original_scroll["sticky_elements"]) == len(converted_scroll["sticky_elements"]),
        },
        "fixed_elements": {
            "original_count": len(original_scroll["fixed_elements"]),
            "converted_count": len(converted_scroll["fixed_elements"]),
            "match": len(original_scroll["fixed_elements"]) == len(converted_scroll["fixed_elements"]),
        },
    }
    return results
```

## Full Validation Runner

Orchestrates all phases and produces the final report:

```python
def run_validation(original_url, project_dir, output_dir="validation-report"):
    """
    Full validation pipeline: compare original site vs. converted React project.
    """
    import json

    os.makedirs(output_dir, exist_ok=True)
    report = {}
    local_url = "http://localhost:3000"

    # --- Start dev server ---
    server_proc = start_dev_server(project_dir)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            # ========== Phase 2: Visual comparison ==========
            capture_screenshots(original_url, output_dir, "original")
            capture_screenshots(local_url, output_dir, "converted")

            visual_results = {}
            for vp in VIEWPORTS:
                orig_img = os.path.join(output_dir, f"original-{vp['name']}.png")
                conv_img = os.path.join(output_dir, f"converted-{vp['name']}.png")
                diff_img = os.path.join(output_dir, f"diff-{vp['name']}.png")
                visual_results[vp["name"]] = pixel_diff(orig_img, conv_img, diff_img)
            report["visual"] = visual_results

            # ========== Phase 3: Interactive elements ==========
            page_orig = browser.new_page(viewport={"width": 1440, "height": 900})
            page_orig.goto(original_url, wait_until="networkidle", timeout=30000)
            orig_elements = collect_interactive_elements(page_orig)

            page_conv = browser.new_page(viewport={"width": 1440, "height": 900})
            page_conv.goto(local_url, wait_until="networkidle", timeout=30000)
            conv_elements = collect_interactive_elements(page_conv)

            report["interactions"] = diff_interactive_elements(orig_elements, conv_elements)

            # ========== Phase 4: Hover states ==========
            orig_hovers = capture_hover_states(
                page_orig, orig_elements, output_dir, "original")
            conv_hovers = capture_hover_states(
                page_conv, conv_elements, output_dir, "converted")
            report["hover_states"] = diff_hover_states(orig_hovers, conv_hovers)

            # ========== Phase 5: Animations ==========
            orig_anims = extract_animations(page_orig)
            conv_anims = extract_animations(page_conv)
            report["animations"] = diff_animations(orig_anims, conv_anims)

            # ========== Phase 6: Scroll behavior ==========
            orig_scroll = validate_scroll_behavior(page_orig)
            conv_scroll = validate_scroll_behavior(page_conv)
            report["scroll"] = diff_scroll_behavior(orig_scroll, conv_scroll)

            page_orig.close()
            page_conv.close()
            browser.close()

    finally:
        server_proc.terminate()
        server_proc.wait()

    # ========== Write report ==========
    report_path = os.path.join(output_dir, "validation-report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    return report
```

## Report Interpretation

### Visual Fidelity

```
VISUAL COMPARISON
  Desktop (1440px):  96.2% similarity  ✓ Excellent
  Tablet  (768px):   93.1% similarity  ✓ Good
  Mobile  (375px):   89.4% similarity  △ Fair — check diff-mobile.png
```

- Open `diff-*.png` to see exactly where the differences are (bright pixels = differences)
- Common causes of low similarity: missing fonts (fallback renders differently), image loading timing, scroll-triggered animations not firing

### Interaction Diff

```
INTERACTIVE ELEMENTS
  Matched:   24/28 elements (85.7%)
  Missing:   4 elements
    - "Import from Figma" (button) at (890, 340)
    - "Watch demo" (cursor-pointer) at (650, 520)
    - dropdown trigger "Resources" (expandable) at (720, 45)
    - "Newsletter signup" (form-control) at (300, 2400)
  Degraded:  2 elements (lost signals)
    - "Pricing" link lost: cursor-pointer
    - "Get started" button lost: has-popup
```

### Hover State Diff

```
HOVER STATES
  Matching:       8/10 elements have correct hover effects
  Missing hover:  2 elements lost hover transitions
    - "Features" nav link — original has underline slide, converted has none
    - "Get started" CTA — original has glow effect, converted is static
```

### Animation Diff

```
ANIMATIONS & TRANSITIONS
  @keyframes:
    Matched: 5 (fadeIn, slideUp, pulse, marquee, shimmer)
    Missing: 2 (float, gradientShift)
  Transitions:
    Matched: 12 elements
    Missing: 3 elements
      - nav-link hover transition (color 0.2s)
      - card hover scale (transform 0.3s)
      - button hover background (background-color 0.15s)
  Animated elements:
    Matched: 8 (fadeIn: 4, slideUp: 3, pulse: 1)
    Missing: 3 (float: 2, gradientShift: 1)
```

### Scroll Behavior

```
SCROLL BEHAVIOR
  Smooth scroll:     ✓ match (both enabled)
  Sticky elements:   ✓ match (1 original, 1 converted)
  Fixed elements:    ✓ match (0 original, 0 converted)
```

## Auto-Fix Suggestions

Based on the validation diff, generate actionable fix suggestions:

| Issue | Suggested Fix |
|-------|--------------|
| Missing @keyframes `float` | Copy the `@keyframes float` definition from original CSS into `globals.css` |
| Nav link missing hover transition | Add `transition: color 0.2s ease` to `.nav-link` in globals.css |
| Button lost `cursor-pointer` | Add `cursor: pointer` to the button's CSS class |
| Missing interactive element | Check if the element was stripped during HTML→JSX conversion; verify component JSX |
| Low visual similarity on mobile | Compare `diff-mobile.png` — likely a missing `@media` breakpoint rule |
| Hover effect not reproducing | Check if `:hover` pseudo-class rules were included in globals.css |

## Integration with Phase 5

Validation runs AFTER Phase 5 (Build Verification) succeeds. If `--validate` flag is set or Mode C is used:

1. Phase 5 confirms `npm run build` passes
2. Phase 6 starts the dev server with `npm run dev`
3. Runs the full validation pipeline
4. Outputs the validation report
5. If critical issues found (visual < 80% or > 30% interactions missing), attempts auto-fix (up to 2 rounds):
   - Apply fix suggestions to CSS/components
   - Re-run `npm run build`
   - Re-run validation
6. Includes final validation results in the conversion report

## Validation Output Files

```
validation-report/
├── original-desktop.png       # Full-page screenshot of original (desktop)
├── original-tablet.png        # Full-page screenshot of original (tablet)
├── original-mobile.png        # Full-page screenshot of original (mobile)
├── converted-desktop.png      # Full-page screenshot of converted (desktop)
├── converted-tablet.png       # Full-page screenshot of converted (tablet)
├── converted-mobile.png       # Full-page screenshot of converted (mobile)
├── diff-desktop.png           # Pixel diff visualization (desktop)
├── diff-tablet.png            # Pixel diff visualization (tablet)
├── diff-mobile.png            # Pixel diff visualization (mobile)
├── original-hover-*-before.png  # Hover state screenshots (original)
├── original-hover-*-after.png
├── converted-hover-*-before.png # Hover state screenshots (converted)
├── converted-hover-*-after.png
└── validation-report.json     # Full structured report
```

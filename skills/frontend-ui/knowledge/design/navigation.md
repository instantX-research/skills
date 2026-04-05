# Navigation System Design

**Scope:** Navigation architecture and visual design patterns. For ARIA/keyboard implementation of nav components, see `implementation/code-standards-extended.md`. For icon choices in nav, see the SVG decision tree in `implementation/code-standards-extended.md`.

Navigation is the skeleton of every page. The right navigation pattern is invisible — users find what they need without noticing the system. The wrong one creates friction on every interaction.

---

## Choosing a Navigation Pattern

The primary decision: **top nav vs. sidebar**.

| Signal | → Top nav | → Sidebar |
|---|---|---|
| Page count | ≤ 7 top-level sections | > 7 sections, or deep hierarchy |
| Content type | Marketing, docs, editorial | Application, dashboard, tool |
| Screen usage | Content needs full width | Content lives in a defined area |
| Mobile | Hamburger collapses cleanly | Drawer or bottom tab bar |
| User frequency | Occasional visits | Daily use, power users |

**Rule:** Marketing sites → top nav. Applications → sidebar. Never use both as primary navigation simultaneously.

---

## Top Navigation

### Anatomy

```
┌────────────────────────────────────────────────────────────────┐
│  [Logo]    Product  Solutions  Pricing  Blog      [Login] [CTA]│
└────────────────────────────────────────────────────────────────┘
```

- **Logo:** left-aligned, links to homepage — clickable area minimum 44px tall
- **Primary links:** 5–7 items maximum (Hick's Law — more choices = longer decision time)
- **Utility actions:** right-aligned — login, sign up, search, CTA button
- **CTA button:** one only, primary variant, rightmost element
- Height: 56–64px for marketing sites, 48px for app top bars

### Scroll behavior — 4 options

**1. Static (no scroll behavior)**
Nav stays at top, scrolls away with page. Use only for short pages or when full-screen content is the priority (landing page hero videos).

**2. Sticky with blur glass** *(most common for marketing sites)*
```css
.nav {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px) saturate(180%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  transition: background 200ms ease;
}
```
On dark sites: `background: rgba(9, 9, 11, 0.85)`.

**3. Appears on scroll-up (hide-on-scroll)**
Nav slides out when scrolling down, slides back in when scrolling up. Maximizes reading space.
```js
// Show nav when scrolling up, hide when scrolling down
let lastY = 0
window.addEventListener('scroll', () => {
  const currentY = window.scrollY
  nav.style.transform = currentY > lastY && currentY > 80
    ? 'translateY(-100%)'
    : 'translateY(0)'
  lastY = currentY
})
```
Use with `transition: transform 200ms ease-out` on the nav element.

**4. Shrinking nav**
Nav is taller at the top (e.g., 80px), shrinks to compact (56px) after scrolling past 80px. Signals you're inside the page.
```css
.nav { height: 80px; transition: height 200ms ease; }
.nav.scrolled { height: 56px; }
```

### Dropdown menus

Use only when there are genuine sub-categories (≥ 3 items per group).

**Mega dropdown** (for marketing sites with many products/solutions):
```
Solutions ▼
┌──────────────────────────────────────────────┐
│ By use case           By team                │
│ ─────────────         ─────────              │
│ ◻ Analytics           ◻ Engineering          │
│ ◻ Automation          ◻ Marketing            │
│ ◻ Reporting           ◻ Operations           │
│                                              │
│ [Featured: New → Product announcement]       │
└──────────────────────────────────────────────┘
```

**Simple dropdown** (≤ 6 items, no categories):
```
Product ▼
┌─────────────────┐
│ Features        │
│ Pricing         │
│ Changelog       │
│ ─────────────── │
│ Documentation ↗ │
└─────────────────┘
```

**Dropdown rules:**
- Open on hover (desktop) AND on click (keyboard/touch) — both must work
- `role="menu"` + `aria-expanded` on the trigger
- Close on: click outside, Escape key, focus leaving the menu
- Dividers separate logical groups — use `<hr>` with `role="separator"`
- External links get `↗` icon and `target="_blank" rel="noopener"`

---

## Sidebar Navigation

### Hierarchy levels

Sidebars support 2 levels maximum. Three levels are a sign the information architecture needs rethinking.

```
┌─────────────────────┐
│ [Logo / app name]   │
│                     │
│ ○ Overview          │  ← Level 1 (icon + label)
│ ○ Analytics      ▸  │  ← Level 1 with children
│   ├ Traffic         │  ← Level 2 (indented, no icon)
│   ├ Conversions     │
│   └ Revenue         │
│ ● Settings          │  ← Active item
│                     │
│ ─────────────────── │  ← Group divider
│ ○ Help              │
│ [User avatar] Name  │  ← User/account section at bottom
└─────────────────────┘
```

### Visual rules

- **Width:** 240–280px. Narrower feels cramped; wider wastes content space.
- **Active state:** filled background (`--color-bg-subtle`), accent left border (2–3px), or accent text color. One of these, not all three.
- **Hover state:** lighter background fill (`--color-bg-subtle` at 50% opacity). No transform.
- **Icons:** 16–18px, same color as label, align to the same grid. Use icons consistently — either all items have icons or none do. Never a mix.
- **Group headers:** 10–11px, uppercase, wide letter-spacing, muted color, no interaction
- **Bottom section:** account/user info lives at the bottom, separated by a divider — never mix with navigation links

### Collapsible sidebar

For apps where content needs full width occasionally.

**Behavior:** Clicking a toggle collapses the sidebar to icon-only (64px wide) or slides it off-screen entirely.

```css
.sidebar {
  width: 256px;
  transition: width 200ms var(--ease-out);
  overflow: hidden;
}
.sidebar.collapsed {
  width: 64px;  /* icon-only mode */
}
.sidebar.collapsed .nav-label {
  opacity: 0;
  pointer-events: none;
}
```

**Icon-only collapsed rules:**
- Show a tooltip on hover for each item (since labels are hidden)
- Active item still gets visual indicator even in collapsed mode
- The collapse toggle button lives at the top of the sidebar

### Sidebar on mobile

Sidebar navigation becomes a **drawer** on mobile:
- Full-height, slides in from left
- Overlay backdrop (`rgba(0,0,0,0.4)`) covers the content
- Closes on backdrop tap, Escape key, or navigation
- Width: `min(280px, 85vw)` — never full screen
- Trigger: hamburger menu in the top bar

---

## Mobile Navigation

### 4 patterns by product type

**1. Hamburger + Drawer** *(marketing sites, content sites)*
```
☰  [Logo]                       (top bar)

    ←  [Logo]
    ─────────────
    Home
    Features
    Pricing
    Blog
    ─────────────
    [Login]
    [Get started]
```
- Drawer slides in from left or right (left is more conventional)
- Full-height overlay
- Links are larger tap targets (min 48px height)
- **Critical:** The mobile menu container AND the hamburger toggle button must be `display: none`
  in the base (desktop) styles. Only show them inside the mobile media query. Otherwise the
  mobile menu renders visibly on desktop alongside the top nav, creating duplicate navigation.
  ```css
  /* Base — hidden on desktop */
  .nav-mobile { display: none; }
  .nav-toggle { display: none; }

  /* Mobile — show toggle, menu opens on interaction */
  @media (max-width: 768px) {
    .nav-links { display: none; }
    .nav-toggle { display: flex; }
    .nav-mobile.open { display: block; }
  }
  ```

**2. Bottom Tab Bar** *(apps with 3–5 primary sections)*
```
┌────────────────────────────────────┐
│  App content                       │
│                                    │
│                                    │
├────────────────────────────────────┤
│  🏠     📊     ➕     💬     👤    │
│ Home Analytics Add  Messages  You  │
└────────────────────────────────────┘
```
- 3–5 tabs maximum (more = too small tap targets)
- Active tab: filled icon + accent color label
- Center tab can be a primary action (+ button, camera, compose)
- `padding-bottom: env(safe-area-inset-bottom)` — mandatory for iPhone home indicator
- Tab bar height: 56px + safe area

**3. Full-screen overlay** *(agency sites, portfolio, cinematic experiences)*
```
[✕]    [Logo]

    01  Work
    02  About
    03  Services
    04  Contact

    [Instagram] [Twitter] [Dribbble]
```
- Large type (32–48px), generous vertical spacing
- Close button top-right or top-left
- Opening animation: fade in + slide down (`transform: translateY(-20px)` → `translateY(0)`)
- Good fit for Archetype H (Cinematic Portfolio) and C (Chromatic Confidence)

**4. No separate nav** *(single-page sites, minimal personal sites)*
Anchor links within a single page. No separate navigation state. The page IS the navigation.
- Only viable for pages with ≤ 5 sections
- Optional: sticky dot indicators or progress indicator on the right edge

---

## Breadcrumbs

Breadcrumbs show "where you are" in a hierarchy.

```
Home  ›  Products  ›  Electronics  ›  Laptops
```

**When to use:**
- 3+ levels of hierarchy
- Users frequently need to navigate up (e-commerce categories, documentation, admin panels)
- Content pages where arriving from search means no browser history

**When NOT to use:**
- Single-level sites
- Apps where tabs or sidebar already show position
- Landing pages (no hierarchy to show)

**Design rules:**
- Font: 13–14px, same as secondary text
- Separator: `›` or `/` — never `>` (looks like markup) or `→` (directional arrow implies moving forward)
- Current page: muted color or no link — it should not be clickable
- Truncate middle levels on mobile: `Home › … › Current Page`

```html
<nav aria-label="Breadcrumb">
  <ol>
    <li><a href="/">Home</a></li>
    <li><a href="/products">Products</a></li>
    <li aria-current="page">Laptops</li>
  </ol>
</nav>
```

---

## Tabs and Segmented Controls

Both show multiple views of the same content. The difference is context.

| | Tabs | Segmented control |
|---|---|---|
| **Use for** | Different content sections | Different views of the same data |
| **Content relationship** | Each tab is its own topic | Same data, different format/filter |
| **Example** | "Overview / Activity / Settings" | "Monthly / Weekly / Daily" |
| **Visual weight** | Lighter — sits within a page section | Heavier — looks like a control |
| **Max items** | 6 (more → use a dropdown or sidebar) | 4 (more → use a dropdown select) |

### Tab design rules

```
Overview  |  Activity  |  Settings
─────────────────────────────────────
```
- Active tab: 2px accent underline below, or filled background
- Inactive tabs: same font weight as active — only color changes
- Tabs DO NOT use button styles — they are a navigation pattern
- Tab panel has `role="tabpanel"` and `aria-labelledby` pointing to its tab

### Segmented control design rules

```
┌──────────┬──────────┬──────────┐
│  Weekly  │ Monthly  │  Annual  │
└──────────┴──────────┴──────────┘
```
- Looks like a button group: rounded outer container, dividers between options
- Selected option: filled background (elevated surface), weight 500
- All options same width for visual balance
- Height: 32–36px (compact control — not a primary CTA)

---

## Search Integration

Search has two patterns based on prominence.

### Global search (Cmd+K)
For apps where search is a power-user shortcut.
- Trigger: Cmd+K (Mac) / Ctrl+K (Windows) — always both
- Opens a centered modal overlay
- Placeholder: "Search or jump to…" — indicates both search and navigation
- Shows recent items before any query is typed
- Results categorized: Pages, Components, Users, etc.
- Keyboard-navigable: arrow keys move selection, Enter navigates, Escape closes

### Inline search (persistent)
For content-heavy sites (documentation, e-commerce, directories).
- Position: top-right in nav, or prominent top of page
- Min width: 240px desktop, full-width mobile
- Instant results: show dropdown with top 5 results after 300ms debounce
- "See all results" at bottom of dropdown navigates to a full search page

### Search input design

```
┌──────────────────────────────────────┐
│ 🔍  Search...                    ⌘K │
└──────────────────────────────────────┘
```
- Leading search icon (`aria-hidden`)
- Trailing keyboard shortcut hint (hidden on mobile)
- Border: `1px solid var(--color-border)` at rest, accent on focus
- Border radius: matches the product's overall radius system (don't use pill shape unless intentional)

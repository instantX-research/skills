# Design Principles — Motion & Animation

**When to load:** At Phase 4 start when MOTION_INTENSITY ≥ 4. Supplements `design-principles.md` (always-loaded core). For basic easing curves and duration scale, see the core file.

---

## Animation orchestration — choreographing complex UI

Individual easing curves are in the core file. This section covers multi-element sequences.

### Staggered list entry

When a list of items loads, stagger their appearance so they cascade rather than pop all at once.

```css
/* CSS-only stagger using custom property + animation-delay */
.list-item {
  opacity: 0;
  transform: translateY(8px);
  animation: item-enter 300ms var(--ease-out-expo) forwards;
}

.list-item:nth-child(1)  { animation-delay: 0ms; }
.list-item:nth-child(2)  { animation-delay: 40ms; }
.list-item:nth-child(3)  { animation-delay: 80ms; }
.list-item:nth-child(4)  { animation-delay: 120ms; }
.list-item:nth-child(5)  { animation-delay: 160ms; }
/* Cap delay at ~200ms for long lists — don't make users wait */

@keyframes item-enter {
  to { opacity: 1; transform: translateY(0); }
}
```

```tsx
// React: dynamic stagger via style prop
{items.map((item, i) => (
  <div
    key={item.id}
    style={{ animationDelay: `${Math.min(i * 40, 200)}ms` }}
    className="list-item"
  >
    {/* content */}
  </div>
))}
```

**Stagger timing rules:**
- 30–50ms between items (faster = snappier, slower = theatrical)
- Cap total stagger delay at 200–300ms regardless of list length
- Stagger only on initial load, not on every re-render

### Scroll-triggered reveal

Elements animate in as they enter the viewport. Use `IntersectionObserver`, not scroll listeners.

```tsx
// React hook for scroll-triggered animation
function useScrollReveal(threshold = 0.1) {
  const ref = useRef<HTMLElement>(null)
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) { setIsVisible(true); observer.disconnect() } },
      { threshold }
    )
    if (ref.current) observer.observe(ref.current)
    return () => observer.disconnect()
  }, [threshold])

  return { ref, isVisible }
}

// Usage:
const { ref, isVisible } = useScrollReveal()
<section
  ref={ref}
  className={cn('reveal-section', isVisible && 'revealed')}
>
```

```css
.reveal-section {
  opacity: 0;
  transform: translateY(24px);
  transition: opacity 500ms var(--ease-out-expo), transform 500ms var(--ease-out-expo);
}
.reveal-section.revealed {
  opacity: 1;
  transform: translateY(0);
}

/* Respect reduced motion */
@media (prefers-reduced-motion: reduce) {
  .reveal-section { opacity: 1; transform: none; transition: none; }
}
```

**Scroll reveal rules:**
- Reveal from bottom (translateY 16–32px), never from sides (disorienting)
- One reveal trigger per viewport entry — once revealed, stays revealed
- Don't reveal elements already in the viewport on page load — only off-screen elements
- Threshold 0.1–0.15 (trigger when 10–15% of element is visible)

### Page / route transitions

```tsx
// Next.js App Router: layout-level fade transition
// app/layout.tsx — wrap page content
<div
  key={pathname}  // re-mounts on route change
  className="page-enter"
>
  {children}
</div>
```

```css
.page-enter {
  animation: page-fade-in 200ms var(--ease-out) both;
}
@keyframes page-fade-in {
  from { opacity: 0; transform: translateY(4px); }
  to   { opacity: 1; transform: translateY(0); }
}
```

**Page transition rules:**
- Keep page transitions under 200ms — users are waiting to use the new page
- Simple fade (+tiny translateY) is almost always better than slide transitions
- Shared element transitions (hero image expanding into detail view) are powerful but complex — only use with `View Transitions API` or Motion's `layoutId`
- Never animate the entire page if only a region is changing — animate the changing region instead

### Modal / drawer / sheet enter/exit

```css
/* Modal: scale + fade */
.modal { animation: modal-enter 200ms var(--ease-out-expo); }
@keyframes modal-enter {
  from { opacity: 0; transform: scale(0.96) translateY(4px); }
  to   { opacity: 1; transform: scale(1) translateY(0); }
}

/* Drawer (slides from right): */
.drawer { animation: drawer-enter 300ms var(--ease-out-expo); }
@keyframes drawer-enter {
  from { transform: translateX(100%); }
  to   { transform: translateX(0); }
}

/* Bottom sheet (slides from bottom): */
.sheet { animation: sheet-enter 300ms var(--ease-out-expo); }
@keyframes sheet-enter {
  from { transform: translateY(100%); }
  to   { transform: translateY(0); }
}

/* Exit: reverse + slightly faster */
.modal[data-closing] { animation: modal-exit 150ms var(--ease-out) forwards; }
@keyframes modal-exit {
  to { opacity: 0; transform: scale(0.96) translateY(4px); }
}
```

### Mobile drawer pattern
```tsx
// Sidebar becomes an off-canvas drawer on mobile
<nav
  aria-label="Main navigation"
  data-open={isOpen}
  className="sidebar"
>
  {/* ... nav items ... */}
</nav>
{/* Backdrop */}
{isOpen && (
  <div
    aria-hidden="true"
    className="fixed inset-0 bg-black/40 z-40 md:hidden"
    onClick={() => setIsOpen(false)}
  />
)}
```
```css
.sidebar {
  transform: translateX(-100%);
  transition: transform var(--duration-slow) var(--ease-out-expo);
}
.sidebar[data-open='true'] { transform: translateX(0); }
@media (min-width: 768px) {
  .sidebar { transform: none; position: sticky; }  /* always visible on desktop */
}
```

---

## Animation Performance Budget

Apply during Phase 4 generation whenever adding motion. These rules prevent jank and battery drain without eliminating delight.

### Hard limits

- **Max 3 animations running simultaneously** on any given frame. If more are needed, stagger starts so they don't overlap.
- **GPU-safe properties only:** `transform` and `opacity`. Never animate `width`, `height`, `top`, `left`, `margin`, `padding`, `border-width`, or `box-shadow` — these trigger layout or paint.
- **Duration ranges by interaction type:**
  - Micro-interactions (hover, focus): 100–200ms
  - Reveals and entrances (scroll-triggered): 200–400ms
  - Page transitions and panel slides: 300–500ms
  - Ambient / looping animations: 2000ms+ with `ease-in-out`

### Stagger rule

When animating a list or grid of elements, stagger entrance delays by `50–100ms` per item. Cap total stagger at `600ms` regardless of list length — late items should never feel abandoned.

```css
/* Stagger pattern — cap at 6 items worth of delay */
.card:nth-child(1) { animation-delay: 0ms; }
.card:nth-child(2) { animation-delay: 60ms; }
.card:nth-child(3) { animation-delay: 120ms; }
.card:nth-child(4) { animation-delay: 180ms; }
.card:nth-child(5) { animation-delay: 240ms; }
.card:nth-child(n+6) { animation-delay: 300ms; } /* all remaining items share last slot */
```

### `will-change` rules

- Set `will-change: transform` **only** on elements that will animate imminently — not as a blanket performance hint.
- Remove `will-change` after the animation completes (via JS or `:not(:hover)`).
- Never apply `will-change` to more than 3–4 elements simultaneously.

```css
/* Correct: set on hover, remove at rest */
.card { transition: transform 200ms var(--ease-out); }
.card:hover { will-change: transform; transform: translateY(-4px); }
/* will-change auto-removed when :hover ends */
```

### `prefers-reduced-motion` gate

Every non-essential animation must be wrapped. Essential = state change feedback (button active, error shake). Non-essential = entrance reveal, hover lift, ambient motion.

```css
@media (prefers-reduced-motion: no-preference) {
  .card { transition: transform 200ms var(--ease-out); }
  .hero-text { animation: fadeSlideUp 400ms var(--ease-out-expo) both; }
}
/* At reduced motion: elements are still visible, just instant */
```

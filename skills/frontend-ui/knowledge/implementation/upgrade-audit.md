# Upgrade Audit — Priority Order

**When to use:** Load this file for Mode D (Upgrade existing) only. Apply fixes in P1→P10 order. After completing, run Phase 4.5.

---

**P1 — Font swap** *(biggest instant improvement, lowest risk)*
- Generic font (Roboto, Arial, system-ui, Inter with no customization) → swap to Geist, Outfit, Cabinet Grotesk, or Satoshi; or add Inter customizations (letter-spacing, weight variation, pairing)
- No negative heading tracking → add `letter-spacing: -0.025em` to `−0.04em`
- Orphaned words → add `text-wrap: balance` on headings

**P2 — Color palette cleanup**
- Pure `#000000` or pure `#ffffff` bg → replace with off-black/off-white
- AI purple/blue gradient → strip; replace with neutral base + single considered accent
- More than one accent → pick one and remove the rest
- Mixed warm/cool grays → commit to one gray family

**P3 — Hover and active states**
- Buttons with no hover → `background-color` shift + `200ms ease-out`
- No active/pressed feedback → `scale(0.98)` on press
- Instant transitions → add 150–200ms on all interactive elements
- Missing focus rings → visible `outline` for keyboard users

**P4 — Layout and spacing**
- Arbitrary pixel values → convert to 4/8px grid
- No `max-width` → `max-width: 1280px; margin-inline: auto`
- Equal vertical padding everywhere → differentiate component / section / page rhythm

**P5 — Replace generic components**
- 3-equal-column feature cards → asymmetric 2-column or bento grid
- Lucide icons exclusively → introduce Phosphor for differentiation

**P6 — States**
- No loading states → skeleton screens matching layout shape
- No empty states → "getting started" view with primary CTA
- No error states → inline error messages (no `window.alert()`)

**P7 — Typography polish**
- Only 400/700 weights → introduce 500/600 for mid-hierarchy
- Missing tabular figures on data → `font-variant-numeric: tabular-nums`
- Title Case On Every Header → sentence case

**P8 — Responsive & mobile**
- `100vh` → `100dvh`
- Hardcoded font sizes → `clamp()` fluid scale (marketing) or breakpoint-aware (app UI)
- Touch targets < 44px → `min-height: 44px; min-width: 44px`

**P9 — Accessibility**
- Icon-only buttons → `aria-label` + tooltip
- `outline: none` → `focus-visible:outline-2 focus-visible:outline-offset-2`
- Dynamic content → `aria-live="polite"` or `role="alert"`
- Missing skip link → `<a href="#main" class="skip-link">Skip to main content</a>` as first body element

**P10 — Dark mode**
- Hardcoded hex → CSS variables
- No `[data-theme='dark']` → add dark token block
- SVG hardcoded fill → `fill: currentColor`

---

## P11+ — Advanced polish (optional, high-impact)

Apply after P1–P10 are complete. Each adds significant visual differentiation. Details and code in `implementation/advanced-effects.md`.

- **Spotlight border** — cursor-reactive card illumination; biggest single upgrade for dark card grids
- **Variable font animation** — weight/width interpolation on hover or scroll-into-view
- **Grain/noise overlay** — SVG `feTurbulence` at 2–5% opacity; eliminates digital sterility on flat surfaces
- **Colored tinted shadows** — replace `rgba(0,0,0,x)` shadows with hue-matched accent tints
- **True glassmorphism** — `backdrop-filter: blur` + 1px inner border + inner shadow (3 layers required)
- **Broken grid / negative margin** — overlapping elements for Z-axis depth without 3D transforms
- **Outlined-to-fill text** — text stroke reveals fill on scroll-into-view
- **Parallax card stack** — layered cards that separate on scroll

**Priority within P11+:** Spotlight border → grain overlay → tinted shadows → glassmorphism → others.

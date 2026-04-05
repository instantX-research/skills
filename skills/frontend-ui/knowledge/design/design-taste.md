# Design Taste: Craft Standards

**Scope:** Prescriptive rules — what the correct behavior is. For underlying theory (why these rules exist), see `design-principles.md`. For code implementation of these rules, see `implementation/code-standards-core.md` and `implementation/code-standards-extended.md`.

Positive prescriptions for every design decision. Each rule states the correct behavior — not what to avoid.

---

## Typography craft

- Headings use negative tracking: `letter-spacing: -0.02em` to `-0.04em` depending on size
- Type scale uses at least four weights (400, 500, 600, 700) to establish hierarchy
- `line-height` is always explicit: 1.1–1.2 for headings, 1.5–1.65 for body
- Body default is minimum 15px, prefer 16px
- `font-weight: 300` reserved for display-size text ≥ 32px only; all UI body text ≥ 400
- Type system: one display + one body + one mono — no more than three families total

## Color craft

- Text color is near-black: `#0f0f0f`, `#111827`, `#1a1a2e`, or similar — not pure `#000000`
- Page white is one step off: `#fafafa`, `#f9fafb`, `#f8f4ed` — not pure `#ffffff` as the only option
- Accent color covers ≤ 15% of the visual surface — above that it becomes noise, not emphasis
- One primary accent dominates; all supporting colors are clearly subordinate in weight
- Default Tailwind colors are customized with a palette-derived token before use
- Text placed over images has a contrast layer; minimum 4.5:1 contrast ratio always maintained
- Semantic red and green are reserved for status (error/success) — never used decoratively

## Spacing craft

- All spacing values live on the 4/8px grid: 4, 8, 12, 16, 24, 32, 48, 64, 96…
- Component padding, section padding, and page padding are three distinct values
- Sections breathe more than components — vertical rhythm increases at the section boundary
- Body text is left-aligned; centering is reserved for hero headlines and CTA copy only

## Layout craft

- Content max-width is 1280px; prose max-width is `72ch` / `720px`
- Column ratios reflect content importance — equal-weight columns only for equal-importance content
- Mobile layout is designed independently — not a vertically compressed version of desktop
- Navigation includes a visible current-state indicator on the active item

## Component craft

- Primary and secondary buttons differ in both weight and form, not only color
- Every input field has a visible custom focus ring — `outline: none` is replaced, never just removed
- Card layouts establish internal visual hierarchy through size, weight, and spacing
- Every async component has a designed loading state: skeleton screen or spinner
- Every empty state has a meaningful illustration or message plus a primary action CTA
- `cursor: pointer` applies only to interactive elements
- Disabled state uses 40–50% opacity + `cursor: not-allowed`, visually distinct from enabled

## Excellence markers

- Hero sections use asymmetric layout, real photography or abstract pattern, non-centered headline
- Feature sections vary card size, use asymmetric grids, and combine text with real UI screenshots
- Footers contain navigation, useful links, social connections, and a contextual brand statement
- Background variation is limited to one or two intentional transitions per page
- Shadows appear only on floating elements (modals, dropdowns, tooltips) — flat surfaces are flat
- Gradient text sits on a solid or neutral background — gradient-on-gradient makes text illegible
- Social proof sections name specific companies with logos and specific, credible metrics
- Every section heading carries information value — it answers "why is this section here?"
- Dark sections are deliberate design decisions supported by the surrounding composition
- Every section has visual depth through layering, subtle texture, or motion — not plain text on plain background

## Typography detail craft

- Headings and key body text use `text-wrap: balance` or `text-wrap: pretty` to prevent orphaned words
- Subheader style varies across the page: lowercase italics, sentence case, or small-caps — not uniform all-caps
- Numeric data uses `font-variant-numeric: tabular-nums` so columns align in tables and stats
- Type weight scale uses at least 400 / 500 / 600 / 700 to create richer visual hierarchy

## Optical alignment

- Icons inside buttons get a 1–2px visual nudge from mathematical center to achieve perceived balance
- Play/triangle icons shift 1px right to account for the triangle's rightward visual mass
- All centered elements are verified visually, not just checked by measuring coordinates
- Badge text gets 1px top padding when mathematical centering reads as visually low

## Layout precision

- Cards with variable content length pin their CTA with `align-self: end` on the card footer using CSS Grid
- Pricing columns use fixed-height title and price blocks so feature lists align at the same vertical start
- Side-by-side elements (titles, prices, descriptions) share the same Y baseline across all columns
- Gray family is consistent: all neutral tones share one hue tint — no mixing warm and cool grays

## Content quality

- Numeric data uses organic, specific values: "47.2%", "$99.00" — not round "99.9%", "$100.00"
- Persona names are diverse and specific-sounding — not "John Doe" or "Jane Smith"
- Brand names in mockups are contextually invented — not "Acme Corp", "Nexus", or "SmartFlow"
- Copy is plain, specific, and informative — free of: "Elevate", "Seamless", "Unleash", "Next-Gen", "Game-changer", "Delve", "Tapestry", "In the world of…", "Empowering teams"
- Success messages are confident and quiet — no exclamation marks
- Error messages are direct and actionable: "Connection failed. Please try again." — not "Oops!"
- All placeholder copy is real draft content — lorem ipsum is never acceptable
- Section headers use sentence case — not Title Case On Every Word
- Blog post dates and timestamps are varied to appear realistic
- Each distinct user or persona has a unique avatar asset

## Copy craft (microcopy)

Good microcopy is invisible — users don't notice it, they just know what to do. Bad microcopy creates friction at every interaction.

**Button labels**
- Format: verb + object, 2–3 words max — "Create project", "Save changes", "Send invoice"
- Never: "Click here", "Submit", "OK", "Yes" (ambiguous), "Continue" (to what?)
- Destructive actions name what will be destroyed: "Delete account" not "Confirm"
- Loading state: use progressive verb — "Saving…", "Sending…", "Creating…"

**Empty state copy — three-part structure**
1. What's empty (1 line, neutral): "No projects yet"
2. Why it matters or what it enables (1 line): "Projects help you organize your work by client or team"
3. Primary action (button): "Create your first project"
Never: "Nothing here!", "No data found", a lone illustration with no text

**Error messages — three-part anatomy**
1. What happened (specific, no jargon): "Couldn't send your message"
2. Why (if known and useful): "Your session expired"
3. What to do: "Sign in again to continue"
- Plain language: "Your file is too large (max 10 MB)" not "413 Payload Too Large"
- Never blame the user: "Invalid input" → "Enter a valid email address"

**Tooltip copy**
- Adds information the label alone doesn't give — never repeat the button label
- One sentence, no period at the end
- Bad: tooltip on "Delete" that says "Delete this item" — restates the obvious
- Good: tooltip on "Archive" that says "Hidden from view but not permanently deleted"

**Onboarding hints and helper text**
- Write in the user's perspective, not the product's: "Your API key" not "The API key for this integration"
- Present tense, active voice: "Connects to your Slack workspace" not "This will be used to connect to Slack"
- Helper text under a field: shown always (not on hover) — 12–13px, muted color, directly below input

**Number formatting**
- Integers under 1,000: write as-is — "247 users"
- 1,000–9,999: use comma — "1,247 users"  (never "1.2k" below 10,000)
- 10,000+: abbreviate — "14.2k", "2.4M"
- Currency: match locale; always show cents for prices under $10 — "$9.99" not "$10"
- Percentages: one decimal place — "12.4%" not "12%" (unless it's a round number by nature)
- Dates: use "Mar 15" or "March 15, 2025" — never "03/15/25" (ambiguous across locales)

## Iconography

- Phosphor or Heroicons is the primary icon set — Lucide and Feather are not used as the sole choice
- Icon metaphors are specific to the action — not clichéd rocketship for Launch, shield for Security
- All icons within the set share one consistent stroke weight
- Every page includes a branded favicon

## Responsive & mobile

- Full-height layouts use `100dvh` — `100vh` breaks on mobile browsers with dynamic address bars
- Font sizes use `clamp()` for fluid scaling across breakpoints — no hardcoded `px` values for display type
- All interactive elements have a minimum 44×44px tap area
- Fixed bottom UI (nav bars, sticky CTAs) includes `padding-bottom: env(safe-area-inset-bottom)`
- `overflow-x` issues are diagnosed at the source — `overflow-x: hidden` on `<body>` is not acceptable
- Every `:hover` state has a corresponding `:active` equivalent for touch devices
- Element heights that must survive the mobile keyboard use percentages or `dvh`, not `vh`
- All mobile form inputs have `font-size: 16px` minimum to prevent iOS Safari auto-zoom

## Accessibility

- Every removed `outline` is replaced with a custom focus ring of equivalent visibility
- Every icon-only interactive element has an `aria-label` with a descriptive action
- Error states communicate through border color + icon + text label — color alone is insufficient
- Decorative images have `alt=""`; images that carry meaning have a descriptive alt text
- All async updates (toasts, inline errors, loading states) use `aria-live="polite"` or `role="alert"`
- Interactive elements use semantic `<button>` or `<a>` tags; if a `<div>` is unavoidable, add `role="button"` + `tabindex="0"` + keyboard handler
- Every form field has an associated `<label>` — placeholder text alone is not a label
- Modals trap focus within their boundary while open
- Modals return focus to the triggering element on close
- Every interactive action is reachable by keyboard without a mouse

## Dark mode

- Dark mode is a redesigned color system — not a CSS invert of the light palette
- Dark page backgrounds use `#08090a`–`#141414`, not pure `#000000`
- Dark mode text uses `#e8e8e8`–`#f0f0f2`, not pure `#ffffff`
- Accent colors are desaturated 10–20% in dark mode to avoid looking garish on dark surfaces
- Dark mode borders use `rgba(255,255,255,0.08)`–`rgba(255,255,255,0.12)` for perceived depth
- All color values live in CSS custom properties — one token block handles the full dark mode swap
- Images in dark mode use `filter: brightness(0.85) contrast(1.05)` to prevent harsh whiteness
- SVG icons use `fill: currentColor` so they inherit the themed text color automatically
- Dark mode always includes an `@media (prefers-color-scheme: dark)` fallback for JS-off contexts

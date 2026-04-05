# Design Principles — UX Patterns & Interface Design

**When to load:** At Phase 4 start when component count ≥ 4 OR output includes forms, data tables, or navigation. Supplements `design-principles.md` (always-loaded core).

---

## Nielsen's 10 Usability Heuristics — translated to implementation

These are not abstract concepts. Each heuristic maps directly to a code decision.

**1. Visibility of system status**
Users must always know what's happening. In code:
- Every async action needs a loading state (spinner or skeleton)
- Progress bars for multi-step processes (file upload, onboarding)
- Active nav item must have a distinct visual treatment (not just bold)
- Form submission: button changes to "Saving…" + disabled, never stays static
- Toast notifications for background operations that complete out of view

**2. Match between system and real world**
Use the user's language, not the system's. In code:
- Button labels: "Save changes" not "Submit" / "Delete account" not "Deactivate entity"
- Icons must match their universal metaphor (floppy disk = save, gear = settings)
- Error messages in plain language: "Your session expired. Please sign in again." not "401 Unauthorized"
- Date/time in human format: "3 minutes ago" not Unix timestamp
- Destructive actions use red — color carries semantic meaning users already understand

**3. User control and freedom**
Every action must be undoable or escapable. In code:
- Modals and drawers need an X button AND Escape key dismissal
- Destructive actions (Delete, Archive) need a confirmation dialog — not just a "are you sure?" alert, a properly designed modal
- Multi-step flows need a visible Back button on every step
- Form autosave with a "Discard changes" escape hatch
- Never trap users: every dead-end state needs a primary action to continue

**4. Consistency and standards**
Same thing looks and works the same way everywhere. In code:
- One button component, not ad-hoc styled `<button>` tags scattered in JSX
- Icon size: pick 16px or 20px, not both
- If blue means "primary action" on screen A, it means that everywhere
- Destructive = red, always. Success = green, always. Never swap semantic colors for aesthetic reasons
- Keyboard shortcuts are consistent (Cmd+S = save, everywhere it appears)

**5. Error prevention**
Don't let errors happen in the first place. In code:
- Disable a submit button until required fields are filled (don't let users submit an empty form)
- Inline validation on blur (not on submit) — catch the error where it happens
- Confirmation dialogs for destructive, irreversible actions: "This will permanently delete 47 files."
- Auto-save drafts so users don't lose work
- Constrain inputs: date pickers instead of free-text date fields

**6. Recognition over recall**
Don't make users remember — show them. In code:
- Breadcrumbs on deep pages so users always know where they are
- Persistent sidebar with visible current-page highlight
- Recently used items in dropdowns and search
- Show placeholder examples in input fields: `placeholder="e.g. john@company.com"`
- Contextual action menus — show relevant options where the user already is, don't hide them in a settings page

**7. Flexibility and efficiency of use**
Design for both novices and experts. In code:
- Keyboard shortcuts for power users (Cmd+K command palette, Vim keys in code editors)
- Bulk actions for repetitive tasks (select all + delete, not one-by-one)
- Saved filters, templates, pinned items
- Progressive disclosure: simple defaults, advanced options revealed on demand
- Search that works from any screen (global search, not page-scoped)

**8. Aesthetic and minimalist design**
Every element competes for attention. In code:
- Remove labels when context makes them obvious (a search icon in a search box needs no label)
- Empty whitespace is not empty — it's breathing room that reduces cognitive load
- Max 2 CTAs per screen section; more than 2 and none stand out
- Secondary information in smaller, lighter text — not the same weight as primary
- Never add decorative elements that carry no information: empty dividers, random icons, filler gradients

**9. Help users recognize, diagnose, and recover from errors**
Error states are first-class design deliverables. In code:
- Error message anatomy: [icon] + [plain-language problem] + [specific fix]
  - Bad: "Invalid input"
  - Good: "Email address is already in use. [Sign in instead →]"
- Inline errors appear directly under the offending field, not at the top of the form
- Error color (#ef4444 range) for border + icon + message — all three, not just text color
- Never use `window.alert()` — always inline or toast
- Success states are as important as error states: confirm completion explicitly

**10. Help and documentation**
Good UI is self-documenting, but when help is needed it's contextual. In code:
- Tooltip on hover for icon-only buttons (always — icons alone are ambiguous)
- Empty states include brief explanation + primary action CTA, not just "No data"
- Onboarding: first-run experience that shows the product's value before asking for commitment
- Contextual helper text under complex fields, not in a separate help page

---

## Affordance — how elements communicate what they do

Affordance is the visual language of interaction. A user should understand how to interact with an element without thinking.

**Strong affordance signals:**
- Buttons: sufficient height (≥36px), filled background or visible border, pointer cursor
- Links: distinct color from body text, optional underline on hover
- Draggable: drag handle icon (⋮⋮ or ≡), `grab` cursor on hover, `grabbing` while dragging
- Resizable: resize handle at edges, `resize` cursor
- Editable text: subtle underline or input-like appearance when hovered
- Expandable: chevron icon that rotates on open, consistent with system conventions
- Scrollable: content slightly cut off at boundary signals "there's more" (the Closure principle)

**Signifiers vs affordances:**
- Affordance = what an element CAN do (a door can be pushed)
- Signifier = what tells you HOW (a push plate vs a pull handle)
- Design for signifiers, not just affordances: a button that looks like a button IS a signifier

**Anti-affordance (things that look broken):**
- Disabled button with no explanation — add a tooltip: "You need to fill Name first"
- Clickable area smaller than the visual element (icon inside a small `<span>`) — expand the hit target
- Text that looks like a link but isn't (or vice versa)
- A card that is interactive but has no hover state — it looks broken

---

## Progressive disclosure — reveal complexity gradually

Never show everything at once. Complexity should be earned.

**The three levels:**
1. **Primary** — always visible. The main action, the key information.
2. **Secondary** — revealed on hover or expand. Supporting details, additional options.
3. **Tertiary** — revealed on demand. Advanced settings, edge cases, power-user features.

**Implementation patterns:**

```
Simple → Advanced:
  Show "Create account" → after click, reveal full form fields progressively

Tooltip disclosure:
  Icon button → hover reveals label tooltip (always add this)

Accordion:
  Section heading → click expands content (FAQ, settings groups)

"Show more":
  Truncated list of 5 → "Show 12 more" → full list

Inline expansion:
  Collapsed row → click expands inline detail (better than navigating to a new page)

Command palette:
  Surface-level UI → Cmd+K reveals full capability set for power users
```

**Rule:** If a feature is used by <20% of users, put it behind progressive disclosure. If it's used by <5%, put it in settings. Never surface rare edge cases in the primary UI.

---

## Cognitive load — design for the working memory limit

Human working memory holds 5–9 chunks. Design that exceeds this causes overwhelm.

**Three types of cognitive load:**

| Type | Cause | Design response |
|------|-------|----------------|
| **Intrinsic** | Task complexity (unavoidable) | Break into steps, use wizards |
| **Extraneous** | Poor design (avoidable) | Remove noise, simplify layout |
| **Germane** | Meaningful learning | Onboarding, tooltips, progressive reveal |

**Reduce extraneous load in code:**
- Chunk navigation: group 5–7 items max per level, use dividers between groups
- One primary action per screen section — multiple CTAs split attention
- Use `text-wrap: balance` on headings to prevent jarring line breaks
- Consistent component placement: search always top-right, back always top-left
- Remove labels that context makes obvious — a magnifying glass needs no "Search" label next to it in a search bar

**The Miller's Law implication:**
- Max 7 (±2) items in a dropdown, navigation menu, or list before adding search/filter
- Pricing tables: max 3–4 tiers before users stop comparing
- Form: max 5–7 fields per step; split long forms into a multi-step wizard

**The Serial Position Effect:**
- Users remember the first item and last item in a list better than middle items
- Put the most important nav item first OR last, never in the middle
- In pricing, put the recommended tier in the most visually prominent position (center)

---

## Form design system — the most-used, least-designed component category

Forms are where users do real work. Bad form design is the #1 cause of abandoned flows.

### Validation timing strategy

| Trigger | When to use | Why |
|---------|-------------|-----|
| **onBlur** (leave field) | Default for most fields | Catch error exactly when user finishes; not disruptive while typing |
| **onInput** (real-time) | After first error shown; password strength | Once they know there's a rule, real-time feedback is helpful |
| **onSubmit** | Never as the ONLY validation | Users discover errors too late; combine with field-level |
| **Async / server** | Email uniqueness, username availability | Use debounce (500ms) + loading spinner in field |

**The two-phase rule:** Validate on blur to show errors; validate in real-time only after an error has been shown once. Don't interrupt users while they type for the first time.

### Error message anatomy

```
✗  Don't: "Invalid email"
✓  Do:    "Enter a valid email address, e.g. name@company.com"

✗  Don't: "Password too short"
✓  Do:    "Password must be at least 8 characters (currently 5)"

✗  Don't: "An error occurred"
✓  Do:    "Couldn't save — check your internet connection and try again"
```

Error placement: directly below the offending field, never at the top of the form alone.
Use red for: border (`#ef4444`), label, icon, and message text — all four, not just the message.

### Multi-step form / wizard pattern

```
Rules:
1. Show a progress indicator that names each step — not just "Step 2 of 4"
2. Back button on every step (never trap users in a forward-only flow)
3. Persist data across steps (don't lose work if user hits Back)
4. Validate the current step before allowing Next
5. Last step: show a summary of all entered data before final submit
6. Loading state on the final submit button — disable it and show spinner
```

```tsx
// Step indicator pattern
<nav aria-label="Form progress">
  {steps.map((step, i) => (
    <div
      key={step.id}
      aria-current={i === currentStep ? 'step' : undefined}
      className={cn(
        'flex items-center gap-2 text-sm',
        i < currentStep  && 'text-[var(--color-accent)]',        // completed
        i === currentStep && 'text-[var(--color-text-primary)] font-medium', // current
        i > currentStep  && 'text-[var(--color-text-tertiary)]'  // upcoming
      )}
    >
      <span className="step-dot">{i < currentStep ? '✓' : i + 1}</span>
      {step.label}
    </div>
  ))}
</nav>
```

### Field type decision matrix

| Use case | Component | Why |
|----------|-----------|-----|
| One of 2–3 exclusive options | Radio buttons (visible) | See all options at once |
| One of 4–10 options | Select dropdown | Compact; use when options are well-known |
| One of 11+ options | Combobox with search | Dropdown too long to scan |
| Binary toggle (setting) | Toggle switch | Immediate visual feedback |
| Binary confirmation (form) | Checkbox | Explicit user action; readable label |
| Multiple from a list (≤6) | Checkboxes (visible) | All options visible |
| Multiple from a list (7+) | Multi-select combobox | Searchable |
| Date selection | Date picker | Prevent format errors |
| Short free text (1 line) | `<input type="text">` | |
| Long free text | `<textarea>` | Auto-resize with content if possible |
| Constrained number | Number input with +/- | Avoid raw `type="number"` on mobile |

### Form accessibility checklist

- Every input has a visible `<label>` (not just placeholder — placeholder disappears)
- Labels are connected via `htmlFor` / `id` pair (or wrapping)
- Required fields marked with `aria-required="true"` AND a visual indicator (not just `*`)
- Error messages connected to their field: `aria-describedby="field-error-id"`
- Success state communicated via `aria-live="polite"` region, not just visual color
- Autocomplete attributes on personal data fields: `autocomplete="email"`, `autocomplete="name"` etc.

```tsx
<div className="field-group">
  <label htmlFor="email" className="field-label">
    Email address <span aria-hidden="true" className="required-mark">*</span>
  </label>
  <input
    id="email"
    type="email"
    aria-required="true"
    aria-invalid={!!emailError}
    aria-describedby={emailError ? 'email-error' : 'email-hint'}
    autoComplete="email"
    className={cn('field-input', emailError && 'field-input--error')}
  />
  {emailError
    ? <p id="email-error" role="alert" className="field-error">{emailError}</p>
    : <p id="email-hint" className="field-hint">We'll never share your email</p>
  }
</div>
```

---

## Data display — tables, lists, and dashboards

### Data table visual hierarchy

Tables are dense information environments. Every visual decision should reduce cognitive load, not add decoration.

**Column alignment rules:**
- Text columns: left-aligned
- Numeric columns: right-aligned (so decimal points and digits align vertically)
- Status/badge columns: center-aligned
- Action columns (Edit, Delete): right-aligned, icons only with tooltips

**Row states:**
```css
tr { background: transparent; }
tr:hover { background: var(--color-bg-subtle); }
tr.selected { background: color-mix(in oklch, var(--color-accent) 8%, transparent); }
tr.loading { opacity: 0.5; pointer-events: none; }

/* Zebra striping — only for very dense tables (>10 columns) */
tr:nth-child(even) { background: var(--color-bg-subtle); }
/* For most tables, use row hover instead of zebra */
```

**Typography in tables:**
```css
th { font-size: 12px; font-weight: 500; letter-spacing: 0.04em; text-transform: uppercase; color: var(--color-text-secondary); }
td { font-size: 14px; font-variant-numeric: tabular-nums; }  /* always tabular nums for data */
```

**Sorting UI:**
```tsx
<th
  aria-sort={sortCol === 'name' ? sortDir : 'none'}
  onClick={() => handleSort('name')}
  className="cursor-pointer select-none"
>
  Name
  <SortIcon direction={sortCol === 'name' ? sortDir : null} aria-hidden="true" />
</th>
```

### Pagination vs infinite scroll — decision matrix

| Scenario | Pattern | Why |
|----------|---------|-----|
| User needs to return to a specific position | Pagination | URL-addressable pages; predictable |
| Feed / discovery browsing | Infinite scroll | Browsing doesn't need position |
| Search results | Pagination | Users compare and backtrack |
| Admin / data table | Pagination + "per page" selector | Power users need precision |
| Social timeline | Infinite scroll + "Load new" button | Avoids disorienting jumps |

**Never use infinite scroll for task-critical content** (invoices, records, search results) — users lose position and can't reference "page 3 item 2".

### Empty / loading / error states for data tables

```
Empty (no data yet):
  → Illustration + "No [records] yet" + primary CTA ("Add your first [record]")

Empty (filtered — no results):
  → "No results for '[search term]'" + "Clear filters" link

Loading:
  → Skeleton rows matching the expected data shape (not a full-page spinner)

Error:
  → "Couldn't load [records]" + retry button + error code for support
```

### Stat / metric cards (dashboard KPIs)

```tsx
// The anatomy of a metric card that communicates clearly
<div className="stat-card">
  <p className="stat-label">Monthly Revenue</p>          {/* small, secondary */}
  <p className="stat-value">$48,294</p>                  {/* large, primary, tabular-nums */}
  <p className="stat-delta positive">↑ 12.4% vs last month</p>  {/* trend, colored */}
</div>

// CSS:
// .stat-label:  font-size: 12px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.04em; color: var(--color-text-secondary);
// .stat-value:  font-size: 28–32px; font-weight: 600; font-variant-numeric: tabular-nums;
// .stat-delta:  font-size: 13px; color: green/red with semantic meaning (don't use for decoration)
```

**Data visualization color rules:**
- Use a maximum of 5 distinct hues in a chart before grouping becomes impossible
- Never rely on color alone to distinguish categories — use shape, pattern, or label too (accessibility)
- For sequential data (low→high): single-hue scale (light to dark)
- For diverging data (negative→positive): two-hue scale anchored at neutral gray/white
- Chart grid lines: extremely subtle — `rgba(0,0,0,0.06)` — they should disappear, not compete

---

## Navigation patterns — systematic coverage

### Pattern decision matrix

| Pattern | Use when | Avoid when |
|---------|----------|------------|
| **Top navigation** | ≤7 items, marketing/public site, broad audience | Deep hierarchy, complex tools |
| **Left sidebar** | 7–20 items, logged-in app, multiple sections | Mobile (collapse to drawer) |
| **Bottom navigation** | Mobile app, 3–5 top-level destinations | Desktop (too much vertical space used) |
| **Tabs** | Switching views within same page context | Site-level navigation |
| **Breadcrumbs** | 3+ levels of hierarchy, content/docs sites | Flat apps with no hierarchy |
| **Command palette** | Power users, dense apps (>50 actions possible) | Simple single-purpose apps |

### Current-page indicator — NEVER omit
```css
/* Active nav item must be visually distinct — not just bold */
.nav-item { color: var(--color-text-secondary); }
.nav-item[aria-current='page'] {
  color: var(--color-text-primary);
  background: var(--color-bg-subtle);
  /* Add: left border accent for sidebar, bottom border for tab nav */
}

/* Sidebar: left accent bar */
.sidebar-item[aria-current='page']::before {
  content: '';
  position: absolute; left: 0; top: 4px; bottom: 4px;
  width: 3px;
  background: var(--color-accent);
  border-radius: 0 2px 2px 0;
}
```

---

## Micro-copy & UX writing — the words are part of the design

Bad copy makes good UI feel broken. Every string in the interface is a design decision.

### Action label syntax

Always: **verb + noun** that describes the outcome, not the mechanism.

| Bad (generic) | Good (specific) | Why |
|--------------|----------------|-----|
| Submit | Save changes | Tells user what happens |
| Click here | View pricing | Describes destination |
| Yes / No | Delete account / Keep account | Removes ambiguity |
| Confirm | Send invoice | The real action |
| Update | Save profile | Domain-specific |
| OK | Got it / Done | Conversational, not robotic |

**Destructive action labels must name the thing being destroyed:**
- `Delete project` not `Delete`
- `Remove 3 members` not `Confirm`
- `Cancel subscription` not `Proceed`

### Confirmation dialog copy formula

```
[Title]:   [Verb] "[Name of thing]"?
           e.g. "Delete 'Q4 Marketing Campaign'?"

[Body]:    [Consequence] — [what cannot be undone].
           e.g. "This will permanently remove the campaign and all
                 its 47 assets. This action cannot be undone."

[Actions]: [Destructive button: red]  [Cancel button: secondary]
           "Delete campaign"           "Keep campaign"
```

Never use: "Are you sure?" — it adds no information. State the consequence instead.

### Empty state copy formula

```
[Illustration or icon — not generic "no data"]

[Title]:  What's missing (noun phrase)
          e.g. "No campaigns yet" / "Your inbox is empty"

[Body]:   Why it's empty + what to do (1 sentence max)
          e.g. "Create a campaign to start tracking performance."
          NOT: "There are currently no items to display."

[CTA]:    Primary action to fill it
          e.g. "Create your first campaign →"
```

**Filtered empty state** (no results for search/filter):
```
"No results for '[search term]'"
"Try a different search or [clear all filters]."
```

### Error message formula

```
[Icon: ✕ or ⚠]  [Plain-language problem]
                [Specific fix or next step]
                [Link to action if applicable]

Good:  "Email address is already in use.
        [Sign in instead →] or [reset your password →]"

Bad:   "Error: DUPLICATE_EMAIL_ADDRESS_CONSTRAINT_VIOLATION"

Good:  "Couldn't save — check your internet connection and try again."
Bad:   "An unexpected error occurred. Please try again later."

Good:  "Password must be at least 8 characters (currently 5)."
Bad:   "Password too short."
```

### Success & status message tone

- **Success**: confident, not excited. "Changes saved." not "Changes saved! 🎉"
- **Progress**: active verb in present tense. "Uploading 3 of 12 files…" not "Please wait"
- **Warning**: direct about the risk. "Free plan limit reached. Upgrade to continue." not "You're nearing your limit!"
- **Info**: actionable context. "Scheduled for Monday 9:00 AM" not "Note: see settings for more options"

### Tooltip copy rules

- Maximum 1 sentence. If it needs more, the UI design is at fault, not the tooltip.
- State what the element **does**, not what it **is**:
  - Good: "Archive this conversation (it won't be deleted)"
  - Bad: "Archive button"
- Never restate the button label as the tooltip: "Save" button tooltip should not be "Save".

### Placeholder text rules

- Write an example, not a label: `placeholder="e.g. growth@company.com"` not `"Email address"`
- Never use placeholder as the only label — it disappears when the user types
- Placeholder color must be `--color-text-tertiary` (40–50% opacity of body text)

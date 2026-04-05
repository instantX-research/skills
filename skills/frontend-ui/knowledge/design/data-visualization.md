# Data Visualization & Dashboard Design

**Scope:** Chart type selection, KPI card anatomy, dashboard layout patterns, and color rules specific to data. For general layout principles, see `design-principles.md`. For general component states (loading, empty, error), see `implementation/code-standards-extended.md` — this file covers the data-specific variants of those states.

Data visualization is the one domain where design aesthetics must subordinate to perceptual accuracy. A beautiful chart that misleads is worse than an ugly chart that communicates.

---

## Chart Type Decision Matrix

Choose chart type by the **relationship** the data expresses, not by aesthetic preference.

| Data relationship | Chart type | When to avoid |
|---|---|---|
| **Change over time** (1–3 series) | Line chart | Fewer than 5 data points — use a stat card instead |
| **Change over time** (many series, comparing) | Small multiples (faceted line charts) | More than 6 panels — switch to a table or filter |
| **Part-to-whole over time** (cumulative) | Stacked area chart | More than 4 series — too many stacks = unreadable |
| **Comparison across categories** | Vertical bar chart | More than 8 categories — switch to horizontal |
| **Comparison, long category labels** | Horizontal bar chart | Animating sort changes — disorienting |
| **Part-to-whole** (≤ 5 segments) | Donut chart | > 5 segments — use a bar chart instead |
| **Part-to-whole** (many segments) | Stacked bar chart | Comparing individual segments across groups |
| **Distribution** | Histogram | Ordinal data — use bar chart |
| **Correlation between two variables** | Scatter plot | When one variable is time — use line chart |
| **Ranking** | Ranked horizontal bar | Fewer than 3 items — use a stat card |
| **Progress toward a goal** | Progress bar or gauge | No clear maximum — progress bars need a 100% |
| **Geospatial data** | Choropleth / pin map | Data that doesn't vary geographically |
| **Flow / funnel** | Funnel chart | More than 6 stages |

### The chart you should almost never use

**Pie chart:** Humans are very bad at estimating arc angles. A donut chart is marginally better (the center hole removes the worst perceptual issue). If you must use one:
- Max 3 segments (ideally 2)
- Largest segment clockwise from 12 o'clock
- Never explode slices
- Label slices directly — don't use a legend that requires eye travel

**3D charts:** Never. 3D distorts proportions and adds zero information.

---

## KPI Card Anatomy

A KPI card answers one question: "How is this metric performing right now?"

```
┌──────────────────────────────┐
│ METRIC LABEL           ⋯    │  ← 11–12px, uppercase, muted — "MONTHLY REVENUE"
│                              │
│ $48,291                      │  ← 32–48px, 700 weight, tabular-nums
│                              │
│ ↑ 12.4%  vs. last month     │  ← trend line: color + icon + value + context
│ ▁▂▃▄▅▆▇ (sparkline)        │  ← optional, 40–48px tall, accent color
└──────────────────────────────┘
```

**Rules:**

**The number is the hero.** Everything else supports it.
- Primary value: 32–48px depending on card size. `font-variant-numeric: tabular-nums` always.
- Label: 11–12px, uppercase, `letter-spacing: 0.06em`, secondary color — not competing with the number
- Trend: ↑/↓ icon + percentage + comparison context ("vs. last month") — all three or skip trend entirely
- Trend colors: green for positive, red for negative — but check if "up" is actually good (e.g., error rate going up is bad despite positive trend)

**Sparkline rules:**
- Keep it simple: line only, no axes, no labels — it's a texture, not a chart
- Height: 40–48px, width fills card
- Color: accent or trend color
- Fills: subtle area fill below the line (opacity 0.1–0.15)

**Card sizing:** Min 200px wide, min 100px tall. Cards that are too small force font sizes below legibility thresholds.

**Grid of KPI cards:** 3–4 cards in a row for desktop, 2 for tablet, 1 for mobile. The top KPI row should always be the first thing visible on a dashboard.

---

## Dashboard Layout Patterns

### Pattern 1: KPI row + chart grid *(most common)*

```
┌────────┬────────┬────────┬────────┐  ← KPI row (4 cards)
│  KPI   │  KPI   │  KPI   │  KPI   │
└────────┴────────┴────────┴────────┘
┌─────────────────────┬──────────────┐  ← Chart grid
│   Main chart        │  Secondary   │
│   (line/bar)        │  chart       │
│   60% width         │  40% width   │
├──────────────────────┴─────────────┤
│   Data table (full width)          │
└────────────────────────────────────┘
```

**When to use:** Analytics dashboards, reporting tools, single-domain data

---

### Pattern 2: Sidebar filters + scrollable content

```
┌──────────┬──────────────────────────────┐
│          │  ┌──────┐┌──────┐┌──────┐   │
│ Filters  │  │ KPI  ││ KPI  ││ KPI  │   │
│          │  └──────┘└──────┘└──────┘   │
│ Date     │                              │
│ range    │  ┌──────────────────────┐    │
│          │  │    Main chart        │    │
│ Segment  │  └──────────────────────┘    │
│          │                              │
│ Group    │  ┌──────────────────────┐    │
│ by       │  │    Data table        │    │
│          │  └──────────────────────┘    │
└──────────┴──────────────────────────────┘
```

**When to use:** Exploratory analytics, multi-dimension data, user-driven filtering

**Sidebar width:** 240–280px. Never resizable in a first-pass — add resize handle only if truly needed.

---

### Pattern 3: Tab-separated views

```
  Overview | Acquisition | Engagement | Revenue | [+ Add]

  ┌─────────────────────────────────────────────┐
  │  Tab-specific KPIs and charts               │
  └─────────────────────────────────────────────┘
```

**When to use:** Multiple distinct data domains (e.g., Google Analytics-style), saved views per team

**Tab rules:**
- Max 5–6 tabs before switching to a dropdown or sidebar
- Active tab: accent underline or filled background — must be unambiguous
- Tab content should persist state when switching back (don't reset filters on tab change)

---

### Density modes

Dashboards often need a density toggle for power users vs. managers.

| Mode | Use | Spacing |
|---|---|---|
| **Compact** | Data-heavy operations tools, traders, operators | 8–12px card gap, 12–16px card padding |
| **Comfortable** (default) | General analytics dashboards | 16–24px card gap, 20–24px card padding |
| **Spacious** | Executive summaries, presentation mode | 24–32px card gap, 32–48px card padding |

Implement with a CSS class toggle on the dashboard root:
```css
.dashboard[data-density="compact"]    { --card-gap: 8px;  --card-pad: 12px; }
.dashboard[data-density="comfortable"]{ --card-gap: 16px; --card-pad: 20px; }
.dashboard[data-density="spacious"]   { --card-gap: 24px; --card-pad: 32px; }
```

---

## Color Rules in Data Visualization

Color in data viz follows different rules than UI color. The primary purpose is **encoding information**, not aesthetics.

### Categorical color palettes (series colors)

For distinguishing multiple data series:
- Max 5–6 distinct hues — beyond that, users cannot reliably distinguish
- Colors must be perceptually equidistant (same perceived brightness) — avoid pairing a vivid and a muted color at the same level
- **Never use the brand's accent color as one of several series colors** — it will look like a primary vs. secondary hierarchy rather than equal data series

**Accessible categorical palette (works for colorblind users):**
```
Blue:    #4C8EDA
Orange:  #E8892B
Green:   #4CAF6B
Red:     #E05252
Purple:  #9B6ECC
Teal:    #4CBCBC
```
These are distinguishable in deuteranopia (most common color blindness). Never rely on red/green alone.

### Sequential palettes (single-dimension intensity)

For choropleth maps, heatmaps, gradient-encoded data:
- Use a single hue, varying lightness (e.g., light blue → dark blue)
- Never use a rainbow (spectral) scale — it has no perceptual ordering and misleads

```css
/* Sequential 5-step scale */
--data-seq-1: oklch(90% 0.08 240);   /* light */
--data-seq-2: oklch(75% 0.12 240);
--data-seq-3: oklch(58% 0.16 240);   /* mid */
--data-seq-4: oklch(42% 0.18 240);
--data-seq-5: oklch(28% 0.18 240);   /* dark */
```

### Diverging palettes (data with a meaningful midpoint)

For data where the midpoint matters (sentiment, variance from target, above/below zero):
- Blue (negative/low) ← neutral gray → Red (positive/high)
- The neutral midpoint color matters — it should be the same perceived brightness as the extremes

### Semantic colors in data

These meanings are fixed — never repurpose:
- **Red** → bad, error, below target, decreasing (bad)
- **Green** → good, success, above target, increasing (good)
- **Yellow/orange** → warning, approaching threshold
- **Gray** → no data, null, inactive

Exception: if the product domain inverts these (e.g., a cost reduction dashboard where "red" means expenses went down = good), add an explicit legend label to prevent misreading.

---

## Axes, Gridlines, and Labels

### Axes
- Y-axis: always start at 0 for bar charts (truncated bars lie about magnitude)
- Y-axis: may start above 0 for line charts if the variance is the story (stock prices)
- Axis labels: 11–12px, muted color, never bold

### Gridlines
- Horizontal only (for bar/line charts) — vertical gridlines add noise
- Color: `rgba(0,0,0,0.06)` on light, `rgba(255,255,255,0.06)` on dark
- Fewer is better: 3–5 gridlines is usually sufficient

### Data labels
- On bar charts: label directly on or above each bar if ≤ 8 bars
- On line charts: label the endpoint of each line (avoids legend eye travel)
- Never auto-rotate labels — if category labels are long, use a horizontal bar chart instead

---

## Empty, Loading, and Error States for Data

### Loading state
```
┌──────────────────────────────┐
│ ░░░░░░░░░  (skeleton)        │  ← KPI value skeleton
│ ░░░░░░░░░░░░░░               │
│                              │
│ ▁▂▃░░░░░░░░░░░░░░░░░░        │  ← Chart skeleton (static shape)
└──────────────────────────────┘
```
- Skeleton should match the approximate shape of the loaded data — a line chart skeleton is a wavy line shape, not a rectangle
- Never use a spinner for chart loading — skeleton communicates "data is coming" more clearly

### Empty state
Two types: no data yet vs. filters returned no results.

**No data yet:**
```
  [simple illustration or icon]

  No data for this period yet

  Data appears as soon as your first [event] is recorded.
  [View documentation →]
```

**Filters returned nothing:**
```
  No results match your filters

  Try adjusting the date range or removing some filters.
  [Clear filters]
```
Never show the same empty state for both — they have different causes and different solutions.

### Error state
```
  [error icon]

  Couldn't load this chart

  There was a problem fetching your data.
  [Try again]   Last updated: 3 minutes ago
```
- Always show when data was last successfully loaded
- "Try again" triggers a re-fetch, not a full page reload

---

## Tooltip Design

Tooltips are the primary interaction in most charts. They must be fast, clear, and non-obstructive.

```
┌───────────────────────┐
│ March 15, 2025        │  ← context (date, category)
│                       │
│ ● Revenue    $12,450  │  ← series color dot + name + value
│ ● Sessions   8,291    │
│ ● Conversion 2.1%     │
└───────────────────────┘
```

**Rules:**
- Appear on hover with no delay (0ms) — any delay feels broken
- Position: follow cursor, avoid going offscreen (flip to opposite side at viewport edge)
- Values aligned right, labels aligned left (use `justify-content: space-between`)
- `font-variant-numeric: tabular-nums` on all values
- `background: var(--color-surface)` with `box-shadow: var(--shadow-md)` — the tooltip must float visually
- Max width: 220px — if content is wider, you're showing too much

---

## Responsive behavior for dashboards

Dashboards are primarily desktop experiences. Mobile should show a simplified view, not a scaled-down desktop.

| Breakpoint | Layout change |
|---|---|
| ≥ 1024px | Full dashboard: sidebar + multi-column chart grid |
| 768–1023px | No sidebar (collapse to top filter bar); 2-column chart grid |
| < 768px | Single column; KPI cards stack vertically; charts full-width; hide non-critical charts |

**Mobile dashboard rule:** Show the top 3 KPIs and the primary chart. Everything else behind a "View full report" link that opens a filtered view or navigates to desktop.

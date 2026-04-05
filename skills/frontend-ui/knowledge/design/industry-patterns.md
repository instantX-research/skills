# Industry-Specific Design Patterns

**When to use:** Load this file in Phase 3 Design Brief Synthesis. Apply the matching industry row's color, typography, effects, and avoid rules as overrides. If the user's product spans multiple industries, use the more specific row.

Each entry includes reference URLs for live inspection when more guidance is needed.

---

## Industry Pattern Reference

| Product Type | Color mood | Typography | Key effects | Avoid | Reference URLs |
|-------------|-----------|------------|-------------|-------|----------------|
| **SaaS / Dev Tool** | Cool neutral | Geometric sans + mono | Dot-grid bg, code highlight, kbd tags | Gradients on every card | https://linear.app · https://vercel.com · https://supabase.com |
| **FinTech** | Deep navy or warm dark + gold/green | Humanist sans or transitional serif | Number animation, status badges, data tables | Neon, playful illustrations | https://stripe.com · https://robinhood.com · https://avenia.io |
| **Healthcare** | White-dominant, clinical blue/green | Clear humanist sans | Large tap targets, progress indicators | Dark mode, aggressive color | — |
| **E-commerce** | Neutral bg (products pop) | Tight line-height, bold price | Hover zoom, cart micro-animation, trust badges | Bg competing with product photography | https://apple.com (hardware store) |
| **Luxury / Fashion** | Black/ivory/warm white | Transitional serif, generous spacing | Full-bleed photography, ultra-slow fades | Rounded corners, bright CTAs | https://a24films.com · https://www.lvmh.com |
| **B2B SaaS / Dashboard** | Light neutral `#f8fafc`, white cards | Inter/Geist, tabular numbers | Data charts, status dots, condensed tables | Cinematic animations, heavy hero | https://linear.app · https://base44.com |
| **Creative Portfolio** | Archetype-driven | Custom/licensed display font | Custom cursor, page transitions | Generic card grids, stock photos | https://robin-noguier.com · https://dennissnellenberg.com |
| **Personal Dev Site** | Monochrome or near-mono | Serif + mono, 42–65ch prose | `::selection` brand color, code blocks | Flashy hero, social proof sections | https://paco.me · https://brianlovin.com · https://ryo.lu |
| **Academic / Research Homepage** | Restrained off-white, stone, or institutional neutral + one muted accent | **Font rule:** DM Sans or Inter throughout (weight hierarchy only) is the default. If a serif is used, limit it to the researcher's name at large size only — use Lora or Source Serif 4, never Fraunces or other variable/optical-size display serifs (literary register, wrong for research). Mono only for metadata/citations. | Publication lists, student/alumni roster, talks/teaching blocks, paper/code links | Startup CTA stacks, pricing-card sections, aggressive gradients, display serifs on paper titles | https://www.sainingxie.com/ · https://kaiming.me/ |
| **Institutional / University / Government** | Institutional neutrals + one restrained brand color | Sober sans or institutional serif+sober sans pairing; dense nav stays readable | Utility nav, audience shortcuts, by-the-numbers band, research/news/program cards, directory/contact-heavy footer | App-style hero CTA stacks, startup slogans, hidden navigation, decorative gradients overwhelming content | https://www.berkeley.edu/ · https://www.mit.edu/ · https://www.stanford.edu/ |
| **Aggregation / Directory / Offer Hub** | Neutral base + one strong organizing accent | Crisp sans hierarchy; compact metadata and price/value labels scan instantly | Category chips, offer cards, partner logos, urgency labels, filters/sorting, comparison-friendly grids | Giant abstract hero art, sparse one-message layouts, inconsistent card anatomy | https://lennysproductpass.com/ |
| **AI / ML Platform** | Dark-first, electric blue or teal | Geometric sans + mono | Animated data streams, terminal aesthetics | Bubble chat UI, robot emoji, generic purple | https://lumalabs.ai/ · https://www.granola.ai/ · https://supabase.com |
| **Restaurant / Food** | Warm cream/terracotta or dark chalkboard | Organic humanist or slab serif | Full-bleed food photography, menu cards | Cold blue-gray, sterile feeling | — |
| **Chinese Consumer App (国内消费类App)** | High-saturation brand color (red/orange/blue) on white; bottom tab nav dominant | PingFang SC or HarmonyOS Sans; compact 12–14px body; bold numeric labels | Bottom navigation bar, WeChat mini-program style cards, red dot badges, swipe carousels, "限时" urgency labels | Western sidebar layout, low-density whitespace, serif body text | https://www.meituan.com/ · https://www.jd.com/ |
| **Chinese SaaS / Enterprise (国内B端SaaS)** | Neutral light bg `#f0f2f5`, white cards, blue `#1677ff` (Ant Design system) | PingFang SC / Noto Sans SC; tabular numbers; dense information hierarchy | Ant Design component patterns, side nav + content layout, data tables with row actions, form-heavy pages, ICP/beian footer | Dark mode by default, playful illustration, sparse layout | https://ant.design/ · https://pro.ant.design/ |
| **Chinese Content / Media (内容资讯类)** | White bg; accent red `#e62117` (Bilibili teal `#00AEEC`); thumbnail-grid dominant | PingFang SC; tight line-height 1.4; tag/category chips prominent | Video/article thumbnail grids, up-count and play-count labels, hot-topic tags, floating comment sidebar | Western magazine editorial layout, generous whitespace, serif | https://www.bilibili.com/ · https://36kr.com/ |

---

## Academic Homepage: Section Anatomy

For academic/research pages, the information architecture follows a predictable pattern. Use this as a scaffold:

1. **Header** — Name, title, institution, profile photo, contact/links
2. **Research interests** — 3–6 area tags or short phrases
3. **News / Updates** — Recent highlights, talks, media coverage
4. **Publications** — Year-grouped or ranked, with PDF/code/demo links
5. **Teaching** — Current and past courses with links
6. **Bio** — Short prose paragraph
7. **Footer** — Department link, lab link, email

Reference: https://www.sainingxie.com/ · https://kaiming.me/

---

## Institutional Homepage: Section Anatomy

For university, corporate root sites, and government portals, the information architecture serves multiple audiences simultaneously:

1. **Utility nav** — Quick links (Maps, Library, Events, Campus Life, Contact)
2. **Audience shortcuts** — Prospective students / Current students / Faculty / Alumni / Visitors / Press
3. **Hero** — Mission statement or institutional moment, photography-forward
4. **By-the-numbers band** — Facts/stats that establish institutional authority
5. **News + Research spotlights** — 3–4 cards, with date and category
6. **Programs / Schools / Departments** — Grid or list with quick links
7. **Events** — Upcoming calendar, filterable
8. **Footer** — Dense: address, legal, social, sub-site map

Reference: https://www.berkeley.edu/ · https://www.mit.edu/ · https://www.stanford.edu/ · https://www.cmu.edu/

---

## Aggregation / Offer Hub: Card Anatomy

Each card in a directory or offer hub should follow consistent anatomy for scanability:

- **Logo or brand mark** — top-left
- **Offer headline** — concise, value-forward
- **Category tag** — chips or badges
- **Value label** — price, discount %, or "Free"
- **Urgency indicator** — expiry date or limited availability (optional)
- **CTA** — "Claim" / "View" / "Learn More" (one action per card)

Reference: https://lennysproductpass.com/

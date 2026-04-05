# Premium Color Palette Library

**When to use:** Reference this library when the user has not specified a color direction, when Phase 3 archetype selection guides a palette choice, or when upgrading an existing UI's color system. Every palette below is production-validated and avoids AI-slop defaults.

Each entry lists: background → surface → text hierarchy → border → accent, with the matching archetype label for Phase 3 mapping.

## Color System: Restrained vs. Chromatic

This is the single canonical definition. All references in SKILL.md point here.

**Restrained (default):** One accent colour throughout. No gradients on cards, buttons, or interactive elements. Borders use `--border` token only. Hover states shift `opacity` or `border`, never hue. Applies to D1–D8 and L1–L8 palettes.

**Chromatic (opt-in):** Gradients and multi-accent permitted on hero sections and feature moments only. Interactive elements (buttons, inputs, links) remain single-colour. Requires explicit user signal: "colorful", "bold", "strong color", or "vivid". Applies to B1–B4 and S3 palettes.

**Trigger words that unlock Chromatic:** "colorful", "bold", "strong color", "vivid", "gradient", "expressive", "high contrast"

**Never Chromatic by default for:** Archetype A, B, E, G, I — these are definitionally restrained palettes.

---

## Archetype → Palette Quick Reference

Use this table in Phase 3 Step 3 to present only the relevant options for the locked archetype.

| Archetype | Palette options | Auto-resolve note |
|-----------|----------------|-------------------|
| A Obsidian Precision | D1 Linear Void · D4 Deep Cobalt · D7 Obsidian Pearl | Ask — dark warm/cool/neutral variants differ meaningfully |
| B Warm Editorial | L1 Parchment Warmth · L7 Zen Ink · L3 Cream Canvas · S2 Duotone Sepia · F1 Earth Craft · F2 Maroon Mood | Ask — temperature and mood vary; F1/F2 for artisan/boutique brands |
| C Chromatic Confidence | B1 Stripe Oxide · B2 Framer Noir · B3 Prismatic Dusk · B4 High Noon · F3 Power Purple · S3 Neon Brutalist | All require explicit opt-in; auto-select B1 if no preference |
| D Terminal Glass | D3 Ember Obsidian · D2 Terminal Jade · D5 Volcanic Amber · D8 Steel Teal · S1 Glassmorphic Night | Ask; D5 for dramatic/luxury dark, D8 for data/monitoring |
| E Luxury Silence | L2 Arctic Restraint · L8 Bone Linen · L4 Mist Sage | Ask — cool/warm/natural |
| F Soft Structuralism | L5 Slate Cloud · L6 Ivory Coral · D6 Cosmic Violet | Ask |
| G Museum Authority | L7 Zen Ink · L1 Parchment Warmth · L8 Bone Linen | Usually auto-resolve to L7 |
| H Cinematic Portfolio | D7 Obsidian Pearl · L8 Bone Linen · B2 Framer Noir | Ask |
| I Developer Personal | L7 Zen Ink · L2 Arctic Restraint · D1 Linear Void | Usually auto-resolve to L7 or L2 |

---

#### ── DARK PRECISION PALETTES ──────────────────────────────

**D1 · Linear Void** `[Obsidian Precision]`
Personality: precise · minimal · tool-grade
```css
--color-bg:              #08090a;   /* near-black, not pure black */
--color-bg-subtle:       #0f1011;
--color-surface:         #131416;
--color-surface-raised:  #1a1b1e;
--color-text-primary:    #e8e8e8;
--color-text-secondary:  #8a8a92;
--color-text-tertiary:   #52525b;
--color-border:          rgba(255,255,255,0.06);
--color-border-strong:   rgba(255,255,255,0.12);
--color-accent:          #5e6ad2;   /* desaturated indigo — never pure blue */
--color-accent-hover:    #6c78db;
--color-success:         #2da44e;
--color-warning:         #9a6700;
--color-error:           #cf4a4a;
```
Best for: productivity apps, developer tools, kanban/project management

**D2 · Terminal Jade** `[Terminal Glass]`
Personality: technical · alive · underground
```css
--color-bg:              #0d0d0d;
--color-bg-subtle:       #111111;
--color-surface:         #161616;   /* distinguishable without being gray */
--color-surface-raised:  #1e1e1e;
--color-text-primary:    #e6ffe6;   /* green-tinted white — subliminal terminal feel */
--color-text-secondary:  #7a9e7e;
--color-text-tertiary:   #4a6a4e;
--color-border:          rgba(0,208,132,0.08);
--color-border-strong:   rgba(0,208,132,0.18);
--color-accent:          #00d084;   /* jade — Supabase palette */
--color-accent-hover:    #00e891;
--color-success:         #00d084;
--color-warning:         #f5a623;
--color-error:           #ff5757;
```
Best for: databases, CLIs, developer platforms, infrastructure tools

**D3 · Ember Obsidian** `[Terminal Glass]`
Personality: warm dark · energetic · bold
```css
--color-bg:              #0f0e0d;   /* warm near-black — amber undertone */
--color-bg-subtle:       #141210;
--color-surface:         #1a1714;
--color-surface-raised:  #221e1a;
--color-text-primary:    #f5ede4;   /* warm white */
--color-text-secondary:  #9c8a7a;
--color-text-tertiary:   #6b5b4e;
--color-border:          rgba(232,92,44,0.10);
--color-border-strong:   rgba(232,92,44,0.20);
--color-accent:          #e85c2c;   /* ember orange — Raycast-style */
--color-accent-hover:    #f06a38;
--color-success:         #65c97a;
--color-warning:         #f0a500;
--color-error:           #e84444;
```
Best for: launcher apps, command palettes, macOS-native style tools

**D4 · Deep Cobalt** `[Obsidian Precision]`
Personality: corporate dark · trustworthy · structured
```css
--color-bg:              #080c14;   /* dark navy — not gray-black */
--color-bg-subtle:       #0d1320;
--color-surface:         #111827;
--color-surface-raised:  #1a2333;
--color-text-primary:    #e2e8f4;   /* cool white */
--color-text-secondary:  #8494b0;
--color-text-tertiary:   #4e5d7a;
--color-border:          rgba(59,130,246,0.10);
--color-border-strong:   rgba(59,130,246,0.20);
--color-accent:          #3b82f6;   /* calibrated blue — NOT Tailwind default weight */
--color-accent-hover:    #2563eb;
--color-success:         #10b981;
--color-warning:         #f59e0b;
--color-error:           #ef4444;
```
Best for: B2B SaaS, fintech dashboards, analytics platforms

**D5 · Volcanic Amber** `[Terminal Glass]`
Personality: dramatic · luxurious dark · editorial tech
```css
--color-bg:              #111008;   /* warm dark — amber blood in black veins */
--color-bg-subtle:       #17140c;
--color-surface:         #1e1a10;
--color-surface-raised:  #28240f;
--color-text-primary:    #f7edd8;   /* warm ivory */
--color-text-secondary:  #a08c60;
--color-text-tertiary:   #6b5c3a;
--color-border:          rgba(245,158,11,0.12);
--color-border-strong:   rgba(245,158,11,0.22);
--color-accent:          #f59e0b;   /* amber gold */
--color-accent-hover:    #fbbf24;
--color-success:         #4ade80;
--color-warning:         #f59e0b;
--color-error:           #f87171;
```
Best for: premium SaaS, luxury consumer apps, editorial tech platforms

**D6 · Cosmic Violet** `[Soft Structuralism]`
Personality: ethereal · immersive · dreamlike dark
```css
--color-bg:              #0a0812;   /* near-black with purple undertone */
--color-bg-subtle:       #100e1a;
--color-surface:         #161322;
--color-surface-raised:  #1e1a2e;
--color-text-primary:    #ede8ff;   /* lavender-tinted white */
--color-text-secondary:  #8b80b0;
--color-text-tertiary:   #5a5070;
--color-border:          rgba(167,139,250,0.10);
--color-border-strong:   rgba(167,139,250,0.20);
--color-accent:          #a78bfa;   /* soft violet — desaturated enough to feel premium */
--color-accent-hover:    #b89cf8;
--color-success:         #34d399;
--color-warning:         #fbbf24;
--color-error:           #f87171;
```
Best for: AI products, creative tools, music/media apps, crypto platforms

**D7 · Obsidian Pearl** `[Obsidian Precision]`
Personality: near-monochrome · architectural · Resend-style
```css
--color-bg:              #131316;
--color-bg-subtle:       #18181c;
--color-surface:         #1e1e22;
--color-surface-raised:  #26262b;
--color-text-primary:    #ededef;
--color-text-secondary:  #8c8c96;
--color-text-tertiary:   #5c5c66;
--color-border:          rgba(255,255,255,0.07);
--color-border-strong:   rgba(255,255,255,0.13);
--color-accent:          #e2e2e6;   /* near-white accent — monochromatic play */
--color-accent-hover:    #ffffff;
--color-success:         #4ade80;
--color-warning:         #facc15;
--color-error:           #f87171;
```
Best for: email tools, monochrome brand products, developer-focused minimal apps

**D8 · Steel Teal** `[Terminal Glass]`
Personality: cold precision · data-focused · industrial
```css
--color-bg:              #0c1218;   /* dark navy-charcoal */
--color-bg-subtle:       #101a22;
--color-surface:         #152230;
--color-surface-raised:  #1c2d3e;
--color-text-primary:    #e0f2f1;   /* teal-tinted white */
--color-text-secondary:  #7ab0aa;
--color-text-tertiary:   #4a7570;
--color-border:          rgba(45,212,191,0.10);
--color-border-strong:   rgba(45,212,191,0.20);
--color-accent:          #2dd4bf;   /* teal — distinct from green and blue */
--color-accent-hover:    #14b8a6;
--color-success:         #2dd4bf;
--color-warning:         #f59e0b;
--color-error:           #f87171;
```
Best for: data visualization tools, monitoring dashboards, fintech dark mode

---

#### ── LIGHT EDITORIAL PALETTES ─────────────────────────────

**L1 · Parchment Warmth** `[Warm Editorial]`
Personality: human · written · craft-focused
```css
--color-bg:              #f8f4ed;   /* Anthropic signature cream */
--color-bg-subtle:       #f2ede4;
--color-surface:         #ffffff;
--color-surface-raised:  #faf7f2;
--color-text-primary:    #1c1309;   /* warm near-black */
--color-text-secondary:  #6b5c44;
--color-text-tertiary:   #9e8c76;
--color-border:          rgba(92,64,16,0.12);
--color-border-strong:   rgba(92,64,16,0.22);
--color-accent:          #cc5500;   /* burnt orange — warm authority */
--color-accent-hover:    #b84a00;
--color-success:         #2d6a4f;
--color-warning:         #9a6700;
--color-error:           #c0392b;
```
Best for: writing tools, documentation, AI products, editorial platforms

**L2 · Arctic Restraint** `[Luxury Silence]`
Personality: clean · restrained · Apple-adjacent
```css
--color-bg:              #f5f5f7;   /* Apple's warm light gray */
--color-bg-subtle:       #ebebed;
--color-surface:         #ffffff;
--color-surface-raised:  #f9f9fb;
--color-text-primary:    #1d1d1f;   /* Apple's near-black */
--color-text-secondary:  #6e6e73;
--color-text-tertiary:   #aeaeb2;
--color-border:          rgba(0,0,0,0.10);
--color-border-strong:   rgba(0,0,0,0.18);
--color-accent:          #0071e3;   /* Apple blue */
--color-accent-hover:    #0077ed;
--color-success:         #34c759;
--color-warning:         #ff9f0a;
--color-error:           #ff3b30;
```
Best for: consumer apps, hardware products, premium landing pages

**L3 · Cream Canvas** `[Warm Editorial]`
Personality: warm minimal · readable · cozy product
```css
--color-bg:              #fffbf5;   /* softer than pure white, warmer than parchment */
--color-bg-subtle:       #faf5ec;
--color-surface:         #ffffff;
--color-surface-raised:  #fdf9f3;
--color-text-primary:    #18120a;
--color-text-secondary:  #6b5d4a;
--color-text-tertiary:   #a09080;
--color-border:          rgba(60,40,10,0.10);
--color-border-strong:   rgba(60,40,10,0.18);
--color-accent:          #6366f1;   /* indigo pop against warm bg — unexpected contrast */
--color-accent-hover:    #4f52dc;
--color-success:         #16a34a;
--color-warning:         #b45309;
--color-error:           #dc2626;
```
Best for: note-taking apps, journaling tools, reading apps

**L4 · Mist Sage** `[Warm Editorial · Luxury Silence]`
Personality: calm · organic · wellness-adjacent
```css
--color-bg:              #f3f5f0;   /* green-tinted off-white */
--color-bg-subtle:       #eaede6;
--color-surface:         #ffffff;
--color-surface-raised:  #f7f8f5;
--color-text-primary:    #1a2218;   /* near-black with forest undertone */
--color-text-secondary:  #5a7055;
--color-text-tertiary:   #8aaa85;
--color-border:          rgba(61,107,79,0.12);
--color-border-strong:   rgba(61,107,79,0.22);
--color-accent:          #3d6b4f;   /* deep sage — understated authority */
--color-accent-hover:    #2e5940;
--color-success:         #3d6b4f;
--color-warning:         #92400e;
--color-error:           #991b1b;
```
Best for: sustainability products, health/wellness apps, outdoor brands

**L5 · Slate Cloud** `[Soft Structuralism · Obsidian Precision light variant]`
Personality: crisp · enterprise · trusted
```css
--color-bg:              #f8fafc;   /* Tailwind slate-50 — but use it intentionally */
--color-bg-subtle:       #f1f5f9;
--color-surface:         #ffffff;
--color-surface-raised:  #f8fafc;
--color-text-primary:    #0f172a;   /* slate-900 */
--color-text-secondary:  #475569;
--color-text-tertiary:   #94a3b8;
--color-border:          #e2e8f0;   /* solid — not rgba for light mode */
--color-border-strong:   #cbd5e1;
--color-accent:          #4f46e5;   /* indigo-600 — not default blue */
--color-accent-hover:    #4338ca;
--color-success:         #059669;
--color-warning:         #d97706;
--color-error:           #dc2626;
```
Best for: B2B SaaS light mode, admin panels, enterprise dashboards

**L6 · Ivory Coral** `[Soft Structuralism]`
Personality: warm modern · inviting · brand-forward
```css
--color-bg:              #fdf8f5;   /* warm ivory — between white and cream */
--color-bg-subtle:       #f9f1eb;
--color-surface:         #ffffff;
--color-surface-raised:  #fef9f7;
--color-text-primary:    #1c120e;   /* warm dark brown-black */
--color-text-secondary:  #7a5245;
--color-text-tertiary:   #b08880;
--color-border:          rgba(232,115,90,0.14);
--color-border-strong:   rgba(232,115,90,0.26);
--color-accent:          #e8735a;   /* salmon-coral — warm and energetic */
--color-accent-hover:    #d4604a;
--color-success:         #2e7d52;
--color-warning:         #b45309;
--color-error:           #c0392b;
```
Best for: e-commerce, food/lifestyle brands, consumer startups

**L7 · Zen Ink** `[Warm Editorial]`
Personality: Notion-style · thoughtful · information-dense
```css
--color-bg:              #f9f9f7;   /* warm barely-off-white */
--color-bg-subtle:       #f3f3f0;
--color-surface:         #ffffff;
--color-surface-raised:  #f7f7f5;
--color-text-primary:    #37352f;   /* Notion's signature warm near-black */
--color-text-secondary:  #787672;
--color-text-tertiary:   #b2b1ad;
--color-border:          rgba(55,53,47,0.09);
--color-border-strong:   rgba(55,53,47,0.16);
--color-accent:          #2eaadc;   /* Notion blue — muted, not electric */
--color-accent-hover:    #2596c4;
--color-success:         #0f7b6c;
--color-warning:         #dfab01;
--color-error:           #e03e3e;
```
Best for: wikis, knowledge bases, document editors, content management

**L8 · Bone Linen** `[Luxury Silence]`
Personality: literary · stripped · archival luxury
```css
--color-bg:              #f7f4f0;   /* bone — warmer than parchment */
--color-bg-subtle:       #f0ece7;
--color-surface:         #fdfaf7;
--color-surface-raised:  #f3efe9;
--color-text-primary:    #2c2019;   /* deep warm brown-black */
--color-text-secondary:  #7a6555;
--color-text-tertiary:   #b0a090;
--color-border:          rgba(90,60,30,0.12);
--color-border-strong:   rgba(90,60,30,0.20);
--color-accent:          #8b4513;   /* saddle brown — authoritative, literary */
--color-accent-hover:    #6f360f;
--color-success:         #3a5c3a;
--color-warning:         #8b6914;
--color-error:           #8b2020;
```
Best for: publishing platforms, legal/financial tools, premium editorial blogs

---

#### ── BOLD STATEMENT PALETTES ──────────────────────────────

**B1 · Stripe Oxide** `[Chromatic Confidence]`
Personality: enterprise bold · authoritative · premium SaaS
```css
--color-bg:              #0a2540;   /* Stripe's deep navy */
--color-bg-subtle:       #0d2e4e;
--color-surface:         #0f3460;
--color-surface-raised:  #163d6e;
--color-text-primary:    #ffffff;
--color-text-secondary:  #8ba0b8;
--color-text-tertiary:   #5a7090;
--color-border:          rgba(255,255,255,0.10);
--color-border-strong:   rgba(255,255,255,0.20);
--color-accent:          #635bff;   /* Stripe's warm purple — NOT cool blue */
--color-accent-hover:    #7b74ff;
--color-success:         #24c278;
--color-warning:         #f8c44a;
--color-error:           #ff6b6b;
```
Best for: payment platforms, fintech, API infrastructure, enterprise SaaS

**B2 · Framer Noir** `[Chromatic Confidence]`
Personality: designer-grade · electric · head-turning
```css
--color-bg:              #0c0c0c;   /* almost pure black — bold statement */
--color-bg-subtle:       #111111;
--color-surface:         #161616;
--color-surface-raised:  #1e1e1e;
--color-text-primary:    #f0f0f0;
--color-text-secondary:  #888888;
--color-text-tertiary:   #555555;
--color-border:          rgba(255,255,255,0.06);
--color-border-strong:   rgba(255,255,255,0.14);
--color-accent:          #ff4444;   /* pure-force red — used surgically */
--color-accent-secondary: #ff9900; /* gradient partner for hero moments only */
--color-accent-hover:    #ff2222;
--color-success:         #39d353;
--color-warning:         #ff9900;
--color-error:           #ff4444;
```
Usage note: `--color-accent-secondary` only for hero gradients. Never on interactive elements.
Best for: design tools, creative portfolios, agency sites, motion studios

**B3 · Prismatic Dusk** `[Chromatic Confidence]`
Personality: immersive · futuristic · generative-AI era
```css
--color-bg:              #1a0a2e;   /* deep purple-black */
--color-bg-subtle:       #20102e;
--color-surface:         rgba(30,15,50,0.90);  /* semi-transparent for glass */
--color-surface-raised:  rgba(44,22,70,0.80);
--color-text-primary:    #f0e8ff;   /* ultra-light lavender */
--color-text-secondary:  #9580c0;
--color-text-tertiary:   #6050a0;
--color-border:          rgba(180,100,255,0.12);
--color-border-strong:   rgba(180,100,255,0.25);
--color-accent:          #b464ff;   /* vivid purple — electric, not pastel */
--color-accent-hover:    #c478ff;
--color-gradient-hero:   linear-gradient(135deg, #b464ff 0%, #4488ff 50%, #00d4ff 100%);
--color-success:         #00e5a0;
--color-warning:         #ffcc44;
--color-error:           #ff4477;
```
Best for: AI products, generative art tools, crypto/web3, futuristic SaaS

**B4 · High Noon** `[Chromatic Confidence]`
Personality: bold · Mediterranean warmth · energetic
```css
--color-bg:              #f0ebe0;   /* warm natural linen */
--color-bg-subtle:       #e8e0d0;
--color-surface:         #faf6ee;
--color-surface-raised:  #ffffff;
--color-text-primary:    #1a1008;   /* warm deep black */
--color-text-secondary:  #6b5030;
--color-text-tertiary:   #a08060;
--color-border:          rgba(180,80,0,0.12);
--color-border-strong:   rgba(180,80,0,0.24);
--color-accent:          #ff4500;   /* fire red-orange — assertive, Mediterranean */
--color-accent-hover:    #e03d00;
--color-success:         #2d7a40;
--color-warning:         #c87000;
--color-error:           #c0200a;
```
Best for: food/restaurant brands, travel, bold marketing pages, summer campaigns

---

#### ── SPECIAL TECHNIQUE PALETTES ──────────────────────────

**S1 · Glassmorphic Night** `[Terminal Glass]`
For UI built primarily with glass morphism. All surfaces use backdrop-filter.
```css
/* Base (set on body/root — usually a gradient or image bg) */
--color-bg-base:         linear-gradient(135deg, #0a0a1a 0%, #0d1a2e 50%, #0a120a 100%);
--color-glass-light:     rgba(255,255,255,0.05);
--color-glass-medium:    rgba(255,255,255,0.10);
--color-glass-strong:    rgba(255,255,255,0.18);
--color-glass-border:    rgba(255,255,255,0.12);
--color-glass-border-strong: rgba(255,255,255,0.22);
--color-text-primary:    #f0f0ff;
--color-text-secondary:  #8888aa;
--color-accent:          #4499ff;
--color-accent-glow:     rgba(68,153,255,0.30);  /* for glow effects on accent */
/* Glass recipe: background: var(--color-glass-medium); backdrop-filter: blur(20px) saturate(180%); border: 1px solid var(--color-glass-border); */
```

**S2 · Duotone Sepia** `[Warm Editorial]`
Single brand color expressed through sepia-tinted monochrome system.
```css
--color-bg:              #faf7f2;
--color-bg-subtle:       #f4efe6;
--color-surface:         #ffffff;
--color-surface-raised:  #f8f4ee;
--color-text-primary:    #2d2418;
--color-text-secondary:  #7a6450;
--color-text-tertiary:   #b8a898;
--color-border:          #e0d5c5;
--color-border-strong:   #c8b8a4;
--color-accent:          #7c5c3c;   /* medium saddle brown — the ONE allowed color */
--color-accent-hover:    #634a30;
/* Rule: absolutely NO other hues. Even success/error use sepia tints */
--color-success:         #5c7a50;   /* muted olive-green, not pure green */
--color-warning:         #9a7030;
--color-error:           #8a3a3a;   /* desaturated red */
```

**S3 · Neon Brutalist** `[Terminal Glass]` (maximum contrast, anti-establishment)
```css
--color-bg:              #000000;   /* pure black — this IS the bold statement */
--color-bg-subtle:       #0a0a0a;
--color-surface:         #111111;
--color-surface-raised:  #1a1a1a;
--color-text-primary:    #ffffff;   /* pure white — intentional maximalism */
--color-text-secondary:  #888888;
--color-text-tertiary:   #444444;
--color-border:          #333333;   /* solid, not rgba */
--color-border-strong:   #555555;
--color-accent:          #00ff88;   /* neon green — used as a weapon */
--color-accent-hover:    #00e07a;
--color-accent-alt:      #ff0066;   /* secondary neon — for structural highlights only */
/* Rule: brutalist means borders ARE the design. No shadows. No radius. */
--radius-sm: 0px;  --radius-md: 0px;  --radius-lg: 0px;
```
Best for: hacker tools, underground projects, punk aesthetic brands, art experiments

---

#### ── FRAMER EDITORIAL PALETTES ────────────────────────────

**F1 · Earth Craft** `[Warm Editorial]`
Personality: organic · grounded · artisan warmth
```css
--color-bg:              #f8f3ec;   /* warm parchment — almost linen */
--color-bg-subtle:       #f0e9dd;
--color-surface:         #ffffff;
--color-surface-raised:  #faf6f1;
--color-text-primary:    #8d6959;   /* acorn brown replaces black — critical */
--color-text-secondary:  #a8896e;
--color-text-tertiary:   #c4aa94;
--color-border:          rgba(141,105,89,0.14);
--color-border-strong:   rgba(141,105,89,0.24);
--color-accent:          #e1937d;   /* terra cotta — warm, approachable CTA */
--color-accent-hover:    #d07e67;
--color-accent-secondary: #8e9867; /* olive — secondary actions only */
--color-success:         #8e9867;
--color-warning:         #c4912a;
--color-error:           #b85c4a;
```
Key rule: brown replaces black for body copy — never use #000 or #111 here.
Best for: artisan brands, sustainability products, food/wellness, handcraft studios

**F2 · Maroon Mood** `[Warm Editorial]`
Personality: intimate · composed · quietly luxurious
```css
--color-bg:              #f8f5f5;   /* pale rose — barely-there tint */
--color-bg-subtle:       #f1ebeb;
--color-surface:         #ffffff;
--color-surface-raised:  #faf7f7;
--color-text-primary:    #262626;   /* soft black — not pure */
--color-text-secondary:  #575757;   /* sophisticated gray */
--color-text-tertiary:   #8a8a8a;
--color-border:          rgba(122,59,59,0.10);
--color-border-strong:   rgba(122,59,59,0.20);
--color-accent:          #7a3b3b;   /* deep maroon — warmth not urgency */
--color-accent-hover:    #682f2f;
--color-success:         #4a7a5a;
--color-warning:         #8a6a2a;
--color-error:           #7a3b3b;   /* accent doubles as error — intentional */
```
Key rule: maroon reframes red's energy as comfort, not urgency. Never use true red here.
Best for: boutique hospitality, premium editorial, literary brands, intimate SaaS

**F3 · Power Purple** `[Chromatic Confidence]`
Personality: bold restraint · regal warmth · colorful yet controlled
```css
--color-bg:              #ebe7e0;   /* warm off-white — not pure white */
--color-bg-subtle:       #e0dbd3;
--color-surface:         #f5f2ed;
--color-surface-raised:  #ffffff;
--color-text-primary:    #312335;   /* aubergine replaces black — signature move */
--color-text-secondary:  #5b4060;
--color-text-tertiary:   #8a7090;
--color-border:          rgba(91,38,85,0.12);
--color-border-strong:   rgba(91,38,85,0.22);
--color-accent:          #5b2655;   /* royal purple — deep, not pastel */
--color-accent-hover:    #4a1e44;
--color-accent-gradient: linear-gradient(135deg, #5b2655 0%, #312335 100%);
--color-success:         #3d6b4f;
--color-warning:         #8b6914;
--color-error:           #8b2a2a;
```
Key rule: aubergine as the "black" for display type creates color interest without loudness.
Best for: beauty/fashion, creative agencies, premium lifestyle apps, luxury events

---

#### ── HOW TO SELECT A PALETTE ─────────────────────────────

**Decision matrix — match palette to context:**

| Signal in request | Recommend |
|-------------------|-----------|
| "productivity", "tool", "dashboard" (dark) | D1 Linear Void or D4 Deep Cobalt |
| "terminal", "CLI", "database", "code" | D2 Terminal Jade or D8 Steel Teal |
| "creative tool", "launcher", "desktop app" | D3 Ember Obsidian |
| "AI product", "generative", "future" | D6 Cosmic Violet or B3 Prismatic Dusk |
| "writing", "docs", "editorial", "AI assistant" | L1 Parchment Warmth or L7 Zen Ink |
| "Apple-like", "minimal", "consumer app" | L2 Arctic Restraint |
| "B2B", "enterprise", "admin panel" (light) | L5 Slate Cloud |
| "wellness", "sustainability", "nature" | L4 Mist Sage |
| "e-commerce", "lifestyle", "warm brand" | L6 Ivory Coral |
| "fintech", "payment", "API platform" | B1 Stripe Oxide |
| "design tool", "creative portfolio" | B2 Framer Noir |
| "luxury", "fashion", "premium" | L8 Bone Linen or L2 Arctic Restraint |
| "food", "restaurant", "travel", "bold" | B4 High Noon |
| "dark monochrome", "minimal SaaS" | D7 Obsidian Pearl |
| "glassmorphism", "layered bg" | S1 Glassmorphic Night |
| "single-hue editorial" | S2 Duotone Sepia |
| "artisan", "handcraft", "organic brand" | F1 Earth Craft |
| "boutique", "intimate", "literary luxury" | F2 Maroon Mood |
| "beauty", "fashion", "creative agency" | F3 Power Purple |

**Never mix palettes** — pick one and derive all values from it. The only cross-palette operation allowed is taking an accent color from one palette and applying it to the neutral base of another.

**Temperature rule:** Warm bg + cool accent = high energy tension (L3, B4). Cool bg + warm accent = grounded drama (D3, D5). Matched temperature = serene, intentional (L1, D1).

**Replace-black rule (Framer principle):** In warm and editorial palettes, never use `#000000` or `#111111` for body text. Use the darkest shade of the dominant hue instead:
- Warm palettes: dark brown (`#8d6959`, `#2c2019`)
- Purple palettes: aubergine (`#312335`)
- Blue palettes: deep navy (`#0a2540`, `#0f172a`)
This makes the entire design feel tonally unified rather than color-on-black.

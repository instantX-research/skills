# Advanced Visual Effects

**When to use:** Load this file when implementing premium visual polish — spotlight borders, variable font animations, grain overlays, glassmorphism. These are high-impact upgrade techniques from production-quality design systems.

---

## Spotlight / cursor-reactive border

Cards that illuminate where the cursor hovers — the most striking single upgrade for dark-theme card grids.

```jsx
// Track mouse position and apply to CSS custom property
useEffect(() => {
  const card = cardRef.current;
  const handleMouseMove = (e) => {
    const rect = card.getBoundingClientRect();
    card.style.setProperty('--mouse-x', `${e.clientX - rect.left}px`);
    card.style.setProperty('--mouse-y', `${e.clientY - rect.top}px`);
  };
  card.addEventListener('mousemove', handleMouseMove);
  return () => card.removeEventListener('mousemove', handleMouseMove);
}, []);
```

```css
.card {
  position: relative;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  overflow: hidden;
}

.card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(
    600px circle at var(--mouse-x, 50%) var(--mouse-y, 50%),
    rgba(255,255,255,0.06),
    transparent 40%
  );
  border-radius: inherit;
  opacity: 0;
  transition: opacity 300ms ease;
  pointer-events: none;
}

.card:hover::before { opacity: 1; }
```

---

## Variable font animation

Animate font weight or width on scroll or hover — works only with variable fonts (Geist, Outfit, Cabinet Grotesk support this).

```css
/* Weight animation on hover */
.heading {
  font-variation-settings: 'wght' 400;
  transition: font-variation-settings 400ms cubic-bezier(0.34, 1.56, 0.64, 1);
}
.heading:hover {
  font-variation-settings: 'wght' 700;
}

/* Width animation on scroll (with IntersectionObserver) */
.hero-title {
  font-variation-settings: 'wdth' 75, 'wght' 300;
  transition: font-variation-settings 600ms cubic-bezier(0.16, 1, 0.3, 1);
}
.hero-title.in-view {
  font-variation-settings: 'wdth' 125, 'wght' 700;
}
```

---

## Outlined-to-fill text transition

Dramatic text reveal: outline strokes fill in as the element enters view.

```css
.outlined-text {
  -webkit-text-stroke: 1px currentColor;
  color: transparent;
  background-clip: text;
  -webkit-background-clip: text;
  background-image: linear-gradient(currentColor, currentColor);
  background-size: 0% 100%;
  background-repeat: no-repeat;
  transition: background-size 800ms cubic-bezier(0.16, 1, 0.3, 1);
}
.outlined-text.in-view {
  background-size: 100% 100%;
  color: currentColor;
  -webkit-text-stroke: 0;
}
```

---

## True glassmorphism

Correct glassmorphism = layered depth cues, not just blur. Three required layers:

```css
.glass {
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(20px) saturate(1.4);
  -webkit-backdrop-filter: blur(20px) saturate(1.4);

  /* 1px inner border — the defining detail */
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.12),   /* top inner highlight */
    inset 0 -1px 0 rgba(0, 0, 0, 0.08),          /* bottom inner shadow */
    0 8px 32px rgba(0, 0, 0, 0.24);              /* outer depth shadow */

  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
}
```

**Performance rule:** `backdrop-filter` triggers GPU compositing. Wrap in a Client Component and isolate from the main layout tree. Never apply to more than 3 elements per viewport.

---

## Grain / noise overlay

Adds tactile texture to flat backgrounds. Eliminates the "digital sterility" of pure solid colors.

```jsx
// SVG noise filter — apply once to the DOM root or a wrapper
const GrainOverlay = () => (
  <svg style={{ position: 'fixed', top: 0, left: 0, width: 0, height: 0 }}>
    <defs>
      <filter id="grain">
        <feTurbulence
          type="fractalNoise"
          baseFrequency="0.65"
          numOctaves="3"
          stitchTiles="stitch"
        />
        <feColorMatrix type="saturate" values="0" />
      </filter>
    </defs>
  </svg>
);
```

```css
/* Apply the grain as a pseudo-element — never on actual content layers */
.section::after {
  content: '';
  position: absolute;
  inset: 0;
  filter: url(#grain);
  opacity: 0.035;   /* 0.02–0.05 is the working range; above 0.06 looks dirty */
  pointer-events: none;
  z-index: 1;
}
```

**Dark theme:** `opacity: 0.04–0.06`
**Light theme:** `opacity: 0.02–0.035`

---

## Colored / tinted shadows

Replace flat neutral shadows with hue-matched shadows that feel more premium.

```css
/* Accent-tinted shadow — use on CTAs and highlighted cards */
.card-accent {
  box-shadow:
    0 4px 24px rgba(37, 99, 235, 0.20),   /* blue accent tint */
    0 1px 4px rgba(37, 99, 235, 0.08);
}

/* Warm shadow for editorial / light contexts */
.card-warm {
  box-shadow:
    0 8px 32px rgba(120, 80, 40, 0.12),
    0 2px 8px rgba(120, 80, 40, 0.06);
}

/* Rule: shadow hue matches the surface color, never defaults to pure black */
```

---

## Parallax card stack

Layered cards that separate on scroll — creates Z-axis depth without 3D transforms.

```css
.card-stack {
  position: relative;
  height: 400px;
}

.card-stack .card:nth-child(1) { transform: translateY(0)    scale(1);    z-index: 3; }
.card-stack .card:nth-child(2) { transform: translateY(20px) scale(0.96); z-index: 2; opacity: 0.7; }
.card-stack .card:nth-child(3) { transform: translateY(40px) scale(0.92); z-index: 1; opacity: 0.4; }
```

```js
// On scroll, interpolate the Y offsets
const offset = scrollProgress * 60; // 0–1 from IntersectionObserver
cards[1].style.transform = `translateY(${20 - offset}px) scale(0.96)`;
cards[2].style.transform = `translateY(${40 - offset * 1.5}px) scale(0.92)`;
```

---

## Broken grid / negative margin depth

Overlapping elements create visual depth without shadows or 3D.

```css
/* Image card that bleeds into adjacent section */
.feature-image {
  margin-bottom: -80px;    /* pulls element into next section */
  position: relative;
  z-index: 2;
}

/* Text block that starts inside the section above */
.feature-text {
  padding-top: 96px;       /* creates the overlap area */
  position: relative;
  z-index: 1;
}

/* Bento cell that spans outside its grid boundary */
.bento-accent {
  grid-column: 2 / 4;
  grid-row: 1 / 3;
  margin-top: -24px;       /* intentional out-of-grid placement */
}
```

**Rule:** Only use negative margins when the overlap is the design intent, not to fix spacing bugs.

---

## Halftone / dithering (Brutalist / Print aesthetic)

Creates newsprint/screen-print texture via blend modes — no images needed.

```css
.halftone-layer {
  position: relative;
  overflow: hidden;
}

.halftone-layer::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: radial-gradient(circle, #000 1px, transparent 1px);
  background-size: 4px 4px;
  mix-blend-mode: multiply;   /* merges into background, not overlaid */
  opacity: 0.15;
  pointer-events: none;
}
```

---

## CRT scanlines (Brutalist / Terminal aesthetic)

```css
.crt-surface::after {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0, 0, 0, 0.08) 2px,
    rgba(0, 0, 0, 0.08) 4px
  );
  pointer-events: none;
  z-index: 10;
}

/* Phosphor glow effect on terminal text */
.terminal-text {
  color: #4af626;
  text-shadow:
    0 0 4px #4af626,
    0 0 12px rgba(74, 246, 38, 0.4);
}
```

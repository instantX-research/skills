# Next.js Project Scaffold Templates

## Project Initialization

```bash
npx create-next-app@latest reactor-[domain] \
  --typescript \
  --tailwind \        # only if Tailwind detected
  --eslint \
  --app \
  --src-dir=false \
  --import-alias="@/*" \
  --no-turbopack
```

For non-Tailwind projects, omit `--tailwind` flag.

After init, remove boilerplate:
- Clear `app/page.tsx` default content
- Clear `app/globals.css` default content (replace with extracted CSS)
- Remove `public/` placeholder files (next.svg, vercel.svg)

## File Templates

### app/layout.tsx

```tsx
import type { Metadata } from 'next';
import { Navbar } from '@/components/shared/Navbar';
import { Footer } from '@/components/shared/Footer';
import './globals.css';

// If Google Fonts detected:
import { Inter, Playfair_Display } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-sans',
});

// Optional: second font
const playfair = Playfair_Display({
  subsets: ['latin'],
  variable: '--font-display',
});

export const metadata: Metadata = {
  title: '[Site Title from clone]',
  description: '[Meta description from clone]',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${playfair.variable}`}>
      <body>
        <Navbar />
        <main>{children}</main>
        <Footer />
      </body>
    </html>
  );
}
```

### app/page.tsx (Home)

```tsx
import { Hero } from '@/components/home/Hero';
import { Features } from '@/components/home/Features';
import { Pricing } from '@/components/home/Pricing';
import { Testimonials } from '@/components/home/Testimonials';
import { CTA } from '@/components/home/CTA';

export default function Home() {
  return (
    <>
      <Hero />
      <Features />
      <Pricing />
      <Testimonials />
      <CTA />
    </>
  );
}
```

### app/[route]/page.tsx (Sub-pages)

```tsx
import { PricingHero } from '@/components/pricing/PricingHero';
import { Plans } from '@/components/pricing/Plans';
import { FAQ } from '@/components/pricing/FAQ';

export default function PricingPage() {
  return (
    <>
      <PricingHero />
      <Plans />
      <FAQ />
    </>
  );
}
```

### Component Template (CSS Modules)

```tsx
import styles from './ComponentName.module.css';

export function ComponentName() {
  return (
    <section className={styles.wrapper}>
      {/* Converted JSX here */}
    </section>
  );
}
```

### Component Template (Tailwind)

```tsx
export function ComponentName() {
  return (
    <section className="relative py-24 px-6">
      {/* Converted JSX with Tailwind classes */}
    </section>
  );
}
```

### Shared Navbar with Active State

```tsx
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import styles from './Navbar.module.css';

const navLinks = [
  { href: '/', label: 'Home' },
  { href: '/pricing', label: 'Pricing' },
  { href: '/about', label: 'About' },
  // ... extracted from clone
];

export function Navbar() {
  const pathname = usePathname();

  return (
    <nav className={styles.nav}>
      <div className={styles.navInner}>
        {/* Logo */}
        <Link href="/" className={styles.logo}>
          {/* Logo content from clone */}
        </Link>

        {/* Navigation Links */}
        <div className={styles.navLinks}>
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={
                pathname === link.href
                  ? styles.navLinkActive
                  : styles.navLink
              }
            >
              {link.label}
            </Link>
          ))}
        </div>

        {/* CTA Button (if present in clone) */}
        <Link href="/signup" className={styles.navCta}>
          Get Started
        </Link>
      </div>
    </nav>
  );
}
```

### next.config.mjs

```js
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '[original-domain]',
        // Allow images from the original site
      },
      {
        protocol: 'https',
        hostname: '**.amazonaws.com',
        // Common CDN for images
      },
      {
        protocol: 'https',
        hostname: '**.cloudinary.com',
      },
      {
        protocol: 'https', 
        hostname: 'images.unsplash.com',
      },
    ],
  },
};

export default nextConfig;
```

### tsconfig.json Path Aliases

Ensure `@/*` alias works:
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

## Output Directory Structure

```
results/reactor-[domain]/  (or custom --output path)
├── app/
│   ├── layout.tsx              # Root layout with Navbar, Footer, fonts
│   ├── page.tsx                # Home page
│   ├── globals.css             # All global styles + design tokens
│   ├── pricing/
│   │   └── page.tsx            # /pricing route
│   ├── about/
│   │   └── page.tsx            # /about route
│   └── [other-routes]/
│       └── page.tsx
├── components/
│   ├── shared/
│   │   ├── Navbar.tsx
│   │   ├── Navbar.module.css   # (if CSS Modules)
│   │   ├── Footer.tsx
│   │   └── Footer.module.css
│   ├── home/
│   │   ├── Hero.tsx
│   │   ├── Hero.module.css
│   │   ├── Features.tsx
│   │   ├── Features.module.css
│   │   └── ...
│   ├── pricing/
│   │   ├── PricingHero.tsx
│   │   └── ...
│   └── icons.tsx               # Extracted SVG icon components
├── public/
│   └── assets/                 # Downloaded images (optional)
├── package.json
├── tsconfig.json
├── next.config.mjs
├── tailwind.config.ts          # (if Tailwind)
└── postcss.config.mjs          # (if Tailwind)
```

## Font Handling

### Google Fonts (detected via @import or <link>)

Convert to `next/font/google` for performance:

```tsx
// Detected: @import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700")
import { Inter } from 'next/font/google';
const inter = Inter({ subsets: ['latin'], weight: ['400', '500', '600', '700'], variable: '--font-sans' });
```

Common font mappings:
- `Inter` → `next/font/google` Inter
- `Plus Jakarta Sans` → `next/font/google` Plus_Jakarta_Sans
- `DM Sans` → `next/font/google` DM_Sans
- `Geist` → `next/font/local` (not on Google Fonts — use @font-face)

### Custom Fonts (detected via @font-face)

Keep as `@font-face` in globals.css, or convert to `next/font/local`:

```tsx
import localFont from 'next/font/local';
const customFont = localFont({
  src: './fonts/CustomFont.woff2',
  variable: '--font-custom',
});
```

## Build Verification Checklist

After scaffolding, run:

```bash
cd [output-dir]
npm run build
```

Common build errors and fixes:

| Error | Fix |
|-------|-----|
| `class` attribute in JSX | Convert to `className` |
| `for` attribute in JSX | Convert to `htmlFor` |
| Unclosed self-closing tag | Add `/>` to `<img>`, `<br>`, `<input>`, etc. |
| `style` is string not object | Convert inline styles to objects |
| Missing import for `Link` | Add `import Link from 'next/link'` |
| `usePathname` in server component | Add `'use client'` directive |
| Image hostname not configured | Add to `next.config.mjs` `images.remotePatterns` |
| CSS Module class not found | Check for typos in `styles.className` reference |

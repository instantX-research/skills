# brand-quill

A Claude Code skill that rewrites everyday text into the aesthetic voice of iconic brands.

## Installation

```bash
npx skills install brand-quill
```

Or manually copy into your Claude Code skills directory:

```bash
cp -r skills/brand-quill ~/.claude/skills/
```

## What It Does

Not translation — regeneration. The copy is born again in the brand's way of thinking. 13 brand voices, each with a curated knowledge base of real copy, writing principles, and sentence templates.

## Usage

```
/brand-quill <your text> [--style <style>] [--scene <scene>] [--level <level>] [--mood <mood>] [--lang <lang>]
```

### Examples

```
/brand-quill 下雨天不想上班，只想窝在沙发上 --style ikea
```

```
/brand-quill 下雨天 --style muji --mood positive
```

```
/brand-quill 下雨天 --style aesop --mood negative
```

```
/brand-quill woke up early on a Sunday, made coffee, did nothing --style aesop
```

### Parameters

| Parameter | Values | Default |
|-----------|--------|---------|
| `--style` | `muji` `apple` `aesop` `patagonia` `diptyque` `snowpeak` `ikea` `nike` `suntory` `hobonichi` `hermes` `rollsroyce` `guinness` `all` | `muji` |
| `--scene` | `social` `vlog` `product` `bio` `slogan` | `slogan` |
| `--level` | `full` `balanced` `light` `all` | `balanced` |
| `--mood` | `positive` `negative` `neutral` | `neutral` |
| `--lang` | `zh` `en` `ja` `auto` | Follows input language |
| `--help` | — | Show help |

Use `--level` to control which concentration level(s) to output (default: `balanced`):

| Level | Description | Best For |
|-------|-------------|----------|
| `full` | Fully immersed in the brand's aesthetic | Brand accounts, product launches |
| `balanced` | Style essence, everyday approachable | Personal social media, Vlog |
| `light` | Subtle hint, natural and effortless | Casual posts, bios, chat |
| `all` | Output all 3 levels at once | Comparing intensity options |

Use `--mood` to control the emotional direction of the copy (default: `neutral`):

| Mood | Description | Example (rain) |
|------|-------------|----------------|
| `positive` | Optimistic, uplifting, hopeful | Rain → renewal, growth, the earth breathing |
| `negative` | Melancholic, reflective, wistful | Rain → solitude, longing, quiet sadness |
| `neutral` | No emotional bias, faithful to input | Rain → preserves original tone |

13 brand voices, each with a curated knowledge base of real copy, writing principles, and sentence templates:

| Style | Aesthetic | Languages | Example |
|-------|-----------|-----------|---------|
| **MUJI** | Restraint, emptiness, essence | JP / ZH / EN | 「再見，在山川、湖海、田野......見。」 |
| **Apple** | Minimal, confident, rhythmic | EN / ZH / JP | "Light. Years ahead." |
| **Aesop** | Literary, sensory, intellectual | EN / ZH / JP | "A product needs to perform, but if it can do so with a little poetry, so much the better." |
| **Patagonia** | Honest, anti-consumption, activist | EN / JP | "Don't Buy This Jacket." |
| **Diptyque** | Parisian, sensory narrative, memory | FR / EN / ZH / JP | "Philosykos captures the warmth and verdant stillness of a Greek fig grove." |
| **Snow Peak** | Nature, craftsmanship, human bonds | JP / EN / ZH | 「人生に、野遊びを。」 |
| **IKEA** | Everyday, warm, playful | EN / ZH / JP / SV | 「在一起，就很好。」 |
| **Nike** | Action, empowerment, provocation | EN / ZH / JP | "Just Do It." |
| **Suntory** | Liquid philosophy, poetic everyday | JP / ZH / EN | 「何も足さない。何も引かない。」 |
| **Hobonichi** | Gentle everyday philosophy | JP / EN | 「なんでもない日、おめでとう。」 |
| **Hermès** | Poetic craft, French nonchalance | FR / EN / ZH / JP | "Silk that remembers the wind." |
| **Rolls-Royce** | Facts as poetry, engineering elegance | EN | "At 60 miles an hour the loudest noise..." |
| **Guinness** | Patience, substance, warm storytelling | EN / GA | "Good things come to those who wait." |

## Knowledge Base

Each brand's knowledge file (`knowledge/styles/<brand>.md`) contains:

- **Writing principles** — Do's and don'ts that define the brand voice
- **Real copy** — Sourced from official campaigns, not fabricated
- **Multi-language originals** — Native copy, not translations
- **Sentence templates** — Structural patterns to guide generation
- **Copy density guidelines** — Word counts and rhythm rules

### Sources

The copy in the knowledge base is collected from official brand websites, advertising archives, and verified campaign materials. Key sources include:

- MUJI: ryohin-keikaku.jp, digitaling.com, adquan.com
- Apple: apple.com regional sites, macfan.book.mynavi.jp
- Aesop: aesop.com product pages, brand case studies
- Patagonia: patagonia.com/stories, campaign archives
- Diptyque: diptyqueparis.com product descriptions
- Snow Peak: snowpeak.co.jp/about
- IKEA: ikea.cn, digitaling.com, campaign archives
- Nike: nike.com campaigns, digitaling.com
- Suntory: suntory.co.jp, business-textbooks.com
- Hobonichi: 1101.com, Itoi Shigesato works archive
- Hermès: hermes.com seasonal campaigns
- Rolls-Royce: David Ogilvy archives, swiped.co
- Guinness: guinness.com, AMV BBDO campaign archives

## File Structure

```
brand-quill/
├── SKILL.md                           # Main skill definition
├── README.md                          # This file
└── knowledge/
    └── styles/
        ├── muji.md                    # 無印良品 — restraint, emptiness
        ├── apple.md                   # Apple — minimal confidence
        ├── aesop.md                   # Aesop — literary sensory
        ├── patagonia.md               # Patagonia — honest activism
        ├── diptyque.md                # Diptyque — Parisian narrative
        ├── snowpeak.md                # Snow Peak — nature craft
        ├── ikea.md                    # IKEA — everyday warmth
        ├── nike.md                    # Nike — action empowerment
        ├── suntory.md                 # Suntory — liquid philosophy
        ├── hobonichi.md               # Hobonichi — gentle everyday
        ├── hermes.md                  # Hermès — poetic craft
        ├── rollsroyce.md              # Rolls-Royce — facts as poetry
        └── guinness.md                # Guinness — patience & substance
```

## Credits

Created by [Haofan Wang](https://haofanwang.github.io/) with Claude Code.

## License

MIT — Use it, modify it, share it.

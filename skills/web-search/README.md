# web-search

A Claude Code skill for intelligent web search. Autonomously determines whether a query requires web search, then fetches and returns clean, formatted text results or reference images.

## Installation

```bash
npx skills add https://github.com/instantX-research/skills --skill web-search
```

Or manually copy into your Claude Code skills directory:

```bash
cp -r skills/web-search ~/.claude/skills/
```

## API Key Setup

The skill supports multiple search providers. Set up at least one:

```bash
# Option 1: Environment variable (recommended)
export TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxx

# Option 2: .env file in your project root
echo "TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxx" >> .env
```

### Supported Providers

| Provider | Env Var | Text | Image | Free Tier | Sign Up |
|----------|---------|------|-------|-----------|---------|
| **Tavily** (recommended) | `TAVILY_API_KEY` | Yes | Yes | 1,000 credits/month (recurring, no credit card) | [tavily.com](https://tavily.com) |
| **SerpAPI** | `SERPAPI_API_KEY` | Yes | Yes | 250 searches/month (recurring) | [serpapi.com](https://serpapi.com) |
| **Serper** | `SERPER_API_KEY` | Yes | Yes | 2,500 searches (one-time, no credit card) | [serper.dev](https://serper.dev) |
| **Exa** | `EXA_API_KEY` | Yes (semantic) | No | 1,000 searches/month (recurring) | [exa.ai](https://exa.ai) |
| **Brave Search** | `BRAVE_API_KEY` | Yes | Yes | ~1,000 searches/month (recurring, requires attribution) | [brave.com/search/api](https://brave.com/search/api) |
| **Jina** | `JINA_API_KEY` | Yes | Indirect | 10M tokens (one-time, non-commercial) | [jina.ai](https://jina.ai) |
| **Firecrawl** | `FIRECRAWL_API_KEY` | Yes | Yes | 500 credits (one-time, no credit card) | [firecrawl.dev](https://firecrawl.dev) |
| **SearXNG** | `SEARXNG_URL` | Yes | Yes | Unlimited (self-hosted, completely free) | [docs.searxng.org](https://docs.searxng.org) |
| **Custom** | `CUSTOM_SEARCH_URL` + `CUSTOM_SEARCH_KEY` | Varies | Varies | — | — |

> **Note:** Exa only supports text search. Jina can extract images from result pages (indirect), but does not have a dedicated image search endpoint. If your query requires high-quality image search, use Tavily, Serper, SerpAPI, Brave, Firecrawl, or SearXNG.
>
> **Recommended for free usage:**
> - **SearXNG** — completely free, unlimited, self-hosted, no API key needed
> - **Tavily** — 1,000/month recurring, no credit card, supports text + image
> - **Serper** — 2,500 one-time, no credit card, supports text + image

### SearXNG Quick Start (free, self-hosted)

```bash
# Run SearXNG locally via Docker (one command)
docker run -d -p 8080:8080 --name searxng searxng/searxng

# Set the URL
export SEARXNG_URL=http://localhost:8080
```

No API key, no rate limits, no cost. Aggregates results from 70+ search engines.

## What It Does

Given any user query, this skill:

1. **Analyzes the query** to decide if web search is needed (and what type)
2. **Extracts optimized search keywords** from natural language, with sub-question decomposition for complex queries
3. **Searches the web** via external API (Tavily, Serper, Exa, SearXNG, etc.)
4. **Cleans and filters** results — strips HTML, deduplicates, removes low-quality/watermarked images
5. **Returns formatted results** — clean markdown text, downloaded reference images

It does **not** execute the user's task — it only provides search results as input/context. Even if the query says "generate", "edit", "send", or "create", this skill will only search for relevant reference materials. It will never generate images/videos, edit files, send messages, or perform any downstream action.

Platform-agnostic: uses `curl` for all API calls, works in Claude Code, Cursor, Windsurf, or any environment with shell access.

## Usage

```bash
# Basic usage
/web-search Taylor Swift 2026 latest album

# Specify provider
/web-search --provider brave What happened at GTC 2026

# Semantic search with Exa (better for research queries)
/web-search --provider exa Recent advances in diffusion models 2026

# Force text-only search (skip images)
/web-search --text-only NVIDIA stock price today

# Force image-only search (skip text)
/web-search --images-only Wes Anderson color palette

# Limit images
/web-search --max-images 3 Tesla Cybertruck design reference

# Custom output directory
/web-search --out ./references Studio Ghibli art style examples

# Free self-hosted search
/web-search --provider searxng Latest AI news
```

### Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--max-images <N>` | Maximum number of images to download | `5` |
| `--provider <name>` | Force a specific search provider | Auto-detect |
| `--text-only` | Force text-only search, skip image search | Off |
| `--images-only` | Force image-only search, skip text search | Off |
| `--out <dir>` | Base directory to save downloaded images | `results` |

Images are saved to `<out>/<query_slug>/` to avoid conflicts between searches.

## How It Decides

### Search Type Classification

| Type | When | Example |
|------|------|---------|
| **No Search** | Generic common subjects (cat, chair, mountain, rice), abstract/creative tasks, purely imaginary entities, or too vague | "一只猫", "a chair", "write a poem", "a Zorgblat" |
| **Text Search** | Factual/data queries where images add no value, **or** generic subjects with informational intent (price, how-to, recommendation) | "Bitcoin price", "一只猫多少钱", "椅子推荐" |
| **Image Search** | Visual references needed — specific variants, named styles, named landmarks | "缅因猫", "Wes Anderson color palette", "泰山", "宜家POÄNG" |
| **Mixed Search** | **Default for most real-world entity queries.** People, events, products, characters | "Taylor Swift 2026 new album", "Brad Pitt photos", "Harry Potter fighting Iron Man" |

### Time Awareness

| Query | Time Signal | Handling |
|-------|------------|---------|
| Taylor Swift | None | No time filter — search all time |
| Taylor Swift 2026 new album | Explicit (2026) | Keep `2026`, use API time filter for that year |
| Taylor Swift latest album | Implicit recent | Add current year, filter to recent month |
| Taylor Swift 2008 concert | Historical | Keep `2008`, do NOT add current year |
| what did OpenAI announce yesterday | Relative | Convert to absolute date, filter to past few days |

## Query Behavior Quick Reference

At-a-glance table showing how the skill classifies different queries. Use this to set expectations before you search.

| Query | Category | Search? | Type |
|-------|----------|---------|------|
| **Generic subjects — NO_SEARCH** | | | |
| "一只猫" / "a cat" | Generic animal | No | — |
| "一把椅子" / "a chair" | Generic object | No | — |
| "一碗饭" / "a bowl of rice" | Generic food | No | — |
| "一座山" / "a mountain" | Generic geography | No | — |
| "a cute cat sleeping on a sofa" | Generic + adjective + scene | No | — |
| **Specific variants — IMAGE_SEARCH** | | | |
| "缅因猫" / "Maine Coon" | Specific breed | Yes | Image |
| "宜家POÄNG扶手椅" / "IKEA POÄNG" | Specific brand/model | Yes | Image |
| "东安鸡" / "Dong'an chicken" | Specific regional dish | Yes | Image |
| "泰山" / "Mount Tai" | Named landmark | Yes | Image |
| "黑胡桃木纹理" / "black walnut grain" | Specific material | Yes | Image |
| "明式圈椅" / "Ming Dynasty chair" | Specific cultural variant | Yes | Image |
| **Generic + specific mix — partial search** | | | |
| "莫奈风格的猫" / "cat in Monet style" | Generic + named style | Yes | Image (style only) |
| "故宫前的一只猫" / "cat in front of Forbidden City" | Generic + named place | Yes | Image (place only) |
| **Informational intent — TEXT_SEARCH** | | | |
| "一只猫多少钱" / "how much is a cat" | Generic + price intent | Yes | Text |
| "猫怎么养" / "how to raise a cat" | Generic + how-to intent | Yes | Text |
| "椅子推荐" / "chair recommendations" | Generic + recommendation | Yes | Text |
| "泰山门票多少钱" / "Mount Tai ticket price" | Named place + price intent | Yes | Text |
| "Apple最新发布" / "Apple latest release" | Ambiguous entity + news | Yes | Text/Mixed |
| **People & events — MIXED_SEARCH** | | | |
| "Taylor Swift 2026 latest album" | Person + recent event | Yes | Mixed |
| "Brad Pitt and Angelina Jolie red carpet" | Confirmed co-occurrence | Yes | Mixed (whole) |
| "Keanu Reeves and Gordon Ramsay together" | Uncertain co-occurrence | Yes | Mixed (whole → auto-split) |
| "周杰伦和昆凌的结婚照" | Person pair (married) | Yes | Mixed |
| **Fictional / historical entities** | | | |
| "Kim Tan from The Heirs" | Portrayed character | Yes | Image/Mixed |
| "Harry Potter and Iron Man fighting" | Fictional crossover | Yes | Mixed (split per character) |
| "Keanu Reeves with Iron Man" | Real + fictional | Yes | Mixed (search both) |
| "拿破仑在滑铁卢" / "Napoleon at Waterloo" | Historical figure | Yes | Image |
| **Styles & concepts — IMAGE_SEARCH** | | | |
| "Wes Anderson color palette" | Visual style | Yes | Image |
| "brutalist architecture inspiration" | Abstract concept | Yes | Image |
| "Santorini sunset from Oia" | Named location scenery | Yes | Image |
| "吉卜力风格的Keanu Reeves弹钢琴" | Entity + style | Yes | Image (split: style + person) |
| **Time-sensitive** | | | |
| "OpenAI昨天发布了什么" | Relative time ("yesterday") | Yes | Text |
| "Taylor Swift 2008 concert photos" | Historical time | Yes | Mixed |
| "2028 LA Olympics opening ceremony" | Future event | Yes | Mixed (partial) |
| **Comparisons** | | | |
| "Cybertruck vs Rivian R1T design" | Product comparison | Yes | Mixed (split per entity) |
| **No search — other** | | | |
| "write a poem about the moon" | Abstract/creative task | No | — |
| "sort an array in Python" | Programming task | No | — |
| "something cool" | Too vague | No | — |
| "a Zorgblat riding a flumbus" | Purely imaginary | No | — |
| **Flag overrides** | | | |
| "--images-only 一只猫" | Flag overrides generic NO_SEARCH | Yes | Image |
| "--text-only Wes Anderson" | Flag forces text only | Yes | Text |

## Output Format

### Text Results
```
## Direct Answer
Taylor Swift released her 12th studio album "The Manuscript" ...

## Sources
### 1. [Taylor Swift Announces New Album - Billboard](https://...)
Clean, formatted snippet without HTML tags...

### 2. [Title](URL)
...
```

### Image Results
Images are downloaded to a query-specific subdirectory:

```
## Reference Images for: "Elon Musk SpaceX launch"

| # | File | Source | Description |
|---|------|--------|-------------|
| 1 | results/elon_musk_spacex_launch/image_01.jpg | wikipedia.org | Elon Musk at SpaceX launch site |
| 2 | results/elon_musk_spacex_launch/image_02.jpg | ... | ... |

Images saved to: results/elon_musk_spacex_launch/
```

## When to Use Which Provider

| Use Case | Best Provider | Why |
|----------|--------------|-----|
| General purpose | Tavily, Serper | Balanced quality, supports text + image |
| Google-quality results | Serper, SerpAPI | Direct Google SERP data, image search via Google Images |
| Research / academic | Exa | Semantic search finds conceptually related content |
| Privacy-sensitive | Brave, SearXNG | No tracking, independent indexes |
| Zero cost | SearXNG | Self-hosted, unlimited, free forever |
| Deep content extraction | Firecrawl, Jina | Full page content, not just snippets (Firecrawl also supports image search) |
| Budget-friendly image search | Serper, Firecrawl | Low cost per query with dedicated image endpoints |

## MCP Server Alternatives

If you're using Claude Code, Cursor, or another MCP-compatible client, you can also use dedicated MCP search servers instead of this skill:

| MCP Server | Backend | Install |
|------------|---------|---------|
| [Brave Search MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search) | Brave API | Official, supports image/video/news |
| [Tavily MCP](https://github.com/tavily-ai/tavily-mcp) | Tavily API | Official, search + extract + crawl |
| [Exa MCP](https://exa.ai/mcp) | Exa API | Official, semantic search |
| [Serper MCP](https://github.com/marcopesani/mcp-server-serper) | Serper API | Community, full Google SERP |
| [SearXNG MCP](https://github.com/The-AI-Workshops/searxng-mcp-server) | Self-hosted SearXNG | Community, free, 70+ sources |

This skill is preferred when you want **autonomous search decision-making** (auto-detect if search is needed), **query optimization**, **image download + quality filtering**, and **cross-platform compatibility** (works without MCP support).

## More

For detailed edge case handling, query decomposition logic, full optimization examples, and 24 test cases, see [EXAMPLES.md](EXAMPLES.md).

## Credits

Created by [Haofan Wang](https://haofanwang.github.io/) with Claude Code.

## License

MIT — Use it, modify it, share it.

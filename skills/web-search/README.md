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
3. **Deduplicates sub-queries** before execution — detects strict subsets and high-overlap queries to avoid wasting budget on semantically identical searches
4. **Ensures named locations get independent searches** — place entities mentioned as background/context (schools, landmarks, venues) always get their own dedicated sub-query, not buried inside a person-focused query
5. **Searches the web** via external API (Tavily, Serper, Exa, SearXNG, etc.)
6. **Cleans and filters** results — strips HTML, deduplicates, removes low-quality/watermarked images
7. **Validates images with Pillow** — opens and fully decodes each downloaded image, filters out corrupt/truncated files and low-resolution images (< 400×400), auto-renumbers remaining files
8. **Returns formatted results** — clean markdown text, downloaded reference images

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
/web-search --search-type text NVIDIA stock price today

# Force image-only search (skip text)
/web-search --search-type image Wes Anderson color palette

# Force mixed search (both text + images)
/web-search --search-type mixed 景德镇鸡排哥

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
| `--search-type <text\|image\|mixed>` | Force search type: `text` (text only), `image` (images only), `mixed` (both) | Auto-classify |
| `--out <dir>` | Base directory to save downloaded images | `results` |

Images are saved to `<out>/<query_slug>_<YYYYMMDD_HHMMSS>/` — the timestamp suffix ensures repeated runs of the same query produce separate directories.

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
| "--search-type image 一只猫" | Flag overrides generic NO_SEARCH | Yes | Image |
| "--search-type text Wes Anderson" | Flag forces text only | Yes | Text |
| "--search-type mixed 鸡排哥" | Flag forces both text + image | Yes | Mixed |

## Output Format

Each search produces one output file:

- **`search_results.json`** — structured data for programmatic consumption (image generation pipelines, grounded prompt consumers)

### JSON Structure (`search_results.json`)

```json
{
  "query": "original user query",
  "search_type": "mixed",
  "provider": "serpapi",
  "sub_queries": [{"text": "...", "type": "image", "language": "en"}],
  "time_filter": null,
  "date": "2026-04-03",
  "text_results": [
    {"title": "...", "url": "...", "snippet": "..."}
  ],
  "image_results": [
    {
      "name": "Elon Musk",
      "sub_query": "Elon Musk",
      "directory": "elon_musk",
      "images": [
        {"file": "image_01.jpg", "path": "elon_musk/image_01.jpg",
         "width": 1080, "height": 810, "format": "JPEG",
         "source_url": "...", "description": "..."}
      ]
    }
  ],
  "grounded_prompt": {
    "enabled": true,
    "prompt": "...with [image: path] tags...",
    "reference_mapping": {"Elon Musk": ["elon_musk/image_01.jpg"]},
    "entity_corrections": {}
  },
  "summary": "Key findings in 2-3 sentences"
}
```

### Directory Structure

Single image sub-query (flat):

```
results/wes_anderson_color_palette_20260403_152030/
├── search_results.json
├── image_01.jpg
└── image_02.jpg
```

Multiple image sub-queries (per-concept subdirectories):

```
results/taylor_swift_sofi_stadium_20260403_152030/
├── search_results.json
├── taylor_swift_eras_tour/
│   ├── image_01.jpg
│   └── image_02.jpg
└── sofi_stadium_concert_night/
    ├── image_01.jpg
    └── image_02.jpg
```

### Grounded Prompt (for image generation)

When the query has generation/visual intent, both JSON and Markdown include a **Grounded Prompt** — the original prompt with `[image: path]` tags injected at each entity mention, plus a reference mapping and any entity name corrections from text search.

Downstream tools can:
- Read `search_results.json` → `grounded_prompt.prompt` and `reference_mapping` directly
- Or regex-match `\[image:\s*([^\]]+)\]` from the Markdown version

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

## Image Generation with Nano Banana

After searching, you can generate images from the `grounded_prompt` using Google Gemini's native image generation (Nano Banana). This reads `search_results.json`, loads reference images, and calls the Gemini API.

### Setup

```bash
pip install google-genai Pillow
export GEMINI_API_KEY=your-key-here   # or add to .env
```

Get a free API key at [ai.google.dev](https://ai.google.dev/).

### Models

| Model | Key | Characteristics |
|-------|-----|-----------------|
| Nano Banana 2 | `nano-banana-2` | Default. Fast, good quality |
| Nano Banana Pro | `nano-banana-pro` | Lower temperature, more controlled output |

### Usage

```bash
# Generate from search results (reads grounded_prompt + reference images)
python3 scripts/generate_nano_banana.py results/your_query_slug/

# Use Nano Banana Pro
python3 scripts/generate_nano_banana.py results/your_query_slug/ --model nano-banana-pro

# Generate 3 variations with 16:9 aspect ratio
python3 scripts/generate_nano_banana.py results/your_query_slug/ --num-images 3 --aspect-ratio 16:9

# Text-only (no reference images)
python3 scripts/generate_nano_banana.py results/your_query_slug/ --text-only

# Custom prompt
python3 scripts/generate_nano_banana.py results/your_query_slug/ --prompt "A cinematic poster of..."
```

### How It Works

1. Reads `search_results.json` → extracts `grounded_prompt`
2. Loads reference images from `reference_mapping`
3. Detects prompt language (Chinese/English) and replaces `[image: path]` tags with numbered references (e.g., `（参考图1和图2）` or `(ref image 1 & image 2)`)
4. Sends reference images with numbered labels + annotated prompt to Gemini API as multimodal content
5. Saves generated images to `<results_dir>/generated/`

### Output

```
results/your_query_slug_20260403_152030/
├── search_results.json          # from /web-search
├── concept_1/image_01.jpg       # reference images
└── generated/                   # ← generated output
    ├── generated_01.png
    └── generation_metadata.json
```

## More

For detailed edge case handling, query decomposition logic, full optimization examples, and 24 test cases, see [EXAMPLES.md](EXAMPLES.md).

## Credits

Created by [Haofan Wang](https://haofanwang.github.io/) with Claude Code.

## License

MIT — Use it, modify it, share it.

# Search Provider Reference

This file contains provider detection, selection, API key loading, and API call templates.
Loaded on-demand by the web-search skill during Steps 4–5.

---

## Provider Detection (Step 4)

**MANDATORY — run this FIRST before checking any env vars:**

```bash
_env_loaded=0
for d in . .. ../.. ../../.. skills/web-search skills/skills/web-search ~/.claude/skills/web-search; do
  if [ "$_env_loaded" -eq 0 ] && [ -f "$d/.env" ]; then
    set -a; source "$d/.env"; set +a; _env_loaded=1
  fi
done
if [ "$_env_loaded" -eq 0 ]; then
  _skill_dir="$(find . -path '*/web-search/.env' -maxdepth 5 2>/dev/null | head -1)"
  if [ -n "$_skill_dir" ]; then set -a; source "$_skill_dir"; set +a; fi
fi
```

### API Key Security Rules

- **Detection**: `[ -n "$VAR_NAME" ]` to check existence. **NEVER** `echo $VAR_NAME`.
- **Loading**: `set -a; source .env; set +a` — do NOT `cat .env` or `grep .env`.
- **Masking**: `echo "${VAR_NAME:0:4}****${VAR_NAME: -4}"` if display is needed.

### Supported Providers

| Provider | Env Var | Text | Image |
|----------|---------|------|-------|
| Tavily | `TAVILY_API_KEY` | Yes | Yes |
| SerpAPI | `SERPAPI_API_KEY` | Yes | Yes (Google Images) |
| Serper | `SERPER_API_KEY` | Yes | Yes (Google Images) |
| Exa | `EXA_API_KEY` | Yes (semantic) | No |
| Brave | `BRAVE_API_KEY` | Yes | Yes |
| Jina | `JINA_API_KEY` | Yes | Indirect only |
| Firecrawl | `FIRECRAWL_API_KEY` | Yes | Yes |
| SearXNG | `SEARXNG_URL` | Yes | Yes |
| Custom | `CUSTOM_SEARCH_URL` + `CUSTOM_SEARCH_KEY` | Depends | Depends |
| Gemini (generation) | `GEMINI_API_KEY` or `GOOGLE_API_KEY` | — | — (see nano-banana.md) |

### Selection Priority

**`IMAGE_SEARCH` or `MIXED_SEARCH`:**

| Priority | Provider | Why |
|----------|----------|-----|
| 1 | Serper | Google Images, fast, returns dimensions |
| 2 | SerpAPI | Google Images, returns original with width/height |
| 3 | Brave | Independent image index |
| 4 | Tavily | Text-first but `include_images` works |
| 5 | Firecrawl | `sources=images` support |
| 6 | SearXNG | Aggregated, quality varies |
| 7 | Jina | Indirect only — last resort |
| — | Exa | **Skip** — no image support |

**`TEXT_SEARCH`:**

| Priority | Provider | Why |
|----------|----------|-----|
| 1 | Tavily | Best text quality, returns direct answers |
| 2 | Exa | Semantic search, excellent for research |
| 3 | Serper | Google SERP, fast |
| 4 | SerpAPI | Google SERP, comprehensive |
| 5 | Brave | Independent index |
| 6 | Jina | Full page content extraction |
| 7 | Firecrawl | Full page content |
| 8 | SearXNG | Aggregated |

### Capability Checks

- **Exa** for `IMAGE_SEARCH`/`MIXED_SEARCH`: skip, fall through to next image-capable provider. Only downgrade to `TEXT_SEARCH` if no image provider is available.
- **Jina** for images: indirect only (extracts from result pages). Prefer other providers; warn if Jina is the only option.
- **No key at all**: ask user to configure one and stop. SearXNG is free and self-hosted (`docker run -p 8080:8080 searxng/searxng`).

---

## Text Search API Calls

### Tavily (text)

```bash
curl -s -X POST "https://api.tavily.com/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TAVILY_API_KEY" \
  -d "{
    \"query\": $JSON_QUERY,
    \"max_results\": 8,
    \"include_answer\": true,
    \"include_raw_content\": false,
    \"days\": $TIME_FILTER_DAYS
  }"
```
> Omit `"days"` field entirely when TIME is NONE/HISTORICAL/SPAN. Only include for IMPLICIT_RECENT/IMPLICIT_RELATIVE.

### SerpAPI (text)

```bash
curl -s "https://serpapi.com/search.json?q=$ENCODED_QUERY&api_key=$SERPAPI_API_KEY&num=8&tbs=$TIME_FILTER_TBS"
```
> Omit `&tbs=` when no time filter. Use `qdr:d` (day), `qdr:w` (week), `qdr:m` (month), `qdr:y` (year).

### Serper (text)

```bash
curl -s -X POST "https://google.serper.dev/search" \
  -H "X-API-KEY: $SERPER_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"q\": $JSON_QUERY,
    \"num\": 8,
    \"tbs\": \"$TIME_FILTER_TBS\"
  }"
```
> Omit `"tbs"` field when no time filter.

### Exa (text — semantic search)

```bash
curl -s -X POST "https://api.exa.ai/search" \
  -H "x-api-key: $EXA_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": $JSON_QUERY,
    \"num_results\": 8,
    \"type\": \"auto\",
    \"start_published_date\": \"$TIME_FILTER_START\",
    \"contents\": {
      \"text\": {\"max_characters\": 500}
    }
  }"
```
> Omit `"start_published_date"` when no time filter. Format: `"2026-03-01T00:00:00.000Z"`.

### Brave (text)

```bash
curl -s "https://api.search.brave.com/res/v1/web/search?q=$ENCODED_QUERY&count=8&freshness=$TIME_FILTER_FRESHNESS" \
  -H "X-Subscription-Token: $BRAVE_API_KEY" \
  -H "Accept: application/json"
```
> Omit `&freshness=` when no time filter. Use `pd` (day), `pw` (week), `pm` (month), `py` (year).

### Jina (text)

```bash
curl -s "https://s.jina.ai/$ENCODED_QUERY" \
  -H "Authorization: Bearer $JINA_API_KEY" \
  -H "Accept: application/json" \
  -H "X-Retain-Images: none"
```

### Jina (text + extract images from result pages)

```bash
curl -s "https://s.jina.ai/$ENCODED_QUERY" \
  -H "Authorization: Bearer $JINA_API_KEY" \
  -H "Accept: application/json" \
  -H "X-Retain-Images: all" \
  -H "X-With-Images-Summary: all" \
  -H "X-With-Generated-Alt: true"
```

### Firecrawl (text)

```bash
curl -s -X POST "https://api.firecrawl.dev/v1/search" \
  -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": $JSON_QUERY,
    \"limit\": 8,
    \"sources\": [\"web\"]
  }"
```

### SearXNG (text)

```bash
curl -s "$SEARXNG_URL/search?q=$ENCODED_QUERY&format=json&categories=general&pageno=1&time_range=$TIME_FILTER_RANGE"
```
> Omit `&time_range=` when no time filter. Use `day`, `week`, `month`, `year`.

### Custom (text)

```bash
curl -s "$CUSTOM_SEARCH_URL?q=$ENCODED_QUERY" \
  -H "Authorization: Bearer $CUSTOM_SEARCH_KEY"
```

---

## Image Search API Calls

> **CRITICAL**: Always extract the **full-size original** image URL, never the thumbnail.
> See the "Response → use this field" notes after each provider.

### Tavily (image)

```bash
curl -s -X POST "https://api.tavily.com/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TAVILY_API_KEY" \
  -d "{
    \"query\": $JSON_QUERY,
    \"max_results\": 10,
    \"include_images\": true,
    \"include_answer\": false
  }"
```
> **Response**: Image URLs are in `images[]` (string array). These are typically full-size.

### SerpAPI (image)

```bash
curl -s "https://serpapi.com/search.json?q=$ENCODED_QUERY&tbm=isch&api_key=$SERPAPI_API_KEY&num=10&ijn=0"
```
> **Response**: Use `images_results[].original` for the full-size URL. **DO NOT** use `images_results[].thumbnail` — that is Google's ~200px cached version (URL contains `encrypted-tbn`). Also available: `.original_width`, `.original_height` for pre-download size filtering.

### Serper (image)

```bash
curl -s -X POST "https://google.serper.dev/images" \
  -H "X-API-KEY: $SERPER_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"q\": $JSON_QUERY,
    \"num\": 10
  }"
```
> **Response**: Use `images[].imageUrl` for the full-size URL. **DO NOT** use `images[].thumbnailUrl`. Also available: `.imageWidth`, `.imageHeight`.

### Brave (image)

```bash
curl -s "https://api.search.brave.com/res/v1/images/search?q=$ENCODED_QUERY&count=10" \
  -H "X-Subscription-Token: $BRAVE_API_KEY" \
  -H "Accept: application/json"
```
> **Response**: Use `results[].properties.url` for the full-size URL. **DO NOT** use `results[].thumbnail.src` — that is Brave's proxied small thumbnail. Also available: `.properties.width`, `.properties.height`.

### Firecrawl (image)

```bash
curl -s -X POST "https://api.firecrawl.dev/v1/search" \
  -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": $JSON_QUERY,
    \"limit\": 10,
    \"sources\": [\"images\"]
  }"
```
> **Response**: Image URLs in `results[].metadata["og:image"]` or `results[].images[]`. Pick the largest available.

### SearXNG (image)

```bash
curl -s "$SEARXNG_URL/search?q=$ENCODED_QUERY&format=json&categories=images&pageno=1"
```
> **Response**: Use `results[].img_src` for the full-size URL. **DO NOT** use `results[].thumbnail_src`. Also available: `.img_format` (e.g., "1920 x 1080").

---

## Time Filter Parameters

| Provider | Parameter | Recent (month) | Recent (week) | Recent (day) | Custom range |
|----------|-----------|---------------|--------------|-------------|--------------|
| Tavily | `days` | `30` | `7` | `1` | N days |
| SerpAPI | `tbs` | `qdr:m` | `qdr:w` | `qdr:d` | `qdr:y` (year) |
| Serper | `tbs` | `qdr:m` | `qdr:w` | `qdr:d` | — |
| Brave | `freshness` | `pm` | `pw` | `pd` | `py` (year) |
| Exa | `start_published_date` | ISO date | ISO date | ISO date | ISO date range |
| SearXNG | `time_range` | `month` | `week` | `day` | `year` |
| Jina | — | Not supported | — | — | — |
| Firecrawl | — | Not supported | — | — | — |

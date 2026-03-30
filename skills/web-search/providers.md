# Search Provider API Reference

This file contains the API call templates for each supported search provider.
It is loaded on-demand by the web-search skill during Step 5 execution.

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

### SerpAPI (image)

```bash
curl -s "https://serpapi.com/search.json?q=$ENCODED_QUERY&tbm=isch&api_key=$SERPAPI_API_KEY&num=10"
```

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

### Brave (image)

```bash
curl -s "https://api.search.brave.com/res/v1/images/search?q=$ENCODED_QUERY&count=10" \
  -H "X-Subscription-Token: $BRAVE_API_KEY" \
  -H "Accept: application/json"
```

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

### SearXNG (image)

```bash
curl -s "$SEARXNG_URL/search?q=$ENCODED_QUERY&format=json&categories=images&pageno=1"
```

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

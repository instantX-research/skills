# web-search — Examples & Test Cases

Detailed classification logic, query optimization examples, and test cases for the web-search skill.

For quick setup and usage, see [README.md](README.md).

---

## Edge Case Handling

| Situation | Handling |
|-----------|----------|
| **Generic common subject** (a cat, a chair, a mountain, a bowl of rice) | No search — model already knows these generic concepts |
| **Specific breed / species** (Maine Coon, Shiba Inu, Blue Morpho butterfly) | Searchable — distinct visual features the model may not accurately capture |
| **Specific brand / model** (IKEA POÄNG, Tesla Model S, Nike AJ1 Chicago) | Searchable — specific product designs require reference |
| **Specific dish / regional food** (老婆饼, 狮子头, 东安鸡, Beef Wellington) | Searchable — dish names are culturally specific, appearance not universally known |
| **Generic food** (a bowl of rice, some bread, a plate of food) | No search — universally known generic food |
| **Named location / landmark** (泰山, 故宫, 长城, Santorini, Machu Picchu) | Searchable — named places have unique visual identity |
| **Generic geographic concept** (a mountain, a river, a beach) | No search — model knows generic landforms |
| **Specific material variant** (黑胡桃木, Carrara marble, brushed rose gold) | Searchable — specific material textures need reference |
| **Generic material** (wood, stone, metal) | No search — universally known generic materials |
| **Generic + specific style** (a cat in Monet style) | Search **style only** — skip the generic subject |
| **Generic + named place** (a cat in front of the Forbidden City) | Search **place only** — skip the generic subject |
| **Informational intent on generic subject** (一只猫多少钱, 椅子推荐, 猫怎么养) | Text search — informational intent overrides generic NO_SEARCH |
| **Historical figure** (Napoleon, Cleopatra) | Searchable — paintings, sculptures, engravings, archival photos exist |
| **Art style / artist** (Monet, Impressionism) | Searchable — digitized museum collections, representative paintings |
| **Fictional character** (Kim Tan, Harry Potter, Iron Man) | Searchable — stills/screenshots from real works |
| **Fictional crossover** (Harry Potter vs Iron Man) | Split and search each character independently |
| **Mythological figure** (Zeus, Medusa, Anubis) | Searchable — classical art, sculptures, modern illustrations |
| **Prehistoric creature** (dinosaur, mammoth) | Searchable — scientific illustrations, museum reconstructions, CGI |
| **Natural phenomenon** (aurora, eclipse) | Searchable — abundant photography |
| **Meme / internet culture** (Doge, Nyan Cat) | Searchable — original sources traceable |
| **Science visual** (black hole, DNA) | Searchable — NASA images, scientific illustrations |
| **Purely imaginary** (a Zorgblat) | No search — no visual source exists |
| **Future event** (2028 Olympics photos) | Mixed — planned info (text) + past edition images |
| **Ambiguous entity** (Apple, Mercury) | Disambiguate from context; default to most common meaning |
| **Unknown / made-up name** (Xarbloft CEO) | Search normally; if 0 results, report honestly |
| **Vague query** (something cool) | No search — ask for more specific details |

---

## Smart Decomposition

The skill decides whether to search as a whole or split based on **concept relationships** and **search purpose**:

| Pattern | Example | Strategy |
|---------|---------|----------|
| Generic subject (no search) | a cat, a chair, a bowl of rice | **Skip** — model already knows, no search needed |
| Generic + specific (partial) | a cat in front of the Forbidden City | **Search specific only** — search 故宫, skip cat |
| Generic + style (partial) | a cat in Monet style | **Search style only** — search Monet, skip cat |
| Joint scene — confirmed | Brad Pitt and Angelina Jolie event photo | **Whole** — keep together (known relationship) |
| Joint scene — uncertain | Keanu Reeves and Gordon Ramsay walking on the street | **Whole first → auto-split** — try combined, split if < 2 results (no known association) |
| Generation reference | generate Keanu Reeves holding coffee in Paris | **Split (skip generic)** — person + named place only; skip generic action ("holding coffee") |
| Entity + Style | Studio Ghibli style Keanu Reeves playing piano | **Split** — style refs + person refs separately |
| Comparison | Cybertruck vs R1T | **Split** — one query per entity |
| Entity + Context (find) | Elon Musk at SpaceX launch site | **Whole first** — split only if < 2 results |
| Location only | Santorini sunset from Oia | **Simple** — locations are well-indexed |
| Abstract concept | brutalist architecture inspiration | **Simple** — search in English |
| Future event | 2028 LA Olympics opening ceremony | **Partial** — search plans + past edition as reference |
| Portrayed character | Kim Tan from The Heirs driving in California | **Searchable** — character from real TV show, stills exist |
| Fictional crossover | Harry Potter fighting Iron Man | **Split** — search each character independently from their own films |
| Real + fictional mix | Keanu Reeves with Iron Man | **Search all** — both have visual material |

Max 4 sub-queries per request. If initial results are poor (< 2 relevant), auto-refines: broadens terms, switches language, or falls back from whole to split (max 2 rounds).

**Uncertain co-occurrence detection:** When a query mentions 2+ named entities together, the skill checks if they have a widely-known public relationship. If not (e.g., two celebrities from different domains), the combined search runs first but automatically falls back to independent per-entity searches when results are poor.

---

## Full Examples

| User Query | Type | Time | Language | Strategy | Queries |
|------------|------|------|----------|----------|---------|
| 一只猫 | NO_SEARCH | — | — | Skip | — (generic subject, model knows) |
| 一只猫多少钱 | TEXT | None | ZH | Simple | `猫 价格` (informational intent overrides generic) |
| 缅因猫 | IMAGE | None | EN+ZH | Simple | `Maine Coon cat photo` (specific breed) |
| 故宫前的一只猫 | IMAGE | None | EN+ZH | Partial | `故宫 Forbidden City photo` (skip cat) |
| Taylor Swift 2026 new album | MIXED | Explicit | EN | Simple | `Taylor Swift 2026 new album` + time filter |
| Taylor Swift latest album | MIXED | Recent | EN | Simple | `Taylor Swift 2026 new album` + `days=30` |
| Brad Pitt and Angelina Jolie event photo | MIXED | None | EN | Whole (confirmed) | `Brad Pitt Angelina Jolie event photo` |
| Keanu Reeves and Gordon Ramsay on the street | MIXED | None | EN | Whole → auto-split | Try `Keanu Reeves Gordon Ramsay street` → fallback to individual queries |
| generate Keanu Reeves holding coffee in Paris | IMAGE | None | EN | Split (skip generic) | `Keanu Reeves face HD` + `Eiffel Tower Paris vacation` |
| what did OpenAI announce yesterday | TEXT | Relative | EN | Simple | `OpenAI announcement 2026-03-28` + `days=3` |
| Santorini sunset from Oia | IMAGE | None | EN | Simple | `Santorini sunset Oia Greece photo` |
| 2028 LA Olympics opening ceremony | MIXED | None | EN | Partial (future) | `2028 LA Olympics opening ceremony plans` + `2024 Paris Olympics opening ceremony` |
| Harry Potter fighting Iron Man | MIXED | None | EN | Split per character | `Harry Potter movie stills HD` + `Iron Man movie stills HD` |
| Cybertruck vs Rivian R1T design | MIXED | None | EN | Split per entity | `Tesla Cybertruck design` + `Rivian R1T design` |

---

## Test Cases

### Test 1: Text search — recent event
```
/web-search Taylor Swift 2026 latest album
```
**Expected:** Text search triggered. Returns news articles about Taylor Swift's latest album. Search query optimized to `Taylor Swift 2026 new album` with time filter.

### Test 2: Image search — confirmed co-occurrence
```
/web-search Brad Pitt and Angelina Jolie red carpet photo
```
**Expected:** Image search triggered. Entities have a known public relationship (former couple) — searches as whole query. Downloads reference photos to `results/brad_pitt_angelina_jolie_red_carpet/`.

### Test 3: Image search — uncertain co-occurrence (auto-split)
```
/web-search Keanu Reeves and Gordon Ramsay walking on the street together
```
**Expected:** Image search triggered. Entities have no known public association — tries combined search first, then auto-splits into independent queries (`Keanu Reeves street candid` + `Gordon Ramsay street photo`) when combined results are poor. Results organized by person.

### Test 4: No search — generic creative request
```
/web-search write a poem about the moon
```
**Expected:** No search needed. Returns: "This query does not require web search."

### Test 4a: No search — generic common subject
```
/web-search 帮我生成一只猫
```
**Expected:** No search. "猫" (cat) is a generic common subject — the model already knows what it looks like. Same applies to "一把椅子", "一碗饭", "一座山" etc.

### Test 4b: Image search — specific variant (breed / brand / dish / landmark)
```
/web-search 生成一把宜家POÄNG扶手椅
```
**Expected:** Image search triggered. "宜家POÄNG扶手椅" (IKEA POÄNG armchair) is a specific product with distinct design. Same logic applies to specific breeds ("缅因猫"), regional dishes ("东安鸡"), and named landmarks ("泰山").

### Test 4c: Partial search — generic subject + specific context
```
/web-search 生成故宫前的一只猫
```
**Expected:** Image search triggered for **故宫 (Forbidden City) only** — "猫" is generic and skipped. Same logic for "莫奈风格的猫" — search Monet style, skip the cat.

### Test 5: Image search — specific visual style
```
/web-search Wes Anderson symmetrical color palette reference images
```
**Expected:** Image search triggered. Downloads up to 5 reference images showcasing Wes Anderson's signature visual style to `results/wes_anderson_visual_style/`.

### Test 6: Text search — tech news
```
/web-search What new features were announced at WWDC 2026
```
**Expected:** Text search triggered. Returns clean, formatted summaries of WWDC 2026 announcements with source links. Search query optimized to `WWDC 2026 announcements highlights`.

### Test 7: Image search — portrayed fictional character
```
/web-search Kim Tan from The Heirs driving in California
```
**Expected:** Image search triggered. Kim Tan is a fictional character but from a real TV show (The Heirs) — real stills/screenshots exist. Searches with character name + show title + scene context.

### Test 8: Mixed search — fictional crossover (split per character)
```
/web-search Harry Potter and Iron Man fighting in Tokyo
```
**Expected:** Mixed search triggered. Both characters have real visual material from their respective films. Splits into independent searches: `"Harry Potter movie stills"` + `"Iron Man movie stills"`. Results organized by character.

### Test 9: Mixed search — real + fictional character mix
```
/web-search Keanu Reeves standing next to Iron Man
```
**Expected:** Mixed search triggered for both entities. Keanu Reeves (real person) and Iron Man (fictional but from real films) both have visual material. Searches both independently.

### Test 10: Future event
```
/web-search 2028 LA Olympics opening ceremony photos
```
**Expected:** Text search for planned/announced information + image search for past Olympic ceremonies as reference. Informs user the event hasn't occurred yet.

### Test 11: Location only
```
/web-search Santorini sunset from Oia
```
**Expected:** Image search triggered. Downloads scenic photos of Santorini sunset from Oia.

### Test 12: Abstract concept
```
/web-search brutalist architecture inspiration
```
**Expected:** Image search triggered in English. Downloads reference images of brutalist architecture.

### Test 13: Vague query
```
/web-search something cool
```
**Expected:** No search. Query too vague. Returns: "Query is too vague. Please provide more specific details."

### Test 14: Non-English — Chinese text search
```
/web-search 周杰伦2026最新的专辑
```
**Expected:** Text search triggered. Returns results in Chinese. Demonstrates native-language search for region-specific content.

### Test 15: Non-English — Chinese generation reference
```
/web-search 帮我生成一张周杰伦和昆凌的结婚照
```
**Expected:** Mixed search (image + text). Downloads reference photos of Jay Chou and Hannah Quinlivan (confirmed co-occurrence — married couple). Does NOT generate the photo.

### Test 16: Text search — informational intent on generic subject
```
/web-search 一只猫多少钱
```
**Expected:** Text search triggered. Although "猫" is generic, the intent is **informational** (price query) — overrides NO_SEARCH. Returns text results about cat prices. Same logic for "猫怎么养", "椅子推荐", "泰山门票多少钱".

### Test 17: No search — purely imaginary entity
```
/web-search generate a Zorgblat riding a flumbus
```
**Expected:** No search. These are completely made-up entities with no real-world visual material. Not overridable by flags.

### Test 18: Text search — relative time
```
/web-search OpenAI昨天发布了什么
```
**Expected:** Text search triggered. "昨天" converted to absolute date. Time filter set to past few days.

### Test 19: Mixed search — historical time
```
/web-search Taylor Swift 2008 concert photos
```
**Expected:** Mixed search triggered (person query — images for likeness + text for concert info). Preserves `2008` as historical time signal — does NOT add current year. Time strategy: HISTORICAL.

### Test 20: Image search — entity + style split
```
/web-search 吉卜力风格的Keanu Reeves弹钢琴
```
**Expected:** Image search, split into: "Studio Ghibli anime art style" + "Keanu Reeves playing piano photo". Style and person searched independently.

### Test 21: Mixed search — comparison query
```
/web-search Cybertruck vs Rivian R1T design comparison
```
**Expected:** Mixed search, split per entity: "Tesla Cybertruck design" + "Rivian R1T design". Both are specific products.

### Test 22: Flag override — --images-only on generic subject
```
/web-search --images-only 一只猫
```
**Expected:** Image search triggered. Although "猫" is generic (normally NO_SEARCH), the explicit `--images-only` flag overrides the smart default. Downloads cat reference images.

### Test 23: Graceful degradation — zero results
```
/web-search Xarbloft CEO 最新动态
```
**Expected:** Search attempted, but entity likely doesn't exist. Returns 0 results honestly. Does NOT fabricate results or create empty output files. Suggests checking spelling or providing more context.

### Test 24: Ambiguous entity
```
/web-search Apple最新发布
```
**Expected:** Text or mixed search. "Apple" disambiguated to Apple Inc. (most common meaning) based on "发布" context. Returns results about Apple's latest product announcements.

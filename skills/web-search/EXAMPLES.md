# web-search — Examples & Test Cases

Detailed classification logic, query optimization examples, and test cases for the web-search skill.

For quick setup and usage, see [README.md](README.md).

---

## Edge Case Handling

| Situation | Handling |
|-----------|----------|
| **Generic common subject** (a cat, a chair, a mountain) | No search — model already knows these generic concepts |
| **Specific breed / brand / dish / landmark** (Maine Coon, IKEA POÄNG, 东安鸡, 故宫) | Searchable — distinct visual features the model may not accurately capture |
| **Generic + specific context** (a cat in front of the Forbidden City) | Search **specific part only** — skip the generic subject |
| **Informational intent on generic subject** (一只猫多少钱, 椅子推荐) | Text search — informational intent overrides generic NO_SEARCH |
| **Historical figure / mythological figure** (Napoleon, Medusa) | Searchable — paintings, sculptures, archival photos exist |
| **Art style / artist** (Monet, Impressionism) | Searchable — digitized museum collections, representative works |
| **Fictional character from real work** (Kim Tan, Iron Man) | Searchable — stills/screenshots from real productions |
| **Fictional crossover** (Harry Potter vs Iron Man) | Split and search each character independently |
| **Prehistoric creature / science visual** (dinosaur, black hole) | Searchable — scientific illustrations, museum reconstructions |
| **Meme / internet culture** (Doge, Nyan Cat) | Searchable — original sources traceable |
| **Purely imaginary** (a Zorgblat) | No search — no visual source exists |
| **Future event** (2028 Olympics photos) | Mixed — planned info (text) + past edition images |
| **Ambiguous entity** (Apple, Mercury) | Disambiguate from context; default to most common meaning |
| **Unknown / made-up name** (Xarbloft CEO) | Search normally; if 0 results, report honestly |
| **Vague query** (something cool) | No search — ask for more specific details |

---

## Smart Decomposition

| Pattern | Example | Strategy |
|---------|---------|----------|
| Generic subject (no search) | a cat, a chair | **Skip** — model already knows |
| Generic + specific (partial) | a cat in front of the Forbidden City | **Search specific only** — search 故宫, skip cat |
| Generic + style (partial) | a cat in Monet style | **Search style only** — search Monet, skip cat |
| Joint scene — confirmed pair | Brad Pitt and Angelina Jolie | **Whole** — keep together (known relationship) |
| Joint scene — uncertain pair | Keanu Reeves and Gordon Ramsay | **Whole first → auto-split** if < 2 results |
| Entity + Style | Studio Ghibli style Keanu Reeves | **Split** — style refs + person refs separately |
| Comparison | Cybertruck vs R1T | **Split** — one query per entity |
| Entity + named place (generation) | Keanu Reeves in Paris | **Split (skip generic)** — person + named place only |
| Future event | 2028 LA Olympics | **Partial** — search plans + past edition as reference |

Max 4 sub-queries per request. If initial results are poor (< 2 relevant), auto-refines: broadens terms, switches language, or falls back from whole to split (max 2 rounds).

---

## Test Cases

Each test covers a **distinct scenario**. Grouped by category.

### Category: No Search

#### Test 1: Generic common subject
```
/web-search 帮我生成一只猫
```
**Expected:** No search. "猫" is a generic subject the model already knows. Same for "一把椅子", "一碗饭", "一座山".

#### Test 2: Purely imaginary entity
```
/web-search generate a Zorgblat riding a flumbus
```
**Expected:** No search. Completely made-up entities with no real-world visual material.

#### Test 3: Vague query
```
/web-search something cool
```
**Expected:** No search. Too vague to produce useful results.

#### Test 4: Pure creative task (no visual reference needed)
```
/web-search write a poem about the moon
```
**Expected:** No search. Creative writing task requiring no web information.

---

### Category: Text Search

#### Test 5: Recent event — English
```
/web-search What new features were announced at WWDC 2026
```
**Expected:** Text search with time filter. Returns formatted summaries of WWDC 2026 announcements.

#### Test 6: Recent event — Chinese with relative time
```
/web-search OpenAI昨天发布了什么
```
**Expected:** Text search. "昨天" converted to absolute date, time filter set to past few days.

#### Test 7: Informational intent on generic subject
```
/web-search 一只猫多少钱
```
**Expected:** Text search. Although "猫" is generic, the **informational intent** (price query) overrides NO_SEARCH.

#### Test 8: Ambiguous entity — context disambiguation
```
/web-search Apple最新发布
```
**Expected:** Text search. "Apple" disambiguated to Apple Inc. based on "发布" context.

---

### Category: Image Search

#### Test 9: Specific breed
```
/web-search 缅因猫
```
**Expected:** Image search. "缅因猫" (Maine Coon) is a specific breed with distinct features.

#### Test 10: Named location / landmark
```
/web-search Santorini sunset from Oia
```
**Expected:** Image search. Named location with distinct visual identity.

#### Test 11: Abstract visual concept
```
/web-search brutalist architecture inspiration
```
**Expected:** Image search in English. Downloads reference images of brutalist architecture.

#### Test 12: Specific product
```
/web-search 生成一把宜家POÄNG扶手椅
```
**Expected:** Image search. "宜家POÄNG扶手椅" (IKEA POÄNG) is a specific product with distinct design.

---

### Category: Mixed / Split Search

#### Test 13: Confirmed co-occurrence
```
/web-search Brad Pitt and Angelina Jolie red carpet photo
```
**Expected:** Image search. Known couple — searches as whole query, no split needed.

#### Test 14: Uncertain co-occurrence (auto-split)
```
/web-search Keanu Reeves and Gordon Ramsay walking on the street
```
**Expected:** Tries combined search first, then auto-splits into independent queries when combined results are poor (no known public association).

#### Test 15: Entity + style split
```
/web-search 吉卜力风格的Keanu Reeves弹钢琴
```
**Expected:** Split into: "Studio Ghibli anime art style" + "Keanu Reeves photo". Style and person searched independently.

#### Test 16: Comparison query
```
/web-search Cybertruck vs Rivian R1T design comparison
```
**Expected:** Split per entity: "Tesla Cybertruck design" + "Rivian R1T design".

#### Test 17: Fictional crossover (split per character)
```
/web-search Harry Potter and Iron Man fighting in Tokyo
```
**Expected:** Split per character: "Harry Potter movie stills" + "Iron Man movie stills". Each has visual material from their respective films.

#### Test 18: Portrayed fictional character
```
/web-search Kim Tan from The Heirs driving in California
```
**Expected:** Image search. Kim Tan is fictional but from a real TV show — stills exist. Search with character name + show title.

#### Test 19: Historical time (preserve year, don't add current)
```
/web-search Taylor Swift 2008 concert photos
```
**Expected:** Mixed search. Preserves `2008` — does NOT add current year. Time strategy: HISTORICAL.

#### Test 20: Future event
```
/web-search 2028 LA Olympics opening ceremony photos
```
**Expected:** Text search for planned info + image search for past editions as reference. Informs user the event hasn't happened yet.

---

### Category: Partial Search (Generic + Specific)

#### Test 21: Generic subject + named place
```
/web-search 生成故宫前的一只猫
```
**Expected:** Image search for **故宫 only** — "猫" is generic and skipped.

#### Test 22: Generic subject + named style
```
/web-search 莫奈风格的一碗米饭
```
**Expected:** Image search for **Monet style only** — "一碗米饭" (bowl of rice) is generic and skipped.

---

### Category: Special Behaviors

#### Test 23: Flag override on generic subject
```
/web-search --search-type image 一只猫
```
**Expected:** Image search triggered. `--search-type image` overrides the generic NO_SEARCH smart default.

#### Test 24: Graceful degradation — zero results
```
/web-search Xarbloft CEO 最新动态
```
**Expected:** Search attempted, 0 results returned honestly. Does NOT fabricate results. Suggests checking spelling.

---

### Category: Image Generation Scenarios

These queries simulate what users ask when they need **reference images for AI image generation**. The skill should search for visual references, not generate the image itself.

#### Test 25: Person as specific character / cosplay
```
/web-search generate Elon Musk as a samurai warrior
```
**Expected:** Image search, split: "Elon Musk face portrait HD" + "samurai warrior armor reference". Person + costume concept searched independently.

#### Test 26: Specific fashion / runway reference
```
/web-search 生成一个模特穿Chanel 2025春季系列
```
**Expected:** Image search. "Chanel 2025春季系列" (Chanel 2025 Spring collection) is specific — search for runway photos and lookbook images.

#### Test 27: Regional dish for food photography
```
/web-search generate a photo of 佛跳墙
```
**Expected:** Image search. "佛跳墙" (Buddha Jumps Over the Wall) is a specific regional dish — search for reference photos of the dish presentation.

#### Test 28: Interior design style reference
```
/web-search generate a living room in wabi-sabi Japanese style
```
**Expected:** Image search. "Wabi-sabi Japanese interior" is a specific aesthetic — search for interior design reference images.

#### Test 29: Specific animal variant in scene
```
/web-search generate a Bengal cat sitting in a bamboo garden
```
**Expected:** Image search for "Bengal cat" only (specific breed). "Bamboo garden" is generic enough for the model to know; skip if no distinguishing named garden.

#### Test 30: Vehicle design inspiration
```
/web-search generate a retro-futuristic car inspired by Citroën DS
```
**Expected:** Image search. "Citroën DS" is a specific classic car with iconic design — search for reference photos of the vehicle.

#### Test 31: Landmark reimagined (scene generation)
```
/web-search generate a cyberpunk version of Tokyo Tower at night
```
**Expected:** Image search for "Tokyo Tower night" — the named landmark needs reference. "Cyberpunk" as a general style may or may not need search (model likely knows the aesthetic).

#### Test 32: Historical figure portrait generation
```
/web-search generate a realistic portrait of young Nikola Tesla
```
**Expected:** Image search. "Nikola Tesla" is a historical figure — search for archival photos, especially young/early portraits.

#### Test 33: Multi-person generation with specific outfits
```
/web-search generate Taylor Swift and Beyoncé in Met Gala dresses
```
**Expected:** Mixed search, split: "Taylor Swift Met Gala dress" + "Beyoncé Met Gala dress". Each person + event-specific outfit searched independently.

#### Test 34: Architecture generation with specific style
```
/web-search generate a house designed by Zaha Hadid on a cliffside
```
**Expected:** Image search. "Zaha Hadid architecture" is a specific architect's style — search for her signature building designs as reference.

#### Test 35: Specific texture / material for generation
```
/web-search generate a vase made of 黑胡桃木 with gold inlay
```
**Expected:** Image search for "黑胡桃木" (black walnut wood) texture reference. "Gold inlay" is a known technique the model likely understands; search only if needed.

#### Test 36: Album cover style generation
```
/web-search generate an album cover in the style of Pink Floyd's Dark Side of the Moon
```
**Expected:** Image search. "Pink Floyd Dark Side of the Moon album cover" is a specific iconic artwork — search for the original cover art as reference.

#### Test 37: Mascot / IP character generation
```
/web-search 生成一张皮卡丘在上海外滩的照片
```
**Expected:** Image search, split: "Pikachu official art" + "上海外滩 Shanghai Bund photo". Fictional character from real franchise + named landmark, both searched.

#### Test 38: Specific makeup / beauty look
```
/web-search generate a model with Pat McGrath golden editorial makeup look
```
**Expected:** Image search. "Pat McGrath golden editorial makeup" is a specific makeup artist's signature look — search for reference images.

---

### Category: Long / Complex Queries

Real-world users often paste verbose, detail-heavy prompts. The skill must extract **only the searchable entities** from the noise, ignore generic descriptors, and stay within the 4 sub-query limit.

#### Test 39: Long generation prompt — person + outfit + scene + mood
```
/web-search Generate a cinematic full-body portrait of Zendaya wearing a custom Iris van Herpen couture gown, standing in the middle of a foggy ancient Japanese torii gate path in Kyoto, golden hour lighting, shot on 35mm film with shallow depth of field, moody atmosphere
```
**Expected:** Image search, split (max 4): "Zendaya full body portrait HD" + "Iris van Herpen couture gown" + "Fushimi Inari torii gate path Kyoto". Generic modifiers (foggy, golden hour, 35mm film, shallow depth of field, moody) are all skipped — these are photography/rendering terms the model already understands.

#### Test 40: Long Chinese prompt — multi-entity scene composition
```
/web-search 帮我生成一张图：周杰伦穿着一件Off-White联名款卫衣，站在重庆洪崖洞夜景前，旁边停着一辆黑色兰博基尼Urus，画面风格参考王家卫电影的色调，带有霓虹灯光和雨天倒影效果
```
**Expected:** Image search, split (max 4): "周杰伦 Jay Chou face portrait" + "Off-White hoodie" + "重庆洪崖洞夜景 Chongqing Hongyadong night" + "兰博基尼Urus Lamborghini Urus black". "王家卫电影色调" (Wong Kar-wai color tone) is a known cinematic style — search if sub-query budget allows, otherwise deprioritize vs. the named entities. Generic atmosphere descriptors (霓虹灯光, 雨天倒影) are skipped.

#### Test 41: Long prompt — all generic, nothing to search
```
/web-search Create a dreamy watercolor painting of a small cottage surrounded by wildflowers in a peaceful meadow, with butterflies flying around, soft pastel colors, gentle morning sunlight streaming through misty air, birds perched on a wooden fence, a winding path leading to the door
```
**Expected:** No search. Every element is generic (cottage, wildflowers, meadow, butterflies, fence, path). No specific entity, style, brand, breed, or named place. The model can render this from general knowledge.

#### Test 42: Long prompt — single searchable entity buried in generic description
```
/web-search Generate a beautiful oil painting of a woman sitting by a window reading a book in a cozy room with warm afternoon light, a cup of tea on the table, a fluffy blanket on her lap, and a Siamese cat sleeping beside her on a vintage velvet armchair
```
**Expected:** Image search for "Siamese cat" only. Everything else (woman, window, book, cozy room, warm light, tea, blanket, armchair) is generic. The Siamese cat is a specific breed with distinct visual features (color points, blue eyes).

#### Test 43: Long prompt — multiple specific entities mixed with generic filler
```
/web-search 生成一张赛博朋克风格的海报，画面中心是一个穿着Nike Air Max 97银色子弹配色球鞋的女孩，背景是东京新宿歌舞伎町的霓虹街道，她手里拿着一杯星巴克，旁边有一只柴犬，整体画风参考Beeple的数字艺术风格，4K高清
```
**Expected:** Image search, split (max 4): "Nike Air Max 97 Silver Bullet" + "新宿歌舞伎町 Shinjuku Kabukicho neon street" + "Beeple digital art style" + "柴犬 Shiba Inu". Starbucks cup is a known brand but too visually generic (green cup) to prioritize over the 4-query limit. "赛博朋克" (cyberpunk), "4K高清" are generic modifiers — skipped.

#### Test 44: Long English prompt — fictional IP mashup with detailed scene
```
/web-search Generate an epic wide-angle shot of Goku from Dragon Ball Z and Master Chief from Halo standing back-to-back on top of a crumbling skyscraper in a post-apocalyptic New York City skyline at sunset, with dramatic clouds and debris flying everywhere, hyper-realistic style, Unreal Engine 5 rendering quality
```
**Expected:** Image search, split: "Goku Dragon Ball Z official art" + "Master Chief Halo official art" + "New York City skyline". Both are fictional characters from real franchises (searchable). NYC skyline is a named location. Post-apocalyptic mood, dramatic clouds, debris, Unreal Engine 5 — all generic rendering descriptors, skipped.

#### Test 45: Long prompt — specific art reference + historical context
```
/web-search Generate a Renaissance-style oil painting depicting the signing of the Treaty of Westphalia in 1648, with delegates in period-accurate 17th century European diplomatic attire, in a grand hall with Baroque architectural details, lighting inspired by Rembrandt's The Night Watch, warm chiaroscuro tones
```
**Expected:** Image search, split: "Treaty of Westphalia 1648 painting" + "17th century European diplomatic attire" + "Rembrandt The Night Watch painting". Historical event + period costume + specific artwork reference — all searchable. "Renaissance-style", "Baroque", "chiaroscuro" are well-known art terms the model already understands; skip unless sub-query budget allows.

#### Test 46: Long prompt — product design with multiple brand references
```
/web-search Design a limited-edition sneaker that combines the silhouette of Nike Dunk Low with the color blocking of Sacai collaboration and the sole technology of Adidas Boost, with a premium suede upper in the Tiffany blue colorway that was used in the Nike x Tiffany & Co. AF1
```
**Expected:** Image search, split (max 4): "Nike Dunk Low silhouette" + "Nike Sacai collaboration color blocking" + "Adidas Boost sole" + "Nike Tiffany AF1 blue colorway". Four distinct product references, each with specific visual identity. "Premium suede upper" is generic material — skipped.

#### Test 47: Long mixed-language prompt — travel scene with specifics
```
/web-search 帮我生成一张旅行照片，我想要一个穿着Fjällräven Kånken背包的女生，站在挪威Trolltunga巨人之舌岩石上，背景是蓝色的峡湾和远处的雪山，她穿着Arc'teryx冲锋衣，脚上是Salomon越野跑鞋，手里举着一台富士X100VI相机在自拍，整体画面要有国家地理杂志的感觉
```
**Expected:** Image search, split (max 4): "Trolltunga Norway 巨人之舌" + "Fjällräven Kånken backpack" + "Fujifilm X100VI camera" + "Arc'teryx jacket". Trolltunga is a named landmark (highest priority). Three specific brand products compete for remaining slots — prioritize by visual distinctiveness. "Salomon越野跑鞋" deprioritized (less visually unique than the others). "国家地理杂志" (National Geographic) as a style is well-known; skip. Generic descriptors (蓝色峡湾, 雪山, 自拍) skipped.

#### Test 48: Extremely long prompt — stress test for entity extraction
```
/web-search I want to create a massive mural-style digital artwork for my living room wall. The scene should depict a surreal floating city inspired by the architecture of Antoni Gaudí's Sagrada Familia mixed with the organic forms of Zaha Hadid's Heydar Aliyev Center in Baku. In the foreground, there's a garden with Japanese cherry blossoms and a traditional Chinese moon gate entrance. A woman resembling young Audrey Hepburn in her Breakfast at Tiffany's era is walking through the gate wearing a modern Valentino haute couture dress. The sky features the swirling patterns of Van Gogh's Starry Night but in a warm sunset palette. There are floating islands with miniature versions of Fallingwater by Frank Lloyd Wright and the Farnsworth House by Mies van der Rohe. The overall mood should feel like a Studio Ghibli film meets Blade Runner 2049 cinematography.
```
**Expected:** Image search, split (max 4, prioritize most visually specific): "Sagrada Familia Gaudí architecture" + "Audrey Hepburn Breakfast at Tiffany's" + "Zaha Hadid Heydar Aliyev Center Baku" + "Van Gogh Starry Night painting". Many named entities compete — prioritize those most critical to the composition's identity. Secondary references (Fallingwater, Farnsworth House, Valentino haute couture, Studio Ghibli, Blade Runner 2049) can be noted for follow-up searches if the user wants more precision. Generic elements (cherry blossoms, moon gate, floating islands, sunset palette) skipped.

---

### Category: Novel / Post-Cutoff Concepts (Web Search Required)

Image models have training data cutoffs — anything that emerged **after** their training data cannot be generated from memory. These test cases cover recent products, viral trends, new buildings, and fresh cultural phenomena that **genuinely require web search** to obtain visual references.

#### Test 49: Recent product — Apple Vision Pro
```
/web-search generate a person wearing Apple Vision Pro in a coffee shop
```
**Expected:** Image search for "Apple Vision Pro headset". This is a relatively new product (2024) that many image models cannot accurately render from training data alone. The coffee shop is generic — skipped.

#### Test 50: Recent architecture — completed landmark
```
/web-search 生成一张沙特阿拉伯The Line镜面城市的概念图
```
**Expected:** Image search for "The Line NEOM Saudi Arabia mirror city". NEOM The Line is an ongoing megaproject with a distinctive mirror-facade linear city design that post-dates most model training data. Must search for latest renderings and construction photos.

#### Test 51: Recent viral meme / internet trend
```
/web-search generate a picture in the Ghibli-fied AI portrait trend style
```
**Expected:** Image search for "Ghibli AI portrait trend 2025". The viral trend of converting photos into Studio Ghibli-style art using AI emerged in early 2025 — image models don't know what this specific trend's output looks like without reference.

#### Test 52: New car model not in training data
```
/web-search 生成一辆小米SU7 Ultra在赛道上飙车的照片
```
**Expected:** Image search for "小米SU7 Ultra Xiaomi SU7 Ultra". Xiaomi's performance EV is a very recent vehicle — image models cannot generate its specific body design, front fascia, or interior without reference images.

#### Test 53: Recent fashion collaboration / drop
```
/web-search generate a streetwear outfit featuring the UNIQLO x Marni 2025 collection
```
**Expected:** Image search for "UNIQLO Marni 2025 collaboration collection". Fast-fashion collabs have specific colorways, prints, and silhouettes that change every season — the model has no way to know the 2025 collection's look.

#### Test 54: Newly opened building / venue
```
/web-search generate a photo inside the new Lucas Museum of Narrative Art in Los Angeles
```
**Expected:** Image search for "Lucas Museum of Narrative Art Los Angeles interior". The museum by MAD Architects opened recently — its distinctive interior spaces are not in most training data.

#### Test 55: Recent tech product — humanoid robot
```
/web-search 生成一张特斯拉Optimus机器人在工厂工作的图
```
**Expected:** Image search for "Tesla Optimus robot Gen 2". Tesla's humanoid robot has undergone rapid design iterations — the latest version looks very different from early prototypes. Must search for the most recent design.

#### Test 56: New social media UI / app interface
```
/web-search generate a screenshot of the Threads app dark mode interface
```
**Expected:** Image search for "Threads app dark mode interface 2025". App UIs change frequently with updates — the current interface may differ significantly from what's in training data.

#### Test 57: Recent space mission imagery
```
/web-search generate an image of SpaceX Starship catching by the chopsticks tower
```
**Expected:** Image search for "SpaceX Starship booster catch chopsticks Mechazilla". The booster catch maneuver (2024) produced iconic imagery that most image models have never seen. Must search for actual photos/footage stills.

#### Test 58: Recent AI-generated art style / aesthetic trend
```
/web-search 用最近很火的黏土风格生成一张城市街景
```
**Expected:** Image search for "clay style AI art trend 粘土风格". The "claymation/clay render" aesthetic trend in AI art is a recent viral style with specific visual characteristics (miniature tilt-shift, clay texture, soft lighting) — model needs references of this particular trend's look.

#### Test 59: New consumer electronics — specific design
```
/web-search generate a desk setup with the Samsung Odyssey 3D monitor
```
**Expected:** Image search for "Samsung Odyssey 3D monitor". Glasses-free 3D monitor with a distinctive design — too new for most image models to know its exact appearance. "Desk setup" is generic, skipped.

#### Test 60: Recent political / cultural moment — visual reference
```
/web-search 生成一张2025年大阪世博会日本馆的外观图
```
**Expected:** Image search for "2025 Osaka Expo Japan Pavilion exterior". Expo 2025 pavilions have specific architectural designs that are only visible through recent photos and renderings — not in any image model's training data.

#### Test 61: New brand identity / logo redesign
```
/web-search generate packaging using Jaguar's new 2024 rebranded logo and visual identity
```
**Expected:** Image search for "Jaguar rebrand 2024 new logo visual identity". Jaguar's controversial rebrand (late 2024) introduced a completely new wordmark and design language — image models trained before this would generate the old leaping cat logo.

#### Test 62: Recent viral product — specific design details
```
/web-search 生成一张戴森OnTrac耳机的产品图
```
**Expected:** Image search for "Dyson OnTrac headphones". Dyson's first audio-only headphones with a distinctive colorful modular design — too new and visually unique for image models to know without reference.

#### Test 63: Emerging architecture — parametric / AI-designed structures
```
/web-search generate a building in the style of the new Shenzhen Wave art center
```
**Expected:** Image search for "Shenzhen Wave art center architecture". Newer landmark buildings in rapidly developing cities often post-date model training. Must verify the building exists and search for its actual design.

#### Test 64: Recent movie / show visual style
```
/web-search generate a scene in the visual style of Dune Part Two's desert sequences
```
**Expected:** Image search for "Dune Part Two desert cinematography Greig Fraser". While "Dune" as a franchise is known, the specific cinematography and color grading of Part Two (2024) by Greig Fraser has distinctive visual characteristics that differ from Part One.

#### Test 65: Latest iteration of a known product line
```
/web-search 生成一个人戴着Meta Quest 3S在玩游戏的场景
```
**Expected:** Image search for "Meta Quest 3S headset". Each generation of VR headsets has different industrial design — the Quest 3S has a specific form factor distinct from Quest 2 and Quest 3. Using outdated design would be visually wrong.

#### Test 66: Recent concept car / prototype
```
/web-search generate a futuristic city street with the Mercedes Vision EQXX driving through
```
**Expected:** Image search for "Mercedes Vision EQXX concept car". Concept cars have unique one-off designs that image models cannot fabricate from general knowledge of the brand. "Futuristic city street" is generic, skipped.

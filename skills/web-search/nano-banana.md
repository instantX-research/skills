# Step 9: Image Generation with Nano Banana (Optional)

When `search_results.json` contains a `grounded_prompt` with `enabled: true`, you can optionally generate images using Google Gemini's native image generation (Nano Banana). This step is **not automatic** — it runs only when the user explicitly requests image generation via `--generate` flag or a separate invocation.

## 9.1 Prerequisites

- `GEMINI_API_KEY` or `GOOGLE_API_KEY` must be set in `.env` or environment
- Python packages: `google-genai`, `Pillow`

```bash
pip install google-genai Pillow
```

## 9.2 Available Models

| Model Key | Gemini Model ID | Characteristics |
|-----------|----------------|-----------------|
| `nano-banana-2` (default) | `gemini-3.1-flash-image-preview` | Fast generation, good quality, balanced speed/fidelity |
| `nano-banana-pro` | `gemini-3-pro-image-preview` | Pro-grade quality, lower temperature (0.8) for more precise/controlled output |

## 9.3 How It Works

The generation script (`scripts/generate_nano_banana.py`) performs these steps:

1. **Read** `search_results.json` from the search output directory
2. **Load reference images** from `grounded_prompt.reference_mapping`, applying limits:
   - **Max 2 images per entity** — more references dilute each image's weight in the model's attention
   - **Max 6 images total** — keeps payload within API limits and controls cost
   - These defaults can be overridden via `--max-ref-per-entity` and `--max-ref-total`
3. **Resize reference images** — any image with a long side > 1024px is resized down (LANCZOS resampling) before upload, reducing bandwidth and token cost without meaningful quality loss
4. **Extract** the `grounded_prompt.prompt` field — the user's original prompt with `[image: path]` reference tags
5. **Apply entity corrections** from `grounded_prompt.entity_corrections`
6. **Detect prompt language** using CJK character ratio (≥15% of non-whitespace chars → Chinese, otherwise English). This is more robust than simple presence-check for mixed-language prompts like `"Taylor Swift 在长城上"`
7. **Replace `[image: ...]` tags** with numbered references matching the loaded images — e.g., Chinese: `（参考图1和图2）`, English: `(ref image 1 & image 2)` — so the model knows which uploaded image corresponds to which entity
8. **Build Gemini API contents** — reference images are sent as a single interleaved list: numbered labels (e.g., `图1 - 浪浪山小妖怪:` or `Image 1 - Elon Musk:`) + PIL.Image objects + annotated text prompt. The function returns both clean prompt text (for logging) and the full contents list (for API call)
9. **Call Gemini API** with `response_modalities=["TEXT", "IMAGE"]`, with **retry on transient errors**:
   - Retries up to 2 times (configurable) on: rate limit (429), server errors (5xx), timeouts, connection failures
   - Exponential backoff: 2s → 4s between retries
   - Non-retryable errors (auth, invalid request, content safety hard-block) abort immediately
   - If no images in response (possible soft content safety refusal), also retries before giving up
10. **Save** generated images to `<results_dir>/generated/`
11. **Write** `generation_metadata.json` with model info, prompt, config, and reference image limits used

## 9.4 Converting grounded_prompt to Nano Banana Format

The `grounded_prompt` in `search_results.json` uses `[image: path]` tags inline:

```json
{
  "prompt": "A cinematic poster of Elon Musk [image: elon_musk_spacex_starbase/image_01.jpg] at the SpaceX launch pad [image: spacex_launch_pad_boca_chica/image_01.jpg] at golden hour",
  "reference_mapping": {
    "Elon Musk": ["elon_musk_spacex_starbase/image_01.jpg", "elon_musk_spacex_starbase/image_03.jpg"],
    "SpaceX launch pad": ["spacex_launch_pad_boca_chica/image_01.jpg", "spacex_launch_pad_boca_chica/image_04.jpg"]
  }
}
```

The script detects the prompt language and converts to Gemini's multimodal content format with numbered labels:

**English prompt example:**

```python
contents = [
    "Image 1 - Elon Musk:",
    <PIL.Image: elon_musk_spacex_starbase/image_01.jpg>,
    "Image 2 - Elon Musk:",
    <PIL.Image: elon_musk_spacex_starbase/image_03.jpg>,
    "Image 3 - SpaceX launch pad:",
    <PIL.Image: spacex_launch_pad_boca_chica/image_01.jpg>,
    "Image 4 - SpaceX launch pad:",
    <PIL.Image: spacex_launch_pad_boca_chica/image_04.jpg>,
    "\nBased on the reference images above, generate: A cinematic poster of Elon Musk (ref image 1 & image 2) at the SpaceX launch pad (ref image 3 & image 4) at golden hour"
]
```

**Chinese prompt example:**

```python
contents = [
    "图1 - 浪浪山小妖怪:",
    <PIL.Image: 浪浪山小妖怪_中国奇谭/image_01.jpg>,
    "图2 - 浪浪山小妖怪:",
    <PIL.Image: 浪浪山小妖怪_中国奇谭/image_02.jpg>,
    "图3 - 天津狮子林桥:",
    <PIL.Image: 天津狮子林桥跳水/image_01.jpg>,
    "图4 - 天津狮子林桥:",
    <PIL.Image: 天津狮子林桥跳水/image_02.jpg>,
    "\n根据以上参考图片，生成：浪浪山小妖怪（参考图1和图2）在天津狮子林桥（参考图3和图4）跳水"
]
```

## 9.5 Usage

```bash
# Locate the generation script
SCRIPT_DIR="$(dirname "$(find . -path '*/web-search/scripts/generate_nano_banana.py' -maxdepth 6 2>/dev/null | head -1)")"

# Basic — generate from search results with default model (nano-banana-2)
python3 "$SCRIPT_DIR/generate_nano_banana.py" results/elon_musk_spacex_starbase_poster/

# Use Nano Banana Pro (lower temperature, more controlled)
python3 "$SCRIPT_DIR/generate_nano_banana.py" results/elon_musk_spacex_starbase_poster/ --model nano-banana-pro

# Custom prompt (override grounded_prompt)
python3 "$SCRIPT_DIR/generate_nano_banana.py" results/elon_musk_spacex_starbase_poster/ --prompt "A cinematic poster..."

# Generate multiple variations (each is a separate API call)
python3 "$SCRIPT_DIR/generate_nano_banana.py" results/elon_musk_spacex_starbase_poster/ --num-images 3

# Change aspect ratio
python3 "$SCRIPT_DIR/generate_nano_banana.py" results/elon_musk_spacex_starbase_poster/ --aspect-ratio 16:9

# Text-only (ignore reference images)
python3 "$SCRIPT_DIR/generate_nano_banana.py" results/elon_musk_spacex_starbase_poster/ --text-only

# Custom output directory
python3 "$SCRIPT_DIR/generate_nano_banana.py" results/elon_musk_spacex_starbase_poster/ --out ./my_output

# Adjust reference image limits (default: 2 per entity, 6 total)
python3 "$SCRIPT_DIR/generate_nano_banana.py" results/elon_musk_spacex_starbase_poster/ --max-ref-per-entity 3 --max-ref-total 8
```

## 9.6 Output

Generated images are saved to `<results_dir>/generated/`:

```
results/elon_musk_spacex_starbase_poster_20260403_152030/
├── search_results.json
├── elon_musk_spacex_starbase/
│   ├── image_01.jpg
│   └── ...
├── spacex_launch_pad_boca_chica/
│   ├── image_01.jpg
│   └── ...
└── generated/                      ← NEW
    ├── generated_01.png
    ├── generated_02.png           (if --num-images > 1)
    └── generation_metadata.json   (model, prompt, config)
```

`generation_metadata.json` records the full generation config for reproducibility:

```json
{
  "model": "nano-banana-2",
  "model_name": "gemini-3.1-flash-image-preview",
  "prompt": "clean text prompt used",
  "aspect_ratio": "1:1",
  "text_only": false,
  "num_reference_images": 4,
  "max_ref_per_entity": 2,
  "max_ref_total": 6,
  "reference_images": ["elon_musk_spacex_starbase/image_01.jpg", "..."],
  "generated_images": ["generated_01.png"],
  "source_search_results": "results/.../search_results.json"
}
```

## 9.7 API Key Setup

```bash
# Option 1: Environment variable
export GEMINI_API_KEY=your-key-here

# Option 2: Add to .env file (same one used for search API keys)
echo "GEMINI_API_KEY=your-key-here" >> .env
```

Get a free API key at [ai.google.dev](https://ai.google.dev/).

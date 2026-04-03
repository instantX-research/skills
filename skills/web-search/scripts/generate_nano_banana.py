#!/usr/bin/env python3
"""
Generate images using Google Gemini's native image generation (Nano Banana).

Reads search_results.json from a web-search output directory, extracts the
grounded_prompt with reference images, and calls Gemini to generate images.

Models:
  - nano-banana-2:   gemini-3.1-flash-image-preview  (fast, good quality)
  - nano-banana-pro: gemini-3-pro-image-preview       (higher quality, pro config)

Usage:
    # Basic — reads search_results.json, generates with default model
    python3 generate_nano_banana.py <results_dir>

    # Specify model
    python3 generate_nano_banana.py <results_dir> --model nano-banana-pro

    # Custom prompt (override grounded_prompt from JSON)
    python3 generate_nano_banana.py <results_dir> --prompt "A cinematic poster of ..."

    # Adjust parameters
    python3 generate_nano_banana.py <results_dir> --aspect-ratio 16:9 --num-images 2

    # Use only prompt text, no reference images
    python3 generate_nano_banana.py <results_dir> --text-only

Requires:
    pip install google-genai Pillow

Environment:
    GEMINI_API_KEY or GOOGLE_API_KEY must be set.
"""

import argparse
import base64
import io
import json
import os
import re
import sys
import time
from pathlib import Path

try:
    from google import genai
    from google.genai import types
except ImportError:
    print(
        "ERROR: google-genai is not installed. Install with: pip install google-genai",
        file=sys.stderr,
    )
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print(
        "ERROR: Pillow is not installed. Install with: pip install Pillow",
        file=sys.stderr,
    )
    sys.exit(1)


# Model mapping
MODELS = {
    "nano-banana-2": "gemini-3.1-flash-image-preview",
    "nano-banana-pro": "gemini-3-pro-image-preview",
}

# Default config per model
MODEL_CONFIGS = {
    "nano-banana-2": {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
    },
    "nano-banana-pro": {
        "temperature": 0.8,
        "top_p": 0.9,
        "top_k": 32,
    },
}

# Reference image limits
MAX_IMAGES_PER_ENTITY = 2
MAX_IMAGES_TOTAL = 6
# Resize long side to this before uploading (saves bandwidth and tokens)
MAX_IMAGE_LONG_SIDE = 1024

# Retry config
MAX_RETRIES = 2
RETRY_BASE_DELAY = 2  # seconds, doubles each retry


def load_search_results(results_dir: str) -> dict:
    """Load search_results.json from the given directory."""
    json_path = os.path.join(results_dir, "search_results.json")
    if not os.path.isfile(json_path):
        print(f"ERROR: {json_path} not found", file=sys.stderr)
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def resize_image(img: Image.Image, max_long_side: int = MAX_IMAGE_LONG_SIDE) -> Image.Image:
    """Resize image so its longest side is at most max_long_side pixels.

    Returns the original image if it's already within the limit.
    Uses LANCZOS resampling for best quality.
    """
    w, h = img.size
    long_side = max(w, h)
    if long_side <= max_long_side:
        return img
    scale = max_long_side / long_side
    new_w = int(w * scale)
    new_h = int(h * scale)
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    print(f"    Resized: {w}x{h} → {new_w}x{new_h}")
    return resized


def load_reference_images(
    results_dir: str,
    reference_mapping: dict,
    max_per_entity: int = MAX_IMAGES_PER_ENTITY,
    max_total: int = MAX_IMAGES_TOTAL,
) -> list:
    """Load reference images from the reference_mapping in search_results.json.

    Limits to max_per_entity images per entity and max_total overall.
    Resizes large images to reduce upload payload.
    Returns a list of (entity_name, PIL.Image, rel_path) tuples.
    """
    images = []
    for entity_name, paths in reference_mapping.items():
        entity_count = 0
        for rel_path in paths:
            if entity_count >= max_per_entity:
                print(f"  SKIP: {rel_path} ({entity_name}) — reached {max_per_entity} per entity limit")
                break
            if len(images) >= max_total:
                print(f"  SKIP: {rel_path} ({entity_name}) — reached {max_total} total limit")
                break
            abs_path = os.path.join(results_dir, rel_path)
            if os.path.isfile(abs_path):
                try:
                    img = Image.open(abs_path)
                    img.load()  # force decode
                    img = resize_image(img)
                    images.append((entity_name, img, rel_path))
                    entity_count += 1
                    print(f"  Loaded: {rel_path} ({entity_name})")
                except Exception as e:
                    print(f"  WARN: Cannot load {rel_path}: {e}", file=sys.stderr)
            else:
                print(f"  WARN: File not found: {abs_path}", file=sys.stderr)
        if len(images) >= max_total:
            remaining = list(reference_mapping.keys())
            current_idx = list(reference_mapping.keys()).index(entity_name)
            skipped = remaining[current_idx + 1:]
            if skipped:
                print(f"  SKIP: entities {skipped} — reached {max_total} total limit")
            break
    return images


def detect_prompt_language(text: str) -> str:
    """Detect whether the prompt is primarily Chinese or English.

    Uses CJK character ratio instead of simple presence check.
    Returns "zh" if CJK characters make up ≥15% of non-whitespace chars,
    "en" otherwise.
    """
    non_ws = re.sub(r'\s+', '', text)
    if not non_ws:
        return "en"
    cjk_count = len(re.findall(
        r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]', non_ws
    ))
    ratio = cjk_count / len(non_ws)
    return "zh" if ratio >= 0.15 else "en"


# Language-aware templates
_TEMPLATES = {
    "zh": {
        "ref_single": "（参考图{idx}）",
        "ref_multi": "（参考{refs}）",
        "ref_item": "图{idx}",
        "ref_join": "和",
        "image_label": "图{idx} - {entity}:",
        "generate_instruction": "\n根据以上参考图片，生成：{prompt}",
    },
    "en": {
        "ref_single": " (ref image {idx}) ",
        "ref_multi": " (ref {refs}) ",
        "ref_item": "image {idx}",
        "ref_join": " & ",
        "image_label": "Image {idx} - {entity}:",
        "generate_instruction": "\nBased on the reference images above, generate: {prompt}",
    },
}


def strip_image_tags(prompt: str) -> str:
    """Remove [image: ...] tags from the grounded prompt to get clean text."""
    return re.sub(r'\s*\[image:\s*[^\]]+\]\s*', ' ', prompt).strip()


def build_gemini_contents(
    grounded_prompt: dict,
    reference_images: list,
    text_only: bool = False,
) -> tuple[str, list]:
    """Build the full Gemini API contents list from grounded_prompt and reference images.

    Returns (prompt_text, contents) where:
      - prompt_text: clean text prompt for logging/metadata
      - contents: list of interleaved labels, PIL.Images, and prompt text
                  ready to pass to client.models.generate_content(contents=...)
    """
    raw_prompt = grounded_prompt.get("prompt", "")

    # Apply entity corrections
    corrections = grounded_prompt.get("entity_corrections", {})
    for original, corrected in corrections.items():
        corrected_name = corrected.split("（")[0].split("(")[0].strip()
        raw_prompt = raw_prompt.replace(original, corrected_name)

    if text_only or not reference_images:
        clean_text = strip_image_tags(raw_prompt)
        return clean_text, [clean_text]

    # Detect language from prompt text (ignoring [image:] tags)
    lang = detect_prompt_language(strip_image_tags(raw_prompt))
    tpl = _TEMPLATES[lang]

    # Build path -> entity_name mapping (exact path match)
    path_to_entity = {}
    for _entity_name, _img, _path in reference_images:
        path_to_entity[_path] = _entity_name

    # Build directory prefix -> entity_name mapping (for fuzzy match when
    # the [image:] tag path differs from the actual loaded path, e.g.
    # prompt has "哈拉尔德/image_01.jpg" but reference_mapping lists
    # "哈拉尔德/image_04.jpg")
    dir_to_entity = {}
    for _entity_name, _img, _path in reference_images:
        parent = os.path.dirname(_path)
        if parent:
            dir_to_entity[parent] = _entity_name

    # Build entity_name -> list of 1-based image indices
    entity_indices: dict[str, list[int]] = {}
    for idx, (entity_name, _img, _path) in enumerate(reference_images, start=1):
        entity_indices.setdefault(entity_name, []).append(idx)

    # Replace [image: path] tags with numbered references
    seen_entities: set[str] = set()

    def _replace_tag(match: re.Match) -> str:
        path = match.group(1).strip()
        # Try exact path match first, then fall back to directory-based match
        entity = path_to_entity.get(path)
        if not entity:
            parent = os.path.dirname(path)
            entity = dir_to_entity.get(parent) if parent else None
        if not entity or entity in seen_entities:
            return ""
        seen_entities.add(entity)
        indices = entity_indices.get(entity, [])
        if not indices:
            return ""
        if len(indices) == 1:
            return tpl["ref_single"].format(idx=indices[0])
        refs = tpl["ref_join"].join(
            tpl["ref_item"].format(idx=i) for i in indices
        )
        return tpl["ref_multi"].format(refs=refs)

    annotated_prompt = re.sub(r'\s*\[image:\s*([^\]]+)\]\s*', _replace_tag, raw_prompt)
    annotated_prompt = re.sub(r' {2,}', ' ', annotated_prompt).strip()

    # Build contents: labeled reference images + annotated prompt
    contents = []
    for idx, (entity_name, img, _path) in enumerate(reference_images, start=1):
        contents.append(tpl["image_label"].format(idx=idx, entity=entity_name))
        contents.append(img)
    contents.append(tpl["generate_instruction"].format(prompt=annotated_prompt))

    return annotated_prompt, contents


def generate_image_with_retry(
    client,
    model_name: str,
    model_key: str,
    contents: list,
    aspect_ratio: str = "1:1",
    max_retries: int = MAX_RETRIES,
):
    """Call Gemini API to generate an image, with retry on transient errors.

    Args:
        client: genai.Client instance
        model_name: Full Gemini model name
        model_key: Model key (nano-banana-2 or nano-banana-pro)
        contents: Pre-built contents list from build_gemini_contents
        aspect_ratio: Aspect ratio string (e.g., "1:1", "16:9")
        max_retries: Max number of retries on transient errors

    Returns:
        List of PIL.Image objects (generated images)
    """
    config = MODEL_CONFIGS[model_key]

    gen_config = types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        temperature=config["temperature"],
        top_p=config["top_p"],
        top_k=config["top_k"],
    )

    last_error = None
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                delay = RETRY_BASE_DELAY * (2 ** (attempt - 1))
                print(f"  Retry {attempt}/{max_retries} after {delay}s...")
                time.sleep(delay)

            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=gen_config,
            )

            generated_images = []
            text_responses = []

            if response.candidates:
                for candidate in response.candidates:
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if part.text is not None:
                                text_responses.append(part.text)
                            elif part.inline_data is not None:
                                try:
                                    img_data = part.inline_data.data
                                    if isinstance(img_data, str):
                                        img_data = base64.b64decode(img_data)
                                    pil_img = Image.open(io.BytesIO(img_data))
                                    pil_img.load()
                                    generated_images.append(pil_img)
                                except Exception as e:
                                    print(f"  WARN: Failed to decode generated image: {e}", file=sys.stderr)

            if text_responses:
                print(f"\n  Model response text:")
                for t in text_responses:
                    print(f"    {t}")

            if generated_images:
                return generated_images

            # No images generated but no exception — likely content safety refusal
            if attempt < max_retries:
                print("  WARN: No images in response, retrying...", file=sys.stderr)
                last_error = "No images in API response (possible content safety refusal)"
                continue
            else:
                print("  ERROR: No images generated after all retries", file=sys.stderr)
                return []

        except Exception as e:
            last_error = str(e)
            error_str = str(e).lower()
            # Retry on rate limit (429) and transient server errors (5xx)
            is_retryable = any(s in error_str for s in [
                "429", "rate limit", "resource exhausted",
                "500", "502", "503", "504", "internal", "unavailable",
                "timeout", "timed out", "connection",
            ])
            if is_retryable and attempt < max_retries:
                print(f"  WARN: {e} — will retry", file=sys.stderr)
                continue
            else:
                print(f"  ERROR: {e}", file=sys.stderr)
                if not is_retryable:
                    print("  (non-retryable error, aborting)", file=sys.stderr)
                return []

    print(f"  ERROR: All retries exhausted. Last error: {last_error}", file=sys.stderr)
    return []


def main():
    parser = argparse.ArgumentParser(
        description="Generate images with Gemini Nano Banana from web-search results"
    )
    parser.add_argument(
        "results_dir",
        help="Directory containing search_results.json (output of /web-search)",
    )
    parser.add_argument(
        "--model",
        choices=list(MODELS.keys()),
        default="nano-banana-2",
        help="Model to use (default: nano-banana-2)",
    )
    parser.add_argument(
        "--prompt",
        help="Override the grounded_prompt with a custom prompt",
    )
    parser.add_argument(
        "--aspect-ratio",
        default="1:1",
        help="Aspect ratio for generated images (default: 1:1). Options: 1:1, 16:9, 9:16, 4:3, 3:4",
    )
    parser.add_argument(
        "--num-images",
        type=int,
        default=1,
        help="Number of images to generate (default: 1). Each is a separate API call.",
    )
    parser.add_argument(
        "--text-only",
        action="store_true",
        help="Use only text prompt, ignore reference images",
    )
    parser.add_argument(
        "--out",
        help="Output directory for generated images (default: <results_dir>/generated)",
    )
    parser.add_argument(
        "--max-ref-per-entity",
        type=int,
        default=MAX_IMAGES_PER_ENTITY,
        help=f"Max reference images per entity (default: {MAX_IMAGES_PER_ENTITY})",
    )
    parser.add_argument(
        "--max-ref-total",
        type=int,
        default=MAX_IMAGES_TOTAL,
        help=f"Max total reference images (default: {MAX_IMAGES_TOTAL})",
    )

    args = parser.parse_args()

    # Validate results directory
    if not os.path.isdir(args.results_dir):
        print(f"ERROR: {args.results_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    # Get API key
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print(
            "ERROR: GEMINI_API_KEY or GOOGLE_API_KEY must be set.\n"
            "  export GEMINI_API_KEY=your-key-here\n"
            "  Or add to .env: GEMINI_API_KEY=your-key-here",
            file=sys.stderr,
        )
        sys.exit(1)

    # Initialize client
    client = genai.Client(api_key=api_key)

    # Load search results
    data = load_search_results(args.results_dir)
    grounded_prompt = data.get("grounded_prompt", {})

    if not grounded_prompt.get("enabled", False) and not args.prompt:
        print(
            "ERROR: No grounded_prompt in search_results.json and no --prompt provided.\n"
            "  This search was informational (no generation intent).\n"
            "  Use --prompt to provide a custom generation prompt.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Load reference images (with limits and resize)
    reference_images = []
    if not args.text_only and grounded_prompt.get("reference_mapping"):
        print("\nLoading reference images:")
        print(f"  Limits: {args.max_ref_per_entity} per entity, {args.max_ref_total} total")
        print(f"  Resize: long side ≤ {MAX_IMAGE_LONG_SIDE}px")
        reference_images = load_reference_images(
            args.results_dir,
            grounded_prompt["reference_mapping"],
            max_per_entity=args.max_ref_per_entity,
            max_total=args.max_ref_total,
        )
        print(f"  Total: {len(reference_images)} reference images loaded")

    # Build contents for Gemini API
    if args.prompt:
        prompt_text = args.prompt
        if reference_images and not args.text_only:
            # Custom prompt with reference images: wrap in the same labeled format
            lang = detect_prompt_language(args.prompt)
            tpl = _TEMPLATES[lang]
            contents = []
            for idx, (entity_name, img, _path) in enumerate(reference_images, start=1):
                contents.append(tpl["image_label"].format(idx=idx, entity=entity_name))
                contents.append(img)
            contents.append(tpl["generate_instruction"].format(prompt=args.prompt))
        else:
            contents = [args.prompt]
    else:
        prompt_text, contents = build_gemini_contents(
            grounded_prompt,
            reference_images=reference_images,
            text_only=args.text_only,
        )

    print(f"\nPrompt: {prompt_text[:300]}{'...' if len(prompt_text) > 300 else ''}")

    # Output directory
    out_dir = args.out or os.path.join(args.results_dir, "generated")
    os.makedirs(out_dir, exist_ok=True)

    # Generate images
    model_name = MODELS[args.model]
    all_generated = []

    print(f"\nCalling {model_name} (config: {args.model})...")
    print(f"  Aspect ratio: {args.aspect_ratio}")
    print(f"  Reference images: {len(reference_images) if not args.text_only else 0}")
    print(f"  Requested: {args.num_images} image(s)")

    for i in range(args.num_images):
        if args.num_images > 1:
            print(f"\n--- Generating image {i + 1}/{args.num_images} ---")

        generated = generate_image_with_retry(
            client=client,
            model_name=model_name,
            model_key=args.model,
            contents=contents,
            aspect_ratio=args.aspect_ratio,
        )
        all_generated.extend(generated)

    if not all_generated:
        print("\nERROR: No images were generated. The model may have refused the prompt "
              "or all retries were exhausted.", file=sys.stderr)
        sys.exit(1)

    # Save generated images
    saved_paths = []
    for idx, img in enumerate(all_generated, start=1):
        filename = f"generated_{idx:02d}.png"
        filepath = os.path.join(out_dir, filename)
        img.save(filepath, "PNG")
        saved_paths.append(filepath)
        print(f"  Saved: {filepath}")

    # Write generation metadata
    metadata = {
        "model": args.model,
        "model_name": model_name,
        "prompt": prompt_text,
        "aspect_ratio": args.aspect_ratio,
        "text_only": args.text_only,
        "num_reference_images": len(reference_images),
        "max_ref_per_entity": args.max_ref_per_entity,
        "max_ref_total": args.max_ref_total,
        "reference_images": [path for _, _, path in reference_images],
        "generated_images": [os.path.basename(p) for p in saved_paths],
        "source_search_results": os.path.join(args.results_dir, "search_results.json"),
    }
    meta_path = os.path.join(out_dir, "generation_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"\nDone! Generated {len(all_generated)} image(s)")
    print(f"  Images: {out_dir}/")
    print(f"  Metadata: {meta_path}")


if __name__ == "__main__":
    main()

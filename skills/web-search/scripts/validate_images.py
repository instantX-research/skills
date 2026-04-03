#!/usr/bin/env python3
"""
Validate and filter downloaded images.

Usage:
    python3 validate_images.py <image_dir> [--min-width 400] [--min-height 400] [--remove] [--keep-best N]

Checks:
  1. File can be opened and decoded by Pillow (not corrupt/truncated)
  2. Resolution meets minimum threshold (default 400x400)
  3. File size > 1KB

Fallback:
  If ALL images are filtered out by resolution, automatically relaxes the threshold
  and keeps the top N largest (by pixel count) decodable images (--keep-best, default 3).
  This ensures at least some results are always returned when valid downloads exist.

Output:
  Prints a JSON report of all images with status (valid/invalid) and dimensions.
  With --remove, deletes invalid images and re-numbers remaining files sequentially.
"""

import argparse
import json
import os
import re
import sys

try:
    from PIL import Image
except ImportError:
    print(
        "ERROR: Pillow is not installed. Install with: pip install Pillow",
        file=sys.stderr,
    )
    sys.exit(1)


def validate_image(path, min_width, min_height):
    """Validate a single image file. Returns (is_valid, info_dict).

    info_dict always contains 'decodable' (bool) indicating whether the file
    could be opened and decoded, regardless of resolution check.
    """
    info = {"file": os.path.basename(path), "path": path, "decodable": False}

    # Check file size
    try:
        size_bytes = os.path.getsize(path)
        info["size_bytes"] = size_bytes
        if size_bytes <= 1024:
            info["status"] = "invalid"
            info["reason"] = f"too small ({size_bytes} bytes)"
            return False, info
    except OSError as e:
        info["status"] = "invalid"
        info["reason"] = f"cannot stat: {e}"
        return False, info

    # Try to open and fully decode the image
    try:
        with Image.open(path) as img:
            img.verify()
        with Image.open(path) as img:
            img.load()
            width, height = img.size
            info["width"] = width
            info["height"] = height
            info["format"] = img.format
            info["mode"] = img.mode
            info["decodable"] = True
    except Exception as e:
        info["status"] = "invalid"
        info["reason"] = f"cannot decode: {e}"
        return False, info

    # Check resolution
    if width < min_width or height < min_height:
        info["status"] = "invalid"
        info["reason"] = f"low resolution ({width}x{height}, min {min_width}x{min_height})"
        return False, info

    info["status"] = "valid"
    return True, info


def renumber_images(directory):
    """Re-number remaining image files sequentially (image_01, image_02, ...)."""
    pattern = re.compile(r"^image_\d+\.(jpg|jpeg|png|webp)$", re.IGNORECASE)
    files = sorted(
        f for f in os.listdir(directory) if pattern.match(f)
    )
    if not files:
        return

    # Rename to temp names first to avoid collisions
    temp_names = []
    for f in files:
        ext = os.path.splitext(f)[1]
        temp = f"_temp_rename_{len(temp_names)}{ext}"
        os.rename(os.path.join(directory, f), os.path.join(directory, temp))
        temp_names.append(temp)

    # Rename to final sequential names
    for i, temp in enumerate(temp_names, start=1):
        ext = os.path.splitext(temp)[1]
        final = f"image_{i:02d}{ext}"
        os.rename(os.path.join(directory, temp), os.path.join(directory, final))


def main():
    parser = argparse.ArgumentParser(description="Validate and filter downloaded images")
    parser.add_argument("image_dir", help="Directory containing downloaded images")
    parser.add_argument("--min-width", type=int, default=400, help="Minimum width (default: 400)")
    parser.add_argument("--min-height", type=int, default=400, help="Minimum height (default: 400)")
    parser.add_argument("--remove", action="store_true", help="Remove invalid images and re-number")
    parser.add_argument("--keep-best", type=int, default=3,
                        help="When all images fail resolution check, keep the N largest decodable images (default: 3)")
    args = parser.parse_args()

    if not os.path.isdir(args.image_dir):
        print(f"ERROR: {args.image_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    # Find image files
    pattern = re.compile(r"^image_\d+\.(jpg|jpeg|png|webp)$", re.IGNORECASE)
    image_files = sorted(
        os.path.join(args.image_dir, f)
        for f in os.listdir(args.image_dir)
        if pattern.match(f)
    )

    if not image_files:
        print(json.dumps({"total": 0, "valid": 0, "invalid": 0, "images": [], "fallback": False}, indent=2))
        return

    results = []
    valid_count = 0
    invalid_count = 0

    for path in image_files:
        is_valid, info = validate_image(path, args.min_width, args.min_height)
        results.append(info)
        if is_valid:
            valid_count += 1
        else:
            invalid_count += 1

    # Fallback: if ALL images failed resolution check but some are decodable,
    # keep the top N largest decodable images by pixel count
    used_fallback = False
    if valid_count == 0 and args.remove:
        decodable = [r for r in results if r.get("decodable")]
        if decodable:
            # Sort by pixel count (width * height) descending
            decodable.sort(key=lambda r: r.get("width", 0) * r.get("height", 0), reverse=True)
            keep = decodable[: args.keep_best]
            keep_paths = {r["path"] for r in keep}

            # Update statuses
            for r in results:
                if r["path"] in keep_paths:
                    r["status"] = "valid"
                    r["reason"] = f"kept by fallback (best {args.keep_best} of {len(decodable)} decodable)"
                    valid_count += 1
                    invalid_count -= 1

            used_fallback = True

    # Remove invalid files if requested
    removed = []
    if args.remove:
        for r in results:
            if r["status"] == "invalid":
                try:
                    os.remove(r["path"])
                    removed.append(r["file"])
                except OSError:
                    pass

        if removed:
            renumber_images(args.image_dir)

    report = {
        "total": len(image_files),
        "valid": valid_count,
        "invalid": len(image_files) - valid_count,
        "fallback": used_fallback,
        "images": results,
    }
    if used_fallback:
        report["fallback_reason"] = (
            f"All images below {args.min_width}x{args.min_height} threshold. "
            f"Kept top {min(args.keep_best, valid_count)} by resolution."
        )
    if removed:
        report["removed"] = removed

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

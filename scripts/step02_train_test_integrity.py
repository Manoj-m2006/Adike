"""
Step 2: Train/Test Image Integrity Audit
Script: D:\\Areca\\scripts\\step02_train_test_integrity.py
Output: D:\\Areca\\reports\\step02_train_test_integrity.txt

READ-ONLY AUDIT:
Analyzes ONLY:
  - D:\\Areca\\Data\\train
  - D:\\Areca\\Data\\test

Explicitly DOES NOT inspect or touch:
  - D:\\Areca\\Data\\final_testing-20230830T042904Z-001
"""

import os
import sys
from pathlib import Path
from collections import defaultdict
import statistics

# Attempt to import PIL / Pillow
try:
    from PIL import Image, ImageFile, UnidentifiedImageError
    # Ensure truncated images raise exceptions during load
    ImageFile.LOAD_TRUNCATED_IMAGES = False
except ImportError:
    print("\n[ERROR] Pillow is required for Step 2 image integrity audit.")
    print("Please install Pillow in your environment: pip install Pillow\n")
    sys.exit(1)

# Configuration thresholds
SUSPICIOUSLY_SMALL_BYTES = 1024       # Files < 1 KB
UNUSUALLY_SMALL_DIMENSION = 64        # Width or Height < 64 px
UNUSUALLY_LARGE_DIMENSION = 4000      # Width or Height > 4000 px
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


class Logger:
    """Helper to simultaneously print to console and buffer for report file."""
    def __init__(self):
        self.lines = []

    def log(self, message=""):
        print(message)
        self.lines.append(message)

    def write_to_file(self, filepath: Path):
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(self.lines) + "\n")


def calculate_stats(values):
    """Calculates min, max, mean, and median for a list of numeric values."""
    if not values:
        return 0, 0, 0.0, 0.0
    return min(values), max(values), statistics.mean(values), statistics.median(values)


def inspect_single_image(file_path: Path, split_name: str, class_name: str):
    """Inspects a single image file for decoding, format, dimensions, mode, and corruptions."""
    result = {
        "path": str(file_path),
        "split": split_name,
        "class": class_name,
        "filename": file_path.name,
        "file_size": 0,
        "is_valid": False,
        "is_corrupt": False,
        "is_jpeg": False,
        "format": None,
        "mode": None,
        "channels": 0,
        "width": None,
        "height": None,
        "is_grayscale": False,
        "is_rgba": False,
        "is_small_file": False,
        "is_unusually_small": False,
        "is_unusually_large": False,
        "issues": [],
    }

    try:
        file_size = file_path.stat().st_size
        result["file_size"] = file_size
        if file_size == 0:
            result["issues"].append("Zero-byte file (0 bytes)")
            result["is_corrupt"] = True
            result["is_small_file"] = True
            return result
        elif file_size < SUSPICIOUSLY_SMALL_BYTES:
            result["issues"].append(f"Suspiciously small file ({file_size} bytes < {SUSPICIOUSLY_SMALL_BYTES} bytes)")
            result["is_small_file"] = True
    except Exception as e:
        result["issues"].append(f"Cannot read file stats: {e}")
        result["is_corrupt"] = True
        return result

    # 1. Open and verify image structure & full pixel decoding
    try:
        with Image.open(file_path) as img:
            result["format"] = img.format
            result["mode"] = img.mode
            result["width"], result["height"] = img.size
            result["channels"] = len(img.getbands())

            # Format check
            if img.format == "JPEG":
                result["is_jpeg"] = True
            else:
                result["issues"].append(f"Non-JPEG image format: {img.format}")

            # Mode & color channel checks
            if img.mode in ("L", "1") or result["channels"] == 1:
                result["is_grayscale"] = True
                result["issues"].append(f"Grayscale mode: {img.mode} ({result['channels']} channel)")

            if img.mode in ("RGBA", "LA") or result["channels"] == 4 or ("transparency" in img.info):
                result["is_rgba"] = True
                result["issues"].append(f"RGBA / Transparency mode: {img.mode} ({result['channels']} channels)")

            # Dimension checks
            w, h = result["width"], result["height"]
            if w < UNUSUALLY_SMALL_DIMENSION or h < UNUSUALLY_SMALL_DIMENSION:
                result["is_unusually_small"] = True
                result["issues"].append(f"Unusually small dimension: {w}x{h} (< {UNUSUALLY_SMALL_DIMENSION}px)")

            if w > UNUSUALLY_LARGE_DIMENSION or h > UNUSUALLY_LARGE_DIMENSION:
                result["is_unusually_large"] = True
                result["issues"].append(f"Unusually large dimension: {w}x{h} (> {UNUSUALLY_LARGE_DIMENSION}px)")

            # Full decode check: force decompression of pixel array
            try:
                img.load()
            except Exception as decode_err:
                result["is_corrupt"] = True
                result["issues"].append(f"Pixel decoding failed / truncated: {decode_err}")
                return result

        # If no corruptions or decode errors, mark valid
        if not result["is_corrupt"]:
            result["is_valid"] = True

    except UnidentifiedImageError:
        result["is_corrupt"] = True
        result["issues"].append("Cannot identify image format / UnidentifiedImageError")
    except Exception as e:
        result["is_corrupt"] = True
        result["issues"].append(f"Failed to open/decode image: {e}")

    return result


def audit_split(split_path: Path, split_name: str, logger: Logger):
    """Audits all images in a given split directory (train or test)."""
    results = []
    if not split_path.exists() or not split_path.is_dir():
        logger.log(f"[WARNING] Directory does not exist: {split_path}")
        return results

    # Direct class subdirectories
    class_dirs = sorted([d for d in split_path.iterdir() if d.is_dir()], key=lambda x: x.name)

    for c_dir in class_dirs:
        class_name = c_dir.name
        # Walk within this class folder
        for root, _, files in os.walk(c_dir):
            for f in files:
                f_path = Path(root) / f
                if f_path.suffix.lower() in IMAGE_EXTENSIONS or f_path.is_file():
                    res = inspect_single_image(f_path, split_name, class_name)
                    results.append(res)

    # Check any stray files directly under split root
    root_files = [f for f in split_path.iterdir() if f.is_file()]
    for rf in root_files:
        res = inspect_single_image(rf, split_name, "_ROOT_UNASSIGNED_")
        res["issues"].append("File located directly in split root without class directory")
        results.append(res)

    return results


def main():
    logger = Logger()

    project_root = Path(r"D:\Areca")
    train_path = project_root / "Data" / "train"
    test_path = project_root / "Data" / "test"
    report_file = project_root / "reports" / "step02_train_test_integrity.txt"

    separator = "=" * 80
    sub_sep = "-" * 80

    logger.log(separator)
    logger.log("STEP 2 — TRAIN/TEST IMAGE INTEGRITY AUDIT REPORT")
    logger.log(separator)
    logger.log(f"Project Root: {project_root}")
    logger.log(f"Target Train Directory: {train_path}")
    logger.log(f"Target Test Directory:  {test_path}")
    logger.log(sub_sep)
    logger.log("CRITICAL SCOPE ENFORCEMENT:")
    logger.log("  [VERIFIED] ONLY train and test directories were analyzed.")
    logger.log("  [VERIFIED] D:\\Areca\\Data\\final_testing-20230830T042904Z-001 was ABSOLUTELY NOT inspected.")
    logger.log(separator)

    # Perform Image Integrity Audit
    train_results = audit_split(train_path, "train", logger)
    test_results = audit_split(test_path, "test", logger)
    all_results = train_results + test_results

    total_images = len(all_results)
    train_total = len(train_results)
    test_total = len(test_results)

    train_valid = [r for r in train_results if r["is_valid"]]
    train_invalid = [r for r in train_results if not r["is_valid"] or r["is_corrupt"]]

    test_valid = [r for r in test_results if r["is_valid"]]
    test_invalid = [r for r in test_results if not r["is_valid"] or r["is_corrupt"]]

    total_valid = len(train_valid) + len(test_valid)
    total_invalid = len(train_invalid) + len(test_invalid)

    # Grayscale & RGBA
    grayscale_images = [r for r in all_results if r["is_grayscale"]]
    rgba_images = [r for r in all_results if r["is_rgba"]]
    non_jpeg_images = [r for r in all_results if r["format"] and not r["is_jpeg"]]
    small_files = [r for r in all_results if r["is_small_file"]]
    unusually_small = [r for r in all_results if r["is_unusually_small"]]
    unusually_large = [r for r in all_results if r["is_unusually_large"]]
    corrupt_images = [r for r in all_results if r["is_corrupt"]]

    # Dimension statistics
    valid_widths = [r["width"] for r in all_results if r["width"] is not None]
    valid_heights = [r["height"] for r in all_results if r["height"] is not None]

    min_w, max_w, mean_w, median_w = calculate_stats(valid_widths)
    min_h, max_h, mean_h, median_h = calculate_stats(valid_heights)

    # Modes breakdown
    modes_count = defaultdict(int)
    formats_count = defaultdict(int)
    for r in all_results:
        if r["mode"]:
            modes_count[r["mode"]] += 1
        if r["format"]:
            formats_count[r["format"]] += 1

    # 1. Open & 2. Decode & 3. Valid JPEG summary
    logger.log("1 & 2 & 3. IMAGE OPEN, DECODE & JPEG VALIDATION:")
    logger.log(f"   - Total files analyzed:                 {total_images}")
    logger.log(f"   - Successfully opened & fully decoded:  {total_valid} ({total_valid / total_images * 100:.2f}%)" if total_images else "0")
    logger.log(f"   - Failed opening / decode errors:       {len(corrupt_images)}")
    logger.log(f"   - Valid JPEG format:                    {formats_count.get('JPEG', 0)}")
    if non_jpeg_images:
        logger.log(f"   - Other formats detected:               {dict(formats_count)}")
    logger.log(sub_sep)

    # 4 & 5. Dimensions & Channels/Modes
    logger.log("4 & 5. DIMENSIONS & COLOR CHANNELS / MODES:")
    logger.log(f"   - Image modes breakdown:                {dict(modes_count)}")
    logger.log(f"   - Color channels:                       RGB (3 bands): {modes_count.get('RGB', 0)}, "
               f"Grayscale (1 band): {modes_count.get('L', 0) + modes_count.get('1', 0)}, "
               f"RGBA (4 bands): {modes_count.get('RGBA', 0)}")
    logger.log(sub_sep)

    # 6 & 7. Grayscale & RGBA detection
    logger.log("6 & 7. GRAYSCALE & RGBA / TRANSPARENCY DETECTION:")
    logger.log(f"   - Grayscale images count:               {len(grayscale_images)}")
    logger.log(f"   - RGBA / Transparent images count:      {len(rgba_images)}")
    logger.log(sub_sep)

    # 8, 9, 10, 11. Anomalies & Corruptions
    logger.log("8, 9, 10, 11. ANOMALY & CORRUPTION DETECTION:")
    logger.log(f"   - Zero-byte / Suspiciously small (<1KB): {len(small_files)}")
    logger.log(f"   - Unusually small images (<{UNUSUALLY_SMALL_DIMENSION}px):       {len(unusually_small)}")
    logger.log(f"   - Unusually large images (>{UNUSUALLY_LARGE_DIMENSION}px):      {len(unusually_large)}")
    logger.log(f"   - Truncated / Corrupted JPEG files:     {len(corrupt_images)}")
    logger.log(sub_sep)

    # 12 & 13. Overall Dimension Stats
    logger.log("12 & 13. OVERALL IMAGE DIMENSION METRICS:")
    logger.log(f"   - Width  (px): Min = {min_w}, Max = {max_w}, Mean = {mean_w:.2f}, Median = {median_w:.2f}")
    logger.log(f"   - Height (px): Min = {min_h}, Max = {max_h}, Mean = {mean_h:.2f}, Median = {median_h:.2f}")
    logger.log(sub_sep)

    # 14. Dimension stats per class
    logger.log("14. IMAGE DIMENSIONS PER CLASS:")
    classes = sorted(list(set(r["class"] for r in all_results)))
    for c in classes:
        c_res = [r for r in all_results if r["class"] == c]
        c_widths = [r["width"] for r in c_res if r["width"] is not None]
        c_heights = [r["height"] for r in c_res if r["height"] is not None]
        c_min_w, c_max_w, c_mean_w, c_med_w = calculate_stats(c_widths)
        c_min_h, c_max_h, c_mean_h, c_med_h = calculate_stats(c_heights)
        logger.log(f"   Class: '{c}' ({len(c_res)} images)")
        logger.log(f"      Width  (px): Min={c_min_w}, Max={c_max_w}, Mean={c_mean_w:.1f}, Med={c_med_w:.1f}")
        logger.log(f"      Height (px): Min={c_min_h}, Max={c_max_h}, Mean={c_mean_h:.1f}, Med={c_med_h:.1f}")
    logger.log(sub_sep)

    # 15 & 16. Split-wise and overall integrity summary
    logger.log("15 & 16. INTEGRITY STATUS BREAKDOWN (TRAIN vs TEST):")
    logger.log(f"   - TRAIN Split: Total = {train_total}, Valid = {len(train_valid)}, Invalid/Corrupt = {len(train_invalid)}")
    logger.log(f"   - TEST Split:  Total = {test_total}, Valid = {len(test_valid)}, Invalid/Corrupt = {len(test_invalid)}")
    logger.log(f"   - COMBINED:    Total = {total_images}, Valid = {total_valid}, Invalid/Corrupt = {total_invalid}")
    logger.log(sub_sep)

    # 17. List of problematic images
    problematic = [r for r in all_results if r["issues"]]
    logger.log(f"17. PROBLEMATIC / FLAGGED IMAGES LIST ({len(problematic)} total flagged):")
    if problematic:
        for idx, p in enumerate(problematic, 1):
            dim_str = f"{p['width']}x{p['height']}" if p['width'] is not None else "N/A"
            logger.log(f"   [{idx}] File: {p['path']}")
            logger.log(f"       Split: {p['split']} | Class: {p['class']} | Dimensions: {dim_str} | Mode: {p['mode']}")
            logger.log(f"       Problems: {'; '.join(p['issues'])}")
    else:
        logger.log("   None (All images passed integrity, decoding, format, mode, and dimension checks)")
    logger.log(separator)

    # Disclaimer notice
    logger.log("SCOPE CONFIRMATION:")
    logger.log("   D:\\Areca\\Data\\final_testing-20230830T042904Z-001 was NOT inspected or accessed.")
    logger.log(separator)

    # Required Final Summary Block
    is_pass = (total_invalid == 0 and len(corrupt_images) == 0 and total_images > 0)
    overall_status = "PASS" if is_pass else "FAIL"

    dim_range_str = f"Width [{min_w} to {max_w}], Height [{min_h} to {max_h}]"

    logger.log("FINAL INTEGRITY AUDIT SUMMARY:")
    logger.log(f"TOTAL IMAGES:           {total_images}")
    logger.log(f"VALID IMAGES:           {total_valid}")
    logger.log(f"INVALID/CORRUPT IMAGES: {total_invalid}")
    logger.log(f"TRAIN VALID/INVALID:    {len(train_valid)} / {len(train_invalid)}")
    logger.log(f"TEST VALID/INVALID:     {len(test_valid)} / {len(test_invalid)}")
    logger.log(f"GRAYSCALE COUNT:        {len(grayscale_images)}")
    logger.log(f"RGBA COUNT:             {len(rgba_images)}")
    logger.log(f"DIMENSION RANGE:        {dim_range_str}")
    logger.log(f"OVERALL PASS/FAIL:      {overall_status}")
    logger.log(separator)
    logger.log(f"Report written to: {report_file}")
    logger.log(separator)

    # Save to disk
    logger.write_to_file(report_file)


if __name__ == "__main__":
    main()

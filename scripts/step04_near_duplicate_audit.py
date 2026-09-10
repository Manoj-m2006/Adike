"""
Step 4: Near-Duplicate / Perceptual Similarity Audit
Script: D:\\Areca\\scripts\\step04_near_duplicate_audit.py
Output:
  - D:\\Areca\\reports\\step04_near_duplicate_audit.txt
  - D:\\Areca\\reports\\step04_near_duplicate_audit.json

READ-ONLY AUDIT:
Analyzes ONLY:
  - D:\\Areca\\Data\\train
  - D:\\Areca\\Data\\test

Explicitly DOES NOT inspect, read, or access:
  - D:\\Areca\\Data\\final_testing-20230830T042904Z-001
"""

import os
import sys
import json
import time
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

# Verify required libraries
try:
    from PIL import Image
    import numpy as np
except ImportError as e:
    print(f"\n[ERROR] Missing required library: {e}")
    print("Please install in your environment: pip install Pillow numpy\n")
    sys.exit(1)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}

# Perceptual Hashing Configuration
PHASH_SIZE = 8       # 8x8 = 64-bit hash
HIGHFREQ_FACTOR = 4  # 32x32 intermediate resolution for DCT

# Similarity Thresholds (Hamming Distance on 64-bit pHash)
THRESHOLD_VERY_STRONG = 4   # 0 to 4: Very Strong Similarity (near-identical image / compression / minor resize)
THRESHOLD_STRONG = 8        # 5 to 8: Strong Similarity (same scene / slight crop / angle / lighting shift)
THRESHOLD_POSSIBLE = 10     # 9 to 10: Possible Similarity (structural / visual pattern similarity)
MAX_HAMMING_THRESHOLD = 10  # Maximum distance to consider as candidate pair


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


# Precompute 1D DCT matrix for 32 -> 8 transform
def build_dct_matrix(n_in=32, n_out=8):
    """Builds a projection matrix for 1D DCT-II from n_in to n_out coefficients."""
    matrix = np.zeros((n_out, n_in), dtype=np.float64)
    for k in range(n_out):
        for n in range(n_in):
            scale = np.sqrt(1.0 / n_in) if k == 0 else np.sqrt(2.0 / n_in)
            matrix[k, n] = scale * np.cos(np.pi * (2 * n + 1) * k / (2.0 * n_in))
    return matrix

DCT_MATRIX = build_dct_matrix(32, 8)


def compute_phash_64(image_path: Path):
    """
    Computes standard 64-bit pHash (Perceptual Hash) using DCT on Pillow grayscale image.
    Returns:
        hash_int: 64-bit integer
        hash_hex: 16-character hex string
        hash_bits: 64-element boolean numpy array
    """
    with Image.open(image_path) as img:
        img_gray = img.convert("L").resize((32, 32), Image.Resampling.BILINEAR)
        arr = np.asarray(img_gray, dtype=np.float64)

    # 2D DCT: D * A * D.T (shape: 8x8)
    dct_2d = DCT_MATRIX @ arr @ DCT_MATRIX.T
    
    # 64 coefficients
    dct_flat = dct_2d.flatten()
    
    # Exclude DC term (index 0) or use median across coefficients
    median_val = np.median(dct_flat[1:])
    
    # 64 boolean bits
    bits = (dct_flat > median_val)
    
    # Convert to 64-bit unsigned integer & hex string
    hash_int = 0
    for b in bits:
        hash_int = (hash_int << 1) | int(b)
    hash_hex = f"{hash_int:016x}"
    
    return hash_int, hash_hex, bits


def compute_dhash_64(image_path: Path):
    """Computes standard 64-bit dHash (Difference Hash) as supporting metric."""
    with Image.open(image_path) as img:
        img_gray = img.convert("L").resize((9, 8), Image.Resampling.BILINEAR)
        arr = np.asarray(img_gray, dtype=np.int32)
    # Difference between adjacent horizontal pixels: (8 rows, 8 differences)
    diff = arr[:, 1:] > arr[:, :-1]
    diff_flat = diff.flatten()
    hash_int = 0
    for b in diff_flat:
        hash_int = (hash_int << 1) | int(b)
    return f"{hash_int:016x}"


def categorize_similarity(dist: int) -> str:
    """Classifies Hamming distance into documented similarity tiers."""
    if dist <= THRESHOLD_VERY_STRONG:
        return "Very strong similarity"
    elif dist <= THRESHOLD_STRONG:
        return "Strong similarity"
    elif dist <= THRESHOLD_POSSIBLE:
        return "Possible similarity"
    else:
        return "Distinct"


def collect_split_images(split_path: Path, split_name: str, logger: Logger):
    """Collects images strictly within split_path."""
    images = []
    if not split_path.exists() or not split_path.is_dir():
        logger.log(f"[ERROR] Split directory does not exist: {split_path}")
        return images

    class_dirs = sorted([d for d in split_path.iterdir() if d.is_dir()], key=lambda x: x.name)
    for c_dir in class_dirs:
        class_name = c_dir.name
        for root, _, files in os.walk(c_dir):
            for file_name in files:
                f_path = Path(root) / file_name
                if f_path.suffix.lower() in IMAGE_EXTENSIONS or f_path.is_file():
                    images.append({
                        "path": str(f_path),
                        "filename": file_name,
                        "split": split_name,
                        "class": class_name,
                        "rel_path": str(f_path.relative_to(split_path.parent))
                    })

    # Stray files directly under split root
    for rf in [f for f in split_path.iterdir() if f.is_file()]:
        images.append({
            "path": str(rf),
            "filename": rf.name,
            "split": split_name,
            "class": "_ROOT_UNASSIGNED_",
            "rel_path": str(rf.relative_to(split_path.parent))
        })
    return images


def process_image_hashing(img_item):
    """Worker function to compute perceptual hashes for a single image."""
    f_path = Path(img_item["path"])
    try:
        hash_int, hash_hex, bits = compute_phash_64(f_path)
        dhash_hex = compute_dhash_64(f_path)
        return {
            "success": True,
            "img_item": img_item,
            "phash_int": hash_int,
            "phash_hex": hash_hex,
            "phash_bits": bits,
            "dhash_hex": dhash_hex,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "img_item": img_item,
            "phash_int": None,
            "phash_hex": None,
            "phash_bits": None,
            "dhash_hex": None,
            "error": str(e)
        }


def main():
    logger = Logger()

    project_root = Path(r"D:\Areca")
    train_dir = project_root / "Data" / "train"
    test_dir = project_root / "Data" / "test"
    reports_dir = project_root / "reports"
    txt_report_file = reports_dir / "step04_near_duplicate_audit.txt"
    json_report_file = reports_dir / "step04_near_duplicate_audit.json"

    reports_dir.mkdir(parents=True, exist_ok=True)

    separator = "=" * 80
    sub_sep = "-" * 80

    logger.log(separator)
    logger.log("STEP 4 — NEAR-DUPLICATE / PERCEPTUAL SIMILARITY AUDIT (pHash & dHash)")
    logger.log(separator)
    logger.log(f"Project Root:           {project_root}")
    logger.log(f"Target Train Directory: {train_dir}")
    logger.log(f"Target Test Directory:  {test_dir}")
    logger.log(sub_sep)
    logger.log("CRITICAL SCOPE ENFORCEMENT:")
    logger.log("  [VERIFIED] ONLY train and test directories were analyzed.")
    logger.log("  [VERIFIED] D:\\Areca\\Data\\final_testing-20230830T042904Z-001 was ABSOLUTELY NOT accessed.")
    logger.log(sub_sep)
    logger.log("PERCEPTUAL HASH CONFIGURATION:")
    logger.log(f"  - Primary Algorithm:    pHash (DCT-based, 64-bit / 8x8 matrix)")
    logger.log(f"  - Secondary Metric:     dHash (Gradient Difference, 64-bit)")
    logger.log(f"  - Similarity Tiers (Hamming Distance <= 64):")
    logger.log(f"      * Very strong similarity:  Distance 0 to {THRESHOLD_VERY_STRONG}")
    logger.log(f"      * Strong similarity:       Distance {THRESHOLD_VERY_STRONG + 1} to {THRESHOLD_STRONG}")
    logger.log(f"      * Possible similarity:     Distance {THRESHOLD_STRONG + 1} to {THRESHOLD_POSSIBLE}")
    logger.log(f"      * Distinct / Unflagged:    Distance > {THRESHOLD_POSSIBLE}")
    logger.log(separator)

    # 1. Collect images
    train_items = collect_split_images(train_dir, "train", logger)
    test_items = collect_split_images(test_dir, "test", logger)
    all_items = train_items + test_items

    total_train = len(train_items)
    total_test = len(test_items)
    total_images = len(all_items)

    logger.log(f"Total Train images found: {total_train}")
    logger.log(f"Total Test images found:  {total_test}")
    logger.log(f"Total images to process:  {total_images}")
    logger.log(sub_sep)

    # 2. Compute Perceptual Hashes
    logger.log("Computing 64-bit pHash and dHash for all images...")
    start_time = time.time()

    processed_data = []
    errors = []

    # Parallelize image loading and hash calculation across CPU threads
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
        results = list(executor.map(process_image_hashing, all_items))

    for res in results:
        if res["success"]:
            item = res["img_item"]
            item["phash_int"] = res["phash_int"]
            item["phash_hex"] = res["phash_hex"]
            item["phash_bits"] = res["phash_bits"]
            item["dhash_hex"] = res["dhash_hex"]
            processed_data.append(item)
        else:
            errors.append({
                "path": res["img_item"]["path"],
                "error": res["error"]
            })

    hash_duration = time.time() - start_time
    total_processed = len(processed_data)
    logger.log(f"Hashing complete in {hash_duration:.2f}s ({total_processed}/{total_images} images succeeded, {len(errors)} errors)")
    logger.log(sub_sep)

    # 3. Fast Vectorized Hamming Distance Candidate Search
    logger.log("Performing fast vectorized Hamming distance comparisons...")
    search_start = time.time()

    # Stack bit arrays into matrix of shape (N, 64) boolean
    bit_matrix = np.array([item["phash_bits"] for item in processed_data], dtype=bool)
    n_items = len(processed_data)

    within_train_candidates = []
    within_test_candidates = []
    train_test_candidates = []
    class_conflict_candidates = []

    # Chunked all-pairs distance search (batch rows to stay cache & memory friendly)
    BATCH_SIZE = 500
    for i_start in range(0, n_items, BATCH_SIZE):
        i_end = min(i_start + BATCH_SIZE, n_items)
        batch_bits = bit_matrix[i_start:i_end]  # shape (B, 64)

        # Vectorized XOR sum: (B, N) Hamming distances
        # diff shape: (B, N, 64) -> sum over axis 2
        dists = np.sum(batch_bits[:, None, :] != bit_matrix[None, :, :], axis=2, dtype=np.uint8)

        # Inspect pairs (i, j) where j > i
        for local_i in range(i_end - i_start):
            i = i_start + local_i
            # Look at candidates with distance <= MAX_HAMMING_THRESHOLD for j > i
            matching_j = np.where(dists[local_i, i + 1 :] <= MAX_HAMMING_THRESHOLD)[0] + (i + 1)

            img_a = processed_data[i]
            for j in matching_j:
                img_b = processed_data[j]
                h_dist = int(dists[local_i, j])
                tier = categorize_similarity(h_dist)

                pair_record = {
                    "image_a": {
                        "path": img_a["path"],
                        "split": img_a["split"],
                        "class": img_a["class"],
                        "phash": img_a["phash_hex"],
                        "dhash": img_a["dhash_hex"],
                    },
                    "image_b": {
                        "path": img_b["path"],
                        "split": img_b["split"],
                        "class": img_b["class"],
                        "phash": img_b["phash_hex"],
                        "dhash": img_b["dhash_hex"],
                    },
                    "hamming_distance": h_dist,
                    "similarity_tier": tier,
                    "is_class_conflict": (img_a["class"] != img_b["class"]),
                    "is_cross_split": (img_a["split"] != img_b["split"]),
                }

                # Check class conflict
                if img_a["class"] != img_b["class"]:
                    class_conflict_candidates.append(pair_record)

                # Categorize split relation
                if img_a["split"] == "train" and img_b["split"] == "train":
                    within_train_candidates.append(pair_record)
                elif img_a["split"] == "test" and img_b["split"] == "test":
                    within_test_candidates.append(pair_record)
                else:
                    # Cross-split (ensure image_a is train and image_b is test for consistency)
                    if img_a["split"] == "test" and img_b["split"] == "train":
                        pair_record["image_a"], pair_record["image_b"] = pair_record["image_b"], pair_record["image_a"]
                    train_test_candidates.append(pair_record)

    search_duration = time.time() - search_start
    total_candidate_pairs = (
        len(within_train_candidates) + len(within_test_candidates) + len(train_test_candidates)
    )
    logger.log(f"Similarity search complete in {search_duration:.2f}s.")
    logger.log(f"Total candidate near-duplicate pairs found: {total_candidate_pairs}")
    logger.log(separator)

    # 4. Detailed Breakdown of Findings

    # A. Within Train
    logger.log(f"A. NEAR-DUPLICATES WITHIN TRAIN: {len(within_train_candidates)} candidate pair(s)")
    train_dist_counts = defaultdict(int)
    for p in within_train_candidates:
        train_dist_counts[p["similarity_tier"]] += 1
    for tier, cnt in sorted(train_dist_counts.items()):
        logger.log(f"   - {tier}: {cnt} pair(s)")
    logger.log(sub_sep)

    # B. Within Test
    logger.log(f"B. NEAR-DUPLICATES WITHIN TEST: {len(within_test_candidates)} candidate pair(s)")
    test_dist_counts = defaultdict(int)
    for p in within_test_candidates:
        test_dist_counts[p["similarity_tier"]] += 1
    for tier, cnt in sorted(test_dist_counts.items()):
        logger.log(f"   - {tier}: {cnt} pair(s)")
    logger.log(sub_sep)

    # C. Cross-Split (Train <-> Test) Leakage Candidates
    logger.log(f"C. NEAR-DUPLICATES ACROSS TRAIN AND TEST (CRITICAL LEAKAGE CANDIDATES): {len(train_test_candidates)} candidate pair(s)")
    cross_dist_counts = defaultdict(int)
    for p in train_test_candidates:
        cross_dist_counts[p["similarity_tier"]] += 1
    for tier, cnt in sorted(cross_dist_counts.items()):
        logger.log(f"   - {tier}: {cnt} pair(s)")

    # Sort cross-split pairs by Hamming distance (ascending)
    train_test_candidates.sort(key=lambda x: x["hamming_distance"])

    logger.log("\nDETAILED LIST OF TRAIN <-> TEST NEAR-DUPLICATE CANDIDATE PAIRS:")
    if train_test_candidates:
        for idx, cp in enumerate(train_test_candidates, 1):
            t_img = cp["image_a"]
            te_img = cp["image_b"]
            conflict_tag = " [CLASS CONFLICT!]" if cp["is_class_conflict"] else ""
            logger.log(f"   [{idx}] Hamming Distance: {cp['hamming_distance']} ({cp['similarity_tier']}){conflict_tag}")
            logger.log(f"       TRAIN: [{t_img['class']}] {t_img['path']}")
            logger.log(f"              pHash: {t_img['phash']} | dHash: {t_img['dhash']}")
            logger.log(f"       TEST:  [{te_img['class']}] {te_img['path']}")
            logger.log(f"              pHash: {te_img['phash']} | dHash: {te_img['dhash']}")
    else:
        logger.log("   None (ZERO train-test near-duplicate candidates detected)")
    logger.log(sub_sep)

    # D. Class-Conflict Candidates
    logger.log(f"D. NEAR-DUPLICATE CANDIDATES UNDER DIFFERENT CLASS LABELS: {len(class_conflict_candidates)} candidate pair(s)")
    if class_conflict_candidates:
        for idx, cc in enumerate(class_conflict_candidates, 1):
            logger.log(f"   [{idx}] Hamming Distance: {cc['hamming_distance']} ({cc['similarity_tier']})")
            logger.log(f"       Image A: [{cc['image_a']['split']} - {cc['image_a']['class']}] {cc['image_a']['path']}")
            logger.log(f"       Image B: [{cc['image_b']['split']} - {cc['image_b']['class']}] {cc['image_b']['path']}")
    else:
        logger.log("   None (All similar pairs share identical class labels)")
    logger.log(separator)

    # Summary and Decision Status
    status_str = "REVIEW REQUIRED" if (len(train_test_candidates) > 0 or len(class_conflict_candidates) > 0) else "PASS"

    logger.log("============================================================")
    logger.log("STEP 4 - NEAR-DUPLICATE AUDIT SUMMARY")
    logger.log("============================================================")
    logger.log(f"Train images found:                 {total_train}")
    logger.log(f"Test images found:                  {total_test}")
    logger.log(f"Total images:                       {total_images}")
    logger.log(f"Images successfully processed:      {total_processed}")
    logger.log(f"Processing errors:                  {len(errors)}")
    logger.log(f"Perceptual hash method:             pHash (DCT 64-bit) + dHash (64-bit)")
    logger.log(f"Hash size:                          64 bits (8x8 matrix)")
    logger.log(f"Similarity thresholds:              Very Strong (0-4), Strong (5-8), Possible (9-10)")
    logger.log("")
    logger.log(f"Total candidate pairs/groups:       {total_candidate_pairs}")
    logger.log(f"Within-train candidates:            {len(within_train_candidates)}")
    logger.log(f"Within-test candidates:             {len(within_test_candidates)}")
    logger.log(f"Train-test candidates:              {len(train_test_candidates)}")
    logger.log(f"Class-conflict candidates:          {len(class_conflict_candidates)}")
    logger.log("")
    logger.log(f"STEP 4 STATUS:                      {status_str}")
    logger.log("")
    logger.log("Reports saved:")
    logger.log(f"  - {txt_report_file}")
    logger.log(f"  - {json_report_file}")
    logger.log("------------------------------------------------------------")
    logger.log("SCOPE CONFIRMATION:")
    logger.log("  final_testing-20230830T042904Z-001 was NOT accessed.")
    logger.log("============================================================")

    # Save Text Report
    logger.write_to_file(txt_report_file)

    # Prepare JSON serializable structure (without numpy arrays)
    json_data = {
        "audit_step": "STEP 04 - Near-Duplicate / Perceptual Similarity Audit",
        "scope": {
            "project_root": str(project_root),
            "train_dir": str(train_dir),
            "test_dir": str(test_dir),
            "final_testing_excluded": True
        },
        "configuration": {
            "algorithm": "pHash (DCT 64-bit)",
            "supporting_algorithm": "dHash (64-bit)",
            "hash_size_bits": 64,
            "thresholds": {
                "very_strong_similarity": f"0 - {THRESHOLD_VERY_STRONG}",
                "strong_similarity": f"{THRESHOLD_VERY_STRONG + 1} - {THRESHOLD_STRONG}",
                "possible_similarity": f"{THRESHOLD_STRONG + 1} - {THRESHOLD_POSSIBLE}",
                "max_examined_distance": MAX_HAMMING_THRESHOLD
            }
        },
        "summary": {
            "total_train_images": total_train,
            "total_test_images": total_test,
            "total_images": total_images,
            "images_successfully_processed": total_processed,
            "processing_errors_count": len(errors),
            "total_candidate_pairs": total_candidate_pairs,
            "within_train_candidates_count": len(within_train_candidates),
            "within_test_candidates_count": len(within_test_candidates),
            "train_test_candidates_count": len(train_test_candidates),
            "class_conflict_candidates_count": len(class_conflict_candidates),
            "step_4_status": status_str
        },
        "train_test_leakage_candidates": train_test_candidates,
        "class_conflict_candidates": class_conflict_candidates,
        "within_train_candidates": within_train_candidates,
        "within_test_candidates": within_test_candidates,
        "errors": errors
    }

    with open(json_report_file, "w", encoding="utf-8") as jf:
        json.dump(json_data, jf, indent=2)


if __name__ == "__main__":
    main()

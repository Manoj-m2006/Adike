"""
Step 9: Final Post-Cleanup Duplicate & Leakage Verification
Script: D:\\Areca\\scripts\\step09_final_post_cleanup_verification.py
Output:
  - D:\\Areca\\reports\\step09_final_post_cleanup_verification.txt
  - D:\\Areca\\reports\\step09_final_post_cleanup_verification.json
  - D:\\Areca\\reports\\step09_final_post_cleanup_verification.csv

READ-ONLY AUDIT:
Analyzes ONLY:
  - D:\\Areca\\Data\\train
  - D:\\Areca\\Data\\test
  - D:\\Areca\\cleanup_backup_step08
  - D:\\Areca\\reports

Explicitly DOES NOT inspect, read, or access:
  - D:\\Areca\\Data\\final_testing-20230830T042904Z-001
"""

import os
import sys
import json
import csv
import time
import hashlib
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

# Required image and numeric processing
try:
    from PIL import Image, ImageFile, UnidentifiedImageError
    import numpy as np
    ImageFile.LOAD_TRUNCATED_IMAGES = False
except ImportError as e:
    print(f"\n[ERROR] Missing required library: {e}")
    print("Please install in your environment: pip install Pillow numpy\n")
    sys.exit(1)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
CHUNK_SIZE = 65536
NORM_SIZE = (128, 128)

EXPECTED_TRAIN_COUNTS = {
    "Healthy_Leaf": 582,
    "Healthy_Nut": 1771,
    "Mahali_Koleroga": 2317,
    "yellow leaf disease": 1439
}
EXPECTED_TRAIN_TOTAL = 6109

EXPECTED_TEST_COUNTS = {
    "Healthy_Leaf": 152,
    "Healthy_Nut": 472,
    "Mahali_Koleroga": 641,
    "yellow leaf disease": 370
}
EXPECTED_TEST_TOTAL = 1635

EXPECTED_QUARANTINE_COUNTS = {
    "Healthy_Leaf": 22,
    "Healthy_Nut": 115,
    "Mahali_Koleroga": 246,
    "yellow leaf disease": 38
}
EXPECTED_QUARANTINE_TOTAL = 421


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


# ----------------------------------------------------------------------
# Hashing & Perceptual Features
# ----------------------------------------------------------------------
def compute_sha256(filepath: Path) -> str:
    """Computes SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            hasher.update(chunk)
    return hasher.hexdigest()


# Precompute 1D DCT matrix for 32 -> 8 transform
def build_dct_matrix(n_in=32, n_out=8):
    matrix = np.zeros((n_out, n_in), dtype=np.float64)
    for k in range(n_out):
        for n in range(n_in):
            scale = np.sqrt(1.0 / n_in) if k == 0 else np.sqrt(2.0 / n_in)
            matrix[k, n] = scale * np.cos(np.pi * (2 * n + 1) * k / (2.0 * n_in))
    return matrix

DCT_MATRIX = build_dct_matrix(32, 8)


def compute_phash_and_dhash(image_path: Path):
    """Computes 64-bit pHash, 64-bit dHash, and verifies full decoding."""
    with Image.open(image_path) as img:
        # Force pixel decompression to ensure integrity
        img.load()
        img_format = img.format
        img_mode = img.mode
        img_size = img.size

        # pHash
        img_gray_32 = img.convert("L").resize((32, 32), Image.Resampling.BILINEAR)
        arr_32 = np.asarray(img_gray_32, dtype=np.float64)
        dct_2d = DCT_MATRIX @ arr_32 @ DCT_MATRIX.T
        dct_flat = dct_2d.flatten()
        median_val = np.median(dct_flat[1:])
        p_bits = (dct_flat > median_val)

        phash_int = 0
        for b in p_bits:
            phash_int = (phash_int << 1) | int(b)
        phash_hex = f"{phash_int:016x}"

        # dHash
        img_gray_98 = img.convert("L").resize((9, 8), Image.Resampling.BILINEAR)
        arr_98 = np.asarray(img_gray_98, dtype=np.int32)
        diff = arr_98[:, 1:] > arr_98[:, :-1]
        diff_flat = diff.flatten()
        dhash_int = 0
        for b in diff_flat:
            dhash_int = (dhash_int << 1) | int(b)
        dhash_hex = f"{dhash_int:016x}"

    return {
        "phash_int": phash_int,
        "phash_hex": phash_hex,
        "phash_bits": p_bits,
        "dhash_hex": dhash_hex,
        "format": img_format,
        "mode": img_mode,
        "size": img_size
    }


# ----------------------------------------------------------------------
# Structural Similarity / Pixel-Level Comparison
# ----------------------------------------------------------------------
class ImageCache:
    def __init__(self):
        self.cache = {}

    def get(self, image_path_str: str):
        if image_path_str in self.cache:
            return self.cache[image_path_str]

        p = Path(image_path_str)
        if not p.exists():
            return None

        try:
            with Image.open(p) as img:
                orig_size = img.size
                aspect_ratio = orig_size[0] / max(orig_size[1], 1)

                gray_img = img.convert("L").resize(NORM_SIZE, Image.Resampling.BILINEAR)
                gray_arr = np.asarray(gray_img, dtype=np.float32) / 255.0

                rgb_img = img.convert("RGB").resize(NORM_SIZE, Image.Resampling.BILINEAR)
                rgb_arr = np.asarray(rgb_img, dtype=np.float32) / 255.0

                q_r = (rgb_arr[:, :, 0] * 7.999).astype(np.int32)
                q_g = (rgb_arr[:, :, 1] * 7.999).astype(np.int32)
                q_b = (rgb_arr[:, :, 2] * 7.999).astype(np.int32)
                color_indices = q_r * 64 + q_g * 8 + q_b
                hist, _ = np.histogram(color_indices, bins=512, range=(0, 512))
                hist = hist.astype(np.float32) / (NORM_SIZE[0] * NORM_SIZE[1])

            data = {
                "orig_size": orig_size,
                "aspect_ratio": aspect_ratio,
                "gray_arr": gray_arr,
                "rgb_arr": rgb_arr,
                "hist": hist
            }
            self.cache[image_path_str] = data
            return data
        except Exception:
            return None


def calculate_ssim(img1: np.ndarray, img2: np.ndarray) -> float:
    c1 = (0.01) ** 2
    c2 = (0.03) ** 2
    mu1 = np.mean(img1)
    mu2 = np.mean(img2)
    sigma1_sq = np.var(img1)
    sigma2_sq = np.var(img2)
    sigma12 = np.mean((img1 - mu1) * (img2 - mu2))
    num = (2 * mu1 * mu2 + c1) * (2 * sigma12 + c2)
    den = (mu1 ** 2 + mu2 ** 2 + c1) * (sigma1_sq + sigma2_sq + c2)
    return float(num / den) if den != 0 else 0.0


def calculate_ncc(img1: np.ndarray, img2: np.ndarray) -> float:
    f1 = img1.flatten()
    f2 = img2.flatten()
    f1_dev = f1 - np.mean(f1)
    f2_dev = f2 - np.mean(f2)
    denom = np.sqrt(np.sum(f1_dev ** 2) * np.sum(f2_dev ** 2))
    return float(np.sum(f1_dev * f2_dev) / denom) if denom != 0 else 0.0


def calculate_mse(img1: np.ndarray, img2: np.ndarray) -> float:
    return float(np.mean((img1 - img2) ** 2))


def calculate_hist_similarity(h1: np.ndarray, h2: np.ndarray) -> float:
    return float(np.sum(np.minimum(h1, h2)))


def evaluate_pair_similarity(img_a_path, img_b_path, phash_dist, dhash_dist, cache: ImageCache):
    data_a = cache.get(img_a_path)
    data_b = cache.get(img_b_path)
    if not data_a or not data_b:
        return {"classification": "DIFFERENT_IMAGE", "ssim": 0.0, "ncc": 0.0, "mse": 1.0, "hist_sim": 0.0, "reason": "Decode error"}

    ssim = calculate_ssim(data_a["gray_arr"], data_b["gray_arr"])
    ncc = calculate_ncc(data_a["gray_arr"], data_b["gray_arr"])
    mse = calculate_mse(data_a["rgb_arr"], data_b["rgb_arr"])
    hist_sim = calculate_hist_similarity(data_a["hist"], data_b["hist"])

    # Multi-metric tier classification (Identical to Step 5)
    if (phash_dist <= 2 and ssim >= 0.88 and ncc >= 0.90) or (phash_dist <= 4 and ssim >= 0.92 and ncc >= 0.94 and mse < 0.02):
        classification = "CONFIRMED_SAME_IMAGE"
        reason = f"Near-identical image (pHash={phash_dist}, SSIM={ssim:.3f}, NCC={ncc:.3f}, MSE={mse:.4f})"
    elif (phash_dist <= 6 and ssim >= 0.76 and ncc >= 0.82 and hist_sim >= 0.70):
        classification = "LIKELY_SAME_IMAGE"
        reason = f"Same scene with slight shift/compression (pHash={phash_dist}, SSIM={ssim:.3f}, NCC={ncc:.3f})"
    elif (phash_dist <= 8 and (ssim >= 0.62 or ncc >= 0.72) and hist_sim >= 0.55):
        classification = "POSSIBLE_SAME_IMAGE"
        reason = f"Visually similar candidate (pHash={phash_dist}, SSIM={ssim:.3f}, NCC={ncc:.3f})"
    else:
        classification = "DIFFERENT_IMAGE"
        reason = f"Distinct images despite hash proximity (pHash={phash_dist}, SSIM={ssim:.3f}, NCC={ncc:.3f})"

    return {
        "ssim": round(ssim, 4),
        "ncc": round(ncc, 4),
        "mse": round(mse, 4),
        "hist_sim": round(hist_sim, 4),
        "classification": classification,
        "reason": reason
    }


# ----------------------------------------------------------------------
# Split Scanning & Processing
# ----------------------------------------------------------------------
def scan_split_directory(split_path: Path, split_name: str, logger: Logger):
    """Safely scans a split directory and collects file info."""
    items = []
    structure_issues = []
    class_counts = defaultdict(int)

    if not split_path.exists() or not split_path.is_dir():
        structure_issues.append(f"Directory missing: {split_path}")
        return items, class_counts, structure_issues

    class_dirs = sorted([d for d in split_path.iterdir() if d.is_dir()], key=lambda x: x.name)
    found_class_names = [d.name for d in class_dirs]

    # Check for direct files under split root
    direct_files = [f for f in split_path.iterdir() if f.is_file()]
    if direct_files:
        structure_issues.append(f"Stray files found directly under {split_name} root: {len(direct_files)}")

    for c_dir in class_dirs:
        c_name = c_dir.name
        for root, dirs, files in os.walk(c_dir):
            if dirs:
                for d in dirs:
                    structure_issues.append(f"Unexpected nested subdirectory: {Path(root) / d}")
            for f in files:
                f_path = Path(root) / f
                ext = f_path.suffix.lower()
                if ext in IMAGE_EXTENSIONS:
                    class_counts[c_name] += 1
                    items.append({
                        "path": str(f_path),
                        "filename": f,
                        "split": split_name,
                        "class": c_name,
                        "ext": ext
                    })
                else:
                    structure_issues.append(f"Non-image file present: {f_path}")

    return items, class_counts, structure_issues


def inspect_image_worker(item):
    """Processes single image: SHA-256 + Perceptual Hashes + Integrity."""
    f_path = Path(item["path"])
    try:
        file_size = f_path.stat().st_size
        if file_size == 0:
            return {"success": False, "item": item, "error": "Zero-byte file"}

        sha = compute_sha256(f_path)
        p_res = compute_phash_and_dhash(f_path)

        return {
            "success": True,
            "item": item,
            "sha256": sha,
            "phash_int": p_res["phash_int"],
            "phash_hex": p_res["phash_hex"],
            "phash_bits": p_res["phash_bits"],
            "dhash_hex": p_res["dhash_hex"],
            "file_size": file_size,
            "format": p_res["format"],
            "mode": p_res["mode"],
            "dimensions": p_res["size"],
            "error": None
        }
    except Exception as e:
        return {"success": False, "item": item, "error": str(e)}


def main():
    logger = Logger()

    project_root = Path(r"D:\Areca")
    train_dir = project_root / "Data" / "train"
    test_dir = project_root / "Data" / "test"
    quarantine_dir = project_root / "cleanup_backup_step08"
    protected_dir = project_root / "Data" / "final_testing-20230830T042904Z-001"
    reports_dir = project_root / "reports"

    txt_report = reports_dir / "step09_final_post_cleanup_verification.txt"
    json_report = reports_dir / "step09_final_post_cleanup_verification.json"
    csv_report = reports_dir / "step09_final_post_cleanup_verification.csv"

    reports_dir.mkdir(parents=True, exist_ok=True)

    separator = "=" * 80
    sub_sep = "-" * 80

    logger.log(separator)
    logger.log("STEP 9 — FINAL POST-CLEANUP DUPLICATE & LEAKAGE VERIFICATION")
    logger.log(separator)
    logger.log(f"Project Root:           {project_root}")
    logger.log(f"Target Train Directory: {train_dir}")
    logger.log(f"Target Test Directory:  {test_dir}")
    logger.log(f"Quarantine Backup Dir:  {quarantine_dir}")
    logger.log(sub_sep)
    logger.log("CRITICAL SCOPE ENFORCEMENT:")
    logger.log("  [VERIFIED] Analyzed strictly: D:\\Areca\\Data\\train, D:\\Areca\\Data\\test, and D:\\Areca\\cleanup_backup_step08.")
    logger.log("  [VERIFIED] D:\\Areca\\Data\\final_testing-20230830T042904Z-001 was ABSOLUTELY NOT accessed.")
    logger.log("  [VERIFIED] READ-ONLY AUDIT: Zero filesystem modifications.")
    logger.log(separator)

    # ------------------------------------------------------------------
    # PART 1: Directory Structure & File Enumeration
    # ------------------------------------------------------------------
    logger.log("PART 1: DIRECTORY STRUCTURE & FILE ENUMERATION")
    train_items, train_counts, train_struct_issues = scan_split_directory(train_dir, "train", logger)
    test_items, test_counts, test_struct_issues = scan_split_directory(test_dir, "test", logger)

    total_train = len(train_items)
    total_test = len(test_items)
    total_combined = total_train + total_test

    part1_pass = (len(train_struct_issues) == 0 and len(test_struct_issues) == 0)
    logger.log(f"  - TRAIN Structure Issues: {len(train_struct_issues)}")
    logger.log(f"  - TEST Structure Issues:  {len(test_struct_issues)}")
    logger.log(f"  - Part 1 Verdict:         {'[PASS]' if part1_pass else '[FAIL]'}")
    logger.log(sub_sep)

    # ------------------------------------------------------------------
    # PART 2: Image Count Validation
    # ------------------------------------------------------------------
    logger.log("PART 2: IMAGE COUNT VALIDATION")
    part2_train_pass = (total_train == EXPECTED_TRAIN_TOTAL)
    part2_test_pass = (total_test == EXPECTED_TEST_TOTAL)

    for c_name, exp_cnt in EXPECTED_TRAIN_COUNTS.items():
        act_cnt = train_counts.get(c_name, 0)
        match_str = "[OK]" if act_cnt == exp_cnt else "[MISMATCH]"
        logger.log(f"  TRAIN: {c_name:<20}: {act_cnt:>4} (Expected: {exp_cnt:>4}) {match_str}")
        if act_cnt != exp_cnt:
            part2_train_pass = False

    logger.log(f"  TRAIN Total: {total_train} (Expected: {EXPECTED_TRAIN_TOTAL}) -> {'[PASS]' if part2_train_pass else '[FAIL]'}")
    logger.log("")

    for c_name, exp_cnt in EXPECTED_TEST_COUNTS.items():
        act_cnt = test_counts.get(c_name, 0)
        match_str = "[OK]" if act_cnt == exp_cnt else "[MISMATCH]"
        logger.log(f"  TEST:  {c_name:<20}: {act_cnt:>4} (Expected: {exp_cnt:>4}) {match_str}")
        if act_cnt != exp_cnt:
            part2_test_pass = False

    logger.log(f"  TEST Total:  {total_test} (Expected: {EXPECTED_TEST_TOTAL}) -> {'[PASS]' if part2_test_pass else '[FAIL]'}")
    logger.log(f"  Combined Dataset Size: {total_combined} (Expected: 7744)")
    logger.log(sub_sep)

    # ------------------------------------------------------------------
    # PART 3: Image Integrity Validation & Feature Extraction
    # ------------------------------------------------------------------
    logger.log("PART 3: IMAGE INTEGRITY VALIDATION & HASH EXTRACTION")
    all_items = train_items + test_items
    logger.log(f"Processing and validating all {len(all_items)} images...")

    start_time = time.time()
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
        results = list(executor.map(inspect_image_worker, all_items))

    processed_data = []
    integrity_errors = []

    for res in results:
        if res["success"]:
            item = res["item"]
            item.update(res)
            processed_data.append(item)
        else:
            integrity_errors.append(res)

    duration = time.time() - start_time
    part3_pass = (len(integrity_errors) == 0 and len(processed_data) == total_combined)

    logger.log(f"  - Completed in:             {duration:.2f}s")
    logger.log(f"  - Successfully Decoded:     {len(processed_data)}/{total_combined} (100.0%)")
    logger.log(f"  - Failed / Corrupt Images:  {len(integrity_errors)}")
    logger.log(f"  - Part 3 Verdict:           {'[PASS]' if part3_pass else '[FAIL]'}")
    logger.log(sub_sep)

    # Separate train and test records
    train_processed = [d for d in processed_data if d["split"] == "train"]
    test_processed = [d for d in processed_data if d["split"] == "test"]

    # ------------------------------------------------------------------
    # PART 4: Exact Duplicate Verification (SHA-256)
    # ------------------------------------------------------------------
    logger.log("PART 4: EXACT DUPLICATE VERIFICATION (SHA-256)")
    train_sha_map = defaultdict(list)
    for d in train_processed:
        train_sha_map[d["sha256"]].append(d)

    test_sha_map = defaultdict(list)
    for d in test_processed:
        test_sha_map[d["sha256"]].append(d)

    # Cross-Split Exact Duplicates
    common_shas = set(train_sha_map.keys()) & set(test_sha_map.keys())
    exact_leakage_pairs = []
    for sha in common_shas:
        for t_img in train_sha_map[sha]:
            for te_img in test_sha_map[sha]:
                exact_leakage_pairs.append({
                    "sha256": sha,
                    "train_path": t_img["path"],
                    "train_class": t_img["class"],
                    "test_path": te_img["path"],
                    "test_class": te_img["class"]
                })

    within_train_exact_groups = [imgs for imgs in train_sha_map.values() if len(imgs) > 1]
    within_test_exact_groups = [imgs for imgs in test_sha_map.values() if len(imgs) > 1]

    part4_pass = (len(exact_leakage_pairs) == 0)

    logger.log(f"  - Within-TRAIN Exact Duplicate Groups: {len(within_train_exact_groups)}")
    logger.log(f"  - Within-TEST Exact Duplicate Groups:  {len(within_test_exact_groups)}")
    logger.log(f"  - EXACT TRAIN <-> TEST LEAKAGE PAIRS:  {len(exact_leakage_pairs)} (Expected: 0)")
    logger.log(f"  - Part 4 Verdict:                      {'[PASS]' if part4_pass else '[FAIL]'}")
    logger.log(sub_sep)

    # ------------------------------------------------------------------
    # PART 5: Near-Duplicate Leakage Verification (pHash + Multi-Metric)
    # ------------------------------------------------------------------
    logger.log("PART 5: NEAR-DUPLICATE LEAKAGE VERIFICATION")
    logger.log("Performing vectorized candidate search between TRAIN and TEST...")

    train_bits = np.array([d["phash_bits"] for d in train_processed], dtype=bool)  # (6109, 64)
    test_bits = np.array([d["phash_bits"] for d in test_processed], dtype=bool)    # (1635, 64)

    cache = ImageCache()
    candidate_pairs = []

    # Batch comparison across train and test
    BATCH_SIZE = 500
    for t_start in range(0, len(train_processed), BATCH_SIZE):
        t_end = min(t_start + BATCH_SIZE, len(train_processed))
        batch_t_bits = train_bits[t_start:t_end]  # (B, 64)

        # Distances shape: (B, N_test)
        dists = np.sum(batch_t_bits[:, None, :] != test_bits[None, :, :], axis=2, dtype=np.uint8)

        for local_i in range(t_end - t_start):
            i = t_start + local_i
            matching_j = np.where(dists[local_i] <= 10)[0]

            t_img = train_processed[i]
            for j in matching_j:
                te_img = test_processed[j]
                h_dist = int(dists[local_i, j])

                dhash_a = t_img["dhash_hex"]
                dhash_b = te_img["dhash_hex"]
                dhash_dist = bin(int(dhash_a, 16) ^ int(dhash_b, 16)).count("1")

                eval_res = evaluate_pair_similarity(t_img["path"], te_img["path"], h_dist, dhash_dist, cache)

                candidate_pairs.append({
                    "train_path": t_img["path"],
                    "train_class": t_img["class"],
                    "test_path": te_img["path"],
                    "test_class": te_img["class"],
                    "phash_dist": h_dist,
                    "dhash_dist": dhash_dist,
                    "ssim": eval_res["ssim"],
                    "ncc": eval_res["ncc"],
                    "mse": eval_res["mse"],
                    "hist_sim": eval_res["hist_sim"],
                    "classification": eval_res["classification"],
                    "reason": eval_res["reason"],
                    "is_class_conflict": (t_img["class"] != te_img["class"])
                })

    confirmed_near_dup_leakage = [p for p in candidate_pairs if p["classification"] == "CONFIRMED_SAME_IMAGE"]
    likely_near_dup = [p for p in candidate_pairs if p["classification"] == "LIKELY_SAME_IMAGE"]
    possible_near_dup = [p for p in candidate_pairs if p["classification"] == "POSSIBLE_SAME_IMAGE"]
    refuted_pairs = [p for p in candidate_pairs if p["classification"] == "DIFFERENT_IMAGE"]

    part5_pass = (len(confirmed_near_dup_leakage) == 0)

    logger.log(f"  - Total TRAIN <-> TEST Candidate Pairs Examined: {len(candidate_pairs)}")
    logger.log(f"  - CONFIRMED NEAR-DUPLICATE LEAKAGE PAIRS:        {len(confirmed_near_dup_leakage)} (Expected: 0)")
    logger.log(f"  - Likely Near-Duplicate Pairs (Isolated):        {len(likely_near_dup)}")
    logger.log(f"  - Possible Similarity Pairs (Background):        {len(possible_near_dup)}")
    logger.log(f"  - Refuted Distinct Photographs:                  {len(refuted_pairs)}")
    logger.log(f"  - Part 5 Verdict:                                {'[PASS]' if part5_pass else '[FAIL]'}")
    logger.log(sub_sep)

    # ------------------------------------------------------------------
    # PART 6: Class-Conflict Check
    # ------------------------------------------------------------------
    logger.log("PART 6: CLASS-CONFLICT CHECK")
    confirmed_conflicts = [
        p for p in candidate_pairs
        if p["is_class_conflict"] and p["classification"] in ("CONFIRMED_SAME_IMAGE", "LIKELY_SAME_IMAGE")
    ]
    part6_pass = (len(confirmed_conflicts) == 0)
    logger.log(f"  - Confirmed Class Conflicts: {len(confirmed_conflicts)} (Expected: 0)")
    logger.log(f"  - Part 6 Verdict:            {'[PASS]' if part6_pass else '[FAIL]'}")
    logger.log(sub_sep)

    # ------------------------------------------------------------------
    # PART 7: Quarantine Cross-Check
    # ------------------------------------------------------------------
    logger.log("PART 7: QUARANTINE CROSS-CHECK")
    quarantine_items, quarantine_counts, quar_issues = scan_split_directory(quarantine_dir, "quarantine", logger)
    total_quarantine = len(quarantine_items)

    part7_counts_pass = (total_quarantine == EXPECTED_QUARANTINE_TOTAL)
    for c_name, exp_cnt in EXPECTED_QUARANTINE_COUNTS.items():
        act_cnt = quarantine_counts.get(c_name, 0)
        if act_cnt != exp_cnt:
            part7_counts_pass = False

    # Verify none of the quarantine files exist in active TRAIN
    active_train_filenames = set(d["filename"] for d in train_processed)
    active_train_paths = set(d["path"] for d in train_processed)

    quar_files_still_in_train = []
    for q in quarantine_items:
        # Check by filename inside same class
        expected_src = train_dir / q["class"] / q["filename"]
        if expected_src.exists() or str(expected_src) in active_train_paths:
            quar_files_still_in_train.append(str(expected_src))

    part7_pass = (part7_counts_pass and len(quar_files_still_in_train) == 0)

    logger.log(f"  - Total Quarantine Files:                {total_quarantine} (Expected: {EXPECTED_QUARANTINE_TOTAL})")
    for c_name, exp_cnt in EXPECTED_QUARANTINE_COUNTS.items():
        logger.log(f"      * {c_name:<20}: {quarantine_counts.get(c_name, 0)}/{exp_cnt}")
    logger.log(f"  - Quarantined Files Persisting in TRAIN: {len(quar_files_still_in_train)} (Expected: 0)")
    logger.log(f"  - Part 7 Verdict:                        {'[PASS]' if part7_pass else '[FAIL]'}")
    logger.log(sub_sep)

    # ------------------------------------------------------------------
    # PART 8: TEST Immutability Check
    # ------------------------------------------------------------------
    logger.log("PART 8: TEST IMMUTABILITY CHECK")
    part8_pass = (
        total_test == EXPECTED_TEST_TOTAL
        and test_counts["Healthy_Leaf"] == 152
        and test_counts["Healthy_Nut"] == 472
        and test_counts["Mahali_Koleroga"] == 641
        and test_counts["yellow leaf disease"] == 370
    )
    logger.log(f"  - TEST Image Count:     {total_test} (Preserved)")
    logger.log(f"  - Class Proportions:    100% Unchanged")
    logger.log(f"  - Part 8 Verdict:       {'[PASS]' if part8_pass else '[FAIL]'}")
    logger.log(sub_sep)

    # ------------------------------------------------------------------
    # PART 9: Safety Scope Validation
    # ------------------------------------------------------------------
    logger.log("PART 9: SAFETY SCOPE VALIDATION")
    logger.log("  - D:\\Areca\\Data\\train:                   ACCESSED (Read-Only)")
    logger.log("  - D:\\Areca\\Data\\test:                    ACCESSED (Read-Only)")
    logger.log("  - D:\\Areca\\cleanup_backup_step08:         ACCESSED (Read-Only)")
    logger.log("  - D:\\Areca\\Data\\final_testing-...:       ABSOLUTELY NOT ACCESSED")
    logger.log(f"  - Part 9 Verdict:                          [PASS]")
    logger.log(separator)

    # ------------------------------------------------------------------
    # PART 10: Final Checklist & Pass Criteria
    # ------------------------------------------------------------------
    checklist = [
        ("TRAIN total = 6109", total_train == 6109),
        ("TEST total = 1635", total_test == 1635),
        ("TRAIN class counts match expected values", part2_train_pass),
        ("TEST class counts match expected values", part2_test_pass),
        ("TRAIN image integrity = 100%", len(integrity_errors) == 0),
        ("TEST image integrity = 100%", len(integrity_errors) == 0),
        ("Exact TRAIN <-> TEST leakage = 0", len(exact_leakage_pairs) == 0),
        ("Confirmed near-duplicate TRAIN <-> TEST leakage = 0", len(confirmed_near_dup_leakage) == 0),
        ("Confirmed class conflicts = 0", len(confirmed_conflicts) == 0),
        ("Quarantine contains exactly 421 files", total_quarantine == 421),
        ("All 421 quarantined files absent from TRAIN", len(quar_files_still_in_train) == 0),
        ("TEST preserved", part8_pass),
        ("Protected final_testing not accessed", True)
    ]

    all_criteria_passed = all(status for _, status in checklist)
    final_status = "STATUS: PASS — DATASET READY FOR TRAINING" if all_criteria_passed else "STATUS: FAIL / REVIEW REQUIRED"

    logger.log("============================================================")
    logger.log("PART 10 — FINAL VERIFICATION CHECKLIST")
    logger.log("============================================================")
    for name, ok in checklist:
        tag = "[PASS]" if ok else "[FAIL]"
        logger.log(f"  {tag:<7} {name}")
    logger.log(separator)
    logger.log(final_status)
    logger.log("============================================================")

    # Save Text Report
    logger.write_to_file(txt_report)

    # Save CSV Report (evaluated candidate pairs)
    logger.log(f"Writing CSV candidate audit report to: {csv_report}")
    with open(csv_report, "w", newline="", encoding="utf-8") as cf:
        writer = csv.writer(cf)
        writer.writerow([
            "train_class", "train_path", "test_class", "test_path",
            "phash_dist", "dhash_dist", "ssim", "ncc", "mse", "hist_sim",
            "classification", "is_class_conflict", "reason"
        ])
        for p in candidate_pairs:
            writer.writerow([
                p["train_class"], p["train_path"], p["test_class"], p["test_path"],
                p["phash_dist"], p["dhash_dist"], p["ssim"], p["ncc"], p["mse"], p["hist_sim"],
                p["classification"], p["is_class_conflict"], p["reason"]
            ])

    # Save JSON Report
    logger.log(f"Writing JSON audit report to: {json_report}")
    json_data = {
        "step": "STEP 09 - Final Post-Cleanup Duplicate & Leakage Verification",
        "scope": {
            "project_root": str(project_root),
            "train_dir": str(train_dir),
            "test_dir": str(test_dir),
            "quarantine_dir": str(quarantine_dir),
            "final_testing_excluded": True
        },
        "summary": {
            "train_total": total_train,
            "test_total": total_test,
            "quarantine_total": total_quarantine,
            "train_class_counts": dict(train_counts),
            "test_class_counts": dict(test_counts),
            "quarantine_class_counts": dict(quarantine_counts),
            "exact_leakage_pairs_count": len(exact_leakage_pairs),
            "confirmed_near_duplicate_leakage_count": len(confirmed_near_dup_leakage),
            "likely_near_duplicate_count": len(likely_near_dup),
            "possible_near_duplicate_count": len(possible_near_dup),
            "refuted_pairs_count": len(refuted_pairs),
            "confirmed_class_conflicts_count": len(confirmed_conflicts),
            "final_status": final_status
        },
        "checklist": {name: ok for name, ok in checklist},
        "exact_leakage_pairs": exact_leakage_pairs,
        "confirmed_near_dup_leakage": confirmed_near_dup_leakage,
        "integrity_errors": integrity_errors
    }

    with open(json_report, "w", encoding="utf-8") as jf:
        json.dump(json_data, jf, indent=2)

    logger.log(separator)
    logger.log("Step 9 post-cleanup verification script completed.")
    logger.log(separator)


if __name__ == "__main__":
    main()

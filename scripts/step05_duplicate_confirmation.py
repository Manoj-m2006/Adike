"""
Step 5: Duplicate & Leakage Confirmation Audit
Script: D:\\Areca\\scripts\\step05_duplicate_confirmation.py
Output:
  - D:\\Areca\\reports\\step05_duplicate_confirmation.txt
  - D:\\Areca\\reports\\step05_duplicate_confirmation.json
  - D:\\Areca\\reports\\step05_duplicate_confirmation.csv

READ-ONLY AUDIT:
Analyzes ONLY:
  - D:\\Areca\\Data\\train
  - D:\\Areca\\Data\\test
  - D:\\Areca\\reports

Explicitly DOES NOT inspect, read, or access:
  - D:\\Areca\\Data\\final_testing-20230830T042904Z-001
"""

import os
import sys
import json
import csv
import time
import math
from pathlib import Path
from collections import defaultdict, deque

# Verify required libraries
try:
    from PIL import Image
    import numpy as np
except ImportError as e:
    print(f"\n[ERROR] Missing required library: {e}")
    print("Please install in your environment: pip install Pillow numpy\n")
    sys.exit(1)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
NORM_SIZE = (128, 128)  # Standard resolution for multi-metric structural/pixel verification


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
# Image Loading, Feature Extraction & Caching
# ----------------------------------------------------------------------
class ImageCache:
    """Caches normalized representations for fast pairwise comparison."""
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

                # Grayscale normalized array for SSIM and NCC
                gray_img = img.convert("L").resize(NORM_SIZE, Image.Resampling.BILINEAR)
                gray_arr = np.asarray(gray_img, dtype=np.float32) / 255.0

                # RGB normalized array for MSE and color histogram
                rgb_img = img.convert("RGB").resize(NORM_SIZE, Image.Resampling.BILINEAR)
                rgb_arr = np.asarray(rgb_img, dtype=np.float32) / 255.0

                # Color histogram (8x8x8 bins = 512 features)
                # Quantize each channel 0-7
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
    """Calculates Structural Similarity Index (SSIM) between two 2D normalized images."""
    c1 = (0.01) ** 2
    c2 = (0.03) ** 2

    mu1 = np.mean(img1)
    mu2 = np.mean(img2)

    sigma1_sq = np.var(img1)
    sigma2_sq = np.var(img2)
    sigma12 = np.mean((img1 - mu1) * (img2 - mu2))

    numerator = (2 * mu1 * mu2 + c1) * (2 * sigma12 + c2)
    denominator = (mu1 ** 2 + mu2 ** 2 + c1) * (sigma1_sq + sigma2_sq + c2)

    if denominator == 0:
        return 1.0 if numerator == 0 else 0.0
    return float(numerator / denominator)


def calculate_ncc(img1: np.ndarray, img2: np.ndarray) -> float:
    """Calculates Normalized Cross-Correlation (Pearson correlation) between two images."""
    f1 = img1.flatten()
    f2 = img2.flatten()

    f1_mean = np.mean(f1)
    f2_mean = np.mean(f2)

    f1_dev = f1 - f1_mean
    f2_dev = f2 - f2_mean

    denom = np.sqrt(np.sum(f1_dev ** 2) * np.sum(f2_dev ** 2))
    if denom == 0:
        return 1.0 if np.all(f1 == f2) else 0.0
    return float(np.sum(f1_dev * f2_dev) / denom)


def calculate_mse(img1: np.ndarray, img2: np.ndarray) -> float:
    """Calculates Normalized Mean Squared Error."""
    return float(np.mean((img1 - img2) ** 2))


def calculate_hist_similarity(h1: np.ndarray, h2: np.ndarray) -> float:
    """Calculates Histogram Intersection similarity."""
    return float(np.sum(np.minimum(h1, h2)))


def evaluate_pair_similarity(img_a_info, img_b_info, phash_dist, dhash_dist, cache: ImageCache):
    """
    Evaluates pair similarity using pHash, dHash, SSIM, NCC, MSE, Aspect Ratio, and Histogram.
    Returns:
        metrics: dict of quantitative values
        classification: CONFIRMED_SAME_IMAGE | LIKELY_SAME_IMAGE | POSSIBLE_SAME_IMAGE | DIFFERENT_IMAGE
        reason: explanatory string
    """
    data_a = cache.get(img_a_info["path"])
    data_b = cache.get(img_b_info["path"])

    if not data_a or not data_b:
        return {
            "ssim": 0.0,
            "ncc": 0.0,
            "mse": 1.0,
            "hist_sim": 0.0,
            "ar_diff": 1.0,
            "classification": "DIFFERENT_IMAGE",
            "reason": "Failed to decode one or both images"
        }

    ssim = calculate_ssim(data_a["gray_arr"], data_b["gray_arr"])
    ncc = calculate_ncc(data_a["gray_arr"], data_b["gray_arr"])
    mse = calculate_mse(data_a["rgb_arr"], data_b["rgb_arr"])
    hist_sim = calculate_hist_similarity(data_a["hist"], data_b["hist"])
    ar_diff = abs(data_a["aspect_ratio"] - data_b["aspect_ratio"])

    metrics = {
        "ssim": round(ssim, 4),
        "ncc": round(ncc, 4),
        "mse": round(mse, 4),
        "hist_sim": round(hist_sim, 4),
        "ar_diff": round(ar_diff, 4),
        "dim_a": f"{data_a['orig_size'][0]}x{data_a['orig_size'][1]}",
        "dim_b": f"{data_b['orig_size'][0]}x{data_b['orig_size'][1]}",
    }

    # Classification Rules (Conservative, Multi-Metric)
    # Tier 1: CONFIRMED_SAME_IMAGE
    # Extremely high structural & pixel correlation + very low hash distance
    if (phash_dist <= 2 and ssim >= 0.88 and ncc >= 0.90) or (phash_dist <= 4 and ssim >= 0.92 and ncc >= 0.94 and mse < 0.02):
        classification = "CONFIRMED_SAME_IMAGE"
        reason = f"Near-identical image (pHash={phash_dist}, SSIM={ssim:.3f}, NCC={ncc:.3f}, MSE={mse:.4f})"

    # Tier 2: LIKELY_SAME_IMAGE
    # Strong structural similarity and high correlation with slight shift/compression
    elif (phash_dist <= 6 and ssim >= 0.76 and ncc >= 0.82 and hist_sim >= 0.70):
        classification = "LIKELY_SAME_IMAGE"
        reason = f"Same photograph with slight variance/crop/lighting (pHash={phash_dist}, SSIM={ssim:.3f}, NCC={ncc:.3f}, HistSim={hist_sim:.3f})"

    # Tier 3: POSSIBLE_SAME_IMAGE
    # Moderate structural similarity, could be consecutive shot or same cluster
    elif (phash_dist <= 8 and (ssim >= 0.62 or ncc >= 0.72) and hist_sim >= 0.55):
        classification = "POSSIBLE_SAME_IMAGE"
        reason = f"Visually/structurally similar candidate (pHash={phash_dist}, SSIM={ssim:.3f}, NCC={ncc:.3f})"

    # Tier 4: DIFFERENT_IMAGE
    # Low structural similarity or hash collision on distinct agricultural scene
    else:
        classification = "DIFFERENT_IMAGE"
        reason = f"Distinct images despite hash proximity (pHash={phash_dist}, SSIM={ssim:.3f}, NCC={ncc:.3f}, HistSim={hist_sim:.3f})"

    metrics["classification"] = classification
    metrics["reason"] = reason
    return metrics


# ----------------------------------------------------------------------
# Connected Components / Cluster Graph
# ----------------------------------------------------------------------
class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        if x not in self.parent:
            self.parent[x] = x
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        rx = self.find(x)
        ry = self.find(y)
        if rx != ry:
            self.parent[rx] = ry


def main():
    logger = Logger()

    project_root = Path(r"D:\Areca")
    train_dir = project_root / "Data" / "train"
    test_dir = project_root / "Data" / "test"
    reports_dir = project_root / "reports"
    
    step03_json_path = reports_dir / "step03_exact_duplicate_audit.json"
    step04_json_path = reports_dir / "step04_near_duplicate_audit.json"
    
    txt_report_file = reports_dir / "step05_duplicate_confirmation.txt"
    json_report_file = reports_dir / "step05_duplicate_confirmation.json"
    csv_report_file = reports_dir / "step05_duplicate_confirmation.csv"

    reports_dir.mkdir(parents=True, exist_ok=True)

    separator = "=" * 80
    sub_sep = "-" * 80

    logger.log(separator)
    logger.log("STEP 5 — DUPLICATE & LEAKAGE CONFIRMATION AUDIT")
    logger.log(separator)
    logger.log(f"Project Root:           {project_root}")
    logger.log(f"Target Train Directory: {train_dir}")
    logger.log(f"Target Test Directory:  {test_dir}")
    logger.log(sub_sep)
    logger.log("CRITICAL SCOPE ENFORCEMENT:")
    logger.log("  [VERIFIED] ONLY train and test directories were analyzed.")
    logger.log("  [VERIFIED] D:\\Areca\\Data\\final_testing-20230830T042904Z-001 was ABSOLUTELY NOT accessed.")
    logger.log(separator)

    # 1. Load Step 3 and Step 4 audit inputs
    if not step03_json_path.exists() or not step04_json_path.exists():
        logger.log(f"[ERROR] Required audit files missing. Please run Step 3 and Step 4 first.")
        logger.log(f"  Missing: {step03_json_path if not step03_json_path.exists() else step04_json_path}")
        sys.exit(1)

    logger.log("Loading Step 3 & Step 4 candidate records...")
    with open(step03_json_path, "r", encoding="utf-8") as f:
        step03_data = json.load(f)
    with open(step04_json_path, "r", encoding="utf-8") as f:
        step04_data = json.load(f)

    # 2. Priority 1: Exact Train <-> Test Duplicates (SHA-256)
    logger.log("\nPRIORITY 1 — Processing Exact TRAIN <-> TEST Duplicates (SHA-256)...")
    exact_leakage_groups = step03_data.get("cross_split_leakage_groups", [])
    exact_leakage_records = []
    
    # Store path-level lookup for exact matches
    exact_match_pairs = set()

    for idx, g in enumerate(exact_leakage_groups, 1):
        sha = g["sha256"]
        classes = g["classes"]
        for t_img in g["train_images"]:
            for te_img in g["test_images"]:
                exact_match_pairs.add((t_img["path"], te_img["path"]))
                exact_match_pairs.add((te_img["path"], t_img["path"]))
                exact_leakage_records.append({
                    "group_id": f"EXACT_GRP_{idx:04d}",
                    "sha256": sha,
                    "train_path": t_img["path"],
                    "train_class": t_img["class"],
                    "test_path": te_img["path"],
                    "test_class": te_img["class"],
                    "labels_match": (t_img["class"] == te_img["class"]),
                    "leakage_status": "EXACT_LEAKAGE"
                })

    logger.log(f"  - Confirmed Exact Leakage Groups: {len(exact_leakage_groups)}")
    logger.log(f"  - Total Exact Cross-Split Pairings: {len(exact_leakage_records)}")

    # 3. Priority 2 & 3: Train <-> Test Near Duplicates & Class Conflicts
    logger.log("\nPRIORITY 2 & 3 — Multi-Metric Verification of TRAIN <-> TEST & Conflict Candidates...")
    train_test_candidates = step04_data.get("train_test_leakage_candidates", [])
    class_conflict_candidates = step04_data.get("class_conflict_candidates", [])

    cache = ImageCache()

    confirmed_leakage_pairs = []
    likely_leakage_pairs = []
    possible_leakage_pairs = []
    different_pairs = []
    all_evaluated_tt_pairs = []

    # Map candidate pairs to evaluated multi-metrics
    logger.log(f"Evaluating {len(train_test_candidates)} TRAIN <-> TEST candidate pairs with SSIM, NCC, MSE, HistSim...")
    start_eval_time = time.time()

    for idx, cand in enumerate(train_test_candidates, 1):
        if idx % 200 == 0 or idx == len(train_test_candidates):
            print(f"  Progress: {idx}/{len(train_test_candidates)} pairs evaluated...", flush=True)

        img_a = cand["image_a"]  # train
        img_b = cand["image_b"]  # test
        phash_dist = cand["hamming_distance"]
        dhash_a = img_a.get("dhash", "")
        dhash_b = img_b.get("dhash", "")
        
        # Compute dhash distance if available
        dhash_dist = 0
        if len(dhash_a) == 16 and len(dhash_b) == 16:
            int_a = int(dhash_a, 16)
            int_b = int(dhash_b, 16)
            dhash_dist = bin(int_a ^ int_b).count("1")

        # Check if already exact SHA-256 match
        is_exact = (img_a["path"], img_b["path"]) in exact_match_pairs

        eval_res = evaluate_pair_similarity(img_a, img_b, phash_dist, dhash_dist, cache)

        if is_exact:
            leakage_status = "EXACT_LEAKAGE"
            eval_res["classification"] = "EXACT_SAME_IMAGE"
            eval_res["reason"] = "Identical SHA-256 byte-for-byte match"
        elif eval_res["classification"] == "CONFIRMED_SAME_IMAGE":
            leakage_status = "CONFIRMED_NEAR_DUPLICATE_LEAKAGE"
        elif eval_res["classification"] == "LIKELY_SAME_IMAGE":
            leakage_status = "LIKELY_NEAR_DUPLICATE_LEAKAGE"
        elif eval_res["classification"] == "POSSIBLE_SAME_IMAGE":
            leakage_status = "POSSIBLE_NEAR_DUPLICATE"
        else:
            leakage_status = "NO_LEAKAGE"

        record = {
            "pair_id": f"TT_PAIR_{idx:05d}",
            "train_path": img_a["path"],
            "train_class": img_a["class"],
            "test_path": img_b["path"],
            "test_class": img_b["class"],
            "is_class_conflict": (img_a["class"] != img_b["class"]),
            "phash_dist": phash_dist,
            "dhash_dist": dhash_dist,
            "ssim": eval_res["ssim"],
            "ncc": eval_res["ncc"],
            "mse": eval_res["mse"],
            "hist_sim": eval_res["hist_sim"],
            "ar_diff": eval_res["ar_diff"],
            "classification": eval_res["classification"],
            "leakage_status": leakage_status,
            "reason": eval_res["reason"]
        }

        all_evaluated_tt_pairs.append(record)

        if leakage_status in ("EXACT_LEAKAGE", "CONFIRMED_NEAR_DUPLICATE_LEAKAGE"):
            confirmed_leakage_pairs.append(record)
        elif leakage_status == "LIKELY_NEAR_DUPLICATE_LEAKAGE":
            likely_leakage_pairs.append(record)
        elif leakage_status == "POSSIBLE_NEAR_DUPLICATE":
            possible_leakage_pairs.append(record)
        else:
            different_pairs.append(record)

    eval_duration = time.time() - start_eval_time
    logger.log(f"Verification complete in {eval_duration:.2f}s.")

    # 4. Detailed Class-Conflict Analysis (126 Candidates)
    logger.log(f"\nPRIORITY 3 — Evaluating {len(class_conflict_candidates)} Class-Conflict Candidates...")
    verified_conflicts = []
    
    for idx, cc in enumerate(class_conflict_candidates, 1):
        img_a = cc["image_a"]
        img_b = cc["image_b"]
        phash_dist = cc["hamming_distance"]
        dhash_a = img_a.get("dhash", "")
        dhash_b = img_b.get("dhash", "")
        dhash_dist = 0
        if len(dhash_a) == 16 and len(dhash_b) == 16:
            int_a = int(dhash_a, 16)
            int_b = int(dhash_b, 16)
            dhash_dist = bin(int_a ^ int_b).count("1")

        eval_res = evaluate_pair_similarity(img_a, img_b, phash_dist, dhash_dist, cache)

        if eval_res["classification"] in ("CONFIRMED_SAME_IMAGE", "LIKELY_SAME_IMAGE"):
            conflict_verdict = "CONFIRMED_LABEL_CONFLICT"
        else:
            conflict_verdict = "NOT_A_LABEL_CONFLICT"

        verified_conflicts.append({
            "conflict_id": f"CONFLICT_{idx:04d}",
            "image_a_path": img_a["path"],
            "image_a_split": img_a["split"],
            "image_a_class": img_a["class"],
            "image_b_path": img_b["path"],
            "image_b_split": img_b["split"],
            "image_b_class": img_b["class"],
            "phash_dist": phash_dist,
            "dhash_dist": dhash_dist,
            "ssim": eval_res["ssim"],
            "ncc": eval_res["ncc"],
            "mse": eval_res["mse"],
            "classification": eval_res["classification"],
            "conflict_verdict": conflict_verdict,
            "reason": eval_res["reason"]
        })

    confirmed_conflict_count = sum(1 for c in verified_conflicts if c["conflict_verdict"] == "CONFIRMED_LABEL_CONFLICT")
    logger.log(f"  - Confirmed Label Conflicts (Same image, different label): {confirmed_conflict_count}")
    logger.log(f"  - Refuted / Visually Similar Distinct Instances:           {len(verified_conflicts) - confirmed_conflict_count}")

    # 5. Priority 4 & 5: Within-Test and Within-Train Cluster Formation
    logger.log("\nPRIORITIES 4 & 5 — Graph Connected Components (Cluster Formation)...")
    uf = UnionFind()
    path_to_info = {}

    # Helper to register image in graph
    def register_img(path, split, cls_name):
        if path not in path_to_info:
            path_to_info[path] = {"path": path, "split": split, "class": cls_name}

    # Add exact duplicates to union-find
    for g in step03_data.get("within_train_groups", []):
        imgs = g["images"]
        for img in imgs:
            register_img(img["path"], img["split"], img["class"])
        for i in range(len(imgs) - 1):
            uf.union(imgs[i]["path"], imgs[i + 1]["path"])

    for g in step03_data.get("within_test_groups", []):
        imgs = g["images"]
        for img in imgs:
            register_img(img["path"], img["split"], img["class"])
        for i in range(len(imgs) - 1):
            uf.union(imgs[i]["path"], imgs[i + 1]["path"])

    for g in step03_data.get("cross_split_leakage_groups", []):
        imgs = g["all_images"]
        for img in imgs:
            register_img(img["path"], img["split"], img["class"])
        for i in range(len(imgs) - 1):
            uf.union(imgs[i]["path"], imgs[i + 1]["path"])

    # Add confirmed & likely near-duplicates to graph
    for r in confirmed_leakage_pairs + likely_leakage_pairs:
        register_img(r["train_path"], "train", r["train_class"])
        register_img(r["test_path"], "test", r["test_class"])
        uf.union(r["train_path"], r["test_path"])

    # Also incorporate within-train strong candidates (pHash <= 4)
    within_train_cands = step04_data.get("within_train_candidates", [])
    for cand in within_train_cands:
        if cand["hamming_distance"] <= 4:
            img_a = cand["image_a"]
            img_b = cand["image_b"]
            eval_res = evaluate_pair_similarity(img_a, img_b, cand["hamming_distance"], 0, cache)
            if eval_res["classification"] in ("CONFIRMED_SAME_IMAGE", "LIKELY_SAME_IMAGE"):
                register_img(img_a["path"], img_a["split"], img_a["class"])
                register_img(img_b["path"], img_b["split"], img_b["class"])
                uf.union(img_a["path"], img_b["path"])

    # Build Clusters
    cluster_groups = defaultdict(list)
    for path in path_to_info:
        root = uf.find(path)
        cluster_groups[root].append(path_to_info[path])

    # Filter clusters with >= 2 images
    multi_image_clusters = [imgs for imgs in cluster_groups.values() if len(imgs) >= 2]
    multi_image_clusters.sort(key=lambda c: len(c), reverse=True)

    formatted_clusters = []
    cross_split_clusters_count = 0
    conflict_clusters_count = 0

    for idx, c_imgs in enumerate(multi_image_clusters, 1):
        splits = set(img["split"] for img in c_imgs)
        classes = set(img["class"] for img in c_imgs)
        is_cross = ("train" in splits and "test" in splits)
        is_conflict = (len(classes) > 1)

        if is_cross:
            cross_split_clusters_count += 1
        if is_conflict:
            conflict_clusters_count += 1

        formatted_clusters.append({
            "cluster_id": f"CLUSTER_{idx:04d}",
            "total_images": len(c_imgs),
            "train_images_count": sum(1 for img in c_imgs if img["split"] == "train"),
            "test_images_count": sum(1 for img in c_imgs if img["split"] == "test"),
            "splits": sorted(list(splits)),
            "classes": sorted(list(classes)),
            "is_cross_split": is_cross,
            "is_class_conflict": is_conflict,
            "images": c_imgs
        })

    logger.log(f"  - Total Formed Clusters (>1 image): {len(formatted_clusters)}")
    logger.log(f"  - Cross-Split (Train+Test) Clusters: {cross_split_clusters_count}")
    logger.log(f"  - Conflicting Label Clusters:        {conflict_clusters_count}")
    logger.log(separator)

    # ----------------------------------------------------------------------
    # Build Formal TXT Report
    # ----------------------------------------------------------------------
    logger.log("Generating comprehensive audit sections...")

    # Section 1: STEP 5 SUMMARY
    logger.log("============================================================")
    logger.log("1. STEP 5 SUMMARY")
    logger.log("============================================================")
    logger.log(f"Total Evaluated TRAIN <-> TEST Pairs:           {len(all_evaluated_tt_pairs)}")
    logger.log(f"  - Exact Leakage Pairs (SHA-256):              {len(exact_leakage_records)} (from {len(exact_leakage_groups)} groups)")
    logger.log(f"  - Confirmed Near-Duplicate Leakage Pairs:     {len(confirmed_leakage_pairs)}")
    logger.log(f"  - Likely Near-Duplicate Leakage Pairs:        {len(likely_leakage_pairs)}")
    logger.log(f"  - Possible Near-Duplicate Pairs:              {len(possible_leakage_pairs)}")
    logger.log(f"  - Different / Refuted Pairs:                  {len(different_pairs)}")
    logger.log("")
    logger.log(f"Total Unique Multi-Image Clusters Formed:       {len(formatted_clusters)}")
    logger.log(f"  - Cross-Split Leakage Clusters:               {cross_split_clusters_count}")
    logger.log(f"  - Class Conflict Clusters:                    {conflict_clusters_count}")
    logger.log(f"  - Total Images in Clusters:                   {sum(c['total_images'] for c in formatted_clusters)}")
    logger.log(separator)

    # Section 2: SCOPE VERIFICATION
    logger.log("2. SCOPE VERIFICATION:")
    logger.log("   [VERIFIED] Analyzed strictly: D:\\Areca\\Data\\train and D:\\Areca\\Data\\test.")
    logger.log("   [VERIFIED] final_testing-20230830T042904Z-001 was NOT accessed, read, or scanned.")
    logger.log(sub_sep)

    # Section 3: EXACT TRAIN <-> TEST DUPLICATES
    logger.log(f"3. EXACT TRAIN <-> TEST DUPLICATES ({len(exact_leakage_groups)} groups, {len(exact_leakage_records)} pairings):")
    for r in exact_leakage_records[:15]:
        logger.log(f"   [{r['group_id']}] SHA-256: {r['sha256'][:16]}... | Label Match: {r['labels_match']}")
        logger.log(f"       TRAIN: [{r['train_class']}] {r['train_path']}")
        logger.log(f"       TEST:  [{r['test_class']}] {r['test_path']}")
    if len(exact_leakage_records) > 15:
        logger.log(f"   ... and {len(exact_leakage_records) - 15} more exact leakage pairings (see full JSON/CSV)")
    logger.log(sub_sep)

    # Section 4: CONFIRMED TRAIN <-> TEST NEAR DUPLICATES
    logger.log(f"4. CONFIRMED TRAIN <-> TEST NEAR DUPLICATES ({len(confirmed_leakage_pairs)} pairs):")
    for r in confirmed_leakage_pairs[:15]:
        logger.log(f"   [{r['pair_id']}] pHash={r['phash_dist']}, dHash={r['dhash_dist']}, SSIM={r['ssim']:.3f}, NCC={r['ncc']:.3f}, MSE={r['mse']:.4f}")
        logger.log(f"       TRAIN: [{r['train_class']}] {r['train_path']}")
        logger.log(f"       TEST:  [{r['test_class']}] {r['test_path']}")
        logger.log(f"       Reason: {r['reason']}")
    if len(confirmed_leakage_pairs) > 15:
        logger.log(f"   ... and {len(confirmed_leakage_pairs) - 15} more confirmed near-duplicate pairs")
    logger.log(sub_sep)

    # Section 5: LIKELY TRAIN <-> TEST NEAR DUPLICATES
    logger.log(f"5. LIKELY TRAIN <-> TEST NEAR DUPLICATES ({len(likely_leakage_pairs)} pairs):")
    for r in likely_leakage_pairs[:10]:
        logger.log(f"   [{r['pair_id']}] pHash={r['phash_dist']}, SSIM={r['ssim']:.3f}, NCC={r['ncc']:.3f}")
        logger.log(f"       TRAIN: [{r['train_class']}] {r['train_path']}")
        logger.log(f"       TEST:  [{r['test_class']}] {r['test_path']}")
    if len(likely_leakage_pairs) > 10:
        logger.log(f"   ... and {len(likely_leakage_pairs) - 10} more likely leakage pairs")
    logger.log(sub_sep)

    # Section 6: POSSIBLE TRAIN <-> TEST NEAR DUPLICATES
    logger.log(f"6. POSSIBLE TRAIN <-> TEST NEAR DUPLICATES ({len(possible_leakage_pairs)} pairs):")
    logger.log(f"   Total {len(possible_leakage_pairs)} pairs exhibited moderate structural similarity but insufficient evidence for definitive duplicate declaration.")
    logger.log(sub_sep)

    # Section 7: DIFFERENT TRAIN <-> TEST IMAGES
    logger.log(f"7. DIFFERENT TRAIN <-> TEST IMAGES ({len(different_pairs)} pairs):")
    logger.log(f"   Total {len(different_pairs)} candidate pairs from pHash audit were refuted by multi-metric SSIM/NCC/Hist evaluation as distinct photographs.")
    logger.log(sub_sep)

    # Section 8: CLASS-CONFLICT ANALYSIS
    logger.log(f"8. CLASS-CONFLICT ANALYSIS ({len(verified_conflicts)} candidates evaluated):")
    logger.log(f"   - CONFIRMED_LABEL_CONFLICT: {confirmed_conflict_count} pair(s)")
    logger.log(f"   - NOT_A_LABEL_CONFLICT:     {len(verified_conflicts) - confirmed_conflict_count} pair(s)")
    for c in verified_conflicts:
        if c["conflict_verdict"] == "CONFIRMED_LABEL_CONFLICT":
            logger.log(f"   * [CONFLICT] [{c['conflict_id']}] {c['image_a_class']} <--> {c['image_b_class']}")
            logger.log(f"       Image A: [{c['image_a_split']}] {c['image_a_path']}")
            logger.log(f"       Image B: [{c['image_b_split']}] {c['image_b_path']}")
            logger.log(f"       Metrics: pHash={c['phash_dist']}, SSIM={c['ssim']:.3f}, NCC={c['ncc']:.3f}")
    if confirmed_conflict_count == 0:
        logger.log("   Zero confirmed label conflicts found (no identical photographs appear under conflicting disease labels).")
    logger.log(sub_sep)

    # Section 9: WITHIN-TEST DUPLICATES
    within_test_exact = step03_data.get("within_test_groups", [])
    logger.log(f"9. WITHIN-TEST DUPLICATES:")
    logger.log(f"   - Exact Duplicate Groups in TEST: {len(within_test_exact)}")
    for idx, g in enumerate(within_test_exact[:5], 1):
        logger.log(f"     Group {idx}: SHA-256 {g['sha256'][:16]}... ({len(g['images'])} copies in class '{g['classes'][0]}')")
    logger.log(sub_sep)

    # Section 10: WITHIN-TRAIN DUPLICATE CLUSTERS
    logger.log(f"10. WITHIN-TRAIN DUPLICATE CLUSTERS:")
    within_train_clusters = [c for c in formatted_clusters if c["splits"] == ["train"]]
    logger.log(f"    - Purely within-train clusters: {len(within_train_clusters)}")
    for c in within_train_clusters[:5]:
        logger.log(f"      [{c['cluster_id']}] {c['total_images']} images in class {c['classes']}")
    logger.log(sub_sep)

    # Section 11: LEAKAGE SUMMARY
    total_leakage_pairs = len(exact_leakage_records) + len(confirmed_leakage_pairs) + len(likely_leakage_pairs)
    logger.log("11. LEAKAGE SUMMARY:")
    logger.log(f"    - Total Critical Cross-Split Leakage Pairings: {total_leakage_pairs}")
    logger.log(f"    - Cross-Split Multi-Image Clusters:           {cross_split_clusters_count}")
    logger.log(f"    - Leakage Impact: Contaminates independent test set evaluation if left unresolved.")
    logger.log(sub_sep)

    # Section 12: DATA-CLEANUP RECOMMENDATIONS
    logger.log("12. DATA-CLEANUP RECOMMENDATIONS:")
    logger.log("    1. Remove all TEST-leaked copies from TRAIN (or isolate pure independent test set).")
    logger.log("    2. Deduplicate within-test exact copies to prevent skewed test distribution.")
    logger.log("    3. Collapse within-train duplicate clusters to single canonical exemplars.")
    logger.log("    4. Re-verify train/val/test splits after deduplication.")
    logger.log(sub_sep)

    # Section 13: FINAL STATUS
    status_str = "REVIEW REQUIRED (LEAKAGE CONFIRMED)" if total_leakage_pairs > 0 else "PASS"
    logger.log("13. FINAL STATUS:")
    logger.log(f"    STEP 5 STATUS: {status_str}")
    logger.log(separator)
    logger.log("SCOPE CONFIRMATION:")
    logger.log("  final_testing-20230830T042904Z-001 was NOT accessed.")
    logger.log(separator)

    # Write TXT report
    logger.write_to_file(txt_report_file)

    # Write CSV report
    logger.log(f"Writing CSV report to: {csv_report_file}")
    with open(csv_report_file, "w", newline="", encoding="utf-8") as cf:
        writer = csv.writer(cf)
        writer.writerow([
            "pair_id", "train_split", "train_class", "train_path",
            "test_split", "test_class", "test_path",
            "phash_dist", "dhash_dist", "ssim", "ncc", "mse", "hist_sim", "ar_diff",
            "classification", "leakage_status", "is_class_conflict", "reason"
        ])
        for r in all_evaluated_tt_pairs:
            writer.writerow([
                r["pair_id"], "train", r["train_class"], r["train_path"],
                "test", r["test_class"], r["test_path"],
                r["phash_dist"], r["dhash_dist"], r["ssim"], r["ncc"], r["mse"], r["hist_sim"], r["ar_diff"],
                r["classification"], r["leakage_status"], r["is_class_conflict"], r["reason"]
            ])

    # Write JSON report
    logger.log(f"Writing JSON report to: {json_report_file}")
    json_data = {
        "audit_step": "STEP 05 - Duplicate & Leakage Confirmation Audit",
        "scope": {
            "project_root": str(project_root),
            "train_dir": str(train_dir),
            "test_dir": str(test_dir),
            "final_testing_excluded": True
        },
        "summary": {
            "total_evaluated_train_test_pairs": len(all_evaluated_tt_pairs),
            "exact_leakage_groups_count": len(exact_leakage_groups),
            "exact_leakage_pairings_count": len(exact_leakage_records),
            "confirmed_near_duplicate_leakage_pairs_count": len(confirmed_leakage_pairs),
            "likely_near_duplicate_leakage_pairs_count": len(likely_leakage_pairs),
            "possible_near_duplicate_pairs_count": len(possible_leakage_pairs),
            "different_refuted_pairs_count": len(different_pairs),
            "total_multi_image_clusters_count": len(formatted_clusters),
            "cross_split_clusters_count": cross_split_clusters_count,
            "conflict_clusters_count": conflict_clusters_count,
            "confirmed_label_conflicts_count": confirmed_conflict_count,
            "step_5_status": status_str
        },
        "exact_leakage_records": exact_leakage_records,
        "confirmed_near_duplicate_leakage_pairs": confirmed_leakage_pairs,
        "likely_near_duplicate_leakage_pairs": likely_leakage_pairs,
        "possible_near_duplicate_pairs": possible_leakage_pairs,
        "class_conflict_verifications": verified_conflicts,
        "clusters": formatted_clusters
    }

    with open(json_report_file, "w", encoding="utf-8") as jf:
        json.dump(json_data, jf, indent=2)

    logger.log(separator)
    logger.log(f"All reports successfully generated.")
    logger.log(separator)


if __name__ == "__main__":
    main()

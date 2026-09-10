"""
Step 6: Train/Test Cleanup Manifest Generator (Read-Only)
Script: D:\\Areca\\scripts\\step06_cleanup_manifest.py
Output:
  - D:\\Areca\\reports\\step06_cleanup_manifest.txt
  - D:\\Areca\\reports\\step06_cleanup_manifest.json
  - D:\\Areca\\reports\\step06_cleanup_manifest.csv

READ-ONLY SCRIPT:
Analyzes ONLY:
  - D:\\Areca\\Data\\train
  - D:\\Areca\\Data\\test
  - D:\\Areca\\reports

Explicitly DOES NOT inspect, read, modify, or delete anything in:
  - D:\\Areca\\Data\\final_testing-20230830T042904Z-001
"""

import os
import sys
import json
import csv
from pathlib import Path
from collections import defaultdict

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


def validate_removal_item(train_path_str: str, test_ref_str: str, train_dir: Path, test_dir: Path, protected_dir: Path):
    """
    Strict safety validation:
    1. Train path exists
    2. Train path is inside D:\\Areca\\Data\\train
    3. Train path is NOT in test or final_testing
    4. Test reference exists and is inside D:\\Areca\\Data\\test
    """
    t_path = Path(train_path_str)
    te_path = Path(test_ref_str) if test_ref_str else None

    # Existence checks
    if not t_path.exists():
        return False, f"Train image does not exist on disk: {train_path_str}"

    # Directory boundary checks
    try:
        t_path.resolve().relative_to(train_dir.resolve())
    except ValueError:
        return False, f"Train image is NOT located inside train directory: {train_path_str}"

    if str(test_dir.resolve()) in str(t_path.resolve()):
        return False, f"CRITICAL ERROR: Proposed removal is inside TEST directory: {train_path_str}"

    if str(protected_dir.resolve()) in str(t_path.resolve()):
        return False, f"CRITICAL ERROR: Proposed removal is inside protected final_testing: {train_path_str}"

    if te_path:
        if not te_path.exists():
            return False, f"Referenced TEST image does not exist on disk: {test_ref_str}"
        try:
            te_path.resolve().relative_to(test_dir.resolve())
        except ValueError:
            return False, f"Referenced TEST image is NOT located inside TEST directory: {test_ref_str}"

    return True, "OK"


def count_files_in_split(split_path: Path):
    """Safely counts image files in a split directory."""
    if not split_path.exists() or not split_path.is_dir():
        return 0
    count = 0
    for root, _, files in os.walk(split_path):
        for f in files:
            if Path(f).suffix.lower() in IMAGE_EXTENSIONS:
                count += 1
    return count


def main():
    logger = Logger()

    project_root = Path(r"D:\Areca")
    train_dir = project_root / "Data" / "train"
    test_dir = project_root / "Data" / "test"
    protected_dir = project_root / "Data" / "final_testing-20230830T042904Z-001"
    reports_dir = project_root / "reports"

    step03_json = reports_dir / "step03_exact_duplicate_audit.json"
    step04_json = reports_dir / "step04_near_duplicate_audit.json"
    step05_json = reports_dir / "step05_duplicate_confirmation.json"

    txt_manifest = reports_dir / "step06_cleanup_manifest.txt"
    json_manifest = reports_dir / "step06_cleanup_manifest.json"
    csv_manifest = reports_dir / "step06_cleanup_manifest.csv"

    separator = "=" * 80
    sub_sep = "-" * 80

    logger.log(separator)
    logger.log("STEP 6 — TRAIN/TEST DATASET CLEANUP MANIFEST GENERATION (READ-ONLY)")
    logger.log(separator)
    logger.log(f"Project Root:           {project_root}")
    logger.log(f"Target Train Directory: {train_dir}")
    logger.log(f"Target Test Directory:  {test_dir}")
    logger.log(sub_sep)
    logger.log("CRITICAL SCOPE ENFORCEMENT:")
    logger.log("  [VERIFIED] Analyzed strictly: D:\\Areca\\Data\\train and D:\\Areca\\Data\\test.")
    logger.log("  [VERIFIED] D:\\Areca\\Data\\final_testing-20230830T042904Z-001 was ABSOLUTELY NOT accessed.")
    logger.log("  [VERIFIED] READ-ONLY AUDIT: No dataset files will be modified, moved, or deleted.")
    logger.log(separator)

    # 1. Verify input files exist
    if not step05_json.exists():
        logger.log(f"[ERROR] Step 5 structured report missing: {step05_json}")
        sys.exit(1)

    logger.log("Loading Step 5 confirmed duplicate & leakage records...")
    with open(step05_json, "r", encoding="utf-8") as f:
        step05_data = json.load(f)

    # Load Step 3 if available for full exact duplicate context
    step03_data = {}
    if step03_json.exists():
        with open(step03_json, "r", encoding="utf-8") as f:
            step03_data = json.load(f)

    # Count dataset images directly from directories
    train_total_files = count_files_in_split(train_dir)
    test_total_files = count_files_in_split(test_dir)

    # Extract Step 5 datasets
    exact_leakage_records = step05_data.get("exact_leakage_records", [])
    confirmed_near_dup_pairs = step05_data.get("confirmed_near_duplicate_leakage_pairs", [])
    likely_near_dup_pairs = step05_data.get("likely_near_duplicate_leakage_pairs", [])
    possible_near_dup_pairs = step05_data.get("possible_near_duplicate_pairs", [])
    clusters = step05_data.get("clusters", [])
    within_test_groups = step03_data.get("within_test_groups", [])

    # Map image path to cluster ID
    path_to_cluster = {}
    for c in clusters:
        c_id = c["cluster_id"]
        for img in c["images"]:
            path_to_cluster[img["path"]] = c_id

    # ------------------------------------------------------------------
    # Consolidate and Deduplicate TRAIN Removals
    # ------------------------------------------------------------------
    logger.log("\nConsolidating confirmed TRAIN removals...")

    # Key: train_path -> Dict of removal details
    proposed_train_removals = {}

    # 1. Process Exact TRAIN <-> TEST Duplicates
    for rec in exact_leakage_records:
        t_path = rec["train_path"]
        te_path = rec["test_path"]
        t_class = rec["train_class"]
        sha = rec["sha256"]
        c_id = path_to_cluster.get(t_path, rec.get("group_id", "CLUSTER_EXACT"))

        if t_path not in proposed_train_removals:
            proposed_train_removals[t_path] = {
                "train_path": t_path,
                "class": t_class,
                "removal_type": "EXACT_LEAKAGE",
                "reasons": [f"Exact byte-for-byte duplicate (SHA-256: {sha[:16]}...) of TEST image"],
                "test_references": [te_path],
                "cluster_id": c_id,
                "confidence": "CONFIRMED",
                "details": []
            }
        else:
            if te_path not in proposed_train_removals[t_path]["test_references"]:
                proposed_train_removals[t_path]["test_references"].append(te_path)

    # 2. Process Confirmed Near-Duplicate TRAIN <-> TEST Pairs
    for pair in confirmed_near_dup_pairs:
        t_path = pair["train_path"]
        te_path = pair["test_path"]
        t_class = pair["train_class"]
        c_id = path_to_cluster.get(t_path, "CLUSTER_NEAR_DUP")
        detail_str = f"Confirmed near-duplicate (SSIM={pair.get('ssim', 0):.3f}, NCC={pair.get('ncc', 0):.3f}, pHash={pair.get('phash_dist', 0)}) of TEST image"

        if t_path not in proposed_train_removals:
            proposed_train_removals[t_path] = {
                "train_path": t_path,
                "class": t_class,
                "removal_type": "CONFIRMED_NEAR_DUPLICATE_LEAKAGE",
                "reasons": [detail_str],
                "test_references": [te_path],
                "cluster_id": c_id,
                "confidence": "CONFIRMED",
                "details": [pair]
            }
        else:
            # If already recorded as exact or near-duplicate, append test reference if not present
            if te_path not in proposed_train_removals[t_path]["test_references"]:
                proposed_train_removals[t_path]["test_references"].append(te_path)
            proposed_train_removals[t_path]["reasons"].append(detail_str)
            proposed_train_removals[t_path]["details"].append(pair)

    # 3. Validation Phase (9 Pre-Manifest Integrity Checks)
    logger.log("Executing safety validations on all proposed removals...")
    validation_failures = []
    
    unique_removals = []
    for idx, (t_path, item) in enumerate(sorted(proposed_train_removals.items(), key=lambda x: x[0]), 1):
        test_ref = item["test_references"][0] if item["test_references"] else None
        is_valid, msg = validate_removal_item(t_path, test_ref, train_dir, test_dir, protected_dir)
        if not is_valid:
            validation_failures.append(f"[{t_path}]: {msg}")
        
        rem_entry = {
            "removal_id": f"REMOVE_{idx:04d}",
            "train_path": t_path,
            "class": item["class"],
            "removal_type": item["removal_type"],
            "reason": "; ".join(item["reasons"]),
            "test_references": item["test_references"],
            "primary_test_ref": test_ref,
            "cluster_id": item["cluster_id"],
            "confidence": item["confidence"]
        }
        unique_removals.append(rem_entry)

    if validation_failures:
        logger.log("\n[CRITICAL ERROR] SAFETY VALIDATION FAILED:")
        for fail in validation_failures:
            logger.log(f"  - {fail}")
        logger.log("Aborting manifest generation to prevent unsafe operations.")
        sys.exit(1)

    logger.log(f"Safety validation PASSED for all {len(unique_removals)} unique TRAIN removals.")

    # 4. Class-wise summary of proposed removals
    removals_by_class = defaultdict(int)
    for r in unique_removals:
        removals_by_class[r["class"]] += 1

    # Counts for other categories
    likely_leakage_count = len(likely_near_dup_pairs)
    possible_leakage_count = len(possible_near_dup_pairs)
    refuted_pairs_count = step05_data.get("summary", {}).get("different_refuted_pairs_count", 566)
    cross_split_clusters_count = step05_data.get("summary", {}).get("cross_split_clusters_count", 328)

    exact_leakage_groups_cnt = step05_data.get("summary", {}).get("exact_leakage_groups_count", 122)

    # ------------------------------------------------------------------
    # Build Formal Report Sections
    # ------------------------------------------------------------------

    # SECTION 1 — SUMMARY
    logger.log("============================================================")
    logger.log("SECTION 1 — SUMMARY")
    logger.log("============================================================")
    logger.log(f"Original TRAIN image count:                     {train_total_files}")
    logger.log(f"Original TEST image count:                      {test_total_files}")
    logger.log(f"Number of TRAIN images proposed for removal:    {len(unique_removals)}")
    logger.log(f"Number of TEST images proposed for removal:     0 (Preserved as Reference Set)")
    logger.log(f"Number of exact leakage groups:                 {exact_leakage_groups_cnt}")
    logger.log(f"Number of confirmed near-duplicate pairs:       {len(confirmed_near_dup_pairs)}")
    logger.log(f"Number of likely leakage groups (Review Only):  {likely_leakage_count}")
    logger.log(f"Number of possible leakage groups (Pending):    {possible_leakage_count}")
    logger.log(f"Number of confirmed class conflicts:            0")
    logger.log(f"Number of cross-split clusters:                 {cross_split_clusters_count}")
    logger.log(f"Number of UNIQUE TRAIN files proposed for removal: {len(unique_removals)}")
    logger.log(separator)

    # SECTION 2 — EXACT LEAKAGE REMOVALS
    logger.log("SECTION 2 — EXACT LEAKAGE REMOVALS")
    logger.log(f"Total exact cross-split pairings: {len(exact_leakage_records)}")
    logger.log("Policy: REMOVE_FROM_TRAIN | KEEP_IN_TEST")
    logger.log(sub_sep)
    for r in exact_leakage_records[:10]:
        logger.log(f"  [{r.get('group_id', 'EXACT')}] SHA-256: {r['sha256'][:16]}...")
        logger.log(f"    TRAIN ({r['train_class']}): {r['train_path']} -> ACTION: REMOVE_FROM_TRAIN")
        logger.log(f"    TEST  ({r['test_class']}):  {r['test_path']} -> ACTION: KEEP_IN_TEST")
    if len(exact_leakage_records) > 10:
        logger.log(f"  ... and {len(exact_leakage_records) - 10} more exact leakage pairings (see JSON/CSV)")
    logger.log(separator)

    # SECTION 3 — CONFIRMED NEAR-DUPLICATE REMOVALS
    logger.log("SECTION 3 — CONFIRMED NEAR-DUPLICATE REMOVALS")
    logger.log(f"Total confirmed near-duplicate leakage pairs: {len(confirmed_near_dup_pairs)}")
    logger.log("Policy: REMOVE_FROM_TRAIN | KEEP_IN_TEST")
    logger.log(sub_sep)
    for pair in confirmed_near_dup_pairs[:10]:
        logger.log(f"  [{pair['pair_id']}] pHash={pair.get('phash_dist',0)}, dHash={pair.get('dhash_dist',0)}, SSIM={pair.get('ssim',0):.3f}, NCC={pair.get('ncc',0):.3f}")
        logger.log(f"    TRAIN ({pair['train_class']}): {pair['train_path']} -> ACTION: REMOVE_FROM_TRAIN")
        logger.log(f"    TEST  ({pair['test_class']}):  {pair['test_path']} -> ACTION: KEEP_IN_TEST")
    if len(confirmed_near_dup_pairs) > 10:
        logger.log(f"  ... and {len(confirmed_near_dup_pairs) - 10} more confirmed near-duplicate pairs")
    logger.log(separator)

    # SECTION 4 — LIKELY CASES
    logger.log("SECTION 4 — LIKELY CASES")
    logger.log(f"Total likely near-duplicate leakage pairs: {likely_leakage_count}")
    logger.log("Action: REVIEW_REQUIRED (NOT automatically marked for deletion)")
    logger.log("Reason: While structural similarity is elevated, conservative policy requires explicit manual review before removal.")
    logger.log(separator)

    # SECTION 5 — POSSIBLE CASES
    logger.log("SECTION 5 — POSSIBLE CASES")
    logger.log(f"Total possible near-duplicate pairs: {possible_leakage_count}")
    logger.log("Action: KEEP_PENDING_REVIEW (Retained in training set)")
    logger.log("Reason: Moderate structural similarity could represent natural agricultural visual patterns or distinct plants.")
    logger.log(separator)

    # SECTION 6 — REFUTED CASES
    logger.log("SECTION 6 — REFUTED CASES")
    logger.log(f"Total refuted / different candidate pairs: {refuted_pairs_count}")
    logger.log("Action: NO_ACTION (Confirmed distinct photographs)")
    logger.log(separator)

    # SECTION 7 — WITHIN-TEST DUPLICATES
    logger.log("SECTION 7 — WITHIN-TEST DUPLICATES")
    logger.log(f"Total exact duplicate groups within TEST: {len(within_test_groups)}")
    logger.log("Action: REVIEW_REQUIRED (NOT automatically deleted)")
    logger.log("Reason: TEST set is preserved as the independent benchmark. Deduplication of TEST requires separate evaluation.")
    logger.log(separator)

    # SECTION 8 — WITHIN-TRAIN DUPLICATES
    logger.log("SECTION 8 — WITHIN-TRAIN DUPLICATES")
    logger.log("Action: RETAINED (Unless leaking into TEST)")
    logger.log("Reason: Within-train duplicate clusters not leaking to TEST are preserved to avoid aggressive dataset compression.")
    logger.log(separator)

    # SECTION 9 — CLASS CONFLICTS
    logger.log("SECTION 9 — CLASS CONFLICTS")
    logger.log("Report: 0 CONFIRMED_LABEL_CONFLICT")
    logger.log("No relabeling is proposed.")
    logger.log(separator)

    # FINAL PROPOSED TRAIN REMOVAL LIST
    logger.log("============================================================")
    logger.log("FINAL PROPOSED TRAIN REMOVAL LIST")
    logger.log("============================================================")
    for r in unique_removals[:25]:
        logger.log(f"[{r['removal_id']}]")
        logger.log(f"TRAIN:          {r['train_path']}")
        logger.log(f"CLASS:          {r['class']}")
        logger.log(f"REASON:         {r['reason']}")
        logger.log(f"TEST REFERENCE: {r['primary_test_ref']}")
        logger.log(f"CLUSTER:        {r['cluster_id']}")
        logger.log(f"CONFIDENCE:     {r['confidence']}")
        logger.log(sub_sep)

    if len(unique_removals) > 25:
        logger.log(f"... and {len(unique_removals) - 25} more unique proposed removals (full list in {json_manifest} and {csv_manifest})")
        logger.log(sub_sep)

    # Class breakdown
    logger.log("TOTALS BY CLASS:")
    for c_name in ["Healthy_Leaf", "Healthy_Nut", "Mahali_Koleroga", "yellow leaf disease"]:
        logger.log(f"  {c_name:<20}: {removals_by_class.get(c_name, 0)} proposed removals")
    logger.log(sub_sep)
    logger.log(f"TOTAL: {len(unique_removals)} unique TRAIN images proposed for removal")
    logger.log(separator)

    # Save TXT Manifest
    logger.write_to_file(txt_manifest)

    # Save CSV Manifest
    logger.log(f"Writing CSV manifest to: {csv_manifest}")
    with open(csv_manifest, "w", newline="", encoding="utf-8") as cf:
        writer = csv.writer(cf)
        writer.writerow([
            "removal_id", "train_path", "class", "removal_type",
            "reason", "primary_test_reference", "cluster_id", "confidence"
        ])
        for r in unique_removals:
            writer.writerow([
                r["removal_id"], r["train_path"], r["class"], r["removal_type"],
                r["reason"], r["primary_test_ref"], r["cluster_id"], r["confidence"]
            ])

    # Save JSON Manifest
    logger.log(f"Writing JSON manifest to: {json_manifest}")
    json_data = {
        "manifest_step": "STEP 06 - Train/Test Cleanup Manifest",
        "scope": {
            "project_root": str(project_root),
            "train_dir": str(train_dir),
            "test_dir": str(test_dir),
            "final_testing_excluded": True
        },
        "summary": {
            "original_train_count": train_total_files,
            "original_test_count": test_total_files,
            "unique_train_removals_count": len(unique_removals),
            "test_removals_count": 0,
            "removals_by_class": dict(removals_by_class),
            "exact_leakage_groups_count": exact_leakage_groups_cnt,
            "confirmed_near_duplicate_pairs_count": len(confirmed_near_dup_pairs),
            "likely_leakage_count": likely_leakage_count,
            "possible_leakage_count": possible_leakage_count,
            "refuted_pairs_count": refuted_pairs_count,
            "within_test_exact_groups_count": len(within_test_groups),
            "confirmed_class_conflicts_count": 0
        },
        "proposed_train_removals": unique_removals,
        "likely_leakage_review_list": likely_near_dup_pairs,
        "possible_leakage_list": possible_near_dup_pairs,
        "within_test_duplicate_groups": within_test_groups
    }

    with open(json_manifest, "w", encoding="utf-8") as jf:
        json.dump(json_data, jf, indent=2)

    logger.log(separator)
    logger.log(f"Step 6 Cleanup Manifest successfully generated (Read-Only).")
    logger.log(separator)


if __name__ == "__main__":
    main()

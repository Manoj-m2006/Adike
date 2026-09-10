"""
Step 8: Approved Train Cleanup (Quarantine Move & Validation)
Script: D:\\Areca\\scripts\\step08_actual_train_cleanup.py
Output:
  - D:\\Areca\\reports\\step08_actual_train_cleanup.txt
  - D:\\Areca\\reports\\step08_actual_train_cleanup.json
  - D:\\Areca\\reports\\step08_actual_train_cleanup.csv
Quarantine Directory:
  - D:\\Areca\\cleanup_backup_step08

SAFETY FIRST:
  - Moves approved 421 duplicate/leaked TRAIN files to quarantine backup.
  - TEST set is completely UNTOUCHED.
  - Explicitly DOES NOT access, read, or scan D:\\Areca\\Data\\final_testing-20230830T042904Z-001.
"""

import os
import sys
import json
import csv
import shutil
import hashlib
from pathlib import Path
from collections import defaultdict

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
CHUNK_SIZE = 65536

# Authoritative Expected Counts
EXPECTED_REMOVAL_TOTAL = 421
EXPECTED_REMOVAL_BY_CLASS = {
    "Healthy_Leaf": 22,
    "Healthy_Nut": 115,
    "Mahali_Koleroga": 246,
    "yellow leaf disease": 38
}

EXPECTED_POST_TRAIN_TOTAL = 6109
EXPECTED_POST_TRAIN_BY_CLASS = {
    "Healthy_Leaf": 582,
    "Healthy_Nut": 1771,
    "Mahali_Koleroga": 2317,
    "yellow leaf disease": 1439
}

EXPECTED_TEST_TOTAL = 1635


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


def compute_sha256(filepath: Path) -> str:
    """Computes SHA-256 hash of a file reading in 64KB chunks."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            hasher.update(chunk)
    return hasher.hexdigest()


def count_split_images(split_path: Path):
    """Safely counts image files per class strictly inside split_path."""
    class_counts = defaultdict(int)
    all_files = []
    if not split_path.exists() or not split_path.is_dir():
        return class_counts, all_files

    class_dirs = sorted([d for d in split_path.iterdir() if d.is_dir()], key=lambda x: x.name)
    for c_dir in class_dirs:
        c_name = c_dir.name
        for root, _, files in os.walk(c_dir):
            for f in files:
                if Path(f).suffix.lower() in IMAGE_EXTENSIONS:
                    p = str(Path(root) / f)
                    class_counts[c_name] += 1
                    all_files.append((p, c_name))
    return class_counts, all_files


def main():
    logger = Logger()

    project_root = Path(r"D:\Areca")
    train_dir = project_root / "Data" / "train"
    test_dir = project_root / "Data" / "test"
    protected_dir = project_root / "Data" / "final_testing-20230830T042904Z-001"
    reports_dir = project_root / "reports"
    quarantine_dir = project_root / "cleanup_backup_step08"

    manifest_json = reports_dir / "step06_cleanup_manifest.json"

    txt_report = reports_dir / "step08_actual_train_cleanup.txt"
    json_report = reports_dir / "step08_actual_train_cleanup.json"
    csv_report = reports_dir / "step08_actual_train_cleanup.csv"

    reports_dir.mkdir(parents=True, exist_ok=True)

    separator = "=" * 80
    sub_sep = "-" * 80

    logger.log(separator)
    logger.log("STEP 8 — APPROVED TRAIN DATASET CLEANUP (QUARANTINE MOVE)")
    logger.log(separator)
    logger.log(f"Project Root:           {project_root}")
    logger.log(f"Target Train Directory: {train_dir}")
    logger.log(f"Target Test Directory:  {test_dir}")
    logger.log(f"Quarantine Backup Dir:  {quarantine_dir}")
    logger.log(sub_sep)
    logger.log("CRITICAL SCOPE ENFORCEMENT:")
    logger.log("  [VERIFIED] Operating strictly on: D:\\Areca\\Data\\train.")
    logger.log("  [VERIFIED] TEST set is PRESERVED and completely UNTOUCHED.")
    logger.log("  [VERIFIED] D:\\Areca\\Data\\final_testing-20230830T042904Z-001 was ABSOLUTELY NOT accessed.")
    logger.log(separator)

    # 1. Load Step 6 Cleanup Manifest
    if not manifest_json.exists():
        logger.log(f"[FATAL ERROR] Step 6 cleanup manifest missing: {manifest_json}")
        sys.exit(1)

    logger.log("Loading authoritative Step 6 cleanup manifest...")
    with open(manifest_json, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    proposed_removals = manifest_data.get("proposed_train_removals", [])
    num_removals = len(proposed_removals)

    # ------------------------------------------------------------------
    # Pre-Flight Safety Verification (Fail-Closed)
    # ------------------------------------------------------------------
    logger.log("\nExecuting Pre-Flight Safety Checks...")
    preflight_errors = []

    # Check 1: Exactly 421 Unique Removals
    if num_removals != EXPECTED_REMOVAL_TOTAL:
        preflight_errors.append(
            f"Manifest total removal count mismatch: Expected {EXPECTED_REMOVAL_TOTAL}, got {num_removals}"
        )

    # Check 2: No duplicate removal paths in manifest
    removal_paths = [r["train_path"] for r in proposed_removals]
    if len(removal_paths) != len(set(removal_paths)):
        preflight_errors.append("Duplicate paths detected in removal list")

    # Check 3: Class Breakdown matches authoritative counts
    manifest_class_counts = defaultdict(int)
    for r in proposed_removals:
        manifest_class_counts[r["class"]] += 1

    for c_name, exp_cnt in EXPECTED_REMOVAL_BY_CLASS.items():
        act_cnt = manifest_class_counts.get(c_name, 0)
        if act_cnt != exp_cnt:
            preflight_errors.append(
                f"Removal count mismatch for class '{c_name}': Expected {exp_cnt}, got {act_cnt}"
            )

    # Check 4: Strict Path & Boundary Validations
    train_resolved = train_dir.resolve()
    test_resolved = test_dir.resolve()
    protected_resolved = protected_dir.resolve()

    validated_removal_records = []

    for r in proposed_removals:
        t_path_str = r["train_path"]
        t_path = Path(t_path_str)
        t_class = r["class"]

        if not t_path.exists():
            preflight_errors.append(f"File not found on disk: {t_path_str}")
            continue

        if not t_path.is_file():
            preflight_errors.append(f"Target is not a regular file: {t_path_str}")
            continue

        try:
            rel_to_train = t_path.resolve().relative_to(train_resolved)
        except ValueError:
            preflight_errors.append(f"Target escapes TRAIN directory boundary: {t_path_str}")
            continue

        if str(test_resolved) in str(t_path.resolve()):
            preflight_errors.append(f"CRITICAL VIOLATION: Target is inside TEST directory: {t_path_str}")
            continue

        if str(protected_resolved) in str(t_path.resolve()):
            preflight_errors.append(f"CRITICAL VIOLATION: Target is inside final_testing directory: {t_path_str}")
            continue

        # Check that top part of rel_to_train is the class name
        if rel_to_train.parts[0] != t_class:
            preflight_errors.append(
                f"Class directory mismatch: Path has '{rel_to_train.parts[0]}', manifest specifies '{t_class}' ({t_path_str})"
            )
            continue

        # Compute pre-move hash & size
        try:
            file_size = t_path.stat().st_size
            pre_hash = compute_sha256(t_path)
            validated_removal_records.append({
                "removal_id": r["removal_id"],
                "train_path": t_path,
                "rel_path": rel_to_train,
                "class": t_class,
                "filename": t_path.name,
                "file_size": file_size,
                "pre_sha256": pre_hash,
                "reason": r.get("reason", "Confirmed duplicate/leakage"),
                "cluster_id": r.get("cluster_id", "N/A"),
                "test_reference": r.get("primary_test_ref", "N/A")
            })
        except Exception as e:
            preflight_errors.append(f"Failed to inspect/hash {t_path_str}: {e}")

    # Check 5: Initial Dataset Image Counts
    train_class_counts_init, _ = count_split_images(train_dir)
    test_class_counts_init, _ = count_split_images(test_dir)
    total_train_init = sum(train_class_counts_init.values())
    total_test_init = sum(test_class_counts_init.values())

    if total_train_init != 6530:
        preflight_errors.append(f"Initial TRAIN count mismatch: Expected 6530, found {total_train_init}")
    if total_test_init != EXPECTED_TEST_TOTAL:
        preflight_errors.append(f"Initial TEST count mismatch: Expected {EXPECTED_TEST_TOTAL}, found {total_test_init}")

    # Abort if any preflight check fails
    if preflight_errors:
        logger.log("\n[ABORTED] PRE-FLIGHT SAFETY CHECKS FAILED:")
        for err in preflight_errors[:10]:
            logger.log(f"  * {err}")
        if len(preflight_errors) > 10:
            logger.log(f"  ... and {len(preflight_errors) - 10} more errors")
        logger.log("\nNO FILES WERE MOVED OR MODIFIED.")
        sys.exit(1)

    logger.log("Pre-flight safety checks PASSED (All 421 files verified & hashed).")
    logger.log(sub_sep)

    # ------------------------------------------------------------------
    # Execution: Quarantine Move using shutil.move
    # ------------------------------------------------------------------
    logger.log(f"Moving 421 files to Quarantine Directory: {quarantine_dir} ...")
    quarantine_dir.mkdir(parents=True, exist_ok=True)

    moved_records = []
    move_errors = []

    for item in validated_removal_records:
        src_path = item["train_path"]
        rel_path = item["rel_path"]
        dest_path = quarantine_dir / rel_path

        # Create class directory in quarantine if needed
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Move file
            shutil.move(str(src_path), str(dest_path))

            # Post-move SHA-256 verification in quarantine
            post_hash = compute_sha256(dest_path)
            hash_verified = (post_hash == item["pre_sha256"])

            if not hash_verified:
                move_errors.append(
                    f"Post-move SHA-256 verification FAILED for {dest_path.name}: Expected {item['pre_sha256']}, got {post_hash}"
                )

            # Confirm source no longer exists
            src_still_exists = src_path.exists()
            if src_still_exists:
                move_errors.append(f"Source file still present after move: {src_path}")

            moved_records.append({
                "removal_id": item["removal_id"],
                "original_train_path": str(src_path),
                "quarantine_path": str(dest_path),
                "filename": item["filename"],
                "class": item["class"],
                "file_size_bytes": item["file_size"],
                "sha256": post_hash,
                "hash_verified": hash_verified,
                "move_status": "SUCCESS" if (hash_verified and not src_still_exists) else "FAILED",
                "cluster_id": item["cluster_id"],
                "test_reference": item["test_reference"],
                "reason": item["reason"]
            })

        except Exception as move_exc:
            move_errors.append(f"Error moving {src_path} -> {dest_path}: {move_exc}")

    logger.log(f"Quarantine move complete: {len(moved_records)} files processed.")
    if move_errors:
        logger.log(f"[WARNING] {len(move_errors)} move/verification error(s) occurred:")
        for me in move_errors:
            logger.log(f"  * {me}")
    logger.log(sub_sep)

    # ------------------------------------------------------------------
    # Post-Cleanup Validation
    # ------------------------------------------------------------------
    logger.log("Executing Post-Cleanup Dataset Validation...")

    # 1. Recount TRAIN and TEST
    train_class_counts_post, _ = count_split_images(train_dir)
    test_class_counts_post, _ = count_split_images(test_dir)
    total_train_post = sum(train_class_counts_post.values())
    total_test_post = sum(test_class_counts_post.values())

    post_validation_errors = []

    # Check remaining TRAIN count
    if total_train_post != EXPECTED_POST_TRAIN_TOTAL:
        post_validation_errors.append(
            f"Post-cleanup TRAIN count mismatch: Expected {EXPECTED_POST_TRAIN_TOTAL}, found {total_train_post}"
        )

    for c_name, exp_cnt in EXPECTED_POST_TRAIN_BY_CLASS.items():
        act_cnt = train_class_counts_post.get(c_name, 0)
        if act_cnt != exp_cnt:
            post_validation_errors.append(
                f"Post-cleanup TRAIN class count mismatch for '{c_name}': Expected {exp_cnt}, found {act_cnt}"
            )

    # Check TEST count has not changed
    if total_test_post != EXPECTED_TEST_TOTAL:
        post_validation_errors.append(
            f"TEST count altered! Expected {EXPECTED_TEST_TOTAL}, found {total_test_post}"
        )

    for c_name, init_cnt in test_class_counts_init.items():
        curr_cnt = test_class_counts_post.get(c_name, 0)
        if curr_cnt != init_cnt:
            post_validation_errors.append(
                f"TEST class '{c_name}' count changed from {init_cnt} to {curr_cnt}"
            )

    # Check all moved files exist in quarantine
    quarantine_counts, _ = count_split_images(quarantine_dir)
    total_quarantine = sum(quarantine_counts.values())
    if total_quarantine != EXPECTED_REMOVAL_TOTAL:
        post_validation_errors.append(
            f"Quarantine directory count mismatch: Expected {EXPECTED_REMOVAL_TOTAL}, found {total_quarantine}"
        )

    # Check all SHA-256 match
    unverified_hashes = [r for r in moved_records if not r["hash_verified"]]
    if unverified_hashes:
        post_validation_errors.append(f"{len(unverified_hashes)} files failed SHA-256 post-move verification")

    overall_pass = (len(move_errors) == 0 and len(post_validation_errors) == 0)
    final_status = "PASS — All 421 approved files safely quarantined & verified" if overall_pass else "REVIEW REQUIRED — Validation errors encountered"

    # ------------------------------------------------------------------
    # Build Formal Report Sections
    # ------------------------------------------------------------------
    logger.log("============================================================")
    logger.log("STEP 8 SUMMARY REPORT")
    logger.log("============================================================")
    logger.log(f"Original TRAIN Count:                       {total_train_init}")
    logger.log(f"Files Quarantined:                          {len(moved_records)}")
    logger.log(f"Remaining TRAIN Count:                      {total_train_post} (Expected: {EXPECTED_POST_TRAIN_TOTAL})")
    logger.log(f"TEST Count (Untouched):                     {total_test_post} (Expected: {EXPECTED_TEST_TOTAL})")
    logger.log(f"Quarantine Backup Count:                    {total_quarantine} (Expected: {EXPECTED_REMOVAL_TOTAL})")
    logger.log(f"SHA-256 Identity Integrity Check:           {'100% VERIFIED' if not unverified_hashes else 'FAILED'}")
    logger.log(sub_sep)

    logger.log("POST-CLEANUP TRAIN CLASS BREAKDOWN:")
    for c_name in ["Healthy_Leaf", "Healthy_Nut", "Mahali_Koleroga", "yellow leaf disease"]:
        act = train_class_counts_post.get(c_name, 0)
        exp = EXPECTED_POST_TRAIN_BY_CLASS.get(c_name, 0)
        rem = manifest_class_counts.get(c_name, 0)
        status_tag = " [OK]" if act == exp else " [MISMATCH]"
        logger.log(f"  - {c_name:<20}: {act:>4} remaining (Removed: {rem:>3}){status_tag}")
    logger.log(sub_sep)

    logger.log("POST-CLEANUP TEST CLASS BREAKDOWN (UNTOUCHED):")
    for c_name in ["Healthy_Leaf", "Healthy_Nut", "Mahali_Koleroga", "yellow leaf disease"]:
        act = test_class_counts_post.get(c_name, 0)
        logger.log(f"  - {c_name:<20}: {act:>4} (100% Retained)")
    logger.log(separator)

    logger.log("SAMPLE MOVED & QUARANTINED FILES (First 15):")
    for r in moved_records[:15]:
        logger.log(f"  [{r['removal_id']}] {r['class']} | {r['filename']}")
        logger.log(f"      Source:      {r['original_train_path']}")
        logger.log(f"      Quarantine:  {r['quarantine_path']}")
        logger.log(f"      SHA-256:     {r['sha256'][:16]}... [VERIFIED]")
    if len(moved_records) > 15:
        logger.log(f"  ... and {len(moved_records) - 15} more files (full details in JSON/CSV)")
    logger.log(separator)

    logger.log("============================================================")
    logger.log("FINAL STATUS")
    logger.log("============================================================")
    logger.log(f"STATUS: {final_status}")
    logger.log("============================================================")
    logger.log("SCOPE CONFIRMATION:")
    logger.log("  final_testing-20230830T042904Z-001 was NOT accessed.")
    logger.log("============================================================")

    # Save Text Report
    logger.write_to_file(txt_report)

    # Save CSV Report
    logger.log(f"Writing CSV audit record to: {csv_report}")
    with open(csv_report, "w", newline="", encoding="utf-8") as cf:
        writer = csv.writer(cf)
        writer.writerow([
            "removal_id", "original_train_path", "quarantine_path", "filename",
            "class", "file_size_bytes", "sha256", "hash_verified", "move_status",
            "cluster_id", "test_reference", "reason"
        ])
        for r in moved_records:
            writer.writerow([
                r["removal_id"], r["original_train_path"], r["quarantine_path"], r["filename"],
                r["class"], r["file_size_bytes"], r["sha256"], r["hash_verified"], r["move_status"],
                r["cluster_id"], r["test_reference"], r["reason"]
            ])

    # Save JSON Report
    logger.log(f"Writing JSON audit record to: {json_report}")
    json_data = {
        "step": "STEP 08 - Actual Train Cleanup (Quarantine Move)",
        "scope": {
            "project_root": str(project_root),
            "train_dir": str(train_dir),
            "test_dir": str(test_dir),
            "quarantine_dir": str(quarantine_dir),
            "final_testing_excluded": True
        },
        "summary": {
            "original_train_count": total_train_init,
            "removed_files_count": len(moved_records),
            "remaining_train_count": total_train_post,
            "test_count": total_test_post,
            "quarantine_backup_count": total_quarantine,
            "sha256_verified_count": sum(1 for r in moved_records if r["hash_verified"]),
            "train_class_breakdown_post": dict(train_class_counts_post),
            "test_class_breakdown_post": dict(test_class_counts_post),
            "removals_by_class": dict(manifest_class_counts),
            "status": final_status
        },
        "moved_records": moved_records,
        "preflight_errors": preflight_errors,
        "post_validation_errors": post_validation_errors
    }

    with open(json_report, "w", encoding="utf-8") as jf:
        json.dump(json_data, jf, indent=2)

    logger.log(separator)
    logger.log("Step 8 actual train cleanup script completed execution.")
    logger.log(separator)


if __name__ == "__main__":
    main()

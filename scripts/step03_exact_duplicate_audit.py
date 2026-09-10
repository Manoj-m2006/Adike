"""
Step 3: Exact Duplicate Audit (SHA-256)
Script: D:\\Areca\\scripts\\step03_exact_duplicate_audit.py
Output:
  - D:\\Areca\\reports\\step03_exact_duplicate_audit.txt
  - D:\\Areca\\reports\\step03_exact_duplicate_audit.json

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
import hashlib
from pathlib import Path
from collections import defaultdict

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
CHUNK_SIZE = 65536  # 64 KB chunks for memory-efficient hashing


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
    """Computes the SHA-256 hash of a file reading in chunks."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            hasher.update(chunk)
    return hasher.hexdigest()


def collect_split_images(split_path: Path, split_name: str, logger: Logger):
    """
    Collects images from a split directory (strictly within split_path).
    Does NOT scan parent directory or any other sibling directories.
    """
    images = []
    if not split_path.exists() or not split_path.is_dir():
        logger.log(f"[ERROR] Split path does not exist: {split_path}")
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

    # Also capture any files directly under split root (if any)
    root_files = [f for f in split_path.iterdir() if f.is_file()]
    for rf in root_files:
        images.append({
            "path": str(rf),
            "filename": rf.name,
            "split": split_name,
            "class": "_ROOT_UNASSIGNED_",
            "rel_path": str(rf.relative_to(split_path.parent))
        })

    return images


def main():
    logger = Logger()

    project_root = Path(r"D:\Areca")
    train_dir = project_root / "Data" / "train"
    test_dir = project_root / "Data" / "test"
    reports_dir = project_root / "reports"
    txt_report_file = reports_dir / "step03_exact_duplicate_audit.txt"
    json_report_file = reports_dir / "step03_exact_duplicate_audit.json"

    reports_dir.mkdir(parents=True, exist_ok=True)

    separator = "=" * 80
    sub_sep = "-" * 80

    logger.log(separator)
    logger.log("STEP 3 — TRAIN/TEST EXACT DUPLICATE AUDIT (SHA-256)")
    logger.log(separator)
    logger.log(f"Project Root: {project_root}")
    logger.log(f"Target Train Directory: {train_dir}")
    logger.log(f"Target Test Directory:  {test_dir}")
    logger.log(sub_sep)
    logger.log("CRITICAL SCOPE ENFORCEMENT:")
    logger.log("  [VERIFIED] ONLY train and test directories were analyzed.")
    logger.log("  [VERIFIED] D:\\Areca\\Data\\final_testing-20230830T042904Z-001 was ABSOLUTELY NOT accessed.")
    logger.log(separator)

    # 1. Collect images from train and test independently
    train_images = collect_split_images(train_dir, "train", logger)
    test_images = collect_split_images(test_dir, "test", logger)
    all_images = train_images + test_images

    total_train = len(train_images)
    total_test = len(test_images)
    total_images = len(all_images)

    logger.log(f"Images collected from Train: {total_train}")
    logger.log(f"Images collected from Test:  {total_test}")
    logger.log(f"Total images to hash:        {total_images}")
    logger.log(sub_sep)

    # 2. Compute SHA-256 for all images
    logger.log("Computing SHA-256 hashes across all images...")
    hash_to_images = defaultdict(list)
    hashing_errors = []

    for idx, img_info in enumerate(all_images, 1):
        try:
            h = compute_sha256(Path(img_info["path"]))
            img_info["sha256"] = h
            hash_to_images[h].append(img_info)
        except Exception as e:
            hashing_errors.append({
                "path": img_info["path"],
                "error": str(e)
            })

    total_hashed = total_images - len(hashing_errors)
    unique_hashes = len(hash_to_images)

    # 3. Categorize duplicate groups
    duplicate_groups = {h: imgs for h, imgs in hash_to_images.items() if len(imgs) > 1}
    num_duplicate_groups = len(duplicate_groups)
    images_in_duplicates = sum(len(imgs) for imgs in duplicate_groups.values())
    extra_duplicate_copies = sum(len(imgs) - 1 for imgs in duplicate_groups.values())

    # Sub-categories
    within_train_groups = []
    within_test_groups = []
    cross_split_groups = []
    class_conflict_groups = []

    for h, imgs in duplicate_groups.items():
        splits = set(img["split"] for img in imgs)
        classes = set(img["class"] for img in imgs)

        # Check for class conflict (same image under different class names)
        if len(classes) > 1:
            class_conflict_groups.append({
                "sha256": h,
                "classes": sorted(list(classes)),
                "splits": sorted(list(splits)),
                "images": imgs
            })

        # Check split location
        if splits == {"train"}:
            within_train_groups.append({
                "sha256": h,
                "classes": sorted(list(classes)),
                "count": len(imgs),
                "images": imgs
            })
        elif splits == {"test"}:
            within_test_groups.append({
                "sha256": h,
                "classes": sorted(list(classes)),
                "count": len(imgs),
                "images": imgs
            })
        elif "train" in splits and "test" in splits:
            train_files = [img for img in imgs if img["split"] == "train"]
            test_files = [img for img in imgs if img["split"] == "test"]
            cross_split_groups.append({
                "sha256": h,
                "classes": sorted(list(classes)),
                "train_count": len(train_files),
                "test_count": len(test_files),
                "train_images": train_files,
                "test_images": test_files,
                "all_images": imgs
            })

    train_test_duplicate_images_count = sum(len(g["all_images"]) for g in cross_split_groups)

    # 4. Detailed Logging of Findings
    logger.log(f"Hashing Complete:")
    logger.log(f"  - Successfully hashed:    {total_hashed} / {total_images}")
    logger.log(f"  - Hashing errors:         {len(hashing_errors)}")
    logger.log(f"  - Unique SHA-256 hashes:  {unique_hashes}")
    logger.log(f"  - Exact duplicate groups: {num_duplicate_groups}")
    logger.log(f"  - Images in duplicates:   {images_in_duplicates}")
    logger.log(f"  - Extra duplicate copies: {extra_duplicate_copies}")
    logger.log(separator)

    # A. Within-Train Duplicates
    logger.log(f"A. EXACT DUPLICATES OCCURRING ONLY WITHIN TRAIN: {len(within_train_groups)} groups")
    if within_train_groups:
        for idx, g in enumerate(within_train_groups, 1):
            logger.log(f"   Group {idx} [SHA-256: {g['sha256'][:16]}...] ({g['count']} images) | Classes: {g['classes']}")
            for img in g["images"]:
                logger.log(f"      - [{img['class']}] {img['path']}")
    else:
        logger.log("   None (No exact duplicate groups confined strictly to train)")
    logger.log(sub_sep)

    # B. Within-Test Duplicates
    logger.log(f"B. EXACT DUPLICATES OCCURRING ONLY WITHIN TEST: {len(within_test_groups)} groups")
    if within_test_groups:
        for idx, g in enumerate(within_test_groups, 1):
            logger.log(f"   Group {idx} [SHA-256: {g['sha256'][:16]}...] ({g['count']} images) | Classes: {g['classes']}")
            for img in g["images"]:
                logger.log(f"      - [{img['class']}] {img['path']}")
    else:
        logger.log("   None (No exact duplicate groups confined strictly to test)")
    logger.log(sub_sep)

    # C. Cross-Split (Train <-> Test) Duplicates (CRITICAL LEAKAGE)
    logger.log(f"C. EXACT DUPLICATES OCCURRING ACROSS TRAIN AND TEST (DATA LEAKAGE): {len(cross_split_groups)} groups")
    if cross_split_groups:
        for idx, g in enumerate(cross_split_groups, 1):
            logger.log(f"   Leakage Group {idx} [SHA-256: {g['sha256']}]:")
            logger.log(f"     Train copies ({g['train_count']}):")
            for t_img in g["train_images"]:
                logger.log(f"       * Class: {t_img['class']} | Path: {t_img['path']}")
            logger.log(f"     Test copies ({g['test_count']}):")
            for te_img in g["test_images"]:
                logger.log(f"       * Class: {te_img['class']} | Path: {te_img['path']}")
    else:
        logger.log("   None (ZERO cross-split exact duplicates detected - No exact train-test leakage)")
    logger.log(sub_sep)

    # D. Class-Conflict Duplicates
    logger.log(f"D. EXACT DUPLICATES WITH CLASS CONFLICTS (LABEL INCONSISTENCY): {len(class_conflict_groups)} groups")
    if class_conflict_groups:
        for idx, g in enumerate(class_conflict_groups, 1):
            logger.log(f"   Conflict Group {idx} [SHA-256: {g['sha256']}]:")
            logger.log(f"     Conflicting Classes: {g['classes']}")
            for img in g["images"]:
                logger.log(f"       * Split: {img['split']} | Class: {img['class']} | Path: {img['path']}")
    else:
        logger.log("   None (All duplicate instances share identical class labels)")
    logger.log(separator)

    # Decision Logic for Status
    is_pass = (
        total_hashed == total_images
        and len(hashing_errors) == 0
        and len(cross_split_groups) == 0
        and len(class_conflict_groups) == 0
    )
    status_str = "PASS" if is_pass else "REVIEW REQUIRED"

    # Required Summary Block
    logger.log("============================================================")
    logger.log("STEP 3 - EXACT DUPLICATE AUDIT SUMMARY")
    logger.log("============================================================")
    logger.log(f"Train images found:                 {total_train}")
    logger.log(f"Test images found:                  {total_test}")
    logger.log(f"Total images:                       {total_images}")
    logger.log(f"Images successfully hashed:         {total_hashed}")
    logger.log(f"Unique SHA-256 hashes:              {unique_hashes}")
    logger.log(f"Exact duplicate groups:             {num_duplicate_groups}")
    logger.log(f"Images involved in duplicates:      {images_in_duplicates}")
    logger.log(f"Extra duplicate copies:             {extra_duplicate_copies}")
    logger.log("")
    logger.log(f"Within-train duplicate groups:      {len(within_train_groups)}")
    logger.log(f"Within-test duplicate groups:       {len(within_test_groups)}")
    logger.log(f"Train-test exact duplicate groups:  {len(cross_split_groups)}")
    logger.log(f"Train-test duplicate images:        {train_test_duplicate_images_count}")
    logger.log(f"Class-conflict duplicate groups:    {len(class_conflict_groups)}")
    logger.log("")
    logger.log(f"STEP 3 STATUS:                      {status_str}")
    logger.log("")
    logger.log("Reports saved:")
    logger.log(f"  - {txt_report_file}")
    logger.log(f"  - {json_report_file}")
    logger.log("------------------------------------------------------------")
    logger.log("SCOPE CONFIRMATION:")
    logger.log("  final_testing-20230830T042904Z-001 was NOT accessed.")
    logger.log("============================================================")

    # Save TXT Report
    logger.write_to_file(txt_report_file)

    # Save JSON Report
    json_data = {
        "audit_step": "STEP 03 - Exact Duplicate Audit",
        "scope": {
            "project_root": str(project_root),
            "train_dir": str(train_dir),
            "test_dir": str(test_dir),
            "final_testing_excluded": True
        },
        "summary": {
            "train_images_found": total_train,
            "test_images_found": total_test,
            "total_images": total_images,
            "images_successfully_hashed": total_hashed,
            "hashing_errors_count": len(hashing_errors),
            "unique_sha256_hashes": unique_hashes,
            "exact_duplicate_groups_total": num_duplicate_groups,
            "images_involved_in_duplicates": images_in_duplicates,
            "extra_duplicate_copies": extra_duplicate_copies,
            "within_train_duplicate_groups_count": len(within_train_groups),
            "within_test_duplicate_groups_count": len(within_test_groups),
            "train_test_exact_duplicate_groups_count": len(cross_split_groups),
            "train_test_duplicate_images_count": train_test_duplicate_images_count,
            "class_conflict_duplicate_groups_count": len(class_conflict_groups),
            "step_3_status": status_str
        },
        "cross_split_leakage_groups": cross_split_groups,
        "class_conflict_groups": class_conflict_groups,
        "within_train_groups": within_train_groups,
        "within_test_groups": within_test_groups,
        "hashing_errors": hashing_errors
    }

    with open(json_report_file, "w", encoding="utf-8") as jf:
        json.dump(json_data, jf, indent=2)


if __name__ == "__main__":
    main()

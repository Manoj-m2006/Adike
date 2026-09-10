"""
Step 1: Train/Test Dataset Structure Audit
Script: D:\\Areca\\scripts\\step01_train_test_structure.py
Output: D:\\Areca\\reports\\step01_train_test_structure.txt

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

# Standard image extensions (case-insensitive)
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


def analyze_split(split_name: str, split_path: Path, logger: Logger):
    """Analyzes a single split (train or test) strictly within its directory."""
    split_info = {
        "exists": split_path.exists(),
        "is_dir": split_path.is_dir() if split_path.exists() else False,
        "class_counts": {},
        "all_files": [],
        "image_files": [],
        "non_image_files": [],
        "extensions": set(),
        "empty_dirs": [],
        "unexpected_nesting": [],
        "filename_to_paths": defaultdict(list),
        "duplicate_filenames": defaultdict(list),
    }

    if not split_info["exists"] or not split_info["is_dir"]:
        return split_info

    # Inspect direct children of split directory
    direct_children = list(split_path.iterdir())
    direct_subdirs = [p for p in direct_children if p.is_dir()]
    direct_files = [p for p in direct_children if p.is_file()]

    if direct_files:
        split_info["unexpected_nesting"].append(
            f"Found {len(direct_files)} file(s) directly under {split_name} root instead of inside a class folder: "
            + ", ".join([f.name for f in direct_files[:5]])
            + (f" ... and {len(direct_files) - 5} more" if len(direct_files) > 5 else "")
        )

    # Class folders are immediate subdirectories
    class_folders = sorted(direct_subdirs, key=lambda p: p.name)

    # Walk directory to detect deep nesting, empty dirs, files
    for root, dirs, files in os.walk(split_path):
        current_p = Path(root)
        rel_from_split = current_p.relative_to(split_path)

        # Check for empty directories
        if not dirs and not files:
            split_info["empty_dirs"].append(str(rel_from_split))

        # Check for unexpected deep nesting (> 1 level deep from split root)
        if len(rel_from_split.parts) > 1:
            for d in dirs:
                nested_dir_rel = rel_from_split / d
                split_info["unexpected_nesting"].append(
                    f"Subdirectory nested inside class folder: {nested_dir_rel}"
                )

        # Process files
        for f in files:
            file_p = current_p / f
            rel_file_path = file_p.relative_to(split_path)
            split_info["all_files"].append(rel_file_path)

            ext = file_p.suffix.lower()
            split_info["extensions"].add(ext if ext else "[no extension]")

            split_info["filename_to_paths"][f].append(rel_file_path)

            if ext in IMAGE_EXTENSIONS:
                split_info["image_files"].append(rel_file_path)
            else:
                split_info["non_image_files"].append(rel_file_path)

    # Identify duplicate filenames within this split
    for fname, paths in split_info["filename_to_paths"].items():
        if len(paths) > 1:
            split_info["duplicate_filenames"][fname] = paths

    # Count image files per direct class folder
    for c_dir in class_folders:
        c_name = c_dir.name
        # Count all images residing inside this class folder (including subdirectories if any)
        c_images = [
            p for p in split_info["image_files"]
            if p.parts and p.parts[0] == c_name
        ]
        split_info["class_counts"][c_name] = len(c_images)

    return split_info


def print_tree(dir_path: Path, logger: Logger, max_files_per_dir: int = 5):
    """Prints directory structure tree without loading unwanted paths."""
    if not dir_path.exists():
        logger.log(f"  [Directory Does Not Exist: {dir_path}]")
        return

    logger.log(f"  {dir_path.name}/")
    try:
        subdirs = sorted([d for d in dir_path.iterdir() if d.is_dir()], key=lambda x: x.name)
        for s in subdirs:
            files = sorted([f for f in s.iterdir() if f.is_file()], key=lambda x: x.name)
            sub_subdirs = sorted([d for d in s.iterdir() if d.is_dir()], key=lambda x: x.name)
            
            logger.log(f"    ├── {s.name}/ ({len(files)} files" + (f", {len(sub_subdirs)} subdirectories" if sub_subdirs else "") + ")")
            
            # Show sample files
            for f in files[:max_files_per_dir]:
                logger.log(f"    │   ├── {f.name}")
            if len(files) > max_files_per_dir:
                logger.log(f"    │   └── ... [{len(files) - max_files_per_dir} more files]")

            # Show nested subdirectories if present
            for nested in sub_subdirs:
                nested_files = list(nested.glob("*"))
                logger.log(f"    │   └── [NESTED DIR] {nested.name}/ ({len(nested_files)} items)")

        # Direct files under root split
        root_files = sorted([f for f in dir_path.iterdir() if f.is_file()], key=lambda x: x.name)
        if root_files:
            logger.log(f"    └── [FILES AT SPLIT ROOT]: {len(root_files)} file(s)")
            for rf in root_files[:max_files_per_dir]:
                logger.log(f"        ├── {rf.name}")
            if len(root_files) > max_files_per_dir:
                logger.log(f"        └── ... [{len(root_files) - max_files_per_dir} more files]")
    except Exception as e:
        logger.log(f"  Error reading directory tree: {e}")


def main():
    logger = Logger()

    project_root = Path(r"D:\Areca")
    train_path = project_root / "Data" / "train"
    test_path = project_root / "Data" / "test"
    report_file = project_root / "reports" / "step01_train_test_structure.txt"

    separator = "=" * 80
    sub_sep = "-" * 80

    logger.log(separator)
    logger.log("STEP 1 — TRAIN/TEST DATASET STRUCTURE AUDIT REPORT")
    logger.log(separator)
    logger.log(f"Project Root: {project_root}")
    logger.log(f"Target Train Directory: {train_path}")
    logger.log(f"Target Test Directory:  {test_path}")
    logger.log(sub_sep)
    logger.log("CRITICAL SCOPE ENFORCEMENT:")
    logger.log("  [VERIFIED] ONLY train and test directories were analyzed.")
    logger.log("  [VERIFIED] D:\\Areca\\Data\\final_testing-20230830T042904Z-001 was ABSOLUTELY NOT inspected.")
    logger.log(separator)

    # 1. Existence check
    train_exists = train_path.exists() and train_path.is_dir()
    test_exists = test_path.exists() and test_path.is_dir()

    logger.log(f"1. Train Directory Exists: {'YES' if train_exists else 'NO'} ({train_path})")
    logger.log(f"2. Test Directory Exists:  {'YES' if test_exists else 'NO'} ({test_path})")
    logger.log(sub_sep)

    # 3 & 4. Directory structures
    logger.log("3. COMPLETE DIRECTORY STRUCTURE (TRAIN):")
    print_tree(train_path, logger)
    logger.log(sub_sep)

    logger.log("4. COMPLETE DIRECTORY STRUCTURE (TEST):")
    print_tree(test_path, logger)
    logger.log(separator)

    # Perform Analysis
    train_info = analyze_split("train", train_path, logger)
    test_info = analyze_split("test", test_path, logger)

    train_classes = sorted(list(train_info["class_counts"].keys()))
    test_classes = sorted(list(test_info["class_counts"].keys()))

    # 5 & 6. Class folders
    logger.log("5. CLASS FOLDERS FOUND IN TRAIN:")
    if train_classes:
        for idx, c in enumerate(train_classes, 1):
            logger.log(f"   {idx}. {c}")
    else:
        logger.log("   None found / Directory missing")
    logger.log(sub_sep)

    logger.log("6. CLASS FOLDERS FOUND IN TEST:")
    if test_classes:
        for idx, c in enumerate(test_classes, 1):
            logger.log(f"   {idx}. {c}")
    else:
        logger.log("   None found / Directory missing")
    logger.log(sub_sep)

    # 7 & 8. Number of image files in every class
    logger.log("7. NUMBER OF IMAGE FILES IN EVERY TRAIN CLASS:")
    if train_info["class_counts"]:
        for c, cnt in train_info["class_counts"].items():
            logger.log(f"   - {c}: {cnt} images")
    else:
        logger.log("   No class image counts available")
    logger.log(sub_sep)

    logger.log("8. NUMBER OF IMAGE FILES IN EVERY TEST CLASS:")
    if test_info["class_counts"]:
        for c, cnt in test_info["class_counts"].items():
            logger.log(f"   - {c}: {cnt} images")
    else:
        logger.log("   No class image counts available")
    logger.log(sub_sep)

    # 9, 10, 11. Totals
    total_train_images = len(train_info["image_files"])
    total_test_images = len(test_info["image_files"])
    total_combined_images = total_train_images + total_test_images

    logger.log(f" 9. Total Number of Train Images:        {total_train_images}")
    logger.log(f"10. Total Number of Test Images:         {total_test_images}")
    logger.log(f"11. Total Number of Images (Train+Test): {total_combined_images}")
    logger.log(sub_sep)

    # 12. Extensions present
    all_extensions = sorted(list(train_info["extensions"] | test_info["extensions"]))
    logger.log("12. IMAGE / FILE EXTENSIONS PRESENT:")
    logger.log(f"    Train extensions: {sorted(list(train_info['extensions']))}")
    logger.log(f"    Test extensions:  {sorted(list(test_info['extensions']))}")
    logger.log(f"    Combined extensions present: {all_extensions}")
    logger.log(sub_sep)

    # 13. Non-image files present
    total_non_images = len(train_info["non_image_files"]) + len(test_info["non_image_files"])
    logger.log(f"13. NON-IMAGE FILES PRESENT: {total_non_images} found")
    if train_info["non_image_files"]:
        logger.log("    In Train:")
        for f in train_info["non_image_files"]:
            logger.log(f"      - {f}")
    if test_info["non_image_files"]:
        logger.log("    In Test:")
        for f in test_info["non_image_files"]:
            logger.log(f"      - {f}")
    if total_non_images == 0:
        logger.log("    None (All files are valid image extensions)")
    logger.log(sub_sep)

    # 14. Empty directories
    total_empty_dirs = len(train_info["empty_dirs"]) + len(test_info["empty_dirs"])
    logger.log(f"14. EMPTY DIRECTORIES: {total_empty_dirs} found")
    if train_info["empty_dirs"]:
        logger.log("    In Train:")
        for d in train_info["empty_dirs"]:
            logger.log(f"      - {d}")
    if test_info["empty_dirs"]:
        logger.log("    In Test:")
        for d in test_info["empty_dirs"]:
            logger.log(f"      - {d}")
    if total_empty_dirs == 0:
        logger.log("    None")
    logger.log(sub_sep)

    # 15. Duplicate filenames within train
    logger.log(f"15. DUPLICATE FILENAMES WITHIN TRAIN: {len(train_info['duplicate_filenames'])} duplicate filename sets")
    if train_info["duplicate_filenames"]:
        for fname, paths in train_info["duplicate_filenames"].items():
            logger.log(f"    Filename '{fname}' occurs {len(paths)} times:")
            for p in paths:
                logger.log(f"      - {p}")
    else:
        logger.log("    None (All filenames within train are unique)")
    logger.log(sub_sep)

    # 16. Duplicate filenames within test
    logger.log(f"16. DUPLICATE FILENAMES WITHIN TEST: {len(test_info['duplicate_filenames'])} duplicate filename sets")
    if test_info["duplicate_filenames"]:
        for fname, paths in test_info["duplicate_filenames"].items():
            logger.log(f"    Filename '{fname}' occurs {len(paths)} times:")
            for p in paths:
                logger.log(f"      - {p}")
    else:
        logger.log("    None (All filenames within test are unique)")
    logger.log(sub_sep)

    # 17. Filenames occurring in both train and test
    train_filenames = set(train_info["filename_to_paths"].keys())
    test_filenames = set(test_info["filename_to_paths"].keys())
    common_filenames = sorted(list(train_filenames & test_filenames))

    logger.log(f"17. FILENAMES OCCURRING IN BOTH TRAIN AND TEST: {len(common_filenames)} filenames overlap")
    if common_filenames:
        for fname in common_filenames[:20]:
            train_occurrences = [str(p) for p in train_info["filename_to_paths"][fname]]
            test_occurrences = [str(p) for p in test_info["filename_to_paths"][fname]]
            logger.log(f"    - '{fname}':")
            logger.log(f"        Train: {train_occurrences}")
            logger.log(f"        Test:  {test_occurrences}")
        if len(common_filenames) > 20:
            logger.log(f"    ... and {len(common_filenames) - 20} more overlapping filenames")
    else:
        logger.log("    None (No filename overlap between train and test)")
    logger.log(sub_sep)

    # 18. Unexpected directory nesting
    total_nesting_issues = len(train_info["unexpected_nesting"]) + len(test_info["unexpected_nesting"])
    logger.log(f"18. UNEXPECTED DIRECTORY NESTING: {total_nesting_issues} issue(s) detected")
    if train_info["unexpected_nesting"]:
        logger.log("    In Train:")
        for issue in train_info["unexpected_nesting"]:
            logger.log(f"      - {issue}")
    if test_info["unexpected_nesting"]:
        logger.log("    In Test:")
        for issue in test_info["unexpected_nesting"]:
            logger.log(f"      - {issue}")
    if total_nesting_issues == 0:
        logger.log("    None (Structure matches exact 1-level class folder hierarchy)")
    logger.log(sub_sep)

    # 19. Verify class names alignment
    classes_match = (train_classes == test_classes) and len(train_classes) > 0
    missing_in_test = sorted(list(set(train_classes) - set(test_classes)))
    missing_in_train = sorted(list(set(test_classes) - set(train_classes)))

    logger.log("19. CLASS NAMES ALIGNMENT CHECK:")
    logger.log(f"    Train Classes ({len(train_classes)}): {train_classes}")
    logger.log(f"    Test Classes  ({len(test_classes)}): {test_classes}")
    logger.log(f"    Exact Match: {'YES' if classes_match else 'NO'}")
    if missing_in_test:
        logger.log(f"    Classes in Train but missing in Test: {missing_in_test}")
    if missing_in_train:
        logger.log(f"    Classes in Test but missing in Train: {missing_in_train}")
    logger.log(sub_sep)

    # 20. Disclaimer notice
    logger.log("20. SCOPE CONFIRMATION STATEMENT:")
    logger.log("    D:\\Areca\\Data\\final_testing-20230830T042904Z-001 was NOT inspected or accessed in any way.")
    logger.log(separator)

    # Concise PASS/REVIEW Summary
    review_flags = []

    if not train_exists:
        review_flags.append("Train directory does not exist")
    if not test_exists:
        review_flags.append("Test directory does not exist")
    if not classes_match:
        review_flags.append("Train and test class names do not match")
    if total_non_images > 0:
        review_flags.append(f"{total_non_images} non-image file(s) found")
    if total_empty_dirs > 0:
        review_flags.append(f"{total_empty_dirs} empty directory/directories found")
    if total_nesting_issues > 0:
        review_flags.append(f"{total_nesting_issues} unexpected directory nesting issue(s)")
    if common_filenames:
        review_flags.append(f"{len(common_filenames)} filename overlap(s) between train and test")
    if train_info["duplicate_filenames"]:
        review_flags.append(f"{len(train_info['duplicate_filenames'])} duplicate filename(s) inside train")
    if test_info["duplicate_filenames"]:
        review_flags.append(f"{len(test_info['duplicate_filenames'])} duplicate filename(s) inside test")

    logger.log("AUDIT SUMMARY:")
    if not review_flags:
        logger.log(">>> OVERALL STATUS: [PASS] <<<")
        logger.log("All directory structures, class alignments, and filename checks passed standard structure expectations.")
    else:
        logger.log(">>> OVERALL STATUS: [REVIEW] <<<")
        logger.log("The following items require attention / review:")
        for idx, flag in enumerate(review_flags, 1):
            logger.log(f"  {idx}. [REVIEW] {flag}")

    logger.log(separator)
    logger.log(f"Report saved to: {report_file}")
    logger.log(separator)

    # Write complete report to disk
    logger.write_to_file(report_file)


if __name__ == "__main__":
    main()

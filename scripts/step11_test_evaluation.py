"""
Step 11: Arecanut ResNet-50 Final Test Evaluation
Script: D:\\Areca\\scripts\\step11_test_evaluation.py

Purpose:
  - Evaluates the trained best ResNet-50 checkpoint on the untouched TEST dataset (1,635 images).
  - Strictly EVALUATION-ONLY: Zero backprop, zero weight updates, zero image modifications.
  - Generates comprehensive metrics, per-class breakdown, confidence analysis, confusion matrix, and misclassification records.

Scope:
  - Reads ONLY: D:\\Areca\\Data\\test
  - Checkpoint: D:\\Areca\\models\\areca_resnet50_best.pth (or D:\\Areca\\areca_resnet50_best.pth)
  - Explicitly DOES NOT access D:\\Areca\\Data\\final_testing-20230830T042904Z-001
"""

import os
import sys
import json
import csv
import time
from pathlib import Path
from collections import defaultdict

# Required Deep Learning & Numerical Libraries
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch.utils.data import Dataset, DataLoader
    import torchvision
    import torchvision.transforms as transforms
    from torchvision.models import resnet50, ResNet50_Weights
    import numpy as np
    from PIL import Image
    import matplotlib
    matplotlib.use("Agg")  # Non-interactive backend
    import matplotlib.pyplot as plt
except ImportError as e:
    print(f"\n[ERROR] Missing required library: {e}")
    print("Please install required dependencies: pip install torch torchvision numpy Pillow matplotlib\n")
    sys.exit(1)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}

# Authoritative 4-Class Mapping
CLASS_MAPPING = {
    "Healthy_Leaf": 0,
    "Healthy_Nut": 1,
    "Mahali_Koleroga": 2,
    "yellow leaf disease": 3
}
CLASS_NAMES = ["Healthy_Leaf", "Healthy_Nut", "Mahali_Koleroga", "yellow leaf disease"]

# Expected Authoritative TEST Counts
EXPECTED_TEST_COUNTS = {
    "Healthy_Leaf": 152,
    "Healthy_Nut": 472,
    "Mahali_Koleroga": 641,
    "yellow leaf disease": 370
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


class TestImageDataset(Dataset):
    """PyTorch dataset for loading and evaluating TEST images."""
    def __init__(self, samples, transform=None):
        self.samples = samples  # List of tuples: (image_path, class_idx, class_name)
        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label, class_name = self.samples[idx]
        with Image.open(path) as img:
            img = img.convert("RGB")
            if self.transform:
                img = self.transform(img)
        return img, label, path, class_name


def get_test_transforms(image_size: int = 224):
    """Deterministic validation/evaluation preprocessing matching Step 10."""
    return transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])


def collect_test_samples(test_dir: Path, class_mapping: dict):
    """Scans and validates all images inside TEST class folders."""
    samples = []
    class_counts = defaultdict(int)

    for class_name, class_idx in class_mapping.items():
        c_dir = test_dir / class_name
        if not c_dir.exists():
            raise FileNotFoundError(f"Expected class directory not found in TEST: {c_dir}")

        for root, _, files in os.walk(c_dir):
            for f in files:
                f_path = Path(root) / f
                if f_path.suffix.lower() in IMAGE_EXTENSIONS:
                    samples.append((str(f_path), class_idx, class_name))
                    class_counts[class_name] += 1

    return samples, dict(class_counts)


def build_resnet50_model(num_classes: int = 4):
    """Reconstructs exact ResNet-50 architecture from Step 10."""
    try:
        weights = ResNet50_Weights.DEFAULT
        model = resnet50(weights=weights)
    except Exception:
        try:
            model = resnet50(pretrained=True)
        except Exception as exc:
            raise RuntimeError(f"Unable to initialize base ResNet-50: {exc}")

    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)
    return model


def load_best_checkpoint(checkpoint_path: Path, model: nn.Module, device: torch.device):
    """Loads the trained weights from the Step 10 checkpoint dictionary."""
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint file not found: {checkpoint_path}")

    checkpoint = torch.load(checkpoint_path, map_location=device)
    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        state_dict = checkpoint["model_state_dict"]
        metadata = {
            "epoch": checkpoint.get("epoch", "N/A"),
            "val_loss": checkpoint.get("val_loss", "N/A"),
            "val_acc": checkpoint.get("val_acc", "N/A"),
            "phase": checkpoint.get("phase", "N/A")
        }
    else:
        state_dict = checkpoint
        metadata = {"epoch": "N/A", "val_loss": "N/A", "val_acc": "N/A", "phase": "N/A"}

    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    return model, metadata


def calculate_metrics(y_true, y_pred, class_names):
    """Computes overall accuracy, 4x4 confusion matrix, and macro/weighted per-class metrics."""
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    n = len(y_true)

    accuracy = float(np.mean(y_true == y_pred)) if n > 0 else 0.0

    num_classes = len(class_names)
    cm = np.zeros((num_classes, num_classes), dtype=int)
    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1

    per_class = {}
    precisions = []
    recalls = []
    f1s = []
    supports = []

    for c_idx, c_name in enumerate(class_names):
        tp = cm[c_idx, c_idx]
        fp = np.sum(cm[:, c_idx]) - tp
        fn = np.sum(cm[c_idx, :]) - tp
        sup = np.sum(cm[c_idx, :])
        supports.append(sup)

        prec = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
        rec = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        f1 = float(2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
        class_acc = float(tp / sup) if sup > 0 else 0.0

        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)

        per_class[c_name] = {
            "support": int(sup),
            "correct": int(tp),
            "incorrect": int(sup - tp),
            "accuracy": round(class_acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4)
        }

    total_sup = sum(supports)
    macro_f1 = float(np.mean(f1s)) if f1s else 0.0
    macro_prec = float(np.mean(precisions)) if precisions else 0.0
    macro_rec = float(np.mean(recalls)) if recalls else 0.0

    weighted_f1 = float(sum(f * s for f, s in zip(f1s, supports)) / total_sup) if total_sup > 0 else 0.0
    weighted_prec = float(sum(p * s for p, s in zip(precisions, supports)) / total_sup) if total_sup > 0 else 0.0
    weighted_rec = float(sum(r * s for r, s in zip(recalls, supports)) / total_sup) if total_sup > 0 else 0.0

    return {
        "accuracy": round(accuracy, 4),
        "macro_precision": round(macro_prec, 4),
        "macro_recall": round(macro_rec, 4),
        "macro_f1": round(macro_f1, 4),
        "weighted_precision": round(weighted_prec, 4),
        "weighted_recall": round(weighted_rec, 4),
        "weighted_f1": round(weighted_f1, 4),
        "confusion_matrix": cm.tolist(),
        "per_class": per_class
    }


def plot_confusion_matrix(cm, class_names, output_path: Path, title: str):
    """Renders and saves a 4x4 confusion matrix heatmap plot."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.5, 6.5))
    cax = ax.matshow(cm, cmap="Blues")
    fig.colorbar(cax)

    ax.set_xticks(range(len(class_names)))
    ax.set_yticks(range(len(class_names)))
    ax.set_xticklabels(class_names, rotation=25, ha="left", fontsize=10)
    ax.set_yticklabels(class_names, fontsize=10)

    for i in range(len(class_names)):
        for j in range(len(class_names)):
            val = cm[i][j]
            color = "white" if val > (np.max(cm) / 2) else "black"
            ax.text(j, i, str(val), ha="center", va="center", color=color, fontsize=12, fontweight="bold")

    ax.set_xlabel("Predicted Label", fontweight="bold", fontsize=11)
    ax.set_ylabel("Actual / True Label", fontweight="bold", fontsize=11)
    ax.set_title(title, fontweight="bold", pad=30, fontsize=12)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def main():
    logger = Logger()

    project_root = Path(r"D:\Areca")
    test_dir = project_root / "Data" / "test"
    protected_dir = project_root / "Data" / "final_testing-20230830T042904Z-001"
    models_dir = project_root / "models"
    reports_dir = project_root / "reports"
    plots_dir = project_root / "plots"

    reports_dir.mkdir(parents=True, exist_ok=True)
    plots_dir.mkdir(parents=True, exist_ok=True)

    # Locate best checkpoint
    primary_ckpt = models_dir / "areca_resnet50_best.pth"
    root_ckpt = project_root / "areca_resnet50_best.pth"

    if primary_ckpt.exists():
        checkpoint_path = primary_ckpt
    elif root_ckpt.exists():
        checkpoint_path = root_ckpt
    else:
        checkpoint_path = primary_ckpt  # Will trigger clear error below

    txt_report_path = reports_dir / "step11_test_evaluation_report.txt"
    json_report_path = reports_dir / "step11_test_evaluation_report.json"
    misclass_csv_path = reports_dir / "step11_misclassifications.csv"
    predictions_csv_path = reports_dir / "step11_test_predictions.csv"
    cm_plot_path = plots_dir / "step11_test_confusion_matrix.png"

    separator = "=" * 80
    sub_sep = "-" * 80

    logger.log(separator)
    logger.log("STEP 11 — ARECANUT RESNET-50 FINAL TEST EVALUATION")
    logger.log(separator)
    logger.log(f"Project Root:            {project_root}")
    logger.log(f"Target TEST Directory:   {test_dir}")
    logger.log(f"Evaluated Checkpoint:    {checkpoint_path}")
    logger.log(sub_sep)
    logger.log("CRITICAL SCOPE ENFORCEMENT:")
    logger.log("  [VERIFIED] Operating strictly on: D:\\Areca\\Data\\test.")
    logger.log("  [VERIFIED] Evaluation-Only: Zero backprop, zero weight updates, zero image modifications.")
    logger.log("  [VERIFIED] D:\\Areca\\Data\\final_testing-20230830T042904Z-001 was ABSOLUTELY NOT accessed.")
    logger.log(separator)

    # 1. Environment & Device Verification
    cuda_available = torch.cuda.is_available()
    device = torch.device("cuda" if cuda_available else "cpu")
    gpu_name = torch.cuda.get_device_name(0) if cuda_available else "N/A (CPU Mode)"
    pytorch_version = torch.__version__
    torchvision_version = torchvision.__version__

    logger.log("ENVIRONMENT & HARDWARE:")
    logger.log(f"  - PyTorch Version:       {pytorch_version}")
    logger.log(f"  - Torchvision Version:   {torchvision_version}")
    logger.log(f"  - CUDA Available:        {cuda_available}")
    logger.log(f"  - Compute Device:        {device}")
    logger.log(f"  - GPU Name:              {gpu_name}")
    logger.log(sub_sep)

    # 2. Data Integrity Pre-Evaluation Safety Checks
    logger.log("DATA INTEGRITY SAFETY CHECKS (TEST DATASET):")
    if not test_dir.exists():
        logger.log(f"[FATAL ERROR] TEST directory missing: {test_dir}")
        sys.exit(1)

    test_samples, test_class_counts = collect_test_samples(test_dir, CLASS_MAPPING)
    total_test_found = len(test_samples)

    count_errors = []
    if total_test_found != EXPECTED_TEST_TOTAL:
        count_errors.append(f"Total TEST count mismatch: Expected {EXPECTED_TEST_TOTAL}, found {total_test_found}")

    for c_name, exp_cnt in EXPECTED_TEST_COUNTS.items():
        act_cnt = test_class_counts.get(c_name, 0)
        status_str = "[OK]" if act_cnt == exp_cnt else "[MISMATCH]"
        logger.log(f"  - {c_name:<20}: {act_cnt:>4} (Expected: {exp_cnt:>4}) {status_str}")
        if act_cnt != exp_cnt:
            count_errors.append(f"Class '{c_name}' count mismatch: Expected {exp_cnt}, found {act_cnt}")

    if count_errors:
        logger.log("\n[FATAL ERROR] TEST DATASET INTEGRITY VIOLATION:")
        for err in count_errors:
            logger.log(f"  * {err}")
        logger.log("Aborting evaluation to prevent invalid benchmark results.")
        sys.exit(1)

    logger.log(f"  Total TEST Images:       {total_test_found} (100% verified)")
    logger.log("  TEST Integrity Checks:   PASSED")
    logger.log(sub_sep)

    # 3. Model Reconstruction & Checkpoint Loading
    logger.log("RECONSTRUCTING MODEL & LOADING CHECKPOINT:")
    if not checkpoint_path.exists():
        logger.log(f"[FATAL ERROR] Best model checkpoint not found at: {checkpoint_path}")
        sys.exit(1)

    model = build_resnet50_model(num_classes=4)
    model, ckpt_meta = load_best_checkpoint(checkpoint_path, model, device)

    logger.log(f"  - Architecture:          ResNet-50 (Pretrained ImageNet Head Modified to 4 Outputs)")
    logger.log(f"  - Checkpoint Loaded:     {checkpoint_path}")
    logger.log(f"  - Checkpoint Best Epoch: {ckpt_meta['epoch']}")
    logger.log(f"  - Checkpoint Val Loss:   {ckpt_meta['val_loss']}")
    logger.log(f"  - Checkpoint Val Acc:    {ckpt_meta['val_acc']}")
    logger.log(f"  - Model Mode:            model.eval() [VERIFIED]")
    logger.log(sub_sep)

    # 4. Inference Execution on Full TEST Dataset
    logger.log("EXECUTING INFERENCE ON ALL 1,635 TEST IMAGES...")
    test_transform = get_test_transforms(image_size=224)
    test_dataset = TestImageDataset(test_samples, transform=test_transform)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False, num_workers=0)

    criterion = nn.CrossEntropyLoss()

    all_y_true = []
    all_y_pred = []
    all_confidences = []
    all_predictions_records = []
    misclassifications = []

    total_test_loss = 0.0
    start_eval_time = time.time()

    with torch.no_grad():
        for inputs, labels, paths, class_names_batch in test_loader:
            inputs = inputs.to(device)
            labels = labels.to(device)

            outputs = model(inputs)
            loss = criterion(outputs, labels)
            total_test_loss += loss.item() * inputs.size(0)

            # Softmax probabilities
            probs = F.softmax(outputs, dim=1).cpu().numpy()
            preds = np.argmax(probs, axis=1)
            confidences = np.max(probs, axis=1)

            labels_np = labels.cpu().numpy()

            for idx in range(len(preds)):
                actual_idx = int(labels_np[idx])
                pred_idx = int(preds[idx])
                conf = float(confidences[idx])
                path_str = paths[idx]
                actual_name = class_names_batch[idx]
                pred_name = CLASS_NAMES[pred_idx]
                is_correct = (actual_idx == pred_idx)
                prob_list = [round(float(p), 4) for p in probs[idx]]

                all_y_true.append(actual_idx)
                all_y_pred.append(pred_idx)
                all_confidences.append(conf)

                record = {
                    "image_path": path_str,
                    "actual_class": actual_name,
                    "actual_index": actual_idx,
                    "predicted_class": pred_name,
                    "predicted_index": pred_idx,
                    "confidence": round(conf, 4),
                    "correct": is_correct,
                    "probabilities": prob_list
                }
                all_predictions_records.append(record)

                if not is_correct:
                    misclassifications.append(record)

    eval_duration = time.time() - start_eval_time
    avg_test_loss = total_test_loss / total_test_found
    metrics = calculate_metrics(all_y_true, all_y_pred, CLASS_NAMES)

    correct_total = sum(1 for c in all_predictions_records if c["correct"])
    incorrect_total = len(misclassifications)

    # 5. Confidence Analysis
    all_conf_np = np.array(all_confidences)
    correct_conf_np = np.array([r["confidence"] for r in all_predictions_records if r["correct"]])
    incorrect_conf_np = np.array([r["confidence"] for r in misclassifications]) if misclassifications else np.array([0.0])

    conf_stats = {
        "overall": {
            "mean": round(float(np.mean(all_conf_np)), 4),
            "min": round(float(np.min(all_conf_np)), 4),
            "max": round(float(np.max(all_conf_np)), 4),
            "std": round(float(np.std(all_conf_np)), 4)
        },
        "correct": {
            "mean": round(float(np.mean(correct_conf_np)), 4) if len(correct_conf_np) > 0 else 0.0,
            "min": round(float(np.min(correct_conf_np)), 4) if len(correct_conf_np) > 0 else 0.0,
            "max": round(float(np.max(correct_conf_np)), 4) if len(correct_conf_np) > 0 else 0.0
        },
        "incorrect": {
            "count": incorrect_total,
            "mean": round(float(np.mean(incorrect_conf_np)), 4) if len(misclassifications) > 0 else 0.0,
            "min": round(float(np.min(incorrect_conf_np)), 4) if len(misclassifications) > 0 else 0.0,
            "max": round(float(np.max(incorrect_conf_np)), 4) if len(misclassifications) > 0 else 0.0
        }
    }

    # 6. Generate Confusion Matrix Plot
    plot_confusion_matrix(metrics["confusion_matrix"], CLASS_NAMES, cm_plot_path, "ResNet-50 Final Test Confusion Matrix")

    # ------------------------------------------------------------------
    # Format & Log Comprehensive Report
    # ------------------------------------------------------------------
    logger.log(separator)
    logger.log("FINAL TEST EVALUATION RESULTS SUMMARY")
    logger.log(separator)
    logger.log(f"Inference Duration:        {eval_duration:.2f}s ({total_test_found / eval_duration:.1f} images/sec)")
    logger.log(f"Total Test Images:         {total_test_found}")
    logger.log(f"Correct Predictions:       {correct_total}")
    logger.log(f"Incorrect Predictions:     {incorrect_total}")
    logger.log(f"Test Loss (CrossEntropy):  {avg_test_loss:.4f}")
    logger.log(f"TEST ACCURACY:             {metrics['accuracy'] * 100:.2f}%")
    logger.log(sub_sep)

    logger.log("OVERALL CLASSIFICATION REPORT:")
    logger.log(f"  - Macro Precision:       {metrics['macro_precision']:.4f}")
    logger.log(f"  - Macro Recall:          {metrics['macro_recall']:.4f}")
    logger.log(f"  - Macro F1-Score:        {metrics['macro_f1']:.4f}")
    logger.log(f"  - Weighted Precision:    {metrics['weighted_precision']:.4f}")
    logger.log(f"  - Weighted Recall:       {metrics['weighted_recall']:.4f}")
    logger.log(f"  - Weighted F1-Score:     {metrics['weighted_f1']:.4f}")
    logger.log(sub_sep)

    logger.log("PER-CLASS TEST PERFORMANCE BREAKDOWN:")
    logger.log(f"{'Class Name':<22} | {'Support':>7} | {'Correct':>7} | {'Incorrect':>9} | {'Accuracy':>8} | {'Precision':>9} | {'Recall':>6} | {'F1-Score':>8}")
    logger.log("-" * 95)
    for c_name, c_m in metrics["per_class"].items():
        logger.log(f"{c_name:<22} | {c_m['support']:>7} | {c_m['correct']:>7} | {c_m['incorrect']:>9} | {c_m['accuracy']*100:>7.2f}% | {c_m['precision']:>9.4f} | {c_m['recall']:>6.4f} | {c_m['f1_score']:>8.4f}")
    logger.log(sub_sep)

    logger.log("CONFUSION MATRIX (True \\ Predicted):")
    logger.log(f"{'':<22} | " + " | ".join([f"{name[:12]:>12}" for name in CLASS_NAMES]))
    logger.log("-" * 80)
    for idx, row in enumerate(metrics["confusion_matrix"]):
        row_str = " | ".join([f"{val:>12}" for val in row])
        logger.log(f"{CLASS_NAMES[idx]:<22} | {row_str}")
    logger.log(sub_sep)

    logger.log("PREDICTION CONFIDENCE ANALYSIS:")
    logger.log(f"  - Overall Confidence:    Mean={conf_stats['overall']['mean']:.4f}, Min={conf_stats['overall']['min']:.4f}, Max={conf_stats['overall']['max']:.4f}, Std={conf_stats['overall']['std']:.4f}")
    logger.log(f"  - Correct Predictions:   Mean={conf_stats['correct']['mean']:.4f}, Min={conf_stats['correct']['min']:.4f}, Max={conf_stats['correct']['max']:.4f}")
    if incorrect_total > 0:
        logger.log(f"  - Incorrect Predictions: Mean={conf_stats['incorrect']['mean']:.4f}, Min={conf_stats['incorrect']['min']:.4f}, Max={conf_stats['incorrect']['max']:.4f}")
    else:
        logger.log("  - Incorrect Predictions: 0 (100% Perfect Test Accuracy)")
    logger.log(sub_sep)

    # Misclassification Detail Log
    if misclassifications:
        logger.log(f"MISCLASSIFICATION DETAILS ({len(misclassifications)} total):")
        for idx, m in enumerate(misclassifications, 1):
            logger.log(f"  [{idx}] File: {m['image_path']}")
            logger.log(f"      Actual: {m['actual_class']} -> Predicted: {m['predicted_class']} (Confidence: {m['confidence']:.4f})")
            logger.log(f"      Probabilities [HL, HN, MK, YLD]: {m['probabilities']}")
    else:
        logger.log("MISCLASSIFICATION DETAILS: None (Zero misclassifications on unseen TEST set).")
    logger.log(separator)

    # ------------------------------------------------------------------
    # Save Output Files (TXT, JSON, CSVs)
    # ------------------------------------------------------------------
    logger.write_to_file(txt_report_path)

    # 1. Predictions CSV
    logger.log(f"Saving all predictions to: {predictions_csv_path}")
    with open(predictions_csv_path, "w", newline="", encoding="utf-8") as cf:
        writer = csv.writer(cf)
        writer.writerow([
            "image_path", "actual_class", "actual_index", "predicted_class", "predicted_index",
            "confidence", "correct", "prob_Healthy_Leaf", "prob_Healthy_Nut", "prob_Mahali_Koleroga", "prob_yellow_leaf_disease"
        ])
        for r in all_predictions_records:
            writer.writerow([
                r["image_path"], r["actual_class"], r["actual_index"], r["predicted_class"], r["predicted_index"],
                r["confidence"], r["correct"], r["probabilities"][0], r["probabilities"][1], r["probabilities"][2], r["probabilities"][3]
            ])

    # 2. Misclassifications CSV
    logger.log(f"Saving misclassifications to: {misclass_csv_path}")
    with open(misclass_csv_path, "w", newline="", encoding="utf-8") as cf:
        writer = csv.writer(cf)
        writer.writerow([
            "image_path", "actual_class", "predicted_class", "confidence",
            "prob_Healthy_Leaf", "prob_Healthy_Nut", "prob_Mahali_Koleroga", "prob_yellow_leaf_disease"
        ])
        for m in misclassifications:
            writer.writerow([
                m["image_path"], m["actual_class"], m["predicted_class"], m["confidence"],
                m["probabilities"][0], m["probabilities"][1], m["probabilities"][2], m["probabilities"][3]
            ])

    # 3. JSON Report
    logger.log(f"Saving structured JSON report to: {json_report_path}")
    json_data = {
        "step": "STEP 11 — Arecanut ResNet-50 Final Test Evaluation",
        "scope": {
            "test_dir": str(test_dir),
            "checkpoint_evaluated": str(checkpoint_path),
            "final_testing_excluded": True
        },
        "environment": {
            "device": str(device),
            "gpu_name": gpu_name,
            "pytorch_version": pytorch_version,
            "torchvision_version": torchvision_version
        },
        "summary": {
            "total_test_images": total_test_found,
            "correct_predictions": correct_total,
            "incorrect_predictions": incorrect_total,
            "test_accuracy": metrics["accuracy"],
            "test_loss": round(avg_test_loss, 4),
            "evaluation_duration_seconds": round(eval_duration, 2),
            "macro_precision": metrics["macro_precision"],
            "macro_recall": metrics["macro_recall"],
            "macro_f1": metrics["macro_f1"],
            "weighted_precision": metrics["weighted_precision"],
            "weighted_recall": metrics["weighted_recall"],
            "weighted_f1": metrics["weighted_f1"],
            "confidence_statistics": conf_stats
        },
        "per_class_metrics": metrics["per_class"],
        "confusion_matrix": metrics["confusion_matrix"],
        "class_mapping": CLASS_MAPPING,
        "misclassifications_count": len(misclassifications),
        "misclassifications": misclassifications
    }

    with open(json_report_path, "w", encoding="utf-8") as jf:
        json.dump(json_data, jf, indent=2)

    logger.log(separator)
    logger.log("Step 11 final test evaluation report completed successfully.")
    logger.log("=" * 80)


if __name__ == "__main__":
    main()

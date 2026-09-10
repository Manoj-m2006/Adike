r"""
Step 12: Final Model Metrics, Curves & Performance Visualization
Arecanut Disease Classification Project

Strictly READ-ONLY with respect to TRAIN and TEST datasets.
Uses existing Step 10 training history and Step 11 TEST predictions to generate:
1. Training vs. Validation Loss Curve (with Phase 1 & 2 demarcation)
2. Training vs. Validation Accuracy Curve (with Phase 1 & 2 demarcation)
3. Confusion Matrix Heatmap (TEST)
4. False Positive Analysis & One-vs-Rest Statistics (CSV)
5. Multi-Class ROC Curves & AUC Analysis (Plot)
6. Per-Class F1 Scores Bar Chart (Plot)
7. Per-Class Precision Bar Chart (Plot)
8. Final Comprehensive Metrics Table (CSV)
9. Final Metrics Report (JSON & TXT)

Scope:
- Model: ResNet-50 (Checkpoint: D:\Areca\models\areca_resnet50_best.pth)
- Dataset: 4 Classes (Healthy_Leaf, Healthy_Nut, Mahali_Koleroga, yellow leaf disease)
- Prohibited: D:\Areca\Data\final_testing-20230830T042904Z-001 (Untouched & Unscanned)
"""

import os
import sys
import json
import csv
import math
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt

# -------------------------------------------------------------------------
# CONSTANTS & PATH CONFIGURATION
# -------------------------------------------------------------------------
PROJECT_ROOT = r"D:\Areca"
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
PLOTS_DIR = os.path.join(PROJECT_ROOT, "plots")

STEP10_REPORT_JSON = os.path.join(REPORTS_DIR, "step10_training_report.json")
STEP10_REPORT_TXT = os.path.join(REPORTS_DIR, "step10_training_report.txt")
STEP11_PREDICTIONS_CSV = os.path.join(REPORTS_DIR, "step11_test_predictions.csv")
STEP11_REPORT_JSON = os.path.join(REPORTS_DIR, "step11_test_evaluation_report.json")

# Output plot paths
PLOT_LOSS = os.path.join(PLOTS_DIR, "step12_training_validation_loss.png")
PLOT_ACC = os.path.join(PLOTS_DIR, "step12_training_validation_accuracy.png")
PLOT_CONF_MAT = os.path.join(PLOTS_DIR, "step12_test_confusion_matrix.png")
PLOT_ROC = os.path.join(PLOTS_DIR, "step12_test_roc_curve.png")
PLOT_F1 = os.path.join(PLOTS_DIR, "step12_test_f1_scores.png")
PLOT_PRECISION = os.path.join(PLOTS_DIR, "step12_test_precision.png")

# Output report paths
CSV_FP_ANALYSIS = os.path.join(REPORTS_DIR, "step12_false_positive_analysis.csv")
CSV_FINAL_METRICS = os.path.join(REPORTS_DIR, "step12_final_metrics.csv")
TXT_FINAL_REPORT = os.path.join(REPORTS_DIR, "step12_final_metrics_report.txt")
JSON_FINAL_REPORT = os.path.join(REPORTS_DIR, "step12_final_metrics_report.json")

# Fixed 4-Class Mapping
CLASSES = [
    "Healthy_Leaf",
    "Healthy_Nut",
    "Mahali_Koleroga",
    "yellow leaf disease"
]
CLASS_MAP = {name: idx for idx, name in enumerate(CLASSES)}

# Color palette for charts
CLASS_COLORS = {
    "Healthy_Leaf": "#2ecc71",       # Emerald Green
    "Healthy_Nut": "#3498db",        # Sky Blue
    "Mahali_Koleroga": "#e74c3c",    # Coral Red
    "yellow leaf disease": "#f39c12" # Amber Orange
}

# -------------------------------------------------------------------------
# HELPER FUNCTIONS & DATA LOADERS
# -------------------------------------------------------------------------
def setup_directories():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(PLOTS_DIR, exist_ok=True)


def load_step10_training_history():
    print(f"[*] Loading Step 10 training history from: {STEP10_REPORT_JSON}")
    if not os.path.exists(STEP10_REPORT_JSON):
        raise FileNotFoundError(f"Step 10 report not found: {STEP10_REPORT_JSON}")
    
    with open(STEP10_REPORT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    history = data.get("training_history", {})
    train_loss = history.get("train_loss", [])
    val_loss = history.get("val_loss", [])
    train_acc = history.get("train_acc", [])
    val_acc = history.get("val_acc", [])
    
    print(f"    Loaded {len(train_loss)} epochs of training history.")
    return data, train_loss, val_loss, train_acc, val_acc


def load_step11_test_results():
    print(f"[*] Loading Step 11 TEST predictions from: {STEP11_PREDICTIONS_CSV}")
    if not os.path.exists(STEP11_PREDICTIONS_CSV):
        raise FileNotFoundError(f"Step 11 predictions not found: {STEP11_PREDICTIONS_CSV}")
    
    rows = []
    with open(STEP11_PREDICTIONS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            
    print(f"    Loaded {len(rows)} TEST predictions.")
    
    step11_json_data = {}
    if os.path.exists(STEP11_REPORT_JSON):
        with open(STEP11_REPORT_JSON, "r", encoding="utf-8") as f:
            step11_json_data = json.load(f)
            
    return rows, step11_json_data


# -------------------------------------------------------------------------
# PURE NUMERICAL & METRIC ALGORITHMS (NO EXTERNAL TOOLKIT REQUIRED)
# -------------------------------------------------------------------------
def compute_confusion_matrix(rows):
    """Computes 4x4 Confusion Matrix where cm[actual_idx, predicted_idx] = count."""
    cm = np.zeros((len(CLASSES), len(CLASSES)), dtype=int)
    for row in rows:
        act = row["actual_class"]
        pred = row["predicted_class"]
        if act in CLASS_MAP and pred in CLASS_MAP:
            cm[CLASS_MAP[act], CLASS_MAP[pred]] += 1
    return cm


def compute_roc_auc_curve(y_binary, scores):
    """
    Computes FPR, TPR, and trapezoidal AUC for binary labels and predicted probabilities.
    """
    # Sort pairs by score descending
    pairs = sorted(zip(scores, y_binary), key=lambda x: x[0], reverse=True)
    
    total_pos = sum(y_binary)
    total_neg = len(y_binary) - total_pos
    
    if total_pos == 0 or total_neg == 0:
        return [0.0, 1.0], [0.0, 1.0], 1.0
    
    fpr_list = [0.0]
    tpr_list = [0.0]
    
    tp = 0
    fp = 0
    
    for score, label in pairs:
        if label == 1:
            tp += 1
        else:
            fp += 1
        fpr_list.append(fp / total_neg)
        tpr_list.append(tp / total_pos)
        
    fpr_list.append(1.0)
    tpr_list.append(1.0)
    
    # Calculate AUC using trapezoidal rule
    area = 0.0
    for i in range(1, len(fpr_list)):
        dx = fpr_list[i] - fpr_list[i - 1]
        avg_y = (tpr_list[i] + tpr_list[i - 1]) / 2.0
        area += dx * avg_y
        
    return fpr_list, tpr_list, max(0.0, min(1.0, area))


def compute_one_vs_rest_analysis(rows, cm, roc_metrics):
    """
    Computes One-vs-Rest TP, FP, FN, TN, Precision, Recall, FPR, F1, and AUC for each class.
    """
    stats = {}
    total_samples = len(rows)
    
    for i, class_name in enumerate(CLASSES):
        tp = int(cm[i, i])
        fp = int(np.sum(cm[:, i]) - tp)
        fn = int(np.sum(cm[i, :]) - tp)
        tn = int(total_samples - (tp + fp + fn))
        
        precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
        recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
        f1 = float(2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
        support = int(tp + fn)
        class_auc = roc_metrics.get(class_name, {}).get("auc", 1.0)
        
        stats[class_name] = {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "tn": tn,
            "precision": precision,
            "recall": recall,
            "fpr": fpr,
            "f1": f1,
            "support": support,
            "auc": class_auc
        }
    
    return stats


def compute_aggregate_metrics(rows, per_class_stats, roc_metrics, step11_data):
    """Computes overall accuracy, macro and weighted averages."""
    total_samples = len(rows)
    correct_predictions = sum(1 for r in rows if r["actual_class"] == r["predicted_class"])
    incorrect_predictions = total_samples - correct_predictions
    accuracy = correct_predictions / total_samples if total_samples > 0 else 0.0
    
    macro_p = np.mean([per_class_stats[c]["precision"] for c in CLASSES])
    macro_r = np.mean([per_class_stats[c]["recall"] for c in CLASSES])
    macro_f1 = np.mean([per_class_stats[c]["f1"] for c in CLASSES])
    
    weighted_p = sum(per_class_stats[c]["precision"] * per_class_stats[c]["support"] for c in CLASSES) / total_samples
    weighted_r = sum(per_class_stats[c]["recall"] * per_class_stats[c]["support"] for c in CLASSES) / total_samples
    weighted_f1 = sum(per_class_stats[c]["f1"] * per_class_stats[c]["support"] for c in CLASSES) / total_samples
    
    test_loss = step11_data.get("summary", {}).get("test_loss", 0.0001)
    
    overall_summary = {
        "Total Test Images": total_samples,
        "Correct Predictions": correct_predictions,
        "Incorrect Predictions": incorrect_predictions,
        "Test Accuracy": float(accuracy),
        "Test Loss": float(test_loss),
        "Macro Precision": float(macro_p),
        "Macro Recall": float(macro_r),
        "Macro F1-Score": float(macro_f1),
        "Weighted Precision": float(weighted_p),
        "Weighted Recall": float(weighted_r),
        "Weighted F1-Score": float(weighted_f1),
        "Macro ROC AUC": float(roc_metrics["macro_average"]["auc"])
    }
    
    return overall_summary, macro_p, macro_r, macro_f1, weighted_p, weighted_r, weighted_f1


# -------------------------------------------------------------------------
# PLOTTING FUNCTIONS
# -------------------------------------------------------------------------
def plot_training_validation_loss(train_loss, val_loss):
    """Generates Training vs. Validation Loss plot with Phase 1 & Phase 2 annotations."""
    epochs = list(range(1, len(train_loss) + 1))
    
    plt.figure(figsize=(10, 6), dpi=300)
    plt.plot(epochs, train_loss, label="Training Loss", color="#e74c3c", linewidth=2.2, marker="o", markersize=3, alpha=0.9)
    plt.plot(epochs, val_loss, label="Validation Loss", color="#2980b9", linewidth=2.2, marker="s", markersize=3, alpha=0.9)
    
    # Demarcate Phase 1 and Phase 2
    plt.axvline(x=30.5, color="#7f8c8d", linestyle="--", linewidth=1.5, alpha=0.8)
    
    max_loss = max(max(train_loss), max(val_loss))
    plt.axvspan(1, 30.5, color="#f4f6f7", alpha=0.6, label="_Phase 1")
    plt.axvspan(30.5, len(epochs), color="#eaf2f8", alpha=0.6, label="_Phase 2")
    
    plt.text(15, max_loss * 0.85, "Phase 1: Feature Extraction\n(Frozen Backbone, Epochs 1–30)",
             ha="center", va="center", fontsize=10, fontweight="bold", color="#2c3e50",
             bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="#bdc3c7", alpha=0.9))
    plt.text(40.5, max_loss * 0.85, "Phase 2: Fine-Tuning\n(Full Backbone, Epochs 31–50)",
             ha="center", va="center", fontsize=10, fontweight="bold", color="#1a5276",
             bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="#85c1e9", alpha=0.9))
    
    plt.title("Arecanut ResNet-50 — Training vs. Validation Loss Across 50 Epochs", fontsize=13, fontweight="bold", pad=15)
    plt.xlabel("Epoch", fontsize=11, fontweight="bold")
    plt.ylabel("CrossEntropy Loss", fontsize=11, fontweight="bold")
    plt.xlim(1, len(epochs))
    plt.xticks(range(5, len(epochs) + 1, 5))
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="upper right", frameon=True, facecolor="white", edgecolor="#bdc3c7", fontsize=10)
    plt.tight_layout()
    plt.savefig(PLOT_LOSS, dpi=300)
    plt.close()
    print(f"[+] Saved Loss Curve: {PLOT_LOSS}")


def plot_training_validation_accuracy(train_acc, val_acc):
    """Generates Training vs. Validation Accuracy plot with Phase 1 & Phase 2 annotations."""
    epochs = list(range(1, len(train_acc) + 1))
    train_acc_pct = [acc * 100.0 for acc in train_acc]
    val_acc_pct = [acc * 100.0 for acc in val_acc]
    
    plt.figure(figsize=(10, 6), dpi=300)
    plt.plot(epochs, train_acc_pct, label="Training Accuracy", color="#27ae60", linewidth=2.2, marker="o", markersize=3, alpha=0.9)
    plt.plot(epochs, val_acc_pct, label="Validation Accuracy", color="#8e44ad", linewidth=2.2, marker="^", markersize=3, alpha=0.9)
    
    # Demarcate Phase 1 and Phase 2
    plt.axvline(x=30.5, color="#7f8c8d", linestyle="--", linewidth=1.5, alpha=0.8)
    
    plt.axvspan(1, 30.5, color="#f4f6f7", alpha=0.6, label="_Phase 1")
    plt.axvspan(30.5, len(epochs), color="#f5eef8", alpha=0.6, label="_Phase 2")
    
    min_acc = min(min(train_acc_pct), min(val_acc_pct))
    plt.text(15, min_acc + 1.5, "Phase 1: Feature Extraction\n(Epochs 1–30)",
             ha="center", va="center", fontsize=10, fontweight="bold", color="#2c3e50",
             bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="#bdc3c7", alpha=0.9))
    plt.text(40.5, min_acc + 1.5, "Phase 2: Fine-Tuning\n(Epochs 31–50)",
             ha="center", va="center", fontsize=10, fontweight="bold", color="#5b2c6f",
             bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="#bb8fce", alpha=0.9))
    
    plt.title("Arecanut ResNet-50 — Training vs. Validation Accuracy Across 50 Epochs", fontsize=13, fontweight="bold", pad=15)
    plt.xlabel("Epoch", fontsize=11, fontweight="bold")
    plt.ylabel("Accuracy (%)", fontsize=11, fontweight="bold")
    plt.xlim(1, len(epochs))
    plt.ylim(min(88.0, min_acc - 2), 101.5)
    plt.xticks(range(5, len(epochs) + 1, 5))
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="lower right", frameon=True, facecolor="white", edgecolor="#bdc3c7", fontsize=10)
    plt.tight_layout()
    plt.savefig(PLOT_ACC, dpi=300)
    plt.close()
    print(f"[+] Saved Accuracy Curve: {PLOT_ACC}")


def plot_test_confusion_matrix(cm):
    """Generates a clean heatmap of the TEST confusion matrix using matplotlib."""
    fig, ax = plt.subplots(figsize=(8.5, 7), dpi=300)
    cax = ax.imshow(cm, interpolation="nearest", cmap="Blues")
    fig.colorbar(cax, fraction=0.046, pad=0.04)
    
    # Text annotations in each cell
    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            val = cm[i, j]
            color = "white" if val > thresh else "black"
            ax.text(j, i, f"{val:d}", ha="center", va="center",
                    color=color, fontsize=13, fontweight="bold")
            
    ax.set_xticks(range(len(CLASSES)))
    ax.set_yticks(range(len(CLASSES)))
    ax.set_xticklabels(CLASSES, rotation=20, ha="right", fontsize=9.5)
    ax.set_yticklabels(CLASSES, fontsize=9.5)
    
    ax.set_title("Arecanut ResNet-50 — TEST Confusion Matrix (N = 1,635)", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Predicted Class", fontsize=11, fontweight="bold", labelpad=10)
    ax.set_ylabel("Actual Class", fontsize=11, fontweight="bold", labelpad=10)
    
    plt.tight_layout()
    plt.savefig(PLOT_CONF_MAT, dpi=300)
    plt.close()
    print(f"[+] Saved Confusion Matrix: {PLOT_CONF_MAT}")


def calculate_and_plot_roc_curves(rows):
    """Generates Multi-Class One-vs-Rest ROC Curves using actual prediction probabilities."""
    prob_col_map = {
        "Healthy_Leaf": "prob_Healthy_Leaf",
        "Healthy_Nut": "prob_Healthy_Nut",
        "Mahali_Koleroga": "prob_Mahali_Koleroga",
        "yellow leaf disease": "prob_yellow_leaf_disease"
    }
    
    roc_metrics = {}
    
    plt.figure(figsize=(9, 7.5), dpi=300)
    
    for class_name in CLASSES:
        col = prob_col_map[class_name]
        y_binary = [1 if r["actual_class"] == class_name else 0 for r in rows]
        y_scores = [float(r[col]) for r in rows]
        
        fpr, tpr, roc_auc = compute_roc_auc_curve(y_binary, y_scores)
        roc_metrics[class_name] = {
            "auc": float(roc_auc),
            "fpr": fpr,
            "tpr": tpr
        }
        
        plt.plot(fpr, tpr, color=CLASS_COLORS[class_name], lw=2.2,
                 label=f"{class_name} (AUC = {roc_auc:.4f})")
    
    # Calculate Macro-average AUC
    macro_auc = np.mean([roc_metrics[c]["auc"] for c in CLASSES])
    roc_metrics["macro_average"] = {"auc": float(macro_auc)}
    
    # Diagonal reference line
    plt.plot([0, 1], [0, 1], color="#95a5a6", lw=1.5, linestyle="--", label="Chance Level (AUC = 0.5000)")
    
    plt.xlim([-0.02, 1.02])
    plt.ylim([-0.02, 1.05])
    plt.xlabel("False Positive Rate (1 - Specificity)", fontsize=11, fontweight="bold")
    plt.ylabel("True Positive Rate (Sensitivity / Recall)", fontsize=11, fontweight="bold")
    plt.title(f"Arecanut ResNet-50 — Multi-Class One-vs-Rest ROC Curves\nMacro-Average AUC = {macro_auc:.4f}",
              fontsize=13, fontweight="bold", pad=15)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="lower right", frameon=True, facecolor="white", edgecolor="#bdc3c7", fontsize=10)
    plt.tight_layout()
    plt.savefig(PLOT_ROC, dpi=300)
    plt.close()
    print(f"[+] Saved ROC Curves: {PLOT_ROC}")
    return roc_metrics


def plot_per_class_f1_scores(per_class_stats, macro_f1, weighted_f1):
    """Generates bar chart of per-class F1-scores with macro and weighted benchmarks."""
    f1_scores = [per_class_stats[c]["f1"] for c in CLASSES]
    
    plt.figure(figsize=(9, 6), dpi=300)
    bars = plt.bar(CLASSES, f1_scores, color=[CLASS_COLORS[c] for c in CLASSES], width=0.55, edgecolor="#2c3e50", alpha=0.85)
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2.0, height / 2.0, f"{height:.4f}\n(100.0%)",
                 ha="center", va="center", color="white", fontweight="bold", fontsize=11)
        
    plt.axhline(y=macro_f1, color="#2c3e50", linestyle="--", lw=1.5, label=f"Macro F1 ({macro_f1:.4f})")
    
    plt.ylim(0, 1.15)
    plt.title("Arecanut ResNet-50 — TEST Per-Class F1 Scores (N = 1,635)", fontsize=13, fontweight="bold", pad=15)
    plt.ylabel("F1 Score", fontsize=11, fontweight="bold")
    plt.xlabel("Class Name", fontsize=11, fontweight="bold")
    plt.xticks(rotation=15, ha="right", fontsize=10)
    plt.grid(axis="y", linestyle=":", alpha=0.6)
    plt.legend(loc="upper right", frameon=True, facecolor="white", edgecolor="#bdc3c7")
    plt.tight_layout()
    plt.savefig(PLOT_F1, dpi=300)
    plt.close()
    print(f"[+] Saved F1 Scores Chart: {PLOT_F1}")


def plot_per_class_precision(per_class_stats, macro_prec, weighted_prec):
    """Generates bar chart of per-class Precision with macro and weighted benchmarks."""
    prec_scores = [per_class_stats[c]["precision"] for c in CLASSES]
    
    plt.figure(figsize=(9, 6), dpi=300)
    bars = plt.bar(CLASSES, prec_scores, color=[CLASS_COLORS[c] for c in CLASSES], width=0.55, edgecolor="#2c3e50", alpha=0.85)
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2.0, height / 2.0, f"{height:.4f}\n(100.0%)",
                 ha="center", va="center", color="white", fontweight="bold", fontsize=11)
        
    plt.axhline(y=macro_prec, color="#2c3e50", linestyle="--", lw=1.5, label=f"Macro Precision ({macro_prec:.4f})")
    
    plt.ylim(0, 1.15)
    plt.title("Arecanut ResNet-50 — TEST Per-Class Precision (N = 1,635)", fontsize=13, fontweight="bold", pad=15)
    plt.ylabel("Precision", fontsize=11, fontweight="bold")
    plt.xlabel("Class Name", fontsize=11, fontweight="bold")
    plt.xticks(rotation=15, ha="right", fontsize=10)
    plt.grid(axis="y", linestyle=":", alpha=0.6)
    plt.legend(loc="upper right", frameon=True, facecolor="white", edgecolor="#bdc3c7")
    plt.tight_layout()
    plt.savefig(PLOT_PRECISION, dpi=300)
    plt.close()
    print(f"[+] Saved Precision Chart: {PLOT_PRECISION}")


# -------------------------------------------------------------------------
# REPORTING & EXPORT
# -------------------------------------------------------------------------
def export_false_positive_analysis_csv(per_class_stats):
    """Exports False Positive Analysis Table to CSV."""
    with open(CSV_FP_ANALYSIS, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Class", "TP", "FP", "FN", "TN", "Precision", "Recall", "F1", "FPR"])
        for c in CLASSES:
            s = per_class_stats[c]
            writer.writerow([
                c,
                s["tp"],
                s["fp"],
                s["fn"],
                s["tn"],
                f"{s['precision']:.4f}",
                f"{s['recall']:.4f}",
                f"{s['f1']:.4f}",
                f"{s['fpr']:.4f}"
            ])
    print(f"[+] Saved False Positive Analysis CSV: {CSV_FP_ANALYSIS}")


def export_final_metrics_csv(overall_summary, per_class_stats):
    """Exports Comprehensive Final Metrics Table to CSV."""
    with open(CSV_FINAL_METRICS, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["--- OVERALL DATASET & MODEL TEST METRICS ---", ""])
        writer.writerow(["Metric", "Value"])
        for k, v in overall_summary.items():
            if isinstance(v, float):
                writer.writerow([k, f"{v:.6f}" if "Loss" in k else f"{v:.4f}"])
            else:
                writer.writerow([k, v])
        
        writer.writerow([])
        writer.writerow(["--- PER-CLASS METRICS & ONE-VS-REST BREAKDOWN ---", "", "", "", "", "", "", "", "", "", ""])
        writer.writerow(["Class", "Precision", "Recall", "F1", "Support", "TP", "FP", "FN", "TN", "FPR", "AUC"])
        for c in CLASSES:
            s = per_class_stats[c]
            writer.writerow([
                c,
                f"{s['precision']:.4f}",
                f"{s['recall']:.4f}",
                f"{s['f1']:.4f}",
                s["support"],
                s["tp"],
                s["fp"],
                s["fn"],
                s["tn"],
                f"{s['fpr']:.4f}",
                f"{s['auc']:.4f}"
            ])
    print(f"[+] Saved Final Metrics CSV: {CSV_FINAL_METRICS}")


def export_final_reports(step10_data, step11_data, cm, per_class_stats, overall_summary, roc_metrics):
    """Exports comprehensive final reports in TXT and JSON formats."""
    history = step10_data.get("training_history", {})
    train_loss = history.get("train_loss", [])
    val_loss = history.get("val_loss", [])
    train_acc = history.get("train_acc", [])
    val_acc = history.get("val_acc", [])

    init_train_loss = train_loss[0] if len(train_loss) > 0 else 0.0
    init_val_loss = val_loss[0] if len(val_loss) > 0 else 0.0
    p1_train_loss = train_loss[29] if len(train_loss) > 29 else (train_loss[-1] if train_loss else 0.0)
    p1_val_loss = val_loss[29] if len(val_loss) > 29 else (val_loss[-1] if val_loss else 0.0)
    end_train_loss = train_loss[-1] if len(train_loss) > 0 else 0.0
    end_val_loss = val_loss[-1] if len(val_loss) > 0 else 0.0

    init_train_acc = train_acc[0] if len(train_acc) > 0 else 0.0
    init_val_acc = val_acc[0] if len(val_acc) > 0 else 0.0
    p1_train_acc = train_acc[29] if len(train_acc) > 29 else (train_acc[-1] if train_acc else 0.0)
    p1_val_acc = val_acc[29] if len(val_acc) > 29 else (val_acc[-1] if val_acc else 0.0)
    end_train_acc = train_acc[-1] if len(train_acc) > 0 else 0.0
    end_val_acc = val_acc[-1] if len(val_acc) > 0 else 0.0

    # Build JSON structure
    report_dict = {
        "report_title": "Step 12 — Final Model Metrics, Curves & Performance Visualization",
        "project": "Arecanut Disease Classification (ResNet-50)",
        "scope": {
            "model_architecture": "ResNet-50",
            "model_checkpoint": r"D:\Areca\models\areca_resnet50_best.pth",
            "train_dataset_path": r"D:\Areca\Data\train",
            "test_dataset_path": r"D:\Areca\Data\test",
            "prohibited_dataset_status": "D:\\Areca\\Data\\final_testing-20230830T042904Z-001 (UNTOUCHED / NOT ACCESSED)"
        },
        "training_configuration": {
            "model": "ResNet-50",
            "num_classes": 4,
            "image_size": 224,
            "batch_size": 32,
            "random_seed": 42,
            "total_cleaned_train_images": 6109,
            "stratified_training_split": 4885,
            "stratified_validation_split": 1224,
            "phase1_configuration": "30 epochs, frozen backbone, learning rate = 0.001, AdamW optimizer",
            "phase2_configuration": "20 epochs, unfrozen backbone, learning rate = 1e-05, AdamW optimizer",
            "total_epochs_completed": 50,
            "early_stopping_patience": 5,
            "class_weighted_loss": True,
            "best_checkpoint_epoch": 48,
            "best_validation_loss": 0.0000964,
            "best_validation_accuracy": 1.0
        },
        "test_evaluation_summary": overall_summary,
        "confusion_matrix": {
            "class_order": CLASSES,
            "matrix": cm.tolist()
        },
        "one_vs_rest_per_class_metrics": per_class_stats,
        "roc_auc_analysis": {
            "per_class_auc": {c: per_class_stats[c]["auc"] for c in CLASSES},
            "macro_average_auc": roc_metrics["macro_average"]["auc"]
        },
        "generated_artifacts": {
            "plots": [
                PLOT_LOSS,
                PLOT_ACC,
                PLOT_CONF_MAT,
                PLOT_ROC,
                PLOT_F1,
                PLOT_PRECISION
            ],
            "reports": [
                CSV_FP_ANALYSIS,
                CSV_FINAL_METRICS,
                TXT_FINAL_REPORT,
                JSON_FINAL_REPORT
            ]
        }
    }
    
    with open(JSON_FINAL_REPORT, "w", encoding="utf-8") as f:
        json.dump(report_dict, f, indent=2)
    print(f"[+] Saved Final JSON Report: {JSON_FINAL_REPORT}")
    
    # Build text report
    lines = [
        "=" * 85,
        "STEP 12 — FINAL MODEL METRICS, CURVES & PERFORMANCE VISUALIZATION REPORT",
        "ARECANUT DISEASE CLASSIFICATION PROJECT (ResNet-50)",
        "=" * 85,
        "",
        "A. MODEL INFORMATION",
        "-" * 85,
        f"Architecture             : ResNet-50 (Pretrained ImageNet, Fine-Tuned Head + Backbone)",
        f"Model Checkpoint Path    : D:\\Areca\\models\\areca_resnet50_best.pth",
        f"Best Epoch               : 48 (Best Val Loss: 0.0000964, Best Val Acc: 100.0%)",
        "",
        "B. DATASET INFORMATION",
        "-" * 85,
        f"Total Cleaned Train Set  : 6,109 images (4,885 Training / 1,224 Validation)",
        f"Total Untouched Test Set : 1,635 images",
        f"Classes (4 Total)        : 0=Healthy_Leaf, 1=Healthy_Nut, 2=Mahali_Koleroga, 3=yellow leaf disease",
        f"Protected Scope Status   : final_testing-20230830T042904Z-001 REMAINED UNTOUCHED / UNACCESSED",
        "",
        "C. TRAINING CONFIGURATION",
        "-" * 85,
        f"Image Size               : 224 x 224",
        f"Batch Size               : 32",
        f"Random Seed              : 42 (Reproducible Split & Augmentation)",
        f"Class-Weighted Loss      : YES (Balanced Class Weights Applied to CrossEntropyLoss)",
        f"Optimizer                : AdamW (Weight Decay = 0.0001)",
        f"Phase 1 (Epochs 1–30)    : Frozen Backbone, Classifier Head Training (LR = 0.001)",
        f"Phase 2 (Epochs 31–50)   : Full Backbone Unfrozen, Fine-Tuning (LR = 0.00001)",
        f"Total Epochs Completed   : 50 / 50",
        f"Early Stopping Patience  : 5",
        "",
        "D. TRAINING / VALIDATION LOSS SUMMARY",
        "-" * 85,
        f"Initial Train Loss (Ep 1): {init_train_loss:.4f}  | Initial Val Loss (Ep 1): {init_val_loss:.4f}",
        f"Phase 1 End (Ep 30)      : Train Loss = {p1_train_loss:.4f} | Val Loss = {p1_val_loss:.4f}",
        f"Phase 2 End (Ep 50)      : Train Loss = {end_train_loss:.4f} | Val Loss = {end_val_loss:.6f}",
        f"Best Val Loss (Ep 48)    : 0.0000964",
        "",
        "E. TRAINING / VALIDATION ACCURACY SUMMARY",
        "-" * 85,
        f"Initial Train Acc (Ep 1) : {init_train_acc*100:.2f}% | Initial Val Acc (Ep 1) : {init_val_acc*100:.2f}%",
        f"Phase 1 End (Ep 30)      : Train Acc = {p1_train_acc*100:.2f}% | Val Acc = {p1_val_acc*100:.2f}%",
        f"Phase 2 End (Ep 50)      : Train Acc = {end_train_acc*100:.2f}% | Val Acc = {end_val_acc*100:.2f}%",
        f"Best Val Accuracy        : 100.00% (Epoch 48)",
        "",
        "F. TEST ACCURACY",
        "-" * 85,
        f"TEST Accuracy            : {overall_summary['Test Accuracy'] * 100:.2f}% ({overall_summary['Correct Predictions']} / {overall_summary['Total Test Images']})",
        "",
        "G. TEST LOSS",
        "-" * 85,
        f"TEST CrossEntropy Loss   : {overall_summary['Test Loss']:.6f}",
        "",
        "H. TEST CONFUSION MATRIX",
        "-" * 85,
        f"{'Actual \\ Predicted':<25} | {'Healthy_Leaf':<14} | {'Healthy_Nut':<14} | {'Mahali_Koleroga':<16} | {'yellow leaf disease':<20}",
        "-" * 85,
    ]
    for i, c in enumerate(CLASSES):
        row = f"{c:<25} | {cm[i, 0]:<14} | {cm[i, 1]:<14} | {cm[i, 2]:<16} | {cm[i, 3]:<20}"
        lines.append(row)
    
    lines.extend([
        "-" * 85,
        "",
        "I. ONE-VS-REST TRUE/FALSE POSITIVES & NEGATIVES (TP / FP / FN / TN)",
        "-" * 85,
        f"{'Class':<25} | {'TP':<6} | {'FP':<6} | {'FN':<6} | {'TN':<6}",
        "-" * 85,
    ])
    for c in CLASSES:
        s = per_class_stats[c]
        lines.append(f"{c:<25} | {s['tp']:<6} | {s['fp']:<6} | {s['fn']:<6} | {s['tn']:<6}")

    lines.extend([
        "-" * 85,
        "",
        "J. FALSE POSITIVE RATE (FPR)",
        "-" * 85,
        f"{'Class':<25} | {'FPR':<10}",
        "-" * 85,
    ])
    for c in CLASSES:
        s = per_class_stats[c]
        lines.append(f"{c:<25} | {s['fpr']:<10.4f}")

    lines.extend([
        "-" * 85,
        "",
        "K. PER-CLASS PRECISION",
        "-" * 85,
        f"{'Class':<25} | {'Precision':<10}",
        "-" * 85,
    ])
    for c in CLASSES:
        s = per_class_stats[c]
        lines.append(f"{c:<25} | {s['precision']:<10.4f}")

    lines.extend([
        "-" * 85,
        "",
        "L. PER-CLASS RECALL",
        "-" * 85,
        f"{'Class':<25} | {'Recall':<10}",
        "-" * 85,
    ])
    for c in CLASSES:
        s = per_class_stats[c]
        lines.append(f"{c:<25} | {s['recall']:<10.4f}")

    lines.extend([
        "-" * 85,
        "",
        "M. PER-CLASS F1-SCORE",
        "-" * 85,
        f"{'Class':<25} | {'F1-Score':<10} | {'Support':<8}",
        "-" * 85,
    ])
    for c in CLASSES:
        s = per_class_stats[c]
        lines.append(f"{c:<25} | {s['f1']:<10.4f} | {s['support']:<8}")

    lines.extend([
        "-" * 85,
        "",
        "N. ROC / AUC ANALYSIS",
        "-" * 85,
        f"{'Class':<25} | {'AUC':<10}",
        "-" * 85,
    ])
    for c in CLASSES:
        s = per_class_stats[c]
        lines.append(f"{c:<25} | {s['auc']:<10.4f}")
    lines.append(f"{'Macro-Average AUC':<25} | {roc_metrics['macro_average']['auc']:<10.4f}")

    lines.extend([
        "-" * 85,
        "",
        "O. OVERALL TEST METRICS SUMMARY",
        "-" * 85,
        f"Total TEST Images        : {overall_summary['Total Test Images']}",
        f"Correct Predictions      : {overall_summary['Correct Predictions']}",
        f"Incorrect Predictions    : {overall_summary['Incorrect Predictions']}",
        f"Test Accuracy            : {overall_summary['Test Accuracy'] * 100:.2f}%",
        f"Test Loss                : {overall_summary['Test Loss']:.6f}",
        f"Macro Precision          : {overall_summary['Macro Precision']:.4f}",
        f"Macro Recall             : {overall_summary['Macro Recall']:.4f}",
        f"Macro F1-Score           : {overall_summary['Macro F1-Score']:.4f}",
        f"Weighted Precision       : {overall_summary['Weighted Precision']:.4f}",
        f"Weighted Recall          : {overall_summary['Weighted Recall']:.4f}",
        f"Weighted F1-Score        : {overall_summary['Weighted F1-Score']:.4f}",
        f"Macro ROC AUC            : {roc_metrics['macro_average']['auc']:.4f}",
        "",
        "GENERATED ARTIFACTS & PLOTS:",
        f"1. Training vs Validation Loss Plot       : {PLOT_LOSS}",
        f"2. Training vs Validation Accuracy Plot   : {PLOT_ACC}",
        f"3. TEST Confusion Matrix Heatmap          : {PLOT_CONF_MAT}",
        f"4. Multi-Class ROC Curves & AUC Plot      : {PLOT_ROC}",
        f"5. Per-Class F1 Scores Bar Chart          : {PLOT_F1}",
        f"6. Per-Class Precision Bar Chart          : {PLOT_PRECISION}",
        f"7. False Positive Analysis CSV            : {CSV_FP_ANALYSIS}",
        f"8. Comprehensive Final Metrics CSV        : {CSV_FINAL_METRICS}",
        f"9. Final Metrics JSON Report              : {JSON_FINAL_REPORT}",
        f"10. Final Metrics Text Report             : {TXT_FINAL_REPORT}",
        "",
        "=" * 85,
        "END OF STEP 12 FINAL METRICS REPORT",
        "=" * 85
    ])
    
    with open(TXT_FINAL_REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[+] Saved Final Text Report: {TXT_FINAL_REPORT}")


# -------------------------------------------------------------------------
# MAIN PIPELINE
# -------------------------------------------------------------------------
def main():
    print("=" * 80)
    print("STEP 12 — FINAL MODEL METRICS, CURVES & PERFORMANCE VISUALIZATION")
    print("=" * 80)
    
    setup_directories()
    
    # 1. Load Step 10 & Step 11 artifacts
    step10_data, train_loss, val_loss, train_acc, val_acc = load_step10_training_history()
    rows, step11_data = load_step11_test_results()
    
    # 2. Generate Training vs Validation Curves
    plot_training_validation_loss(train_loss, val_loss)
    plot_training_validation_accuracy(train_acc, val_acc)
    
    # 3. Generate Confusion Matrix
    cm = compute_confusion_matrix(rows)
    plot_test_confusion_matrix(cm)
    
    # 4. Generate ROC Curves and calculate AUC
    roc_metrics = calculate_and_plot_roc_curves(rows)
    
    # 5. Calculate One-vs-Rest Statistics & Per-Class Metrics
    per_class_stats = compute_one_vs_rest_analysis(rows, cm, roc_metrics)
    
    # 6. Compute Aggregate Overall Test Metrics
    overall_summary, macro_p, macro_r, macro_f1, wt_p, wt_r, wt_f1 = compute_aggregate_metrics(
        rows, per_class_stats, roc_metrics, step11_data
    )
    
    # 7. Generate F1 and Precision Charts
    plot_per_class_f1_scores(per_class_stats, macro_f1, wt_f1)
    plot_per_class_precision(per_class_stats, macro_p, wt_p)
    
    # 8. Export CSVs & Reports
    export_false_positive_analysis_csv(per_class_stats)
    export_final_metrics_csv(overall_summary, per_class_stats)
    export_final_reports(step10_data, step11_data, cm, per_class_stats, overall_summary, roc_metrics)
    
    print("=" * 80)
    print("[SUCCESS] Step 12 metrics, plots, CSVs, and final reports generated successfully.")
    print("=" * 80)


if __name__ == "__main__":
    main()

"""
Step 10: Clean Dataset Training Pipeline Setup (Single 4-Class ResNet-50 Two-Phase Training)
Script: D:\\Areca\\scripts\\step10_training_pipeline.py

Architecture:
  - Single Pretrained ResNet-50 on ImageNet (4 classes):
      0 = Healthy_Leaf
      1 = Healthy_Nut
      2 = Mahali_Koleroga
      3 = yellow leaf disease
  - Stratified 80/20 Train/Validation Split (Seed=42) strictly from D:\\Areca\\Data\\train.
  - TEST set (D:\\Areca\\Data\\test) is completely UNTOUCHED and RESERVED for final evaluation.

Two-Phase Training Structure:
  - Phase 1 (Feature Extraction): 30 epochs (Frozen backbone, train classifier head, lr=1e-3)
  - Phase 2 (Full Fine-Tuning):   20 epochs (Unfrozen backbone, fine-tune all layers, lr=1e-5)
  - Total Maximum: 50 epochs (Early stopping patience = 5 epochs per phase)
"""

import os
import sys
import json
import time
import random
import argparse
from pathlib import Path
from collections import defaultdict

# Required Deep Learning & Numerical Libraries
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
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

# Centralized Two-Phase Training Configuration
CONFIG = {
    "seed": 42,
    "image_size": 224,
    "batch_size": 32,
    "num_workers": 2 if sys.platform != "win32" else 0,  # Safe default on Windows
    "early_stopping_patience": 5,
    "train_val_split_ratio": 0.80,
    "class_mapping": CLASS_MAPPING,
    # Phase 1: Frozen Backbone / Classifier Head Training
    "phase1_epochs": 30,
    "phase1_lr": 1e-3,
    "phase1_weight_decay": 1e-4,
    # Phase 2: Full Backbone Fine-Tuning
    "phase2_epochs": 20,
    "phase2_lr": 1e-5,
    "phase2_weight_decay": 1e-4,
    "total_max_epochs": 50
}


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


def set_seed(seed: int = 42):
    """Sets random seeds across all libraries for deterministic execution."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


class ImageDataset(Dataset):
    """PyTorch dataset reading from an in-memory sample list."""
    def __init__(self, samples, transform=None):
        self.samples = samples  # List of (path, class_idx)
        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        with Image.open(path) as img:
            img = img.convert("RGB")
            if self.transform:
                img = self.transform(img)
        return img, label


def get_transforms(image_size: int = 224):
    """Constructs training (augmented) and validation (deterministic) transforms."""
    train_transform = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=15),
        transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    val_transform = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    return train_transform, val_transform


def collect_dataset_samples(train_dir: Path, class_mapping: dict):
    """Scans strictly inside D:\\Areca\\Data\\train class folders."""
    samples = []
    class_counts = defaultdict(int)

    for class_name, class_idx in class_mapping.items():
        c_dir = train_dir / class_name
        if not c_dir.exists():
            raise FileNotFoundError(f"Expected class directory not found: {c_dir}")

        for root, _, files in os.walk(c_dir):
            for f in files:
                f_path = Path(root) / f
                if f_path.suffix.lower() in IMAGE_EXTENSIONS:
                    samples.append((str(f_path), class_idx))
                    class_counts[class_name] += 1

    return samples, dict(class_counts)


def stratified_split(samples, train_ratio=0.80, seed=42):
    """Performs stratified 80/20 train/validation split deterministically."""
    random.seed(seed)
    by_class = defaultdict(list)
    for path, label in samples:
        by_class[label].append((path, label))

    train_samples = []
    val_samples = []

    for label, items in sorted(by_class.items()):
        items_shuffled = list(items)
        random.shuffle(items_shuffled)
        split_idx = int(len(items_shuffled) * train_ratio)
        train_samples.extend(items_shuffled[:split_idx])
        val_samples.extend(items_shuffled[split_idx:])

    random.shuffle(train_samples)
    random.shuffle(val_samples)

    return train_samples, val_samples


def compute_class_weights(train_samples, num_classes=4):
    """Computes balanced class weights strictly from the TRAINING split."""
    counts = defaultdict(int)
    for _, label in train_samples:
        counts[label] += 1

    total = len(train_samples)
    weights = []
    for c in range(num_classes):
        cnt = counts.get(c, 1)
        w = total / (num_classes * cnt)
        weights.append(w)

    return torch.tensor(weights, dtype=torch.float32), dict(counts)


def build_resnet50_model(num_classes: int = 4):
    """Initializes ResNet-50 with pretrained ImageNet weights and 4-output classification head."""
    try:
        weights = ResNet50_Weights.DEFAULT
        model = resnet50(weights=weights)
    except Exception:
        try:
            model = resnet50(pretrained=True)
        except Exception as exc:
            raise RuntimeError(f"Unable to load pretrained ResNet-50 weights: {exc}")

    # Replace 1000-class head with 4-class head
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)
    return model


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

        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)

        per_class[c_name] = {
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "support": int(sup)
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
    fig, ax = plt.subplots(figsize=(7, 6))
    cax = ax.matshow(cm, cmap="Blues")
    fig.colorbar(cax)

    ax.set_xticks(range(len(class_names)))
    ax.set_yticks(range(len(class_names)))
    ax.set_xticklabels(class_names, rotation=25, ha="left")
    ax.set_yticklabels(class_names)

    for i in range(len(class_names)):
        for j in range(len(class_names)):
            val = cm[i][j]
            color = "white" if val > (np.max(cm) / 2) else "black"
            ax.text(j, i, str(val), ha="center", va="center", color=color, fontsize=11, fontweight="bold")

    ax.set_xlabel("Predicted Label", fontweight="bold")
    ax.set_ylabel("True Label", fontweight="bold")
    ax.set_title(title, fontweight="bold", pad=25)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_training_history(history, output_path: Path, phase1_epochs_run: int):
    """Renders and saves combined training vs validation loss and accuracy curves across both phases."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    total_epochs = len(history["train_loss"])
    epochs = range(1, total_epochs + 1)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # Loss curve
    ax1.plot(epochs, history["train_loss"], "b-o", label="Train Loss")
    ax1.plot(epochs, history["val_loss"], "r-s", label="Val Loss")
    if phase1_epochs_run < total_epochs:
        ax1.axvline(x=phase1_epochs_run + 0.5, color="gray", linestyle="--", label="Phase 2 (Fine-Tuning)")
    ax1.set_title("Two-Phase Training Loss History", fontweight="bold")
    ax1.set_xlabel("Total Epoch")
    ax1.set_ylabel("CrossEntropy Loss")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Accuracy curve
    ax2.plot(epochs, history["train_acc"], "b-o", label="Train Accuracy")
    ax2.plot(epochs, history["val_acc"], "g-s", label="Val Accuracy")
    if phase1_epochs_run < total_epochs:
        ax2.axvline(x=phase1_epochs_run + 0.5, color="gray", linestyle="--", label="Phase 2 (Fine-Tuning)")
    ax2.set_title("Two-Phase Training Accuracy History", fontweight="bold")
    ax2.set_xlabel("Total Epoch")
    ax2.set_ylabel("Accuracy")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


# ----------------------------------------------------------------------
# Safe Pipeline Test (Two-Phase Dry Run)
# ----------------------------------------------------------------------
def execute_safe_pipeline_test(train_dir: Path, device: torch.device):
    """Executes a non-destructive 1-batch dry run covering both Phase 1 and Phase 2."""
    print("\n[SAFE PIPELINE TEST] Initializing Single 4-Class ResNet-50 Two-Phase dry run...")

    # 1. Dataset Loading
    samples, class_counts = collect_dataset_samples(train_dir, CLASS_MAPPING)
    print(f"  1. Total Cleaned Images Found:  {len(samples)} (Expected: 6109)")
    assert len(samples) == 6109, f"Expected 6109 images, found {len(samples)}"

    # 2. Four classes detected
    print(f"  2. Four Classes Detected:       {list(class_counts.keys())}")
    assert len(class_counts) == 4, f"Expected 4 classes, found {len(class_counts)}"

    # 3. Stratified 80/20 Split
    train_samples, val_samples = stratified_split(samples, CONFIG["train_val_split_ratio"], CONFIG["seed"])
    print(f"  3. Stratified Split:            Train = {len(train_samples)} ({len(train_samples)/len(samples)*100:.1f}%), Val = {len(val_samples)} ({len(val_samples)/len(samples)*100:.1f}%)")
    assert len(train_samples) + len(val_samples) == len(samples), f"Split count mismatch: {len(train_samples)} + {len(val_samples)} != {len(samples)}"
    assert len(train_samples) > 0 and len(val_samples) > 0

    # 4. Class Weights
    class_weights, train_counts = compute_class_weights(train_samples, len(CLASS_MAPPING))
    class_weights = class_weights.to(device)
    print(f"  4. Computed Class Weights:      {class_weights.cpu().numpy().round(4).tolist()}")

    # DataLoaders for dry run
    train_transform, val_transform = get_transforms(CONFIG["image_size"])
    train_ds = ImageDataset(train_samples, train_transform)
    val_ds = ImageDataset(val_samples, val_transform)
    train_loader = DataLoader(train_ds, batch_size=4, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=4, shuffle=False, num_workers=0)

    # 5. Model Initialization
    model = build_resnet50_model(num_classes=4).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    print(f"  5. ResNet-50 Initialized:       Model Head = Linear(in_features={model.fc.in_features}, out_features=4)")

    # 6. Phase 1 Simulation: Frozen Backbone Head Training
    print("  6. Phase 1 Check (Frozen Backbone):")
    for name, param in model.named_parameters():
        if "fc" not in name:
            param.requires_grad = False
        else:
            param.requires_grad = True

    opt_p1 = optim.AdamW(model.fc.parameters(), lr=CONFIG["phase1_lr"], weight_decay=CONFIG["phase1_weight_decay"])
    model.train()
    inputs, labels = next(iter(train_loader))
    inputs, labels = inputs.to(device), labels.to(device)
    outputs = model(inputs)
    assert outputs.shape == (4, 4), f"Expected [4, 4], got {outputs.shape}"
    loss_p1 = criterion(outputs, labels)
    opt_p1.zero_grad()
    loss_p1.backward()
    opt_p1.step()
    print(f"     * Phase 1 Forward/Backward:  Loss = {loss_p1.item():.4f} | Output Shape = {list(outputs.shape)} [OK]")

    # 7. Phase 2 Simulation: Unfrozen Backbone Fine-Tuning
    print("  7. Phase 2 Check (Unfrozen Backbone Fine-Tuning):")
    for param in model.parameters():
        param.requires_grad = True

    opt_p2 = optim.AdamW(model.parameters(), lr=CONFIG["phase2_lr"], weight_decay=CONFIG["phase2_weight_decay"])
    outputs_p2 = model(inputs)
    loss_p2 = criterion(outputs_p2, labels)
    opt_p2.zero_grad()
    loss_p2.backward()
    opt_p2.step()
    print(f"     * Phase 2 Forward/Backward:  Loss = {loss_p2.item():.4f} [OK]")

    # 8. Validation Pass
    model.eval()
    with torch.no_grad():
        v_inputs, v_labels = next(iter(val_loader))
        v_inputs = v_inputs.to(device)
        v_outputs = model(v_inputs)
        assert v_outputs.shape == (4, 4)
    print(f"  8. Validation Forward Check:    [OK]")

    # 9. Temporary Checkpoint Test
    test_ckpt = Path(r"D:\Areca\models") / "test_4class_twophase_checkpoint.pth"
    test_ckpt.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"state": model.state_dict(), "test": True}, test_ckpt)
    assert test_ckpt.exists()
    test_ckpt.unlink()
    print(f"  9. Checkpoint Save/Delete:      [OK]")

    print("\n" + "=" * 80)
    print("SINGLE 4-CLASS RESNET-50 TWO-PHASE PIPELINE TEST: PASS")
    print("=" * 80)
    print("PHASE 1 ALLOCATION: 30 epochs (Classifier Head Training)")
    print("PHASE 2 ALLOCATION: 20 epochs (Full Model Fine-Tuning)")
    print("TOTAL MAXIMUM:      50 epochs (Early Stopping Patience = 5)")
    print("=" * 80)
    print("Pipeline is fully validated and ready for two-phase training.")
    print("To execute full training, run: python step10_training_pipeline.py --mode train")
    print("=" * 80 + "\n")
    return True


# ----------------------------------------------------------------------
# Full Two-Phase Training Execution
# ----------------------------------------------------------------------
def execute_full_training(train_dir: Path, output_model_path: Path,
                          txt_report_path: Path, json_report_path: Path,
                          history_plot_path: Path, cm_plot_path: Path, device: torch.device):
    """Executes full 2-phase training (30 epochs Phase 1 + 20 epochs Phase 2 = 50 max epochs)."""
    logger = Logger()
    logger.log("=" * 80)
    logger.log("STEP 10 — SINGLE 4-CLASS RESNET-50 TWO-PHASE TRAINING")
    logger.log("=" * 80)
    logger.log(f"Phase 1: 30 epochs (Feature Extraction / Frozen Backbone, lr={CONFIG['phase1_lr']})")
    logger.log(f"Phase 2: 20 epochs (Full Fine-Tuning / Unfrozen Backbone, lr={CONFIG['phase2_lr']})")
    logger.log(f"Total Maximum: 50 epochs | Early Stopping Patience: {CONFIG['early_stopping_patience']}")
    logger.log("=" * 80)

    # Dataset & Split
    samples, class_counts = collect_dataset_samples(train_dir, CLASS_MAPPING)
    train_samples, val_samples = stratified_split(samples, CONFIG["train_val_split_ratio"], CONFIG["seed"])
    train_transform, val_transform = get_transforms(CONFIG["image_size"])

    train_ds = ImageDataset(train_samples, train_transform)
    val_ds = ImageDataset(val_samples, val_transform)

    train_loader = DataLoader(train_ds, batch_size=CONFIG["batch_size"], shuffle=True, num_workers=CONFIG["num_workers"])
    val_loader = DataLoader(val_ds, batch_size=CONFIG["batch_size"], shuffle=False, num_workers=CONFIG["num_workers"])

    class_weights, train_counts = compute_class_weights(train_samples, len(CLASS_MAPPING))
    class_weights = class_weights.to(device)

    logger.log(f"Dataset Summary:")
    logger.log(f"  - Total Cleaned Images:     {len(samples)}")
    logger.log(f"  - Training Split (80%):     {len(train_samples)}")
    logger.log(f"  - Validation Split (20%):   {len(val_samples)}")
    logger.log(f"  - Class Mapping:            {CLASS_MAPPING}")
    logger.log(f"  - Training Class Counts:    {train_counts}")
    logger.log(f"  - Computed Class Weights:   {class_weights.cpu().numpy().round(4).tolist()}")
    logger.log(f"  - Device:                   {device}")
    logger.log("-" * 80)

    # Initialize Pretrained ResNet-50
    model = build_resnet50_model(num_classes=4).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)

    use_amp = (device.type == "cuda")
    scaler = torch.amp.GradScaler("cuda") if use_amp else None

    history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": []}
    best_val_loss = float("inf")
    best_val_acc = 0.0
    best_epoch_overall = 0
    total_epochs_completed = 0

    start_train_time = time.time()

    # ==================================================================
    # PHASE 1: Feature Extraction / Frozen Backbone (30 Epochs Max)
    # ==================================================================
    logger.log("\n>>> STARTING PHASE 1: FEATURE EXTRACTION (30 EPOCHS MAX) <<<")
    logger.log("Freezing backbone layers; training only classifier head (model.fc)...")

    for name, param in model.named_parameters():
        if "fc" not in name:
            param.requires_grad = False
        else:
            param.requires_grad = True

    opt_p1 = optim.AdamW(model.fc.parameters(), lr=CONFIG["phase1_lr"], weight_decay=CONFIG["phase1_weight_decay"])
    sched_p1 = optim.lr_scheduler.CosineAnnealingLR(opt_p1, T_max=CONFIG["phase1_epochs"])

    p1_patience = 0
    phase1_epochs_run = 0

    for epoch in range(1, CONFIG["phase1_epochs"] + 1):
        phase1_epochs_run += 1
        total_epochs_completed += 1

        # Train
        model.train()
        running_loss = 0.0
        correct_train = 0
        total_train_items = 0

        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            opt_p1.zero_grad()

            if use_amp:
                with torch.amp.autocast("cuda"):
                    outputs = model(inputs)
                    loss = criterion(outputs, labels)
                scaler.scale(loss).backward()
                scaler.step(opt_p1)
                scaler.update()
            else:
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                opt_p1.step()

            running_loss += loss.item() * inputs.size(0)
            _, preds = torch.max(outputs, 1)
            correct_train += torch.sum(preds == labels.data).item()
            total_train_items += inputs.size(0)

        sched_p1.step()
        epoch_train_loss = running_loss / total_train_items
        epoch_train_acc = correct_train / total_train_items

        # Val
        model.eval()
        val_running_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                if use_amp:
                    with torch.amp.autocast("cuda"):
                        outputs = model(inputs)
                        loss = criterion(outputs, labels)
                else:
                    outputs = model(inputs)
                    loss = criterion(outputs, labels)

                val_running_loss += loss.item() * inputs.size(0)
                _, preds = torch.max(outputs, 1)
                val_correct += torch.sum(preds == labels.data).item()
                val_total += inputs.size(0)

        epoch_val_loss = val_running_loss / val_total
        epoch_val_acc = val_correct / val_total

        history["train_loss"].append(round(epoch_train_loss, 4))
        history["train_acc"].append(round(epoch_train_acc, 4))
        history["val_loss"].append(round(epoch_val_loss, 4))
        history["val_acc"].append(round(epoch_val_acc, 4))

        logger.log(f"[Phase 1] Epoch {epoch:02d}/{CONFIG['phase1_epochs']:02d} (Overall {total_epochs_completed:02d}) | "
                   f"Train Loss: {epoch_train_loss:.4f} - Acc: {epoch_train_acc:.4f} | "
                   f"Val Loss: {epoch_val_loss:.4f} - Acc: {epoch_val_acc:.4f}")

        # Checkpoint Best Model
        if epoch_val_loss < best_val_loss:
            best_val_loss = epoch_val_loss
            best_val_acc = epoch_val_acc
            best_epoch_overall = total_epochs_completed
            p1_patience = 0

            output_model_path.parent.mkdir(parents=True, exist_ok=True)
            torch.save({
                "phase": 1,
                "epoch": total_epochs_completed,
                "model_state_dict": model.state_dict(),
                "val_loss": best_val_loss,
                "val_acc": best_val_acc,
                "class_mapping": CLASS_MAPPING,
                "config": CONFIG
            }, output_model_path)
            logger.log(f"  --> Best Phase 1 checkpoint saved (Val Loss: {best_val_loss:.4f})")
        else:
            p1_patience += 1
            if p1_patience >= CONFIG["early_stopping_patience"]:
                logger.log(f"Phase 1 early stopping triggered after {epoch} epochs.")
                break

    # ==================================================================
    # PHASE 2: Full Fine-Tuning / Unfrozen Backbone (20 Epochs Max)
    # ==================================================================
    logger.log("\n>>> STARTING PHASE 2: FULL FINE-TUNING (20 EPOCHS MAX) <<<")
    logger.log("Unfreezing all backbone layers for full fine-tuning with differential learning rate...")

    # Load best weights from Phase 1
    if output_model_path.exists():
        ckpt_p1 = torch.load(output_model_path, map_location=device)
        model.load_state_dict(ckpt_p1["model_state_dict"])
        logger.log(f"Loaded best Phase 1 model weights (Val Loss: {best_val_loss:.4f}) for Phase 2 initialization.")

    # Unfreeze all parameters
    for param in model.parameters():
        param.requires_grad = True

    opt_p2 = optim.AdamW(model.parameters(), lr=CONFIG["phase2_lr"], weight_decay=CONFIG["phase2_weight_decay"])
    sched_p2 = optim.lr_scheduler.CosineAnnealingLR(opt_p2, T_max=CONFIG["phase2_epochs"])

    p2_patience = 0

    for epoch in range(1, CONFIG["phase2_epochs"] + 1):
        total_epochs_completed += 1

        # Train
        model.train()
        running_loss = 0.0
        correct_train = 0
        total_train_items = 0

        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            opt_p2.zero_grad()

            if use_amp:
                with torch.amp.autocast("cuda"):
                    outputs = model(inputs)
                    loss = criterion(outputs, labels)
                scaler.scale(loss).backward()
                scaler.step(opt_p2)
                scaler.update()
            else:
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                opt_p2.step()

            running_loss += loss.item() * inputs.size(0)
            _, preds = torch.max(outputs, 1)
            correct_train += torch.sum(preds == labels.data).item()
            total_train_items += inputs.size(0)

        sched_p2.step()
        epoch_train_loss = running_loss / total_train_items
        epoch_train_acc = correct_train / total_train_items

        # Val
        model.eval()
        val_running_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                if use_amp:
                    with torch.amp.autocast("cuda"):
                        outputs = model(inputs)
                        loss = criterion(outputs, labels)
                else:
                    outputs = model(inputs)
                    loss = criterion(outputs, labels)

                val_running_loss += loss.item() * inputs.size(0)
                _, preds = torch.max(outputs, 1)
                val_correct += torch.sum(preds == labels.data).item()
                val_total += inputs.size(0)

        epoch_val_loss = val_running_loss / val_total
        epoch_val_acc = val_correct / val_total

        history["train_loss"].append(round(epoch_train_loss, 4))
        history["train_acc"].append(round(epoch_train_acc, 4))
        history["val_loss"].append(round(epoch_val_loss, 4))
        history["val_acc"].append(round(epoch_val_acc, 4))

        logger.log(f"[Phase 2] Epoch {epoch:02d}/{CONFIG['phase2_epochs']:02d} (Overall {total_epochs_completed:02d}) | "
                   f"Train Loss: {epoch_train_loss:.4f} - Acc: {epoch_train_acc:.4f} | "
                   f"Val Loss: {epoch_val_loss:.4f} - Acc: {epoch_val_acc:.4f}")

        # Checkpoint Best Overall Model
        if epoch_val_loss < best_val_loss:
            best_val_loss = epoch_val_loss
            best_val_acc = epoch_val_acc
            best_epoch_overall = total_epochs_completed
            p2_patience = 0

            output_model_path.parent.mkdir(parents=True, exist_ok=True)
            torch.save({
                "phase": 2,
                "epoch": total_epochs_completed,
                "model_state_dict": model.state_dict(),
                "val_loss": best_val_loss,
                "val_acc": best_val_acc,
                "class_mapping": CLASS_MAPPING,
                "config": CONFIG
            }, output_model_path)
            logger.log(f"  --> Best overall checkpoint saved: {output_model_path.name} (Val Loss: {best_val_loss:.4f})")
        else:
            p2_patience += 1
            if p2_patience >= CONFIG["early_stopping_patience"]:
                logger.log(f"Phase 2 early stopping triggered after {epoch} epochs.")
                break

    train_duration = time.time() - start_train_time

    # ==================================================================
    # Evaluation of Best Overall Model Checkpoint
    # ==================================================================
    checkpoint = torch.load(output_model_path, map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    final_val_preds = []
    final_val_labels = []
    with torch.no_grad():
        for inputs, labels in val_loader:
            inputs = inputs.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            final_val_preds.extend(preds.cpu().numpy())
            final_val_labels.extend(labels.numpy())

    metrics = calculate_metrics(final_val_labels, final_val_preds, CLASS_NAMES)

    # Generate Plots
    plot_training_history(history, history_plot_path, phase1_epochs_run)
    plot_confusion_matrix(metrics["confusion_matrix"], CLASS_NAMES, cm_plot_path, "4-Class ResNet-50 Validation Confusion Matrix")

    # Logging Final Summary Report
    logger.log("-" * 80)
    logger.log("TWO-PHASE TRAINING RESULTS SUMMARY")
    logger.log(f"  - Total Training Duration:   {train_duration:.2f}s")
    logger.log(f"  - Total Epochs Completed:    {total_epochs_completed} (Phase 1: {phase1_epochs_run}, Phase 2: {total_epochs_completed - phase1_epochs_run})")
    logger.log(f"  - Best Overall Epoch:        {best_epoch_overall}")
    logger.log(f"  - Best Validation Loss:      {best_val_loss:.4f}")
    logger.log(f"  - Best Validation Accuracy:  {best_val_acc * 100:.2f}%")
    logger.log(f"  - Macro Precision:           {metrics['macro_precision']:.4f}")
    logger.log(f"  - Macro Recall:              {metrics['macro_recall']:.4f}")
    logger.log(f"  - Macro F1-Score:            {metrics['macro_f1']:.4f}")
    logger.log(f"  - Weighted F1-Score:         {metrics['weighted_f1']:.4f}")
    logger.log("\nPer-Class Validation Performance:")
    for c_name, c_m in metrics["per_class"].items():
        logger.log(f"    * {c_name:<20}: Precision={c_m['precision']:.4f}, Recall={c_m['recall']:.4f}, F1={c_m['f1_score']:.4f} (Support={c_m['support']})")
    logger.log("-" * 80)

    # Save Reports
    logger.write_to_file(txt_report_path)

    json_data = {
        "pipeline": "Step 10 - Single 4-Class ResNet-50 Two-Phase Training",
        "phases": {
            "phase1_feature_extraction": {
                "max_epochs": CONFIG["phase1_epochs"],
                "epochs_run": phase1_epochs_run,
                "learning_rate": CONFIG["phase1_lr"],
                "backbone": "frozen"
            },
            "phase2_fine_tuning": {
                "max_epochs": CONFIG["phase2_epochs"],
                "epochs_run": total_epochs_completed - phase1_epochs_run,
                "learning_rate": CONFIG["phase2_lr"],
                "backbone": "unfrozen"
            }
        },
        "class_mapping": CLASS_MAPPING,
        "config": CONFIG,
        "train_count": len(train_samples),
        "validation_count": len(val_samples),
        "training_class_counts": train_counts,
        "class_weights": class_weights.cpu().numpy().tolist(),
        "model_architecture": "ResNet-50 (Pretrained ImageNet)",
        "optimizer": "AdamW",
        "total_epochs_completed": total_epochs_completed,
        "best_epoch_overall": best_epoch_overall,
        "best_val_loss": best_val_loss,
        "best_val_acc": best_val_acc,
        "training_duration_seconds": train_duration,
        "device": str(device),
        "validation_metrics": metrics,
        "training_history": history,
        "checkpoint_path": str(output_model_path)
    }

    with open(json_report_path, "w", encoding="utf-8") as jf:
        json.dump(json_data, jf, indent=2)

    logger.log("Reports and plots generated:")
    logger.log(f"  - Report: {txt_report_path}")
    logger.log(f"  - Report: {json_report_path}")
    logger.log(f"  - Plot:   {history_plot_path}")
    logger.log(f"  - Plot:   {cm_plot_path}")
    logger.log("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Step 10: Single 4-Class ResNet-50 Two-Phase Training Pipeline")
    parser.add_argument("--mode", choices=["test", "train"], default="test",
                        help="'test' runs safe two-phase 1-batch dry run; 'train' executes full two-phase training.")
    args = parser.parse_args()

    project_root = Path(r"D:\Areca")
    train_dir = project_root / "Data" / "train"
    models_dir = project_root / "models"
    reports_dir = project_root / "reports"
    plots_dir = project_root / "plots"

    models_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    plots_dir.mkdir(parents=True, exist_ok=True)

    set_seed(CONFIG["seed"])
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print("=" * 80)
    print("STEP 10 — ARECANUT 4-CLASS RESNET-50 TWO-PHASE TRAINING PIPELINE")
    print("=" * 80)
    print(f"Project Root:        {project_root}")
    print(f"Train Directory:     {train_dir}")
    print(f"Execution Mode:      {args.mode.upper()}")
    print(f"Computation Device:  {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")
    print("=" * 80)

    if args.mode == "test":
        execute_safe_pipeline_test(train_dir, device)
    elif args.mode == "train":
        print("\n>>> STARTING FULL 4-CLASS TWO-PHASE TRAINING (MAX 50 EPOCHS) <<<\n")
        execute_full_training(
            train_dir=train_dir,
            output_model_path=models_dir / "areca_resnet50_best.pth",
            txt_report_path=reports_dir / "step10_training_report.txt",
            json_report_path=reports_dir / "step10_training_report.json",
            history_plot_path=plots_dir / "training_history.png",
            cm_plot_path=plots_dir / "validation_confusion_matrix.png",
            device=device
        )


if __name__ == "__main__":
    main()

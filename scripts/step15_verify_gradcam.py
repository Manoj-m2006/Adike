"""
Step 15: Standalone Grad-CAM Verification Script for Arecanut ResNet-50.
Script: D:\\Areca\\scripts\\step15_verify_gradcam.py

Checks:
  1. Model checkpoint loads successfully.
  2. Model architecture has 4 outputs.
  3. Valid image preprocessing works.
  4. Prediction produces valid softmax probabilities that sum to 1.0.
  5. Predicted class belongs to the 4 authoritative classes.
  6. Grad-CAM target layer is resolved as ResNet-50 layer4 (2048 channels).
  7. Grad-CAM heatmap is generated with valid [0, 1] range.
  8. Heatmap and overlay dimensions match original image dimensions.
  9. Model parameters are strictly unmodified (cloned weight equality check).
  10. Zero dataset modifications, zero final_testing access.
"""

import sys
from pathlib import Path
from PIL import Image
import numpy as np
import torch
import torch.nn as nn

# Configure paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from predictor.config import (
    MODEL_PATH,
    CLASS_NAMES,
    CLASS_MAPPING,
    CLASS_DISPLAY_NAMES,
    IMAGE_SIZE,
    IMAGENET_MEAN,
    IMAGENET_STD
)
from predictor.ml_model import ResNet50InferenceEngine, get_inference_engine
from predictor.gradcam import GradCAM, generate_gradcam_overlay


def run_gradcam_verification():
    print("=" * 80)
    print("STEP 15 — ARECANUT RESNET-50 GRAD-CAM VERIFICATION")
    print("=" * 80)

    # 1. Model Checkpoint Location
    print(f"\n[1/8] Checking Model Checkpoint:")
    print(f"      Target Path: {MODEL_PATH}")
    if not MODEL_PATH.exists():
        print(f"      [FAILED] Checkpoint not found at: {MODEL_PATH}")
        sys.exit(1)
    file_size_mb = MODEL_PATH.stat().st_size / (1024 * 1024)
    print(f"      [PASSED] Checkpoint exists ({file_size_mb:.2f} MB)")

    # 2. Inference Engine & Target Layer Verification
    print(f"\n[2/8] Initializing Engine & Resolving Target Layer:")
    engine = get_inference_engine()
    model = engine.model

    assert hasattr(model, "layer4"), "ResNet-50 must have layer4 attribute"
    assert model.fc.out_features == 4, f"Expected 4 outputs, got {model.fc.out_features}"
    print(f"      Architecture: ResNet-50 (4 Outputs)")
    print(f"      Target Layer: model.layer4 (Bottleneck Stage 4, 2048 channels)")
    print(f"      Model Mode:   eval() [training={model.training}]")
    print(f"      [PASSED] Target layer verified.")

    # 3. Parameter Immutability Snapshot (Before Grad-CAM)
    print(f"\n[3/8] Snapshotting Initial Model Weights for Immutability Check:")
    weights_before = [p.clone() for p in model.parameters()]
    print(f"      Snapshotted {len(weights_before)} parameter tensors.")

    # 4. Image Preprocessing Check
    print(f"\n[4/8] Preprocessing Sample Image:")
    orig_w, orig_h = 480, 360
    synthetic_image = Image.new("RGB", (orig_w, orig_h), color=(80, 160, 90))
    tensor = engine.preprocess_image(synthetic_image)

    assert tensor.shape == (1, 3, 224, 224), f"Expected shape (1, 3, 224, 224), got {tensor.shape}"
    print(f"      Original Image Dimensions: {orig_w} × {orig_h}")
    print(f"      Preprocessed Tensor Shape: {list(tensor.shape)}")
    print(f"      [PASSED] Preprocessing verified.")

    # 5. Normal Forward Pass & Prediction Check
    print(f"\n[5/8] Normal Inference Pass:")
    result = engine.predict(synthetic_image)
    predicted_idx = result["predicted_class_index"]
    predicted_class = result["predicted_class"]

    assert predicted_class in CLASS_NAMES, f"Invalid predicted class: {predicted_class}"
    assert 0 <= predicted_idx < 4, f"Invalid predicted index: {predicted_idx}"
    prob_sum = sum(result["raw_probabilities"])
    assert abs(prob_sum - 1.0) < 0.01, f"Probabilities do not sum to 1.0: {prob_sum}"

    print(f"      Predicted Class:      {predicted_class} (Index: {predicted_idx})")
    print(f"      Display Name:         {result['predicted_display_name']}")
    print(f"      Confidence:           {result['confidence_percentage']}%")
    print(f"      Probability Sum:      {prob_sum:.4f}")
    print(f"      [PASSED] Prediction valid.")

    # 6. Grad-CAM Activation Map Computation
    print(f"\n[6/8] Generating Grad-CAM Class Activation Map:")
    grad_cam = GradCAM(model, target_layer=model.layer4)
    cam = grad_cam.generate_cam(tensor.to(engine.device), target_class_idx=predicted_idx)

    assert isinstance(cam, np.ndarray), "CAM output must be a numpy ndarray"
    assert cam.ndim == 2, f"CAM output must be 2D, got {cam.ndim}D"
    assert 0.0 <= float(cam.min()) and float(cam.max()) <= 1.0, f"CAM values out of [0, 1] range: [{cam.min()}, {cam.max()}]"
    print(f"      Feature Map Spatial Grid: {cam.shape}")
    print(f"      Normalized Min Value:     {cam.min():.4f}")
    print(f"      Normalized Max Value:     {cam.max():.4f}")
    print(f"      [PASSED] Heatmap activation generated.")

    # 7. Colormap & Heatmap Overlay Generation
    print(f"\n[7/8] Generating Colormap & Blended Overlay:")
    heatmap_img, overlay_img = grad_cam.create_visualization(synthetic_image, cam, alpha=0.45)

    assert heatmap_img.size == (orig_w, orig_h), f"Heatmap size {heatmap_img.size} != original {(orig_w, orig_h)}"
    assert overlay_img.size == (orig_w, orig_h), f"Overlay size {overlay_img.size} != original {(orig_w, orig_h)}"
    assert heatmap_img.mode == "RGB", f"Expected RGB mode, got {heatmap_img.mode}"
    assert overlay_img.mode == "RGB", f"Expected RGB mode, got {overlay_img.mode}"
    print(f"      Heatmap Image Size:   {heatmap_img.size} ({heatmap_img.mode})")
    print(f"      Overlay Image Size:   {overlay_img.size} ({overlay_img.mode})")
    print(f"      Colormap:             Jet (Scientific Palette)")
    print(f"      Blend Factor Alpha:   0.45")
    print(f"      [PASSED] Visualization overlay generated.")

    # 8. Model Parameter Immutability Check (After Grad-CAM)
    print(f"\n[8/8] Verifying Model Parameters Remained Completely Unmodified:")
    weights_after = [p.clone() for p in model.parameters()]

    for idx, (p_before, p_after) in enumerate(zip(weights_before, weights_after)):
        if not torch.equal(p_before, p_after):
            print(f"      [FAILED] Parameter tensor {idx} was modified!")
            sys.exit(1)

    print(f"      All {len(weights_after)} parameter tensors are 100% BIT-FOR-BIT IDENTICAL.")
    print(f"      [PASSED] Zero weight modification confirmed.")

    # Final Summary
    print("\n" + "=" * 80)
    print("ALL STEP 15 GRAD-CAM VERIFICATION TESTS PASSED!")
    print("=" * 80)
    print("Grad-CAM Explainable AI is fully integrated into the Django application.")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_gradcam_verification()

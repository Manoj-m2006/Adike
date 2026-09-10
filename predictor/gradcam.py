"""
Grad-CAM (Gradient-weighted Class Activation Mapping) for ResNet-50.
Produces visual explanations for decisions made by the 4-class Arecanut Disease Model.
Strictly explanation-only: zero parameter modification, zero optimizer updates.
"""

import io
import base64
from typing import Tuple, Optional, Union, BinaryIO
from pathlib import Path

import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.cm as cm

import torch
import torch.nn as nn
import torch.nn.functional as F


class GradCAM:
    """
    Computes Gradient-weighted Class Activation Maps for a PyTorch convolutional network.
    Target layer for ResNet-50: `model.layer4` (the final 2048-channel residual bottleneck block).
    """

    def __init__(self, model: nn.Module, target_layer: Optional[nn.Module] = None):
        self.model = model
        self.target_layer = target_layer if target_layer is not None else getattr(model, "layer4", None)
        if self.target_layer is None:
            raise ValueError("Target layer for Grad-CAM could not be resolved from model architecture.")

        self.activations = None
        self.gradients = None
        self.hook_handles = []

    def _save_activations(self, module, input, output):
        self.activations = output.detach()

    def _save_gradients(self, module, grad_input, grad_output):
        # In PyTorch full backward hooks, grad_output[0] contains the gradient w.r.t layer output
        self.gradients = grad_output[0].detach()

    def _register_hooks(self):
        self._remove_hooks()
        h_fwd = self.target_layer.register_forward_hook(self._save_activations)
        h_bwd = self.target_layer.register_full_backward_hook(self._save_gradients)
        self.hook_handles = [h_fwd, h_bwd]

    def _remove_hooks(self):
        for h in self.hook_handles:
            try:
                h.remove()
            except Exception:
                pass
        self.hook_handles = []

    def generate_cam(self, input_tensor: torch.Tensor, target_class_idx: Optional[int] = None) -> np.ndarray:
        """
        Executes a targeted forward-backward pass to extract the 2D Grad-CAM activation map.
        Returns a normalized 2D numpy array [0.0, 1.0].
        """
        self._register_hooks()
        self.model.zero_grad()

        # Requires gradients ONLY during this localized backward pass
        with torch.enable_grad():
            tensor = input_tensor.clone()
            tensor.requires_grad = True

            logits = self.model(tensor)

            if target_class_idx is None:
                target_class_idx = int(torch.argmax(logits, dim=1).item())

            score = logits[0, target_class_idx]
            score.backward(retain_graph=False)

        # Retrieve hooked feature maps and gradients
        activations = self.activations  # Shape: (1, C, H, W) e.g. (1, 2048, 7, 7)
        gradients = self.gradients      # Shape: (1, C, H, W) e.g. (1, 2048, 7, 7)

        self._remove_hooks()
        self.model.zero_grad()

        if activations is None or gradients is None:
            raise RuntimeError("Failed to capture activations or gradients during Grad-CAM execution.")

        # 1. Global Average Pooling over spatial dimensions (H, W) -> Channel weights alpha_k
        weights = torch.mean(gradients, dim=(2, 3), keepdim=True)  # Shape: (1, C, 1, 1)

        # 2. Weighted linear combination of forward activation maps
        cam = torch.sum(weights * activations, dim=1, keepdim=True)  # Shape: (1, 1, H, W)

        # 3. Apply ReLU to isolate features positively correlated with the target class
        cam = F.relu(cam)

        # 4. Squeeze to 2D numpy array
        cam_np = cam.squeeze().cpu().numpy()

        # 5. Min-Max Normalization to range [0, 1]
        cam_min, cam_max = cam_np.min(), cam_np.max()
        if cam_max > cam_min:
            cam_norm = (cam_np - cam_min) / (cam_max - cam_min + 1e-8)
        else:
            cam_norm = np.zeros_like(cam_np)

        return cam_norm

    def create_visualization(
        self,
        original_pil_image: Image.Image,
        cam_map: np.ndarray,
        alpha: float = 0.45,
        colormap_name: str = "jet"
    ) -> Tuple[Image.Image, Image.Image]:
        """
        Resizes heatmap to original image dimensions and creates:
        1. Colored Heatmap Image
        2. Blended Heatmap Overlay on original image
        """
        orig_w, orig_h = original_pil_image.size
        orig_rgb = original_pil_image.convert("RGB")

        # Resize CAM heatmap to exact dimensions of original image via bicubic interpolation
        cam_uint8 = np.uint8(255 * cam_map)
        cam_pil = Image.fromarray(cam_uint8).resize((orig_w, orig_h), Image.Resampling.BICUBIC)
        cam_resized = np.array(cam_pil, dtype=np.float32) / 255.0

        # Apply standard scientific colormap (Jet)
        cmap = matplotlib.colormaps[colormap_name] if hasattr(matplotlib, "colormaps") else cm.get_cmap(colormap_name)
        heatmap_rgba = cmap(cam_resized)  # Shape: (H, W, 4) in [0.0, 1.0]
        heatmap_rgb = heatmap_rgba[:, :, :3]  # Shape: (H, W, 3)

        heatmap_image = Image.fromarray(np.uint8(heatmap_rgb * 255))

        # Overlay computation: alpha * heatmap + (1 - alpha) * original_image
        orig_np = np.array(orig_rgb, dtype=np.float32) / 255.0
        overlay_np = (alpha * heatmap_rgb) + ((1.0 - alpha) * orig_np)
        overlay_np = np.clip(overlay_np, 0.0, 1.0)

        overlay_image = Image.fromarray(np.uint8(overlay_np * 255))

        return heatmap_image, overlay_image


def generate_gradcam_overlay(
    model: nn.Module,
    input_tensor: torch.Tensor,
    original_pil_image: Image.Image,
    target_class_idx: Optional[int] = None,
    alpha: float = 0.45
) -> Tuple[str, str, np.ndarray]:
    """
    Convenience function that generates Grad-CAM and returns base64 data URIs
    for both the overlay and the raw heatmap.
    """
    grad_cam = GradCAM(model)
    cam_map = grad_cam.generate_cam(input_tensor, target_class_idx=target_class_idx)
    heatmap_img, overlay_img = grad_cam.create_visualization(original_pil_image, cam_map, alpha=alpha)

    # Encode overlay image to base64 Data URI
    overlay_buf = io.BytesIO()
    overlay_img.save(overlay_buf, format="PNG")
    overlay_b64 = base64.b64encode(overlay_buf.getvalue()).decode("utf-8")
    overlay_data_uri = f"data:image/png;base64,{overlay_b64}"

    # Encode standalone heatmap image to base64 Data URI
    heatmap_buf = io.BytesIO()
    heatmap_img.save(heatmap_buf, format="PNG")
    heatmap_b64 = base64.b64encode(heatmap_buf.getvalue()).decode("utf-8")
    heatmap_data_uri = f"data:image/png;base64,{heatmap_b64}"

    return overlay_data_uri, heatmap_data_uri, cam_map

"""
PyTorch Inference Engine for Arecanut Disease Detection.
Uses Pretrained ResNet-50 (4 Classes) trained in Step 10 and benchmarked in Step 11.
Strictly Inference-Only: Zero backpropagation, model.eval(), torch.no_grad().
"""

import time
import threading
from pathlib import Path
from typing import Dict, Any, Union, BinaryIO

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from torchvision.models import resnet50, ResNet50_Weights
from PIL import Image

from predictor.config import (
    MODEL_PATH,
    CLASS_NAMES,
    CLASS_DISPLAY_NAMES,
    CLASS_INFO,
    IMAGE_SIZE,
    IMAGENET_MEAN,
    IMAGENET_STD,
)


class ResNet50InferenceEngine:
    """
    Thread-safe Singleton inference wrapper for the 4-class Arecanut ResNet-50 model.
    Loads checkpoint into memory once and performs fast, deterministic forward passes.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ResNet50InferenceEngine, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_path: Union[str, Path] = MODEL_PATH):
        if getattr(self, "_initialized", False):
            return

        with self._lock:
            if getattr(self, "_initialized", False):
                return

            self.model_path = Path(model_path)
            self.cuda_available = torch.cuda.is_available()
            self.device = torch.device("cuda" if self.cuda_available else "cpu")
            self.device_name = torch.cuda.get_device_name(0) if self.cuda_available else "CPU"

            # 1. Exact Preprocessing Pipeline (Step 10/11)
            self.transform = transforms.Compose([
                transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
                transforms.ToTensor(),
                transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
            ])

            # 2. Build ResNet-50 Architecture (4 Outputs)
            self.model = self._build_architecture()

            # 3. Load Checkpoint
            self.checkpoint_metadata = self._load_checkpoint()

            # 4. Strict Evaluation Mode
            self.model.to(self.device)
            self.model.eval()

            # Ensure all parameters have requires_grad=False
            for param in self.model.parameters():
                param.requires_grad = False

            self._initialized = True

    def _build_architecture(self) -> nn.Module:
        """Constructs ResNet-50 with 4-output linear classifier."""
        try:
            # Initialize architecture without downloading weights if checkpoint supplies all parameters
            model = resnet50(weights=None)
        except Exception:
            try:
                model = resnet50(pretrained=False)
            except Exception as exc:
                raise RuntimeError(f"Failed to initialize base ResNet-50 model: {exc}")

        # Replace 1000-class head with authoritative 4-class classification head
        in_features = model.fc.in_features
        model.fc = nn.Linear(in_features, len(CLASS_NAMES))
        return model

    def _load_checkpoint(self) -> Dict[str, Any]:
        """Loads trained weights from the saved checkpoint dictionary."""
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model checkpoint not found at: {self.model_path}. "
                "Ensure areca_resnet50_best.pth exists in the models directory."
            )

        checkpoint = torch.load(self.model_path, map_location=self.device)

        if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
            state_dict = checkpoint["model_state_dict"]
            metadata = {
                "epoch": checkpoint.get("epoch", "N/A"),
                "val_loss": checkpoint.get("val_loss", "N/A"),
                "val_acc": checkpoint.get("val_acc", "N/A"),
                "phase": checkpoint.get("phase", "N/A")
            }
        elif isinstance(checkpoint, dict):
            state_dict = checkpoint
            metadata = {"epoch": "N/A", "val_loss": "N/A", "val_acc": "N/A", "phase": "N/A"}
        else:
            raise ValueError(f"Unexpected checkpoint format loaded from: {self.model_path}")

        self.model.load_state_dict(state_dict)
        return metadata

    def preprocess_image(self, image_input: Union[Image.Image, BinaryIO, str, Path, bytes]) -> torch.Tensor:
        """
        Loads and transforms an image input into a (1, 3, 224, 224) normalized PyTorch tensor.
        """
        if isinstance(image_input, Image.Image):
            pil_img = image_input
        elif isinstance(image_input, (str, Path)):
            pil_img = Image.open(image_input)
        elif isinstance(image_input, bytes):
            import io
            pil_img = Image.open(io.BytesIO(image_input))
        else:
            # File-like object (e.g. Django UploadedFile)
            pil_img = Image.open(image_input)

        # Convert to standard RGB (handles Grayscale, RGBA, CMYK, etc.)
        pil_img_rgb = pil_img.convert("RGB")

        # Apply deterministic transforms
        tensor = self.transform(pil_img_rgb)  # Shape: (3, 224, 224)
        tensor = tensor.unsqueeze(0)          # Shape: (1, 3, 224, 224)
        return tensor

    def predict(self, image_input: Union[Image.Image, BinaryIO, str, Path, bytes]) -> Dict[str, Any]:
        """
        Executes complete inference pass with Softmax confidence scoring.
        Returns predicted class, display name, confidence, all class probabilities, and latency.
        """
        start_time = time.perf_counter()

        # 1. Preprocess
        input_tensor = self.preprocess_image(image_input).to(self.device)

        # 2. Strict evaluation pass with zero gradients
        with torch.no_grad():
            logits = self.model(input_tensor)
            probabilities_tensor = F.softmax(logits, dim=1)[0]

        probabilities = probabilities_tensor.cpu().numpy().tolist()
        predicted_idx = int(torch.argmax(probabilities_tensor).item())
        confidence = float(probabilities[predicted_idx])
        predicted_class = CLASS_NAMES[predicted_idx]
        predicted_display = CLASS_DISPLAY_NAMES[predicted_class]

        latency_ms = (time.perf_counter() - start_time) * 1000

        # Build detailed per-class breakdown
        class_breakdown = []
        for idx, (c_name, prob) in enumerate(zip(CLASS_NAMES, probabilities)):
            display_name = CLASS_DISPLAY_NAMES[c_name]
            info = CLASS_INFO.get(c_name, {})
            class_breakdown.append({
                "class_index": idx,
                "internal_name": c_name,
                "display_name": display_name,
                "probability": round(prob, 4),
                "percentage": round(prob * 100, 2),
                "is_predicted": (idx == predicted_idx),
                "status": info.get("status", "Unknown"),
                "badge_class": info.get("badge_class", "badge-secondary"),
                "description": info.get("description", "")
            })

        predicted_info = CLASS_INFO.get(predicted_class, {})

        return {
            "predicted_class": predicted_class,
            "predicted_display_name": predicted_display,
            "predicted_class_index": predicted_idx,
            "confidence": round(confidence, 4),
            "confidence_percentage": round(confidence * 100, 2),
            "status": predicted_info.get("status", "Unknown"),
            "category": predicted_info.get("category", "General"),
            "badge_class": predicted_info.get("badge_class", "badge-primary"),
            "description": predicted_info.get("description", ""),
            "management": predicted_info.get("management", ""),
            "probabilities": class_breakdown,
            "raw_probabilities": [round(p, 4) for p in probabilities],
            "latency_ms": round(latency_ms, 2),
            "device": str(self.device),
            "device_name": self.device_name,
            "checkpoint_epoch": self.checkpoint_metadata.get("epoch", "N/A"),
            "checkpoint_val_loss": self.checkpoint_metadata.get("val_loss", "N/A"),
            "checkpoint_val_acc": self.checkpoint_metadata.get("val_acc", "N/A"),
            # ── Rich class detail fields (from config.CLASS_INFO) ──
            "is_disease": predicted_info.get("is_disease", False),
            "severity": predicted_info.get("severity", ""),
            "severity_color": predicted_info.get("severity_color", "#526B5C"),
            "infection_rate": predicted_info.get("infection_rate", ""),
            "causal_agent": predicted_info.get("causal_agent", ""),
            "symptoms": predicted_info.get("symptoms", []),
            "immediate_actions": predicted_info.get("immediate_actions", []),
            "treatment_steps": predicted_info.get("treatment_steps", []),
            "prevention": predicted_info.get("prevention", []),
            "expert_note": predicted_info.get("expert_note", ""),
            "health_indicators": predicted_info.get("health_indicators", []),
            "watch_for": predicted_info.get("watch_for", []),
            "maintenance_tips": predicted_info.get("maintenance_tips", []),
            "care_schedule": predicted_info.get("care_schedule", []),
        }

    def predict_with_gradcam(
        self,
        image_input: Union[Image.Image, BinaryIO, str, Path, bytes],
        alpha: float = 0.45
    ) -> Dict[str, Any]:
        """
        Executes ResNet-50 inference and computes Grad-CAM explainability visualization
        for the predicted pathology class using the final convolutional layer (layer4).
        """
        from predictor.gradcam import GradCAM

        # Extract PIL Image for visualization overlay
        if isinstance(image_input, Image.Image):
            pil_img = image_input
        elif isinstance(image_input, (str, Path)):
            pil_img = Image.open(image_input)
        elif isinstance(image_input, bytes):
            import io
            pil_img = Image.open(io.BytesIO(image_input))
        else:
            pil_img = Image.open(image_input)

        pil_img_rgb = pil_img.convert("RGB")

        # 1. Base Prediction
        result = self.predict(pil_img_rgb)
        predicted_idx = result["predicted_class_index"]

        # 2. Grad-CAM Computation on layer4
        input_tensor = self.preprocess_image(pil_img_rgb).to(self.device)
        grad_cam = GradCAM(self.model, target_layer=self.model.layer4)

        cam_map = grad_cam.generate_cam(input_tensor, target_class_idx=predicted_idx)
        heatmap_img, overlay_img = grad_cam.create_visualization(pil_img_rgb, cam_map, alpha=alpha)

        # 3. Base64 Data URI Conversion (Zero-disk footprint)
        import io
        import base64

        overlay_buf = io.BytesIO()
        overlay_img.save(overlay_buf, format="PNG")
        overlay_b64 = base64.b64encode(overlay_buf.getvalue()).decode("utf-8")
        overlay_uri = f"data:image/png;base64,{overlay_b64}"

        heatmap_buf = io.BytesIO()
        heatmap_img.save(heatmap_buf, format="PNG")
        heatmap_b64 = base64.b64encode(heatmap_buf.getvalue()).decode("utf-8")
        heatmap_uri = f"data:image/png;base64,{heatmap_b64}"

        result["gradcam_overlay_uri"] = overlay_uri
        result["gradcam_heatmap_uri"] = heatmap_uri
        result["gradcam_target_layer"] = "ResNet-50 layer4 (Bottleneck Conv5_x, 2048 Channels)"
        result["gradcam_cam_min"] = round(float(cam_map.min()), 4)
        result["gradcam_cam_max"] = round(float(cam_map.max()), 4)

        return result


# Global singleton instance accessor
_inference_engine = None
_engine_lock = threading.Lock()


def get_inference_engine() -> ResNet50InferenceEngine:
    """Returns the singleton ResNet50InferenceEngine instance."""
    global _inference_engine
    if _inference_engine is None:
        with _engine_lock:
            if _inference_engine is None:
                _inference_engine = ResNet50InferenceEngine()
    return _inference_engine


def predict_image(image_input: Union[Image.Image, BinaryIO, str, Path, bytes]) -> Dict[str, Any]:
    """Convenience wrapper for predicting a single image using the singleton engine."""
    engine = get_inference_engine()
    return engine.predict(image_input)


def predict_image_with_gradcam(
    image_input: Union[Image.Image, BinaryIO, str, Path, bytes],
    alpha: float = 0.45
) -> Dict[str, Any]:
    """Convenience wrapper for prediction + Grad-CAM generation."""
    engine = get_inference_engine()
    return engine.predict_with_gradcam(image_input, alpha=alpha)


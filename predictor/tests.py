"""
Inference & Explainable AI (Grad-CAM) Unit & Integration Tests.
Verifies model loading, 4-class output architecture, preprocessing, probability bounds,
Grad-CAM heatmap/overlay generation, and zero parameter modification.
"""

from io import BytesIO
from pathlib import Path
from PIL import Image
import numpy as np
import torch

from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from predictor.config import (
    MODEL_PATH,
    CLASS_NAMES,
    CLASS_MAPPING,
    CLASS_DISPLAY_NAMES,
    IMAGE_SIZE
)
from predictor.ml_model import (
    ResNet50InferenceEngine,
    predict_image,
    predict_image_with_gradcam,
    get_inference_engine
)
from predictor.gradcam import GradCAM


class ResNet50InferenceTests(TestCase):
    """Unit tests for PyTorch ResNet-50 inference engine."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.engine = get_inference_engine()

    def test_01_model_checkpoint_exists(self):
        """Verifies that the model checkpoint file is present at the configured path."""
        self.assertTrue(MODEL_PATH.exists(), f"Model checkpoint not found at: {MODEL_PATH}")

    def test_02_model_architecture_has_4_outputs(self):
        """Verifies that the ResNet-50 final classifier has in_features=2048 and out_features=4."""
        model = self.engine.model
        self.assertIsNotNone(model.fc)
        self.assertEqual(model.fc.out_features, 4, f"Expected 4 outputs, found {model.fc.out_features}")
        self.assertEqual(model.fc.in_features, 2048, f"Expected 2048 in_features for ResNet-50, found {model.fc.in_features}")

    def test_03_model_is_in_eval_mode(self):
        """Verifies that model is in eval mode and parameter gradients are disabled."""
        self.assertFalse(self.engine.model.training, "Model should be in eval() mode")
        for param in self.engine.model.parameters():
            self.assertFalse(param.requires_grad, "Model parameters must have requires_grad=False")

    def test_04_image_preprocessing_pipeline(self):
        """Verifies preprocessing produces a (1, 3, 224, 224) normalized float tensor."""
        # Create a synthetic 300x300 RGB test image
        img = Image.new("RGB", (300, 300), color=(120, 200, 80))
        tensor = self.engine.preprocess_image(img)

        self.assertIsInstance(tensor, torch.Tensor)
        self.assertEqual(tensor.shape, (1, 3, IMAGE_SIZE, IMAGE_SIZE))
        self.assertEqual(tensor.dtype, torch.float32)

    def test_05_prediction_returns_valid_class_and_probabilities(self):
        """Verifies inference output structure, valid class index, and probability range [0, 1]."""
        # Create a test synthetic RGB image
        img = Image.new("RGB", (256, 256), color=(50, 160, 90))
        result = self.engine.predict(img)

        # 1. Output Keys Check
        self.assertIn("predicted_class", result)
        self.assertIn("predicted_class_index", result)
        self.assertIn("confidence", result)
        self.assertIn("probabilities", result)

        # 2. Predicted Class Check
        self.assertIn(result["predicted_class"], CLASS_NAMES)
        self.assertIn(result["predicted_class_index"], [0, 1, 2, 3])
        self.assertEqual(result["predicted_display_name"], CLASS_DISPLAY_NAMES[result["predicted_class"]])

        # 3. Probability Bounds Check
        raw_probs = result["raw_probabilities"]
        self.assertEqual(len(raw_probs), 4)
        for p in raw_probs:
            self.assertGreaterEqual(p, 0.0, "Probability must be >= 0.0")
            self.assertLessEqual(p, 1.0, "Probability must be <= 1.0")

        # 4. Probabilities Sum to 1.0 (Approx within 1e-3)
        prob_sum = sum(raw_probs)
        self.assertAlmostEqual(prob_sum, 1.0, places=2, msg=f"Probabilities must sum to ~1.0, got {prob_sum}")

        # 5. Confidence Matches Max Probability
        self.assertAlmostEqual(result["confidence"], max(raw_probs), places=4)

    def test_06_no_gradients_created_during_inference(self):
        """Verifies that no computational graph / gradients are created during normal forward pass."""
        img = Image.new("RGB", (224, 224), color=(30, 80, 40))
        input_tensor = self.engine.preprocess_image(img).to(self.engine.device)

        with torch.no_grad():
            output = self.engine.model(input_tensor)

        self.assertIsNone(output.grad_fn, "Output should not have a grad_fn under torch.no_grad()")
        self.assertFalse(output.requires_grad, "Output tensor should not require grad")


class GradCAMExplainabilityTests(TestCase):
    """Unit tests for Grad-CAM activation mapping and model parameter immutability."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.engine = get_inference_engine()

    def test_01_gradcam_generation_and_normalization(self):
        """Verifies Grad-CAM produces a 2D numpy array bounded in [0.0, 1.0]."""
        img = Image.new("RGB", (320, 240), color=(60, 150, 80))
        input_tensor = self.engine.preprocess_image(img).to(self.engine.device)

        grad_cam = GradCAM(self.engine.model, target_layer=self.engine.model.layer4)
        cam = grad_cam.generate_cam(input_tensor, target_class_idx=2)

        self.assertIsInstance(cam, np.ndarray)
        self.assertEqual(cam.ndim, 2)
        self.assertGreaterEqual(float(cam.min()), 0.0)
        self.assertLessEqual(float(cam.max()), 1.0)

    def test_02_gradcam_visualization_overlay(self):
        """Verifies heatmap and overlay images have identical dimensions to original image."""
        orig_w, orig_h = 400, 300
        img = Image.new("RGB", (orig_w, orig_h), color=(40, 120, 90))
        input_tensor = self.engine.preprocess_image(img).to(self.engine.device)

        grad_cam = GradCAM(self.engine.model, target_layer=self.engine.model.layer4)
        cam = grad_cam.generate_cam(input_tensor, target_class_idx=1)
        heatmap_img, overlay_img = grad_cam.create_visualization(img, cam, alpha=0.45)

        self.assertEqual(heatmap_img.size, (orig_w, orig_h))
        self.assertEqual(overlay_img.size, (orig_w, orig_h))
        self.assertEqual(heatmap_img.mode, "RGB")
        self.assertEqual(overlay_img.mode, "RGB")

    def test_03_model_parameters_remain_unmodified(self):
        """Verifies that model parameters are strictly identical before vs after Grad-CAM."""
        # Snapshot weights before Grad-CAM
        weights_before = [p.clone() for p in self.engine.model.parameters()]

        img = Image.new("RGB", (224, 224), color=(100, 180, 50))
        result = self.engine.predict_with_gradcam(img)

        # Snapshot weights after Grad-CAM
        weights_after = [p.clone() for p in self.engine.model.parameters()]

        for p_before, p_after in zip(weights_before, weights_after):
            self.assertTrue(
                torch.equal(p_before, p_after),
                "Model parameter was altered during Grad-CAM execution!"
            )


class DjangoWebViewsTests(TestCase):
    """Integration tests for Django web routes, forms, and responses."""

    def setUp(self):
        self.client = Client()

    def test_01_home_page_status_code(self):
        """Verifies that the home page loads successfully (HTTP 200)."""
        response = self.client.get(reverse("predictor:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ARECANUT")
        self.assertContains(response, "DISEASE DETECTION")
        self.assertContains(response, "ResNet-50")

    def test_02_about_page_status_code(self):
        """Verifies that the about / methodology page loads successfully (HTTP 200)."""
        response = self.client.get(reverse("predictor:about"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "MODEL")
        self.assertContains(response, "METHODOLOGY")

    def test_03_form_rejects_empty_upload(self):
        """Verifies that submitting with no image triggers validation error."""
        response = self.client.post(reverse("predictor:home"), {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required")

    def test_04_form_rejects_invalid_file_extension(self):
        """Verifies that non-image files are rejected."""
        dummy_file = SimpleUploadedFile("script.py", b"print('malicious')", content_type="text/plain")
        response = self.client.post(reverse("predictor:home"), {"image": dummy_file})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Unsupported file format")

    def test_05_successful_image_upload_with_gradcam_result(self):
        """Verifies valid PNG/JPEG produces a complete 3-card result page with Grad-CAM overlay."""
        img_buffer = BytesIO()
        test_img = Image.new("RGB", (250, 250), color=(80, 180, 70))
        test_img.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        uploaded_file = SimpleUploadedFile("leaf_specimen.png", img_buffer.getvalue(), content_type="image/png")
        response = self.client.post(reverse("predictor:home"), {"image": uploaded_file})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "predictor/result.html")
        self.assertContains(response, "Diagnostic Assessment")
        self.assertContains(response, "Grad-CAM Model Attention")
        self.assertContains(response, "Original Specimen")
        self.assertContains(response, "data:image/png;base64,")
        self.assertContains(response, "Download Grad-CAM")
        self.assertContains(response, "Grad-CAM highlights image regions that contributed most strongly")

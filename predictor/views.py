"""
Views for Arecanut Disease Predictor.
Handles home page rendering, safe image upload validation, model inference, and results display.
"""

import base64
import io
import logging
from PIL import Image

from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages

from predictor.forms import ImageUploadForm
from predictor.ml_model import predict_image_with_gradcam
from predictor.config import CLASS_NAMES, CLASS_DISPLAY_NAMES, CLASS_INFO

logger = logging.getLogger(__name__)


def home_view(request):
    """
    Renders the main project landing and image upload page.
    Handles POST submissions for disease classification and Grad-CAM explainability.
    """
    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data["image"]
            try:
                # Read image bytes in-memory
                image_bytes = uploaded_file.read()
                uploaded_file.seek(0)

                # Inspect image dimensions for metadata display
                with Image.open(io.BytesIO(image_bytes)) as pil_img:
                    img_width, img_height = pil_img.size
                    img_format = pil_img.format or "JPEG"

                # Encode original image to base64 data URI (Zero-disk storage for privacy & security)
                mime_type = "image/png" if img_format.upper() == "PNG" else "image/jpeg"
                b64_encoded = base64.b64encode(image_bytes).decode("utf-8")
                image_data_uri = f"data:{mime_type};base64,{b64_encoded}"

                # Execute ResNet-50 4-Class Inference + Grad-CAM generation
                prediction_result = predict_image_with_gradcam(io.BytesIO(image_bytes), alpha=0.45)

                context = {
                    "prediction": prediction_result,
                    "image_data_uri": image_data_uri,
                    "gradcam_data_uri": prediction_result.get("gradcam_overlay_uri", ""),
                    "heatmap_data_uri": prediction_result.get("gradcam_heatmap_uri", ""),
                    "filename": uploaded_file.name,
                    "image_width": img_width,
                    "image_height": img_height,
                    "image_size_kb": round(len(image_bytes) / 1024, 1),
                    "image_format": img_format,
                }
                return render(request, "predictor/result.html", context)

            except FileNotFoundError as fnf_err:
                logger.error("Model checkpoint not found: %s", fnf_err)
                messages.error(
                    request,
                    "Trained model checkpoint (areca_resnet50_best.pth) is missing. "
                    "Please ensure the model file is placed in the 'models' directory."
                )
            except Exception as exc:
                logger.exception("Inference failure on uploaded image")
                messages.error(
                    request,
                    f"An error occurred during inference: {str(exc)}. Please try uploading a different image."
                )
        else:
            # Form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = ImageUploadForm()

    # Context for initial landing page
    classes_list = []
    for c_name in CLASS_NAMES:
        info = CLASS_INFO.get(c_name, {})
        classes_list.append({
            "internal_name": c_name,
            "display_name": CLASS_DISPLAY_NAMES[c_name],
            "status": info.get("status", ""),
            "category": info.get("category", ""),
            "badge_class": info.get("badge_class", "badge-secondary"),
            "description": info.get("description", ""),
        })

    context = {
        "form": form,
        "classes_list": classes_list,
    }
    return render(request, "predictor/home.html", context)


def about_view(request):
    """
    Renders academic details, methodology overview, and model performance metrics.
    """
    classes_list = []
    for c_name in CLASS_NAMES:
        info = CLASS_INFO.get(c_name, {})
        classes_list.append({
            "internal_name": c_name,
            "display_name": CLASS_DISPLAY_NAMES[c_name],
            "status": info.get("status", ""),
            "category": info.get("category", ""),
            "badge_class": info.get("badge_class", "badge-secondary"),
            "description": info.get("description", ""),
            "management": info.get("management", ""),
        })

    context = {
        "classes_list": classes_list,
    }
    return render(request, "predictor/about.html", context)

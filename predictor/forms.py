"""
Django Forms for Arecanut Image Upload and Safety Validation.
"""

from pathlib import Path
from django import forms
from PIL import Image
import io

from predictor.config import (
    MAX_UPLOAD_SIZE_BYTES,
    ALLOWED_EXTENSIONS,
    ALLOWED_MIME_TYPES
)


class ImageUploadForm(forms.Form):
    """
    Secure image upload form with multi-tier validation:
    1. Size boundary checks (<= 10MB)
    2. Extension whitelist (.jpg, .jpeg, .png)
    3. MIME type inspection
    4. PIL Image verification (corrupt/invalid payload detection)
    """
    image = forms.FileField(
        label="Select Arecanut Image",
        required=True,
        widget=forms.ClearableFileInput(attrs={
            "class": "file-input",
            "id": "image-upload-input",
            "accept": ".jpg,.jpeg,.png,image/jpeg,image/png"
        })
    )

    def clean_image(self):
        upload = self.cleaned_data.get("image")
        if not upload:
            raise forms.ValidationError("Please select an image file to analyze.")

        # 1. Size Validation
        if upload.size > MAX_UPLOAD_SIZE_BYTES:
            size_mb = upload.size / (1024 * 1024)
            raise forms.ValidationError(
                f"File size ({size_mb:.2f} MB) exceeds maximum allowed limit of {MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB."
            )

        # 2. Extension Validation
        ext = Path(upload.name).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            allowed_str = ", ".join(sorted(ALLOWED_EXTENSIONS))
            raise forms.ValidationError(
                f"Unsupported file format '{ext}'. Allowed formats: {allowed_str}"
            )

        # 3. Content Type (MIME) Validation
        content_type = getattr(upload, "content_type", "").lower()
        if content_type and content_type not in ALLOWED_MIME_TYPES:
            raise forms.ValidationError(
                f"Invalid file MIME type '{content_type}'. Must be a JPEG or PNG image."
            )

        # 4. Deep Image Verification with PIL
        try:
            # Read bytes into memory to verify without moving file pointer permanently
            file_bytes = upload.read()
            upload.seek(0)  # Reset pointer for downstream inference

            img = Image.open(io.BytesIO(file_bytes))
            img.verify()  # Verifies file integrity and header

            # Re-open after verify() closes the handle
            img = Image.open(io.BytesIO(file_bytes))
            img_format = (img.format or "").upper()
            if img_format not in {"JPEG", "PNG", "JPG", "MPO"}:
                raise forms.ValidationError(f"Invalid image structure ({img_format}). Expected JPEG or PNG.")

        except forms.ValidationError:
            raise
        except Exception as exc:
            raise forms.ValidationError(f"The uploaded file is corrupted or not a valid image: {str(exc)}")

        return upload

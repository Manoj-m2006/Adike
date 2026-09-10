"""
Centralized Configuration for Arecanut Disease Predictor Application.
Ensures consistent paths, class definitions, preprocessing parameters, and safety limits.
"""

from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"

# Primary Checkpoint Path with Root Fallback
PRIMARY_MODEL_PATH = MODELS_DIR / "areca_resnet50_best.pth"
ROOT_MODEL_PATH = BASE_DIR / "areca_resnet50_best.pth"
MODEL_PATH = PRIMARY_MODEL_PATH if PRIMARY_MODEL_PATH.exists() else ROOT_MODEL_PATH

# Authoritative 4-Class Mapping (Exact Match with Step 10/11)
CLASS_MAPPING = {
    "Healthy_Leaf": 0,
    "Healthy_Nut": 1,
    "Mahali_Koleroga": 2,
    "yellow leaf disease": 3
}

# Indexed Class Names
CLASS_NAMES = [
    "Healthy_Leaf",
    "Healthy_Nut",
    "Mahali_Koleroga",
    "yellow leaf disease"
]

# User-Facing Display Names
CLASS_DISPLAY_NAMES = {
    "Healthy_Leaf": "Healthy Leaf",
    "Healthy_Nut": "Healthy Nut",
    "Mahali_Koleroga": "Mahali Koleroga",
    "yellow leaf disease": "Yellow Leaf Disease"
}

# Botanical Details & Agronomic Context for UI
CLASS_INFO = {
    "Healthy_Leaf": {
        "status": "Healthy",
        "category": "Leaf",
        "badge_class": "badge-success",
        "icon": "leaf",
        "description": "The arecanut palm fronds exhibit uniform deep green coloration with healthy venation, devoid of necrotic chlorosis, spotting, or fungal blight.",
        "management": "Maintain standard agronomic practices, balanced NPK fertilization, and periodic routine canopy surveillance."
    },
    "Healthy_Nut": {
        "status": "Healthy",
        "category": "Nut / Fruit",
        "badge_class": "badge-success",
        "icon": "nut",
        "description": "Arecanut bunches display intact epicarp and calyx structures without water-soaked lesions, fungal mycelium growth, or premature fruit drop.",
        "management": "Ensure optimal bunch spacing, regular irrigation scheduling, and clean sanitation around the palm crown."
    },
    "Mahali_Koleroga": {
        "status": "Diseased",
        "category": "Fungal Infection (Fruit Rot)",
        "badge_class": "badge-danger",
        "icon": "alert-circle",
        "description": "Caused by Phytophthora meadii. Typical symptoms include water-soaked dark lesions near the nut calyx, white fungal felts, rotting, and massive premature nut shedding.",
        "management": "Apply 1% prophylactic Bordeaux mixture spray before monsoon onset, ensure field drainage, and collect/burn fallen diseased nuts."
    },
    "yellow leaf disease": {
        "status": "Diseased",
        "category": "Phytoplasma / Nutritional Disorder",
        "badge_class": "badge-warning",
        "icon": "alert-triangle",
        "description": "Characterized by prominent yellowing of inner leaflets starting from margins, necrosis of lamina, tapering of palm stems, and severe yield reduction.",
        "management": "Implement phytosanitary measures, provide balanced micronutrient management (Zinc/Boron), improve root zone aeration, and isolate severely afflicted palms."
    }
}

# Image Preprocessing Parameters (Strict Step 10/11 ImageNet Standards)
IMAGE_SIZE = 224
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# Upload & Security Validation Constraints
MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024  # 10 Megabytes
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/pjpeg"}

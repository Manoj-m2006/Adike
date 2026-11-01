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
        "management": "Maintain standard agronomic practices, balanced NPK fertilization, and periodic routine canopy surveillance.",
        # ── Rich detail fields ──
        "is_disease": False,
        "health_indicators": [
            "Uniform deep green coloration across all frond leaflets",
            "No chlorosis, necrotic spots, or leaf margin browning",
            "Healthy venation with no yellowing between veins",
            "Turgid fronds with good canopy spread and height",
            "Normal bunch development cycle (8\u20139 bunches/year)",
        ],
        "watch_for": [
            "Any yellowing starting at leaflet tips \u2014 may indicate Yellow Leaf Disease (YLD)",
            "Water-soaked spots near nut calyx \u2014 early Koleroga sign",
            "Unusual nut drop before harvest season",
            "Decline in bunch count below 6 per year",
            "Wilting or browning of central spindle (crown rot warning)",
        ],
        "maintenance_tips": [
            "Apply recommended NPK dose in May\u2013June and September",
            "Mulch the root zone with 12 kg organic matter per palm annually",
            "Ensure soil drainage is functional before monsoon",
            "Conduct quarterly canopy inspection for early signs of disease",
            "Maintain irrigation: 200 L/palm/day in dry months (Jan\u2013April)",
        ],
        "care_schedule": [
            "January\u2013March: Irrigation monitoring and bunch count audit",
            "May\u2013June: NPK + FYM application + pre-monsoon Bordeaux spray",
            "July\u2013August: Second Bordeaux spray during monsoon break",
            "October: Harvest audit and post-harvest nutrition application",
            "December: Phytosanitation \u2014 collect and burn plantation debris",
        ],
    },
    "Healthy_Nut": {
        "status": "Healthy",
        "category": "Nut / Fruit",
        "badge_class": "badge-success",
        "icon": "nut",
        "description": "Arecanut bunches display intact epicarp and calyx structures without water-soaked lesions, fungal mycelium growth, or premature fruit drop.",
        "management": "Ensure optimal bunch spacing, regular irrigation scheduling, and clean sanitation around the palm crown.",
        # ── Rich detail fields ──
        "is_disease": False,
        "health_indicators": [
            "Intact smooth green epicarp with no lesions or spots",
            "Firm nut calyx with no water-soaked darkening",
            "Bunches at expected size (30\u201350 nuts) with no premature drop",
            "No white fungal growth or mycelium visible on nuts",
            "Normal nut development colour (green \u2192 yellow \u2192 orange at maturity)",
        ],
        "watch_for": [
            "Any dark, water-soaked spots near nut calyx base \u2014 Koleroga warning",
            "Premature nut fall \u2014 5+ nuts/day is a serious warning sign",
            "White fluffy cottony growth on fallen nuts (Phytophthora mycelium)",
            "Discolouration of nut skin from green to black",
            "Foul decaying smell from the bunch area",
        ],
        "maintenance_tips": [
            "Schedule bunch-hooding with 125-gauge polythene before June",
            "Apply 1% Bordeaux mixture spray on all bunches before monsoon",
            "Ensure clean orchard floor to prevent fungal inoculum buildup",
            "Remove stray bunch trash to prevent Phytophthora overwintering",
            "Irrigate at 200 L/palm/day during summer months",
        ],
        "care_schedule": [
            "April\u2013May: Bunch hooding and pre-monsoon fungicide spray",
            "June\u2013August: Second spray, monitor bunches after each rain event",
            "September: Remove polythene covers after monsoon ends",
            "October\u2013December: Harvest, clean plantation floor thoroughly",
            "January\u2013March: Fertilizer and irrigation scheduling for dry season",
        ],
    },
    "Mahali_Koleroga": {
        "status": "Diseased",
        "category": "Fungal Infection (Fruit Rot)",
        "badge_class": "badge-danger",
        "icon": "alert-circle",
        "description": "Caused by Phytophthora meadii. Typical symptoms include water-soaked dark lesions near the nut calyx, white fungal felts, rotting, and massive premature nut shedding.",
        "management": "Apply 1% prophylactic Bordeaux mixture spray before monsoon onset, ensure field drainage, and collect/burn fallen diseased nuts.",
        # ── Rich detail fields ──
        "is_disease": True,
        "causal_agent": "Phytophthora meadii McRae (destructive oomycete water-mold)",
        "severity": "HIGH",
        "severity_color": "#B54747",
        "infection_rate": "Destroys 50\u201390% of seasonal crop if untreated",
        "symptoms": [
            "Water-soaked dark lesions near nut calyx (perianth end)",
            "White cottony fungal mycelium on fallen nuts",
            "Massive premature nut shedding within days",
            "Blackening and rotting of entire nut bunch",
            "Foul odour from decaying nuts on plantation floor",
            "Crown rot / bud rot in severe cases \u2192 tree death",
        ],
        "immediate_actions": [
            "Stop overhead irrigation immediately to reduce humidity",
            "Remove and burn ALL fallen diseased nuts the same day",
            "Do NOT compost infected material \u2014 incinerate it",
            "Isolate visibly infected palms from spray reach of neighbors",
            "Photograph symptoms and report to your local KVK immediately",
        ],
        "treatment_steps": [
            "Prepare 1% Bordeaux mixture: 1 kg CuSO\u2084 + 1 kg lime in 100 L water",
            "First spray: Immediately before monsoon onset (May\u2013June)",
            "Second spray: 40\u201345 days later during a monsoon rain break (July\u2013August)",
            "Third spray if rains persist beyond September",
            "Tie 125-gauge polythene covers (75\u00d760 cm) over all bunches before monsoon",
            "Excavate drainage channels 2\u20133 feet deep to prevent waterlogging",
        ],
        "prevention": [
            "Annual pre-monsoon Bordeaux spray (prophylactic \u2014 every year without exception)",
            "Polythene bunch hooding before June every season",
            "Plantation floor sanitation: collect fallen nuts weekly",
            "Improve field drainage before the monsoon season",
            "Maintain palm spacing for canopy airflow to reduce humidity",
            "Avoid overhead irrigation during humid monsoon months",
        ],
        "expert_note": "No curative chemical exists once systemic crown rot sets in. Prevention before monsoon is the only reliable strategy. Consult ICAR-CPCRI Kasaragod or local KVK for chemical dosage verification.",
    },
    "yellow leaf disease": {
        "status": "Diseased",
        "category": "Phytoplasma / Nutritional Disorder",
        "badge_class": "badge-warning",
        "icon": "alert-triangle",
        "description": "Characterized by prominent yellowing of inner leaflets starting from margins, necrosis of lamina, tapering of palm stems, and severe yield reduction.",
        "management": "Implement phytosanitary measures, provide balanced micronutrient management (Zinc/Boron), improve root zone aeration, and isolate severely afflicted palms.",
        # ── Rich detail fields ──
        "is_disease": True,
        "causal_agent": "Phytoplasma sp. (phloem-inhabiting obligate parasite, transmitted by insect vectors)",
        "severity": "HIGH",
        "severity_color": "#A96E16",
        "infection_rate": "60\u201380% yield reduction over 3\u20135 years if unmanaged",
        "symptoms": [
            "Intense yellowing of inner leaflets starting from tips and margins",
            "Yellowing progresses inward leaving green midribs only",
            "Fronds become brittle, shortened; crown tapers severely",
            "Nuts become small, cracked, with blackened spongy endosperm",
            "Premature nut fall and severely reduced bunch count",
            "Root zone waterlogging and soil acidity often co-occur",
        ],
        "immediate_actions": [
            "Improve field drainage immediately if waterlogging is present",
            "Apply foliar micronutrient spray: zinc sulfate 0.5% + boric acid 0.1%",
            "Set up yellow sticky traps to monitor planthopper vector populations",
            "Remove severely declined palms to reduce vector reservoir",
            "Report to agricultural officer for laboratory phytoplasma confirmation",
        ],
        "treatment_steps": [
            "NPK per palm/year: 100 g N (220 g urea) + 40 g P (200 g rock phosphate) + 140 g K (230 g MOP)",
            "Apply in two equal splits: May\u2013June and September\u2013October",
            "Apply 12 kg farmyard manure + 12 kg green leaf mulch per palm annually",
            "Zinc sulfate 0.5% foliar spray \u2014 twice per year (June and October)",
            "Magnesium sulfate soil application: 200 g per palm, twice yearly",
            "Construct deep drainage channels to eliminate root hypoxia",
        ],
        "prevention": [
            "Balanced NPK fertilization every season without skipping",
            "Maintain soil pH between 5.5 and 6.5 with liming if needed",
            "Plant companion crops (cocoa, banana) to improve soil biology",
            "Control planthopper and lace bug vectors with neem-based sprays",
            "Avoid waterlogging \u2014 lay drainage channels proactively every year",
            "Isolate and rogue severely diseased palms to prevent vector buildup",
        ],
        "expert_note": "There is NO chemical cure for phytoplasma infection. All management focuses on nutritional rehabilitation and vector control. Rogue terminally declined palms. Consult ICAR-CPCRI for region-specific protocols.",
    },
}

# Image Preprocessing Parameters (Strict Step 10/11 ImageNet Standards)
IMAGE_SIZE = 224
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# Upload & Security Validation Constraints
MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024  # 10 Megabytes
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/pjpeg"}

# 🌴 Arecanut Disease Predictor

An end-to-end Deep Learning & Django web application for automated detection and diagnosis of Arecanut (Betel Nut) palm diseases using a fine-tuned ResNet50 convolutional neural network.

---

## 📌 Features

- **Deep Learning Classification**: Fine-tuned ResNet-50 model trained to classify arecanut leaves and nuts.
- **Disease Classes Supported**:
  1. `Healthy Leaf`
  2. `Healthy Nut`
  3. `Mahali Koleroga` (Fruit Rot / *Phytophthora meadii*)
  4. `Yellow Leaf Disease` (Phytoplasma / Nutritional Disorder)
- **Django Web Interface**: Interactive user interface for drag-and-drop image uploads, real-time prediction, confidence scoring, disease symptoms, and agronomic management advisories.
- **Reports & Plots**: Model performance reports, confusion matrices, and training history logs included.

---

## 🏗️ Project Structure

```
Arecanut/
├── areca_project/            # Django project settings & configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── predictor/                # Django prediction app
│   ├── config.py             # Class mappings & configuration
│   ├── views.py              # Prediction and view handlers
│   ├── static/               # CSS, JS, and image assets
│   └── templates/            # HTML templates
├── models/                   # Pre-trained ResNet-50 weights
│   └── areca_resnet50_best.pth
├── plots/                    # Evaluation & training metric plots
├── reports/                  # Classification & evaluation reports
├── scripts/                  # Data preparation & training pipelines
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Manoj-m2006/Adike.git
cd Adike
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv venv

# On Windows:
.\venv\Scripts\activate

# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment (Optional for Multilingual AI Translations)
Create a `.env` file in the root folder:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 5. Run Migrations & Start Development Server
```bash
python manage.py migrate
python manage.py runserver
```

Open your browser and navigate to `http://127.0.0.1:8000/`.

---

## 📊 Dataset & Model
- **Model**: ResNet-50 (Transfer Learning with PyTorch)
- **Input Resolution**: 224 x 224 RGB
- **Evaluation**: Accuracy, Precision, Recall, F1-Score metrics are documented under `reports/` and visualized under `plots/`.

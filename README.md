# Intelligent SIM INDONESIA OCR Parser (Adaptive Driver's License Extractor)

A highly robust, noise-tolerant Optical Character Recognition (OCR) extraction service specifically designed to parse and validate Indonesian Driving Licenses (SIM A, BI, BII, and C).

The system combines adaptive image preprocessing, OCR text extraction, contextual validation, and regex-based parsing to reliably extract driver information from various image qualities, including mobile phone captures, faded cards, and scanned documents.

---

## ✨ Features

- **Adaptive Image Preprocessing**: Automatically calculates image contrast variance using standard deviation (`cv2.meanStdDev`). It applies **CLAHE** dynamically for low-contrast/faded images and completely bypasses it for already sharp/black-white images to prevent character pixelation.
- **Robust Anchor-Based Name Extraction**: Successfully handles corrupted OCR anchors (e.g., `NamwNamo`, `NAMSNENO`, `NMPNAN`) and captures multi-line names below the identifier tokens.
- **Smart Initial & Vowel Filtration**: Preserves critical single-letter initials like **"M"** (e.g., _M JOHN) while effectively dropping garbage OCR consonant strings (e.g., \_KXTPL_) by ensuring proper vowel composition.
- **Smart Expiry Correction**: Detects and auto-replaces broken expiry date headers (like `00*06-2026`) with structured current-day fallbacks.
- **Auto-Override SIM Classification**: Scans full-text contexts for vehicular keywords (`SEPEDA MOTOR`, `MOBIL PENUMPANG`, etc.) to automatically correct any mismatches in user-provided classification payloads.

---

## 🛠️ Technical Architecture

This system acts as a multi-layered verification engine:

1. **_Image Processing_**

- Resize normalization
- Contrast analysis
- CLAHE enhancement (conditional)
- Image binarization

2. **_OCR Engine_**
   Uses EasyOCR with:

```bash
["id", "en"]
```

language models.

3. **_Context Engine_**
   Performs:

- Token normalization
- Anchor detection
- Multi-line extraction
- OCR noise reduction

4. **\*Regex Parsing**
   Extracts structured information:

- SIM Number
- Driver Name
- Expiry Date
- SIM Type

5. **_Validation Layer_**
   Validates extracted data and applies automatic corrections when possible.

## 📂 Project Structure

project-root/
│
├── data/
│ └── ocr_repository.py
│
├── services/
│ └── sim_service.py
│
├── models/
│ └── sim_model.py
│
├── tests/
│
├── requirements.txt
└── README.md

## 🚀 Getting Started

### Prerequisites

Make sure you have the following system dependencies installed:

- Python 3.9+
- pip
- OpenCV (`opencv-python-headless`)
- EasyOCR
- Numpy

### Installation

1. Clone the repository:

```bash
git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
cd YOUR_REPO_NAME
```

2. Create and activate a virtual environment:

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

 # On macOS/Linux:
source venv/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Quick Usage Example

```bash
from data.ocr_repository import OCRRepository
from services.sim_service import SIMService

# Initialize components
repo = OCRRepository()
service = SIMService(repo)

# Process base64 string
base64_image_string = "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
sim_data = service.process_ocr_sim(base64_image_string, tipe_sim="C")

print(f"SIM Number: {sim_data.number}")
print(f"Driver Name: {sim_data.name}")
print(f"Expiry Date: {sim_data.expired_date}")
print(f"Status: {sim_data.status_sim}")
```

### 📋 Schema Structures

The service parses and yields data matching the following structured object format:

```JSON
{
    "type": "C",
    "number": "12345678910",
    "name": "JOHN DOE",
    "expired_date": "16/06/2026",
    "status_sim": "ACTIVE",
    "raw_text": [...]
}
```

### 📄 License

Distributed under the MIT License.
See LICENSE for more information.

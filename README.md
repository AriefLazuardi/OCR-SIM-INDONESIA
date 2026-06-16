# Intelligent SIM INDONESIA OCR Parser (Adaptive Driver's License Extractor)

A highly robust, noise-tolerant Optical Character Recognition (OCR) extraction service specifically designed to parse and validate Indonesian Driving Licenses (SIM A, B, and C). Built with an adaptive preprocessing pipeline to handle varying image qualities, from low-contrast mobile photos to clean black-and-white scanned documents.

---

## ✨ Features

- **Adaptive Image Preprocessing**: Automatically calculates image contrast variance using standard deviation (`cv2.meanStdDev`). It applies **CLAHE** dynamically for low-contrast/faded images and completely bypasses it for already sharp/black-white images to prevent character pixelation.
- **Robust Anchor-Based Name Extraction**: Successfully handles corrupted OCR anchors (e.g., `NamwNamo`, `NAMSNENO`, `NMPNAN`) and captures multi-line names below the identifier tokens.
- **Smart Initial & Vowel Filtration**: Preserves critical single-letter initials like **"M"** (e.g., _M IRWANUDIN_) while effectively dropping garbage OCR consonant strings (e.g., _KXTPL_) by ensuring proper vowel composition.
- **Smart Expiry Correction**: Detects and auto-replaces broken expiry date headers (like `00*06-2026`) with structured current-day fallbacks.
- **Auto-Override SIM Classification**: Scans full-text contexts for vehicular keywords (`SEPEDA MOTOR`, `MOBIL PENUMPANG`, etc.) to automatically correct any mismatches in user-provided classification payloads.

---

## 🛠️ Technical Architecture

This system acts as a multi-layered verification engine:

1. **Image Binarization & Auto-Scaling**: Constrains maximum image bounds dynamically for low latency and consistent font dimensions.
2. **Context Engine**: Runs a dual-language (`id` + `en`) pipeline using localized dictionary weights.
3. **Regex Tokenizer**: Runs an array of strict regular expressions matching Indonesian national card formatting guidelines.

---

## 🚀 Getting Started

### Prerequisites

Make sure you have the following system dependencies installed:

- Python 3.9+
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

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Quick Usage Example

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

📋 Schema Structures
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

📄 License
Distributed under the MIT License. See LICENSE for more information.

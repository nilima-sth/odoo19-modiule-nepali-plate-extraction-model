![GitHub top language](https://img.shields.io/github/languages/top/sanzgrapher/TRaiFIC-ANPR-Nepali-Number-Plate-Detection-plus-Character-Recognition)
![GitHub last commit](https://img.shields.io/github/last-commit/sanzgrapher/TRaiFIC-ANPR-Nepali-Number-Plate-Detection-plus-Character-Recognition)

# TRaiFIC: Automatic Nepali Number Plate Recognition System

TRaiFIC is an Automatic Number Plate Recognition (ANPR) system designed specifically for Nepali license plates. The system utilizes multiple machine learning models in a pipeline architecture to detect license plates, segment characters, and perform optical character recognition.

## 🔍 Overview

This project implements a complete ANPR pipeline:

1. **Plate Detection** - Detects license plates from images or video frames
2. **Character Segmentation** - Segments individual characters from the detected plate
3. **Character Recognition** - Recognizes the segmented characters

The system is deployed as a Flask web application for easy interaction.


## Demo

[![TRaiFIC Demo Video](https://img.shields.io/badge/Watch-Demo%20Video-blue)](https://drive.google.com/file/d/1-cuF_zvJ8r68mr4TatM_Fbf_fHvdS_TK/view)

<video src="https://github-production-user-asset-6210df.s3.amazonaws.com/101717917/439588348-f5c71dd6-7080-4bec-9dcf-4c7a689a85ea.mp4?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAVCODYLSA53PQK4ZA%2F20250501%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20250501T115137Z&X-Amz-Expires=300&X-Amz-Signature=30a129e90087a683dda015d3808cbbdb9995a400b5646a1012b378b42ed76c08&X-Amz-SignedHeaders=host" controls></video>





## 📂 Project Structure

```
ANPR/
├── application/          # Flask web application
│   ├── app.py           # Main Flask application
│   ├── config.py        # Application configuration
│   ├── model_loader.py  # Model loading utilities
│   ├── image_processing.py  # Image processing pipeline
│   ├── templates/       # HTML templates
│   └── static/          # Static assets (CSS, JS, images)
├── models/              # Machine learning models
│   ├── pd-traific/      # Plate detection model
│   ├── sg/              # Segmentation model
│   └── char-traiffic/   # Character recognition model
├── main.py
├── .python-version
└── pyproject.toml       # Project dependencies and metadata
```

## 🚀 Installation

This project uses [UV](https://github.com/astral-sh/uv), an extremely fast Python package and project manager written in Rust. Follow these steps to set up the project:

### Prerequisites

1. Python 3.10 or higher
2. [UV](https://github.com/astral-sh/uv) installed on your system

### Clone the Repository

```bash
git clone https://github.com/sanzgrapher/TRaiFIC-ANPR-Nepali-Number-Plate-Detection-plus-Character-Recognition.git
cd ANPR
```

### Install Dependencies with UV

```bash
uv sync
```

This will install all dependencies defined in the `pyproject.toml` file.

## 🏃 Running the Application

From the project root (`TraificNPR`), run:

```bash
cd /home/nilima/Documents/TraificNPR
./.venv/bin/python -m TraificNPR.application.app
```

The service will be available at:

- UI: `http://127.0.0.1:5001/`
- API: `http://127.0.0.1:5001/api/v1/ocr`

## ⚙️ Configuration

Key runtime settings are in `application/config.py` and environment variables:

- `OCR_API_TOKEN` (env): API token for `/api/v1/ocr`
- `FLASK_SECRET_KEY` (config): Flask session secret
- `MAX_CONTENT_LENGTH` (config): max upload size (32 MB by default)
- `ALLOWED_EXTENSIONS` (config): supported image/video extensions

Set token for protected API mode:

```bash
export OCR_API_TOKEN="your-token"
```

Token behavior:

- `OCR_API_TOKEN` empty: auth disabled (development mode)
- `OCR_API_TOKEN` set: token required on every API request

## 🔌 OCR API (Odoo Integration)

This service also exposes a machine-to-machine OCR API endpoint.

- Base URL (default when running `application/app.py`): `http://127.0.0.1:5001`
- Endpoint: `POST /api/v1/ocr`
- Content-Type: `multipart/form-data`
- Required form field: `file`

### API token setup (optional)

Token auth is controlled by `OCR_API_TOKEN`.

- If `OCR_API_TOKEN` is set, requests must provide a valid token.
- If it is empty, auth is disabled (development mode).

```bash
export OCR_API_TOKEN="your-token"
```

Accepted token headers:

- `X-API-Token: your-token`
- `Authorization: Bearer your-token`

### cURL example

```bash
curl -X POST "http://127.0.0.1:5001/api/v1/ocr" \
  -H "X-API-Token: your-token" \
  -F "file=@/path/to/plate-image.jpg"
```

### Response format

```json
{
  "filename": "plate-image.jpg",
  "processing_time_seconds": 0.842,
  "plate_count": 1,
  "plates": []
}
```

Error responses are structured JSON with appropriate HTTP codes (`401`, `400`, `503`, `500`).

### Odoo `requests.post` example

```python
import requests

api_url = "http://127.0.0.1:5001/api/v1/ocr"
token = "your-token"
file_path = "/path/to/plate-image.jpg"

with open(file_path, "rb") as f:
    response = requests.post(
        api_url,
        headers={"X-API-Token": token},
        files={"file": f},
        timeout=120,
    )

response.raise_for_status()
result = response.json()
print(result)
```

## 🛠️ Troubleshooting

If `python -m TraificNPR.application.app` fails with exit code `127` from your shell, use the absolute interpreter path from this README:

```bash
./.venv/bin/python -m TraificNPR.application.app
```

This bypasses broken local launcher scripts and starts the service reliably.

## 🔄 Pipeline Process

The ANPR system follows this workflow:

1. **Plate Detection (PD)**: Uses YOLOv8-based model to detect license plates in images
2. **Segmentation (SG)**: Isolates and segments characters from the detected plate
3. **Character Recognition (CHAR)**: Recognizes individual characters using a trained model

Model pipeline: `PD → SG → CHAR`

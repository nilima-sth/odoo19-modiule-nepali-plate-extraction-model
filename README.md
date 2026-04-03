![GitHub top language](https://img.shields.io/github/languages/top/sanzgrapher/TRaiFIC-ANPR-Nepali-Number-Plate-Detection-plus-Character-Recognition)
![GitHub last commit](https://img.shields.io/github/last-commit/sanzgrapher/TRaiFIC-ANPR-Nepali-Number-Plate-Detection-plus-Character-Recognition)

# TRaiFIC: Automatic Nepali Number Plate Recognition System

This repository focuses on deployment and integration updates added on top of an existing Nepali number plate OCR model.

## What Was Added

This version is mainly about making the service production/integration ready.

1. Added machine-to-machine API endpoint: `POST /api/v1/ocr`
2. Added optional token auth via `OCR_API_TOKEN`
3. Added token header support:
  - `X-API-Token`
  - `Authorization: Bearer <token>`
4. Added request validation for file upload and extension checks
5. Added structured JSON errors with integration-friendly status codes:
  - `401` unauthorized
  - `400` bad request
  - `503` models unavailable
  - `500` internal error
6. Added startup logging for auth mode (enabled/disabled)
7. Added Odoo-friendly API docs and examples
8. Added run/troubleshooting guidance (including exit `127` workaround)

## Base Model Note

Core OCR model logic remains the same. Most changes here are around API access, security, configuration, and integration workflow.

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

## 🔄 Base Pipeline (Unchanged)

1. Plate Detection (PD)
2. Character Segmentation (SG)
3. Character Recognition (CHAR)

Pipeline: `PD -> SG -> CHAR`

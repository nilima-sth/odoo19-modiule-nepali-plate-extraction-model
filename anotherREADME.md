# Nepali OCRs

This repository currently contains the TraificNPR ANPR service as a Flask microservice for Nepali number plate recognition.

Source attribution:
- Model baseline was obtained from TRaiFIC ANPR:
	https://github.com/sanzgrapher/TRaiFIC-ANPR-Nepali-Number-Plate-Detection-plus-Character-Recognition?tab=readme-ov-file
- This repo adapts it for microservice usage and Odoo integration.

## Service Location

- App code: TraificNPR/application
- Main server file: TraificNPR/application/app.py
- Default port: 5001

## Run Service

```bash
cd TraificNPR
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install flask ultralytics deep-sort-realtime lap numpy split-folders pillow opencv-python torch
cd application
python app.py
```

Open:
- http://127.0.0.1:5001/

## API Endpoints

- GET / : upload UI
- POST / : upload UI submit (HTML response)
- POST /api/v1/ocr : machine endpoint (JSON response)

## Token Protection

The API endpoint supports token protection using environment variable OCR_API_TOKEN.

Set token before running:

```bash
export OCR_API_TOKEN="replace-with-a-long-random-token"
python app.py
```

Send token using either:
- X-API-Token header
- Authorization: Bearer <token>

If OCR_API_TOKEN is empty, API token check is disabled.

## API Request Example

```bash
curl -X POST "http://127.0.0.1:5001/api/v1/ocr" \
	-H "X-API-Token: replace-with-a-long-random-token" \
	-F "file=@/absolute/path/to/plate.jpg"
```

Example JSON response:

```json
{
	"filename": "plate.jpg",
	"processing_time_seconds": 0.842,
	"plate_count": 1,
	"plates": [
		{
			"final_text": "बा १ च १२३४"
		}
	]
}
```

## Odoo Integration (Server-Side Python)

```python
import requests

OCR_URL = "http://127.0.0.1:5001/api/v1/ocr"
OCR_TOKEN = "replace-with-a-long-random-token"

def extract_plate_from_image(image_path):
		with open(image_path, "rb") as f:
				response = requests.post(
						OCR_URL,
						headers={"X-API-Token": OCR_TOKEN},
						files={"file": ("plate.jpg", f, "image/jpeg")},
						timeout=60,
				)
		response.raise_for_status()
		return response.json()
```
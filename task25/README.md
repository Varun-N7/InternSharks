# Task 25 — Multimodal AI Vision API

A FastAPI-based multimodal vision service that accepts image uploads and uses an OpenRouter vision model to analyze and compare images.

## Features

- Image validation using Pillow
- AI image analysis
- Optional natural-language questions about an image
- Image-to-image comparison
- Similarity and difference detection
- Image metadata extraction
- Structured JSON responses using Pydantic models
- Clear error handling for invalid images and vision-service failures
- FastAPI Swagger/OpenAPI documentation

## API Endpoints

### Analyze an Image

```http
POST /ai/vision/analyze
```

**Content-Type:** `multipart/form-data`

Fields:

| Field | Type | Required | Description |
|---|---|---:|---|
| `image` | File | Yes | Image to analyze |
| `question` | Text | No | Optional question about the image |

### Compare Two Images

```http
POST /ai/vision/compare
```

**Content-Type:** `multipart/form-data`

Fields:

| Field | Type | Required | Description |
|---|---|---:|---|
| `image1` | File | Yes | First image |
| `image2` | File | Yes | Second image |

The comparison response contains:

- `summary`
- `similarities`
- `differences`
- `uncertainty`

## Project Structure

```text
task25/
├── app/
│   ├── models/
│   │   └── vision.py
│   ├── routes/
│   │   └── vision.py
│   ├── services/
│   │   ├── image_service.py
│   │   └── vision_service.py
│   ├── config.py
│   └── main.py
├── tests/
│   ├── test_image_service.py
│   └── test_vision_routes.py
├── .env
├── .env.example
└── README.md
```

## Configuration

Create a `.env` file in the task root and configure the OpenRouter settings required by the application.

Example:

```env
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=your_vision_model
REQUEST_TIMEOUT_SECONDS=60
```

**Do not commit real API keys to Git.**

## Environment Setup

This project uses the shared virtual environment located outside the task directory.

From the project root:

```bash
cd ~/Desktop/doubletap
source venv/bin/activate
```

Then enter the task:

```bash
cd task25
```

Install dependencies if needed:

```bash
pip install -r requirements.txt
```

Pillow is required for image validation.

## Running the API

From `task25`:

```bash
export PYTHONPATH=.
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

OpenAPI schema:

```text
http://127.0.0.1:8000/openapi.json
```

## Postman Testing

The API was manually verified through Postman.

### Test Results

| # | Test | Result |
|---:|---|---|
| 1 | Analyze Image | ✅ Passed |
| 2 | Compare Two Different Images | ✅ Passed |
| 3 | Invalid Image Handling | ✅ Passed |
| 4 | Vision Service Error Handling | ✅ Passed |
| 5 | Image Metadata | ✅ Passed |
| 6 | Question-Based Image Analysis | ✅ Passed |
| 7 | Compare Different Images | ✅ Passed |
| 8 | Invalid Image in Compare | ✅ Passed |
| 9 | Compare Identical Images | ✅ Passed |
| 10 | Missing Required Image | ✅ Passed |

### Test 2

Test 2 used two different images. This verified that the comparison endpoint could identify meaningful similarities and differences.

### Test 9

Test 9 used the same image for both inputs and verified that the service recognized the images as identical and returned no differences.

## Example Analyze Response

```json
{
  "success": true,
  "status_code": 200,
  "data": {
    "summary": "...",
    "visual_elements": [],
    "document_analysis": null,
    "product_analysis": null,
    "ui_analysis": null,
    "answer": null,
    "uncertainty": [],
    "image_metadata": {
      "filename": "image.jpg",
      "content_type": "image/jpeg",
      "size_bytes": 47370,
      "width": 612,
      "height": 321
    }
  }
}
```

## Error Handling

### Invalid Image

Invalid or unsupported image uploads return HTTP `400`.

Example:

```json
{
  "detail": {
    "error": "Unsupported image type",
    "error_category": "invalid_image"
  }
}
```

### Vision Service Failure

Vision service failures return HTTP `502`.

Example:

```json
{
  "detail": {
    "error": "test vision failure",
    "error_category": "vision_service_error"
  }
}
```

### Missing Required Fields

FastAPI automatically returns a validation error when required multipart fields are missing.

## Reliability and Security

- API credentials are loaded from environment configuration.
- Images are validated before being sent to the vision model.
- The vision prompts instruct the model not to follow instructions contained inside uploaded images.
- Visible text inside images is treated as image content rather than system or developer instructions.
- The prompts require uncertainty to be reported rather than inventing unsupported information.
- Model responses are parsed as JSON and validated against Pydantic models.
- Real API credentials should never be committed to source control.

## Quick Start

```bash
cd ~/Desktop/doubletap
source venv/bin/activate

cd task25
export PYTHONPATH=.

uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

Use Postman to test:

```text
POST /ai/vision/analyze
POST /ai/vision/compare
```

---

**Task 25 — Multimodal AI Vision API**
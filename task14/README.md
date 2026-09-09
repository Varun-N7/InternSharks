# Task 14 — AI Document & Text Summarization API

A simple FastAPI service that uses OpenRouter to summarize text in three modes: `brief`, `detailed`, and `bullet_points`.

## Features

- FastAPI REST API
- OpenRouter AI integration
- `POST /ai/summarize`
- Three summary types
- Separate system and user prompts
- Extracts summary, main topic, and keywords
- Pydantic request and AI-response validation
- Input validation and AI service error handling
- Environment variables for API configuration

## Project Structure

```text
task14/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── routes/
│   │   └── summarizer.py
│   ├── services/
│   │   └── summarizer_service.py
│   ├── models/
│   │   └── summarizer.py
│   └── prompts/
│       └── summarizer_prompt.py
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.10+
- OpenRouter API key

## Installation

```bash
cd task14
python -m venv .venv
```

Activate the virtual environment.

macOS/Linux:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create `.env`:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openrouter/free
```

Keep the real API key private.

`.env.example`:

```env
OPENROUTER_API_KEY=
OPENROUTER_MODEL=
```

## Run the API

```bash
python -m uvicorn app.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## Endpoint

### POST `/ai/summarize`

Request:

```json
{
    "text": "The development team is building a payment API integration for the client.",
    "summary_type": "brief"
}
```

Accepted values:

```text
brief
detailed
bullet_points
```

## Example Response

```json
{
    "success": true,
    "status_code": 200,
    "data": {
        "summary_type": "brief",
        "summary": "The team is developing a payment API integration.",
        "main_topic": "Payment API integration",
        "keywords": [
            "payment API",
            "integration",
            "development"
        ]
    }
}
```

## Summary Modes

### Brief

```json
{
    "text": "The development team is building a payment API integration for the client.",
    "summary_type": "brief"
}
```

Returns a short summary containing the main information.

### Detailed

```json
{
    "text": "The development team is building a payment API integration for the client. Testing is blocked because the client has not provided API credentials.",
    "summary_type": "detailed"
}
```

Returns a more complete summary while preserving important details.

### Bullet Points

```json
{
    "text": "The development team is building a payment API integration for the client. Testing is blocked because the client has not provided API credentials.",
    "summary_type": "bullet_points"
}
```

Returns the important information as bullet points.

## Validation Tests

### Empty text

```json
{
    "text": "",
    "summary_type": "brief"
}
```

Expected: `422 Unprocessable Entity`

### Missing text

```json
{
    "summary_type": "brief"
}
```

Expected: `422 Unprocessable Entity`

### Invalid summary type

```json
{
    "text": "The payment API integration is complete.",
    "summary_type": "short"
}
```

Expected: `422 Unprocessable Entity`

### Empty body

```json
{}
```

Expected: `422 Unprocessable Entity`

## AI Response Validation

The AI is instructed to return JSON with:

```json
{
    "summary_type": "brief",
    "summary": "summary of the text",
    "main_topic": "main topic",
    "keywords": [
        "keyword1",
        "keyword2"
    ]
}
```

The AI response is validated with Pydantic before being returned.

## Error Handling

The API handles:

- Invalid input
- Invalid OpenRouter API key
- OpenRouter rate limits
- OpenRouter service failures
- Model availability failures
- Invalid AI responses

Validation errors use HTTP `422`. AI/provider failures use server-side error responses.

## Postman Tests

The Task 14 test plan includes:

1. Brief Summary
2. Detailed Summary
3. Bullet Points Summary
4. Short Input
5. Long Input
6. Empty Input
7. Missing Text
8. Invalid Summary Type
9. Empty Body
10. Invalid API Key / AI Service Failure

Successful requests should return:

```text
HTTP 200
success: true
```

Validation tests should return:

```text
HTTP 422
success: false
error: VALIDATION_ERROR
```

## Security

Never commit `.env`, API keys, virtual environments, or Python cache files.

Recommended `.gitignore`:

```text
.env
venv/
.venv/
__pycache__/
*.pyc
```

## Git

```bash
git add task14/
git commit -m "Add AI document summarization API"
git push
```

Check before committing:

```bash
git status
```

## Learning Goals

This task demonstrates:

- FastAPI endpoint design
- Pydantic validation
- System prompts vs user prompts
- Structured AI output
- OpenRouter integration
- External AI error handling
- Environment variables
- Postman API testing

## Author

Task 14 — AI Document & Text Summarization API
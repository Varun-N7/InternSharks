# AI Text Analysis API

A FastAPI-based REST API that uses Groq AI to analyze text and return structured information such as summary, category, priority, sentiment, and keywords.

## Features

- FastAPI REST API
- Groq AI integration
- Structured AI text analysis
- Pydantic request validation
- Environment-based API key configuration
- Consistent error responses
- Postman-tested API endpoints

## Project Structure

```text
task13/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── ai.py
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── analysis_prompt.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── ai.py
│   └── services/
│       ├── __init__.py
│       └── ai_service.py
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Technologies Used

- Python
- FastAPI
- Uvicorn
- Pydantic
- Groq API
- python-dotenv
- Postman

## Setup

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd doubletap/task13
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
```

Do not commit `.env` to GitHub.

The project includes `.env.example`:

```env
GROQ_API_KEY=
```

## Run the API

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

## API Documentation

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Endpoints

### Health Check

```http
GET /
```

Example response:

```json
{
    "success": true,
    "message": "AI Text Analysis API is running"
}
```

### Analyze Text

```http
POST /ai/analyze
```

Request:

```json
{
    "text": "The payment API integration is blocked because we are waiting for credentials from the client."
}
```

Example response:

```json
{
    "success": true,
    "status_code": 200,
    "data": {
        "summary": "The payment API integration is blocked while waiting for client credentials.",
        "category": "blocker",
        "priority": "high",
        "sentiment": "negative",
        "keywords": [
            "payment API",
            "credentials",
            "client"
        ]
    }
}
```

## Supported Categories

- `blocker`
- `update`
- `request`
- `question`
- `other`

## Supported Priorities

- `low`
- `medium`
- `high`

## Supported Sentiments

- `positive`
- `neutral`
- `negative`

## Validation

The `text` field is required and must contain at least one character.

Invalid request:

```json
{}
```

Response:

```json
{
    "success": false,
    "status_code": 422,
    "error": "VALIDATION_ERROR",
    "message": "Invalid request data"
}
```

## Testing

The API was tested using Postman with the following test cases:

1. Positive / Happy Path
2. Missing Required Field
3. Empty Text
4. Invalid Text Type
5. Short Valid Text
6. Long Text
7. Request Classification
8. Negative Sentiment

## Security

The Groq API key is stored in `.env` and excluded from Git using `.gitignore`.

Never commit or publicly expose the real API key.

## Author

Task 13 — AI Text Analysis API
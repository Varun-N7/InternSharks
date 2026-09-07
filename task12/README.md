# Task 12 - AI Text Assistant API

A simple AI Text Assistant API built using FastAPI and Groq.

## Features

- FastAPI REST API
- Groq Python SDK
- Pydantic request validation
- Environment variable configuration
- Structured error responses
- Rate-limit handling
- AI service error handling
- Separation of routes, services, models, and configuration

## Request Flow

User Request
    |
    v
FastAPI Endpoint
    |
    v
AI Service
    |
    v
Groq API
    |
    v
LLM
    |
    v
Generated Response
    |
    v
FastAPI Response

## Project Structure

task12/
|
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   └── ai.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── ai_service.py
│   │
│   └── models/
│       ├── __init__.py
│       └── ai.py
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md

## Requirements

- Python 3.10+
- FastAPI
- Uvicorn
- Groq Python SDK
- Pydantic
- python-dotenv
- Groq API key

## Installation

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Configuration

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

The Groq API key must never be hardcoded in the source code.

The `.env` file is ignored by Git and must not be committed.

## Run the API

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

## API Documentation

FastAPI automatically provides interactive API documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

## Generate AI Response

### Endpoint

```text
POST /ai/generate
```

### Full URL

```text
http://127.0.0.1:8000/ai/generate
```

### Request Body

```json
{
    "prompt": "Explain FastAPI in simple words"
}
```

### Successful Response

HTTP 200:

```json
{
    "success": true,
    "status_code": 200,
    "response": "FastAPI is a Python framework used to build APIs..."
}
```

## Validation

### Empty Prompt

Request:

```json
{
    "prompt": ""
}
```

Response:

HTTP 422:

```json
{
    "success": false,
    "status_code": 422,
    "error": "VALIDATION_ERROR",
    "message": "Prompt cannot be empty"
}
```

### Missing Prompt

Request:

```json
{}
```

Response:

HTTP 422:

```json
{
    "success": false,
    "status_code": 422,
    "error": "VALIDATION_ERROR",
    "message": "Invalid request data"
}
```

### Invalid Request Body

Example:

```json
{
    "prompt": ["hello", "world"]
}
```

Response:

HTTP 422:

```json
{
    "success": false,
    "status_code": 422,
    "error": "VALIDATION_ERROR",
    "message": "Invalid request data"
}
```

## AI Service Errors

If the external Groq service is unavailable, the API returns:

HTTP 503:

```json
{
    "success": false,
    "status_code": 503,
    "error": "AI_SERVICE_UNAVAILABLE",
    "message": "AI service is currently unavailable"
}
```

Raw Groq errors and internal exceptions are not exposed to API clients.

## Rate Limit Handling

If the Groq service returns a rate-limit error, the API returns:

HTTP 429:

```json
{
    "success": false,
    "status_code": 429,
    "error": "AI_RATE_LIMITED",
    "message": "AI service rate limit exceeded"
}
```

## Security

- Groq API key is stored in an environment variable.
- `.env` is excluded from Git.
- API keys are never returned in API responses.
- Internal exceptions are not exposed to clients.
- Stack traces are not exposed to clients.
- Raw Groq errors are not returned to clients.

## Testing

The API was tested using Postman.

The following test cases were covered:

1. Normal prompt
2. Different prompt
3. Empty prompt
4. Missing prompt
5. Invalid request body
6. Invalid Groq API key
7. Groq rate-limit handling

Both HTTP status codes and JSON response bodies were verified.

## Learning Points

This project demonstrates:

- What an LLM is
- What an AI API is
- How to use the Groq Python SDK
- How FastAPI communicates with an external AI service
- How prompts are sent to an LLM
- Difference between system and user messages
- How to protect API keys
- How to handle API rate limits
- How to handle external service failures
- Why route and service logic should be separated

## System and User Messages

The AI service uses a system message to define the assistant behavior and a user message containing the actual prompt.

Example:

```python
messages=[
    {
        "role": "system",
        "content": "You are a helpful AI assistant."
    },
    {
        "role": "user",
        "content": prompt
    }
]
```

The system message provides instructions to the AI assistant.

The user message contains the request that should be answered.

## Scope

This project intentionally focuses on a simple AI text generation API.

It does not include:

- MongoDB
- Chat history
- RAG
- Agents
- Authentication
- Vector databases
- Complex AI workflows

The main goal is to understand how a FastAPI application communicates with an external LLM service through the Groq API.

## Git Security

The following files and directories must not be committed:

```text
.env
venv/
.venv/
__pycache__/
*.pyc
.pytest_cache/
```

Use `.env.example` as the safe template for environment configuration.

## Author

Task 12 - AI Text Assistant API
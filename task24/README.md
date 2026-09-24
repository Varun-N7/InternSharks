Task 24 — AI Observability API

Overview

Task 24 implements an AI request API with request tracing and observability.

The application records:

Request trace IDs

Request status

Model and prompt version

Request start/end times

Total latency

Prompt/completion/total token usage

Estimated cost

Trace spans

Error information

Aggregate observability metrics

The project uses FastAPI and SQLite.

Project Structure

task24/
├── app/
│   ├── config.py
│   ├── main.py
│   ├── middleware/
│   ├── models/
│   ├── observability/
│   ├── prompts/
│   ├── routes/
│   ├── services/
│   └── storage/
├── tests/
│   └── test_observability.py
├── .env
├── .env.example
├── .gitignore
├── observability.db
├── README.md
└── requirements.txt

Setup

Activate the virtual environment:

source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Configure .env:

OPENROUTER_MODEL=inclusionai/ling-3.0-flash-vl:free
LOG_AI_CONTENT=false
SLOW_REQUEST_THRESHOLD_MS=3000
PROMPT_VERSION=assistant_v1
DATABASE_PATH=observability.db

If an OpenRouter API key is not configured, the application uses the demo/mock response path.

Run the API

From the project root:

uvicorn app.main:app --reload

API base URL:

http://127.0.0.1:8000

Main Endpoints

AI request

POST /ai/ask

Example body:

{
  "message": "Hello, how are you?"
}

A successful response contains the response and a trace_id.

Retrieve a trace

GET /observability/traces/{trace_id}

Returns stored trace information including latency, token usage, cost, and spans.

List traces

GET /observability/traces

Supports pagination and filters such as status, model, and prompt version.

Failed traces

GET /observability/traces/failures

Slow traces

GET /observability/traces/slow

Metrics

GET /observability/metrics

Returns aggregate request, latency, token, and cost metrics.

Testing

Run automated tests with:

pytest -q

Postman Test Checklist

The Task 24 verification covered exactly these 10 tests:

AI request — successful request — PASSED

AI request — request tracking / trace ID — PASSED

AI request — logging / observability — PASSED

AI request — token usage — PASSED

AI request — latency measurement — PASSED

AI request — cost calculation — PASSED

Observability endpoint — retrieve trace data — PASSED

Metrics endpoint — retrieve metrics — PASSED

Invalid AI request — PASSED

Missing required request field — PASSED

Final result: 10/10 tests passed (100%).

Example Trace

{
  "trace_id": "trace_example",
  "request_type": "ai_ask",
  "model": "demo-model",
  "prompt_version": "assistant_v1",
  "status": "success",
  "total_duration_ms": 10.153,
  "prompt_tokens": 9,
  "completion_tokens": 6,
  "total_tokens": 15,
  "estimated_cost_usd": 0.0000135
}

Trace spans include operations such as:

prompt_build

openrouter_call

Database

SQLite is used for persistence.

Database file:

observability.db

The database stores traces and their associated spans.

Notes

Do not commit real API keys to source control.

Keep .env local and use .env.example as the configuration template.

The demo/mock path provides token and cost values for observability testing when no API key is configured.
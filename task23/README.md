# Task 23 - AI Evaluation Framework

## Overview

Task 23 is an AI evaluation framework for evaluating answers against a RAG-style evaluation dataset.

The framework includes deterministic evaluation, semantic evaluation, optional LLM-judge evaluation, evaluation thresholds, evaluation runs, result persistence, and API endpoints for running and inspecting evaluations.

## Project Structure

```text
app/
├── routes/
│   └── eval.py
├── evals/
│   ├── runner.py
│   ├── deterministic.py
│   ├── semantic.py
│   └── structured.py
├── services/
│   ├── ai_service.py
│   └── judge_service.py
├── storage/
│   ├── database.py
│   └── evaluation_repository.py
├── config.py
└── main.py

tests/
├── test_ai_service.py
├── test_config.py
├── test_deterministic.py
├── test_runner.py
├── test_semantic.py
└── test_structured.py
```

## Evaluation

The evaluation framework checks:

- Keyword matching
- Refusal behavior for unsupported questions
- Semantic groundedness
- Semantic relevance
- Structured judge responses
- Configurable evaluation thresholds
- Evaluation results and case-level results
- Latency recording

Questions with missing information should be answered with a refusal instead of an unsupported guess.

## API

The FastAPI application exposes the following evaluation endpoints.

### Health

```http
GET /health
```

Example response:

```json
{
  "status": "ok",
  "service": "task23-evaluation"
}
```

### Run Evaluation

```http
POST /eval/run
```

Example request:

```json
{
  "suite": "rag_basic",
  "prompt_version": "v1"
}
```

Example response:

```json
{
  "success": true,
  "status_code": 200,
  "data": {
    "run_id": "eval_run_example",
    "suite": "rag_basic",
    "prompt_version": "v1",
    "total_cases": 15,
    "passed": 3,
    "failed": 12,
    "pass_rate": 0.2
  }
}
```

### Get Evaluation Run

```http
GET /eval/runs/{run_id}
```

Returns the stored evaluation run and its individual case results.

### Get Failed Cases

```http
GET /eval/runs/{run_id}/failures
```

Returns only the failed cases for the specified evaluation run.

## Persistence

SQLite is used to persist evaluation runs and individual case results.

Stored information includes:

- Evaluation run ID
- Suite
- Model
- Prompt version
- Total cases
- Passed cases
- Failed cases
- Pass rate
- Case ID
- Question
- Actual answer
- Evaluation checks and scores
- Latency

API keys are not stored in evaluation results.

## Running the Application

Activate the virtual environment:

```bash
source venv/bin/activate
```

Start the FastAPI application:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

## Running Tests

From the project directory, run:

```bash
PYTHONPATH=/home/varun/Desktop/doubletap/task23 pytest -q
```

Current test result:

```text
26 passed
```

## Postman Testing

The implemented API was tested through Postman for:

1. Run Evaluation Suite
2. Get Evaluation Run
3. Get Failed Cases
4. Invalid Evaluation Suite
5. Invalid Prompt Version

## Notes

The evaluation runner uses the `rag_basic` evaluation dataset and the configured evaluation logic to produce deterministic evaluation results.

The project uses FastAPI for the API layer and SQLite for persistence.
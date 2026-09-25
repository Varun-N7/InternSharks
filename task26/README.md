# Task 26 - Async AI Jobs

## Overview

Task 26 implements an asynchronous AI job-processing API using FastAPI.

The API accepts document-analysis jobs, places them into an in-memory queue, and provides endpoints to retrieve job status and results.

## Features

- Create document-analysis jobs
- `summary` and `extract` analysis types
- Validate unsupported analysis types
- Validate uploaded files
- Queue jobs for background processing
- Retrieve jobs by ID
- Retrieve completed results
- List and filter jobs
- Cancel queued jobs
- Jobs health endpoint
- In-memory repository and queue for development/testing

## Project Structure

```text
task26/
├── app/
│   ├── main.py
│   ├── models/
│   │   └── job.py
│   ├── routes/
│   │   └── jobs.py
│   ├── repositories/
│   │   └── job_repository.py
│   ├── queue/
│   │   └── fake_redis.py
│   ├── services/
│   │   └── ai_service.py
│   └── workers/
│       └── worker.py
├── tests/
│   └── test_jobs.py
└── README.md
```

## Environment

Supported settings include:

```text
APP_NAME=Task 26 - Async AI Jobs
WORKER_COUNT=2
PROCESSING_DELAY_SECONDS=2
```

These may be supplied through environment variables.

## Run the Server

Activate the virtual environment:

```bash
source venv/bin/activate
```

Start the application:

```bash
uvicorn app.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### Health

```http
GET /jobs/health
```

Expected status: `200 OK`.

### Create Document Analysis Job

```http
POST /jobs/document-analysis
```

Use `multipart/form-data`:

```text
file           File
analysis_type  Text
```

Supported analysis types:

```text
summary
extract
```

Successful job creation returns `202 Accepted` with a generated `job_id` and `queued` status.

### Get Job

```http
GET /jobs/{job_id}
```

Returns the job information.

- Existing job: `200 OK`
- Unknown job: `404 Not Found`

### Get Job Result

```http
GET /jobs/{job_id}/result
```

If the job is not completed, the API returns `409 Conflict`.

### List Jobs

```http
GET /jobs
```

Optional filters:

```text
status
analysis_type
```

Example:

```http
GET /jobs?status=queued
```

### Cancel Job

```http
POST /jobs/{job_id}/cancel
```

Only queued jobs can be cancelled.

## Postman Tests Completed

The API was manually tested with Postman for:

1. Create job with `summary` — `202 Accepted`
2. Create job with `extract` — `202 Accepted`
3. Invalid `analysis_type` — `400 Bad Request`
4. Missing file — `422 Unprocessable Entity`
5. Empty file — `400 Bad Request`
6. Missing `analysis_type` — current implementation uses the default `summary`
7. Get job by ID — `200 OK`
8. Get result before completion — `409 Conflict`
9. Invalid job ID — `404 Not Found`
10. List jobs — `200 OK`

## Automated Tests

Automated tests are located at:

```text
tests/test_jobs.py
```

Run:

```bash
python -m pytest -v
```

The test suite covers job health, creation, analysis-type validation, file validation, job retrieval, result retrieval, and job listing.

A successful run reached:

```text
10 passed
```

## Development Notes

The current implementation uses in-memory components:

- `JobRepository` stores jobs in memory.
- `FakeRedisQueue` provides an in-memory queue.
- `JobWorker` processes queued jobs.

In-memory data is lost when the server restarts. A production implementation could replace these components with persistent storage and Redis or another production queue.

## Current Status

Task 26 API implementation and the documented manual/automated testing flow are in place.
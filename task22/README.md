# Task 22 — Stateful AI Project Operations Agent

## Overview

Task 22 implements a stateful AI project-operations agent with:
- Tool-based project operations
- Human approval for write operations
- Retry and timeout handling
- Non-retryable failure handling
- Persistent run state and resume support
- Completed-action protection
- OpenRouter integration
- External-service failure simulation

## Running the Application

```bash
source venv/bin/activate
uvicorn app.main:app --reload
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## Main API Endpoints

### Create an agent run

```http
POST /agent/runs
```

Example:

```json
{
  "goal": "List all projects."
}
```

Write example:

```json
{
  "goal": "Create a project named Postman Test Project."
}
```

### Get a run

```http
GET /agent/runs/{run_id}
```

### Resume a run

```http
POST /agent/runs/{run_id}/resume
```

### Approve a pending action

```http
POST /agent/runs/{run_id}/actions/{action_id}/approval
```

Body:

```json
{
  "approved": true
}
```

## Reliability Test Suite

Run:

```bash
pytest -q tests/test_reliability.py
```

Verified result during testing:

```text
5 passed in 3.30s
```

The suite covers retryable failures, non-retryable failures, retry exhaustion, and timeout behavior.

## Postman Test Progress

| # | Test | Status |
|---|---|---|
| 1 | Read tool, no approval | Completed |
| 2 | Write tool should require approval | Completed |
| 3 | Approve the pending write | Completed |
| 4 | Rejected write action-1 | Completed |
| 5 | Rejected write action-2 | Completed |
| 6 | External Service Timeout and Retry Exhaustion | Completed |
| 7 | Successful tool execution | Pending |
| 8 | Temporary failure → retry → success | Pending |
| 9 | Multiple temporary failures → success | Pending |
| 10 | Non-retryable failure → no retry | Pending |
| 11 | Timeout handling | Pending |
| 12 | OpenRouter retryable failure | Completed |
| 13 | OpenRouter non-retryable failure | Pending |
| 14 | Retry counter verification | Pending |
| 15 | Retry state survives restart | Pending |
| 16 | Successful write | Completed |
| 17 | Duplicate write request / idempotency | Pending |
| 18 | Same idempotency key returns previous result | Pending |
| 19 | Write timeout → retry without duplicate | Pending |
| 20 | Completed action cannot execute again | Completed |
| 21 | Resume interrupted run | Completed |
| 22 | Completed run cannot incorrectly resume | Completed |
| 23 | Approval + retry integration | Completed |

## Verified Behaviors

### Completed action protection

Approving an already completed action returned:

```json
{
  "success": false,
  "status_code": 404,
  "error": {
    "code": 404,
    "message": "No pending action found"
  }
}
```

### Resume interrupted run

A resumed run returned successfully and continued its execution state.

### Completed run cannot be resumed

Attempting to resume a completed run returned:

```json
{
  "success": false,
  "error": "Completed runs cannot be resumed"
}
```

### Approval flow

A write operation correctly enters:

```text
waiting_for_approval
```

with a pending action. After approval, the write executes and the run can become:

```text
completed
```

## Approval + Retry Integration Flow (Test 23)

Verified flow for sensitive write operations requiring retry:

```text
approval_required (status: waiting)
       ↓
approval granted (POST /agent/runs/{run_id}/actions/{action_id}/approval)
       ↓
tool_execution (status: failed, error: Temporary service failure, attempt: 1, retryable: true)
       ↓
tool_execution (status: success, attempt: 2)
       ↓
run completed
```

## Reliability Errors

The project classifies failures using:

```text
RetryableError
NonRetryableError
```

Retryable operations can be retried according to the configured retry policy. Non-retryable failures stop without additional retries.

OpenRouter failures are classified by response type, including rate limits and temporary HTTP errors.

## Current Status

Task 22 is under manual Postman verification.

Tests marked **Completed** above were verified through API responses observed during testing. Tests marked **Pending** have not been counted as completed.
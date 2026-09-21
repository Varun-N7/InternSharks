# Task 21: Stateful AI Agent with Human Approval Workflow

## Overview

Task 21 extends the goal-based AI agent from Task 20 into a **stateful
AI agent with a Human-in-the-Loop (HITL) approval workflow**.

The agent can inspect project-management data automatically, while
sensitive actions that modify application data require explicit human
approval before execution.

The agent can pause, persist its state in SQLite, wait for approval or
rejection, resume after approval, and continue from where it stopped.

## Objective

Build a FastAPI-based AI Project Operations Agent using OpenRouter that
can:

-   Understand a high-level user goal
-   Use predefined backend tools
-   Automatically execute read-only tools
-   Detect write actions that require approval
-   Pause execution before sensitive actions
-   Persist agent run state in SQLite
-   Wait for human approval or rejection
-   Revalidate approved actions before execution
-   Prevent duplicate approval/execution
-   Maintain an execution trace
-   Survive FastAPI/server restarts
-   Stop safely at the maximum agent step limit

No LangChain, LangGraph, CrewAI, AutoGen, or similar agent framework is
used. The orchestration is implemented manually.

## Architecture

``` text
User
  |
  v
FastAPI API
  |
  v
Agent Runner
  |
  +--------------------+
  |                    |
  v                    v
Read Tools          Write Tools
(auto execute)      (approval required)
  |                    |
  |                    v
  |              Pending Action
  |                    |
  |              Human Approval
  |               /          \
  |            Approve       Reject
  |               |             |
  |               v             v
  +--------> Execute Tool     Reject
                    |
                    v
              Observe Result
                    |
                    v
               Continue Agent
                    |
                    v
                Final Result
```

### Persistence

``` text
Agent Runner
     |
     v
SQLite
 ├── agent_runs
 └── approvals
```

SQLite stores paused agent state and approval actions so a run can be
recovered after a server restart.

## Technology Stack

-   Python
-   FastAPI
-   OpenRouter
-   SQLite
-   Pydantic
-   Requests
-   python-dotenv
-   Uvicorn

## Project Structure

``` text
task21/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── runner.py
│   │   ├── registry.py
│   │   └── state_manager.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── project_service.py
│   │   └── approval_service.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── approval.py
│   │   └── project.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── employee_tools.py
│   │   ├── project_tools.py
│   │   └── task_tools.py
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── run_repository.py
│   │   └── action_repository.py
│   └── prompts/
│       ├── __init__.py
│       └── agent_prompt.py
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Agent Workflow

``` text
Goal
  ↓
Agent decides next action
  ↓
Tool selected
  ↓
Is approval required?
  ├── No → Execute automatically
  │          ↓
  │       Observe result
  │          ↓
  │       Continue
  │
  └── Yes → Create pending action
             ↓
          Persist state
             ↓
          PAUSE
             ↓
       Human approval
          /       \
      Approve    Reject
        |           |
        v           v
   Revalidate     Reject
        |
        v
   Execute action
        |
        v
   Persist result
        |
        v
   Resume agent
```

The backend controls approval decisions. The LLM does not decide whether
an action is sensitive.

## API Endpoints

### Start Agent Run

**POST** `/agent/runs`

Example request:

``` json
{
  "goal": "Create Project Apollo and add Arun to it."
}
```

### Get Run Details

**GET** `/agent/runs/{run_id}`

Returns the persisted run state, including run ID, goal, status, step
count, pending action, and execution trace.

### Approve or Reject an Action

**POST** `/agent/runs/{run_id}/actions/{action_id}/approval`

Approve:

``` json
{
  "approved": true
}
```

Reject:

``` json
{
  "approved": false
}
```

Approval applies only to the specified pending action.

## Run Statuses

``` text
running
waiting_for_approval
completed
partially_completed
failed
rejected
```

The backend controls these state transitions.

## Tools

### Read-only tools

These execute automatically:

-   `find_employee`
-   `get_project`
-   `list_projects`
-   `get_project_tasks`
-   `get_task`

### Write tools

These require human approval:

-   `create_project`
-   `add_project_member`
-   `create_project_task`
-   `update_task_status`
-   `delete_project_task`

The tool registry contains approval metadata so the orchestration layer
can determine whether approval is required.

## Sample Employees

``` text
101 - Arun  - Backend Developer
102 - Priya - UI/UX Designer
103 - Rahul - QA Engineer
```

Employee IDs are resolved through the backend rather than invented by
the AI.

## Project Data

Projects contain:

``` text
project_id
name
description
members
status
```

Project status:

``` text
active
completed
```

Project names must be unique.

## Project Tasks

Project tasks contain:

``` text
task_id
project_id
title
priority
status
assigned_to
```

Priority:

``` text
low
medium
high
```

Status:

``` text
todo
in_progress
completed
```

Backend validation ensures that the project and employee exist,
duplicate project members are rejected, assigned employees are valid
project members, and task priority/status values are valid.

## Human Approval Safety

The backend is authoritative for write operations.

Before an approved write action executes, the action is validated again
because application state may have changed while the action was waiting
for approval.

For example:

``` text
Run A:
Create Project ValidationTest
        ↓
Waiting for approval

Run B:
Create Project ValidationTest
        ↓
Approved
        ↓
Project created

Run A:
Approved later
        ↓
Backend revalidation
        ↓
Project with this name already exists
        ↓
400 Bad Request
```

This prevents stale approved actions from bypassing current backend
rules.

## Duplicate Approval Protection

An action can only be executed once.

If an already executed action is approved again, the API returns:

``` text
409 Conflict
```

Example:

``` json
{
  "success": false,
  "status_code": 409,
  "error": {
    "code": 409,
    "message": "Action has already been executed"
  }
}
```

## Persistent State

Agent execution state is stored in SQLite.

### `agent_runs`

Stores:

-   run ID
-   goal
-   status
-   step count
-   messages
-   pending action
-   execution trace

### `approvals`

Stores:

-   action ID
-   run ID
-   tool
-   arguments
-   approval status

This allows paused runs to survive a FastAPI/server restart.

## Execution Trace

Each run stores an operational execution trace.

Example:

``` json
{
  "step": 1,
  "type": "tool_execution",
  "tool": "find_employee",
  "status": "success"
}
```

Approval events are also recorded:

``` json
{
  "step": 2,
  "type": "approval_required",
  "tool": "create_project",
  "status": "waiting"
}
```

The trace contains operational information only. Hidden reasoning,
chain-of-thought, prompts, and API keys are not exposed.

## Step Limit

The agent has a maximum execution limit:

``` text
MAX_AGENT_STEPS = 10
```

The step count persists across pause/resume. If the maximum is reached,
the agent stops safely instead of running indefinitely.

## Environment Variables

Create a `.env` file:

``` env
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=inclusionai/ling-3.0-flash-vl:free
```

Use `.env.example` as the template.

**Do not commit `.env` or API keys to GitHub.**

## Installation

``` bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the Application

From the `task21` directory:

``` bash
uvicorn app.main:app --reload
```

API:

``` text
http://127.0.0.1:8000
```

FastAPI documentation:

``` text
http://127.0.0.1:8000/docs
```

## Testing

Testing was performed using Postman.

  \#   Test                                      Result
  ---- ----------------------------------------- --------
  1    Read Tools Execute Automatically          PASS
  2    Write Action Requires Human Approval      PASS
  3    Approved Action Executes Successfully     PASS
  4    Rejected Action Does Not Execute          PASS
  5    Agent Resumes After Approval              PASS
  6    Multiple Approvals In One Workflow        PASS
  7    Invalid Run ID / Action ID                PASS
  8    Approval For Wrong Run                    PASS
  9    Duplicate Approval Protection             PASS
  10   Already Executed Action Protection        PASS
  11   Backend Validation After Approval         PASS
  12   Step Count Persists Across Pause Resume   PASS
  13   Restart Preserves Paused Run              PASS
  14   Completed Run Cannot Be Resumed           PASS
  15   OpenRouter Failure Handling               PASS

### Test 11

A project named `ValidationTest` was created by one run. A second paused
run attempted to create the same project. After approval, backend
validation rejected the action with:

``` text
400 Bad Request
Project with this name already exists
```

### Test 12

The agent first executed `find_employee`, then paused before
`create_project`.

The run had:

``` text
step_count = 1
```

After approval and resume:

``` text
step_count = 2
```

This confirmed that the step count persisted across pause/resume.

### Test 13

A run was paused with:

``` text
status = waiting_for_approval
```

FastAPI was restarted. The same run was retrieved using:

``` text
GET /agent/runs/{run_id}
```

The pending action and waiting state were still present, confirming
SQLite persistence.

### Test 15

An invalid OpenRouter model was temporarily configured. The API returned
a controlled `400 Bad Request` response without exposing a traceback or
API key.

## Error Handling

The API handles:

-   Run not found
-   Action not found
-   Action belonging to another run
-   Invalid approval state
-   Duplicate approval
-   Already executed action
-   Unknown tool
-   Invalid tool arguments
-   Backend validation failure
-   OpenRouter errors
-   Invalid OpenRouter model
-   Invalid OpenRouter API key
-   OpenRouter rate limits
-   Agent step limit

Example structured error:

``` json
{
  "success": false,
  "status_code": 400,
  "error": {
    "code": 400,
    "message": "Error message"
  }
}
```

Raw stack traces, API keys, hidden reasoning, and prompts are not
returned to API clients.

## Example Workflow

Goal:

``` text
Create Project Apollo and add Arun to it.
```

1.  Agent requests `create_project`.
2.  Backend detects that it is a write action.
3.  Agent pauses with `waiting_for_approval`.
4.  Human approves.
5.  Project is created and the real `project_id` returned by the backend
    is used.
6.  Agent resolves Arun using `find_employee`.
7.  Agent requests `add_project_member`.
8.  Backend pauses again for approval.
9.  Human approves.
10. Member is added and the agent completes the goal.

## Key Learning Outcomes

-   Stateful AI agents
-   Human-in-the-loop workflows
-   Approval gates
-   Pause and resume execution
-   Persistent agent state
-   SQLite-based state storage
-   Safe write operations
-   Backend-controlled approval requirements
-   Revalidation after approval
-   Duplicate approval protection
-   Execution traces
-   Step counting across resumes
-   Server restart recovery
-   Controlled AI/API error handling
-   Manual agent orchestration without agent frameworks

## Security Considerations

-   Keep `OPENROUTER_API_KEY` in `.env`
-   Never commit `.env`
-   Do not expose API keys in responses
-   Do not expose hidden reasoning
-   Validate tool arguments on the backend
-   Treat LLM-generated arguments as untrusted input
-   Require approval for state-changing tools
-   Revalidate actions immediately before execution
-   Prevent duplicate execution of approved actions

## Git / Deliverables

Include:

``` text
README.md
requirements.txt
.env.example
.gitignore
app/
```

Do not commit:

``` text
.env
.venv/
__pycache__/
*.pyc
.pytest_cache/
agent_state.db
```

Recommended commit messages:

``` text
Initial Task 21 stateful agent
Add approval workflow
Add SQLite agent persistence
Add action validation and duplicate protection
Complete Task 21 testing
```

## Task Progression

``` text
Task 17
RAG
  ↓
Task 18
AI Tool Calling
  ↓
Task 19
Multi-Tool Calling
  ↓
Task 20
Goal-Based Agent
  ↓
Task 21
Stateful Agent + Human Approval
```

Task 21 adds persistent state and human approval on top of the agent
orchestration concepts developed in the previous tasks.
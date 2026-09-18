# Task 20: Goal-Based AI Agent with Planning & Tool Execution

## Overview

This project implements a goal-based AI agent using FastAPI and OpenRouter.

Unlike a normal chatbot, the user provides a high-level goal. The AI agent decides which backend tools are required, executes them, observes the actual results, and continues until the goal is completed or cannot proceed.

## Agent Flow

User Goal
→ AI decides next action
→ Select Tool
→ Execute Backend Tool
→ Observe Result
→ Decide Next Action
→ Continue
→ Final Response

The agent does not use a fixed sequence of operations.

## Example Goal

```text
Create a project called Apollo, add Arun and Priya to it, create a high priority backend API task assigned to Arun, and create a medium priority UI design task assigned to Priya.
```

The agent can determine that it needs to:

1. Create the project
2. Add Arun
3. Add Priya
4. Create the backend API task
5. Create the UI design task

The actual order is decided by the AI based on the goal and tool results.

## Technologies

- Python
- FastAPI
- OpenRouter
- Pydantic
- Requests
- Python-dotenv
- Uvicorn

## Project Structure

```text
task20/
├── app/
│   ├── agent/
│   │   ├── runner.py
│   │   └── registry.py
│   ├── routes/
│   │   └── agent.py
│   ├── services/
│   │   ├── project_service.py
│   │   ├── employee_service.py
│   │   └── task_service.py
│   ├── models/
│   │   ├── agent.py
│   │   ├── project.py
│   │   └── task.py
│   ├── tools/
│   │   ├── employee_tools.py
│   │   ├── project_tools.py
│   │   └── task_tools.py
│   ├── storage/
│   │   ├── project_store.py
│   │   └── run_store.py
│   ├── prompts/
│   │   └── agent_prompt.py
│   ├── config.py
│   └── main.py
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## API Endpoint

### Run Agent

```text
POST /agent/run
```

Request:

```json
{
  "goal": "Create a project called Apollo and add Arun and Priya to it."
}
```

The user only provides the goal.

The user does not directly specify which backend functions should be called.

## Available Tools

### find_employee

Finds an employee using employee ID or name.

Sample employees:

- 101 - Arun - Backend Developer
- 102 - Priya - UI/UX Designer
- 103 - Rahul - QA Engineer

### create_project

Creates a new project.

The backend generates the project ID.

### get_project

Retrieves an existing project using its project ID.

### add_project_member

Adds an existing employee to a project.

The backend prevents duplicate project members.

### create_project_task

Creates a task inside a project.

Supported priorities:

```text
low
medium
high
```

Supported statuses:

```text
todo
in_progress
completed
```

### list_project_tasks

Lists tasks belonging to a project.

### update_task_status

Updates the status of an existing project task.

## Backend Authority

The AI is responsible for deciding which tools are needed.

The backend is responsible for validating and executing the operations.

The AI cannot directly modify project or task data.

Backend validation checks:

- Employee existence
- Project existence
- Duplicate project names
- Duplicate project members
- Valid project IDs
- Valid employee IDs
- Valid task priorities
- Valid task statuses
- Valid task assignments

Tool results are treated as authoritative.

## Tool Observation

After a tool executes, its actual result is returned to the AI.

For example:

```text
create_project
        ↓
Backend creates project
        ↓
project_id = 1
        ↓
AI observes project_id = 1
        ↓
add_project_member(project_id=1, employee_id=101)
```

The agent does not invent project IDs.

## Conditional Execution

The agent can handle conditions based on backend results.

For example:

```text
Find employee Suresh.
If Suresh exists, add him to the project.
If Suresh does not exist, continue without adding him
and explain the situation.
```

## Partial Completion

If some operations succeed and another operation cannot be completed, the agent should report the result honestly.

Example:

```text
Create Project Titan and assign a backend task to employee Naveen.
```

If Naveen does not exist, the agent must not invent an employee.

The valid part can be completed and the final response should explain what could not be completed.

## Agent Step Limit

The agent uses a maximum execution step limit to prevent endless tool execution.

The configured limit is:

```text
MAX_AGENT_STEPS = 10
```

If the limit is reached, the agent stops and returns a controlled failure response.

## Execution Trace

Each agent run receives a unique run ID.

The execution trace records:

- Run ID
- Goal
- Step number
- Tool used
- Validated arguments
- Tool result
- Success/failure status

The trace does not expose hidden AI reasoning or chain-of-thought.

Execution traces can be retrieved using:

```text
GET /agent/runs/{run_id}
```

## Environment Variables

Create a `.env` file:

```env
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=your_tool_calling_model_here
```

Do not commit `.env` or API keys to GitHub.

## Installation

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Application

```bash
uvicorn app.main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Testing

The API can be tested using Postman or Swagger UI.

Important test scenarios include:

1. Simple one-tool goal
2. Two-tool goal
3. Multiple-tool goal
4. Dependent tool calls
5. Conditional execution
6. Fully completed goal
7. Partially completed goal
8. Missing employee
9. Missing project
10. Duplicate project
11. Invalid priority
12. Invalid task status
13. Step limit
14. Empty goal
15. OpenRouter failure

## Example Multi-Step Goal

```text
Create a project called Apollo, add Arun and Priya, create a high priority backend API task assigned to Arun, and create a medium priority UI design task assigned to Priya.
```

Expected behavior:

```text
Create Project
      ↓
Add Arun
      ↓
Add Priya
      ↓
Create Backend API Task
      ↓
Create UI Design Task
      ↓
Return Final Result
```

## Design Principle

This project intentionally implements the agent loop manually.

No agent framework such as:

- LangChain
- LangGraph
- CrewAI
- AutoGen

is used.

The purpose is to understand the basic mechanism behind agentic systems:

```text
Goal
→ Decide
→ Tool
→ Execute
→ Observe
→ Decide Again
→ Complete
```

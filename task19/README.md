# Task 19 - AI Employee Assistant with Multi-Tool Calling

## Objective

Build an AI Employee Assistant using FastAPI and OpenRouter.

The assistant understands employee requests and selects the correct
backend tools to retrieve information or perform controlled leave actions.

Unlike Task 18, this task supports:

- Multiple tool calling
- Tool chaining
- Conditional tool execution
- Conversation context
- Session isolation
- Backend business-rule validation
- Read and action operations

## Architecture

User
  ↓
FastAPI
  ↓
Employee Assistant Service
  ↓
OpenRouter LLM
  ↓
Tool Decision
  ↓
Backend Tool
  ↓
Tool Result
  ↓
OpenRouter LLM
  ↓
Final Response

## Available Tools

### get_employee

Retrieves employee information.

### get_leave_balance

Retrieves casual and sick leave balance.

### get_company_holidays

Retrieves company holidays.

### apply_leave

Creates a pending leave request after backend validation.

### get_leave_requests

Retrieves employee leave requests.

## Multi-Tool Calling

The assistant can call multiple tools in sequence.

Example:

1. Get employee information.
2. Get leave balance.
3. Return combined information.

## Conditional Tool Calling

Example:

Check whether an employee has casual leave available.

If leave is available:

1. Apply leave.
2. Retrieve leave requests.
3. Show the result.

If leave is not available, the leave action is not performed.

## Conversation Context

Each request contains a session_id.

Example:

Session:
employee-session-1

User:
Who is employee 102?

Assistant:
Employee 102 is Priya, a UI/UX Designer.

User:
How many sick leaves does she have?

The assistant uses the previous conversation context to understand
that "she" refers to employee 102.

Different sessions maintain separate conversation history.

## Tool Validation

AI-generated tool arguments are treated as untrusted.

The backend validates:

- Employee ID
- Leave type
- Start date
- End date
- Leave reason
- Employee existence
- Leave balance
- Date ordering

The AI cannot directly modify backend data.

Only registered backend tools can perform actions.

## Tool Call Limit

The assistant allows a maximum of 5 tool-call rounds.

This prevents unlimited tool loops.

## Project Structure

task19/
├── app/
│   ├── routes/
│   ├── services/
│   ├── models/
│   ├── tools/
│   ├── storage/
│   └── prompts/
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md

## Setup

Create virtual environment:

python3 -m venv .venv

Activate:

source .venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Configure environment variables in `.env`.

## Run

uvicorn app.main:app --reload

## API

POST /ai/employee-assistant

Request:

{
  "session_id": "employee-session-1",
  "message": "Who is employee 101?"
}

Response:

{
  "success": true,
  "status_code": 200,
  "data": {
    "response": "Employee 101 is Arun.",
    "tools_used": [
      "get_employee"
    ]
  }
}

## Conversation History

GET:

/ai/employee-assistant/{session_id}/history

DELETE:

/ai/employee-assistant/{session_id}

## Security

- API keys are stored in environment variables.
- `.env` is ignored by Git.
- AI tool arguments are validated by the backend.
- The AI cannot directly modify backend state.
- Internal exceptions and stack traces are not exposed.
- Tool execution is limited to registered tools.

## Learning Outcomes

This task demonstrates:

- AI tool calling
- Multiple tools
- Tool chaining
- Conditional tool execution
- Conversation context
- Session isolation
- Backend validation
- Business-rule enforcement
- Read vs action operations
- Safe AI-to-backend interaction
- Tool-call limits

No agent framework such as LangChain, LangGraph, or CrewAI is used.
The tool orchestration is implemented manually.
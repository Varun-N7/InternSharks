# AI Tool Calling Assistant

A simple FastAPI backend that uses an OpenRouter-compatible LLM to decide when backend tools should be called and then returns a natural-language response.

## Objective

Build an AI assistant where the LLM can decide when an application action is required.

## Architecture

```text
User Request
     ↓
FastAPI
     ↓
LLM (OpenRouter)
     ↓
Tool Selection
     ↓
Backend Tool Execution
     ↓
Tool Result
     ↓
LLM
     ↓
Final Response
```

## Features

- FastAPI REST API
- OpenRouter AI integration
- OpenAI-compatible tool/function calling
- Calculator tool
- Current date tool
- In-memory task lookup tool
- Pydantic validation for tool arguments
- Centralized tool registry
- Safe handling of invalid tool arguments
- Unknown tool rejection
- Division-by-zero handling
- OpenRouter error handling
- Environment-variable configuration

## Available Tools

### Calculator

Performs add, subtract, multiply, and divide operations. Arithmetic is executed by the backend.

### Get Current Date

Returns the current date from the Python backend.

### Get Task

Retrieves a task from the in-memory dataset using a task ID.

Example data:

```text
1 → Buy groceries → pending
2 → Finish internship work → completed
3 → Call mom → pending
```

## Project Structure

```text
task18/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── assistant.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── assistant_service.py
│   │   └── ai_service.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── assistant.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── calculator.py
│   │   ├── date_tool.py
│   │   ├── task_tool.py
│   │   └── registry.py
│   └── prompts/
│       ├── __init__.py
│       └── assistant_prompt.py
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.12 or compatible Python 3 version
- FastAPI
- Uvicorn
- Requests
- python-dotenv
- Pydantic
- OpenRouter API key

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=your_openrouter_model
```

Do not commit the `.env` file to Git.

## Run the Server

From the `task18` directory:

```bash
uvicorn app.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## API Endpoint

### POST `/ai/assistant`

Example request:

```json
{
  "message": "What is 25 + 15?"
}
```

The LLM can select the calculator tool, the backend executes it, and the result is sent back to the LLM for the final response.

## Example Requests

### Calculator

```json
{
  "message": "What is 25 + 15?"
}
```

Expected result:

```text
40
```

### Current Date

```json
{
  "message": "What is today's date?"
}
```

The date is obtained from the Python backend.

### Get Task

```json
{
  "message": "What is task 1?"
}
```

Expected task:

```text
Buy groceries
Status: pending
```

### Normal Conversation

```json
{
  "message": "Explain FastAPI in one sentence."
}
```

The assistant can respond without using a backend tool.

## Error Handling

The application handles:

- Invalid OpenRouter API key
- Missing OpenRouter configuration
- OpenRouter connection failure
- OpenRouter rate limits
- Invalid AI responses
- Invalid tool arguments
- Unknown tools
- Task not found
- Division by zero
- Invalid request body

Example:

```json
{
  "message": "What is 10 divided by 0?"
}
```

Expected error:

```json
{
  "detail": "Cannot divide by zero"
}
```

## Tool Calling Flow

For:

```text
What is 50 multiplied by 6?
```

the flow is:

```text
User
 ↓
POST /ai/assistant
 ↓
OpenRouter LLM
 ↓
calculator tool selected
 ↓
Tool arguments validated with Pydantic
 ↓
Python calculator executes
 ↓
Tool result = 300
 ↓
Result sent back to LLM
 ↓
Final response
```

## Validation

AI-generated tool arguments are treated as untrusted input.

Pydantic models validate tool arguments before backend execution.

Calculator arguments:

```text
operation
a
b
```

Get-task arguments:

```text
task_id
```

## Testing

The API was tested manually using Postman.

Testing covered:

- Calculator tool calling
- Current date tool
- Task lookup
- Normal AI conversation
- Division-by-zero handling
- Task not found
- Invalid task arguments
- Missing message
- Empty message
- Unknown tool handling
- Successful calculator operations
- Successful task lookup

## Security Notes

- API keys are stored in environment variables.
- `.env` is excluded from Git.
- Tool arguments are validated before execution.
- Unknown tools are rejected.
- API responses do not intentionally expose internal stack traces.

## Key Learning

This task demonstrates how an AI application can connect an LLM with real backend functions.

Main concepts:

- AI tool/function calling
- LLM-to-backend interaction
- Tool definitions
- Tool argument validation
- Tool execution
- Tool result handling
- Multi-step AI workflows
- Safe error handling
- AI-powered backend development with FastAPI
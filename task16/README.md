# Task 16 — Context-Aware AI Chat Assistant

## Project Overview

A simple AI Chat Assistant built with FastAPI and OpenRouter. It maintains separate in-memory conversation history for each `session_id`, allowing previous messages to be supplied as context for future AI responses.

## Features

- Context-aware AI chat
- Session-based conversation history
- Separate memory for different sessions
- In-memory storage
- Last 10 messages sent to the AI
- Get conversation history
- Clear conversation history
- OpenRouter integration
- Pydantic validation
- Error handling

## Application Flow

```text
User
 ↓
FastAPI
 ↓
Load session history
 ↓
Add new user message
 ↓
Send history + new message to OpenRouter
 ↓
Receive AI response
 ↓
Store assistant response
 ↓
Return response
```

Each LLM request is independent. The backend creates the appearance of memory by storing previous messages and sending them back to the LLM as context.

## Project Structure

```text
task16/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── chat.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chat_service.py
│   │   └── ai_service.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── chat.py
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── chat_prompt.py
│   └── storage/
│       ├── __init__.py
│       └── chat_memory.py
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Technologies

- Python
- FastAPI
- Pydantic
- Uvicorn
- OpenRouter
- Requests
- python-dotenv

## Setup

```bash
cd ~/Desktop/doubletap/task16
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment Variables

Create `.env`:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openrouter/free
```

Never commit `.env` or your API key.

## Run the API

```bash
python -m uvicorn app.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### POST `/ai/chat`

Send a message to the AI.

```json
{
    "session_id": "user123",
    "message": "My name is Arun and I am learning FastAPI."
}
```

Example response:

```json
{
    "success": true,
    "status_code": 200,
    "data": {
        "session_id": "user123",
        "response": "Nice to meet you, Arun."
    }
}
```

### GET `/ai/chat/{session_id}/history`

Returns the stored conversation history.

```text
GET /ai/chat/user123/history
```

### DELETE `/ai/chat/{session_id}`

Clears the conversation history for the session.

```text
DELETE /ai/chat/user123
```

## Conversation Context

Conversation history is stored separately for each session:

```text
Session A
├── User message
├── Assistant response
├── User message
└── Assistant response

Session B
├── User message
└── Assistant response
```

Messages from Session A are never sent to Session B.

The AI receives the correct message roles:

```text
system
user
assistant
user
assistant
```

The conversation is not combined into one large user prompt.

## History Limit

Only the last 10 messages are sent to the AI. This prevents history from growing forever.

Unlimited history can cause higher token usage, higher API cost, slower requests, and context-window limitations.

## Testing

The API can be tested using Postman.

Test cases include:

- Start a new conversation
- Multiple messages in the same session
- Context-dependent questions
- Separate sessions
- Get conversation history
- Clear conversation
- Access history after clearing
- Empty message
- Missing message
- Empty session ID
- Non-existing session
- Invalid API key
- AI service failure

## Important Context Test

```text
Message 1:
My project name is Nova.

Message 2:
The backend uses FastAPI.

Message 3:
What is my project name and what backend framework does it use?
```

The AI should answer using the previous messages:

```text
Project name: Nova
Backend framework: FastAPI
```

A different session should not know this information.

## Error Handling

The API handles:

- Invalid input → 422
- Session not found → 404
- Invalid API key → 401
- Rate limit → 429
- AI service failure → 502
- Empty AI response
- Invalid AI response

Raw OpenRouter errors, stack traces, API keys, and internal details are not exposed.

## Security

Do not commit:

```text
.env
.venv/
__pycache__/
*.pyc
```

## Important Learning

OpenRouter does not automatically remember previous API requests. Every LLM request is independent.

The backend creates conversation memory by storing the conversation and supplying the relevant history with the next request.

For this task, conversation history is stored only in memory. No MongoDB or other database is used.

## Learning Goals

- Conversational context
- Conversation history
- Stateless API requests
- Session-based memory
- `system`, `user`, and `assistant` roles
- Context-window limitations
- Token usage
- Separating storage from AI logic
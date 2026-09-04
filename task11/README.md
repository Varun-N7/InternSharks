# Task Management API

A RESTful Task Management API built with FastAPI, MongoDB, JWT authentication, and role-based access control.

## Features

- User registration and login
- JWT access and refresh token authentication
- Refresh token session management
- User profile management
- Role-based access control (`user` / `admin`)
- Task creation, retrieval, updating, status updates, and deletion
- Task filtering by status and priority
- Task search
- Pagination
- Admin user listing
- Admin task listing
- Admin task filtering and pagination
- Task assignment support
- Request validation
- Centralized exception handling
- Structured JSON error responses
- Application logging
- Request logging middleware
- MongoDB health check
- MongoDB persistence
- Environment-based configuration
- Automated pytest testing

## Tech Stack

- Python 3.12+
- FastAPI
- Uvicorn
- MongoDB
- Motor
- Pydantic
- JWT
- bcrypt
- python-dotenv
- pytest
- httpx
- pytest-asyncio
- Postman

## Installation

### Clone Repository

```bash
git clone <repository-url>
cd task-management-api
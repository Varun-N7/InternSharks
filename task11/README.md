# Task 11 - Task Management API

## 1. Objective

Task 11 extends the Task 10 Task Management API with production hardening, centralized exception handling, application logging, request logging middleware, health monitoring, environment-based configuration, security improvements, and automated testing.

---

## 2. Project Stack

- Python
- FastAPI
- MongoDB
- Motor
- Pydantic
- JWT authentication
- bcrypt
- pytest
- pytest-asyncio
- HTTPX
- Postman

---

## 3. Project Structure

```text
task11/
├── app/
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── dependencies.py
│   │   └── jwt_handler.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── mongodb.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── task.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── tasks.py
│   │   └── admin.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   └── task_service.py
│   ├── config.py
│   ├── exceptions.py
│   ├── logging_config.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_users.py
│   └── test_tasks.py
├── .env
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

---

# 4. Task 11 Requirements

## 4.1 Centralized Exception Handling

Every API error uses:

```json
{
  "success": false,
  "status_code": 404,
  "error": "NOT_FOUND",
  "message": "Task not found"
}
```

Examples:

### 401

```json
{
  "success": false,
  "status_code": 401,
  "error": "UNAUTHORIZED",
  "message": "Authentication required"
}
```

### 403

```json
{
  "success": false,
  "status_code": 403,
  "error": "FORBIDDEN",
  "message": "You do not have permission to perform this action"
}
```

### 422

```json
{
  "success": false,
  "status_code": 422,
  "error": "VALIDATION_ERROR",
  "message": "Invalid request data"
}
```

Handled status codes:

```text
400
401
403
404
409
422
500
503
```

HTTP status code and JSON `status_code` match.

Passwords, hashes, JWTs, credentials, internal database errors, and stack traces are not exposed.

---

# 5. Application Logging

Python logging is used instead of development `print()` statements.

The application logs:

- Startup
- Shutdown
- MongoDB connection success/failure
- Registration
- Login success/failure
- Authentication failures
- Task creation
- Task update
- Task deletion
- Unexpected errors

Sensitive information is never logged:

- Passwords
- Password hashes
- JWT tokens
- Authorization headers
- MongoDB credentials
- JWT secrets

Example:

```text
INFO - POST /tasks - 201 - 42ms
```

---

# 6. Request Logging Middleware

Requests are logged with:

- HTTP method
- Path
- Response status
- Processing time

Request bodies and authentication information are not logged.

---

# 7. Health Check

Endpoint:

```text
GET /health
```

Healthy response:

```json
{
  "success": true,
  "status_code": 200,
  "status": "healthy",
  "database": "connected"
}
```

Unhealthy response:

```json
{
  "success": false,
  "status_code": 503,
  "status": "unhealthy",
  "database": "disconnected"
}
```

The health endpoint does not expose MongoDB connection details or internal errors.

---

# 8. Environment Configuration

Required environment variables:

```env
MONGO_URI=
DATABASE_NAME=
JWT_SECRET_KEY=
JWT_ALGORITHM=
ACCESS_TOKEN_EXPIRE_MINUTES=
REFRESH_TOKEN_EXPIRE_DAYS=
APP_ENV=
```

Example:

```env
MONGO_URI=mongodb://YOUR_USERNAME:YOUR_PASSWORD@localhost:27017/?authSource=admin
DATABASE_NAME=task_management_db
JWT_SECRET_KEY=your-32-character-or-longer-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
APP_ENV=development
```

The `.env` file must never be committed.

---

# 9. Authentication APIs

## Register

```text
POST /auth/register
```

Example:

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "Password123"
}
```

## Login

```text
POST /auth/login
```

Example:

```json
{
  "email": "test@example.com",
  "password": "Password123"
}
```

The returned access token is used as:

```text
Authorization: Bearer ACCESS_TOKEN
```

## Refresh

```text
POST /auth/refresh
```

## Logout

```text
POST /auth/logout
```

---

# 10. User APIs

## Current User

```text
GET /users/me
```

Returns the authenticated user's profile.

## Update Current User

```text
PUT /users/me
```

Updates the authenticated user's profile.

Users cannot change their own role through this endpoint.

---

# 11. Task APIs

## Create Task

```text
POST /tasks
```

Example:

```json
{
  "title": "Complete Task 11",
  "description": "Production hardening and testing",
  "status": "todo",
  "priority": "high",
  "due_date": null
}
```

## Get Tasks

```text
GET /tasks
```

## Get Single Task

```text
GET /tasks/{task_id}
```

## Update Task

```text
PUT /tasks/{task_id}
```

## Update Task Status

```text
PATCH /tasks/{task_id}/status
```

Allowed statuses:

```text
todo
in_progress
completed
```

Example:

```json
{
  "status": "completed"
}
```

## Delete Task

```text
DELETE /tasks/{task_id}
```

---

# 12. Task Filtering

Filter by status:

```text
GET /tasks?status=completed
```

Filter by priority:

```text
GET /tasks?priority=high
```

---

# 13. Task Search

```text
GET /tasks?search=Postman
```

---

# 14. Task Pagination

```text
GET /tasks?page=1&limit=5
```

---

# 15. Admin APIs

Admin endpoints require the `admin` role.

## Get Users

```text
GET /admin/users
```

## Get All Tasks

```text
GET /admin/tasks
```

## Assign Task

```text
PATCH /admin/tasks/{task_id}/assign
```

## Admin Task Filtering and Pagination

```text
GET /admin/tasks?page=1&limit=5&status=completed
```

---

# 16. Roles

## User

Normal users can:

- Register
- Login
- View their profile
- Update their profile
- Create tasks
- View permitted tasks
- Update permitted tasks
- Update task status
- Delete permitted tasks

Normal users cannot:

- Access admin endpoints
- Access another user's private tasks
- Change their own role

## Admin

Administrators can:

- Access admin endpoints
- View users
- View all tasks
- Manage tasks
- Assign tasks

---

# 17. Database

MongoDB collections:

```text
users
tasks
refresh_tokens
```

Indexes are created for:

- Email
- Username
- Task creator
- Assigned user
- Status
- Priority
- Refresh token session
- Refresh token expiry

---

# 18. Security

Security features include:

- JWT authentication
- Refresh-token sessions
- bcrypt password hashing
- Role-based authorization
- Ownership checks
- Request validation
- Environment-based secrets
- Protected admin endpoints
- No passwords or hashes in API responses
- No tokens or secrets in logs

---

# 19. Automated Testing

Run:

```bash
pytest
```

Final test result:

```text
38 passed
```

Tests cover:

- User registration
- Duplicate registration
- Invalid registration data
- Invalid email
- Login
- Invalid credentials
- Unknown email
- Invalid login request
- Refresh token
- Logout
- Current user
- Unauthorized access
- User profile update
- Task creation
- Task retrieval
- Task update
- Task status update
- Invalid task status
- Task deletion
- Task not found
- Invalid task ID
- Cross-user restrictions
- Pagination
- Status filtering
- Priority filtering
- Search
- Request validation

---

# 20. Postman Testing

A Postman collection was exported and saved in the Task 11 working directory.

The manual regression covered the main:

- Health check
- Registration
- Duplicate registration
- Invalid registration
- Login
- Invalid credentials
- Current user
- User update
- Task creation
- Task retrieval
- Task update
- Task status update
- Invalid status
- Task deletion
- Deleted task verification
- Pagination
- Filtering
- Search
- Cross-user access
- Authorization scenarios

Some admin scenarios were skipped during the final manual regression because admin login was not completed.

---

# 21. Development

Create virtual environment:

```bash
python3 -m venv venv
```

Activate:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run application:

```bash
uvicorn app.main:app --reload
```

Run tests:

```bash
pytest
```

Compile check:

```bash
python -m compileall app tests
```

---

# 22. Git and .gitignore

Ignored files:

```text
.env
venv/
__pycache__/
*.pyc
.pytest_cache/
```

The `.env` file must not be committed.

---

# 23. API Status Codes

| Code | Meaning |
|---|---|
| 200 | Successful request |
| 201 | Resource created |
| 204 | Resource deleted |
| 400 | Bad request |
| 401 | Authentication required |
| 403 | Permission denied |
| 404 | Resource not found |
| 409 | Conflict |
| 422 | Validation error |
| 500 | Internal server error |
| 503 | Service unavailable |

---

# 24. Task 11 Verification

Automated tests:

```text
38 passed
```

Health check:

```text
Healthy
```

MongoDB:

```text
Connected
```

Postman collection:

```text
Exported
```

Application compilation:

```text
Passed
```

Development `print()` statements:

```text
Removed
```

Sensitive logging checks:

```text
Passed
```

---

# 25. Known Limitations

The following Task 10 administrative scenarios were not fully completed or verified during the Task 11 Postman regression:

- Admin user role update endpoint
- Admin user status update endpoint
- Some admin task assignment scenarios
- Some refresh-token endpoint scenarios
- Admin login-dependent Postman checks were skipped

These remain known limitations and should not be assumed to be fully verified.

---

# 26. Final Result

Task 11 successfully adds production hardening to the Task Management API.

Completed areas include:

- Centralized exception handling
- Structured error responses
- Application logging
- Request logging middleware
- MongoDB health monitoring
- Environment-based configuration
- Secure secret handling
- Input validation
- Authentication
- Authorization
- Database indexes
- Automated testing
- Postman regression testing
- Git ignore configuration
- Updated documentation

Final automated test result:

```text
38 passed
```

The API is ready for final submission subject to the documented admin-related limitations.
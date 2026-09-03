# Task Management API

A RESTful Task Management API built with FastAPI, MongoDB, JWT authentication, and role-based access control.

## Features

- User registration and login
- JWT access and refresh token authentication
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
- Error handling
- MongoDB persistence

## Tech Stack

- Python 3.12+
- FastAPI
- Uvicorn
- MongoDB
- Motor
- Pydantic
- JWT
- Passlib
- bcrypt
- python-dotenv
- Postman

## Installation

### Clone Repository

    git clone <repository-url>
    cd task-management-api

### Create Virtual Environment

    python3 -m venv venv

### Activate Virtual Environment

Linux/macOS:

    source venv/bin/activate

Windows:

    venv\Scripts\activate

### Install Dependencies

    pip install -r requirements.txt

### Configure Environment Variables

Create a `.env` file in the project root.

    MONGODB_URL=mongodb://username:password@host:port/task_management?authSource=admin
    DATABASE_NAME=task_management
    JWT_SECRET_KEY=your-secret-key
    JWT_ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    REFRESH_TOKEN_EXPIRE_DAYS=7

Do not commit `.env` to Git.

### Run Application

    uvicorn app.main:app --reload

Application: `http://127.0.0.1:8000`

Swagger UI: `http://127.0.0.1:8000/docs`

ReDoc: `http://127.0.0.1:8000/redoc`

## API Endpoints

### Authentication

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Logout and revoke refresh token

### Users

- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update current user profile

### Tasks

- `POST /tasks` - Create task
- `GET /tasks` - List permitted tasks
- `GET /tasks/{task_id}` - Get task by ID
- `PUT /tasks/{task_id}` - Update task
- `PATCH /tasks/{task_id}/status` - Update task status
- `DELETE /tasks/{task_id}` - Delete task

Task filters include status, priority, search, and pagination.

Examples:

    GET /tasks?status=in_progress
    GET /tasks?priority=high
    GET /tasks?search=assignment
    GET /tasks?page=1&limit=10

### Admin

- `GET /admin/users` - List users
- `GET /admin/tasks` - List all tasks
- `PATCH /admin/tasks/{task_id}/assign` - Assign task to user

Admin task filtering and pagination are supported.

Examples:

    GET /admin/tasks?status=completed
    GET /admin/tasks?priority=high
    GET /admin/tasks?page=1&limit=10

## Authentication

The API uses JWT-based authentication.

Login returns an access token and refresh token.

Use the access token for protected endpoints:

    Authorization: Bearer <access_token>

Example login request:

    {
      "email": "testuser@example.com",
      "password": "Testuser@123"
    }

Example registration request:

    {
      "username": "testuser",
      "email": "testuser@example.com",
      "password": "Testuser@123",
      "full_name": "Test User"
    }

## Task Model

Tasks contain:

- `id`
- `title`
- `description`
- `status`
- `priority`
- `created_by`
- `assigned_to`
- `due_date`
- `created_at`
- `updated_at`

Supported statuses:

- `todo`
- `in_progress`
- `completed`

Supported priorities:

- `low`
- `medium`
- `high`

## Roles

### User

Normal users can:

- Register and login
- View and update their profile
- Create tasks
- View permitted tasks
- Update permitted tasks
- Update task status
- Delete permitted tasks

Normal users cannot:

- Access admin endpoints
- View all users
- View all tasks
- Change their own role
- Access another user's private tasks

### Admin

Admins can:

- Use normal user functionality
- View all users
- View all tasks
- Filter and paginate admin task lists
- Assign tasks

## Database

MongoDB is used for persistence.

Collections:

- `users`
- `tasks`
- `refresh_sessions`

## Validation

The API validates:

- Duplicate registrations
- Login credentials
- JWT tokens
- Authentication
- Task IDs
- Non-existent tasks
- Task statuses
- Pagination parameters
- Request bodies
- Admin authorization

## HTTP Status Codes

- `200 OK`
- `201 Created`
- `204 No Content`
- `400 Bad Request`
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`
- `422 Unprocessable Entity`
- `500 Internal Server Error`

## Security

- Passwords are hashed before storage.
- JWT authentication protects private endpoints.
- Access and refresh tokens have separate purposes.
- Token expiration is configurable.
- Admin endpoints require admin privileges.
- Normal users cannot change their own role.
- Task ownership is based on the authenticated user.
- Invalid JWT tokens are rejected.
- Refresh tokens cannot be used as access tokens.
- Access tokens cannot be used as refresh tokens.
- Logged-out refresh tokens are rejected.
- Sensitive configuration is stored in environment variables.
- `.env` must not be committed to Git.

## Postman Testing

The API was tested using Postman.

### Tested Functionality

- User registration
- Duplicate registration validation
- Valid login
- Invalid login validation
- Get current profile
- Update current profile
- Create task
- Get tasks
- Get task by ID
- Update task
- Update task status
- Filter tasks by status
- Filter tasks by priority
- Search tasks
- Task pagination
- Delete task
- Verify deleted task
- Invalid task ID validation
- Non-existent task validation
- Invalid task status validation
- Admin user listing
- Admin task listing
- Admin task filtering
- Admin task pagination
- Admin users pagination
- Invalid admin pagination
- Normal user blocked from admin users
- Normal user blocked from admin tasks
- Normal user cannot change own role
- Logout
- Revoked refresh token validation
- Access token cannot be used as refresh token
- Refresh token cannot access protected endpoint
- Protected endpoint without authentication
- Invalid access token

## Known Limitations

The following areas were skipped because they returned errors or require further implementation/debugging:

- Admin user role update route
- Admin user status update route
- Some admin task assignment scenarios
- Refresh token endpoint behavior in certain cases

## Git

Recommended `.gitignore`:

    .env
    venv/
    __pycache__/
    *.pyc

Never commit:

- MongoDB credentials
- JWT secret keys
- Passwords
- Access tokens
- Refresh tokens
- `.env`

## Development

Start the development server:

    uvicorn app.main:app --reload

Open Swagger:

    http://127.0.0.1:8000/docs

## Conclusion

The Task Management API provides a FastAPI-based backend for managing users and tasks with MongoDB persistence, JWT authentication, role-based authorization, task filtering, searching, pagination, validation, and administrative functionality.

The core authentication, user management, task management, authorization, validation, and admin listing functionality has been tested using Postman.

# Task 8 - Role-Based Access Control & User Management API

A FastAPI-based User Management API using MongoDB, JWT authentication, password hashing, and Role-Based Access Control (RBAC).

## Tech Stack

- Python
- FastAPI
- MongoDB
- Motor
- Pydantic
- Passlib
- bcrypt
- python-jose
- python-dotenv
- Uvicorn

## Features

- User registration and login
- JWT-based authentication
- Bearer token authentication
- JWT expiration
- User profiles
- Profile updates
- Role-Based Access Control
- User and Admin roles
- Admin user management
- User filtering
- Account activation and deactivation
- User deletion
- Protected routes
- Password hashing with bcrypt

## User Roles

The application supports two roles:

- user
- admin

New users are automatically created with:

    role = user
    is_active = true

Users cannot assign or modify their own role or account status.

## Project Structure

    task8/
    ├── app/
    │   ├── __init__.py
    │   ├── auth/
    │   │   ├── __init__.py
    │   │   ├── jwt_handler.py
    │   │   └── dependencies.py
    │   ├── database/
    │   │   ├── __init__.py
    │   │   └── mongodb.py
    │   ├── models/
    │   │   ├── __init__.py
    │   │   ├── auth.py
    │   │   └── user.py
    │   ├── routes/
    │   │   ├── __init__.py
    │   │   ├── auth.py
    │   │   ├── user.py
    │   │   └── admin.py
    │   ├── services/
    │   │   ├── __init__.py
    │   │   ├── auth_service.py
    │   │   └── user_service.py
    │   ├── config.py
    │   └── main.py
    ├── .env
    ├── .gitignore
    ├── requirements.txt
    └── README.md

## Installation

Create a virtual environment:

    python3 -m venv venv

Activate the virtual environment:

    source venv/bin/activate

Install dependencies:

    pip install -r requirements.txt

## Environment Variables

Create a .env file in the project root with:

    MONGO_URI=mongodb://localhost:27017
    DATABASE_NAME=auth

    JWT_SECRET_KEY=your-secret-key
    JWT_ALGORITHM=HS256
    JWT_EXPIRE_MINUTES=30

Do not commit .env to GitHub.

## Run the Application

Start the FastAPI server:

    uvicorn app.main:app --reload

The API will be available at:

    http://127.0.0.1:8000

Swagger documentation:

    http://127.0.0.1:8000/docs

## Authentication Flow

    Email + Password
           |
           v
    Verify Credentials
           |
           v
    Generate JWT
           |
           v
    Return Access Token
           |
           v
    Bearer Token
           |
           v
    Validate JWT
           |
           v
    Identify User
           |
           v
    Check Permissions
           |
           v
    Allow or Deny Request

JWT tokens contain authentication information and an expiration time.

Passwords and password hashes are never stored inside the JWT.

## User APIs

### Register User

    POST /register

Example request:

    {
        "username": "testuser",
        "email": "testuser@gmail.com",
        "password": "test1234",
        "full_name": "Test User",
        "phone": "9876543210",
        "department": "AI"
    }

A newly registered user automatically receives:

    role = user
    is_active = true

### Login

    POST /login

Example request:

    {
        "email": "testuser@gmail.com",
        "password": "test1234"
    }

A successful login returns a JWT access token.

### Get Current User

    GET /me

Requires a valid Bearer token.

Returns:

- username
- email
- full_name
- phone
- department
- role
- is_active

The password and password hash are never returned.

### Update Current User

    PUT /me

Users can update:

- username
- full_name
- phone
- department

Users cannot update:

- email
- password
- role
- is_active

## Admin APIs

All /admin/* endpoints require:

1. A valid JWT
2. An authenticated user
3. The admin role

### Get All Users

    GET /admin/users

### Filter Users by Role

    GET /admin/users?role=user

### Filter Users by Department

    GET /admin/users?department=AI

### Filter Users by Active Status

    GET /admin/users?is_active=true

### Get Specific User

    GET /admin/users/{user_id}

Returns 404 Not Found if the user does not exist.

### Change User Role

    PATCH /admin/users/{user_id}/role

Example request:

    {
        "role": "admin"
    }

Allowed roles:

    user
    admin

Invalid roles are rejected.

### Change User Status

    PATCH /admin/users/{user_id}/status

Example request:

    {
        "is_active": false
    }

A deactivated user cannot successfully log in.

### Delete User

    DELETE /admin/users/{user_id}

Returns an appropriate error if the user does not exist.

## Role-Based Access Control

RBAC controls access based on the user's role.

    JWT
     |
     v
    Identify Authenticated User
     |
     v
    Find User in MongoDB
     |
     v
    Check User Role
     |
     v
    Admin?
     /   \
    Yes   No
     |     |
     v     v
    Allow  403 Forbidden

The backend does not trust role information sent by the client.

Users cannot promote themselves to admin.

Users cannot activate or deactivate their own accounts.

## Account Deactivation

When an admin deactivates a user:

    is_active = false

The user cannot successfully log in.

An admin can reactivate the account by setting:

    is_active = true

## Security

- Passwords are hashed using bcrypt.
- Password hashes are never returned in API responses.
- JWT secret keys are stored in environment variables.
- JWT tokens have an expiration time.
- Protected endpoints require authentication.
- Admin endpoints require the admin role.
- Users cannot change their own role.
- Users cannot change their own is_active status.
- Users cannot change their email through /me.
- Deactivated users cannot log in.
- JWT access tokens are not stored in source code.
- MongoDB credentials are not stored in source code.

## Postman Testing

The following scenarios were tested:

1. Register normal user
2. Login as normal user
3. View own profile
4. Update own profile
5. User attempts to modify role
6. User attempts to modify account status
7. User attempts to access admin API
8. Admin views all users
9. Admin filters users by role
10. Admin filters users by department
11. Admin filters users by active status
12. Admin views specific user
13. Admin promotes user to admin
14. Admin deactivates user
15. Deactivated user attempts to login
16. Admin reactivates user
17. Admin deletes user
18. Non-existing user
19. Request without JWT
20. Invalid JWT
21. Expired JWT
22. Valid JWT with insufficient permission

For protected requests in Postman:

    Authorization
          |
          v
    Bearer Token
          |
          v
    <access_token>

## HTTP Status Codes

Common responses include:

    200 OK
    201 Created
    400 Bad Request
    401 Unauthorized
    403 Forbidden
    404 Not Found
    409 Conflict
    422 Unprocessable Entity

## Git and Security

The following files and directories must not be committed:

    .env
    venv/
    .venv/
    __pycache__/
    *.pyc

Never commit:

- MongoDB credentials
- JWT secret keys
- Passwords
- JWT access tokens
- Environment files
- Virtual environments
- Generated cache files

## Learning Outcomes

This project demonstrates:

- Authentication vs Authorization
- JWT authentication
- Bearer authentication
- JWT expiration
- Role-Based Access Control
- User-owned resources
- Admin-controlled resources
- FastAPI dependencies
- MongoDB user management
- Password hashing
- Account activation and deactivation
- Protected API routes
- Permission checking
- Secure handling of user information
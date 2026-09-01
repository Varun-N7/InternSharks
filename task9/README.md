# Task 9 — Refresh Tokens & JWT Token Lifecycle

## Objective

Task 9 extends the existing authentication system to support short-lived access tokens and long-lived refresh tokens.

Users can remain authenticated after an access token expires without entering their email and password again.

## Authentication Flow

Register → Password hashing → MongoDB → Login → Password verification → Access Token + Refresh Token → Protected APIs → Access Token expires → Refresh Token → New Access Token → Logout → Refresh Session Revoked

## Technologies

- Python
- FastAPI
- MongoDB
- Motor
- PyMongo
- JWT
- python-jose
- Passlib
- bcrypt
- Pydantic
- python-dotenv
- Postman

## Project Structure

The project is separated into authentication, database, models, routes, services, configuration, and application startup components.

- app/auth — JWT handling and authentication dependencies
- app/database — MongoDB connection and indexes
- app/models — Pydantic request and response models
- app/routes — Authentication, user, and admin APIs
- app/services — Authentication and user business logic
- app/config.py — Environment configuration
- app/main.py — FastAPI application

## Environment Variables

JWT and MongoDB configuration are stored in environment variables.

The application uses the following configuration:

- MONGO_URI
- DATABASE_NAME
- JWT_SECRET_KEY
- JWT_ALGORITHM
- ACCESS_TOKEN_EXPIRE_MINUTES
- REFRESH_TOKEN_EXPIRE_DAYS

The actual `.env` file must never be committed to GitHub.

The `.env.example` file contains only example configuration values.

## JWT Secret

A strong random secret should be generated and stored in the environment configuration.

The JWT secret must not be hardcoded in the application source code.

## Access Token

The access token is short-lived and is used to access protected APIs.

The access token contains only the information required to identify and authenticate the user.

Important claims include:

- sub — user identifier
- type — identifies the token as an access token
- exp — token expiration time

The access token does not contain:

- Password
- Password hash
- Sensitive profile information

## Refresh Token

The refresh token has a longer lifetime than the access token.

It is used only to obtain a new access token.

Important claims include:

- sub — user identifier
- type — identifies the token as a refresh token
- session_id — identifies the refresh session
- exp — token expiration time

Refresh tokens cannot be used to access normal protected APIs.

Access tokens cannot be used as refresh tokens.

## Access Token vs Refresh Token

Access Token:

- Short-lived
- Used for protected APIs
- Sent with API requests
- Cannot be used at the refresh endpoint

Refresh Token:

- Long-lived
- Used to obtain a new access token
- Associated with a MongoDB refresh session
- Can be revoked
- Cannot be used as an access token

## Password Security

Passwords are never stored as plain text.

During registration, the password is securely hashed before being stored in MongoDB.

During login, the submitted password is verified against the stored password hash.

Password verification happens before tokens are generated.

Passwords and password hashes are never included in JWT tokens or normal API responses.

# Authentication APIs

## Register

Endpoint:

POST /auth/register

Creates a new user account.

The password is hashed before being stored.

Successful registration returns the created user's safe profile information.

## Login

Endpoint:

POST /auth/login

The user provides an email and password.

The system:

1. Finds the user.
2. Verifies the password.
3. Checks that the account is active.
4. Creates an access token.
5. Creates a refresh session.
6. Creates a refresh token.
7. Stores only the secure refresh-token representation in MongoDB.
8. Returns the access token and refresh token.

Successful login returns:

- access_token
- refresh_token
- token_type

## Refresh

Endpoint:

POST /auth/refresh

The refresh endpoint accepts a refresh token and generates a new access token.

The system verifies:

- JWT signature
- Token expiration
- Token type
- Session ID
- Refresh session existence
- Refresh session revocation status
- Associated user existence
- User account active status

An access token must not be accepted as a refresh token.

A revoked refresh token must not be accepted.

An expired refresh token must not be accepted.

A refresh token belonging to a deleted user must not be accepted.

A refresh token belonging to a deactivated user must not be accepted.

## Logout

Endpoint:

POST /auth/logout

Logout invalidates the refresh-token session associated with the current refresh token.

The refresh session is marked as revoked in MongoDB.

After logout, the same refresh token cannot be used to generate another access token.

This demonstrates why simply deleting a token on the client is not enough.

The server maintains the refresh-session state and can revoke it.

# Protected User APIs

## Get Current User

Endpoint:

GET /me

Requires a valid access token.

The access token is supplied using Bearer authentication.

A refresh token must not be accepted.

## Update Current User

Endpoint:

PUT /me

Requires a valid access token.

The user can update permitted profile information.

Passwords and password hashes are not returned.

# Admin APIs

Admin APIs require:

- A valid access token
- An authenticated user
- Admin role

## List Users

Endpoint:

GET /admin/users

Supports user filtering such as:

- Role
- Department
- Active status

## Get Specific User

Endpoint:

GET /admin/users/{user_id}

Returns safe information for a specific user.

Sensitive password information is not returned.

## Change User Role

Endpoint:

PATCH /admin/users/{user_id}/role

Allows an administrator to change another user's role.

## Change User Status

Endpoint:

PATCH /admin/users/{user_id}/status

Allows an administrator to activate or deactivate another user.

When a user is deactivated, their refresh sessions are revoked.

## Delete User

Endpoint:

DELETE /admin/users/{user_id}

Deletes a user.

The user's refresh sessions are revoked before deletion.

# MongoDB Refresh Sessions

Refresh tokens are not stored as plain tokens in MongoDB.

Instead, the refresh token is converted into a secure hash before being stored.

MongoDB stores information associated with the refresh session, including:

- Session ID
- User ID
- Refresh-token hash
- Expiration time
- Revocation status

This means that a usable plain refresh token is not directly stored in the database.

## Refresh Session Lifecycle

Login:

Create a refresh session and associate it with the user.

Refresh:

Validate the refresh token and its MongoDB session.

Logout:

Mark the refresh session as revoked.

After logout:

The revoked refresh token is rejected.

## Refresh Session Expiration

Refresh sessions have an expiration time.

MongoDB can use a TTL index on the expiration field so expired refresh-session records can be automatically removed.

# Token Expiration

Access tokens and refresh tokens have separate expiration settings.

Access tokens should have a short lifetime.

Refresh tokens should have a longer lifetime.

Expiration values are configured through environment variables and are not hardcoded in the application.

Example configuration:

- Access Token — short lifetime
- Refresh Token — longer lifetime

# Security Requirements

The system follows these security rules:

- Password verification occurs before token generation.
- Passwords are hashed.
- Passwords are never stored as plain text.
- Passwords are never included in JWT tokens.
- Password hashes are never returned in API responses.
- Access and refresh tokens have separate expiration values.
- Access tokens are short-lived.
- Refresh tokens are longer-lived.
- Access and refresh tokens have different purposes.
- JWT expiration is validated.
- Invalid JWTs are rejected.
- Access tokens cannot be used as refresh tokens.
- Refresh tokens cannot be used for protected APIs.
- Revoked refresh tokens are rejected.
- Expired refresh tokens are rejected.
- Inactive users cannot refresh authentication.
- Deleted users cannot refresh authentication.
- Plain refresh tokens are not stored in MongoDB.
- JWT secrets are stored in environment variables.
- Complete JWT tokens must never be logged or printed.
- `.env` must not be committed to Git.

# HTTP Status Codes

200 OK

Used for successful requests.

201 Created

Used when a new resource is successfully created.

400 Bad Request

Used for invalid requests or invalid operations.

401 Unauthorized

Used when authentication is missing, invalid, expired, or revoked.

403 Forbidden

Used when the authenticated user does not have permission.

404 Not Found

Used when the requested user or resource does not exist.

409 Conflict

Used for duplicate username or email conflicts.

422 Unprocessable Entity

Used when request validation fails.

# Running the Application

The project uses a Python virtual environment.

Install the required dependencies from requirements.txt.

Start the FastAPI application using Uvicorn.

The API is available locally on port 8000.

FastAPI Swagger documentation is available through the `/docs` endpoint.

# Postman Testing

The authentication system should be tested using Postman.

Important test scenarios include:

1. Successful registration
2. Successful login
3. Login with invalid password
4. Login with invalid email
5. Access protected API using a valid access token
6. Access protected API without a token
7. Access protected API using an invalid access token
8. Access protected API using an expired access token
9. Refresh using a valid refresh token
10. Refresh using an access token
11. Refresh using an invalid refresh token
12. Refresh using an expired refresh token
13. Use refresh token on `/me`
14. Successful logout
15. Attempt refresh after logout
16. Refresh for a deleted user
17. Refresh for a deactivated user
18. Admin list users
19. Filter users by role
20. Filter users by department
21. Filter users by active status
22. Get a specific user
23. Change user role
24. Deactivate/reactivate a user
25. Delete a user
26. Verify normal user cannot access admin endpoints

# Important JWT Lifecycle Tests

## Valid Access Token

A valid access token should successfully access protected endpoints.

Expected result:

200 OK

## Access Token Used as Refresh Token

An access token must not be accepted by the refresh endpoint.

Expected result:

401 Unauthorized

## Refresh Token Used as Access Token

A refresh token must not be accepted by protected endpoints such as `/me`.

Expected result:

401 Unauthorized

## Expired Access Token

An expired access token must be rejected.

Expected result:

401 Unauthorized

## Expired Refresh Token

An expired refresh token must be rejected.

Expected result:

401 Unauthorized

## Revoked Refresh Token

After logout, the refresh token must be rejected.

Expected result:

401 Unauthorized

# Admin Authorization

A normal authenticated user may access normal protected APIs but must not access admin-only APIs.

Example behavior:

Normal user:

Authenticated successfully.

Admin endpoint:

403 Forbidden.

This demonstrates the difference between authentication and authorization.

Authentication confirms who the user is.

Authorization determines what the user is allowed to do.

# Git Security

The following must never be committed:

- `.env`
- `.venv`
- `venv`
- `__pycache__`
- Python cache files
- MongoDB passwords
- JWT secret keys
- Access tokens
- Refresh tokens
- User passwords
- Other credentials

The following can be committed:

- `.env.example`
- `.gitignore`
- `README.md`
- `requirements.txt`
- `app/`
- Postman collection

Before pushing to GitHub, always check Git status and confirm that `.env` and secrets are not included.

# Deliverables

Task 9 deliverables include:

- Updated authentication source code
- JWT access-token implementation
- JWT refresh-token implementation
- Refresh-session management
- Refresh-token revocation
- Logout functionality
- MongoDB refresh-session storage
- Updated requirements.txt
- Updated README.md
- `.env.example`
- `.gitignore`
- Updated Postman collection
- Meaningful Git commits
- GitHub repository update
- Screenshots of important success and failure scenarios

# Learning Outcomes

After completing Task 9, the following concepts should be understood:

- Access Token vs Refresh Token
- Short-lived access tokens
- Long-lived refresh tokens
- JWT expiration
- JWT claims
- Token revocation
- Login sessions
- Logout in a JWT-based system
- Why deleting a JWT on the client is not always sufficient
- Why refresh tokens require stronger protection
- Why access and refresh tokens must not be interchangeable
- MongoDB refresh-session management
- Refresh-token hashing
- User activation and deactivation
- Role-based authorization
- Protected FastAPI endpoints
- FastAPI authentication dependencies
- Environment-based configuration
- Secure secret management

# Complete Authentication Lifecycle

Register

↓

Password is hashed

↓

User stored in MongoDB

↓

Login

↓

Password verification

↓

Access Token + Refresh Token

↓

Access Token used for protected APIs

↓

Access Token expires

↓

Refresh Token used

↓

New Access Token generated

↓

User continues using protected APIs

↓

Logout

↓

Refresh session revoked

↓

Refresh token rejected

↓

Authentication session ends

# Final Checklist

Authentication:

- Registration
- Password hashing
- Password verification
- Login
- Access token
- Refresh token
- Protected `/me`
- Admin authorization

JWT:

- Access token type
- Refresh token type
- User identification
- Expiration
- Session identification
- Separate access-token expiration
- Separate refresh-token expiration
- Environment-based configuration
- Secret not hardcoded

Refresh Lifecycle:

- Refresh endpoint
- Refresh-token validation
- Access token rejected as refresh token
- Refresh token rejected by protected endpoints
- Expired refresh token rejected
- Refresh session stored in MongoDB
- Plain refresh token not stored
- Refresh-token revocation
- Logout
- Refresh after logout rejected
- Inactive-user protection
- Deleted-user protection

Security:

- Passwords not included in JWT
- Password hashes not returned
- Sensitive profile information not included in JWT
- JWT tokens not logged
- `.env` ignored
- Secrets excluded from Git

Deliverables:

- Source code
- requirements.txt
- README.md
- `.env.example`
- `.gitignore`
- Postman collection
- Meaningful Git commit
- GitHub push
- Screenshots for important test cases

# Actual Testing Note

During the current testing session, the following were successfully verified:

- Registration
- Login
- Access token authentication
- `/me`
- Profile update
- Valid refresh
- Access token rejected by refresh endpoint
- Refresh token rejected by `/me`
- Invalid access token
- Invalid refresh token
- Expired access token
- Expired refresh token
- Successful logout
- Refresh after logout rejected
- Admin user listing
- User filtering
- Specific user lookup
- Role update
- User deactivation/reactivation
- User deletion
- Normal user rejected from admin endpoint

The deleted-user refresh and deactivated-user refresh scenarios were skipped during the current manual testing session and should not be claimed as manually verified unless tested separately.
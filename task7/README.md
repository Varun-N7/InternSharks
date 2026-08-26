# JWT Authentication API

A FastAPI authentication API using MongoDB, bcrypt password hashing, and JWT-based authentication.

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

## Features

- User registration
- Email validation
- Password hashing with bcrypt
- User login
- JWT access token generation
- JWT token expiration
- Protected `/me` endpoint
- Bearer token authentication
- Invalid and expired token handling
- MongoDB user storage

## Project Structure

```text
app/
├── auth/
│   └── jwt_handler.py
├── database/
│   └── mongodb.py
├── models/
│   └── user.py
├── routes/
│   └── user_routes.py
├── services/
│   └── user_services.py
├── config.py
└── main.py
# Simple JSON API

A simple REST API built with Python and FastAPI.

The API accepts user information in JSON format, validates the input, and returns JSON responses.

## Tech Stack

- Python
- FastAPI
- Pydantic
- Uvicorn

## Features

- Create a user using a POST request
- Validate required fields
- Validate name length
- Validate email format
- Validate age
- Return appropriate HTTP status codes
- Handle user-not-found errors using HTTP exceptions
- Automatic API documentation with Swagger UI

## Project Structure

```text
task1/
├── main.py
├── requirements.txt
├── README.md
└── Simple_JSON_API.postman_collection.json
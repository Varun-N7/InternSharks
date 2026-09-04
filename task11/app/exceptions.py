from fastapi import Request
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "status_code": 422,
            "error": "VALIDATION_ERROR",
            "message": "Invalid request data"
        }
    )


async def http_exception_handler(
    request: Request,
    exc: HTTPException
):

    error = "HTTP_ERROR"

    if exc.status_code == 400:
        error = "BAD_REQUEST"

    elif exc.status_code == 401:
        error = "UNAUTHORIZED"

    elif exc.status_code == 403:
        error = "FORBIDDEN"

    elif exc.status_code == 404:
        error = "NOT_FOUND"

    elif exc.status_code == 409:
        error = "CONFLICT"

    elif exc.status_code == 503:
        error = "SERVICE_UNAVAILABLE"

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "status_code": exc.status_code,
            "error": error,
            "message": str(exc.detail)
        }
    )


async def general_exception_handler(
    request: Request,
    exc: Exception
):

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "status_code": 500,
            "error": "INTERNAL_SERVER_ERROR",
            "message": "Internal server error"
        }
    )
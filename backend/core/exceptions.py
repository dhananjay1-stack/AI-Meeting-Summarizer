"""
Custom exception classes and global error handlers.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, status_code: int = 400, details: dict | None = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(AppException):
    """Resource not found."""

    def __init__(self, resource: str, resource_id: str = ""):
        detail = f"{resource} not found"
        if resource_id:
            detail += f": {resource_id}"
        super().__init__(message=detail, status_code=404)


class DuplicateError(AppException):
    """Duplicate resource."""

    def __init__(self, field: str, value: str = ""):
        detail = f"{field} already exists"
        if value:
            detail += f": {value}"
        super().__init__(message=detail, status_code=409)


class ValidationError(AppException):
    """Validation failed."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message=message, status_code=422, details=details)


class AuthenticationError(AppException):
    """Authentication failed."""

    def __init__(self, message: str = "Authentication failed."):
        super().__init__(message=message, status_code=401)


class AuthorizationError(AppException):
    """Authorization failed."""

    def __init__(self, message: str = "Insufficient permissions."):
        super().__init__(message=message, status_code=403)


class FileUploadError(AppException):
    """File upload validation failed."""

    def __init__(self, message: str):
        super().__init__(message=message, status_code=400)


class AIProcessingError(AppException):
    """AI pipeline error."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message=message, status_code=500, details=details)


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers with the FastAPI app."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.detail,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        # Log the full traceback in production
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "An internal server error occurred.",
            },
        )

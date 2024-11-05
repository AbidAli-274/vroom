from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


class CustomAPIException(Exception):
    """Custom API Exception with detailed error information."""

    def __init__(self, status_code, detail=None, code=None):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail
        self.code = code


def custom_exception_handler(exc, context):
    """Handles custom exceptions globally, formatting them as JSON for API responses."""
    # Use DRF's default handler to get the initial response
    response = drf_exception_handler(exc, context)

    # Check if an exception is our custom exception and handle accordingly
    if isinstance(exc, CustomAPIException):
        data = {
            "error": {
                "status": exc.status_code,
                "message": exc.detail or "An error occurred",
            }
        }
        if exc.code:
            data["error"]["details"] = exc.code  # Include detailed errors if provided
        return Response(data, status=exc.status_code)

    return response

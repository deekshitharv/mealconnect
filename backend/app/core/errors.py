from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging_config import get_logger

logger = get_logger("errors")

ERROR_TYPES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    409: "conflict",
    422: "validation_error",
    500: "internal_server_error",
}


def error_response(status_code: int, message: str, details=None, headers=None) -> JSONResponse:
    """Build the one standard error format used everywhere in the API."""
    body = {
        "error": {
            "status": status_code,
            "type": ERROR_TYPES.get(status_code, "error"),
            "message": message,
        }
    }
    if details is not None:
        body["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=body, headers=headers)


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handles errors we raise on purpose, e.g. 404 Not Found, 403 Forbidden."""
    return error_response(exc.status_code, str(exc.detail), headers=exc.headers)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handles bad input (wrong type, missing field, etc.) with a readable list."""
    details = []
    for err in exc.errors():
        field = ".".join(str(p) for p in err["loc"] if p not in ("body", "query", "path"))
        details.append({"field": field, "message": err["msg"]})
    return error_response(422, "Validation failed", details=details)


async def unhandled_exception_handler(request: Request, exc: Exception):
    """Handles unexpected crashes. Log the real error, show the user a safe message."""
    logger.error("Unhandled error on %s %s", request.method, request.url.path, exc_info=exc)
    return error_response(500, "Something went wrong on the server. Please try again later.")


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
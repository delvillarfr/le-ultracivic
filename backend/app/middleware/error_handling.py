import logging
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError


logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for consistent error handling across the API"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException as e:
            return await self._handle_http_exception(request, e)
        except ValidationError as e:
            return await self._handle_validation_error(request, e)
        except SQLAlchemyError as e:
            return await self._handle_database_error(request, e)
        except Exception as e:
            return await self._handle_unexpected_error(request, e)
    
    async def _handle_http_exception(self, request: Request, exc: HTTPException):
        """Handle FastAPI HTTP exceptions"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": self._get_error_message(exc.status_code),
                "detail": exc.detail,
                "path": str(request.url.path),
            }
        )
    
    async def _handle_validation_error(self, request: Request, exc: ValidationError):
        """Handle Pydantic validation errors"""
        logger.warning(f"Validation error on {request.url.path}: {exc}")
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation Error",
                "detail": "Invalid request data",
                "path": str(request.url.path),
                "validation_errors": exc.errors(),
            }
        )
    
    async def _handle_database_error(self, request: Request, exc: SQLAlchemyError):
        """Handle database errors"""
        logger.error(f"Database error on {request.url.path}: {exc}")
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Database Error",
                "detail": "A database error occurred. Please try again later.",
                "path": str(request.url.path),
            }
        )
    
    async def _handle_unexpected_error(self, request: Request, exc: Exception):
        """Handle unexpected errors"""
        logger.error(f"Unexpected error on {request.url.path}: {exc}", exc_info=True)
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "detail": "An unexpected error occurred. Please try again later.",
                "path": str(request.url.path),
            }
        )
    
    def _get_error_message(self, status_code: int) -> str:
        """Get user-friendly error message for status code"""
        error_messages = {
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            413: "Request Too Large",
            422: "Unprocessable Entity",
            429: "Too Many Requests",
            500: "Internal Server Error",
            502: "Bad Gateway",
            503: "Service Unavailable",
            504: "Gateway Timeout",
        }
        return error_messages.get(status_code, "Unknown Error")


async def http_exception_handler(request: Request, exc: HTTPException):
    """Global HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "path": str(request.url.path),
        }
    )


async def validation_exception_handler(request: Request, exc: ValidationError):
    """Global validation exception handler"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "path": str(request.url.path),
        }
    )
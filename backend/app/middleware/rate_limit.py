from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse

from app.config import settings


def rate_limit_key_func(request: Request):
    """Generate rate limit key based on client IP address"""
    return get_remote_address(request)


limiter = Limiter(
    key_func=rate_limit_key_func,
    default_limits=[f"{settings.rate_limit_requests}/minute"]
)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit exceeded handler"""
    response = JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "detail": f"Too many requests. Limit: {settings.rate_limit_requests} per minute"
        }
    )
    response.headers["Retry-After"] = str(exc.retry_after)
    return response
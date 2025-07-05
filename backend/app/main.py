from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from slowapi.errors import RateLimitExceeded

from app.api.retirements import router as retirements_router
from app.config import settings
from app.middleware.audit import AuditMiddleware, setup_audit_logging
from app.middleware.cors import setup_cors_middleware
from app.middleware.error_handling import (
    ErrorHandlingMiddleware,
    http_exception_handler,
    validation_exception_handler,
)
from app.middleware.rate_limit import limiter, rate_limit_exceeded_handler
from app.middleware.validation import ValidationMiddleware

app = FastAPI(
    title="Ultra Civic API",
    description="API for carbon allowance retirement and $PR token distribution",
    version="1.0.0",
    debug=settings.debug,
)

# Setup audit logging
setup_audit_logging()

# Add middleware (order matters - last added is executed first)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(AuditMiddleware)
app.add_middleware(ValidationMiddleware)

# Setup CORS
setup_cors_middleware(app)

# Setup rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Global exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)

# Include routers
app.include_router(retirements_router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Ultra Civic API is running"}

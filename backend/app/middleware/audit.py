import hashlib
import json
import logging
from datetime import datetime

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Configure audit logger
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)

# Create file handler for audit logs
audit_handler = logging.FileHandler("audit.log")
audit_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
audit_handler.setFormatter(formatter)
audit_logger.addHandler(audit_handler)


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware for audit logging of retirement requests"""

    def __init__(self, app):
        super().__init__(app)
        self.tracked_paths = ["/api/retirements"]

    async def dispatch(self, request: Request, call_next):
        # Check if this is a tracked endpoint
        should_audit = any(
            request.url.path.startswith(path) for path in self.tracked_paths
        )

        if should_audit and request.method in ["POST", "PUT"]:
            await self._audit_request(request)

        response = await call_next(request)
        return response

    async def _audit_request(self, request: Request):
        """Audit log the request"""
        try:
            # Get client information
            client_ip = self._get_client_ip(request)
            user_agent = request.headers.get("user-agent", "Unknown")

            # Get request body
            body = await request.body()
            request._body = body  # Re-attach for downstream processing

            # Hash sensitive data
            body_hash = self._hash_data(body) if body else None

            # Create audit entry
            audit_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "client_ip": client_ip,
                "user_agent": user_agent,
                "method": request.method,
                "path": str(request.url.path),
                "query_params": dict(request.query_params),
                "body_hash": body_hash,
                "content_length": len(body) if body else 0,
            }

            # Log the audit entry
            audit_logger.info(json.dumps(audit_entry))

        except Exception as e:
            # Don't let audit failures break the request
            audit_logger.error(f"Audit logging failed: {str(e)}")

    def _get_client_ip(self, request: Request) -> str:
        """Get the real client IP address"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fall back to direct connection
        return request.client.host if request.client else "unknown"

    def _hash_data(self, data: bytes) -> str:
        """Hash sensitive data for audit logging"""
        return hashlib.sha256(data).hexdigest()


def setup_audit_logging():
    """Setup audit logging configuration"""
    # Additional setup can be added here
    # e.g., rotating file handler, remote logging, etc.
    pass

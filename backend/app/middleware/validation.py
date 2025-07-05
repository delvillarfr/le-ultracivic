import re

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware


class ValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for request validation and sanitization"""

    def __init__(self, app):
        super().__init__(app)
        self.wallet_pattern = re.compile(r"^0x[a-fA-F0-9]{40}$")
        self.tx_hash_pattern = re.compile(r"^0x[a-fA-F0-9]{64}$")

    async def dispatch(self, request: Request, call_next):
        # Only validate retirement endpoints
        if request.url.path.startswith("/api/retirements"):
            await self._validate_request(request)

        response = await call_next(request)
        return response

    async def _validate_request(self, request: Request):
        """Validate retirement requests"""
        if request.method not in ["POST", "PUT"]:
            return

        try:
            # Get request body
            body = await request.body()
            if not body:
                return

            # Re-create request with body for downstream processing
            request._body = body

            # Basic content-type validation
            content_type = request.headers.get("content-type", "")
            if "application/json" not in content_type:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Content-Type must be application/json",
                )

            # Validate request size
            if len(body) > 10240:  # 10KB limit
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Request body too large",
                )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request format"
            ) from e

    def validate_wallet_address(self, address: str) -> str:
        """Validate and format wallet address"""
        if not self.wallet_pattern.match(address):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid wallet address format",
            )
        return address.lower()

    def validate_tx_hash(self, tx_hash: str) -> str:
        """Validate and format transaction hash"""
        if not self.tx_hash_pattern.match(tx_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid transaction hash format",
            )
        return tx_hash.lower()


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """Sanitize string input"""
    if not isinstance(value, str):
        raise ValueError("Input must be a string")

    # Remove null bytes and control characters
    sanitized = "".join(char for char in value if ord(char) >= 32 or char in "\t\n\r")

    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized.strip()

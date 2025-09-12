# app/logging/middleware.py
"""Logging middleware for FastAPI"""
import time
import uuid
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .core import get_logger, request_id_var, user_id_var


class LoggingMiddleware(BaseHTTPMiddleware):
    """Enhanced logging middleware with structured logging"""

    def __init__(self, app, logger_name: str = "http"):
        super().__init__(app)
        self.logger = get_logger(logger_name)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())

        # Set context variables
        request_id_var.set(request_id)

        # Try to extract user ID from request (implement based on your auth system)
        user_id = self._extract_user_id(request)
        if user_id:
            user_id_var.set(user_id)

        # Start timing
        start_time = time.time()

        # Extract request info
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("User-Agent", "")[:200]
        content_length = request.headers.get("content-length")

        # Log request start
        self.logger.info(
            f"Request started: {request.method} {request.url.path}",
            context={
                "event_type": "http_request_start",
                "method": request.method,
                "path": str(request.url.path),
                "query_params": (
                    str(request.query_params) if request.query_params else None
                ),
                "client_ip": client_ip,
                "user_agent": user_agent,
                "content_length": content_length,
            },
        )

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log successful response
            self.logger.info(
                f"Request completed: {response.status_code} in {duration_ms:.2f}ms",
                context={
                    "event_type": "http_request_success",
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "response_size": response.headers.get("content-length"),
                },
            )

            # Add headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

            return response

        except Exception as e:
            # Calculate duration for errors
            duration_ms = (time.time() - start_time) * 1000

            # Log error
            self.logger.error(
                f"Request failed: {str(e)}",
                context={
                    "event_type": "http_request_error",
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "duration_ms": duration_ms,
                },
            )

            raise

    def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request - implement based on your auth system"""
        # Example implementation - adjust based on your authentication

        # Method 1: From Authorization header (JWT token)
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # You would decode the JWT token here to get user ID
            # This is just a placeholder - implement based on your JWT library
            try:
                # token = auth_header.split(" ")[1]
                # decoded = jwt.decode(token, secret, algorithms=["HS256"])
                # return decoded.get("user_id")
                pass
            except Exception:
                pass

        # Method 2: From request state if set by auth middleware
        if hasattr(request.state, "user") and request.state.user:
            return str(getattr(request.state.user, "id", None))

        # Method 3: From session/cookie
        if hasattr(request.state, "user_id"):
            return str(request.state.user_id)

        return None

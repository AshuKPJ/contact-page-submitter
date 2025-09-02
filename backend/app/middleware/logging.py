# app/middleware/logging.py

import time
import json
import traceback
from datetime import datetime
from typing import Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class DevelopmentLoggingMiddleware(BaseHTTPMiddleware):
    """Comprehensive logging middleware for development mode"""

    def __init__(self, app, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled
        self.request_count = 0

    async def dispatch(self, request: Request, call_next):
        if not self.enabled:
            return await call_next(request)

        # Start timing
        start_time = time.time()
        self.request_count += 1

        # Extract request details
        request_id = f"REQ-{self.request_count:04d}"
        client_ip = request.client.host if request.client else "unknown"

        # Log request start
        print(f"\n{'='*60}")
        print(f"[{request_id}] REQUEST START")
        print(f"[{request_id}] Time: {datetime.utcnow().isoformat()}")
        print(f"[{request_id}] Method: {request.method}")
        print(f"[{request_id}] URL: {request.url}")
        print(f"[{request_id}] Client IP: {client_ip}")

        try:
            # Process request
            response = await call_next(request)

            # Calculate timing
            duration = (time.time() - start_time) * 1000

            # Log response
            print(f"[{request_id}] RESPONSE SUCCESS")
            print(f"[{request_id}] Status: {response.status_code}")
            print(f"[{request_id}] Duration: {duration:.2f}ms")

            # Add custom headers for debugging
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Processing-Time"] = f"{duration:.2f}ms"

            print(f"{'='*60}\n")
            return response

        except Exception as e:
            # Calculate timing for errors too
            duration = (time.time() - start_time) * 1000

            # Log error
            print(f"[{request_id}] RESPONSE ERROR")
            print(f"[{request_id}] Error: {str(e)}")
            print(f"[{request_id}] Duration: {duration:.2f}ms")
            print(f"[{request_id}] Traceback:")
            print(traceback.format_exc())
            print(f"{'='*60}\n")

            # Return structured error response
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "request_id": request_id,
                    "error_type": type(e).__name__,
                    "timestamp": datetime.utcnow().isoformat(),
                },
                headers={
                    "X-Request-ID": request_id,
                    "X-Processing-Time": f"{duration:.2f}ms",
                },
            )


class APILoggingService:
    """Service for logging API events throughout the application"""

    @staticmethod
    def log_auth_event(
        event_type: str, user_email: str, success: bool, details: str = ""
    ):
        """Log authentication events"""
        status = "SUCCESS" if success else "FAILED"
        print(f"[AUTH {status}] {event_type} for {user_email} - {details}")

    @staticmethod
    def log_campaign_event(
        event_type: str, campaign_id: str, user_id: str, details: str = ""
    ):
        """Log campaign events"""
        print(
            f"[CAMPAIGN] {event_type} - Campaign: {campaign_id[:8]}... User: {str(user_id)[:8]}... - {details}"
        )

    @staticmethod
    def log_submission_event(
        event_type: str, submission_id: str, url: str, status: str = ""
    ):
        """Log submission events"""
        print(
            f"[SUBMISSION] {event_type} - ID: {submission_id[:8]}... URL: {url[:50]}... Status: {status}"
        )

    @staticmethod
    def log_database_event(
        event_type: str, table: str, operation: str, success: bool, details: str = ""
    ):
        """Log database operations"""
        status = "SUCCESS" if success else "FAILED"
        print(
            f"[DB {status}] {event_type} - Table: {table} Operation: {operation} - {details}"
        )

    @staticmethod
    def log_worker_event(event_type: str, worker: str, details: str = ""):
        """Log background worker events"""
        print(f"[WORKER] {event_type} - Worker: {worker} - {details}")

    @staticmethod
    def log_error(error_type: str, error_msg: str, context: Dict[str, Any] = None):
        """Log errors with context"""
        print(f"[ERROR] {error_type}: {error_msg}")
        if context:
            print(f"[ERROR CONTEXT] {json.dumps(context, default=str, indent=2)}")


# Create global logger instance
api_logger = APILoggingService()

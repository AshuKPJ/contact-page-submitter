from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio
import time
import traceback


class TimeoutMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, timeout: float = 30.0):
        super().__init__(app)
        self.timeout = timeout

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        try:
            response = await asyncio.wait_for(call_next(request), timeout=self.timeout)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            return response

        except asyncio.TimeoutError:
            return JSONResponse(status_code=408, content={"detail": "Request timeout"})
        except Exception as e:
            traceback.print_exc()
            return JSONResponse(
                status_code=500, content={"detail": "Internal server error"}
            )

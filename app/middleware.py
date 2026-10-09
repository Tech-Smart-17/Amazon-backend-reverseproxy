"""
Custom FastAPI Middlewares for Logging, Correlation IDs, Execution Timing, and Rate Limiting.
"""
import time
import uuid
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.database import get_redis

logger = logging.getLogger("amazon_backend")

class CustomHeaderAndLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 1. Correlation ID
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id

        # 2. Execution timing
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        # 3. Add headers
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"
        response.headers["X-Correlation-ID"] = correlation_id

        # 4. Structured Log
        logger.info(
            f"[{correlation_id}] {request.method} {request.url.path} - Status: {response.status_code} - Duration: {process_time:.4f}s"
        )
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "127.0.0.1"
        key = f"rate_limit:{client_ip}"
        
        try:
            redis_inst = get_redis()
            req_count = await redis_inst.incr(key)
            if req_count == 1:
                await redis_inst.expire(key, self.window_seconds)
            
            if req_count > self.max_requests:
                return Response(
                    content='{"success": false, "error": {"code": "RATE_LIMIT_EXCEEDED", "message": "Too many requests"}}',
                    status_code=429,
                    media_type="application/json"
                )
        except Exception:
            pass  # Fail open if rate limiter errors out

        return await call_next(request)

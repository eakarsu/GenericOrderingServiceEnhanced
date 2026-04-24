from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict
from ..config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware - limits requests per IP address."""

    def __init__(self, app, requests_limit: int = RATE_LIMIT_REQUESTS, window: int = RATE_LIMIT_WINDOW):
        super().__init__(app)
        self.requests_limit = requests_limit
        self.window = window
        self.clients = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # Clean old entries
        self.clients[client_ip] = [
            t for t in self.clients[client_ip] if now - t < self.window
        ]

        if len(self.clients[client_ip]) >= self.requests_limit:
            return JSONResponse(
                status_code=429,
                content={
                    "error": True,
                    "message": "Too many requests. Please try again later.",
                    "retry_after": self.window
                },
                headers={"Retry-After": str(self.window)}
            )

        self.clients[client_ip].append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_limit)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests_limit - len(self.clients[client_ip])
        )
        return response

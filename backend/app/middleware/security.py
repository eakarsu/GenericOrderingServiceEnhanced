from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import html
import re


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds security headers similar to helmet.js."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        return response


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """Sanitizes input to prevent XSS and injection attacks."""

    async def dispatch(self, request: Request, call_next):
        # Sanitize query parameters
        if request.query_params:
            for key, value in request.query_params.items():
                if self._is_suspicious(value):
                    from fastapi.responses import JSONResponse
                    return JSONResponse(
                        status_code=400,
                        content={"error": True, "message": f"Invalid input in parameter: {key}"}
                    )
        response = await call_next(request)
        return response

    def _is_suspicious(self, value: str) -> bool:
        patterns = [
            r'<script[^>]*>',
            r'javascript:',
            r'on\w+\s*=',
            r'union\s+select',
            r';\s*drop\s+table',
            r'--\s*$',
            r'/\*.*\*/',
        ]
        for pattern in patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False

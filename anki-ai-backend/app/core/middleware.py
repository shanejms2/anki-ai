"""
Middleware for security, rate limiting, and request processing.
"""

import time
import json
from typing import Callable, Dict, Any
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import RequestResponseEndpoint
from app.core.rate_limiter import check_rate_limit_middleware, get_rate_limit_config
from app.core.validation import InputSanitizer, validate_search_query, validate_pagination_params
from app.core.logging import logger


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware for security headers and basic request validation."""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Add security headers
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting requests."""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Get client identifier (IP address or user ID)
        client_id = self._get_client_id(request)
        
        # Determine endpoint category and action
        category, action = self._get_endpoint_info(request)
        
        try:
            # Check rate limit
            headers = check_rate_limit_middleware(client_id, category, action)
            
            # Add rate limit headers to response
            response = await call_next(request)
            
            for key, value in headers.items():
                response.headers[key] = str(value)
            
            return response
            
        except HTTPException as e:
            if e.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                safe_headers = {k: str(v) for k, v in (e.headers or {}).items()}
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Rate limit exceeded. Please try again later."},
                    headers=safe_headers
                )
            raise
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Try to get user ID from token first
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # For authenticated users, use a placeholder that will be replaced with actual user ID
            # The actual user ID will be extracted in the auth middleware
            return "authenticated_user"
        
        # Fall back to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        return request.client.host if request.client else "unknown"
    
    def _get_endpoint_info(self, request: Request) -> tuple:
        """Extract endpoint category and action from request path."""
        path = request.url.path
        
        # Map paths to categories and actions
        if path.startswith("/api/v1/auth"):
            if "login" in path:
                return "auth", "login"
            elif "register" in path:
                return "auth", "register"
            elif "password-reset" in path:
                return "auth", "password_reset"
            elif "refresh" in path:
                return "auth", "refresh"
            else:
                return "auth", "other"
        
        elif path.startswith("/api/v1/cards"):
            if request.method == "POST":
                return "cards", "create"
            elif request.method == "PUT":
                return "cards", "update"
            elif request.method == "DELETE":
                return "cards", "delete"
            elif request.method == "GET":
                if "due" in path:
                    return "cards", "list"  # Due cards are still list operations
                else:
                    return "cards", "get"
            else:
                return "cards", "other"
        
        elif path.startswith("/api/v1/reviews"):
            if request.method == "POST":
                return "reviews", "submit"
            elif request.method == "GET":
                if "stats" in path:
                    return "reviews", "stats"
                else:
                    return "reviews", "list"
            else:
                return "reviews", "other"
        
        elif path.startswith("/api/v1/system"):
            if "cache/stats" in path:
                return "system", "cache_stats"
            elif "cache/clear" in path:
                return "system", "cache_clear"
            elif "cache/cleanup" in path:
                return "system", "cache_cleanup"
            else:
                return "system", "other"
        
        else:
            return "default", "other"


class InputValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for input validation and sanitization."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip body sanitization for auth endpoints to avoid login issues
        if request.url.path.startswith("/api/v1/auth"):
            return await call_next(request)

        # Sanitize query parameters (optional: you can remove this if not needed)
        if request.query_params:
            sanitized_params = {}
            for key, value in request.query_params.items():
                if key in ["search", "q"]:
                    sanitized_params[key] = validate_search_query(value)
                elif key in ["page", "page_size"]:
                    sanitized_params[key] = value
                elif key in ["sort_by", "sort_order"]:
                    sanitized_params[key] = value
                else:
                    sanitized_params[key] = InputSanitizer.sanitize_text(value, 100)
            # Note: Do NOT mutate request.scope["query_string"] directly unless you know what you're doing

        # Sanitize JSON body for specific endpoints (skip auth)
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                try:
                    # Read the body
                    body = await request.body()
                    if body:
                        json_data = json.loads(body)
                        sanitized_data = self._sanitize_json_data(json_data, request.url.path)
                        # Set the sanitized body for downstream consumers
                        request._body = json.dumps(sanitized_data).encode()
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON in request body: {request.url.path}")
                except Exception as e:
                    logger.error(f"Error sanitizing request body: {e}")

        # Always call call_next exactly once
        response = await call_next(request)
        return response

    def _sanitize_json_data(self, data: Dict[str, Any], path: str) -> Dict[str, Any]:
        """Sanitize JSON data based on endpoint."""
        if not isinstance(data, dict):
            return data

        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                if "email" in key.lower():
                    sanitized[key] = InputSanitizer.sanitize_email(value)
                elif "url" in key.lower():
                    sanitized[key] = InputSanitizer.sanitize_url(value)
                elif "password" in key.lower():
                    if len(value) < 8:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Password must be at least 8 characters long"
                        )
                    sanitized[key] = value
                elif "content" in key.lower() or "html" in key.lower():
                    sanitized[key] = InputSanitizer.sanitize_html(value)
                else:
                    sanitized[key] = InputSanitizer.sanitize_text(value)
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_json_data(value, path)
            elif isinstance(value, list):
                sanitized[key] = [
                    self._sanitize_json_data(item, path) if isinstance(item, dict)
                    else InputSanitizer.sanitize_text(str(item)) if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                sanitized[key] = value

        return sanitized


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown")
            }
        )
        
        try:
            response = await call_next(request)
            
            # Log response
            process_time = time.time() - start_time
            logger.info(
                f"Request completed: {request.method} {request.url.path} - {response.status_code}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time": process_time
                }
            )
            
            # Add timing header
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path} - {str(e)}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "process_time": process_time
                }
            )
            raise


def setup_middleware(app):
    """Setup all middleware for the FastAPI application."""
    app.add_middleware(SecurityMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(InputValidationMiddleware)
    app.add_middleware(LoggingMiddleware) 
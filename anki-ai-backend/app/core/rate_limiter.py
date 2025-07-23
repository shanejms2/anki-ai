"""
Rate limiting and request throttling system
Provides protection against abuse and ensures fair usage.
"""

import time
from typing import Dict, Tuple, Optional
from collections import defaultdict, deque
from dataclasses import dataclass
from fastapi import HTTPException, status
from app.core.logging import logger


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    max_requests: int
    window_seconds: int
    burst_limit: Optional[int] = None


class RateLimiter:
    """In-memory rate limiter with sliding window and burst protection."""
    
    def __init__(self):
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.burst_requests: Dict[str, deque] = defaultdict(deque)
        self._cleanup_interval = 3600  # Cleanup every hour
        self._last_cleanup = time.time()
    
    def _cleanup_old_requests(self):
        """Remove expired request timestamps."""
        current_time = time.time()
        if current_time - self._last_cleanup > self._cleanup_interval:
            for key in list(self.requests.keys()):
                window_start = current_time - 3600  # Keep last hour
                self.requests[key] = deque(
                    ts for ts in self.requests[key] if ts > window_start
                )
                if not self.requests[key]:
                    del self.requests[key]
            
            for key in list(self.burst_requests.keys()):
                window_start = current_time - 60  # Keep last minute for burst
                self.burst_requests[key] = deque(
                    ts for ts in self.burst_requests[key] if ts > window_start
                )
                if not self.burst_requests[key]:
                    del self.burst_requests[key]
            
            self._last_cleanup = current_time
    
    def _get_client_key(self, client_id: str, endpoint: str) -> str:
        """Generate a unique key for client + endpoint combination."""
        return f"{client_id}:{endpoint}"
    
    def check_rate_limit(
        self, 
        client_id: str, 
        endpoint: str, 
        config: RateLimitConfig
    ) -> Tuple[bool, Dict[str, int]]:
        """
        Check if request is within rate limits.
        
        Returns:
            Tuple of (allowed: bool, headers: Dict)
        """
        self._cleanup_old_requests()
        
        current_time = time.time()
        key = self._get_client_key(client_id, endpoint)
        
        # Check burst limit first (if configured)
        if config.burst_limit:
            burst_window = 60  # 1 minute burst window
            burst_start = current_time - burst_window
            
            # Remove old burst requests
            self.burst_requests[key] = deque(
                ts for ts in self.burst_requests[key] if ts > burst_start
            )
            
            if len(self.burst_requests[key]) >= config.burst_limit:
                logger.warning(f"Burst limit exceeded for {key}")
                return False, {
                    "X-RateLimit-Burst-Remaining": 0,
                    "X-RateLimit-Burst-Reset": int(burst_start + burst_window)
                }
        
        # Check main rate limit
        window_start = current_time - config.window_seconds
        
        # Remove old requests outside the window
        self.requests[key] = deque(
            ts for ts in self.requests[key] if ts > window_start
        )
        
        # Check if limit exceeded
        if len(self.requests[key]) >= config.max_requests:
            logger.warning(f"Rate limit exceeded for {key}")
            return False, {
                "X-RateLimit-Remaining": 0,
                "X-RateLimit-Reset": int(window_start + config.window_seconds)
            }
        
        # Add current request
        self.requests[key].append(current_time)
        if config.burst_limit:
            self.burst_requests[key].append(current_time)
        
        # Calculate remaining requests
        remaining = config.max_requests - len(self.requests[key])
        burst_remaining = config.burst_limit - len(self.burst_requests[key]) if config.burst_limit else None
        
        headers = {
            "X-RateLimit-Limit": config.max_requests,
            "X-RateLimit-Remaining": remaining,
            "X-RateLimit-Reset": int(window_start + config.window_seconds)
        }
        
        if burst_remaining is not None:
            headers["X-RateLimit-Burst-Limit"] = config.burst_limit
            headers["X-RateLimit-Burst-Remaining"] = burst_remaining
        
        return True, headers


# Global rate limiter instance
rate_limiter = RateLimiter()

# Rate limit configurations for different endpoints
RATE_LIMITS = {
    "auth": {
        "login": RateLimitConfig(max_requests=5, window_seconds=300, burst_limit=3),  # 5 per 5min, 3 per min
        "register": RateLimitConfig(max_requests=3, window_seconds=3600, burst_limit=1),  # 3 per hour, 1 per min
        "password_reset": RateLimitConfig(max_requests=3, window_seconds=3600, burst_limit=1),  # 3 per hour, 1 per min
        "refresh": RateLimitConfig(max_requests=10, window_seconds=300, burst_limit=5),  # 10 per 5min, 5 per min
    },
    "cards": {
        "create": RateLimitConfig(max_requests=20, window_seconds=300, burst_limit=5),  # 20 per 5min, 5 per min
        "update": RateLimitConfig(max_requests=30, window_seconds=300, burst_limit=10),  # 30 per 5min, 10 per min
        "delete": RateLimitConfig(max_requests=10, window_seconds=300, burst_limit=3),  # 10 per 5min, 3 per min
        "list": RateLimitConfig(max_requests=500, window_seconds=300, burst_limit=100),  # 500 per 5min, 100 per min
        "get": RateLimitConfig(max_requests=200, window_seconds=300, burst_limit=50),  # 200 per 5min, 50 per min
    },
    "reviews": {
        "submit": RateLimitConfig(max_requests=50, window_seconds=300, burst_limit=10),  # 50 per 5min, 10 per min
        "list": RateLimitConfig(max_requests=100, window_seconds=300, burst_limit=20),  # 100 per 5min, 20 per min
        "stats": RateLimitConfig(max_requests=30, window_seconds=300, burst_limit=10),  # 30 per 5min, 10 per min
    },
    "system": {
        "cache_stats": RateLimitConfig(max_requests=10, window_seconds=300, burst_limit=3),  # 10 per 5min, 3 per min
        "cache_clear": RateLimitConfig(max_requests=2, window_seconds=3600, burst_limit=1),  # 2 per hour, 1 per min
        "cache_cleanup": RateLimitConfig(max_requests=5, window_seconds=3600, burst_limit=2),  # 5 per hour, 2 per min
    }
}

# Default rate limit for unconfigured endpoints
DEFAULT_RATE_LIMIT = RateLimitConfig(max_requests=60, window_seconds=300, burst_limit=15)


def get_rate_limit_config(category: str, action: str) -> RateLimitConfig:
    """Get rate limit configuration for a specific endpoint."""
    return RATE_LIMITS.get(category, {}).get(action, DEFAULT_RATE_LIMIT)


def check_rate_limit_middleware(client_id: str, category: str, action: str):
    """Middleware function to check rate limits."""
    config = get_rate_limit_config(category, action)
    allowed, headers = rate_limiter.check_rate_limit(client_id, f"{category}:{action}", config)
    
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers=headers
        )
    
    return headers 
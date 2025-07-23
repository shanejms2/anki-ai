"""
Caching system for frequently accessed data.
Uses in-memory cache with TTL for performance optimization.
"""

import time
import hashlib
import json
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
from functools import wraps
from app.core.logging import logger


class CacheItem:
    """Represents a cached item with expiration."""
    
    def __init__(self, value: Any, ttl_seconds: int = 300):
        self.value = value
        self.created_at = time.time()
        self.ttl_seconds = ttl_seconds
    
    def is_expired(self) -> bool:
        """Check if the cache item has expired."""
        return time.time() - self.created_at > self.ttl_seconds
    
    def get_value(self) -> Any:
        """Get the cached value if not expired."""
        if self.is_expired():
            return None
        return self.value


class Cache:
    """In-memory cache with TTL support."""
    
    def __init__(self):
        self._cache: Dict[str, CacheItem] = {}
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from prefix and arguments."""
        # Create a hash of the arguments
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        if key in self._cache:
            item = self._cache[key]
            if not item.is_expired():
                self._stats["hits"] += 1
                logger.debug(f"Cache hit for key: {key}")
                return item.get_value()
            else:
                # Remove expired item
                del self._cache[key]
        
        self._stats["misses"] += 1
        logger.debug(f"Cache miss for key: {key}")
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Set a value in cache with TTL."""
        self._cache[key] = CacheItem(value, ttl_seconds)
        self._stats["sets"] += 1
        logger.debug(f"Cache set for key: {key}, TTL: {ttl_seconds}s")
    
    def delete(self, key: str) -> None:
        """Delete a value from cache."""
        if key in self._cache:
            del self._cache[key]
            self._stats["deletes"] += 1
            logger.debug(f"Cache delete for key: {key}")
    
    def delete_pattern(self, pattern: str) -> None:
        """Delete all keys matching a pattern."""
        keys_to_delete = [key for key in self._cache.keys() if pattern in key]
        for key in keys_to_delete:
            self.delete(key)
        logger.debug(f"Cache delete pattern: {pattern}, deleted {len(keys_to_delete)} keys")
    
    def clear(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self._stats,
            "total_requests": total_requests,
            "hit_rate": round(hit_rate, 2),
            "size": len(self._cache)
        }
    
    def cleanup_expired(self) -> int:
        """Remove expired items and return count of removed items."""
        expired_keys = [
            key for key, item in self._cache.items() 
            if item.is_expired()
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.debug(f"Cache cleanup: removed {len(expired_keys)} expired items")
        
        return len(expired_keys)


# Global cache instance
cache = Cache()


def cached(prefix: str, ttl_seconds: int = 300):
    """
    Decorator to cache function results.
    
    Args:
        prefix: Cache key prefix
        ttl_seconds: Time to live in seconds
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache._generate_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl_seconds)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache_pattern(pattern: str):
    """
    Decorator to invalidate cache entries matching a pattern after function execution.
    
    Args:
        pattern: Cache key pattern to invalidate
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            cache.delete_pattern(pattern)
            return result
        
        return wrapper
    return decorator


# Cache key constants
class CacheKeys:
    """Common cache key patterns."""
    
    # User-related cache keys
    USER_PROFILE = "user_profile"
    USER_STATS = "user_stats"
    
    # Card-related cache keys
    USER_CARDS = "user_cards"
    DUE_CARDS = "due_cards"
    DUE_COUNT = "due_count"
    CARD_DETAILS = "card_details"
    
    # Review-related cache keys
    REVIEW_STATS = "review_stats"
    CARD_REVIEWS = "card_reviews"
    
    @staticmethod
    def user_profile(user_id: str) -> str:
        return f"user_profile:{user_id}"
    
    @staticmethod
    def user_stats(user_id: str) -> str:
        return f"user_stats:{user_id}"
    
    @staticmethod
    def user_cards(user_id: str, page: int, size: int, search: str = None) -> str:
        search_hash = hashlib.md5(search.encode()).hexdigest() if search else "none"
        return f"user_cards:{user_id}:{page}:{size}:{search_hash}"
    
    @staticmethod
    def due_cards(user_id: str, limit: int) -> str:
        return f"due_cards:{user_id}:{limit}"
    
    @staticmethod
    def due_count(user_id: str) -> str:
        return f"due_count:{user_id}"
    
    @staticmethod
    def card_details(card_id: str) -> str:
        return f"card_details:{card_id}"
    
    @staticmethod
    def review_stats(user_id: str) -> str:
        return f"review_stats:{user_id}"
    
    @staticmethod
    def card_reviews(card_id: str, limit: int) -> str:
        return f"card_reviews:{card_id}:{limit}"


# Cache TTL constants
class CacheTTL:
    """Cache TTL values in seconds."""
    
    SHORT = 60      # 1 minute
    MEDIUM = 300    # 5 minutes
    LONG = 1800     # 30 minutes
    VERY_LONG = 3600  # 1 hour 
"""
System API endpoints
Handles system monitoring, cache statistics, and health checks.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from app.core.auth import get_current_user
from app.core.cache import cache
from app.core.logging import logger
from app.models.database import User

router = APIRouter(prefix="/system", tags=["System"])


@router.get("/cache/stats")
async def get_cache_stats(current_user: User = Depends(get_current_user)):
    """Get cache statistics and performance metrics."""
    try:
        stats = cache.get_stats()
        
        logger.info(f"Cache stats retrieved by user {current_user.id}")
        
        return {
            "cache_stats": stats,
            "description": "In-memory cache performance metrics"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving cache stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cache statistics"
        )


@router.post("/cache/clear")
async def clear_cache(current_user: User = Depends(get_current_user)):
    """Clear all cached data."""
    try:
        cache.clear()
        
        logger.info(f"Cache cleared by user {current_user.id}")
        
        return {"message": "Cache cleared successfully"}
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear cache"
        )


@router.post("/cache/cleanup")
async def cleanup_expired_cache(current_user: User = Depends(get_current_user)):
    """Remove expired cache entries."""
    try:
        removed_count = cache.cleanup_expired()
        
        logger.info(f"Cache cleanup completed by user {current_user.id}, removed {removed_count} items")
        
        return {
            "message": "Cache cleanup completed",
            "removed_items": removed_count
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cleanup cache"
        ) 
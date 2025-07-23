"""
Reviews API endpoints
Handles review submissions and spaced repetition algorithm integration.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from datetime import datetime, timedelta
from uuid import UUID
from pydantic import BaseModel

from app.core.auth import get_current_user
from app.core.supabase import get_supabase
from app.core.logging import logger
from app.core.cache import cache, CacheKeys, CacheTTL, invalidate_cache_pattern
from app.models.database import Review, ReviewCreate, PaginatedReviews, User
from app.lib.spaced_repetition import SpacedRepetition

router = APIRouter(prefix="/reviews", tags=["Reviews"])


class ReviewSubmissionRequest(BaseModel):
    """Review submission request model."""
    rating: int


class ReviewSubmissionResponse(BaseModel):
    """Review submission response model."""
    review: Review
    card_updated: bool
    next_review: datetime
    message: str


@router.post("/cards/{card_id}/review", response_model=ReviewSubmissionResponse)
async def submit_review(
    card_id: UUID,
    review_data: ReviewSubmissionRequest,
    current_user: User = Depends(get_current_user)
):
    """Submit a review for a card and update spaced repetition algorithm."""
    try:
        supabase = get_supabase()
        
        # Validate rating
        if not 1 <= review_data.rating <= 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 5"
            )
        
        # Get the card
        card_result = supabase.table("cards").select("*").eq("id", str(card_id)).eq("user_id", str(current_user.id)).execute()
        
        if not card_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Card not found"
            )
        
        card_data = card_result.data[0]
        
        # Calculate new interval and ease using spaced repetition algorithm
        new_interval, new_ease, next_review = SpacedRepetition.calculate_next_review(
            current_interval=card_data["interval"],
            current_ease=card_data["ease"],
            rating=review_data.rating
        )
        
        # Create the review record
        review_dict = {
            "user_id": str(current_user.id),
            "card_id": str(card_id),
            "rating": review_data.rating
        }
        
        review_result = supabase.table("reviews").insert(review_dict).execute()
        
        if not review_result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create review"
            )
        
        review = Review(**review_result.data[0])
        
        # Update the card with new interval, ease, and next review date
        card_update = {
            "interval": new_interval,
            "ease": new_ease,
            "next_review": next_review.isoformat()
        }
        
        updated_card_result = supabase.table("cards").update(card_update).eq("id", str(card_id)).eq("user_id", str(current_user.id)).execute()
        
        if not updated_card_result.data:
            logger.warning(f"Failed to update card {card_id} after review")
            card_updated = False
        else:
            card_updated = True
        
        # Get rating description
        rating_desc = SpacedRepetition.get_rating_description(review_data.rating)
        
        # Invalidate related caches
        cache.delete_pattern(f"review_stats:{str(current_user.id)}")
        cache.delete_pattern(f"card_reviews:{str(card_id)}")
        cache.delete(CacheKeys.card_details(str(card_id)))
        cache.delete_pattern(f"due_cards:{str(current_user.id)}")
        cache.delete_pattern(f"due_count:{str(current_user.id)}")
        
        logger.info(f"Review submitted for card {card_id}: rating={review_data.rating} ({rating_desc}), new_interval={new_interval}, new_ease={new_ease}")
        
        return ReviewSubmissionResponse(
            review=review,
            card_updated=card_updated,
            next_review=next_review,
            message=f"Review submitted successfully. Rating: {rating_desc}. Next review in {new_interval} days."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting review for card {card_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit review"
        )


@router.get("/", response_model=PaginatedReviews)
async def list_reviews(
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    card_id: Optional[UUID] = Query(None, description="Filter by card ID")
):
    """List user's reviews with pagination and optional filtering."""
    # Try to get from cache first
    cache_key = f"user_reviews:{str(current_user.id)}:{page}:{size}:{str(card_id) if card_id else 'all'}"
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    """List user's reviews with pagination and optional filtering."""
    try:
        supabase = get_supabase()
        
        # Calculate offset
        offset = (page - 1) * size
        
        # Build query
        query = supabase.table("reviews").select("*").eq("user_id", str(current_user.id))
        
        # Add card filter if provided
        if card_id:
            query = query.eq("card_id", str(card_id))
        
        # Get total count
        count_query = query
        count_result = count_query.execute()
        total = len(count_result.data)
        
        # Get paginated results
        result = query.range(offset, offset + size - 1).order("reviewed_at", desc=True).execute()
        
        reviews = [Review(**review_data) for review_data in result.data]
        
        # Calculate pagination info
        pages = (total + size - 1) // size
        
        logger.info(f"Retrieved {len(reviews)} reviews for user {current_user.id}")
        
        result = PaginatedReviews(
            items=reviews,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
        
        # Cache the result
        cache.set(cache_key, result, CacheTTL.MEDIUM)
        
        return result
        
    except Exception as e:
        logger.error(f"Error listing reviews: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve reviews"
        )


@router.get("/cards/{card_id}", response_model=List[Review])
async def get_card_reviews(
    card_id: UUID,
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of reviews to return")
):
    """Get all reviews for a specific card."""
    # Try to get from cache first
    cache_key = CacheKeys.card_reviews(str(card_id), limit)
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    """Get all reviews for a specific card."""
    try:
        supabase = get_supabase()
        
        # Verify the card belongs to the user
        card_result = supabase.table("cards").select("id").eq("id", str(card_id)).eq("user_id", str(current_user.id)).execute()
        
        if not card_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Card not found"
            )
        
        # Get reviews for this card
        result = supabase.table("reviews").select("*").eq("card_id", str(card_id)).eq("user_id", str(current_user.id)).order("reviewed_at", desc=True).limit(limit).execute()
        
        reviews = [Review(**review_data) for review_data in result.data]
        
        # Cache the result
        cache.set(cache_key, reviews, CacheTTL.MEDIUM)
        
        logger.info(f"Retrieved {len(reviews)} reviews for card {card_id}")
        
        return reviews
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving reviews for card {card_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve card reviews"
        )


@router.get("/stats")
async def get_review_stats(
    current_user: User = Depends(get_current_user)
):
    """Get review statistics for the user."""
    # Try to get from cache first
    cache_key = CacheKeys.review_stats(str(current_user.id))
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    """Get review statistics for the user."""
    try:
        supabase = get_supabase()
        
        # Get total reviews count
        reviews_result = supabase.table("reviews").select("id", count="exact").eq("user_id", str(current_user.id)).execute()
        total_reviews = reviews_result.count or 0
        
        # Get reviews by rating
        rating_stats = {}
        for rating in range(1, 6):
            rating_result = supabase.table("reviews").select("id", count="exact").eq("user_id", str(current_user.id)).eq("rating", rating).execute()
            rating_stats[rating] = rating_result.count or 0
        
        # Get recent reviews (last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        recent_result = supabase.table("reviews").select("id", count="exact").eq("user_id", str(current_user.id)).gte("reviewed_at", week_ago).execute()
        recent_reviews = recent_result.count or 0
        
        # Calculate success rate (ratings 3-5)
        success_reviews = rating_stats[3] + rating_stats[4] + rating_stats[5]
        success_rate = (success_reviews / total_reviews * 100) if total_reviews > 0 else 0
        
        stats = {
            "total_reviews": total_reviews,
            "recent_reviews": recent_reviews,
            "success_rate": round(success_rate, 2),
            "rating_distribution": {
                "forgot": rating_stats[1],
                "hard": rating_stats[2],
                "good": rating_stats[3],
                "easy": rating_stats[4],
                "perfect": rating_stats[5]
            }
        }
        
        # Cache the result with longer TTL since stats don't change frequently
        cache.set(cache_key, stats, CacheTTL.LONG)
        
        logger.info(f"Retrieved review stats for user {current_user.id}")
        
        return stats
        
    except Exception as e:
        logger.error(f"Error retrieving review stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve review statistics"
        ) 
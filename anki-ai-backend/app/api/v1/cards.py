"""
Cards API endpoints
Handles CRUD operations for flashcards and spaced repetition logic.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from app.core.auth import get_current_user
from app.core.supabase import get_supabase
from app.core.logging import logger
from app.core.cache import cache, CacheKeys, CacheTTL, invalidate_cache_pattern
from app.models.database import (
    Card, CardCreate, CardUpdate, PaginatedCards, CardWithReviews
)
from app.lib.spaced_repetition import SpacedRepetition

router = APIRouter(prefix="/cards", tags=["Cards"])


class DummyModel(BaseModel):
    foo: str
    bar: int

@router.post("/test-dummy")
async def test_dummy(dummy: DummyModel):
    print("DUMMY ENDPOINT CALLED:", dummy)
    return dummy


@router.get("/test")
async def test_cards_endpoint():
    """Test endpoint to verify routing is working."""
    return {"message": "Cards endpoint is working"}


@router.get("/test-auth")
async def test_auth_endpoint(current_user: Card = Depends(get_current_user)):
    """Test endpoint to verify authentication is working."""
    return {"message": "Authentication is working", "user_id": str(current_user.id)}


@router.post("/test-post")
async def test_post_endpoint(current_user: Card = Depends(get_current_user)):
    """Test POST endpoint with authentication."""
    return {"message": "POST with authentication is working", "user_id": str(current_user.id)}


# Minimal endpoint to test CardCreate model validation only
@router.post("/test-card")
async def test_card(card_data: CardCreate):
    print("Received card_data:", card_data)
    return card_data

# Minimal endpoint to test get_current_user dependency only
@router.post("/test-dep")
async def test_dep(current_user: Card = Depends(get_current_user)):
    print("Current user:", current_user)
    return {"user_id": str(current_user.id)}

# Plain endpoint to test FastAPI routing and ASGI stack
@router.post("/test-plain")
async def test_plain():
    print("PLAIN ENDPOINT CALLED")
    return {"message": "plain works"}


@router.get("/", response_model=PaginatedCards)
async def list_cards(
    current_user: Card = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search in front and back content")
):
    """List user's cards with pagination and optional search."""
    # Try to get from cache first
    cache_key = CacheKeys.user_cards(str(current_user.id), page, size, search)
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    """List user's cards with pagination and optional search."""
    try:
        supabase = get_supabase()
        
        # Calculate offset
        offset = (page - 1) * size
        
        # Build query
        query = supabase.table("cards").select("*").eq("user_id", str(current_user.id))
        
        # Add search filter if provided
        if search:
            query = query.or_(f"front.ilike.%{search}%,back.ilike.%{search}%")
        
        # Get total count
        count_query = query
        count_result = count_query.execute()
        total = len(count_result.data)
        
        # Get paginated results
        result = query.range(offset, offset + size - 1).order("created_at", desc=True).execute()
        
        cards = [Card(**card_data) for card_data in result.data]
        
        # Calculate pagination info
        pages = (total + size - 1) // size
        
        logger.info(f"Retrieved {len(cards)} cards for user {current_user.id}")
        
        result = PaginatedCards(
            items=cards,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
        
        # Cache the result
        cache.set(cache_key, result, CacheTTL.MEDIUM)
        
        return result
        
    except Exception as e:
        logger.error(f"Error listing cards: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cards"
        )


@router.post("/", response_model=Card)
async def create_card(
    card_data: CardCreate,
    current_user: Card = Depends(get_current_user)
):
    logger.info("=== ENTERED create_card ENDPOINT ===")
    logger.info(f"Received card_data: {card_data}")
    logger.info(f"Current user: {current_user}")
    try:
        logger.info("Step 1: Starting card creation process")
        logger.info(f"User ID: {current_user.id}")
        logger.info("Step 2: Getting Supabase client (before)")
        try:
            supabase = get_supabase()
            logger.info("✓ Supabase client retrieved successfully (after)")
        except Exception as e:
            logger.error(f"✗ Failed to get Supabase client: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database connection failed: {str(e)}"
            )
        logger.info("Step 3: Testing Supabase connection (before)")
        try:
            logger.info("Testing Supabase connection...")
            test_result = await run_in_threadpool(lambda: supabase.table("cards").select("id").limit(1).execute())
            logger.info(f"✓ Supabase connection test successful: {test_result} (after)")
        except Exception as test_error:
            logger.error(f"✗ Supabase connection test failed: {test_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database connection failed: {str(test_error)}"
            )
        logger.info("Step 4: Preparing card data (before)")
        try:
            now = datetime.utcnow().isoformat()
            card_dict = card_data.dict()
            card_dict["id"] = str(uuid4())
            card_dict["user_id"] = str(current_user.id)
            card_dict["interval"] = 1
            card_dict["ease"] = 2.5
            card_dict["next_review"] = now
            card_dict["created_at"] = now
            card_dict["updated_at"] = now
            logger.info(f"✓ Card data prepared: {card_dict} (after)")
        except Exception as e:
            logger.error(f"✗ Failed to prepare card data: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to prepare card data: {str(e)}"
            )
        logger.info("Step 5: Executing Supabase insert (before)")
        try:
            logger.info("Executing Supabase insert...")
            result = await run_in_threadpool(lambda: supabase.table("cards").insert(card_dict).execute())
            logger.info("✓ Supabase insert completed (after)")
        except Exception as insert_error:
            logger.error(f"✗ Supabase insert failed: {insert_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database insert failed: {str(insert_error)}"
            )
        logger.info("Step 6: Processing insert result (before)")
        try:
            logger.info(f"Supabase insert result: {result}")
            logger.info(f"Result data: {result.data}")
            logger.info(f"Result error: {getattr(result, 'error', None)}")
            if not result.data:
                logger.error(f"✗ Supabase insert failed - no data returned: {result}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create card - no data returned from database"
                )
            card = Card(**result.data[0])
            logger.info(f"✓ Card object created: {card.id} (after)")
        except Exception as e:
            logger.error(f"✗ Failed to process insert result: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process insert result: {str(e)}"
            )
        logger.info("Step 7: Invalidating cache (before)")
        try:
            cache.delete_pattern(f"user_cards:{str(current_user.id)}")
            logger.info("✓ Cache invalidated (after)")
        except Exception as e:
            logger.warning(f"Cache invalidation failed (non-critical): {e}")
        logger.info(f"✓ SUCCESS: Created card {card.id} for user {current_user.id}")
        return card
    except Exception as e:
        logger.error(f"Unhandled exception in create_card: {e}")
        raise


@router.get("/{card_id}", response_model=Card)
async def get_card(
    card_id: UUID,
    current_user: Card = Depends(get_current_user)
):
    """Get a specific card by ID."""
    # Try to get from cache first
    cache_key = CacheKeys.card_details(str(card_id))
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    """Get a specific card by ID."""
    try:
        supabase = get_supabase()
        
        result = supabase.table("cards").select("*").eq("id", str(card_id)).eq("user_id", str(current_user.id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Card not found"
            )
        
        card = Card(**result.data[0])
        
        # Cache the result
        cache.set(cache_key, card, CacheTTL.MEDIUM)
        
        return card
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving card {card_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve card"
        )


@router.put("/{card_id}", response_model=Card)
async def update_card(
    card_id: UUID,
    card_data: CardUpdate,
    current_user: Card = Depends(get_current_user)
):
    """Update a card."""
    try:
        supabase = get_supabase()
        
        # Filter out None values
        update_dict = {k: v for k, v in card_data.dict().items() if v is not None}
        
        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields to update"
            )
        
        # Update card
        result = supabase.table("cards").update(update_dict).eq("id", str(card_id)).eq("user_id", str(current_user.id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Card not found"
            )
        
        card = Card(**result.data[0])
        
        # Invalidate card cache
        cache.delete(CacheKeys.card_details(str(card_id)))
        
        logger.info(f"Updated card {card_id} for user {current_user.id}")
        
        return card
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating card {card_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update card"
        )


@router.delete("/{card_id}")
async def delete_card(
    card_id: UUID,
    current_user: Card = Depends(get_current_user)
):
    """Delete a card."""
    try:
        supabase = get_supabase()
        
        # Delete card (cascading delete will handle reviews)
        result = supabase.table("cards").delete().eq("id", str(card_id)).eq("user_id", str(current_user.id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Card not found"
            )
        
        # Invalidate related caches
        cache.delete(CacheKeys.card_details(str(card_id)))
        cache.delete_pattern(f"due_cards:{str(current_user.id)}")
        cache.delete_pattern(f"due_count:{str(current_user.id)}")
        cache.delete_pattern(f"user_cards:{str(current_user.id)}")
        
        logger.info(f"Deleted card {card_id} for user {current_user.id}")
        
        return {"message": "Card deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting card {card_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete card"
        )


@router.get("/due/list", response_model=List[Card])
async def get_due_cards(
    current_user: Card = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of due cards to return")
):
    """Get cards that are due for review."""
    # Try to get from cache first
    cache_key = CacheKeys.due_cards(str(current_user.id), limit)
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    """Get cards that are due for review."""
    try:
        supabase = get_supabase()
        
        # Get cards where next_review is in the past
        now = datetime.now().isoformat()
        result = supabase.table("cards").select("*").eq("user_id", str(current_user.id)).lte("next_review", now).limit(limit).execute()
        
        due_cards = [Card(**card_data) for card_data in result.data]
        
        # Cache the result with shorter TTL since due cards change frequently
        cache.set(cache_key, due_cards, CacheTTL.SHORT)
        
        logger.info(f"Retrieved {len(due_cards)} due cards for user {current_user.id}")
        
        return due_cards
        
    except Exception as e:
        logger.error(f"Error retrieving due cards: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve due cards"
        )


@router.get("/due/count")
async def get_due_cards_count(
    current_user: Card = Depends(get_current_user)
):
    """Get the count of cards that are due for review."""
    # Try to get from cache first
    cache_key = CacheKeys.due_count(str(current_user.id))
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    """Get the count of cards that are due for review."""
    try:
        supabase = get_supabase()
        
        # Count cards where next_review is in the past
        now = datetime.now().isoformat()
        result = supabase.table("cards").select("id", count="exact").eq("user_id", str(current_user.id)).lte("next_review", now).execute()
        
        count = result.count or 0
        
        # Cache the result with shorter TTL since due count changes frequently
        cache.set(cache_key, {"due_count": count}, CacheTTL.SHORT)
        
        logger.info(f"User {current_user.id} has {count} cards due for review")
        
        return {"due_count": count}
        
    except Exception as e:
        logger.error(f"Error counting due cards: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to count due cards"
        )


@router.get("/{card_id}/with-reviews", response_model=CardWithReviews)
async def get_card_with_reviews(
    card_id: UUID,
    current_user: Card = Depends(get_current_user)
):
    """Get a card with its review history."""
    try:
        supabase = get_supabase()
        
        # Get the card
        card_result = supabase.table("cards").select("*").eq("id", str(card_id)).eq("user_id", str(current_user.id)).execute()
        
        if not card_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Card not found"
            )
        
        card = Card(**card_result.data[0])
        
        # Get reviews for this card
        reviews_result = supabase.table("reviews").select("*").eq("card_id", str(card_id)).eq("user_id", str(current_user.id)).order("reviewed_at", desc=True).execute()
        
        from app.models.database import Review
        reviews = [Review(**review_data) for review_data in reviews_result.data]
        
        # Create card with reviews
        card_with_reviews = CardWithReviews(**card.dict(), reviews=reviews)
        
        return card_with_reviews
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving card with reviews {card_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve card with reviews"
        ) 


class BulkDeleteRequest(BaseModel):
    card_ids: list[UUID]

class BulkDeleteResponse(BaseModel):
    deleted: int
    failed: int
    errors: list[str] = []

@router.post("/bulk-delete", response_model=BulkDeleteResponse)
async def bulk_delete_cards(
    req: BulkDeleteRequest,
    current_user: Card = Depends(get_current_user)
):
    logger.info(f"Bulk delete requested for {len(req.card_ids)} cards by user {current_user.id}")
    supabase = get_supabase()
    deleted = 0
    failed = 0
    errors = []
    for card_id in req.card_ids:
        try:
            # Only delete cards belonging to the current user
            result = await run_in_threadpool(
                lambda: supabase.table("cards")
                    .delete()
                    .eq("id", str(card_id))
                    .eq("user_id", str(current_user.id))
                    .execute()
            )
            if result.data and (isinstance(result.data, list) and len(result.data) > 0):
                deleted += 1
            else:
                failed += 1
                errors.append(f"Card {card_id} not found or not owned by user.")
        except Exception as e:
            logger.error(f"Failed to delete card {card_id}: {e}")
            failed += 1
            errors.append(f"Card {card_id}: {str(e)}")
    logger.info(f"Bulk delete complete: {deleted} deleted, {failed} failed.")
    return BulkDeleteResponse(deleted=deleted, failed=failed, errors=errors) 
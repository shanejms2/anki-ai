"""
Database models for Anki-AI application.
These models represent the database schema and provide type safety.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from app.core.validation import EnhancedBaseModel, ValidationRules


class UserBase(EnhancedBaseModel):
    """Base user model."""
    email: str = Field(..., description="User's email address", max_length=ValidationRules.EMAIL_MAX_LENGTH)
    username: Optional[str] = Field(None, description="User's username", min_length=ValidationRules.USERNAME_MIN_LENGTH, max_length=ValidationRules.USERNAME_MAX_LENGTH)


class UserCreate(UserBase):
    """Model for creating a new user."""
    password: str = Field(..., description="User's password", min_length=ValidationRules.PASSWORD_MIN_LENGTH, max_length=ValidationRules.PASSWORD_MAX_LENGTH)


class UserUpdate(EnhancedBaseModel):
    """Model for updating user information."""
    email: Optional[str] = Field(None, description="User's email address", max_length=ValidationRules.EMAIL_MAX_LENGTH)
    username: Optional[str] = Field(None, description="User's username", min_length=ValidationRules.USERNAME_MIN_LENGTH, max_length=ValidationRules.USERNAME_MAX_LENGTH)


class User(UserBase):
    """Complete user model."""
    id: UUID = Field(..., description="User's unique identifier")
    created_at: datetime = Field(..., description="User creation timestamp")
    updated_at: datetime = Field(..., description="User last update timestamp")

    class Config:
        from_attributes = True


class CardBase(BaseModel):
    """Base card model."""
    front: str = Field(..., description="Card front content", min_length=ValidationRules.CARD_FRONT_MIN_LENGTH, max_length=ValidationRules.CARD_FRONT_MAX_LENGTH)
    back: str = Field(..., description="Card back content", min_length=ValidationRules.CARD_BACK_MIN_LENGTH, max_length=ValidationRules.CARD_BACK_MAX_LENGTH)


class CardCreate(CardBase):
    """Model for creating a new card."""
    pass


class CardUpdate(EnhancedBaseModel):
    """Model for updating card information."""
    front: Optional[str] = Field(None, description="Card front content", min_length=ValidationRules.CARD_FRONT_MIN_LENGTH, max_length=ValidationRules.CARD_FRONT_MAX_LENGTH)
    back: Optional[str] = Field(None, description="Card back content", min_length=ValidationRules.CARD_BACK_MIN_LENGTH, max_length=ValidationRules.CARD_BACK_MAX_LENGTH)


class Card(CardBase):
    """Complete card model."""
    id: UUID = Field(..., description="Card's unique identifier")
    user_id: UUID = Field(..., description="Owner user's ID")
    interval: int = Field(default=1, description="Current interval in days")
    ease: float = Field(default=2.5, description="Current ease factor")
    next_review: datetime = Field(..., description="Next review date")
    created_at: datetime = Field(..., description="Card creation timestamp")
    updated_at: datetime = Field(..., description="Card last update timestamp")

    class Config:
        from_attributes = True


class ReviewBase(EnhancedBaseModel):
    """Base review model."""
    rating: int = Field(..., description="Review rating (1-5)", ge=ValidationRules.RATING_MIN, le=ValidationRules.RATING_MAX)


class ReviewCreate(ReviewBase):
    """Model for creating a new review."""
    card_id: UUID = Field(..., description="Reviewed card's ID")


class Review(ReviewBase):
    """Complete review model."""
    id: UUID = Field(..., description="Review's unique identifier")
    user_id: UUID = Field(..., description="Reviewer's user ID")
    card_id: UUID = Field(..., description="Reviewed card's ID")
    reviewed_at: datetime = Field(..., description="Review timestamp")

    class Config:
        from_attributes = True


# Response models for API endpoints
class CardWithReviews(Card):
    """Card model with review history."""
    reviews: list[Review] = Field(default=[], description="Card's review history")


class UserWithStats(User):
    """User model with statistics."""
    total_cards: int = Field(default=0, description="Total number of cards")
    total_reviews: int = Field(default=0, description="Total number of reviews")
    cards_due: int = Field(default=0, description="Number of cards due for review")


# Pagination models
class PaginatedResponse(BaseModel):
    """Generic paginated response model."""
    items: list
    total: int
    page: int
    size: int
    pages: int


class PaginatedCards(PaginatedResponse):
    """Paginated response for cards."""
    items: list[Card]


class PaginatedReviews(PaginatedResponse):
    """Paginated response for reviews."""
    items: list[Review] 
"""
Spaced Repetition Algorithm Implementation
Based on the SuperMemo 2 (SM-2) algorithm for flashcard scheduling.
"""

from datetime import datetime, timedelta
from typing import Tuple
from app.core.logging import logger


class SpacedRepetition:
    """Implements the SM-2 spaced repetition algorithm."""
    
    # Rating constants
    RATING_FORGOT = 1
    RATING_HARD = 2
    RATING_GOOD = 3
    RATING_EASY = 4
    RATING_PERFECT = 5
    
    # Default values
    DEFAULT_INTERVAL = 1
    DEFAULT_EASE = 2.5
    MIN_EASE = 1.3
    
    @classmethod
    def calculate_next_review(
        cls, 
        current_interval: int, 
        current_ease: float, 
        rating: int
    ) -> Tuple[int, float, datetime]:
        """
        Calculate the next review interval and ease factor based on the rating.
        
        Args:
            current_interval: Current interval in days
            current_ease: Current ease factor
            rating: User rating (1-5)
            
        Returns:
            Tuple of (new_interval, new_ease, next_review_date)
        """
        logger.debug(f"Calculating next review: interval={current_interval}, ease={current_ease}, rating={rating}")
        
        # Validate rating
        if not 1 <= rating <= 5:
            raise ValueError(f"Rating must be between 1 and 5, got {rating}")
        
        new_interval: int
        new_ease: float
        
        if rating <= cls.RATING_HARD:
            # Forgot or Hard: reset interval, decrease ease
            new_interval = cls.DEFAULT_INTERVAL
            new_ease = max(cls.MIN_EASE, current_ease - 0.2)
        elif rating == cls.RATING_GOOD:
            # Good: increase interval, keep ease
            if current_interval == cls.DEFAULT_INTERVAL:
                new_interval = 6
            else:
                new_interval = int(current_interval * current_ease)
            new_ease = current_ease
        else:
            # Easy or Perfect: increase interval, increase ease
            if current_interval == cls.DEFAULT_INTERVAL:
                new_interval = 6
            else:
                new_interval = int(current_interval * current_ease)
            new_ease = current_ease + 0.15
        
        # Calculate next review date
        next_review = datetime.now() + timedelta(days=new_interval)
        
        logger.debug(f"New values: interval={new_interval}, ease={new_ease}, next_review={next_review}")
        
        return new_interval, new_ease, next_review
    
    @classmethod
    def get_rating_description(cls, rating: int) -> str:
        """Get a human-readable description of the rating."""
        descriptions = {
            cls.RATING_FORGOT: "Forgot",
            cls.RATING_HARD: "Hard", 
            cls.RATING_GOOD: "Good",
            cls.RATING_EASY: "Easy",
            cls.RATING_PERFECT: "Perfect"
        }
        return descriptions.get(rating, "Unknown")
    
    @classmethod
    def get_rating_color(cls, rating: int) -> str:
        """Get a color class for the rating (for UI purposes)."""
        colors = {
            cls.RATING_FORGOT: "red",
            cls.RATING_HARD: "orange",
            cls.RATING_GOOD: "yellow", 
            cls.RATING_EASY: "green",
            cls.RATING_PERFECT: "blue"
        }
        return colors.get(rating, "gray")
    
    @classmethod
    def is_due(cls, next_review: datetime) -> bool:
        """Check if a card is due for review."""
        return datetime.now() >= next_review
    
    @classmethod
    def get_days_until_due(cls, next_review: datetime) -> int:
        """Get the number of days until a card is due."""
        delta = next_review - datetime.now()
        return max(0, delta.days)
    
    @classmethod
    def get_days_overdue(cls, next_review: datetime) -> int:
        """Get the number of days a card is overdue."""
        delta = datetime.now() - next_review
        return max(0, delta.days) 
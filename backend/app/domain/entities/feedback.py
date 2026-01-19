"""Feedback domain entity.

This module contains the Feedback entity for user recipe ratings.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Feedback:
    """User feedback on a recipe they've cooked.

    Attributes:
        id: Unique identifier
        user_id: ID of the user who submitted feedback
        recipe_id: ID of the recipe being rated
        meal_plan_id: ID of the meal plan where this was cooked (optional)
        rating: Rating from 1 (worst) to 5 (best)
        would_make_again: Whether user would cook this recipe again
        notes: Optional feedback notes
        cooked_date: Date when the recipe was cooked
        created_at: When this feedback was submitted
    """

    id: str
    user_id: str
    recipe_id: str
    rating: int
    would_make_again: bool
    meal_plan_id: Optional[str] = None
    notes: Optional[str] = None
    cooked_date: Optional[date] = None
    created_at: Optional[date] = None

    def __post_init__(self) -> None:
        """Validate feedback data."""
        if not 1 <= self.rating <= 5:
            raise ValueError(f"Rating must be between 1 and 5, got {self.rating}")

    @property
    def is_positive(self) -> bool:
        """Check if this is positive feedback (rating >= 4).

        Returns:
            True if rating is 4 or 5
        """
        return self.rating >= 4

    @property
    def is_negative(self) -> bool:
        """Check if this is negative feedback (rating <= 2).

        Returns:
            True if rating is 1 or 2
        """
        return self.rating <= 2

    def get_sentiment_score(self) -> float:
        """Calculate a sentiment score combining rating and would_make_again.

        The score ranges from -1.0 (worst) to 1.0 (best).
        Formula: ((rating - 3) / 2) * (1.2 if would_make_again else 0.8)

        Returns:
            Sentiment score between -1.0 and 1.0
        """
        # Normalize rating to -1 to 1 range (rating 3 = neutral 0)
        normalized_rating = (self.rating - 3) / 2

        # Boost or reduce based on would_make_again
        multiplier = 1.2 if self.would_make_again else 0.8

        score = normalized_rating * multiplier

        # Clamp to [-1, 1] range
        return max(-1.0, min(1.0, score))

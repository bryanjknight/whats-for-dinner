"""Feedback repository interface (port).

This interface defines the contract for feedback persistence operations.
Any implementation (DynamoDB, etc.) must follow this interface.
"""

from abc import ABC, abstractmethod
from typing import Optional

from ..entities.feedback import Feedback


class IFeedbackRepository(ABC):
    """Abstract interface for feedback storage and retrieval."""

    @abstractmethod
    def save(self, feedback: Feedback) -> None:
        """Save feedback to the repository.

        Args:
            feedback: Feedback entity to save

        Raises:
            RecipeError: If save operation fails
        """
        pass

    @abstractmethod
    def get_by_id(self, feedback_id: str) -> Optional[Feedback]:
        """Retrieve feedback by its ID.

        Args:
            feedback_id: Unique feedback identifier

        Returns:
            Feedback if found, None otherwise
        """
        pass

    @abstractmethod
    def get_by_user(self, user_id: str) -> list[Feedback]:
        """Retrieve all feedback from a specific user.

        Args:
            user_id: Unique user identifier

        Returns:
            List of Feedback entities (empty list if none found)
        """
        pass

    @abstractmethod
    def get_by_recipe(self, recipe_id: str) -> list[Feedback]:
        """Retrieve all feedback for a specific recipe.

        Args:
            recipe_id: Unique recipe identifier

        Returns:
            List of Feedback entities (empty list if none found)
        """
        pass

    @abstractmethod
    def delete(self, feedback_id: str) -> bool:
        """Delete feedback from the repository.

        Args:
            feedback_id: Unique feedback identifier

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def exists(self, feedback_id: str) -> bool:
        """Check if feedback exists in the repository.

        Args:
            feedback_id: Unique feedback identifier

        Returns:
            True if feedback exists, False otherwise
        """
        pass

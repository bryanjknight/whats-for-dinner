"""Meal plan repository interface (port).

This interface defines the contract for meal plan persistence operations.
Any implementation (SQLite, DynamoDB, etc.) must follow this interface.
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

from ..entities.meal_plan import MealPlan


class IMealPlanRepository(ABC):
    """Abstract interface for meal plan storage and retrieval."""

    @abstractmethod
    def save(self, meal_plan: MealPlan) -> None:
        """Save a meal plan to the repository.

        Args:
            meal_plan: MealPlan entity to save

        Raises:
            MealPlanError: If save operation fails
        """
        pass

    @abstractmethod
    def get_by_id(self, plan_id: str) -> Optional[MealPlan]:
        """Retrieve a meal plan by its ID.

        Args:
            plan_id: Unique meal plan identifier

        Returns:
            MealPlan if found, None otherwise
        """
        pass

    @abstractmethod
    def get_active_by_user(self, user_id: str) -> Optional[MealPlan]:
        """Retrieve the active meal plan for a user.

        Args:
            user_id: Unique user identifier

        Returns:
            Active MealPlan if found, None otherwise
        """
        pass

    @abstractmethod
    def get_by_user_and_week(self, user_id: str, week_start_date: date) -> Optional[MealPlan]:
        """Retrieve a meal plan for a specific user and week.

        Args:
            user_id: Unique user identifier
            week_start_date: Start date of the week

        Returns:
            MealPlan if found, None otherwise
        """
        pass

    @abstractmethod
    def delete(self, plan_id: str) -> bool:
        """Delete a meal plan from the repository.

        Args:
            plan_id: Unique meal plan identifier

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def exists(self, plan_id: str) -> bool:
        """Check if a meal plan exists in the repository.

        Args:
            plan_id: Unique meal plan identifier

        Returns:
            True if meal plan exists, False otherwise
        """
        pass

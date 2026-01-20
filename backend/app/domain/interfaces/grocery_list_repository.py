"""Grocery list repository interface (port).

This interface defines the contract for grocery list persistence operations.
Any implementation (DynamoDB, etc.) must follow this interface.
"""

from abc import ABC, abstractmethod
from typing import Optional

from ..entities.grocery_list import GroceryList


class IGroceryListRepository(ABC):
    """Abstract interface for grocery list storage and retrieval."""

    @abstractmethod
    def save(self, grocery_list: GroceryList) -> None:
        """Save a grocery list to the repository.

        Args:
            grocery_list: GroceryList entity to save

        Raises:
            RecipeError: If save operation fails
        """
        pass

    @abstractmethod
    def get_by_id(self, list_id: str) -> Optional[GroceryList]:
        """Retrieve a grocery list by its ID.

        Args:
            list_id: Unique grocery list identifier

        Returns:
            GroceryList if found, None otherwise
        """
        pass

    @abstractmethod
    def get_by_meal_plan(self, meal_plan_id: str) -> Optional[GroceryList]:
        """Retrieve the grocery list for a specific meal plan.

        Args:
            meal_plan_id: Unique meal plan identifier

        Returns:
            GroceryList if found, None otherwise
        """
        pass

    @abstractmethod
    def delete(self, list_id: str) -> bool:
        """Delete a grocery list from the repository.

        Args:
            list_id: Unique grocery list identifier

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def exists(self, list_id: str) -> bool:
        """Check if a grocery list exists in the repository.

        Args:
            list_id: Unique grocery list identifier

        Returns:
            True if grocery list exists, False otherwise
        """
        pass

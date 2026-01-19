"""Recipe repository interface (port).

This interface defines the contract for recipe persistence operations.
Any implementation (SQLite, DynamoDB, etc.) must follow this interface.
"""

from abc import ABC, abstractmethod
from typing import Optional

from ..entities.recipe import Recipe


class IRecipeRepository(ABC):
    """Abstract interface for recipe storage and retrieval."""

    @abstractmethod
    def save(self, recipe: Recipe) -> None:
        """Save a recipe to the repository.

        Args:
            recipe: Recipe entity to save

        Raises:
            RecipeError: If save operation fails
        """
        pass

    @abstractmethod
    def get_by_id(self, recipe_id: str) -> Optional[Recipe]:
        """Retrieve a recipe by its ID.

        Args:
            recipe_id: Unique recipe identifier

        Returns:
            Recipe if found, None otherwise
        """
        pass

    @abstractmethod
    def get_all(self) -> list[Recipe]:
        """Retrieve all recipes from the repository.

        Returns:
            List of all recipes
        """
        pass

    @abstractmethod
    def delete(self, recipe_id: str) -> bool:
        """Delete a recipe from the repository.

        Args:
            recipe_id: Unique recipe identifier

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def exists(self, recipe_id: str) -> bool:
        """Check if a recipe exists in the repository.

        Args:
            recipe_id: Unique recipe identifier

        Returns:
            True if recipe exists, False otherwise
        """
        pass

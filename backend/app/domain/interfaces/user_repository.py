"""User repository interface (port).

This interface defines the contract for user profile persistence operations.
Any implementation (SQLite, DynamoDB, etc.) must follow this interface.
"""

from abc import ABC, abstractmethod
from typing import Optional

from ..entities.user_profile import UserProfile
from ..exceptions import UserError


class IUserRepository(ABC):
    """Abstract interface for user profile storage and retrieval."""

    @abstractmethod
    def save(self, user: UserProfile) -> None:
        """Save a user profile to the repository.

        Args:
            user: UserProfile entity to save

        Raises:
            UserError: If save operation fails
        """
        pass

    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[UserProfile]:
        """Retrieve a user profile by its ID.

        Args:
            user_id: Unique user identifier

        Returns:
            UserProfile if found, None otherwise
        """
        pass

    @abstractmethod
    def delete(self, user_id: str) -> bool:
        """Delete a user profile from the repository.

        Args:
            user_id: Unique user identifier

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def exists(self, user_id: str) -> bool:
        """Check if a user profile exists in the repository.

        Args:
            user_id: Unique user identifier

        Returns:
            True if user exists, False otherwise
        """
        pass

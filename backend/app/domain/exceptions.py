"""Domain layer exceptions.

These exceptions represent business logic errors and should have zero
external dependencies. They can be caught and handled by the application
or infrastructure layers.
"""


class DomainException(Exception):
    """Base exception for all domain layer errors."""

    pass


class RecipeNotFoundError(DomainException):
    """Raised when a requested recipe is not found."""

    pass


class UserNotFoundError(DomainException):
    """Raised when a requested user is not found."""

    pass


class InvalidRecipeError(DomainException):
    """Raised when recipe data is invalid."""

    pass


class MealPlanGenerationError(DomainException):
    """Raised when meal plan generation fails."""

    pass


class VectorStoreError(DomainException):
    """Raised when vector store operations fail."""

    pass

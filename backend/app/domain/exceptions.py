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


class UserError(DomainException):
    """Raised when user-related operations fail."""

    pass


class RecipeError(DomainException):
    """Raised when recipe-related operations fail."""

    pass


class MealPlanError(DomainException):
    """Raised when meal plan-related operations fail."""

    pass


class LLMError(DomainException):
    """Raised when LLM service operations fail."""

    pass


class EmbeddingError(DomainException):
    """Raised when embedding service operations fail."""

    pass

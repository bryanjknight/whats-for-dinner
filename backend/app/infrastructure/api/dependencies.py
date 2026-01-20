"""FastAPI dependency injection for repositories and services."""

from functools import lru_cache

from app.config import get_settings
from app.domain.interfaces.feedback_repository import IFeedbackRepository
from app.domain.interfaces.grocery_list_repository import IGroceryListRepository
from app.domain.interfaces.meal_plan_repository import IMealPlanRepository
from app.domain.interfaces.recipe_repository import IRecipeRepository
from app.domain.interfaces.user_repository import IUserRepository
from app.infrastructure.persistence.dynamodb import (
    DynamoDBFeedbackRepository,
    DynamoDBGroceryListRepository,
    DynamoDBMealPlanRepository,
    DynamoDBRecipeRepository,
    DynamoDBUserRepository,
)


@lru_cache(maxsize=1)
def get_recipe_repository() -> IRecipeRepository:
    """Get the recipe repository implementation.

    Returns:
        Recipe repository instance
    """
    settings = get_settings()
    return DynamoDBRecipeRepository(settings)


@lru_cache(maxsize=1)
def get_user_repository() -> IUserRepository:
    """Get the user repository implementation.

    Returns:
        User repository instance
    """
    settings = get_settings()
    return DynamoDBUserRepository(settings)


@lru_cache(maxsize=1)
def get_meal_plan_repository() -> IMealPlanRepository:
    """Get the meal plan repository implementation.

    Returns:
        Meal plan repository instance
    """
    settings = get_settings()
    return DynamoDBMealPlanRepository(settings)


@lru_cache(maxsize=1)
def get_feedback_repository() -> IFeedbackRepository:
    """Get the feedback repository implementation.

    Returns:
        Feedback repository instance
    """
    settings = get_settings()
    return DynamoDBFeedbackRepository(settings)


@lru_cache(maxsize=1)
def get_grocery_list_repository() -> IGroceryListRepository:
    """Get the grocery list repository implementation.

    Returns:
        Grocery list repository instance
    """
    settings = get_settings()
    return DynamoDBGroceryListRepository(settings)

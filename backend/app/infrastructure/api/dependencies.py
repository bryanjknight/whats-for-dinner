"""FastAPI dependency injection for repositories and services."""

from functools import lru_cache

from fastapi import Depends

from app.config import Settings, get_settings
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
def get_recipe_repository(settings: Settings = Depends(get_settings)) -> IRecipeRepository:
    """Get the recipe repository implementation.

    Args:
        settings: Application configuration

    Returns:
        Recipe repository instance
    """
    return DynamoDBRecipeRepository(settings)


@lru_cache(maxsize=1)
def get_user_repository(settings: Settings = Depends(get_settings)) -> IUserRepository:
    """Get the user repository implementation.

    Args:
        settings: Application configuration

    Returns:
        User repository instance
    """
    return DynamoDBUserRepository(settings)


@lru_cache(maxsize=1)
def get_meal_plan_repository(
    settings: Settings = Depends(get_settings),
) -> IMealPlanRepository:
    """Get the meal plan repository implementation.

    Args:
        settings: Application configuration

    Returns:
        Meal plan repository instance
    """
    return DynamoDBMealPlanRepository(settings)


@lru_cache(maxsize=1)
def get_feedback_repository(
    settings: Settings = Depends(get_settings),
) -> IFeedbackRepository:
    """Get the feedback repository implementation.

    Args:
        settings: Application configuration

    Returns:
        Feedback repository instance
    """
    return DynamoDBFeedbackRepository(settings)


@lru_cache(maxsize=1)
def get_grocery_list_repository(
    settings: Settings = Depends(get_settings),
) -> IGroceryListRepository:
    """Get the grocery list repository implementation.

    Args:
        settings: Application configuration

    Returns:
        Grocery list repository instance
    """
    return DynamoDBGroceryListRepository(settings)

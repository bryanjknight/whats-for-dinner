"""Domain entities package.

This package contains all domain entities with zero infrastructure dependencies.
"""

from app.domain.entities.feedback import Feedback
from app.domain.entities.grocery_list import GroceryItem, GroceryList
from app.domain.entities.meal_plan import MealPlan, MealSlot
from app.domain.entities.recipe import Ingredient, Recipe
from app.domain.entities.user_profile import UserProfile

__all__ = [
    "Feedback",
    "GroceryItem",
    "GroceryList",
    "Ingredient",
    "MealPlan",
    "MealSlot",
    "Recipe",
    "UserProfile",
]

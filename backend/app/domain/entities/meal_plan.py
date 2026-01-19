"""Meal plan domain entity.

This module contains the MealPlan and MealSlot entities.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class MealSlot:
    """A single meal slot in a meal plan.

    Attributes:
        date: Date for this meal
        recipe_id: ID of the recipe for this meal
        servings: Number of servings to prepare
        notes: Optional notes (e.g., "leftovers for lunch")
    """

    date: date
    recipe_id: str
    servings: int
    notes: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate meal slot data."""
        if self.servings < 1:
            raise ValueError(f"Servings must be at least 1, got {self.servings}")


@dataclass
class MealPlan:
    """A meal plan containing multiple meal slots.

    Attributes:
        id: Unique identifier
        user_id: ID of the user who owns this plan
        week_start_date: Start date of the week (typically Monday)
        meals: List of meal slots
        created_at: When this plan was created
        is_active: Whether this is the current active plan
    """

    id: str
    user_id: str
    week_start_date: date
    meals: list[MealSlot] = field(default_factory=list)
    created_at: Optional[date] = None
    is_active: bool = True

    def add_meal(self, meal: MealSlot) -> None:
        """Add a meal to the plan.

        Args:
            meal: MealSlot to add
        """
        self.meals.append(meal)

    def remove_meal(self, meal_date: date) -> bool:
        """Remove a meal from the plan by date.

        Args:
            meal_date: Date of the meal to remove

        Returns:
            True if a meal was removed, False if not found
        """
        original_length = len(self.meals)
        self.meals = [meal for meal in self.meals if meal.date != meal_date]
        return len(self.meals) < original_length

    def get_meal_by_date(self, meal_date: date) -> Optional[MealSlot]:
        """Get a meal from the plan by date.

        Args:
            meal_date: Date to search for

        Returns:
            MealSlot if found, None otherwise
        """
        for meal in self.meals:
            if meal.date == meal_date:
                return meal
        return None

    def get_all_recipe_ids(self) -> list[str]:
        """Get all unique recipe IDs in this plan.

        Returns:
            List of unique recipe IDs
        """
        return list({meal.recipe_id for meal in self.meals})

    def swap_meal(self, meal_date: date, new_recipe_id: str, new_servings: int) -> bool:
        """Swap a meal in the plan with a new recipe.

        Args:
            meal_date: Date of the meal to swap
            new_recipe_id: ID of the new recipe
            new_servings: Number of servings for the new recipe

        Returns:
            True if swap was successful, False if date not found
        """
        for i, meal in enumerate(self.meals):
            if meal.date == meal_date:
                self.meals[i] = MealSlot(
                    date=meal_date,
                    recipe_id=new_recipe_id,
                    servings=new_servings,
                    notes=meal.notes,
                )
                return True
        return False

    def get_date_range(self) -> tuple[date, date]:
        """Get the date range covered by this meal plan.

        Returns:
            Tuple of (earliest_date, latest_date), or (week_start_date, week_start_date) if no meals
        """
        if not self.meals:
            return (self.week_start_date, self.week_start_date)

        dates = [meal.date for meal in self.meals]
        return (min(dates), max(dates))

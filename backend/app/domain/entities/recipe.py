"""Recipe domain entity.

This module contains the Recipe entity and related value objects.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class Ingredient:
    """An ingredient with quantity and unit.

    Attributes:
        name: Ingredient name (e.g., "chicken breast")
        quantity: Numeric amount
        unit: Measurement unit (e.g., "cups", "oz", "whole")
        notes: Optional preparation notes (e.g., "diced", "cooked")
    """

    name: str
    quantity: float
    unit: str
    notes: Optional[str] = None

    def scale(self, factor: float) -> "Ingredient":
        """Scale ingredient quantity by a factor.

        Args:
            factor: Multiplier for quantity (e.g., 2.0 for double)

        Returns:
            New Ingredient with scaled quantity
        """
        return Ingredient(
            name=self.name,
            quantity=self.quantity * factor,
            unit=self.unit,
            notes=self.notes,
        )


@dataclass
class Recipe:
    """A recipe with ingredients and instructions.

    Attributes:
        id: Unique identifier
        title: Recipe name
        description: Short description
        servings: Number of servings this recipe makes
        prep_time_minutes: Preparation time
        cook_time_minutes: Cooking time
        ingredients: List of ingredients
        instructions: Step-by-step cooking instructions
        dietary_tags: Dietary restriction tags (e.g., "vegetarian", "gluten_free")
        cuisine: Cuisine type (e.g., "italian", "mexican", "thai")
        difficulty: Difficulty level ("easy", "medium", "hard")
        protein_type: Primary protein (e.g., "chicken", "tofu", "beans")
        image_url: Optional URL to recipe image
        source_url: Optional URL to original recipe
        rating: Optional average rating (1-5)
    """

    id: str
    title: str
    description: str
    servings: int
    prep_time_minutes: int
    cook_time_minutes: int
    ingredients: list[Ingredient]
    instructions: list[str]
    dietary_tags: list[str] = field(default_factory=list)
    cuisine: str = "other"
    difficulty: str = "medium"
    protein_type: str = "none"
    image_url: Optional[str] = None
    source_url: Optional[str] = None
    rating: Optional[float] = None

    def __post_init__(self) -> None:
        """Validate recipe data."""
        if self.servings < 1:
            raise ValueError(f"Servings must be at least 1, got {self.servings}")

    @property
    def total_time_minutes(self) -> int:
        """Calculate total time (prep + cook).

        Returns:
            Total time in minutes
        """
        return self.prep_time_minutes + self.cook_time_minutes

    def scale(self, new_servings: int) -> "Recipe":
        """Scale recipe to a different number of servings.

        Args:
            new_servings: Target number of servings

        Returns:
            New Recipe with scaled ingredients

        Raises:
            ValueError: If new_servings is less than 1 or if self.servings is 0
        """
        if new_servings < 1:
            raise ValueError(f"Servings must be at least 1, got {new_servings}")

        if self.servings == 0:
            raise ValueError("Cannot scale recipe with 0 servings")

        if new_servings == self.servings:
            return self

        scale_factor = new_servings / self.servings
        scaled_ingredients = [ingredient.scale(scale_factor) for ingredient in self.ingredients]

        return Recipe(
            id=self.id,
            title=self.title,
            description=self.description,
            servings=new_servings,
            prep_time_minutes=self.prep_time_minutes,
            cook_time_minutes=self.cook_time_minutes,
            ingredients=scaled_ingredients,
            instructions=self.instructions,
            dietary_tags=self.dietary_tags,
            cuisine=self.cuisine,
            difficulty=self.difficulty,
            protein_type=self.protein_type,
            image_url=self.image_url,
            source_url=self.source_url,
            rating=self.rating,
        )

    def meets_dietary_requirements(self, required_tags: list[str]) -> bool:
        """Check if recipe meets all dietary requirements.

        Args:
            required_tags: List of required dietary tags (case-insensitive)

        Returns:
            True if recipe has all required tags
        """
        recipe_tags_lower = {tag.lower() for tag in self.dietary_tags}
        required_tags_lower = {tag.lower() for tag in required_tags}
        return required_tags_lower.issubset(recipe_tags_lower)

    def has_ingredient(self, ingredient_name: str) -> bool:
        """Check if recipe contains a specific ingredient.

        Args:
            ingredient_name: Name to search for (case-insensitive)

        Returns:
            True if ingredient is found
        """
        ingredient_name_lower = ingredient_name.lower()
        return any(ingredient_name_lower in ing.name.lower() for ing in self.ingredients)

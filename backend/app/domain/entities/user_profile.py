"""User profile domain entity.

This module contains the UserProfile entity representing user preferences.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class UserProfile:
    """User profile with dietary preferences and constraints.

    Attributes:
        id: Unique identifier
        name: User's display name
        household_size: Number of people to cook for
        dietary_restrictions: Required dietary tags (e.g., ["vegetarian", "gluten_free"])
        disliked_ingredients: Ingredients to avoid
        cuisine_preferences: Preferred cuisines (e.g., ["italian", "mexican"])
        max_prep_time_minutes: Maximum acceptable prep time
        max_cook_time_minutes: Maximum acceptable cook time
        skill_level: Cooking skill level ("beginner", "intermediate", "advanced")
        avoid_protein_types: Protein types to avoid (e.g., ["beef", "pork"])
    """

    id: str
    name: str
    household_size: int = 2
    dietary_restrictions: list[str] = field(default_factory=list)
    disliked_ingredients: list[str] = field(default_factory=list)
    cuisine_preferences: list[str] = field(default_factory=list)
    max_prep_time_minutes: Optional[int] = None
    max_cook_time_minutes: Optional[int] = None
    skill_level: str = "intermediate"
    avoid_protein_types: list[str] = field(default_factory=list)

    @property
    def max_total_time_minutes(self) -> Optional[int]:
        """Calculate maximum total time if both prep and cook limits are set.

        Returns:
            Total time limit, or None if either limit is not set
        """
        if self.max_prep_time_minutes is None or self.max_cook_time_minutes is None:
            return None
        return self.max_prep_time_minutes + self.max_cook_time_minutes

    def has_dietary_restriction(self, tag: str) -> bool:
        """Check if user has a specific dietary restriction.

        Args:
            tag: Dietary tag to check (case-insensitive)

        Returns:
            True if user has this restriction
        """
        tag_lower = tag.lower()
        return any(tag_lower == restriction.lower() for restriction in self.dietary_restrictions)

    def dislikes_ingredient(self, ingredient_name: str) -> bool:
        """Check if user dislikes a specific ingredient.

        Args:
            ingredient_name: Ingredient to check (case-insensitive)

        Returns:
            True if user dislikes this ingredient
        """
        ingredient_lower = ingredient_name.lower()
        return any(
            ingredient_lower in disliked.lower() for disliked in self.disliked_ingredients
        )

    def avoids_protein(self, protein_type: str) -> bool:
        """Check if user avoids a specific protein type.

        Args:
            protein_type: Protein type to check (case-insensitive)

        Returns:
            True if user avoids this protein
        """
        protein_lower = protein_type.lower()
        return any(protein_lower == avoided.lower() for avoided in self.avoid_protein_types)

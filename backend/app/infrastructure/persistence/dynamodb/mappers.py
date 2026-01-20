"""Data mappers for converting between domain entities and DynamoDB items."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from app.domain.entities.feedback import Feedback
from app.domain.entities.grocery_list import GroceryItem, GroceryList
from app.domain.entities.meal_plan import MealPlan, MealSlot
from app.domain.entities.recipe import Ingredient, Recipe
from app.domain.entities.user_profile import UserProfile


class DateTimeMapper:
    """Handle date and datetime serialization for DynamoDB."""

    @staticmethod
    def to_dynamodb_date(d: date | None) -> str | None:
        """Convert a date to ISO format string for DynamoDB.

        Args:
            d: Date object or None

        Returns:
            ISO format string or None
        """
        if d is None:
            return None
        return d.isoformat()

    @staticmethod
    def from_dynamodb_date(s: str | None) -> date | None:
        """Convert an ISO format string to a date object.

        Args:
            s: ISO format string or None

        Returns:
            Date object or None
        """
        if s is None or not isinstance(s, str):
            return None
        return date.fromisoformat(s)

    @staticmethod
    def to_dynamodb_datetime(dt: datetime | None) -> str | None:
        """Convert a datetime to ISO format string for DynamoDB.

        Args:
            dt: Datetime object or None

        Returns:
            ISO format string or None
        """
        if dt is None:
            return None
        return dt.isoformat()

    @staticmethod
    def from_dynamodb_datetime(s: str | None) -> datetime | None:
        """Convert an ISO format string to a datetime object.

        Args:
            s: ISO format string or None

        Returns:
            Datetime object or None
        """
        if s is None or not isinstance(s, str):
            return None
        return datetime.fromisoformat(s)


class RecipeMapper:
    """Map Recipe entities to/from DynamoDB items."""

    @staticmethod
    def to_dynamodb_item(recipe: Recipe) -> dict[str, Any]:
        """Convert Recipe entity to DynamoDB item.

        Args:
            recipe: Recipe entity

        Returns:
            DynamoDB item representation
        """
        ingredients = [
            {
                "name": ing.name,
                "quantity": Decimal(str(ing.quantity)),
                "unit": ing.unit,
                "notes": ing.notes,
            }
            for ing in recipe.ingredients
        ]

        return {
            "PK": f"RECIPE#{recipe.id}",
            "SK": "METADATA",
            "GSI1PK": "RECIPE#ALL",
            "GSI1SK": recipe.title,
            "EntityType": "Recipe",
            "Data": {
                "id": recipe.id,
                "title": recipe.title,
                "description": recipe.description,
                "servings": Decimal(str(recipe.servings)),
                "prep_time_minutes": Decimal(str(recipe.prep_time_minutes)),
                "cook_time_minutes": Decimal(str(recipe.cook_time_minutes)),
                "ingredients": ingredients,
                "instructions": recipe.instructions,
                "dietary_tags": recipe.dietary_tags,
                "cuisine": recipe.cuisine,
                "difficulty": recipe.difficulty,
                "protein_type": recipe.protein_type,
                "image_url": recipe.image_url,
                "source_url": recipe.source_url,
                "rating": Decimal(str(recipe.rating)) if recipe.rating else None,
            },
            "CreatedAt": DateTimeMapper.to_dynamodb_datetime(datetime.now()),
            "UpdatedAt": DateTimeMapper.to_dynamodb_datetime(datetime.now()),
        }

    @staticmethod
    def from_dynamodb_item(item: dict[str, Any]) -> Recipe:
        """Convert DynamoDB item to Recipe entity.

        Args:
            item: DynamoDB item

        Returns:
            Recipe entity
        """
        data = item.get("Data", {})
        ingredients_data = data.get("ingredients", [])

        ingredients = [
            Ingredient(
                name=ing["name"],
                quantity=float(ing["quantity"]),
                unit=ing["unit"],
                notes=ing.get("notes"),
            )
            for ing in ingredients_data
        ]

        return Recipe(
            id=data.get("id", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            servings=int(data.get("servings", 1)),
            prep_time_minutes=int(data.get("prep_time_minutes", 0)),
            cook_time_minutes=int(data.get("cook_time_minutes", 0)),
            ingredients=ingredients,
            instructions=data.get("instructions", []),
            dietary_tags=data.get("dietary_tags", []),
            cuisine=data.get("cuisine", ""),
            difficulty=data.get("difficulty", ""),
            protein_type=data.get("protein_type", ""),
            image_url=data.get("image_url"),
            source_url=data.get("source_url"),
            rating=float(data["rating"]) if data.get("rating") else None,
        )


class UserProfileMapper:
    """Map UserProfile entities to/from DynamoDB items."""

    @staticmethod
    def to_dynamodb_item(user: UserProfile) -> dict[str, Any]:
        """Convert UserProfile entity to DynamoDB item.

        Args:
            user: UserProfile entity

        Returns:
            DynamoDB item representation
        """
        return {
            "PK": f"USER#{user.id}",
            "SK": "PROFILE",
            "EntityType": "UserProfile",
            "Data": {
                "id": user.id,
                "name": user.name,
                "household_size": Decimal(str(user.household_size)),
                "dietary_restrictions": user.dietary_restrictions,
                "disliked_ingredients": user.disliked_ingredients,
                "cuisine_preferences": user.cuisine_preferences,
                "skill_level": user.skill_level,
                "max_prep_time_minutes": (
                    Decimal(str(user.max_prep_time_minutes)) if user.max_prep_time_minutes else None
                ),
                "max_cook_time_minutes": (
                    Decimal(str(user.max_cook_time_minutes)) if user.max_cook_time_minutes else None
                ),
                "avoid_protein_types": user.avoid_protein_types,
            },
            "CreatedAt": DateTimeMapper.to_dynamodb_datetime(datetime.now()),
            "UpdatedAt": DateTimeMapper.to_dynamodb_datetime(datetime.now()),
        }

    @staticmethod
    def from_dynamodb_item(item: dict[str, Any]) -> UserProfile:
        """Convert DynamoDB item to UserProfile entity.

        Args:
            item: DynamoDB item

        Returns:
            UserProfile entity
        """
        data = item.get("Data", {})

        return UserProfile(
            id=data.get("id", ""),
            name=data.get("name", ""),
            household_size=int(data.get("household_size", 2)),
            dietary_restrictions=data.get("dietary_restrictions", []),
            disliked_ingredients=data.get("disliked_ingredients", []),
            cuisine_preferences=data.get("cuisine_preferences", []),
            skill_level=data.get("skill_level", "intermediate"),
            max_prep_time_minutes=(
                int(data["max_prep_time_minutes"]) if data.get("max_prep_time_minutes") else None
            ),
            max_cook_time_minutes=(
                int(data["max_cook_time_minutes"]) if data.get("max_cook_time_minutes") else None
            ),
            avoid_protein_types=data.get("avoid_protein_types", []),
        )


class MealPlanMapper:
    """Map MealPlan entities to/from DynamoDB items."""

    @staticmethod
    def to_dynamodb_item(meal_plan: MealPlan) -> dict[str, Any]:
        """Convert MealPlan entity to DynamoDB item.

        Args:
            meal_plan: MealPlan entity

        Returns:
            DynamoDB item representation
        """
        meals = [
            {
                "date": DateTimeMapper.to_dynamodb_date(meal.date),
                "recipe_id": meal.recipe_id,
                "servings": Decimal(str(meal.servings)),
                "notes": meal.notes,
            }
            for meal in meal_plan.meals
        ]

        return {
            "PK": f"USER#{meal_plan.user_id}",
            "SK": f"MEALPLAN#{meal_plan.id}",
            "GSI1PK": f"MEALPLAN#{meal_plan.id}",
            "GSI1SK": DateTimeMapper.to_dynamodb_date(meal_plan.week_start_date),
            "EntityType": "MealPlan",
            "Data": {
                "id": meal_plan.id,
                "user_id": meal_plan.user_id,
                "week_start_date": DateTimeMapper.to_dynamodb_date(meal_plan.week_start_date),
                "meals": meals,
                "is_active": meal_plan.is_active,
                "created_at": DateTimeMapper.to_dynamodb_date(meal_plan.created_at),
            },
            "CreatedAt": DateTimeMapper.to_dynamodb_datetime(datetime.now()),
            "UpdatedAt": DateTimeMapper.to_dynamodb_datetime(datetime.now()),
        }

    @staticmethod
    def from_dynamodb_item(item: dict[str, Any]) -> MealPlan:
        """Convert DynamoDB item to MealPlan entity.

        Args:
            item: DynamoDB item

        Returns:
            MealPlan entity
        """
        data = item.get("Data", {})
        meals_data = data.get("meals", [])

        meals = []
        for meal in meals_data:
            meal_date = DateTimeMapper.from_dynamodb_date(meal["date"])
            if meal_date is None:
                raise ValueError(
                    f"Meal date is required but was None for recipe: {meal.get('recipe_id')}"
                )

            meals.append(
                MealSlot(
                    date=meal_date,
                    recipe_id=meal["recipe_id"],
                    servings=int(meal["servings"]),
                    notes=meal.get("notes"),
                )
            )

        week_start = DateTimeMapper.from_dynamodb_date(data.get("week_start_date"))
        if week_start is None:
            raise ValueError(
                f"week_start_date is required but was None for meal plan: {data.get('id')}"
            )

        return MealPlan(
            id=data.get("id", ""),
            user_id=data.get("user_id", ""),
            week_start_date=week_start,
            meals=meals,
            is_active=data.get("is_active", True),
            created_at=DateTimeMapper.from_dynamodb_date(data.get("created_at")),
        )


class FeedbackMapper:
    """Map Feedback entities to/from DynamoDB items."""

    @staticmethod
    def to_dynamodb_item(feedback: Feedback) -> dict[str, Any]:
        """Convert Feedback entity to DynamoDB item.

        Args:
            feedback: Feedback entity

        Returns:
            DynamoDB item representation
        """
        return {
            "PK": f"USER#{feedback.user_id}",
            "SK": f"FEEDBACK#{feedback.id}",
            "GSI1PK": f"RECIPE#{feedback.recipe_id}",
            "GSI1SK": DateTimeMapper.to_dynamodb_datetime(datetime.now()),  # For sorting by recency
            "EntityType": "Feedback",
            "Data": {
                "id": feedback.id,
                "user_id": feedback.user_id,
                "recipe_id": feedback.recipe_id,
                "meal_plan_id": feedback.meal_plan_id,
                "cooked_date": DateTimeMapper.to_dynamodb_date(feedback.cooked_date),
                "rating": Decimal(str(feedback.rating)),
                "would_make_again": feedback.would_make_again,
                "notes": feedback.notes,
                "created_at": DateTimeMapper.to_dynamodb_date(feedback.created_at),
            },
            "CreatedAt": DateTimeMapper.to_dynamodb_datetime(datetime.now()),
            "UpdatedAt": DateTimeMapper.to_dynamodb_datetime(datetime.now()),
        }

    @staticmethod
    def from_dynamodb_item(item: dict[str, Any]) -> Feedback:
        """Convert DynamoDB item to Feedback entity.

        Args:
            item: DynamoDB item

        Returns:
            Feedback entity
        """
        data = item.get("Data", {})

        return Feedback(
            id=data.get("id", ""),
            user_id=data.get("user_id", ""),
            recipe_id=data.get("recipe_id", ""),
            meal_plan_id=data.get("meal_plan_id"),
            cooked_date=DateTimeMapper.from_dynamodb_date(data.get("cooked_date")),
            rating=int(data.get("rating", 3)),
            would_make_again=data.get("would_make_again", False),
            notes=data.get("notes"),
            created_at=DateTimeMapper.from_dynamodb_date(data.get("created_at")),
        )


class GroceryListMapper:
    """Map GroceryList entities to/from DynamoDB items."""

    @staticmethod
    def to_dynamodb_item(grocery_list: GroceryList) -> dict[str, Any]:
        """Convert GroceryList entity to DynamoDB item.

        Args:
            grocery_list: GroceryList entity

        Returns:
            DynamoDB item representation
        """
        items = [
            {
                "name": item.name,
                "quantity": Decimal(str(item.quantity)),
                "unit": item.unit,
                "category": item.category,
                "recipe_sources": item.recipe_sources,
                "is_purchased": item.is_purchased,
                "notes": item.notes,
            }
            for item in grocery_list.items
        ]

        return {
            "PK": f"MEALPLAN#{grocery_list.meal_plan_id}",
            "SK": f"GROCERYLIST#{grocery_list.id}",
            "EntityType": "GroceryList",
            "Data": {
                "id": grocery_list.id,
                "meal_plan_id": grocery_list.meal_plan_id,
                "items": items,
                "created_at": DateTimeMapper.to_dynamodb_date(grocery_list.created_at),
                "week_start_date": DateTimeMapper.to_dynamodb_date(grocery_list.week_start_date),
            },
            "CreatedAt": DateTimeMapper.to_dynamodb_datetime(datetime.now()),
            "UpdatedAt": DateTimeMapper.to_dynamodb_datetime(datetime.now()),
        }

    @staticmethod
    def from_dynamodb_item(item: dict[str, Any]) -> GroceryList:
        """Convert DynamoDB item to GroceryList entity.

        Args:
            item: DynamoDB item

        Returns:
            GroceryList entity
        """
        data = item.get("Data", {})
        items_data = data.get("items", [])

        items = [
            GroceryItem(
                name=grocery_item["name"],
                quantity=float(grocery_item["quantity"]),
                unit=grocery_item["unit"],
                category=grocery_item.get("category", "other"),
                recipe_sources=grocery_item.get("recipe_sources", []),
                is_purchased=grocery_item.get("is_purchased", False),
                notes=grocery_item.get("notes"),
            )
            for grocery_item in items_data
        ]

        return GroceryList(
            id=data.get("id", ""),
            meal_plan_id=data.get("meal_plan_id", ""),
            items=items,
            created_at=DateTimeMapper.from_dynamodb_date(data.get("created_at")),
            week_start_date=DateTimeMapper.from_dynamodb_date(data.get("week_start_date")),
        )

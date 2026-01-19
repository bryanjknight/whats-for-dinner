"""Unit tests for domain entities.

These tests verify entity behavior with zero external dependencies.
"""

from datetime import date

import pytest

from app.domain.entities import (
    Feedback,
    GroceryItem,
    GroceryList,
    Ingredient,
    MealPlan,
    MealSlot,
    Recipe,
    UserProfile,
)


class TestIngredient:
    """Tests for Ingredient dataclass."""

    def test_ingredient_creation(self) -> None:
        """Test creating an ingredient."""
        ing = Ingredient(name="flour", quantity=2.0, unit="cups")
        assert ing.name == "flour"
        assert ing.quantity == 2.0
        assert ing.unit == "cups"
        assert ing.notes is None

    def test_ingredient_with_notes(self) -> None:
        """Test creating an ingredient with notes."""
        ing = Ingredient(name="chicken", quantity=1.0, unit="lb", notes="boneless, skinless")
        assert ing.notes == "boneless, skinless"

    def test_ingredient_scale(self) -> None:
        """Test scaling ingredient quantity."""
        ing = Ingredient(name="sugar", quantity=1.0, unit="cup")
        scaled = ing.scale(2.5)
        assert scaled.quantity == 2.5
        assert scaled.name == "sugar"
        assert scaled.unit == "cup"

    def test_ingredient_scale_fractional(self) -> None:
        """Test scaling ingredient with fractional multiplier."""
        ing = Ingredient(name="butter", quantity=4.0, unit="tbsp")
        scaled = ing.scale(0.5)
        assert scaled.quantity == 2.0


class TestRecipe:
    """Tests for Recipe entity."""

    @pytest.fixture
    def sample_recipe(self) -> Recipe:
        """Create a sample recipe for testing."""
        return Recipe(
            id="recipe-1",
            title="Simple Pasta",
            description="Easy pasta dish",
            servings=4,
            prep_time_minutes=10,
            cook_time_minutes=15,
            ingredients=[
                Ingredient(name="pasta", quantity=1.0, unit="lb"),
                Ingredient(name="olive oil", quantity=2.0, unit="tbsp"),
                Ingredient(name="garlic", quantity=3.0, unit="cloves"),
            ],
            instructions=["Boil water", "Cook pasta", "Add oil and garlic"],
            dietary_tags=["vegetarian"],
            cuisine="italian",
            protein_type="none",
        )

    def test_recipe_creation(self, sample_recipe: Recipe) -> None:
        """Test creating a recipe."""
        assert sample_recipe.id == "recipe-1"
        assert sample_recipe.title == "Simple Pasta"
        assert sample_recipe.servings == 4
        assert len(sample_recipe.ingredients) == 3

    def test_total_time_calculation(self, sample_recipe: Recipe) -> None:
        """Test total time property."""
        assert sample_recipe.total_time_minutes == 25

    def test_recipe_scale_double(self, sample_recipe: Recipe) -> None:
        """Test scaling recipe to double servings."""
        scaled = sample_recipe.scale(8)
        assert scaled.servings == 8
        assert scaled.ingredients[0].quantity == 2.0  # pasta doubled
        assert scaled.ingredients[1].quantity == 4.0  # oil doubled
        assert scaled.title == sample_recipe.title  # title unchanged

    def test_recipe_scale_half(self, sample_recipe: Recipe) -> None:
        """Test scaling recipe to half servings."""
        scaled = sample_recipe.scale(2)
        assert scaled.servings == 2
        assert scaled.ingredients[0].quantity == 0.5  # pasta halved

    def test_recipe_scale_same_servings(self, sample_recipe: Recipe) -> None:
        """Test scaling recipe to same servings returns same recipe."""
        scaled = sample_recipe.scale(4)
        assert scaled is sample_recipe

    def test_recipe_scale_invalid_servings(self, sample_recipe: Recipe) -> None:
        """Test scaling recipe with invalid servings raises error."""
        with pytest.raises(ValueError, match="Servings must be at least 1"):
            sample_recipe.scale(0)

        with pytest.raises(ValueError, match="Servings must be at least 1"):
            sample_recipe.scale(-1)

    def test_meets_dietary_requirements_success(self, sample_recipe: Recipe) -> None:
        """Test recipe meets dietary requirements."""
        assert sample_recipe.meets_dietary_requirements(["vegetarian"])

    def test_meets_dietary_requirements_case_insensitive(self, sample_recipe: Recipe) -> None:
        """Test dietary requirements check is case-insensitive."""
        assert sample_recipe.meets_dietary_requirements(["VEGETARIAN"])
        assert sample_recipe.meets_dietary_requirements(["Vegetarian"])

    def test_meets_dietary_requirements_failure(self, sample_recipe: Recipe) -> None:
        """Test recipe does not meet dietary requirements."""
        assert not sample_recipe.meets_dietary_requirements(["vegan", "gluten_free"])

    def test_has_ingredient_found(self, sample_recipe: Recipe) -> None:
        """Test finding an ingredient in recipe."""
        assert sample_recipe.has_ingredient("pasta")
        assert sample_recipe.has_ingredient("garlic")

    def test_has_ingredient_case_insensitive(self, sample_recipe: Recipe) -> None:
        """Test ingredient search is case-insensitive."""
        assert sample_recipe.has_ingredient("PASTA")
        assert sample_recipe.has_ingredient("Olive Oil")

    def test_has_ingredient_not_found(self, sample_recipe: Recipe) -> None:
        """Test not finding an ingredient in recipe."""
        assert not sample_recipe.has_ingredient("chicken")


class TestUserProfile:
    """Tests for UserProfile entity."""

    @pytest.fixture
    def sample_profile(self) -> UserProfile:
        """Create a sample user profile."""
        return UserProfile(
            id="user-1",
            name="Test User",
            household_size=2,
            dietary_restrictions=["vegetarian", "gluten_free"],
            disliked_ingredients=["mushrooms", "olives"],
            cuisine_preferences=["italian", "mexican"],
            max_prep_time_minutes=30,
            max_cook_time_minutes=45,
            avoid_protein_types=["beef"],
        )

    def test_profile_creation(self, sample_profile: UserProfile) -> None:
        """Test creating a user profile."""
        assert sample_profile.id == "user-1"
        assert sample_profile.household_size == 2
        assert len(sample_profile.dietary_restrictions) == 2

    def test_max_total_time_calculation(self, sample_profile: UserProfile) -> None:
        """Test max total time calculation."""
        assert sample_profile.max_total_time_minutes == 75

    def test_max_total_time_none(self) -> None:
        """Test max total time when limits not set."""
        profile = UserProfile(id="user-2", name="Test")
        assert profile.max_total_time_minutes is None

    def test_has_dietary_restriction(self, sample_profile: UserProfile) -> None:
        """Test checking for dietary restriction."""
        assert sample_profile.has_dietary_restriction("vegetarian")
        assert sample_profile.has_dietary_restriction("GLUTEN_FREE")
        assert not sample_profile.has_dietary_restriction("vegan")

    def test_dislikes_ingredient(self, sample_profile: UserProfile) -> None:
        """Test checking for disliked ingredients."""
        assert sample_profile.dislikes_ingredient("mushrooms")
        assert sample_profile.dislikes_ingredient("OLIVES")
        assert not sample_profile.dislikes_ingredient("tomatoes")

    def test_avoids_protein(self, sample_profile: UserProfile) -> None:
        """Test checking for avoided proteins."""
        assert sample_profile.avoids_protein("beef")
        assert sample_profile.avoids_protein("BEEF")
        assert not sample_profile.avoids_protein("chicken")


class TestMealSlot:
    """Tests for MealSlot entity."""

    def test_meal_slot_creation(self) -> None:
        """Test creating a meal slot."""
        slot = MealSlot(date=date(2024, 1, 15), recipe_id="recipe-1", servings=4, notes="Dinner")
        assert slot.date == date(2024, 1, 15)
        assert slot.servings == 4
        assert slot.notes == "Dinner"

    def test_meal_slot_invalid_servings(self) -> None:
        """Test meal slot with invalid servings raises error."""
        with pytest.raises(ValueError, match="Servings must be at least 1"):
            MealSlot(date=date(2024, 1, 15), recipe_id="recipe-1", servings=0)


class TestMealPlan:
    """Tests for MealPlan entity."""

    @pytest.fixture
    def sample_meal_plan(self) -> MealPlan:
        """Create a sample meal plan."""
        plan = MealPlan(
            id="plan-1",
            user_id="user-1",
            week_start_date=date(2024, 1, 15),
        )
        plan.add_meal(MealSlot(date=date(2024, 1, 15), recipe_id="recipe-1", servings=4))
        plan.add_meal(MealSlot(date=date(2024, 1, 16), recipe_id="recipe-2", servings=2))
        plan.add_meal(MealSlot(date=date(2024, 1, 17), recipe_id="recipe-1", servings=4))
        return plan

    def test_meal_plan_creation(self) -> None:
        """Test creating a meal plan."""
        plan = MealPlan(id="plan-1", user_id="user-1", week_start_date=date(2024, 1, 15))
        assert plan.id == "plan-1"
        assert plan.is_active
        assert len(plan.meals) == 0

    def test_add_meal(self, sample_meal_plan: MealPlan) -> None:
        """Test adding meals to plan."""
        assert len(sample_meal_plan.meals) == 3

    def test_get_meal_by_date(self, sample_meal_plan: MealPlan) -> None:
        """Test retrieving meal by date."""
        meal = sample_meal_plan.get_meal_by_date(date(2024, 1, 16))
        assert meal is not None
        assert meal.recipe_id == "recipe-2"

    def test_get_meal_by_date_not_found(self, sample_meal_plan: MealPlan) -> None:
        """Test retrieving meal for date not in plan."""
        meal = sample_meal_plan.get_meal_by_date(date(2024, 1, 20))
        assert meal is None

    def test_get_all_recipe_ids(self, sample_meal_plan: MealPlan) -> None:
        """Test getting all unique recipe IDs."""
        recipe_ids = sample_meal_plan.get_all_recipe_ids()
        assert len(recipe_ids) == 2
        assert "recipe-1" in recipe_ids
        assert "recipe-2" in recipe_ids

    def test_swap_meal(self, sample_meal_plan: MealPlan) -> None:
        """Test swapping a meal in the plan."""
        success = sample_meal_plan.swap_meal(date(2024, 1, 16), "recipe-3", 6)
        assert success
        meal = sample_meal_plan.get_meal_by_date(date(2024, 1, 16))
        assert meal is not None
        assert meal.recipe_id == "recipe-3"
        assert meal.servings == 6

    def test_swap_meal_not_found(self, sample_meal_plan: MealPlan) -> None:
        """Test swapping meal for non-existent date."""
        success = sample_meal_plan.swap_meal(date(2024, 1, 20), "recipe-3", 4)
        assert not success

    def test_remove_meal(self, sample_meal_plan: MealPlan) -> None:
        """Test removing a meal from plan."""
        success = sample_meal_plan.remove_meal(date(2024, 1, 16))
        assert success
        assert len(sample_meal_plan.meals) == 2

    def test_remove_meal_not_found(self, sample_meal_plan: MealPlan) -> None:
        """Test removing meal that doesn't exist."""
        success = sample_meal_plan.remove_meal(date(2024, 1, 20))
        assert not success

    def test_get_date_range(self, sample_meal_plan: MealPlan) -> None:
        """Test getting date range of meal plan."""
        start, end = sample_meal_plan.get_date_range()
        assert start == date(2024, 1, 15)
        assert end == date(2024, 1, 17)

    def test_get_date_range_empty_plan(self) -> None:
        """Test date range for empty meal plan."""
        plan = MealPlan(id="plan-1", user_id="user-1", week_start_date=date(2024, 1, 15))
        start, end = plan.get_date_range()
        assert start == date(2024, 1, 15)
        assert end == date(2024, 1, 15)


class TestGroceryItem:
    """Tests for GroceryItem entity."""

    def test_grocery_item_creation(self) -> None:
        """Test creating a grocery item."""
        item = GroceryItem(
            name="Tomatoes",
            quantity=3.0,
            unit="whole",
            category="produce",
            recipe_sources=["recipe-1"],
        )
        assert item.name == "Tomatoes"
        assert item.quantity == 3.0
        assert not item.is_purchased

    def test_add_quantity(self) -> None:
        """Test adding quantity to item."""
        item = GroceryItem(name="Flour", quantity=2.0, unit="cups")
        item.add_quantity(1.5)
        assert item.quantity == 3.5

    def test_mark_purchased(self) -> None:
        """Test marking item as purchased."""
        item = GroceryItem(name="Milk", quantity=1.0, unit="gallon")
        assert not item.is_purchased
        item.mark_purchased()
        assert item.is_purchased

    def test_mark_unpurchased(self) -> None:
        """Test marking item as unpurchased."""
        item = GroceryItem(name="Eggs", quantity=1.0, unit="dozen", is_purchased=True)
        item.mark_unpurchased()
        assert not item.is_purchased


class TestGroceryList:
    """Tests for GroceryList entity."""

    @pytest.fixture
    def sample_grocery_list(self) -> GroceryList:
        """Create a sample grocery list."""
        return GroceryList(
            id="list-1",
            meal_plan_id="plan-1",
            week_start_date=date(2024, 1, 15),
        )

    def test_grocery_list_creation(self, sample_grocery_list: GroceryList) -> None:
        """Test creating a grocery list."""
        assert sample_grocery_list.id == "list-1"
        assert sample_grocery_list.total_items == 0

    def test_add_item(self, sample_grocery_list: GroceryList) -> None:
        """Test adding item to grocery list."""
        item = GroceryItem(name="Butter", quantity=1.0, unit="stick")
        sample_grocery_list.add_item(item)
        assert sample_grocery_list.total_items == 1

    def test_consolidate_item_new(self, sample_grocery_list: GroceryList) -> None:
        """Test consolidating a new item."""
        sample_grocery_list.consolidate_item("flour", 2.0, "cups", "recipe-1")
        assert sample_grocery_list.total_items == 1
        assert sample_grocery_list.items[0].quantity == 2.0

    def test_consolidate_item_existing(self, sample_grocery_list: GroceryList) -> None:
        """Test consolidating an existing item."""
        sample_grocery_list.consolidate_item("flour", 2.0, "cups", "recipe-1")
        sample_grocery_list.consolidate_item("flour", 1.5, "cups", "recipe-2")
        assert sample_grocery_list.total_items == 1
        assert sample_grocery_list.items[0].quantity == 3.5
        assert len(sample_grocery_list.items[0].recipe_sources) == 2

    def test_consolidate_item_case_insensitive(self, sample_grocery_list: GroceryList) -> None:
        """Test consolidation is case-insensitive."""
        sample_grocery_list.consolidate_item("Flour", 2.0, "cups", "recipe-1")
        sample_grocery_list.consolidate_item("flour", 1.0, "cups", "recipe-2")
        assert sample_grocery_list.total_items == 1
        assert sample_grocery_list.items[0].quantity == 3.0

    def test_consolidate_different_units(self, sample_grocery_list: GroceryList) -> None:
        """Test items with different units are not consolidated."""
        sample_grocery_list.consolidate_item("sugar", 2.0, "cups", "recipe-1")
        sample_grocery_list.consolidate_item("sugar", 100.0, "grams", "recipe-2")
        assert sample_grocery_list.total_items == 2

    def test_get_items_by_category(self, sample_grocery_list: GroceryList) -> None:
        """Test getting items by category."""
        sample_grocery_list.add_item(
            GroceryItem(name="Tomatoes", quantity=3.0, unit="whole", category="produce")
        )
        sample_grocery_list.add_item(
            GroceryItem(name="Chicken", quantity=2.0, unit="lb", category="meat")
        )
        sample_grocery_list.add_item(
            GroceryItem(name="Lettuce", quantity=1.0, unit="head", category="produce")
        )

        produce = sample_grocery_list.get_items_by_category("produce")
        assert len(produce) == 2

    def test_get_all_categories(self, sample_grocery_list: GroceryList) -> None:
        """Test getting all categories."""
        sample_grocery_list.add_item(
            GroceryItem(name="Tomatoes", quantity=3.0, unit="whole", category="produce")
        )
        sample_grocery_list.add_item(
            GroceryItem(name="Chicken", quantity=2.0, unit="lb", category="meat")
        )
        sample_grocery_list.add_item(
            GroceryItem(name="Milk", quantity=1.0, unit="gallon", category="dairy")
        )

        categories = sample_grocery_list.get_all_categories()
        assert len(categories) == 3
        assert "produce" in categories

    def test_mark_item_purchased(self, sample_grocery_list: GroceryList) -> None:
        """Test marking an item as purchased."""
        sample_grocery_list.add_item(GroceryItem(name="Bread", quantity=1.0, unit="loaf"))
        success = sample_grocery_list.mark_item_purchased("Bread")
        assert success
        assert sample_grocery_list.items[0].is_purchased

    def test_mark_item_purchased_not_found(self, sample_grocery_list: GroceryList) -> None:
        """Test marking non-existent item as purchased."""
        success = sample_grocery_list.mark_item_purchased("Unicorn")
        assert not success

    def test_get_unpurchased_items(self, sample_grocery_list: GroceryList) -> None:
        """Test getting unpurchased items."""
        sample_grocery_list.add_item(
            GroceryItem(name="Bread", quantity=1.0, unit="loaf", is_purchased=True)
        )
        sample_grocery_list.add_item(GroceryItem(name="Milk", quantity=1.0, unit="gallon"))

        unpurchased = sample_grocery_list.get_unpurchased_items()
        assert len(unpurchased) == 1
        assert unpurchased[0].name == "Milk"

    def test_completion_percentage(self, sample_grocery_list: GroceryList) -> None:
        """Test calculating completion percentage."""
        sample_grocery_list.add_item(
            GroceryItem(name="Item1", quantity=1.0, unit="unit", is_purchased=True)
        )
        sample_grocery_list.add_item(
            GroceryItem(name="Item2", quantity=1.0, unit="unit", is_purchased=True)
        )
        sample_grocery_list.add_item(GroceryItem(name="Item3", quantity=1.0, unit="unit"))

        assert sample_grocery_list.completion_percentage == pytest.approx(66.666, rel=0.01)

    def test_completion_percentage_empty(self, sample_grocery_list: GroceryList) -> None:
        """Test completion percentage for empty list."""
        assert sample_grocery_list.completion_percentage == 0.0


class TestFeedback:
    """Tests for Feedback entity."""

    def test_feedback_creation(self) -> None:
        """Test creating feedback."""
        feedback = Feedback(
            id="feedback-1",
            user_id="user-1",
            recipe_id="recipe-1",
            rating=5,
            would_make_again=True,
            notes="Delicious!",
            cooked_date=date(2024, 1, 15),
        )
        assert feedback.rating == 5
        assert feedback.would_make_again

    def test_feedback_invalid_rating_too_high(self) -> None:
        """Test feedback with rating too high raises error."""
        with pytest.raises(ValueError, match="Rating must be between 1 and 5"):
            Feedback(
                id="feedback-1",
                user_id="user-1",
                recipe_id="recipe-1",
                rating=6,
                would_make_again=True,
            )

    def test_feedback_invalid_rating_too_low(self) -> None:
        """Test feedback with rating too low raises error."""
        with pytest.raises(ValueError, match="Rating must be between 1 and 5"):
            Feedback(
                id="feedback-1",
                user_id="user-1",
                recipe_id="recipe-1",
                rating=0,
                would_make_again=False,
            )

    def test_is_positive(self) -> None:
        """Test identifying positive feedback."""
        feedback_5 = Feedback(
            id="f1", user_id="u1", recipe_id="r1", rating=5, would_make_again=True
        )
        feedback_4 = Feedback(
            id="f2", user_id="u1", recipe_id="r1", rating=4, would_make_again=True
        )
        feedback_3 = Feedback(
            id="f3", user_id="u1", recipe_id="r1", rating=3, would_make_again=True
        )

        assert feedback_5.is_positive
        assert feedback_4.is_positive
        assert not feedback_3.is_positive

    def test_is_negative(self) -> None:
        """Test identifying negative feedback."""
        feedback_1 = Feedback(
            id="f1", user_id="u1", recipe_id="r1", rating=1, would_make_again=False
        )
        feedback_2 = Feedback(
            id="f2", user_id="u1", recipe_id="r1", rating=2, would_make_again=False
        )
        feedback_3 = Feedback(
            id="f3", user_id="u1", recipe_id="r1", rating=3, would_make_again=True
        )

        assert feedback_1.is_negative
        assert feedback_2.is_negative
        assert not feedback_3.is_negative

    def test_sentiment_score_highest(self) -> None:
        """Test sentiment score for best feedback."""
        feedback = Feedback(id="f1", user_id="u1", recipe_id="r1", rating=5, would_make_again=True)
        # (5-3)/2 * 1.2 = 1.2, clamped to 1.0
        assert feedback.get_sentiment_score() == 1.0

    def test_sentiment_score_lowest(self) -> None:
        """Test sentiment score for worst feedback."""
        feedback = Feedback(id="f1", user_id="u1", recipe_id="r1", rating=1, would_make_again=False)
        # (1-3)/2 * 0.8 = -0.8
        assert feedback.get_sentiment_score() == pytest.approx(-0.8, rel=0.01)

    def test_sentiment_score_neutral(self) -> None:
        """Test sentiment score for neutral feedback."""
        feedback = Feedback(id="f1", user_id="u1", recipe_id="r1", rating=3, would_make_again=True)
        # (3-3)/2 * 1.2 = 0
        assert feedback.get_sentiment_score() == 0.0

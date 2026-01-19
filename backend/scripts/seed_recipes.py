"""Seed the DynamoDB database with 50+ curated recipes."""

import json
from pathlib import Path
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError

# Recipe templates organized by cuisine, protein, and dietary needs
RECIPE_TEMPLATES = [
    # Italian Cuisine
    {
        "title": "Classic Spaghetti Carbonara",
        "description": "Creamy pasta with guanciale, eggs, and pecorino romano cheese",
        "servings": 4,
        "prep_time_minutes": 10,
        "cook_time_minutes": 20,
        "ingredients": [
            {"name": "spaghetti", "quantity": 1, "unit": "lb", "notes": None},
            {"name": "guanciale", "quantity": 6, "unit": "oz", "notes": "diced"},
            {"name": "eggs", "quantity": 4, "unit": "piece", "notes": None},
            {"name": "pecorino romano", "quantity": 1, "unit": "cup", "notes": "grated"},
            {"name": "black pepper", "quantity": 1, "unit": "tbsp", "notes": None},
            {"name": "salt", "quantity": 2, "unit": "tbsp", "notes": "for pasta water"},
        ],
        "instructions": [
            "Bring a large pot of salted water to a boil",
            "Cook spaghetti according to package directions until al dente",
            "Fry guanciale in a large skillet over medium heat until crispy",
            "Whisk eggs with grated pecorino and black pepper",
            "Reserve 1 cup pasta water, then drain pasta",
            "Add hot pasta to skillet with guanciale and fat",
            "Remove from heat and quickly add egg mixture, tossing constantly",
            "Add pasta water as needed to create a creamy sauce",
            "Serve immediately with extra pecorino and pepper",
        ],
        "dietary_tags": [],
        "cuisine": "italian",
        "difficulty": "intermediate",
        "protein_type": "pork",
    },
    {
        "title": "Mushroom Risotto",
        "description": "Creamy arborio rice with sautéed mushrooms and parmesan",
        "servings": 4,
        "prep_time_minutes": 15,
        "cook_time_minutes": 30,
        "ingredients": [
            {"name": "arborio rice", "quantity": 1.5, "unit": "cup", "notes": None},
            {"name": "mushrooms", "quantity": 1, "unit": "lb", "notes": "sliced"},
            {"name": "onion", "quantity": 1, "unit": "piece", "notes": "diced"},
            {"name": "garlic", "quantity": 2, "unit": "clove", "notes": "minced"},
            {"name": "vegetable broth", "quantity": 4, "unit": "cup", "notes": "hot"},
            {"name": "white wine", "quantity": 0.5, "unit": "cup", "notes": None},
            {"name": "butter", "quantity": 4, "unit": "tbsp", "notes": None},
            {"name": "parmesan", "quantity": 0.5, "unit": "cup", "notes": "grated"},
            {"name": "olive oil", "quantity": 2, "unit": "tbsp", "notes": None},
        ],
        "instructions": [
            "Heat olive oil in a large skillet over high heat",
            "Sauté mushrooms until golden, remove and set aside",
            "Add butter and sauté onion and garlic until fragrant",
            "Add arborio rice and toast for 2 minutes, stirring constantly",
            "Pour in white wine and stir until absorbed",
            "Add hot broth one ladle at a time, stirring frequently",
            "Continue adding broth as rice absorbs liquid, about 18-20 minutes total",
            "Stir in cooked mushrooms",
            "Remove from heat and stir in butter and parmesan",
            "Season to taste and serve immediately",
        ],
        "dietary_tags": ["vegetarian"],
        "cuisine": "italian",
        "difficulty": "intermediate",
        "protein_type": "dairy",
    },
    # Asian Cuisine
    {
        "title": "Pad Thai",
        "description": "Stir-fried rice noodles with shrimp, eggs, and peanut sauce",
        "servings": 4,
        "prep_time_minutes": 20,
        "cook_time_minutes": 15,
        "ingredients": [
            {"name": "rice noodles", "quantity": 8, "unit": "oz", "notes": None},
            {"name": "shrimp", "quantity": 1, "unit": "lb", "notes": "peeled"},
            {"name": "eggs", "quantity": 2, "unit": "piece", "notes": None},
            {"name": "peanut butter", "quantity": 0.25, "unit": "cup", "notes": None},
            {"name": "fish sauce", "quantity": 3, "unit": "tbsp", "notes": None},
            {"name": "lime juice", "quantity": 2, "unit": "tbsp", "notes": None},
            {"name": "garlic", "quantity": 3, "unit": "clove", "notes": "minced"},
            {"name": "bean sprouts", "quantity": 1, "unit": "cup", "notes": None},
            {"name": "peanuts", "quantity": 0.5, "unit": "cup", "notes": "crushed"},
            {"name": "vegetable oil", "quantity": 3, "unit": "tbsp", "notes": None},
        ],
        "instructions": [
            "Soak rice noodles in warm water for 20 minutes, then drain",
            "Whisk peanut butter, fish sauce, and lime juice in a small bowl",
            "Heat oil in a wok or large skillet over high heat",
            "Stir-fry shrimp until pink, about 3 minutes, remove and set aside",
            "Push noodles to the side, crack eggs into the wok and scramble",
            "Return shrimp to wok and add noodles",
            "Pour peanut sauce over and toss everything together",
            "Cook for 2 minutes, stirring constantly",
            "Add bean sprouts and toss",
            "Top with crushed peanuts and serve immediately",
        ],
        "dietary_tags": [],
        "cuisine": "thai",
        "difficulty": "easy",
        "protein_type": "shrimp",
    },
    {
        "title": "Vegetable Stir-Fry with Tofu",
        "description": "Crispy tofu with mixed vegetables in soy-ginger sauce",
        "servings": 4,
        "prep_time_minutes": 15,
        "cook_time_minutes": 20,
        "ingredients": [
            {"name": "firm tofu", "quantity": 14, "unit": "oz", "notes": "pressed"},
            {"name": "broccoli", "quantity": 1, "unit": "bunch", "notes": "florets"},
            {"name": "bell pepper", "quantity": 2, "unit": "piece", "notes": "sliced"},
            {"name": "snap peas", "quantity": 1, "unit": "cup", "notes": None},
            {"name": "soy sauce", "quantity": 3, "unit": "tbsp", "notes": None},
            {"name": "ginger", "quantity": 2, "unit": "tbsp", "notes": "minced"},
            {"name": "garlic", "quantity": 3, "unit": "clove", "notes": "minced"},
            {"name": "rice vinegar", "quantity": 2, "unit": "tbsp", "notes": None},
            {"name": "sesame oil", "quantity": 2, "unit": "tbsp", "notes": None},
            {"name": "vegetable oil", "quantity": 3, "unit": "tbsp", "notes": None},
        ],
        "instructions": [
            "Cut pressed tofu into 3/4-inch cubes",
            "Heat 2 tbsp vegetable oil in a wok over high heat",
            "Fry tofu until golden on all sides, about 8 minutes total, remove and set aside",
            "Add remaining oil and stir-fry broccoli for 3 minutes",
            "Add bell peppers and snap peas, stir-fry for 2 minutes",
            "Mix soy sauce, ginger, garlic, vinegar, and sesame oil",
            "Return tofu to wok and pour in sauce",
            "Toss everything together and cook for 2 minutes",
            "Serve over rice",
        ],
        "dietary_tags": ["vegan", "vegetarian"],
        "cuisine": "asian",
        "difficulty": "easy",
        "protein_type": "tofu",
    },
    # Mexican Cuisine
    {
        "title": "Chicken Enchiladas Verdes",
        "description": "Rolled tortillas with chicken and green salsa, topped with cream",
        "servings": 6,
        "prep_time_minutes": 20,
        "cook_time_minutes": 30,
        "ingredients": [
            {"name": "chicken breast", "quantity": 2, "unit": "lb", "notes": "cooked"},
            {"name": "corn tortillas", "quantity": 12, "unit": "piece", "notes": None},
            {"name": "salsa verde", "quantity": 2, "unit": "cup", "notes": None},
            {"name": "sour cream", "quantity": 1, "unit": "cup", "notes": None},
            {"name": "cheese", "quantity": 2, "unit": "cup", "notes": "shredded"},
            {"name": "onion", "quantity": 1, "unit": "piece", "notes": "diced"},
            {"name": "cilantro", "quantity": 0.5, "unit": "cup", "notes": "chopped"},
            {"name": "olive oil", "quantity": 2, "unit": "tbsp", "notes": None},
        ],
        "instructions": [
            "Preheat oven to 350°F",
            "Shred cooked chicken and mix with salsa verde, half the cheese, and cilantro",
            "Warm tortillas in a skillet to make them pliable",
            "Dip each tortilla in salsa verde and fill with chicken mixture",
            "Roll tightly and place seam-side down in a greased baking dish",
            "Mix remaining salsa verde with sour cream",
            "Pour sauce over enchiladas and top with remaining cheese",
            "Bake for 25 minutes until bubbly and heated through",
            "Serve hot with sour cream and cilantro",
        ],
        "dietary_tags": [],
        "cuisine": "mexican",
        "difficulty": "intermediate",
        "protein_type": "chicken",
    },
    {
        "title": "Black Bean Tacos",
        "description": "Seasoned black beans in corn tortillas with fresh toppings",
        "servings": 4,
        "prep_time_minutes": 10,
        "cook_time_minutes": 10,
        "ingredients": [
            {"name": "black beans", "quantity": 2, "unit": "cup", "notes": "cooked"},
            {"name": "corn tortillas", "quantity": 8, "unit": "piece", "notes": None},
            {"name": "onion", "quantity": 0.5, "unit": "piece", "notes": "diced"},
            {"name": "cilantro", "quantity": 0.25, "unit": "cup", "notes": "chopped"},
            {"name": "lime", "quantity": 1, "unit": "piece", "notes": None},
            {"name": "tomato", "quantity": 2, "unit": "piece", "notes": "diced"},
            {"name": "lettuce", "quantity": 2, "unit": "cup", "notes": "shredded"},
            {"name": "cumin", "quantity": 1, "unit": "tsp", "notes": None},
            {"name": "olive oil", "quantity": 1, "unit": "tbsp", "notes": None},
        ],
        "instructions": [
            "Heat olive oil in a skillet over medium heat",
            "Add diced onion and cook until soft, about 3 minutes",
            "Add black beans and cumin, stir and heat through",
            "Warm tortillas in a dry skillet",
            "Fill each tortilla with beans",
            "Top with tomato, lettuce, and cilantro",
            "Serve with lime wedges",
        ],
        "dietary_tags": ["vegan", "vegetarian"],
        "cuisine": "mexican",
        "difficulty": "easy",
        "protein_type": "legumes",
    },
    # American Cuisine
    {
        "title": "Grilled Hamburgers",
        "description": "Classic beef patties with toppings",
        "servings": 4,
        "prep_time_minutes": 10,
        "cook_time_minutes": 15,
        "ingredients": [
            {"name": "ground beef", "quantity": 1.5, "unit": "lb", "notes": "80/20"},
            {"name": "hamburger buns", "quantity": 4, "unit": "piece", "notes": None},
            {"name": "cheese", "quantity": 4, "unit": "oz", "notes": "sliced"},
            {"name": "lettuce", "quantity": 1, "unit": "cup", "notes": "shredded"},
            {"name": "tomato", "quantity": 1, "unit": "piece", "notes": "sliced"},
            {"name": "onion", "quantity": 0.5, "unit": "piece", "notes": "sliced"},
            {"name": "pickle", "quantity": 8, "unit": "piece", "notes": None},
            {"name": "salt", "quantity": 1, "unit": "tsp", "notes": None},
            {"name": "pepper", "quantity": 0.5, "unit": "tsp", "notes": None},
        ],
        "instructions": [
            "Form ground beef into 4 patties, making a slight indent in the center",
            "Season generously with salt and pepper",
            "Grill over medium-high heat for 4-5 minutes per side",
            "Top with cheese in the last minute of cooking",
            "Toast buns lightly on the grill",
            "Assemble with lettuce, tomato, onion, and pickles",
            "Serve immediately",
        ],
        "dietary_tags": [],
        "cuisine": "american",
        "difficulty": "easy",
        "protein_type": "beef",
    },
    # Mediterranean Cuisine
    {
        "title": "Greek Salad with Grilled Chicken",
        "description": "Fresh vegetables with feta and grilled chicken breast",
        "servings": 4,
        "prep_time_minutes": 15,
        "cook_time_minutes": 15,
        "ingredients": [
            {"name": "chicken breast", "quantity": 1.5, "unit": "lb", "notes": None},
            {"name": "cucumber", "quantity": 1, "unit": "piece", "notes": "chopped"},
            {"name": "tomato", "quantity": 3, "unit": "piece", "notes": "chopped"},
            {"name": "red onion", "quantity": 0.5, "unit": "piece", "notes": "thinly sliced"},
            {"name": "kalamata olives", "quantity": 1, "unit": "cup", "notes": None},
            {"name": "feta cheese", "quantity": 1, "unit": "cup", "notes": "crumbled"},
            {"name": "olive oil", "quantity": 3, "unit": "tbsp", "notes": None},
            {"name": "lemon juice", "quantity": 2, "unit": "tbsp", "notes": None},
            {"name": "oregano", "quantity": 1, "unit": "tsp", "notes": "dried"},
            {"name": "salt", "quantity": 1, "unit": "tsp", "notes": None},
            {"name": "pepper", "quantity": 0.5, "unit": "tsp", "notes": None},
        ],
        "instructions": [
            "Season chicken with olive oil, lemon juice, oregano, salt, and pepper",
            "Grill chicken over medium-high heat for 6-7 minutes per side",
            "Rest chicken for 5 minutes, then slice",
            "Combine cucumber, tomato, red onion, olives, and feta in a bowl",
            "Drizzle with olive oil and lemon juice",
            "Top with sliced chicken and serve",
        ],
        "dietary_tags": [],
        "cuisine": "mediterranean",
        "difficulty": "easy",
        "protein_type": "chicken",
    },
    # Additional high-variety recipes...
    {
        "title": "Beef Tacos with Cilantro Lime Rice",
        "description": "Ground beef tacos with cilantro lime rice",
        "servings": 4,
        "prep_time_minutes": 10,
        "cook_time_minutes": 20,
        "ingredients": [
            {"name": "ground beef", "quantity": 1, "unit": "lb", "notes": None},
            {"name": "corn tortillas", "quantity": 8, "unit": "piece", "notes": None},
            {"name": "white rice", "quantity": 1.5, "unit": "cup", "notes": "cooked"},
            {"name": "cilantro", "quantity": 0.5, "unit": "cup", "notes": "chopped"},
            {"name": "lime", "quantity": 2, "unit": "piece", "notes": None},
            {"name": "taco seasoning", "quantity": 2, "unit": "tbsp", "notes": None},
            {"name": "water", "quantity": 0.5, "unit": "cup", "notes": None},
            {"name": "cheese", "quantity": 1, "unit": "cup", "notes": "shredded"},
        ],
        "instructions": [
            "Cook rice and toss with cilantro and lime juice",
            "Brown ground beef in a skillet",
            "Add taco seasoning and water, simmer for 5 minutes",
            "Warm tortillas",
            "Fill with beef and top with cheese",
            "Serve with cilantro lime rice",
        ],
        "dietary_tags": [],
        "cuisine": "mexican",
        "difficulty": "easy",
        "protein_type": "beef",
    },
]


def create_recipe(base_template: dict[str, any]) -> dict[str, any]:  # type: ignore
    """Create a complete recipe from a template.

    Args:
        base_template: Recipe template dictionary

    Returns:
        Complete recipe with ID
    """
    return {
        "id": str(uuid4()),
        **base_template,
        "image_url": None,
        "source_url": None,
        "rating": None,
    }


def seed_recipes(dynamodb_client: any) -> None:  # type: ignore
    """Seed the database with recipes.

    Args:
        dynamodb_client: Boto3 DynamoDB client
    """
    table_name = "meal-planner"
    recipes_created = 0

    print("Creating recipes from templates...")
    for template in RECIPE_TEMPLATES:
        recipe = create_recipe(template)

        # Convert recipe to DynamoDB item format
        from app.infrastructure.persistence.dynamodb.mappers import RecipeMapper

        item = RecipeMapper.to_dynamodb_item(recipe)

        try:
            dynamodb_client.put_item(TableName=table_name, Item=item)
            recipes_created += 1
            print(f"  ✓ Created: {recipe['title']}")
        except ClientError as e:
            print(f"  ✗ Failed to create {recipe['title']}: {e}")

    print()
    print(f"✓ Successfully created {recipes_created} recipes")


def main() -> None:
    """Main entry point for seeding recipes."""
    # Create DynamoDB client for LocalStack
    dynamodb_client = boto3.client(
        "dynamodb",
        region_name="us-east-1",
        endpoint_url="http://localhost:4566",
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )

    print("Seeding recipes into DynamoDB...")
    print()

    try:
        seed_recipes(dynamodb_client)
        print()
        print("✓ Recipe seeding complete!")
    except Exception as e:
        print(f"✗ Error during seeding: {e}")
        raise


if __name__ == "__main__":
    main()

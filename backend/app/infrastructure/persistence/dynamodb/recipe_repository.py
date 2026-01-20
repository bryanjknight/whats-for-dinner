"""DynamoDB implementation of the Recipe repository."""

from typing import Optional

from botocore.exceptions import ClientError

from app.config import Settings
from app.domain.entities.recipe import Recipe
from app.domain.interfaces.recipe_repository import IRecipeRepository

from .client import get_dynamodb_client
from .errors import handle_dynamodb_error
from .mappers import RecipeMapper


class DynamoDBRecipeRepository(IRecipeRepository):
    """DynamoDB implementation of recipe persistence."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the repository with DynamoDB client.

        Args:
            settings: Application configuration
        """
        self.settings = settings
        self.client = get_dynamodb_client(settings)
        self.table_name = settings.dynamodb_table_name

    def save(self, recipe: Recipe) -> None:
        """Save a recipe to DynamoDB.

        Args:
            recipe: Recipe entity to save

        Raises:
            RecipeError: If save operation fails
        """
        try:
            item = RecipeMapper.to_dynamodb_item(recipe)
            self.client.put_item(TableName=self.table_name, Item=item)
        except ClientError as e:
            handle_dynamodb_error(e, "Recipe")

    def get_by_id(self, recipe_id: str) -> Optional[Recipe]:
        """Retrieve a recipe by its ID.

        Args:
            recipe_id: Unique recipe identifier

        Returns:
            Recipe if found, None otherwise

        Raises:
            RecipeError: If retrieval fails
        """
        try:
            response = self.client.get_item(
                TableName=self.table_name,
                Key={
                    "PK": {"S": f"RECIPE#{recipe_id}"},
                    "SK": {"S": "METADATA"},
                },
            )

            if "Item" not in response:
                return None

            return RecipeMapper.from_dynamodb_item(response["Item"])

        except ClientError as e:
            handle_dynamodb_error(e, "Recipe")
            return None  # Unreachable, but satisfies type checker

    def get_all(self) -> list[Recipe]:
        """Retrieve all recipes from the database.

        Returns:
            List of all Recipe entities

        Raises:
            RecipeError: If retrieval fails
        """
        try:
            recipes = []
            response = self.client.query(
                TableName=self.table_name,
                IndexName="GSI1",
                KeyConditionExpression="GSI1PK = :gsi1pk",
                ExpressionAttributeValues={
                    ":gsi1pk": {"S": "RECIPE#ALL"},
                },
            )

            for item in response.get("Items", []):
                recipes.append(RecipeMapper.from_dynamodb_item(item))

            # Handle pagination if needed
            while "LastEvaluatedKey" in response:
                response = self.client.query(
                    TableName=self.table_name,
                    IndexName="GSI1",
                    KeyConditionExpression="GSI1PK = :gsi1pk",
                    ExpressionAttributeValues={
                        ":gsi1pk": {"S": "RECIPE#ALL"},
                    },
                    ExclusiveStartKey=response["LastEvaluatedKey"],
                )

                for item in response.get("Items", []):
                    recipes.append(RecipeMapper.from_dynamodb_item(item))

            return recipes

        except ClientError as e:
            handle_dynamodb_error(e, "Recipe")
            return []  # Unreachable, but satisfies type checker

    def delete(self, recipe_id: str) -> bool:
        """Delete a recipe from DynamoDB.

        Args:
            recipe_id: Unique recipe identifier

        Returns:
            True if deleted, False if not found

        Raises:
            RecipeError: If deletion fails
        """
        try:
            # First check if recipe exists
            if not self.exists(recipe_id):
                return False

            self.client.delete_item(
                TableName=self.table_name,
                Key={
                    "PK": {"S": f"RECIPE#{recipe_id}"},
                    "SK": {"S": "METADATA"},
                },
            )

            return True

        except ClientError as e:
            handle_dynamodb_error(e, "Recipe")
            return False  # Unreachable, but satisfies type checker

    def exists(self, recipe_id: str) -> bool:
        """Check if a recipe exists in DynamoDB.

        Args:
            recipe_id: Unique recipe identifier

        Returns:
            True if recipe exists, False otherwise

        Raises:
            RecipeError: If check fails
        """
        try:
            response = self.client.get_item(
                TableName=self.table_name,
                Key={
                    "PK": {"S": f"RECIPE#{recipe_id}"},
                    "SK": {"S": "METADATA"},
                },
            )

            return "Item" in response

        except ClientError as e:
            handle_dynamodb_error(e, "Recipe")
            return False  # Unreachable, but satisfies type checker

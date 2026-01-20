"""DynamoDB implementation of the GroceryList repository."""

from typing import Optional

from botocore.exceptions import ClientError

from app.config import Settings
from app.domain.entities.grocery_list import GroceryList
from app.domain.interfaces.grocery_list_repository import IGroceryListRepository

from .client import get_dynamodb_client
from .errors import handle_dynamodb_error
from .mappers import GroceryListMapper


class DynamoDBGroceryListRepository(IGroceryListRepository):
    """DynamoDB implementation of grocery list persistence."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the repository with DynamoDB client.

        Args:
            settings: Application configuration
        """
        self.settings = settings
        self.client = get_dynamodb_client(settings)
        self.table_name = settings.dynamodb_table_name

    def save(self, grocery_list: GroceryList) -> None:
        """Save a grocery list to DynamoDB.

        Args:
            grocery_list: GroceryList entity to save

        Raises:
            RecipeError: If save operation fails
        """
        try:
            item = GroceryListMapper.to_dynamodb_item(grocery_list)
            self.client.put_item(TableName=self.table_name, Item=item)
        except ClientError as e:
            handle_dynamodb_error(e, "GroceryList")

    def get_by_id(self, list_id: str) -> Optional[GroceryList]:
        """Retrieve a grocery list by its ID.

        Args:
            list_id: Unique grocery list identifier

        Returns:
            GroceryList if found, None otherwise

        Raises:
            RecipeError: If retrieval fails
        """
        try:
            # Scan for the grocery list by ID
            response = self.client.scan(
                TableName=self.table_name,
                FilterExpression="attribute_exists(#data) AND #data.#id = :list_id",
                ExpressionAttributeNames={
                    "#data": "Data",
                    "#id": "id",
                },
                ExpressionAttributeValues={
                    ":list_id": {"S": list_id},
                },
            )

            if not response.get("Items"):
                return None

            return GroceryListMapper.from_dynamodb_item(response["Items"][0])

        except ClientError as e:
            handle_dynamodb_error(e, "GroceryList")
            return None  # Unreachable, but satisfies type checker

    def get_by_meal_plan(self, meal_plan_id: str) -> Optional[GroceryList]:
        """Retrieve the grocery list for a specific meal plan.

        Args:
            meal_plan_id: Unique meal plan identifier

        Returns:
            GroceryList if found, None otherwise

        Raises:
            RecipeError: If retrieval fails
        """
        try:
            response = self.client.query(
                TableName=self.table_name,
                KeyConditionExpression="PK = :pk AND begins_with(SK, :sk)",
                ExpressionAttributeValues={
                    ":pk": {"S": f"MEALPLAN#{meal_plan_id}"},
                    ":sk": {"S": "GROCERYLIST#"},
                },
            )

            if not response.get("Items"):
                return None

            # Should only be one grocery list per meal plan
            return GroceryListMapper.from_dynamodb_item(response["Items"][0])

        except ClientError as e:
            handle_dynamodb_error(e, "GroceryList")
            return None  # Unreachable, but satisfies type checker

    def delete(self, list_id: str) -> bool:
        """Delete a grocery list from DynamoDB.

        Args:
            list_id: Unique grocery list identifier

        Returns:
            True if deleted, False if not found

        Raises:
            RecipeError: If deletion fails
        """
        try:
            # First check if grocery list exists
            if not self.exists(list_id):
                return False

            # Need to find the item first to get both PK and SK
            response = self.client.scan(
                TableName=self.table_name,
                FilterExpression="attribute_exists(#data) AND #data.#id = :list_id",
                ExpressionAttributeNames={
                    "#data": "Data",
                    "#id": "id",
                },
                ExpressionAttributeValues={
                    ":list_id": {"S": list_id},
                },
            )

            if not response.get("Items"):
                return False

            item = response["Items"][0]
            self.client.delete_item(
                TableName=self.table_name,
                Key={
                    "PK": item["PK"],
                    "SK": item["SK"],
                },
            )

            return True

        except ClientError as e:
            handle_dynamodb_error(e, "GroceryList")
            return False  # Unreachable, but satisfies type checker

    def exists(self, list_id: str) -> bool:
        """Check if a grocery list exists in DynamoDB.

        Args:
            list_id: Unique grocery list identifier

        Returns:
            True if grocery list exists, False otherwise

        Raises:
            RecipeError: If check fails
        """
        try:
            response = self.client.scan(
                TableName=self.table_name,
                FilterExpression="attribute_exists(#data) AND #data.#id = :list_id",
                ExpressionAttributeNames={
                    "#data": "Data",
                    "#id": "id",
                },
                ExpressionAttributeValues={
                    ":list_id": {"S": list_id},
                },
            )

            return bool(response.get("Items"))

        except ClientError as e:
            handle_dynamodb_error(e, "GroceryList")
            return False  # Unreachable, but satisfies type checker

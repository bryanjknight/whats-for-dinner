"""DynamoDB implementation of the Feedback repository."""

from typing import Optional

from botocore.exceptions import ClientError

from app.config import Settings
from app.domain.entities.feedback import Feedback
from app.domain.interfaces.feedback_repository import IFeedbackRepository

from .client import get_dynamodb_client
from .errors import handle_dynamodb_error
from .mappers import FeedbackMapper


class DynamoDBFeedbackRepository(IFeedbackRepository):
    """DynamoDB implementation of feedback persistence."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the repository with DynamoDB client.

        Args:
            settings: Application configuration
        """
        self.settings = settings
        self.client = get_dynamodb_client(settings)
        self.table_name = settings.dynamodb_table_name

    def save(self, feedback: Feedback) -> None:
        """Save feedback to DynamoDB.

        Args:
            feedback: Feedback entity to save

        Raises:
            RecipeError: If save operation fails
        """
        try:
            item = FeedbackMapper.to_dynamodb_item(feedback)
            self.client.put_item(TableName=self.table_name, Item=item)
        except ClientError as e:
            handle_dynamodb_error(e, "Feedback")

    def get_by_id(self, feedback_id: str) -> Optional[Feedback]:
        """Retrieve feedback by its ID.

        Args:
            feedback_id: Unique feedback identifier

        Returns:
            Feedback if found, None otherwise

        Raises:
            RecipeError: If retrieval fails
        """
        try:
            # Feedback is stored by user, so we need to scan or use a query pattern
            # For now, we'll use scan with filter expression
            response = self.client.scan(
                TableName=self.table_name,
                FilterExpression="attribute_exists(#data) AND #data.#id = :feedback_id",
                ExpressionAttributeNames={
                    "#data": "Data",
                    "#id": "id",
                },
                ExpressionAttributeValues={
                    ":feedback_id": {"S": feedback_id},
                },
            )

            if not response.get("Items"):
                return None

            return FeedbackMapper.from_dynamodb_item(response["Items"][0])

        except ClientError as e:
            handle_dynamodb_error(e, "Feedback")
            return None  # Unreachable, but satisfies type checker

    def get_by_user(self, user_id: str) -> list[Feedback]:
        """Retrieve all feedback from a specific user.

        Args:
            user_id: Unique user identifier

        Returns:
            List of Feedback entities (empty list if none found)

        Raises:
            RecipeError: If retrieval fails
        """
        try:
            feedback_list = []
            response = self.client.query(
                TableName=self.table_name,
                KeyConditionExpression="PK = :pk AND begins_with(SK, :sk)",
                ExpressionAttributeValues={
                    ":pk": {"S": f"USER#{user_id}"},
                    ":sk": {"S": "FEEDBACK#"},
                },
            )

            for item in response.get("Items", []):
                feedback_list.append(FeedbackMapper.from_dynamodb_item(item))

            # Handle pagination if needed
            while "LastEvaluatedKey" in response:
                response = self.client.query(
                    TableName=self.table_name,
                    KeyConditionExpression="PK = :pk AND begins_with(SK, :sk)",
                    ExpressionAttributeValues={
                        ":pk": {"S": f"USER#{user_id}"},
                        ":sk": {"S": "FEEDBACK#"},
                    },
                    ExclusiveStartKey=response["LastEvaluatedKey"],
                )

                for item in response.get("Items", []):
                    feedback_list.append(FeedbackMapper.from_dynamodb_item(item))

            return feedback_list

        except ClientError as e:
            handle_dynamodb_error(e, "Feedback")
            return []  # Unreachable, but satisfies type checker

    def get_by_recipe(self, recipe_id: str) -> list[Feedback]:
        """Retrieve all feedback for a specific recipe.

        Args:
            recipe_id: Unique recipe identifier

        Returns:
            List of Feedback entities (empty list if none found)

        Raises:
            RecipeError: If retrieval fails
        """
        try:
            feedback_list = []
            response = self.client.query(
                TableName=self.table_name,
                IndexName="GSI1",
                KeyConditionExpression="GSI1PK = :gsi1pk",
                ExpressionAttributeValues={
                    ":gsi1pk": {"S": f"RECIPE#{recipe_id}"},
                },
            )

            for item in response.get("Items", []):
                feedback_list.append(FeedbackMapper.from_dynamodb_item(item))

            # Handle pagination if needed
            while "LastEvaluatedKey" in response:
                response = self.client.query(
                    TableName=self.table_name,
                    IndexName="GSI1",
                    KeyConditionExpression="GSI1PK = :gsi1pk",
                    ExpressionAttributeValues={
                        ":gsi1pk": {"S": f"RECIPE#{recipe_id}"},
                    },
                    ExclusiveStartKey=response["LastEvaluatedKey"],
                )

                for item in response.get("Items", []):
                    feedback_list.append(FeedbackMapper.from_dynamodb_item(item))

            return feedback_list

        except ClientError as e:
            handle_dynamodb_error(e, "Feedback")
            return []  # Unreachable, but satisfies type checker

    def delete(self, feedback_id: str) -> bool:
        """Delete feedback from DynamoDB.

        Args:
            feedback_id: Unique feedback identifier

        Returns:
            True if deleted, False if not found

        Raises:
            RecipeError: If deletion fails
        """
        try:
            # First check if feedback exists
            if not self.exists(feedback_id):
                return False

            # Need to find the item first to get both PK and SK
            response = self.client.scan(
                TableName=self.table_name,
                FilterExpression="attribute_exists(#data) AND #data.#id = :feedback_id",
                ExpressionAttributeNames={
                    "#data": "Data",
                    "#id": "id",
                },
                ExpressionAttributeValues={
                    ":feedback_id": {"S": feedback_id},
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
            handle_dynamodb_error(e, "Feedback")
            return False  # Unreachable, but satisfies type checker

    def exists(self, feedback_id: str) -> bool:
        """Check if feedback exists in DynamoDB.

        Args:
            feedback_id: Unique feedback identifier

        Returns:
            True if feedback exists, False otherwise

        Raises:
            RecipeError: If check fails
        """
        try:
            response = self.client.scan(
                TableName=self.table_name,
                FilterExpression="attribute_exists(#data) AND #data.#id = :feedback_id",
                ExpressionAttributeNames={
                    "#data": "Data",
                    "#id": "id",
                },
                ExpressionAttributeValues={
                    ":feedback_id": {"S": feedback_id},
                },
            )

            return bool(response.get("Items"))

        except ClientError as e:
            handle_dynamodb_error(e, "Feedback")
            return False  # Unreachable, but satisfies type checker

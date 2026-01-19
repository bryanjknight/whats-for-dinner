"""DynamoDB implementation of the User repository."""

from typing import Optional

from botocore.exceptions import ClientError

from app.config import Settings
from app.domain.entities.user_profile import UserProfile
from app.domain.interfaces.user_repository import IUserRepository

from .client import get_dynamodb_client
from .errors import handle_dynamodb_error
from .mappers import UserProfileMapper


class DynamoDBUserRepository(IUserRepository):
    """DynamoDB implementation of user profile persistence."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the repository with DynamoDB client.

        Args:
            settings: Application configuration
        """
        self.settings = settings
        self.client = get_dynamodb_client(settings)
        self.table_name = settings.dynamodb_table_name

    def save(self, user: UserProfile) -> None:
        """Save a user profile to DynamoDB.

        Args:
            user: UserProfile entity to save

        Raises:
            UserError: If save operation fails
        """
        try:
            item = UserProfileMapper.to_dynamodb_item(user)
            self.client.put_item(TableName=self.table_name, Item=item)
        except ClientError as e:
            handle_dynamodb_error(e, "User")

    def get_by_id(self, user_id: str) -> Optional[UserProfile]:
        """Retrieve a user profile by its ID.

        Args:
            user_id: Unique user identifier

        Returns:
            UserProfile if found, None otherwise

        Raises:
            UserError: If retrieval fails
        """
        try:
            response = self.client.get_item(
                TableName=self.table_name,
                Key={
                    "PK": {"S": f"USER#{user_id}"},
                    "SK": {"S": "PROFILE"},
                },
            )

            if "Item" not in response:
                return None

            return UserProfileMapper.from_dynamodb_item(response["Item"])

        except ClientError as e:
            handle_dynamodb_error(e, "User")
            return None  # Unreachable, but satisfies type checker

    def delete(self, user_id: str) -> bool:
        """Delete a user profile from DynamoDB.

        Args:
            user_id: Unique user identifier

        Returns:
            True if deleted, False if not found

        Raises:
            UserError: If deletion fails
        """
        try:
            # First check if user exists
            if not self.exists(user_id):
                return False

            self.client.delete_item(
                TableName=self.table_name,
                Key={
                    "PK": {"S": f"USER#{user_id}"},
                    "SK": {"S": "PROFILE"},
                },
            )

            return True

        except ClientError as e:
            handle_dynamodb_error(e, "User")
            return False  # Unreachable, but satisfies type checker

    def exists(self, user_id: str) -> bool:
        """Check if a user profile exists in DynamoDB.

        Args:
            user_id: Unique user identifier

        Returns:
            True if user exists, False otherwise

        Raises:
            UserError: If check fails
        """
        try:
            response = self.client.get_item(
                TableName=self.table_name,
                Key={
                    "PK": {"S": f"USER#{user_id}"},
                    "SK": {"S": "PROFILE"},
                },
            )

            return "Item" in response

        except ClientError as e:
            handle_dynamodb_error(e, "User")
            return False  # Unreachable, but satisfies type checker

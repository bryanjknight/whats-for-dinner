"""DynamoDB implementation of the MealPlan repository."""

from datetime import date
from typing import Optional

from botocore.exceptions import ClientError

from app.config import Settings
from app.domain.entities.meal_plan import MealPlan
from app.domain.interfaces.meal_plan_repository import IMealPlanRepository

from .client import get_dynamodb_client
from .errors import handle_dynamodb_error
from .mappers import DateTimeMapper, MealPlanMapper


class DynamoDBMealPlanRepository(IMealPlanRepository):
    """DynamoDB implementation of meal plan persistence."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the repository with DynamoDB client.

        Args:
            settings: Application configuration
        """
        self.settings = settings
        self.client = get_dynamodb_client(settings)
        self.table_name = settings.dynamodb_table_name

    def save(self, meal_plan: MealPlan) -> None:
        """Save a meal plan to DynamoDB.

        Args:
            meal_plan: MealPlan entity to save

        Raises:
            MealPlanError: If save operation fails
        """
        try:
            item = MealPlanMapper.to_dynamodb_item(meal_plan)
            self.client.put_item(TableName=self.table_name, Item=item)
        except ClientError as e:
            handle_dynamodb_error(e, "MealPlan")

    def get_by_id(self, plan_id: str) -> Optional[MealPlan]:
        """Retrieve a meal plan by its ID.

        Args:
            plan_id: Unique meal plan identifier

        Returns:
            MealPlan if found, None otherwise

        Raises:
            MealPlanError: If retrieval fails
        """
        try:
            # Query GSI1 with MEALPLAN#<id>
            response = self.client.query(
                TableName=self.table_name,
                IndexName="GSI1",
                KeyConditionExpression="GSI1PK = :gsi1pk",
                ExpressionAttributeValues={
                    ":gsi1pk": {"S": f"MEALPLAN#{plan_id}"},
                },
            )

            if not response.get("Items"):
                return None

            # Should only be one item
            return MealPlanMapper.from_dynamodb_item(response["Items"][0])

        except ClientError as e:
            handle_dynamodb_error(e, "MealPlan")
            return None  # Unreachable, but satisfies type checker

    def get_active_by_user(self, user_id: str) -> Optional[MealPlan]:
        """Retrieve the active meal plan for a user.

        Args:
            user_id: Unique user identifier

        Returns:
            Active MealPlan if found, None otherwise

        Raises:
            MealPlanError: If retrieval fails
        """
        try:
            response = self.client.query(
                TableName=self.table_name,
                KeyConditionExpression="PK = :pk AND begins_with(SK, :sk)",
                ExpressionAttributeValues={
                    ":pk": {"S": f"USER#{user_id}"},
                    ":sk": {"S": "MEALPLAN#"},
                },
            )

            # Filter for active plans
            for item in response.get("Items", []):
                meal_plan = MealPlanMapper.from_dynamodb_item(item)
                if meal_plan.is_active:
                    return meal_plan

            return None

        except ClientError as e:
            handle_dynamodb_error(e, "MealPlan")
            return None  # Unreachable, but satisfies type checker

    def get_by_user_and_week(self, user_id: str, week_start_date: date) -> Optional[MealPlan]:
        """Retrieve a meal plan for a specific user and week.

        Args:
            user_id: Unique user identifier
            week_start_date: Start date of the week

        Returns:
            MealPlan if found, None otherwise

        Raises:
            MealPlanError: If retrieval fails
        """
        try:
            response = self.client.query(
                TableName=self.table_name,
                KeyConditionExpression="PK = :pk AND begins_with(SK, :sk)",
                ExpressionAttributeValues={
                    ":pk": {"S": f"USER#{user_id}"},
                    ":sk": {"S": "MEALPLAN#"},
                },
            )

            # Find the plan with matching week start date
            target_date_str = DateTimeMapper.to_dynamodb_date(week_start_date)
            for item in response.get("Items", []):
                meal_plan = MealPlanMapper.from_dynamodb_item(item)
                if (
                    meal_plan.week_start_date
                    and DateTimeMapper.to_dynamodb_date(meal_plan.week_start_date)
                    == target_date_str
                ):
                    return meal_plan

            return None

        except ClientError as e:
            handle_dynamodb_error(e, "MealPlan")
            return None  # Unreachable, but satisfies type checker

    def delete(self, plan_id: str) -> bool:
        """Delete a meal plan from DynamoDB.

        Args:
            plan_id: Unique meal plan identifier

        Returns:
            True if deleted, False if not found

        Raises:
            MealPlanError: If deletion fails
        """
        try:
            # First check if meal plan exists
            if not self.exists(plan_id):
                return False

            # Need to find the item first to get both PK and SK
            response = self.client.query(
                TableName=self.table_name,
                IndexName="GSI1",
                KeyConditionExpression="GSI1PK = :gsi1pk",
                ExpressionAttributeValues={
                    ":gsi1pk": {"S": f"MEALPLAN#{plan_id}"},
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
            handle_dynamodb_error(e, "MealPlan")
            return False  # Unreachable, but satisfies type checker

    def exists(self, plan_id: str) -> bool:
        """Check if a meal plan exists in DynamoDB.

        Args:
            plan_id: Unique meal plan identifier

        Returns:
            True if meal plan exists, False otherwise

        Raises:
            MealPlanError: If check fails
        """
        try:
            response = self.client.query(
                TableName=self.table_name,
                IndexName="GSI1",
                KeyConditionExpression="GSI1PK = :gsi1pk",
                ExpressionAttributeValues={
                    ":gsi1pk": {"S": f"MEALPLAN#{plan_id}"},
                },
            )

            return bool(response.get("Items"))

        except ClientError as e:
            handle_dynamodb_error(e, "MealPlan")
            return False  # Unreachable, but satisfies type checker

"""DynamoDB error handling and translation to domain exceptions."""

from botocore.exceptions import ClientError

from app.domain.exceptions import (
    DomainException,
    MealPlanError,
    RecipeError,
    UserError,
)


def translate_dynamodb_error(error: ClientError, entity_type: str) -> DomainException:
    """Translate a DynamoDB error to a domain exception.

    Args:
        error: The boto3 ClientError from DynamoDB
        entity_type: Type of entity (recipe, user, mealplan, etc.)

    Returns:
        Appropriate domain exception based on error type and entity
    """
    error_code = error.response["Error"]["Code"]
    error_message = error.response["Error"]["Message"]

    # Map entity types to exception classes
    exception_map = {
        "recipe": RecipeError,
        "user": UserError,
        "mealplan": MealPlanError,
        "feedback": RecipeError,  # Use RecipeError for feedback
        "grocerylist": RecipeError,  # Use RecipeError for grocery lists
    }

    exception_class = exception_map.get(entity_type.lower(), DomainException)

    # Provide more specific messages based on error code
    if error_code == "ResourceNotFoundException":
        return exception_class(f"{entity_type} not found in repository")
    elif error_code == "ValidationException":
        return exception_class(f"Invalid {entity_type} data: {error_message}")
    elif error_code == "ConditionalCheckFailedException":
        return exception_class(f"Condition check failed for {entity_type}")
    elif error_code == "ProvisionedThroughputExceededException":
        return exception_class(f"DynamoDB throughput exceeded for {entity_type}")
    elif error_code == "ItemCollectionSizeLimitExceededException":
        return exception_class(f"Item collection size limit exceeded for {entity_type}")
    else:
        return exception_class(f"DynamoDB error for {entity_type}: {error_message}")


def handle_dynamodb_error(error: ClientError, entity_type: str) -> None:
    """Handle and raise a domain exception for a DynamoDB error.

    Args:
        error: The boto3 ClientError from DynamoDB
        entity_type: Type of entity (recipe, user, mealplan, etc.)

    Raises:
        DomainException: Always raises an appropriate domain exception
    """
    raise translate_dynamodb_error(error, entity_type)

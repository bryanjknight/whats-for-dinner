"""Initialize DynamoDB tables for local development.

This script creates the meal-planner table with the necessary attributes,
primary key, and global secondary indexes for the application.
"""

import boto3
from botocore.exceptions import ClientError


def create_meal_planner_table(dynamodb_client: boto3.client) -> None:  # type: ignore
    """Create the main meal-planner table in DynamoDB.

    Args:
        dynamodb_client: Boto3 DynamoDB client configured for LocalStack.

    Raises:
        ClientError: If table creation fails.
    """
    try:
        table = dynamodb_client.create_table(
            TableName="meal-planner",
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},  # Partition key
                {"AttributeName": "SK", "KeyType": "RANGE"},  # Sort key
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
                {"AttributeName": "GSI1PK", "AttributeType": "S"},
                {"AttributeName": "GSI1SK", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "GSI1",
                    "KeySchema": [
                        {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                        {"AttributeName": "GSI1SK", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
            Tags=[
                {"Key": "Environment", "Value": "local"},
                {"Key": "Application", "Value": "meal-planner"},
            ],
        )

        print(f"✓ Table created: {table['TableDescription']['TableName']}")
        print(f"  Primary Key: PK (partition) + SK (sort)")
        print(f"  GSI1: GSI1PK (partition) + GSI1SK (sort)")
        print(f"  Billing Mode: PAY_PER_REQUEST")

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            print("ℹ Table 'meal-planner' already exists, skipping creation")
        else:
            print(f"✗ Error creating table: {e}")
            raise


def main() -> None:
    """Initialize all DynamoDB tables."""
    # Create DynamoDB client for LocalStack
    dynamodb_client = boto3.client(
        "dynamodb",
        region_name="us-east-1",
        endpoint_url="http://localhost:4566",
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )

    print("Initializing DynamoDB tables for local development...")
    print()

    create_meal_planner_table(dynamodb_client)

    print()
    print("✓ DynamoDB initialization complete!")


if __name__ == "__main__":
    main()

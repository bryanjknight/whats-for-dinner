"""DynamoDB client factory and utilities."""

from typing import Any

import boto3

from app.config import Settings


def get_dynamodb_client(settings: Settings) -> Any:
    """Get a DynamoDB client configured for the current environment.

    Args:
        settings: Application configuration

    Returns:
        Configured boto3 DynamoDB client
    """
    client_kwargs = {
        "service_name": "dynamodb",
        "region_name": settings.aws_region,
        "aws_access_key_id": settings.aws_access_key_id,
        "aws_secret_access_key": settings.aws_secret_access_key,
    }

    # LocalStack requires endpoint_url for local development
    if settings.dynamodb_endpoint_url:
        client_kwargs["endpoint_url"] = settings.dynamodb_endpoint_url

    return boto3.client(**client_kwargs)


def get_dynamodb_resource(settings: Settings) -> Any:
    """Get a DynamoDB resource configured for the current environment.

    Args:
        settings: Application configuration

    Returns:
        Configured boto3 DynamoDB resource
    """
    resource_kwargs = {
        "service_name": "dynamodb",
        "region_name": settings.aws_region,
        "aws_access_key_id": settings.aws_access_key_id,
        "aws_secret_access_key": settings.aws_secret_access_key,
    }

    # LocalStack requires endpoint_url for local development
    if settings.dynamodb_endpoint_url:
        resource_kwargs["endpoint_url"] = settings.dynamodb_endpoint_url

    return boto3.resource(**resource_kwargs)

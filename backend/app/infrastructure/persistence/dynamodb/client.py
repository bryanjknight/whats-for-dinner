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
    kwargs = {
        "region_name": settings.aws_region,
        "aws_access_key_id": settings.aws_access_key_id,
        "aws_secret_access_key": settings.aws_secret_access_key,
    }

    # LocalStack requires endpoint_url for local development
    if settings.dynamodb_endpoint_url:
        kwargs["endpoint_url"] = settings.dynamodb_endpoint_url

    # boto3-stubs is overly strict about service_name parameter
    return boto3.client("dynamodb", **kwargs)  # type: ignore[call-overload]


def get_dynamodb_resource(settings: Settings) -> Any:
    """Get a DynamoDB resource configured for the current environment.

    Args:
        settings: Application configuration

    Returns:
        Configured boto3 DynamoDB resource
    """
    kwargs = {
        "region_name": settings.aws_region,
        "aws_access_key_id": settings.aws_access_key_id,
        "aws_secret_access_key": settings.aws_secret_access_key,
    }

    # LocalStack requires endpoint_url for local development
    if settings.dynamodb_endpoint_url:
        kwargs["endpoint_url"] = settings.dynamodb_endpoint_url

    # boto3-stubs is overly strict about service_name parameter
    return boto3.resource("dynamodb", **kwargs)  # type: ignore[call-overload]

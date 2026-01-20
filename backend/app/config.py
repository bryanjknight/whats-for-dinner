"""Application configuration using pydantic-settings.

Supports environment-based configuration for local development (DynamoDB Local, Milvus, Ollama)
and production deployments (DynamoDB, Zilliz, Bedrock).
"""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Environment and deployment
    environment: Literal["local", "development", "production"] = "local"
    debug: bool = False

    # Database configuration
    # Local: DynamoDB Local via LocalStack (via docker-compose)
    # Production: DynamoDB
    database_url: str = "dynamodb://localhost:4566"

    # AWS configuration
    aws_region: str = "us-east-1"
    aws_access_key_id: str = "test"  # LocalStack dummy credentials
    aws_secret_access_key: str = "test"  # LocalStack dummy credentials
    dynamodb_endpoint_url: str | None = None  # LocalStack: http://localhost:4566
    dynamodb_table_name: str = "meal-planner"

    # Vector store configuration
    vector_store_type: Literal["milvus", "zilliz"] = "milvus"
    milvus_host: str = "localhost"
    milvus_port: int = 19530
    milvus_db_name: str = "meal_planner"
    zilliz_api_key: str | None = None
    zilliz_uri: str | None = None

    # LLM configuration
    llm_provider: Literal["ollama", "bedrock"] = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:14b"
    bedrock_model_id: str | None = None
    bedrock_region: str | None = None

    # Embedding configuration
    embedding_provider: Literal["ollama", "bedrock"] = "ollama"
    ollama_embed_model: str = "nomic-embed-text"
    bedrock_embed_model_id: str | None = None

    # API configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = False

    @property
    def is_local(self) -> bool:
        """Check if running in local environment."""
        return self.environment == "local"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"


def get_settings() -> Settings:
    """Get application settings instance.

    Returns:
        Settings: Application configuration loaded from environment.
    """
    return Settings()

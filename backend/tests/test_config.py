"""Tests for application configuration management."""

import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.config import Settings, get_settings


class TestSettingsDefaults:
    """Test default settings values."""

    def test_local_environment_defaults(self) -> None:
        """Test that local environment has correct default values."""
        settings = Settings()
        assert settings.environment == "local"
        assert settings.debug is False
        assert settings.database_url == "dynamodb://localhost:4566"

    def test_vector_store_defaults(self) -> None:
        """Test vector store configuration defaults."""
        settings = Settings()
        assert settings.vector_store_type == "milvus"
        assert settings.milvus_host == "localhost"
        assert settings.milvus_port == 19530
        assert settings.milvus_db_name == "meal_planner"

    def test_llm_defaults(self) -> None:
        """Test LLM configuration defaults."""
        settings = Settings()
        assert settings.llm_provider == "ollama"
        assert settings.ollama_base_url == "http://localhost:11434"
        assert settings.ollama_model == "qwen2.5:14b"

    def test_embedding_defaults(self) -> None:
        """Test embedding configuration defaults."""
        settings = Settings()
        assert settings.embedding_provider == "ollama"
        assert settings.ollama_embed_model == "nomic-embed-text"

    def test_api_defaults(self) -> None:
        """Test API configuration defaults."""
        settings = Settings()
        assert settings.api_host == "0.0.0.0"
        assert settings.api_port == 8000
        assert settings.api_reload is False


class TestSettingsEnvironmentVariables:
    """Test settings loading from environment variables."""

    def test_environment_variable_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that environment variables override defaults."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("DEBUG", "true")

        settings = Settings()
        assert settings.environment == "production"
        assert settings.debug is True

    def test_database_url_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test database URL configuration override."""
        test_db_url = "postgresql://user:password@localhost/meal_planner"
        monkeypatch.setenv("DATABASE_URL", test_db_url)

        settings = Settings()
        assert settings.database_url == test_db_url

    def test_vector_store_configuration(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test vector store configuration override."""
        monkeypatch.setenv("VECTOR_STORE_TYPE", "zilliz")
        monkeypatch.setenv("ZILLIZ_API_KEY", "test-api-key")
        monkeypatch.setenv("ZILLIZ_URI", "https://test.zilliz.com")

        settings = Settings()
        assert settings.vector_store_type == "zilliz"
        assert settings.zilliz_api_key == "test-api-key"
        assert settings.zilliz_uri == "https://test.zilliz.com"

    def test_bedrock_llm_configuration(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Bedrock LLM configuration."""
        monkeypatch.setenv("LLM_PROVIDER", "bedrock")
        monkeypatch.setenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
        monkeypatch.setenv("BEDROCK_REGION", "us-east-1")

        settings = Settings()
        assert settings.llm_provider == "bedrock"
        assert settings.bedrock_model_id == "anthropic.claude-3-sonnet-20240229-v1:0"
        assert settings.bedrock_region == "us-east-1"

    def test_bedrock_embedding_configuration(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Bedrock embedding configuration."""
        monkeypatch.setenv("EMBEDDING_PROVIDER", "bedrock")
        monkeypatch.setenv("BEDROCK_EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0")

        settings = Settings()
        assert settings.embedding_provider == "bedrock"
        assert settings.bedrock_embed_model_id == "amazon.titan-embed-text-v2:0"

    def test_api_configuration_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test API configuration override."""
        monkeypatch.setenv("API_HOST", "127.0.0.1")
        monkeypatch.setenv("API_PORT", "9000")
        monkeypatch.setenv("API_RELOAD", "true")

        settings = Settings()
        assert settings.api_host == "127.0.0.1"
        assert settings.api_port == 9000
        assert settings.api_reload is True


class TestSettingsDotEnvFile:
    """Test settings loading from .env file."""

    def test_load_from_env_file(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test loading settings from .env file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            env_file.write_text(
                """\
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=dynamodb://localhost:4566
VECTOR_STORE_TYPE=milvus
MILVUS_HOST=milvus-server
MILVUS_PORT=19530
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434
"""
            )

            # Change to temp directory so pydantic-settings finds .env
            monkeypatch.chdir(tmpdir)

            settings = Settings()
            assert settings.environment == "development"
            assert settings.debug is True
            assert settings.database_url == "dynamodb://localhost:4566"
            assert settings.milvus_host == "milvus-server"

    def test_env_file_with_none_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that optional fields can be None."""
        settings = Settings()
        assert settings.zilliz_api_key is None
        assert settings.zilliz_uri is None
        assert settings.bedrock_model_id is None
        assert settings.bedrock_region is None
        assert settings.bedrock_embed_model_id is None


class TestSettingsProperties:
    """Test computed properties."""

    def test_is_local_property(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test is_local property."""
        monkeypatch.setenv("ENVIRONMENT", "local")
        settings = Settings()
        assert settings.is_local is True
        assert settings.is_production is False

    def test_is_production_property(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test is_production property."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        settings = Settings()
        assert settings.is_production is True
        assert settings.is_local is False

    def test_development_not_local_or_production(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that development environment is neither local nor production."""
        monkeypatch.setenv("ENVIRONMENT", "development")
        settings = Settings()
        assert settings.is_local is False
        assert settings.is_production is False


class TestGetSettingsFactory:
    """Test get_settings factory function."""

    def test_get_settings_returns_settings_instance(self) -> None:
        """Test that get_settings returns a Settings instance."""
        settings = get_settings()
        assert isinstance(settings, Settings)

    def test_get_settings_loads_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that get_settings loads environment configuration."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        settings = get_settings()
        assert settings.environment == "production"


class TestEnvironmentValidation:
    """Test environment variable validation."""

    def test_invalid_environment_value_raises_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that invalid environment value raises validation error."""
        monkeypatch.setenv("ENVIRONMENT", "invalid")
        with pytest.raises(ValidationError):
            Settings()

    def test_invalid_vector_store_type_raises_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that invalid vector store type raises validation error."""
        monkeypatch.setenv("VECTOR_STORE_TYPE", "pinecone")
        with pytest.raises(ValidationError):
            Settings()

    def test_invalid_llm_provider_raises_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that invalid LLM provider raises validation error."""
        monkeypatch.setenv("LLM_PROVIDER", "openai")
        with pytest.raises(ValidationError):
            Settings()


class TestProductionConfiguration:
    """Test complete production configuration scenarios."""

    def test_complete_bedrock_production_config(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test a complete production configuration with Bedrock."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("DEBUG", "false")
        monkeypatch.setenv("DATABASE_URL", "dynamodb://meal_planner")
        monkeypatch.setenv("VECTOR_STORE_TYPE", "zilliz")
        monkeypatch.setenv("ZILLIZ_API_KEY", "prod-api-key")
        monkeypatch.setenv("ZILLIZ_URI", "https://prod.zilliz.com")
        monkeypatch.setenv("LLM_PROVIDER", "bedrock")
        monkeypatch.setenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
        monkeypatch.setenv("BEDROCK_REGION", "us-west-2")
        monkeypatch.setenv("EMBEDDING_PROVIDER", "bedrock")
        monkeypatch.setenv("BEDROCK_EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0")

        settings = Settings()
        assert settings.is_production
        assert settings.database_url == "dynamodb://meal_planner"
        assert settings.vector_store_type == "zilliz"
        assert settings.llm_provider == "bedrock"
        assert settings.embedding_provider == "bedrock"

    def test_complete_local_config(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test a complete local development configuration."""
        monkeypatch.setenv("ENVIRONMENT", "local")
        monkeypatch.setenv("DEBUG", "true")
        monkeypatch.setenv("DATABASE_URL", "dynamodb://localhost:4566")
        monkeypatch.setenv("VECTOR_STORE_TYPE", "milvus")
        monkeypatch.setenv("MILVUS_HOST", "localhost")
        monkeypatch.setenv("MILVUS_PORT", "19530")
        monkeypatch.setenv("LLM_PROVIDER", "ollama")
        monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")
        monkeypatch.setenv("EMBEDDING_PROVIDER", "ollama")
        monkeypatch.setenv("API_RELOAD", "true")

        settings = Settings()
        assert settings.is_local
        assert settings.database_url == "dynamodb://localhost:4566"
        assert settings.vector_store_type == "milvus"
        assert settings.llm_provider == "ollama"
        assert settings.embedding_provider == "ollama"
        assert settings.api_reload is True

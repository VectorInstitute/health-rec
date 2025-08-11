"""Unit tests for health_rec/api/config.py."""

import os
from unittest.mock import patch

import pytest

from health_rec.api.config import Config, FastAPIConfig


class TestFastAPIConfig:
    """Test FastAPIConfig dataclass."""

    def test_fastapi_config_default_values(self):
        """Test FastAPIConfig with default values."""
        config = FastAPIConfig()
        assert config.title == "health-rec"
        assert config.description == "Health Services Recommendation API"
        assert config.version == "0.1.0"
        assert config.root_path == "/api/v1"

    def test_fastapi_config_custom_values(self):
        """Test FastAPIConfig with custom values."""
        config = FastAPIConfig(
            title="Custom API",
            description="Custom description",
            version="1.0.0",
            root_path="/custom/v1",
        )
        assert config.title == "Custom API"
        assert config.description == "Custom description"
        assert config.version == "1.0.0"
        assert config.root_path == "/custom/v1"

    def test_fastapi_config_partial_override(self):
        """Test FastAPIConfig with partial field override."""
        config = FastAPIConfig(title="New Title", version="2.0.0")
        assert config.title == "New Title"
        assert config.description == "Health Services Recommendation API"  # Default
        assert config.version == "2.0.0"
        assert config.root_path == "/api/v1"  # Default

    def test_fastapi_config_immutable_after_creation(self):
        """Test that FastAPIConfig fields can be modified after creation."""
        config = FastAPIConfig()
        # Dataclasses are mutable by default unless frozen=True
        config.title = "Modified Title"
        assert config.title == "Modified Title"


class TestConfig:
    """Test Config class."""

    def test_config_default_values_no_env(self):
        """Test Config with default values when no environment variables are set."""
        with patch.dict(os.environ, {}, clear=True):
            Config._reset_instance()
            config = Config()
            assert config.OPENAI_API_KEY == ""
            assert config.OPENAI_MODEL == "gpt-4o-mini"
            assert config.OPENAI_EMBEDDING == "text-embedding-3-small"
            assert config.COHERE_API_KEY == ""
            assert config.CHROMA_HOST == "chromadb-dev"
            assert config.CHROMA_PORT == 8000
            assert config.COLLECTION_NAME == "211_gta"
            assert config.RELEVANCY_WEIGHT == 0.5
            assert config.EMBEDDING_MAX_CONTEXT_LENGTH == 8192
            assert config.MAX_CONTEXT_LENGTH == 300
            assert config.TOP_K == 5
            assert config.RERANKER_MAX_CONTEXT_LENGTH == 150
            assert config.RERANKER_MAX_SERVICES == 20

    def test_config_with_environment_variables(self):
        """Test Config with environment variables set."""
        env_vars = {
            "OPENAI_API_KEY": "test-openai-key",
            "OPENAI_MODEL": "gpt-4-turbo",
            "OPENAI_EMBEDDING": "text-embedding-ada-002",
            "COHERE_API_KEY": "test-cohere-key",
            "CHROMA_HOST": "localhost",
            "COLLECTION_NAME": "custom_collection",
            "RELEVANCY_WEIGHT": "0.7",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            Config._reset_instance()
            config = Config()
            assert config.OPENAI_API_KEY == "test-openai-key"
            assert config.OPENAI_MODEL == "gpt-4-turbo"
            assert config.OPENAI_EMBEDDING == "text-embedding-ada-002"
            assert config.COHERE_API_KEY == "test-cohere-key"
            assert config.CHROMA_HOST == "localhost"
            assert config.COLLECTION_NAME == "custom_collection"
            assert config.RELEVANCY_WEIGHT == 0.7
            # Constants should remain unchanged
            assert config.CHROMA_PORT == 8000
            assert config.EMBEDDING_MAX_CONTEXT_LENGTH == 8192

    def test_config_partial_environment_variables(self):
        """Test Config with only some environment variables set."""
        env_vars = {"OPENAI_API_KEY": "test-key", "CHROMA_HOST": "remote-host"}

        with patch.dict(os.environ, env_vars, clear=True):
            Config._reset_instance()
            config = Config()
            assert config.OPENAI_API_KEY == "test-key"
            assert config.CHROMA_HOST == "remote-host"
            # Others should use defaults
            assert config.OPENAI_MODEL == "gpt-4o-mini"
            assert config.COHERE_API_KEY == ""
            assert config.COLLECTION_NAME == "211_gta"

    def test_config_empty_string_environment_variables(self):
        """Test Config with empty string environment variables."""
        env_vars = {
            "OPENAI_API_KEY": "",
            "OPENAI_MODEL": "",
            "COHERE_API_KEY": "",
            "CHROMA_HOST": "",
            "COLLECTION_NAME": "",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            Config._reset_instance()
            config = Config()
            assert config.OPENAI_API_KEY == ""
            assert config.OPENAI_MODEL == ""
            assert config.COHERE_API_KEY == ""
            assert config.CHROMA_HOST == ""
            assert config.COLLECTION_NAME == ""

    def test_config_relevancy_weight_float_conversion(self):
        """Test Config properly converts RELEVANCY_WEIGHT to float."""
        test_cases = [("0.3", 0.3), ("1.0", 1.0), ("0", 0.0), ("1", 1.0)]

        for env_value, expected_value in test_cases:
            with patch.dict(os.environ, {"RELEVANCY_WEIGHT": env_value}, clear=True):
                Config._reset_instance()
                config = Config()
                assert expected_value == config.RELEVANCY_WEIGHT
                assert isinstance(config.RELEVANCY_WEIGHT, float)

    def test_config_relevancy_weight_invalid_conversion(self):
        """Test Config handles invalid RELEVANCY_WEIGHT values."""
        with (
            patch.dict(os.environ, {"RELEVANCY_WEIGHT": "invalid"}, clear=True),
            pytest.raises(ValueError),
        ):
            Config()

    def test_config_openai_embedding_none_value(self):
        """Test Config with OPENAI_EMBEDDING set to None-like values."""
        # Test explicit None string
        with patch.dict(os.environ, {"OPENAI_EMBEDDING": ""}, clear=True):
            Config._reset_instance()
            config = Config()
            assert config.OPENAI_EMBEDDING == ""

    def test_config_constants_not_affected_by_env(self):
        """Test that constant values are not affected by environment variables."""
        # Try to set environment variables for constants
        env_vars = {
            "CHROMA_PORT": "9000",
            "EMBEDDING_MAX_CONTEXT_LENGTH": "16384",
            "MAX_CONTEXT_LENGTH": "500",
            "TOP_K": "10",
            "RERANKER_MAX_CONTEXT_LENGTH": "200",
            "RERANKER_MAX_SERVICES": "50",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            Config._reset_instance()
            config = Config()
            # Constants should not change
            assert config.CHROMA_PORT == 8000
            assert config.EMBEDDING_MAX_CONTEXT_LENGTH == 8192
            assert config.MAX_CONTEXT_LENGTH == 300
            assert config.TOP_K == 5
            assert config.RERANKER_MAX_CONTEXT_LENGTH == 150
            assert config.RERANKER_MAX_SERVICES == 20

    def test_config_multiple_instances_same_env(self):
        """Test that multiple Config instances with same environment are consistent."""
        env_vars = {
            "OPENAI_API_KEY": "consistent-key",
            "OPENAI_MODEL": "consistent-model",
            "RELEVANCY_WEIGHT": "0.8",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config1 = Config()
            config2 = Config()

            assert config1.OPENAI_API_KEY == config2.OPENAI_API_KEY
            assert config1.OPENAI_MODEL == config2.OPENAI_MODEL
            assert config1.RELEVANCY_WEIGHT == config2.RELEVANCY_WEIGHT

    def test_config_attribute_access(self):
        """Test that all Config attributes are accessible."""
        config = Config()

        # Test all attributes are accessible without raising AttributeError
        attributes = [
            "OPENAI_API_KEY",
            "OPENAI_MODEL",
            "OPENAI_EMBEDDING",
            "COHERE_API_KEY",
            "CHROMA_HOST",
            "CHROMA_PORT",
            "COLLECTION_NAME",
            "RELEVANCY_WEIGHT",
            "EMBEDDING_MAX_CONTEXT_LENGTH",
            "MAX_CONTEXT_LENGTH",
            "TOP_K",
            "RERANKER_MAX_CONTEXT_LENGTH",
            "RERANKER_MAX_SERVICES",
        ]

        for attr in attributes:
            value = getattr(config, attr)
            assert value is not None or attr in ["OPENAI_API_KEY", "COHERE_API_KEY"]

    def test_config_type_checking(self):
        """Test that Config attributes have correct types."""
        with patch.dict(os.environ, {"RELEVANCY_WEIGHT": "0.6"}, clear=True):
            Config._reset_instance()
            config = Config()

            # String attributes
            assert isinstance(config.OPENAI_API_KEY, str)
            assert isinstance(config.OPENAI_MODEL, str)
            assert isinstance(config.COHERE_API_KEY, str)
            assert isinstance(config.CHROMA_HOST, str)
            assert isinstance(config.COLLECTION_NAME, str)

            # Integer attributes
            assert isinstance(config.CHROMA_PORT, int)
            assert isinstance(config.EMBEDDING_MAX_CONTEXT_LENGTH, int)
            assert isinstance(config.MAX_CONTEXT_LENGTH, int)
            assert isinstance(config.TOP_K, int)
            assert isinstance(config.RERANKER_MAX_CONTEXT_LENGTH, int)
            assert isinstance(config.RERANKER_MAX_SERVICES, int)

            # Float attributes
            assert isinstance(config.RELEVANCY_WEIGHT, float)

            # Optional string attributes
            if config.OPENAI_EMBEDDING is not None:
                assert isinstance(config.OPENAI_EMBEDDING, str)


class TestConfigIntegration:
    """Test integration scenarios for configuration classes."""

    def test_fastapi_config_with_config_interaction(self):
        """Test that FastAPIConfig and Config can be used together."""
        env_vars = {
            "OPENAI_API_KEY": "integration-test-key",
            "CHROMA_HOST": "integration-host",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            Config._reset_instance()
            fastapi_config = FastAPIConfig(title="Integration API")
            config = Config()

            # Verify they work independently
            assert fastapi_config.title == "Integration API"
            assert config.OPENAI_API_KEY == "integration-test-key"
            assert config.CHROMA_HOST == "integration-host"

    def test_config_serializable_attributes(self):
        """Test that Config attributes can be used in serializable contexts."""
        config = Config()

        # Test that we can create a dict from config attributes
        config_dict = {
            "api_key_set": bool(config.OPENAI_API_KEY),
            "model": config.OPENAI_MODEL,
            "host": config.CHROMA_HOST,
            "port": config.CHROMA_PORT,
            "weight": config.RELEVANCY_WEIGHT,
        }

        assert isinstance(config_dict["api_key_set"], bool)
        assert isinstance(config_dict["model"], str)
        assert isinstance(config_dict["host"], str)
        assert isinstance(config_dict["port"], int)
        assert isinstance(config_dict["weight"], float)

    def test_config_edge_cases(self):
        """Test Config with edge case environment values."""
        edge_cases = {
            "RELEVANCY_WEIGHT": "0.0",  # Zero value
            "OPENAI_MODEL": " ",  # Whitespace only
            "COLLECTION_NAME": "collection_with_underscores_123",  # Complex name
        }

        with patch.dict(os.environ, edge_cases, clear=True):
            Config._reset_instance()
            config = Config()
            assert config.RELEVANCY_WEIGHT == 0.0
            assert config.OPENAI_MODEL == " "
            assert config.COLLECTION_NAME == "collection_with_underscores_123"

"""Configuration module."""

from dataclasses import dataclass
from os import getenv
from typing import Any, Optional


@dataclass
class FastAPIConfig:
    """
    Configuration class for FastAPI settings.

    Attributes
    ----------
    title : str
        The title of the FastAPI application.
    description : str
        A brief description of the application.
    version : str
        The version number of the application.
    root_path : str
        The root path for the API.
    """

    title: str = "health-rec"
    description: str = "Health Services Recommendation API"
    version: str = "0.1.0"
    root_path: str = "/api/v1"


class ConfigMeta(type):
    """Metaclass for Config that provides class-level attribute access."""

    def __init__(cls, name: str, bases: tuple[type, ...], dct: dict[str, Any]) -> None:
        super().__init__(name, bases, dct)
        cls._instance = None

    def __getattr__(cls, name: str) -> Any:
        """Get attribute from the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return getattr(cls._instance, name)


class Config(metaclass=ConfigMeta):
    """
    Configuration class for various API keys and settings.

    Attributes
    ----------
    OPENAI_API_KEY : str
        API key for OpenAI services.
    OPENAI_MODEL : str
        The OpenAI model to use.
    OPENAI_EMBEDDING : Optional[str]
        The OpenAI embedding model to use, or None if in test mode.
    COHERE_API_KEY : str
        API key for Cohere services.
    CHROMA_HOST : str
        Hostname for Chroma database.
    CHROMA_PORT : int
        Port number for Chroma database.
    COLLECTION_NAME : str
        Name of the Chroma collection to use.
    RELEVANCY_WEIGHT : float
        The weight of the relevancy score in the ranking strategy.
    """

    def __init__(self) -> None:
        """Initialize configuration with environment variables."""
        self.OPENAI_API_KEY: str = getenv("OPENAI_API_KEY", "")

        # Handle empty string case for OPENAI_MODEL
        openai_model = getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.OPENAI_MODEL: str = openai_model if openai_model else ""

        # Handle empty string case for OPENAI_EMBEDDING
        openai_embedding = getenv("OPENAI_EMBEDDING", "text-embedding-3-small")
        self.OPENAI_EMBEDDING: Optional[str] = (
            openai_embedding if openai_embedding else ""
        )

        self.COHERE_API_KEY: str = getenv("COHERE_API_KEY", "")

        # Handle empty string case for CHROMA_HOST
        chroma_host = getenv("CHROMA_HOST", "chromadb-dev")
        self.CHROMA_HOST: str = chroma_host if chroma_host else ""

        self.CHROMA_PORT: int = 8000

        # Handle empty string case for COLLECTION_NAME
        collection_name = getenv("COLLECTION_NAME", "211_gta")
        self.COLLECTION_NAME: str = collection_name if collection_name else ""

        # Handle RELEVANCY_WEIGHT conversion with error handling
        relevancy_weight_str = getenv("RELEVANCY_WEIGHT", "0.5")
        try:
            self.RELEVANCY_WEIGHT: float = float(relevancy_weight_str)
        except ValueError as err:
            raise ValueError(
                f"Invalid RELEVANCY_WEIGHT value: {relevancy_weight_str}"
            ) from err

        self.EMBEDDING_MAX_CONTEXT_LENGTH: int = 8192
        self.MAX_CONTEXT_LENGTH: int = 300
        self.TOP_K: int = 5
        self.RERANKER_MAX_CONTEXT_LENGTH: int = 150
        self.RERANKER_MAX_SERVICES: int = 20

    @classmethod
    def _reset_instance(cls) -> None:
        """Reset the singleton instance. Used for testing."""
        cls._instance = None

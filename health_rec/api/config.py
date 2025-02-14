"""Configuration module."""

from dataclasses import dataclass
from os import getenv
from typing import Optional


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


class Config:
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

    OPENAI_API_KEY: str = getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_EMBEDDING: Optional[str] = getenv(
        "OPENAI_EMBEDDING", "text-embedding-3-small"
    )
    COHERE_API_KEY: str = getenv("COHERE_API_KEY", "")
    CHROMA_HOST: str = getenv("CHROMA_HOST", "chromadb-dev")
    CHROMA_PORT: int = 8000
    COLLECTION_NAME: str = getenv("COLLECTION_NAME", "211_gta")
    RELEVANCY_WEIGHT: float = float(getenv("RELEVANCY_WEIGHT", "0.5"))
    EMBEDDING_MAX_CONTEXT_LENGTH: int = 8192
    MAX_CONTEXT_LENGTH: int = 300
    TOP_K: int = 5
    RERANKER_MAX_CONTEXT_LENGTH: int = 150
    RERANKER_MAX_SERVICES: int = 20

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
    TEST_MODE : bool
        Flag to indicate if the application is running in test mode.
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
    """

    TEST_MODE: bool = getenv("TEST_MODE", "False").lower() == "true"

    OPENAI_API_KEY: str = getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = getenv("OPENAI_MODEL", "gpt-4-turbo")
    OPENAI_EMBEDDING: Optional[str] = (
        getenv("OPENAI_EMBEDDING", "text-embedding-3-small") if not TEST_MODE else None
    )

    COHERE_API_KEY: str = getenv("COHERE_API_KEY", "")

    CHROMA_HOST: str = getenv("CHROMA_HOST", "localhost")
    CHROMA_PORT: int = int(getenv("CHROMA_PORT", "8000"))

"""Data models."""

from typing import Any, Dict, List

from pydantic import BaseModel


class ChromaDocument(BaseModel):
    """
    Represents a document stored in Chroma vector database.

    Attributes
    ----------
    id : str
        The unique identifier of the document.
    document : str
        The content of the document.
    metadata : Dict[Any, Any]
        Additional metadata associated with the document.
    """

    id: str
    document: str
    metadata: Dict[Any, Any]


class RagGeneration(BaseModel):
    """
    Represents the output of a RAG (Retrieval-Augmented Generation) model.

    Attributes
    ----------
    message : str
        The generated message or response.
    services : List[Any]
        A list of services or items related to the generation.
    """

    message: str
    services: List[Any]


class GetRecommendationPayload(BaseModel):
    """
    Represents the payload for a recommendation request.

    Attributes
    ----------
    discover : str
        The query or topic for which recommendations are sought.
    """

    discover: str


class GetRecommendationResponse(BaseModel):
    """
    Represents the response to a recommendation request.

    Attributes
    ----------
    message : str
        A message accompanying the recommendation.
    services : List[Any]
        A list of recommended services or items.
    """

    message: str
    services: List[Any]

"""Data models."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class Service(BaseModel):
    """
    Represents a service with various attributes.

    Attributes
    ----------
    id : str
        The unique identifier of the service.
    public_name : str
        The public name of the service.
    description : Optional[str]
        The description of the service.
    service_area : Optional[List[str]]
        The areas where the service is available.
    latitude : Optional[float]
        The latitude coordinate of the service location.
    longitude : Optional[float]
        The longitude coordinate of the service location.
    """

    id: str
    public_name: str
    description: Optional[str] = None
    service_area: Optional[List[str]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ServiceDocument(BaseModel):
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


class RAGOutput(BaseModel):
    """
    Represents the output of a RAG (Retrieval-Augmented Generation) model.

    Attributes
    ----------
    message : str
        The generated message or response.
    services : List[Any]
        A list of services or items related to the generation.
    is_emergency : bool
        Whether the message is an emergency message.
    """

    message: str
    services: List[Any]
    is_emergency: bool


class RecommendationPayload(BaseModel):
    """
    Represents the payload for a recommendation request.

    Attributes
    ----------
    discover : str
        The query or topic for which recommendations are sought.
    """

    discover: str


class RecommendationResponse(BaseModel):
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

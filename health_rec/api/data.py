"""Data models."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PhoneNumber(BaseModel):
    """Phone number with metadata.

    Attributes
    ----------
    number : str
        The phone number.
    type : Optional[str]
        The type of the phone number, e.g., fax, toll-free, primary, secondary, etc.
    name : Optional[str]
        Any name associated with the phone number.
    description : Optional[str]
        The description of the phone number.
    extension : Optional[str]
        The extension of the phone number.
    """

    number: str
    type: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    extension: Optional[str] = None


class Address(BaseModel):
    """Physical address information.

    Attributes
    ----------
    street1 : Optional[str]
        The first line of the street address.
    street2 : Optional[str]
        The second line of the street address.
    city : Optional[str]
        The city of the address.
    province : Optional[str]
        The province of the address.
    postal_code : Optional[str]
        The postal code of the address.
    country : Optional[str]
        The country of the address.
    """

    street1: Optional[str] = None
    street2: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None

    def __str__(self) -> str:
        """Return formatted address string."""
        parts = []
        if self.street1:
            parts.append(self.street1)
        if self.street2:
            parts.append(self.street2)
        if self.city:
            parts.append(self.city)
        if self.province:
            parts.append(self.province)
        if self.postal_code:
            parts.append(self.postal_code)
        if self.country:
            parts.append(self.country)
        return ", ".join(filter(None, parts))


class Service(BaseModel):
    """Unified service model with required and optional fields.

    Attributes
    ----------
    id : str
        The unique identifier of the service.
    name : str
        The name of the service.
    description : str
        The description of the service.
    latitude : float
        The latitude coordinate of the service location.
    longitude : float
        The longitude coordinate of the service location.
    phone_numbers : List[PhoneNumber]
        A list of phone numbers associated with the service.
    address : Address
        The physical address of the service.
    metadata : Dict[str, Any]
        Additional metadata associated with the service.
    last_updated : Optional[datetime]
        The last updated timestamp of the service.
    """

    # Required fields
    id: str
    name: str
    description: str
    latitude: float
    longitude: float
    phone_numbers: List[PhoneNumber]
    address: Address

    # Optional metadata fields stored as key-value pairs
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Source tracking
    last_updated: Optional[datetime] = None

    @field_validator("phone_numbers")
    @classmethod
    def validate_phone_numbers(cls, v: List[PhoneNumber]) -> List[PhoneNumber]:  # noqa: N805
        """Ensure at least one phone number exists."""
        if not v:
            raise ValueError("At least one phone number is required")
        return v


class ServiceDocument(BaseModel):
    """
    Represents a document stored in Chroma vector database.

    Attributes
    ----------
    id : str
        The unique identifier of the document.
    document : str
        The content of the document.
    metadata : Dict[str, Any]
        Additional metadata associated with the document.
    relevancy_score: float
        The distance score of the document.
        Larger distances mean the embeddings are less similar, hence less relevant.
    distance : Optional[float]
        The distance to the service to the user's location.
    """

    id: str
    document: str
    metadata: Dict[str, Any]
    relevancy_score: float
    distance: Optional[float] = Field(default=None)


class RecommendationResponse(BaseModel):
    """
    Represents the response to a recommendation request.

    Attributes
    ----------
    message : str
        A message accompanying the recommendation.
    is_emergency : bool
        Whether the request signifies an emergency.
    is_out_of_scope : bool
        Whether the request is out of scope.
    services : Optional[List[Service]]
        A list of services ranked by location and relevancy.
    no_services_found : bool
        Whether no services were found.
    """

    message: str
    is_emergency: bool
    is_out_of_scope: bool
    services: Optional[List[Service]] = Field(default=None)
    no_services_found: bool = Field(default=False)


class Query(BaseModel):
    """
    Represents the user's query and the location of the user.

    Attributes
    ----------
    query : str
        The query that user has entered.
    latitude : Optional[float]
        The latitude coordinate of the user.
    longitude : Optional[float]
        The latitude coordinate of the user.
    radius : Optional[float]
        The radius of the search.
    rerank : Optional[bool]
        Whether to rerank the recommendations.
    """

    query: str
    latitude: Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    radius: Optional[float] = Field(default=None)
    rerank: Optional[bool] = Field(default=False)


class RefineRequest(BaseModel):
    """
    Represents the request for refining recommendations.

    Attributes
    ----------
    query : Query
        The query used to generate the current recommendations.
    recommendation : str
        The recommendation message currently generated.
    questions : List[str]
        A list of additional questions to refine the recommendations.
    answers : List[str]
        A list of answers to the additional questions.
    """

    query: Query
    recommendation: str
    questions: List[str]
    answers: List[str]

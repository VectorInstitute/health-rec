"""Data models."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class ServiceType(str, Enum):
    """Standardized service types across different APIs."""

    EMERGENCY_ROOM = "emergency_room"
    URGENT_CARE = "urgent_care"
    WALK_IN_CLINIC = "walk_in_clinic"
    PHARMACY = "pharmacy"
    MEDICAL_LAB = "medical_lab"
    FAMILY_DOCTOR = "family_doctor"
    COMMUNITY_SERVICE = "community_service"


class AccessibilityLevel(str, Enum):
    """Wheelchair accessibility levels."""

    FULL = "full"
    PARTIAL = "partial"
    NONE = "none"
    UNKNOWN = "unknown"


class DayOfWeek(str, Enum):
    """Days of the week."""

    SUNDAY = "sunday"
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"


class OperatingHours(BaseModel):
    """Operating hours for a specific day."""

    day: DayOfWeek
    is_open: bool
    is_24hour: bool = False
    open_time: Optional[str] = None
    close_time: Optional[str] = None


class HoursException(BaseModel):
    """Special hours or holiday schedules."""

    name: Optional[str] = None
    start_date: datetime
    end_date: datetime
    is_open: bool
    is_24hour: bool = False
    open_time: Optional[str] = None
    close_time: Optional[str] = None


class Address(BaseModel):
    """Physical address information."""

    street1: Optional[str] = None
    street2: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    attention_name: Optional[str] = None


class PhoneNumber(BaseModel):
    """Phone number with additional metadata."""

    number: str
    type: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    extension: Optional[str] = None


class Service(BaseModel):
    """Standardized service model that can accommodate data from multiple APIs."""

    # Core identification
    id: int
    name: str
    service_type: ServiceType
    source_id: Optional[str] = None
    official_name: Optional[str] = None

    # Location
    latitude: float
    longitude: float
    distance: Optional[float] = None
    physical_address: Optional[Address] = None
    mailing_address: Optional[Address] = None

    # Contact information
    phone_numbers: List[PhoneNumber] = Field(default_factory=list)
    fax: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    social_media: Dict[str, str] = Field(default_factory=dict)

    # Service details
    description: Optional[str] = None
    services: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    taxonomy_terms: List[str] = Field(default_factory=list)
    taxonomy_codes: List[str] = Field(default_factory=list)

    # Operating information
    status: Optional[str] = None
    regular_hours: List[OperatingHours] = Field(default_factory=list)
    hours_exceptions: List[HoursException] = Field(default_factory=list)
    timezone_offset: Optional[str] = None

    # Accessibility and special features
    wheelchair_accessible: AccessibilityLevel = AccessibilityLevel.UNKNOWN
    parking_type: Optional[str] = None
    accepts_new_patients: Optional[bool] = None
    wait_time: Optional[int] = None

    # Booking capabilities
    has_online_booking: bool = False
    has_queue_system: bool = False
    accepts_walk_ins: bool = False
    can_book: bool = False

    # Eligibility and fees
    eligibility_criteria: Optional[str] = None
    fee_structure: Optional[str] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None

    # Metadata
    last_updated: Optional[datetime] = None
    record_owner: Optional[str] = None
    data_source: Optional[str] = None  # e.g., "211", "Empower"

    class Config:
        """Pydantic configuration."""

        use_enum_values = True

    @validator("wheelchair_accessible", pre=True)
    def normalize_wheelchair_access(cls, v: str) -> AccessibilityLevel:  # noqa: N805
        """Normalize wheelchair accessibility values from different sources."""
        if isinstance(v, str):
            mapping = {
                "t": AccessibilityLevel.FULL,
                "true": AccessibilityLevel.FULL,
                "p": AccessibilityLevel.PARTIAL,
                "partial": AccessibilityLevel.PARTIAL,
                "f": AccessibilityLevel.NONE,
                "false": AccessibilityLevel.NONE,
            }
            return mapping.get(v.lower(), AccessibilityLevel.UNKNOWN)
        return AccessibilityLevel.UNKNOWN

    @validator("service_type", pre=True)
    def normalize_service_type(cls, v: str) -> ServiceType:  # noqa: N805
        """Normalize service type values from different sources."""
        if isinstance(v, str):
            mapping = {
                "Retail Pharmacy": ServiceType.PHARMACY,
                "Emergency Rooms": ServiceType.EMERGENCY_ROOM,
                "Urgent Care Centre": ServiceType.URGENT_CARE,
                "Primary Care Walk-In Clinic": ServiceType.WALK_IN_CLINIC,
                "Family Doctor's Office": ServiceType.FAMILY_DOCTOR,
                "Medical Labs & Diagnostic Imaging Centres": ServiceType.MEDICAL_LAB,
            }
            return mapping.get(v, ServiceType.COMMUNITY_SERVICE)
        return ServiceType.COMMUNITY_SERVICE


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
    """

    query: str
    latitude: Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    radius: Optional[float] = Field(default=None)


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

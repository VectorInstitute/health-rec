"""Data models."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PhoneNumber(BaseModel):
    """
    Represents a phone number with various attributes.

    Attributes
    ----------
    phone : str
        The phone number.
    name : Optional[str]
        The name of the phone number.
    description : Optional[str]
        The description of the phone number.
    type : Optional[str]
        The type of the phone number.
    """

    phone: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    type: Optional[str] = Field(default=None)


class Service(BaseModel):
    """
    Represents a service with various attributes.

    Attributes
    ----------
    id : int
        The unique identifier of the service.
    parent_id : Optional[int]
        The ID of the parent service.
    public_name : str
        The public name of the service.
    score : Optional[int]
        The score of the service.
    service_area : Optional[List[str]]
        The areas where the service is available.
    distance : Optional[str]
        The distance to the service.
    description : Optional[str]
        The description of the service.
    latitude : Optional[float]
        The latitude coordinate of the service location.
    longitude : Optional[float]
        The longitude coordinate of the service location.
    physical_address_street1 : Optional[str]
        The first line of the physical address.
    physical_address_street2 : Optional[str]
        The second line of the physical address.
    physical_address_city : Optional[str]
        The city of the physical address.
    physical_address_province : Optional[str]
        The province of the physical address.
    physical_address_postal_code : Optional[str]
        The postal code of the physical address.
    physical_address_country : Optional[str]
        The country of the physical address.
    mailing_attention_name : Optional[str]
        The attention name for mailing.
    mailing_address_street1 : Optional[str]
        The first line of the mailing address.
    mailing_address_street2 : Optional[str]
        The second line of the mailing address.
    mailing_address_city : Optional[str]
        The city of the mailing address.
    mailing_address_province : Optional[str]
        The province of the mailing address.
    mailing_address_postal_code : Optional[str]
        The postal code of the mailing address.
    mailing_address_country : Optional[str]
        The country of the mailing address.
    phone_numbers : List[PhoneNumber]
        The phone numbers associated with the service.
    website : Optional[str]
        The website of the service.
    email : Optional[str]
        The email address of the service.
    hours : Optional[str]
        The hours of operation.
    hours2 : Optional[str]
        Additional hours of operation.
    min_age : Optional[str]
        The minimum age for the service.
    max_age : Optional[str]
        The maximum age for the service.
    updated_on : Optional[str]
        The date and time the service was last updated.
    taxonomy_term : Optional[str]
        The taxonomy terms associated with the service.
    taxonomy_terms : Optional[str]
        Additional taxonomy terms.
    taxonomy_codes : Optional[str]
        The taxonomy codes associated with the service.
    eligibility : Optional[str]
        The eligibility criteria for the service.
    fee_structure_source : Optional[str]
        The source of the fee structure.
    official_name : Optional[str]
        The official name of the service.
    physical_city : Optional[str]
        The physical city of the service.
    unique_id_prior_system : Optional[str]
        The unique ID from a prior system.
    record_owner : Optional[str]
        The owner of the record.
    """

    id: int
    parent_id: Optional[int] = Field(default=None, alias="ParentId")
    public_name: str = Field(alias="PublicName")
    score: Optional[int] = Field(default=None, alias="Score")
    service_area: Optional[List[str]] = Field(default=None, alias="ServiceArea")
    distance: Optional[str] = Field(default=None, alias="Distance")
    description: Optional[str] = Field(default=None, alias="Description")
    latitude: Optional[float] = Field(default=None, alias="Latitude")
    longitude: Optional[float] = Field(default=None, alias="Longitude")
    physical_address_street1: Optional[str] = Field(
        default=None, alias="PhysicalAddressStreet1"
    )
    physical_address_street2: Optional[str] = Field(
        default=None, alias="PhysicalAddressStreet2"
    )
    physical_address_city: Optional[str] = Field(
        default=None, alias="PhysicalAddressCity"
    )
    physical_address_province: Optional[str] = Field(
        default=None, alias="PhysicalAddressProvince"
    )
    physical_address_postal_code: Optional[str] = Field(
        default=None, alias="PhysicalAddressPostalCode"
    )
    physical_address_country: Optional[str] = Field(
        default=None, alias="PhysicalAddressCountry"
    )
    mailing_attention_name: Optional[str] = Field(
        default=None, alias="MailingAttentionName"
    )
    mailing_address_street1: Optional[str] = Field(
        default=None, alias="MailingAddressStreet1"
    )
    mailing_address_street2: Optional[str] = Field(
        default=None, alias="MailingAddressStreet2"
    )
    mailing_address_city: Optional[str] = Field(
        default=None, alias="MailingAddressCity"
    )
    mailing_address_province: Optional[str] = Field(
        default=None, alias="MailingAddressProvince"
    )
    mailing_address_postal_code: Optional[str] = Field(
        default=None, alias="MailingAddressPostalCode"
    )
    mailing_address_country: Optional[str] = Field(
        default=None, alias="MailingAddressCountry"
    )
    phone_numbers: List[PhoneNumber] = Field(default_factory=list, alias="PhoneNumbers")
    website: Optional[str] = Field(default=None, alias="Website")
    email: Optional[str] = Field(default=None, alias="Email")
    hours: Optional[str] = Field(default=None, alias="Hours")
    hours2: Optional[str] = Field(default=None, alias="Hours2")
    min_age: Optional[str] = Field(default=None, alias="MinAge")
    max_age: Optional[str] = Field(default=None, alias="MaxAge")
    updated_on: Optional[str] = Field(default=None, alias="UpdatedOn")
    taxonomy_term: Optional[str] = Field(default=None, alias="TaxonomyTerm")
    taxonomy_terms: Optional[str] = Field(default=None, alias="TaxonomyTerms")
    taxonomy_codes: Optional[str] = Field(default=None, alias="TaxonomyCodes")
    eligibility: Optional[str] = Field(default=None, alias="Eligibility")
    fee_structure_source: Optional[str] = Field(
        default=None, alias="FeeStructureSource"
    )
    official_name: Optional[str] = Field(default=None, alias="OfficialName")
    physical_city: Optional[str] = Field(default=None, alias="PhysicalCity")
    unique_id_prior_system: Optional[str] = Field(
        default=None, alias="UniqueIDPriorSystem"
    )
    record_owner: Optional[str] = Field(default=None, alias="RecordOwner")

    class Config:
        """Override Pydantic configuration."""

        populate_by_name = True


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
    """

    id: str
    document: str
    metadata: Dict[str, Any]


class RAGOutput(BaseModel):
    """
    Represents the output of a RAG (Retrieval-Augmented Generation) model.

    Attributes
    ----------
    message : str
        The generated message or response.
    services : List[Service]
        A list of services related to the generation.
    is_emergency : bool
        Whether the message is an emergency message.
    """

    message: str
    services: List[Service]
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
    services : List[Service]
        A list of recommended services.
    """

    message: str
    services: List[Service]

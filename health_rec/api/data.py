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
    alternate_name : Optional[str]
        The alternate name of the service.
    parent_agency : Optional[str]
        The parent agency of the service.
    agency_status : Optional[str]
        The status of the agency.
    agency_description : Optional[str]
        The description of the agency.
    agency_description_site : Optional[str]
        The site description of the agency.
    coverage_area : Optional[str]
        The coverage area of the service.
    coverage_area_text : Optional[str]
        Additional coverage area text.
    eligibility : Optional[str]
        The eligibility criteria for the service.
    disabilities_access : Optional[str]
        Accessibility information.
    hours_of_operation : Optional[str]
        Detailed hours of operation.
    languages_offered : Optional[str]
        Languages in which service is offered.
    last_verified_on : Optional[str]
        When the service was last verified.
    last_verified_by_name : Optional[str]
        Name of person who last verified.
    last_verified_by_email : Optional[str]
        Email of person who last verified.
    application_process : Optional[str]
        The application process description.
    taxonomy_term : Optional[str]
        The taxonomy terms associated with the service.
    taxonomy_terms : Optional[str]
        Additional taxonomy terms.
    taxonomy_codes : Optional[str]
        The taxonomy codes associated with the service.
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
    public_name: str = Field(alias="PublicName")
    description: Optional[str] = Field(default=None, alias="Description")
    latitude: Optional[float] = Field(default=None, alias="Latitude")
    longitude: Optional[float] = Field(default=None, alias="Longitude")
    parent_id: Optional[int] = Field(default=None, alias="ParentId")

    score: Optional[int] = Field(default=None, alias="Score")
    service_area: Optional[List[str]] = Field(default=None, alias="ServiceArea")
    distance: Optional[str] = Field(default=None, alias="Distance")
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
    alternate_name: Optional[str] = Field(default=None, alias="AlternateName")
    parent_agency: Optional[str] = Field(default=None, alias="ParentAgency")
    agency_status: Optional[str] = Field(default=None, alias="AgencyStatus")
    agency_description: Optional[str] = Field(default=None, alias="AgencyDescription")
    agency_description_site: Optional[str] = Field(default=None, alias="AgencyDescription_Site")
    coverage_area: Optional[str] = Field(default=None, alias="CoverageArea")
    coverage_area_text: Optional[str] = Field(default=None, alias="CoverageAreaText")
    eligibility: Optional[str] = Field(default=None, alias="Eligibility")
    disabilities_access: Optional[str] = Field(default=None, alias="DisabilitiesAccess")
    hours_of_operation: Optional[str] = Field(default=None, alias="HoursOfOperation")
    languages_offered: Optional[str] = Field(default=None, alias="LanguagesOffered")
    last_verified_on: Optional[str] = Field(default=None, alias="LastVerifiedOn")
    last_verified_by_name: Optional[str] = Field(default=None, alias="LastVerifiedByName")
    last_verified_by_email: Optional[str] = Field(default=None, alias="LastVerifiedByEmailAddress")
    application_process: Optional[str] = Field(default=None, alias="ApplicationProcess")
    taxonomy_term: Optional[str] = Field(default=None, alias="TaxonomyTerm")
    taxonomy_terms: Optional[str] = Field(default=None, alias="TaxonomyTerms")
    taxonomy_codes: Optional[str] = Field(default=None, alias="TaxonomyCodes")
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

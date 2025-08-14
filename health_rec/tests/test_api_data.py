"""Unit tests for health_rec/api/data.py models."""

from datetime import datetime
from typing import Any, Dict

import pytest
from pydantic import ValidationError

from health_rec.api.data import (
    Address,
    PhoneNumber,
    Query,
    RecommendationResponse,
    RefineRequest,
    Service,
    ServiceDocument,
)


class TestPhoneNumber:
    """Test PhoneNumber model."""

    def test_phone_number_creation_with_required_fields(self):
        """Test creating PhoneNumber with only required fields."""
        phone = PhoneNumber(number="416-555-1234")
        assert phone.number == "416-555-1234"
        assert phone.type is None
        assert phone.name is None
        assert phone.description is None
        assert phone.extension is None

    def test_phone_number_creation_with_all_fields(self):
        """Test creating PhoneNumber with all fields."""
        phone = PhoneNumber(
            number="416-555-1234",
            type="primary",
            name="Main Office",
            description="Business hours phone",
            extension="123",
        )
        assert phone.number == "416-555-1234"
        assert phone.type == "primary"
        assert phone.name == "Main Office"
        assert phone.description == "Business hours phone"
        assert phone.extension == "123"

    def test_phone_number_empty_string_number(self):
        """Test PhoneNumber accepts empty string for number."""
        phone = PhoneNumber(number="")
        assert phone.number == ""


class TestAddress:
    """Test Address model."""

    def test_address_creation_empty(self):
        """Test creating empty Address."""
        address = Address()
        assert address.street1 is None
        assert address.street2 is None
        assert address.city is None
        assert address.province is None
        assert address.postal_code is None
        assert address.country is None

    def test_address_creation_with_all_fields(self):
        """Test creating Address with all fields."""
        address = Address(
            street1="123 Main St",
            street2="Unit 4B",
            city="Toronto",
            province="ON",
            postal_code="M5V 3A8",
            country="Canada",
        )
        assert address.street1 == "123 Main St"
        assert address.street2 == "Unit 4B"
        assert address.city == "Toronto"
        assert address.province == "ON"
        assert address.postal_code == "M5V 3A8"
        assert address.country == "Canada"

    def test_address_str_empty(self):
        """Test __str__ method with empty address."""
        address = Address()
        assert str(address) == ""

    def test_address_str_single_field(self):
        """Test __str__ method with single field."""
        address = Address(city="Toronto")
        assert str(address) == "Toronto"

    def test_address_str_multiple_fields(self):
        """Test __str__ method with multiple fields."""
        address = Address(
            street1="123 Main St", city="Toronto", province="ON", postal_code="M5V 3A8"
        )
        assert str(address) == "123 Main St, Toronto, ON, M5V 3A8"

    def test_address_str_with_none_values(self):
        """Test __str__ method filters out None values."""
        address = Address(
            street1="123 Main St",
            street2=None,
            city="Toronto",
            province=None,
            postal_code="M5V 3A8",
        )
        assert str(address) == "123 Main St, Toronto, M5V 3A8"


class TestService:
    """Test Service model."""

    @pytest.fixture
    def valid_service_data(self) -> Dict[str, Any]:
        """Provide valid service data for testing."""
        return {
            "id": "test_service_1",
            "name": "Test Service",
            "description": "A test service",
            "latitude": 43.6532,
            "longitude": -79.3832,
            "phone_numbers": [{"number": "416-555-1234"}],
            "address": {"street1": "123 Main St", "city": "Toronto"},
        }

    def test_service_creation_with_required_fields(self, valid_service_data):
        """Test creating Service with required fields only."""
        service = Service(**valid_service_data)
        assert service.id == "test_service_1"
        assert service.name == "Test Service"
        assert service.description == "A test service"
        assert service.latitude == 43.6532
        assert service.longitude == -79.3832
        assert len(service.phone_numbers) == 1
        assert service.phone_numbers[0].number == "416-555-1234"
        assert service.address.street1 == "123 Main St"
        assert service.metadata == {}
        assert service.last_updated is None

    def test_service_creation_with_all_fields(self, valid_service_data):
        """Test creating Service with all fields."""
        valid_service_data.update(
            {
                "metadata": {"category": "health", "priority": "high"},
                "last_updated": datetime(2024, 1, 1, 12, 0, 0),
            }
        )
        service = Service(**valid_service_data)
        assert service.metadata == {"category": "health", "priority": "high"}
        assert service.last_updated == datetime(2024, 1, 1, 12, 0, 0)

    def test_service_validation_empty_phone_numbers(self, valid_service_data):
        """Test Service validation fails with empty phone numbers."""
        valid_service_data["phone_numbers"] = []
        with pytest.raises(ValidationError) as exc_info:
            Service(**valid_service_data)
        assert "At least one phone number is required" in str(exc_info.value)

    def test_service_validation_missing_required_fields(self):
        """Test Service validation fails with missing required fields."""
        with pytest.raises(ValidationError):
            Service()

    def test_service_validation_invalid_latitude(self, valid_service_data):
        """Test Service validation with invalid latitude."""
        valid_service_data["latitude"] = "invalid"
        with pytest.raises(ValidationError):
            Service(**valid_service_data)

    def test_service_validation_invalid_longitude(self, valid_service_data):
        """Test Service validation with invalid longitude."""
        valid_service_data["longitude"] = "invalid"
        with pytest.raises(ValidationError):
            Service(**valid_service_data)

    def test_service_phone_numbers_validation_with_valid_data(self, valid_service_data):
        """Test phone_numbers validation with valid data."""
        valid_service_data["phone_numbers"] = [
            {"number": "416-555-1234", "type": "primary"},
            {"number": "416-555-5678", "type": "fax"},
        ]
        service = Service(**valid_service_data)
        assert len(service.phone_numbers) == 2
        assert service.phone_numbers[0].type == "primary"
        assert service.phone_numbers[1].type == "fax"


class TestServiceDocument:
    """Test ServiceDocument model."""

    def test_service_document_creation_required_fields(self):
        """Test creating ServiceDocument with required fields."""
        doc = ServiceDocument(
            id="doc_1",
            document="Test document content",
            metadata={"source": "test"},
            relevancy_score=0.85,
        )
        assert doc.id == "doc_1"
        assert doc.document == "Test document content"
        assert doc.metadata == {"source": "test"}
        assert doc.relevancy_score == 0.85
        assert doc.distance is None

    def test_service_document_creation_with_distance(self):
        """Test creating ServiceDocument with distance."""
        doc = ServiceDocument(
            id="doc_1",
            document="Test document content",
            metadata={"source": "test"},
            relevancy_score=0.85,
            distance=5.2,
        )
        assert doc.distance == 5.2

    def test_service_document_validation_missing_fields(self):
        """Test ServiceDocument validation fails with missing required fields."""
        with pytest.raises(ValidationError):
            ServiceDocument()


class TestRecommendationResponse:
    """Test RecommendationResponse model."""

    def test_recommendation_response_creation_required_fields(self):
        """Test creating RecommendationResponse with required fields."""
        response = RecommendationResponse(
            message="Test recommendation", is_emergency=False, is_out_of_scope=False
        )
        assert response.message == "Test recommendation"
        assert response.is_emergency is False
        assert response.is_out_of_scope is False
        assert response.services is None
        assert response.no_services_found is False

    def test_recommendation_response_creation_with_all_fields(self):
        """Test creating RecommendationResponse with all fields."""
        service_data = {
            "id": "test_service_1",
            "name": "Test Service",
            "description": "A test service",
            "latitude": 43.6532,
            "longitude": -79.3832,
            "phone_numbers": [{"number": "416-555-1234"}],
            "address": {"street1": "123 Main St", "city": "Toronto"},
        }
        service = Service(**service_data)

        response = RecommendationResponse(
            message="Test recommendation",
            is_emergency=True,
            is_out_of_scope=False,
            services=[service],
            no_services_found=True,
        )
        assert response.message == "Test recommendation"
        assert response.is_emergency is True
        assert response.is_out_of_scope is False
        assert len(response.services) == 1
        assert response.services[0].id == "test_service_1"
        assert response.no_services_found is True

    def test_recommendation_response_validation_missing_fields(self):
        """Test RecommendationResponse validation fails with missing required fields."""
        with pytest.raises(ValidationError):
            RecommendationResponse()


class TestQuery:
    """Test Query model."""

    def test_query_creation_required_fields(self):
        """Test creating Query with required fields only."""
        query = Query(query="find healthcare services")
        assert query.query == "find healthcare services"
        assert query.latitude is None
        assert query.longitude is None
        assert query.radius is None
        assert query.rerank is False

    def test_query_creation_with_all_fields(self):
        """Test creating Query with all fields."""
        query = Query(
            query="find healthcare services",
            latitude=43.6532,
            longitude=-79.3832,
            radius=10.5,
            rerank=True,
        )
        assert query.query == "find healthcare services"
        assert query.latitude == 43.6532
        assert query.longitude == -79.3832
        assert query.radius == 10.5
        assert query.rerank is True

    def test_query_validation_missing_query(self):
        """Test Query validation fails with missing query."""
        with pytest.raises(ValidationError):
            Query()

    def test_query_validation_invalid_latitude(self):
        """Test Query validation with invalid latitude."""
        with pytest.raises(ValidationError):
            Query(query="test", latitude="invalid")

    def test_query_validation_invalid_longitude(self):
        """Test Query validation with invalid longitude."""
        with pytest.raises(ValidationError):
            Query(query="test", longitude="invalid")


class TestRefineRequest:
    """Test RefineRequest model."""

    @pytest.fixture
    def valid_query(self) -> Query:
        """Provide valid Query for testing."""
        return Query(
            query="find healthcare services", latitude=43.6532, longitude=-79.3832
        )

    def test_refine_request_creation(self, valid_query):
        """Test creating RefineRequest with all fields."""
        refine_request = RefineRequest(
            query=valid_query,
            recommendation="Based on your query, here are some services...",
            questions=[
                "What time of day do you need services?",
                "Any specific requirements?",
            ],
            answers=["Morning preferred", "Wheelchair accessible"],
        )
        assert refine_request.query.query == "find healthcare services"
        assert (
            refine_request.recommendation
            == "Based on your query, here are some services..."
        )
        assert len(refine_request.questions) == 2
        assert len(refine_request.answers) == 2
        assert refine_request.questions[0] == "What time of day do you need services?"
        assert refine_request.answers[0] == "Morning preferred"

    def test_refine_request_validation_missing_fields(self):
        """Test RefineRequest validation fails with missing required fields."""
        with pytest.raises(ValidationError):
            RefineRequest()

    def test_refine_request_empty_lists(self, valid_query):
        """Test RefineRequest with empty questions and answers lists."""
        refine_request = RefineRequest(
            query=valid_query,
            recommendation="Test recommendation",
            questions=[],
            answers=[],
        )
        assert len(refine_request.questions) == 0
        assert len(refine_request.answers) == 0

    def test_refine_request_validation_invalid_query(self):
        """Test RefineRequest validation with invalid query."""
        with pytest.raises(ValidationError):
            RefineRequest(
                query="invalid",  # Should be Query object
                recommendation="test",
                questions=[],
                answers=[],
            )


class TestModelIntegration:
    """Test integration between different models."""

    def test_service_with_complex_phone_numbers(self):
        """Test Service with complex PhoneNumber objects."""
        service_data = {
            "id": "test_service_1",
            "name": "Test Service",
            "description": "A test service",
            "latitude": 43.6532,
            "longitude": -79.3832,
            "phone_numbers": [
                {
                    "number": "416-555-1234",
                    "type": "primary",
                    "name": "Main Office",
                    "description": "Business hours",
                    "extension": "123",
                },
                {"number": "416-555-5678", "type": "fax"},
            ],
            "address": {
                "street1": "123 Main St",
                "street2": "Suite 100",
                "city": "Toronto",
                "province": "ON",
                "postal_code": "M5V 3A8",
                "country": "Canada",
            },
        }

        service = Service(**service_data)
        assert len(service.phone_numbers) == 2
        assert service.phone_numbers[0].extension == "123"
        assert service.phone_numbers[1].type == "fax"
        assert (
            str(service.address)
            == "123 Main St, Suite 100, Toronto, ON, M5V 3A8, Canada"
        )

    def test_recommendation_response_with_multiple_services(self):
        """Test RecommendationResponse with multiple services."""
        services_data = [
            {
                "id": "service_1",
                "name": "Service 1",
                "description": "First service",
                "latitude": 43.6532,
                "longitude": -79.3832,
                "phone_numbers": [{"number": "416-555-1234"}],
                "address": {"city": "Toronto"},
            },
            {
                "id": "service_2",
                "name": "Service 2",
                "description": "Second service",
                "latitude": 43.6500,
                "longitude": -79.3800,
                "phone_numbers": [{"number": "416-555-5678"}],
                "address": {"city": "Toronto"},
            },
        ]

        services = [Service(**data) for data in services_data]
        response = RecommendationResponse(
            message="Here are your services",
            is_emergency=False,
            is_out_of_scope=False,
            services=services,
        )

        assert len(response.services) == 2
        assert response.services[0].id == "service_1"
        assert response.services[1].id == "service_2"

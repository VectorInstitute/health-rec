"""Pytest configuration and shared fixtures."""

import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import chromadb
import pytest


@pytest.fixture
def test_services() -> List[Dict[str, Any]]:
    """Provide sample test services data."""
    return [
        {
            "id": "test_service_1",
            "name": "Community Health Center",
            "description": "Provides primary healthcare services",
            "latitude": 43.6532,
            "longitude": -79.3832,
            "address": {
                "street1": "123 Main St",
                "city": "Toronto",
                "province": "ON",
                "postal_code": "M5V 3A8",
                "country": "Canada",
            },
            "phone_numbers": [
                {"number": "416-555-1234", "type": "primary"},
                {"number": "416-555-5678", "type": "fax"},
            ],
            "email": "info@communityhealthcenter.ca",
            "website": "https://communityhealthcenter.ca",
            "categories": ["health", "primary care"],
            "languages": ["English", "French", "Spanish"],
            "accessibility": ["wheelchair accessible", "hearing loop"],
        },
        {
            "id": "test_service_2",
            "name": "Mental Health Support",
            "description": "Counseling and mental health services",
            "latitude": 43.6500,
            "longitude": -79.3800,
            "address": {
                "street1": "456 Queen St W",
                "city": "Toronto",
                "province": "ON",
                "postal_code": "M5V 2A4",
            },
            "phone_numbers": [{"number": "416-555-9876", "type": "primary"}],
            "email": "support@mentalhealthsupport.org",
            "categories": ["mental health", "counseling"],
            "languages": ["English"],
            "hours": [
                {
                    "day": "Monday",
                    "is_open": True,
                    "open_time": "09:00",
                    "close_time": "17:00",
                },
                {
                    "day": "Tuesday",
                    "is_open": True,
                    "open_time": "09:00",
                    "close_time": "17:00",
                },
            ],
        },
        {
            "id": "test_service_3",
            "name": "Food Bank",
            "description": "Emergency food assistance",
            "latitude": 43.6400,
            "longitude": -79.3900,
            "phone_numbers": [{"number": "416-555-3333", "type": "primary"}],
            "categories": ["food", "emergency assistance"],
            "eligibility": "Low income families",
            "cost": "Free",
        },
    ]


@pytest.fixture
def temp_json_file(test_services):
    """Create a temporary JSON file with test data."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(test_services, f, indent=2)
        temp_path = f.name

    yield temp_path

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def ephemeral_collection():
    """Create an ephemeral ChromaDB collection for testing."""
    client = chromadb.EphemeralClient()
    collection = client.create_collection(name="test_collection")
    return collection


@pytest.fixture
def sample_service() -> Dict[str, Any]:
    """Provide a single sample service for testing."""
    return {
        "id": "single_test",
        "name": "Test Service",
        "description": "A single test service",
        "latitude": 43.6532,
        "longitude": -79.3832,
        "address": {"street1": "123 Test St", "city": "Toronto"},
        "phone_numbers": [{"number": "555-1234", "type": "primary"}],
    }

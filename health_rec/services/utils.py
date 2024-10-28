"""Utility functions for the services module."""

import json
import logging
from typing import Any, Dict, List, Optional

from chromadb.api.types import QueryResult

from api.data import (
    AccessibilityLevel,
    Address,
    PhoneNumber,
    Service,
    ServiceDocument,
    ServiceType,
)


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def _parse_chroma_result(chroma_results: QueryResult) -> List[ServiceDocument]:
    """Parse the results from ChromaDB into a list of ServiceDocument objects."""
    parsed_results: List[ServiceDocument] = [
        ServiceDocument(id=id_, document=doc, metadata=meta, relevancy_score=score)
        for id_, doc, meta, score in zip(
            chroma_results["ids"][0] if chroma_results["ids"] else [],
            chroma_results["documents"][0] if chroma_results["documents"] else [],
            chroma_results["metadatas"][0] if chroma_results["metadatas"] else [],
            chroma_results["distances"][0] if chroma_results["distances"] else [],
        )
    ]

    return parsed_results


def _parse_json_field(field: Any, default: Any) -> Any:
    """Parse a potentially JSON-encoded field."""
    if isinstance(field, str):
        try:
            return json.loads(field)
        except json.JSONDecodeError:
            return default
    return field


def _parse_coordinates(metadata: Dict[str, Any]) -> tuple[float, float]:
    """Parse latitude and longitude coordinates."""
    try:
        latitude = float(metadata.get("latitude", 0))
        longitude = float(metadata.get("longitude", 0))
    except (ValueError, TypeError):
        latitude = longitude = 0.0
    return latitude, longitude


def _parse_phone_numbers(phones: List[Dict[str, Any]]) -> List[PhoneNumber]:
    """Parse phone numbers from raw data."""
    phone_numbers = []
    for phone in phones:
        number = phone.get("number", "")
        extension = None

        if isinstance(number, str) and "ext" in number.lower():
            parts = number.lower().split("ext")
            number = parts[0].strip()
            extension = parts[1].strip()

        phone_numbers.append(
            PhoneNumber(
                number=number,
                type=phone.get("type"),
                name=phone.get("name"),
                description=phone.get("description"),
                extension=extension,
            )
        )
    return phone_numbers


def _parse_service_type(service_type: Optional[str]) -> ServiceType:
    """Parse and validate service type."""
    if not service_type:
        return ServiceType.COMMUNITY_SERVICE

    try:
        return ServiceType(service_type)
    except ValueError:
        return ServiceType.COMMUNITY_SERVICE


def _parse_wheelchair_access(access: Optional[str]) -> str:
    """Parse and validate wheelchair accessibility."""
    if not access:
        return AccessibilityLevel.UNKNOWN.value

    try:
        return AccessibilityLevel(access).value
    except ValueError:
        return AccessibilityLevel.UNKNOWN.value


def _metadata_to_service(metadata: Dict[str, Any]) -> Service:
    """Convert metadata to a Service object."""
    try:
        # Parse coordinates
        latitude, longitude = _parse_coordinates(metadata)

        # Ensure service_type is always set to a valid ServiceType enum value
        service_type = _parse_service_type(metadata.get("service_type"))

        # Parse complex fields that might be JSON strings
        physical_address = _parse_json_field(metadata.get("physical_address"), None)
        if physical_address:
            physical_address = Address(**physical_address)

        phone_numbers = _parse_json_field(metadata.get("phone_numbers"), [])
        if isinstance(phone_numbers, list):
            phone_numbers = _parse_phone_numbers(phone_numbers)

        # Create the Service object with parsed fields
        service = Service(
            id=metadata["id"],
            name=metadata["name"],
            service_type=service_type,  # This will now always be a valid ServiceType
            latitude=latitude,
            longitude=longitude,
            physical_address=physical_address,
            phone_numbers=phone_numbers,
            fax=metadata.get("fax"),
            email=metadata.get("email"),
            website=metadata.get("website"),
            description=metadata.get("description"),
            services=metadata.get("services", []),
            languages=metadata.get("languages", []),
            status=metadata.get("status"),
            regular_hours=metadata.get("regular_hours", []),
            hours_exceptions=metadata.get("hours_exceptions", []),
            timezone_offset=metadata.get("timezone_offset"),
            wheelchair_accessible=metadata.get("wheelchair_accessible"),
            parking_type=metadata.get("parking_type"),
            accepts_new_patients=metadata.get("accepts_new_patients"),
            wait_time=metadata.get("wait_time"),
            has_online_booking=metadata.get("has_online_booking", False),
            can_book=metadata.get("can_book", False),
            data_source=metadata.get("data_source"),
        )
        logger.debug(f"Successfully parsed service: {service.id}")
        return service
    except Exception as e:
        logger.error(f"Error converting metadata to Service: {e}")
        logger.debug(f"Problematic metadata: {metadata}")
        # Return a minimal valid Service object with required fields
        return Service(
            id=metadata.get("id", 0),
            name=metadata.get("name", "Unknown"),
            service_type=ServiceType.UNKNOWN,  # Always provide a valid ServiceType
            latitude=float(metadata.get("latitude", 0)),
            longitude=float(metadata.get("longitude", 0)),
            data_source=metadata.get("data_source", "unknown"),
        )

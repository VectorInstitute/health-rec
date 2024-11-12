"""Utility functions for the services module."""

import ast
import json
import logging
from typing import Any, Dict, List, Optional, Set, Tuple

from chromadb.api.types import QueryResult

from api.data import Address, PhoneNumber, Service, ServiceDocument


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Core service fields
CORE_SERVICE_FIELDS: Set[str] = {
    "id",
    "name",
    "description",
    "latitude",
    "longitude",
    "address",
    "phone_numbers",
    "email",
    "metadata",
    "last_updated",
}


def _safe_json_loads(value: Any) -> Any:
    """Safely parse JSON or string representation of data structures."""
    if not isinstance(value, str):
        return value

    try:
        return json.loads(value)
    except json.JSONDecodeError:
        try:
            result = ast.literal_eval(value)
            return list(result) if isinstance(result, tuple) else result
        except (ValueError, SyntaxError):
            return value


def _parse_json_field(field: Any, default: Any) -> Any:
    """Parse a potentially JSON-encoded field."""
    if not field:
        return default

    if isinstance(field, (dict, list)):
        return field

    if isinstance(field, str):
        try:
            parsed = _safe_json_loads(field)
            if isinstance(parsed, (dict, list)):
                return parsed
            logger.warning(f"Parsed value is not dict/list: {parsed}")
            return default
        except Exception as e:
            logger.warning(f"Error parsing field: {e}")
            return default

    return default


def _parse_chroma_result(chroma_results: QueryResult) -> List[ServiceDocument]:
    """Parse the results from ChromaDB into a list of ServiceDocument objects."""
    if not chroma_results or not all(
        key in chroma_results for key in ["ids", "documents", "metadatas", "distances"]
    ):
        logger.warning("Invalid or empty ChromaDB results")
        return []

    try:
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
    except Exception as e:
        logger.error(f"Error parsing ChromaDB results: {e}")
        return []


def _parse_coordinates(metadata: Dict[str, Any]) -> Tuple[float, float]:
    """Parse latitude and longitude coordinates."""
    try:
        latitude = float(metadata.get("latitude", 0))
        longitude = float(metadata.get("longitude", 0))
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            logger.warning(
                f"Invalid coordinate values: lat={latitude}, lon={longitude}"
            )
            return 0.0, 0.0
        return latitude, longitude
    except (ValueError, TypeError) as e:
        logger.warning(f"Error parsing coordinates: {e}")
        return 0.0, 0.0


def _normalize_phone_data(phones: Any) -> List[Dict[str, Any]]:
    """Normalize phone data into a list of dictionaries."""
    # Handle string input
    if isinstance(phones, str):
        try:
            phones = _safe_json_loads(phones)
        except Exception:
            return []

    # Convert tuple to list
    if isinstance(phones, tuple):
        phones = list(phones)

    # Handle single dictionary
    if isinstance(phones, dict):
        return [phones]

    # Ensure we have a list
    if not isinstance(phones, list):
        return []

    return phones


def _split_number_extension(number: str) -> Tuple[str, str]:
    """Split phone number and extension."""
    parts = number.lower().split("ext")
    return parts[0].strip(), parts[1].strip()


def _parse_single_phone(phone_data: Any) -> Optional[PhoneNumber]:
    """Parse a single phone number entry."""
    try:
        # Handle string representation of dict
        if isinstance(phone_data, str):
            try:
                phone_data = _safe_json_loads(phone_data)
            except Exception:
                return None

        # Ensure we have a dictionary
        if not isinstance(phone_data, dict):
            return None

        # Get and validate number
        number = str(phone_data.get("number", "")).strip()
        if not number:
            return None

        # Extract extension
        extension = None
        if ext := phone_data.get("extension"):
            extension = str(ext).strip()
        elif "ext" in number.lower():
            number, extension = _split_number_extension(number)

        # Create phone number object
        return PhoneNumber(
            number=number,
            type=str(phone_data.get("type", "")).strip(),
            name=str(phone_data.get("name", "")).strip(),
            description=str(phone_data.get("description", "")).strip(),
            extension=extension,
        )
    except Exception as e:
        logger.debug(f"Error parsing phone number {phone_data}: {e}")
        return None


def _parse_phone_numbers(phones: Any) -> List[PhoneNumber]:
    """Parse phone numbers from raw data."""
    if not phones:
        return [PhoneNumber(number="Unknown")]

    # Convert input to list of dictionaries
    phone_list = _normalize_phone_data(phones)
    if not phone_list:
        return [PhoneNumber(number="Unknown")]

    # Parse each phone number
    phone_numbers = []
    for phone_data in phone_list:
        if parsed_phone := _parse_single_phone(phone_data):
            phone_numbers.append(parsed_phone)

    return phone_numbers if phone_numbers else [PhoneNumber(number="Unknown")]


def _parse_address(address_data: Any) -> Address:
    """Parse address from raw data."""
    default_address = Address(
        street1="Unknown", city="Unknown", province="Unknown", country="Canada"
    )

    if not address_data:
        return default_address

    try:
        parsed_address = _parse_json_field(address_data, {})
        if not isinstance(parsed_address, dict):
            logger.warning(f"Invalid address format: {parsed_address}")
            return default_address

        return Address(
            street1=parsed_address.get("street1", "Unknown"),
            street2=parsed_address.get("street2"),
            city=parsed_address.get("city", "Unknown"),
            province=parsed_address.get("province", "Unknown"),
            postal_code=parsed_address.get("postal_code"),
            country=parsed_address.get("country", "Canada"),
        )
    except Exception as e:
        logger.error(f"Error parsing address: {e}")
        return default_address


def _metadata_to_service(metadata: Dict[str, Any]) -> Service:
    """Convert metadata to a Service object."""
    try:
        # Parse required fields
        service_id = str(metadata.get("id", "0"))
        name = metadata.get("name", "Unknown Service")
        description = metadata.get("description", "No description available")

        # Parse coordinates
        latitude, longitude = _parse_coordinates(metadata)

        # Parse address
        logger.debug(f"Raw address data: {metadata.get('address')}")
        address = _parse_address(metadata.get("address"))

        # Parse phone numbers
        phone_numbers = _parse_phone_numbers(metadata.get("phone_numbers"))

        # Create the Service object
        service = Service(
            id=service_id,
            name=name,
            description=description,
            latitude=latitude,
            longitude=longitude,
            address=address,
            phone_numbers=phone_numbers,
            email=metadata.get("email", ""),
            metadata=_extract_metadata(metadata),
            last_updated=metadata.get("last_updated"),
        )

        logger.debug(f"Successfully parsed service: {service.id}")
        return service

    except Exception as e:
        logger.error(f"Error converting metadata to Service: {e}")
        logger.debug(f"Problematic metadata: {metadata}")
        return Service(
            id=str(metadata.get("id", "0")),
            name=metadata.get("name", "Unknown"),
            description="No description available",
            latitude=float(metadata.get("latitude", 0)),
            longitude=float(metadata.get("longitude", 0)),
            address=Address(
                street1="Unknown", city="Unknown", province="Unknown", country="Canada"
            ),
            phone_numbers=[PhoneNumber(number="Unknown")],
            email="",
            metadata={},
        )


def _extract_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Extract additional fields into metadata."""
    additional_metadata = {
        key: value
        for key, value in metadata.items()
        if key not in CORE_SERVICE_FIELDS and value is not None
    }

    # Parse any string values that might be JSON
    for key, value in additional_metadata.items():
        if isinstance(value, str):
            additional_metadata[key] = _safe_json_loads(value)

    return additional_metadata

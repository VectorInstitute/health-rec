"""Service deduplication utilities."""

import logging
from datetime import datetime

from api.data import Service, ServiceDocument


logger = logging.getLogger(__name__)


def normalize_name(name: str) -> str:
    """Normalize service name for comparison."""
    return name.lower().strip()


def create_duplicate_key(
    name: str, latitude: float, longitude: float, precision: int = 6
) -> str:
    """
    Create a key for duplicate detection based on name and location.

    Parameters
    ----------
    name : str
        The service name
    latitude : float
        The service latitude
    longitude : float
        The service longitude
    precision : int, optional
        Decimal precision for coordinates (default: 6 for ~1m accuracy)

    Returns
    -------
    str
        A normalized key for duplicate detection
    """
    normalized_name = normalize_name(name)
    # Round coordinates to specified precision to handle minor variations
    rounded_lat = round(latitude, precision)
    rounded_lon = round(longitude, precision)
    return f"{normalized_name}|{rounded_lat}|{rounded_lon}"


def find_duplicates(services: list[Service]) -> dict[str, list[Service]]:
    """
    Find duplicate services based on name and location.

    Parameters
    ----------
    services : list[Service]
        List of services to check for duplicates

    Returns
    -------
    dict[str, list[Service]]
        Dictionary mapping duplicate keys to lists of duplicate services
    """
    duplicates_map: dict[str, list[Service]] = {}

    for service in services:
        key = create_duplicate_key(service.name, service.latitude, service.longitude)

        if key not in duplicates_map:
            duplicates_map[key] = []
        duplicates_map[key].append(service)

    # Only return groups with more than one service (actual duplicates)
    return {
        key: services_list
        for key, services_list in duplicates_map.items()
        if len(services_list) > 1
    }


def remove_duplicates(
    services: list[Service], keep_strategy: str = "first"
) -> tuple[list[Service], int]:
    """
    Remove duplicate services from a list.

    Parameters
    ----------
    services : list[Service]
        List of services that may contain duplicates
    keep_strategy : str, optional
        Strategy for which service to keep from duplicates:
        - "first": Keep the first occurrence (default)
        - "last": Keep the last occurrence
        - "most_recent": Keep the service with the most recent last_updated timestamp

    Returns
    -------
    tuple[list[Service], int]
        A tuple containing the deduplicated list and the number of duplicates removed
    """
    if not services:
        return services, 0

    seen_keys: set[str] = set()
    unique_services: list[Service] = []
    removed_count = 0

    if keep_strategy == "last":
        services = list(reversed(services))
    elif keep_strategy == "most_recent":
        # Group services by duplicate key and sort each group
        key_to_services: dict[str, list[Service]] = {}
        for service in services:
            key = create_duplicate_key(
                service.name, service.latitude, service.longitude
            )
            if key not in key_to_services:
                key_to_services[key] = []
            key_to_services[key].append(service)

        # Sort each group by last_updated (most recent first)
        for _key, service_group in key_to_services.items():
            service_group.sort(
                key=lambda s: s.last_updated or datetime.min, reverse=True
            )

        # Flatten back to a single list, keeping most recent first in each group
        services = []
        for service_group in key_to_services.values():
            services.extend(service_group)

    for service in services:
        key = create_duplicate_key(service.name, service.latitude, service.longitude)

        if key not in seen_keys:
            seen_keys.add(key)
            unique_services.append(service)
        else:
            removed_count += 1

    if keep_strategy == "last":
        unique_services = list(reversed(unique_services))

    if removed_count > 0:
        logger.info(f"Removed {removed_count} duplicate services")

    return unique_services, removed_count


def remove_duplicates_from_documents(
    documents: list[ServiceDocument], keep_strategy: str = "first"
) -> tuple[list[ServiceDocument], int]:
    """
    Remove duplicate service documents based on service metadata.

    Parameters
    ----------
    documents : list[ServiceDocument]
        List of service documents that may contain duplicates
    keep_strategy : str, optional
        Strategy for which document to keep from duplicates (default: "first")

    Returns
    -------
    tuple[list[ServiceDocument], int]
        A tuple containing the deduplicated list and the number of duplicates removed
    """
    if not documents:
        return documents, 0

    seen_keys: set[str] = set()
    unique_documents: list[ServiceDocument] = []
    removed_count = 0

    # Handle different keep strategies
    documents_to_process = documents
    if keep_strategy == "last":
        documents_to_process = list(reversed(documents))
    elif keep_strategy == "best_score":
        # Sort by relevancy_score (lower is better for distance-based scores)
        documents_to_process = sorted(documents, key=lambda d: d.relevancy_score)

    for doc in documents_to_process:
        # Extract name and coordinates from metadata
        name = doc.metadata.get("name", "")
        latitude = doc.metadata.get("latitude")
        longitude = doc.metadata.get("longitude")

        if not name or latitude is None or longitude is None:
            # If we can't determine location/name, keep the document
            unique_documents.append(doc)
            continue

        key = create_duplicate_key(name, float(latitude), float(longitude))

        if key not in seen_keys:
            seen_keys.add(key)
            unique_documents.append(doc)
        else:
            removed_count += 1

    if keep_strategy == "last":
        unique_documents = list(reversed(unique_documents))

    if removed_count > 0:
        logger.info(f"Removed {removed_count} duplicate service documents")

    return unique_documents, removed_count

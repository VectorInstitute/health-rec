"""Download and process data from the 211 API."""

import os
import requests
from dotenv import load_dotenv
import json
import math
from pathlib import Path
import argparse
from typing import Dict, Any, Optional, List
from datetime import datetime

from api.data import Service, ServiceType, Address, PhoneNumber, AccessibilityLevel


def validate_service(data: Dict[str, Any]) -> Optional[Service]:
    """Validate and create Service object from mapped data."""
    try:
        return Service(**data)
    except Exception as e:
        print(f"Validation error for a service: {e}")
        return None


def parse_phone_numbers(phones: List[Dict[str, str]]) -> List[PhoneNumber]:
    """Parse phone numbers from 211 data format."""
    phone_numbers = []
    for phone in phones:
        number = phone.get("Phone", "")
        extension = None

        if "ext" in number.lower():
            parts = number.lower().split("ext")
            number = parts[0].strip()
            extension = parts[1].strip()

        phone_numbers.append(
            PhoneNumber(
                number=number,
                type=phone.get("Type", ""),
                name=phone.get("Name", ""),
                description=phone.get("Description", ""),
                extension=extension,
            )
        )
    return phone_numbers


def parse_taxonomy(taxonomy_str: str) -> List[str]:
    """Parse taxonomy strings into clean list."""
    if not taxonomy_str:
        return []

    terms = []
    for term in taxonomy_str.split(";"):
        clean_term = term.split("*")[0].strip()
        if clean_term:
            terms.append(clean_term)
    return terms


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def parse_datetime(date_str: Optional[str]) -> Optional[str]:
    """Parse datetime string to ISO format."""
    if not date_str:
        return None
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return dt.isoformat()
    except ValueError:
        return None


def parse_age(age_str: Optional[str]) -> Optional[int]:
    """Parse age string to integer."""
    if not age_str:
        return None
    try:
        return int(float(age_str))
    except (ValueError, TypeError):
        return None


def map_211_data_to_service(data: Dict[str, Any]) -> Dict[str, Any]:
    """Map 211 API data to standardized Service format."""
    try:
        latitude = float(data.get("Latitude", 0))
        longitude = float(data.get("Longitude", 0))
    except (ValueError, TypeError):
        latitude = longitude = 0.0

    physical_address = Address(
        street1=data.get("PhysicalAddressStreet1"),
        street2=data.get("PhysicalAddressStreet2"),
        city=data.get("PhysicalAddressCity"),
        province=data.get("PhysicalAddressProvince"),
        postal_code=data.get("PhysicalAddressPostalCode"),
        country=data.get("PhysicalAddressCountry"),
    )

    mailing_address = Address(
        street1=data.get("MailingAddressStreet1"),
        street2=data.get("MailingAddressStreet2"),
        city=data.get("MailingAddressCity"),
        province=data.get("MailingAddressProvince"),
        postal_code=data.get("MailingAddressPostalCode"),
        country=data.get("MailingAddressCountry"),
        attention_name=data.get("MailingAttentionName"),
    )

    return {
        "id": int(data["id"]),
        "name": data["PublicName"],
        "service_type": ServiceType.COMMUNITY_SERVICE,
        "source_id": data.get("UniqueIDPriorSystem"),
        "official_name": data.get("OfficialName"),
        "latitude": latitude,
        "longitude": longitude,
        "physical_address": physical_address.dict(exclude_none=True),
        "mailing_address": mailing_address.dict(exclude_none=True),
        "phone_numbers": [
            p.dict() for p in parse_phone_numbers(data.get("PhoneNumbers", []))
        ],
        "email": data.get("Email"),
        "website": data.get("Website"),
        "description": data.get("Description"),
        "taxonomy_terms": parse_taxonomy(data.get("TaxonomyTerms", "")),
        "taxonomy_codes": parse_taxonomy(data.get("TaxonomyCodes", "")),
        "eligibility_criteria": data.get("Eligibility"),
        "fee_structure": data.get("FeeStructureSource"),
        "min_age": parse_age(data.get("MinAge")),
        "max_age": parse_age(data.get("MaxAge")),
        "last_updated": parse_datetime(data.get("UpdatedOn")),
        "record_owner": data.get("RecordOwner"),
        "data_source": "211",
        "wheelchair_accessible": AccessibilityLevel.UNKNOWN,
    }


def save_to_file(data: Dict[str, Any], file_name: str) -> None:
    """Save the data to a JSON file."""
    mapped_services = []
    for service_data in data["Records"]:
        mapped_data = map_211_data_to_service(service_data)
        validated_service = validate_service(mapped_data)
        if validated_service:
            mapped_services.append(validated_service.dict(exclude_none=True))

    with open(file_name, "w") as f:
        json.dump(mapped_services, f, indent=2, cls=DateTimeEncoder)


def create_payload(
    page_index: int, dataset: str, is_gta: bool, page_size: int
) -> Dict[str, Any]:
    """Create the payload for the API request."""
    payload = {
        "Dataset": dataset,
        "Lang": "en",
        "Search": "match",
        "MatchMode": "all",
        "ExtCategory": "",
        "Distance": 100000000000,
        "SortOrder": "distance",
        "PageIndex": page_index,
        "PageSize": page_size,
        "Fields": (
            "TaxonomyTerm,TaxonomyTerms,TaxonomyCodes,Eligibility,"
            "FeeStructureSource,OfficialName,PhysicalCity,DocumentsRequired,"
            "ApplicationProcess,UniqueIDPriorSystem,DisabilitiesAccess"
        ),
    }

    if is_gta:
        payload.update(
            {
                "Communities": "Toronto|Durham Region|York Region|Peel Region",
                "SearchType": "coverage",
            }
        )
    else:
        payload.update(
            {
                "Latitude": 45.2733,
                "Longitude": -66.0633,
                "SearchType": "proximity",
            }
        )

    return payload


def fetch_data(
    page_index: int,
    api_key: str,
    base_url: str,
    dataset: str,
    is_gta: bool,
    page_size: int,
) -> Any:
    """Fetch data from the API for a given page index."""
    headers = {"Content-Type": "application/json"}
    params = {"key": api_key}

    response = requests.post(
        base_url,
        headers=headers,
        params=params,
        json=create_payload(page_index, dataset, is_gta, page_size),
    )
    response.raise_for_status()
    return response.json()


def main(
    api_key: str,
    base_url: str,
    dataset: str,
    is_gta: bool,
    data_dir: str,
    page_size: int,
) -> None:
    os.makedirs(data_dir, exist_ok=True)

    first_page = fetch_data(0, api_key, base_url, dataset, is_gta, page_size)
    total_records = first_page["RecordCount"]
    total_pages = math.ceil(total_records / page_size)

    print(f"Total records: {total_records}")
    print(f"Total pages: {total_pages}")

    for page in range(total_pages):
        print(f"Fetching page {page + 1} of {total_pages}")
        data = fetch_data(page, api_key, base_url, dataset, is_gta, page_size)
        file_name = Path(f"data-{page:02d}.json")
        save_to_file(data, os.path.join(data_dir, file_name))
        print(f"Saved data to {file_name}")


if __name__ == "__main__":
    load_dotenv("./.env.development")

    parser = argparse.ArgumentParser(description="Download data from the 211 API.")
    parser.add_argument(
        "--api-key", default=os.getenv("211_API_KEY"), help="API key for 211 API"
    )
    parser.add_argument(
        "--base-url",
        default="https://data.211support.org/api/v2/search",
        help="Base URL for 211 API",
    )
    parser.add_argument("--dataset", default="on", help="Dataset to download")
    parser.add_argument(
        "--is-gta", action="store_true", help="Whether to download GTA data"
    )
    parser.add_argument(
        "--data-dir", default="/mnt/data/211", help="Directory to save data"
    )
    parser.add_argument(
        "--page-size", type=int, default=1000, help="Number of records per page"
    )

    args = parser.parse_args()

    if not args.api_key:
        raise ValueError("211_API_KEY is not set")

    data_dir = args.data_dir
    if args.is_gta:
        data_dir = os.path.join(data_dir, "gta")
    else:
        data_dir = os.path.join(data_dir, args.dataset)

    main(
        args.api_key, args.base_url, args.dataset, args.is_gta, data_dir, args.page_size
    )

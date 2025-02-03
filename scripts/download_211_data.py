"""Download and process data from the 211 API."""

import argparse
import json
import logging
import math
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv
from pydantic import ValidationError

from api.data import Address, PhoneNumber, Service
from common import RetryableSession
from fields import FIELDS


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_phone_numbers(phones: List[Dict[str, str]]) -> List[PhoneNumber]:
    """Parse phone numbers from 211 data format."""
    phone_numbers = []
    for phone in phones:
        number = phone.get("Phone", "")
        if not number:
            continue

        extension = None
        if "ext" in number.lower():
            parts = number.lower().split("ext")
            number = parts[0].strip()
            extension = parts[1].strip()

        phone_numbers.append(
            PhoneNumber(
                number=number,
                type=phone.get("Type"),
                name=phone.get("Name"),
                description=phone.get("Description"),
                extension=extension,
            )
        )

    # Ensure at least one phone number exists
    if not phone_numbers:
        phone_numbers.append(PhoneNumber(number="Unknown"))

    return phone_numbers


def map_211_data_to_service(data: Dict[str, Any]) -> Service:
    """Map 211 API data to standardized Service format."""
    try:
        # Parse required fields
        address = Address(
            street1=data.get("PhysicalAddressStreet1", "Unknown"),
            street2=data.get("PhysicalAddressStreet2"),
            city=data.get("PhysicalAddressCity", "Unknown"),
            province=data.get("PhysicalAddressProvince", "Unknown"),
            postal_code=data.get("PhysicalAddressPostalCode"),
            country=data.get("PhysicalAddressCountry", "Canada"),
        )

        # Store additional fields in metadata
        metadata = {
            "website": data.get("Website"),
            "taxonomy_terms": [
                term.strip()
                for term in data.get("TaxonomyTerms", "").split(";")
                if term.strip()
            ],
            "eligibility": data.get("Eligibility"),
            "fee_structure": data.get("FeeStructureSource"),
            "mailing_address": {
                "street1": data.get("MailingAddress1"),
                "street2": data.get("MailingAddress2"),
                "city": data.get("MailingCity"),
                "province": data.get("MailingStateProvince"),
                "postal_code": data.get("MailingPostalCode"),
                "country": data.get("MailingCountry"),
            },
            "hours_of_operation": data.get("HoursOfOperation"),
            "email": data.get("EmailAddressMain"),
            "agency_description": data.get("AgencyDescription"),
            "agency_description_site": data.get("AgencyDescription_Site"),
            "search_hints": data.get("SearchHints"),
            "coverage_area": data.get("CoverageArea"),
            "disabilities_access": data.get("DisabilitiesAccess"),
            "physical_location_description": data.get("PhysicalLocationDescription"),
            "application_process": data.get("ApplicationProcess"),
            "documents_required": data.get("DocumentsRequired"),
            "languages_offered": data.get("LanguagesOffered"),
            "languages_offered_list": data.get("LanguagesOfferedList"),
            "language_of_record": data.get("LanguageOfRecord"),
            "coverage": data.get("Coverage"),
            "hours": data.get("Hours"),
        }

        return Service(
            id=str(data["id"]),
            name=data["PublicName"],
            description=data.get("Description", "No description available"),
            latitude=float(data.get("Latitude", 0)),
            longitude=float(data.get("Longitude", 0)),
            phone_numbers=parse_phone_numbers(data.get("PhoneNumbers", [])),
            address=address,
            email=data.get("Email", ""),
            metadata=metadata,
            last_updated=datetime.now(),
        )
    except (ValueError, ValidationError) as e:
        logger.error(f"Error mapping service {data.get('id')}: {str(e)}")
        raise


def save_to_file(data: Dict[str, Any], file_path: Path) -> None:
    """Save the data to a JSON file."""
    mapped_services = []
    for service_data in data["Records"]:
        try:
            service = map_211_data_to_service(service_data)
            mapped_services.append(service.dict(exclude_none=True))
        except Exception as e:
            logger.error(f"Failed to process service: {e}")
            continue

    with open(file_path, "w") as f:
        json.dump(mapped_services, f, indent=2, default=str)


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
        "Fields": FIELDS,
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


def main() -> None:
    """Main function to run the script."""
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
    parser.add_argument(
        "--dataset",
        default="211CX",
        help="Dataset to download",
        choices=["211CX", "on", "nl", "nb"],
    )
    parser.add_argument(
        "--is-gta", action="store_true", help="Whether to download GTA data"
    )
    parser.add_argument(
        "--data-dir", default="/mnt/data/211", help="Directory to save data", type=Path
    )
    parser.add_argument(
        "--page-size", type=int, default=1000, help="Number of records per page"
    )

    args = parser.parse_args()

    if not args.api_key:
        raise ValueError("211_API_KEY environment variable is not set")

    # Setup HTTP session with retries
    session = RetryableSession()

    # Create data directory
    data_dir = args.data_dir / ("gta" if args.is_gta else args.dataset)
    data_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Fetch first page to get total count
        response = session.post(
            args.base_url,
            headers={"Content-Type": "application/json"},
            params={"key": args.api_key},
            json=create_payload(0, args.dataset, args.is_gta, args.page_size),
        )
        response.raise_for_status()
        first_page = response.json()

        total_records = first_page["RecordCount"]
        total_pages = math.ceil(total_records / args.page_size)

        logger.info(f"Total records: {total_records}")
        logger.info(f"Total pages: {total_pages}")

        # Process all pages
        for page in range(total_pages):
            logger.info(f"Fetching page {page + 1} of {total_pages}")

            response = session.post(
                args.base_url,
                headers={"Content-Type": "application/json"},
                params={"key": args.api_key},
                json=create_payload(page, args.dataset, args.is_gta, args.page_size),
            )
            response.raise_for_status()

            file_path = data_dir / f"data-{page:02d}.json"
            save_to_file(response.json(), file_path)
            logger.info(f"Saved data to {file_path}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()

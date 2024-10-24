"""Download data from the 211 API."""

import os
import requests
from dotenv import load_dotenv
import json
import math
from pathlib import Path
import argparse
from typing import Dict, Any, Optional

from api.data import ServiceType


def map_211_data_to_service(data: Dict[str, Any]) -> Dict[str, Any]:
    """Map 211 API data to standardized Service format."""
    # Map phone numbers
    phone_numbers = []
    if data.get("PhoneNumbers"):
        for phone in data["PhoneNumbers"]:
            phone_numbers.append(
                {
                    "number": phone.get("Number", ""),
                    "type": phone.get("Type"),
                    "name": phone.get("Name"),
                    "description": phone.get("Description"),
                    "extension": phone.get("Extension"),
                }
            )

    # Map addresses
    physical_address = {
        "street1": data.get("PhysicalAddressStreet1"),
        "street2": data.get("PhysicalAddressStreet2"),
        "city": data.get("PhysicalAddressCity"),
        "province": data.get("PhysicalAddressProvince"),
        "postal_code": data.get("PhysicalAddressPostalCode"),
        "country": data.get("PhysicalAddressCountry"),
    }

    mailing_address = {
        "street1": data.get("MailingAddressStreet1"),
        "street2": data.get("MailingAddressStreet2"),
        "city": data.get("MailingAddressCity"),
        "province": data.get("MailingAddressProvince"),
        "postal_code": data.get("MailingAddressPostalCode"),
        "country": data.get("MailingAddressCountry"),
        "attention_name": data.get("MailingAttentionName"),
    }

    # Handle age parsing
    def parse_age(age_str: Optional[str]) -> Optional[int]:
        if not age_str:
            return None
        try:
            return int(float(age_str))
        except (ValueError, TypeError):
            return None

    return {
        "id": data["id"],
        "name": data["PublicName"],
        "service_type": ServiceType.UNKNOWN.value,
        "source_id": data.get("UniqueIDPriorSystem"),
        "official_name": data.get("OfficialName"),
        "latitude": float(data["Latitude"]) if data.get("Latitude") else 0.0,
        "longitude": float(data["Longitude"]) if data.get("Longitude") else 0.0,
        "physical_address": physical_address,
        "mailing_address": mailing_address,
        "phone_numbers": phone_numbers,
        "email": data.get("Email"),
        "website": data.get("Website"),
        "description": data.get("Description"),
        "taxonomy_terms": [
            term.strip()
            for term in data.get("TaxonomyTerms", "").split(";")
            if term.strip()
        ],
        "taxonomy_codes": [
            code.strip()
            for code in data.get("TaxonomyCodes", "").split(";")
            if code.strip()
        ],
        "eligibility_criteria": data.get("Eligibility"),
        "fee_structure": data.get("FeeStructureSource"),
        "min_age": parse_age(data.get("MinAge", "")),
        "max_age": parse_age(data.get("MaxAge", "")),
        "last_updated": data.get("UpdatedOn"),
        "record_owner": data.get("RecordOwner"),
        "data_source": "211",
    }


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
        "Fields": "TaxonomyTerm,TaxonomyTerms,TaxonomyCodes,Eligibility,FeeStructureSource,OfficialName,PhysicalCity,UniqueIDPriorSystem",
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


def save_to_file(data: Dict[str, Any], file_name: str) -> None:
    """Save the data to a JSON file."""
    mapped_services = [map_211_data_to_service(service) for service in data["Records"]]
    with open(file_name, "w") as f:
        json.dump(mapped_services, f, indent=2)


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

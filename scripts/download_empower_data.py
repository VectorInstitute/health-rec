"""Download data from the Empower API."""

import argparse
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv

from api.data import Address, PhoneNumber, Service


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def map_empower_data_to_service(data: Dict[str, Any]) -> Service:
    """Map Empower API data to unified Service model."""
    try:
        # Parse required fields
        phones = []
        if data.get("phone"):
            phones.append(PhoneNumber(number=data["phone"], type="primary"))
        if not phones:
            phones = [PhoneNumber(number="Unknown")]

        address = Address(
            street1=data.get("address", "Unknown"),
            city=data.get("city", "Unknown"),
            province=data.get("province", "Unknown"),
            postal_code=data.get("postal_code"),
            country="Canada",
        )

        # Store additional fields in metadata
        metadata = {
            "type": data.get("type"),
            "services": data.get("services", []),
            "languages": data.get("languages", []),
            "hours": [
                {
                    "day": hour["day"],
                    "is_open": hour["is_open"],
                    "open_time": hour.get("opentime"),
                    "close_time": hour.get("closetime"),
                    "is_24hour": hour.get("is_24hour", False),
                }
                for hour in data.get("hours", [])
                if all(key in hour for key in ["day", "is_open"])
            ],
            "website": data.get("website"),
            "fax": data.get("fax"),
            "wheelchair_accessible": data.get("wheelchair"),
            "parking": data.get("parking"),
            "accepts_new_patients": data.get("new_patients", False),
            "has_online_booking": data.get("has_ebooking", False),
            "wait_time": data.get("wait_time"),
            "timezone_offset": data.get("tzoffset"),
        }

        return Service(
            id=str(data["id"]),
            name=data["name"],
            description=data.get("description", "No description available"),
            latitude=float(data.get("lat", 0)),
            longitude=float(data.get("long", 0)),
            phone_numbers=phones,
            address=address,
            email=data.get("email", ""),
            metadata=metadata,
            last_updated=datetime.now(),
        )
    except Exception as e:
        logger.error(f"Error mapping service {data.get('id')}: {str(e)}")
        raise


class EmpowerDataFetcher:
    """Fetcher for Empower API data."""

    def __init__(self, api_key: str, base_url: str):
        """Initialize the EmpowerDataFetcher."""
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0",
            "platform": "web",
            "lang_prefs": "en",
        }
        self.provider_types = {
            1: "Emergency Rooms",
            2: "Urgent Care Centre",
            3: "Primary Care Walk-In Clinic",
            4: "Retail Pharmacy",
            5: "Medical Labs & Diagnostic Imaging Centres",
            11: "Family Doctor's Office",
        }

    def map_provider_type(self, type_id: int) -> str:
        """Map provider type ID to human-readable string."""
        return self.provider_types.get(type_id, f"Unknown Type ({type_id})")

    def fetch_providers_list(
        self, lat: float, long: float, radius: float, page: int
    ) -> Dict[str, Any]:
        """Fetch list of providers for a given page."""
        url = f"{self.base_url}/providers"
        params: Dict[str, Any] = {
            "api_key": self.api_key,
            "lat": lat,
            "long": long,
            "radius": radius,
            "page": page,
        }

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        raw_data: Any = response.json()

        # Create a properly typed dictionary
        data: Dict[str, Any] = {
            "providers": raw_data.get("providers", []),
            "pages": raw_data.get("pages", {}),
        }

        # Map provider types in the response
        for provider in data["providers"]:
            if "type" in provider:
                provider["type"] = self.map_provider_type(provider["type"])

        return data

    def fetch_provider_details(self, provider_id: int) -> Dict[str, Any]:
        """Fetch detailed information for a specific provider."""
        url = f"{self.base_url}/providers/{provider_id}"
        params: Dict[str, str] = {"api_key": self.api_key}

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        raw_data: Any = response.json()

        # Create a properly typed dictionary
        data: Dict[str, Any] = dict(raw_data)

        # Map provider type in the response
        if "type" in data:
            data["type"] = self.map_provider_type(data["type"])

        return data

    def collect_provider_ids(self, lat: float, long: float, radius: float) -> List[int]:
        """Collect all provider IDs from paginated results."""
        provider_ids = []
        page = 1

        # Fetch first page to get total pages
        initial_response = self.fetch_providers_list(lat, long, radius, page)
        total_pages = initial_response["pages"]["total_pages"]

        logger.info(f"Total pages to process: {total_pages}")

        # Process all pages
        while page <= total_pages:
            logger.info(f"Fetching page {page}/{total_pages}")
            response = self.fetch_providers_list(lat, long, radius, page)

            # Extract provider IDs from current page
            for provider in response["providers"]:
                provider_ids.append(provider["id"])

            page += 1
            time.sleep(0.5)  # Rate limiting

        return provider_ids

    def fetch_all_provider_details(
        self, provider_ids: List[int], output_dir: Path
    ) -> None:
        """Fetch and save mapped provider details."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "data-00.json"

        mapped_providers = []
        total_providers = len(provider_ids)

        for idx, provider_id in enumerate(provider_ids, 1):
            logger.info(
                f"Fetching provider {idx}/{total_providers} (ID: {provider_id})"
            )
            try:
                provider_details = self.fetch_provider_details(provider_id)
                mapped_provider = map_empower_data_to_service(provider_details)
                mapped_providers.append(mapped_provider.dict(exclude_none=True))
                time.sleep(0.25)  # Rate limiting
            except Exception as e:
                logger.error(f"Failed to process provider {provider_id}: {e}")
                continue

        with open(output_file, "w") as f:
            json.dump(mapped_providers, f, indent=2, default=str)

        logger.info(f"Saved {len(mapped_providers)} provider details to {output_file}")


def main() -> None:
    """Main function to run the script."""
    load_dotenv("./.env.development")

    parser = argparse.ArgumentParser(description="Download data from the Empower API.")
    parser.add_argument(
        "--api-key",
        default=os.getenv("EMPOWER_API_KEY"),
        help="API key for Empower API",
    )
    parser.add_argument(
        "--base-url",
        default="https://empower.ca/api/v4",
        help="Base URL for Empower API",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("./data/empower"),
        help="Directory to save data",
    )

    args = parser.parse_args()

    if not args.api_key:
        raise ValueError("EMPOWER_API_KEY environment variable is not set")

    fetcher = EmpowerDataFetcher(args.api_key, args.base_url)

    # Parameters for the search
    lat = 44.051507
    long = -79.45811
    radius = 100  # km

    try:
        provider_ids = fetcher.collect_provider_ids(lat, long, radius)
        logger.info(f"Collected {len(provider_ids)} provider IDs")
        fetcher.fetch_all_provider_details(provider_ids, args.data_dir)
    except Exception as e:
        logger.error(f"Fatal error occurred: {e}")
        raise


if __name__ == "__main__":
    main()

"""Download data from the Empower API."""

import requests
from dotenv import load_dotenv
import argparse
import json
import os
from typing import List, Dict, Any, Optional
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime


class RetryableSession:
    """Session with retry capabilities."""

    def __init__(
        self,
        retries: int = 3,
        backoff_factor: float = 0.5,
        status_forcelist: Optional[List[int]] = None,
    ):
        """Initialize session with retry strategy."""
        self.session = requests.Session()
        if status_forcelist is None:
            status_forcelist = [403, 500, 502, 503, 504]

        retry_strategy = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            allowed_methods=["GET", "POST"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def get(self, *args: Any, **kwargs: Any) -> requests.Response:
        """Perform GET request with retry capability."""
        return self.session.get(*args, **kwargs)


class EmpowerDataFetcher:
    """Fetcher for Empower API data."""

    def __init__(self, api_key: str, base_url: str):
        """Initialize the EmpowerDataFetcher."""
        self.api_key = api_key
        self.base_url = base_url
        self.session = RetryableSession()
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

    def _make_request(
        self, url: str, params: Dict[str, Any], max_retries: int = 3
    ) -> Dict[str, Any]:
        """Make API request with retries and error handling."""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                time.sleep((attempt + 1) * 2)  # Exponential backoff
        raise Exception("Failed to make request after all retries")

    def map_provider_type(self, type_id: int) -> str:
        """Map provider type ID to human-readable string."""
        return self.provider_types.get(type_id, f"Unknown Type ({type_id})")

    def fetch_providers_list(
        self, lat: float, long: float, radius: float, page: int
    ) -> Dict[str, Any]:
        """Fetch list of providers for a given page."""
        url = f"{self.base_url}/providers"
        params = {
            "api_key": self.api_key,
            "lat": lat,
            "long": long,
            "radius": radius,
            "page": page,
        }

        data = self._make_request(url, params)

        for provider in data.get("providers", []):
            if "type" in provider:
                provider["type"] = self.map_provider_type(provider["type"])

        return data

    def fetch_provider_details(self, provider_id: int) -> Dict[str, Any]:
        """Fetch detailed information for a specific provider."""
        url = f"{self.base_url}/providers/{provider_id}"
        params = {"api_key": self.api_key}

        data = self._make_request(url, params)

        if "type" in data:
            data["type"] = self.map_provider_type(data["type"])

        return data

    def collect_provider_ids(self, lat: float, long: float, radius: float) -> List[int]:
        """Collect all provider IDs from paginated results."""
        provider_ids: List[int] = []
        page = 1

        initial_response = self.fetch_providers_list(lat, long, radius, page)
        total_pages = initial_response["pages"]["total_pages"]

        print(f"Total pages to process: {total_pages}")

        while page <= total_pages:
            print(f"Fetching page {page}/{total_pages}")
            try:
                response = self.fetch_providers_list(lat, long, radius, page)
                provider_ids.extend(p["id"] for p in response["providers"])
                page += 1
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"Error on page {page}: {e}. Retrying...")
                time.sleep(2)  # Wait before retry
                continue

        return provider_ids

    def fetch_all_provider_details(
        self, provider_ids: List[int], output_dir: str
    ) -> None:
        """Fetch and save mapped provider details."""
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "data-00.json")
        error_log = os.path.join(output_dir, "errors.log")

        mapped_providers = []
        failed_providers = []
        total_providers = len(provider_ids)

        for idx, provider_id in enumerate(provider_ids, 1):
            print(f"Fetching provider {idx}/{total_providers} (ID: {provider_id})")
            try:
                provider_details = self.fetch_provider_details(provider_id)
                mapped_provider = map_empower_data_to_service(provider_details)
                mapped_providers.append(mapped_provider)
                time.sleep(0.25)
            except Exception as e:
                print(f"Error fetching provider {provider_id}: {e}")
                failed_providers.append({"id": provider_id, "error": str(e)})

        # Save successful providers
        with open(output_file, "w") as f:
            json.dump(mapped_providers, f, indent=2)

        # Save failed providers
        if failed_providers:
            with open(error_log, "w") as f:
                json.dump(failed_providers, f, indent=2)

        print(f"Saved {len(mapped_providers)} provider details to {output_file}")
        if failed_providers:
            print(f"Failed to fetch {len(failed_providers)} providers. See {error_log}")


def map_empower_data_to_service(data: Dict[str, Any]) -> Dict[str, Any]:
    """Map Empower API data to standardized Service format."""
    try:
        # Convert coordinates to float
        latitude = float(data.get("lat", 0))
        longitude = float(data.get("long", 0))
    except (ValueError, TypeError):
        latitude = longitude = 0.0

    # Map operating hours
    regular_hours = []
    day_mapping = {
        0: "sunday",
        1: "monday",
        2: "tuesday",
        3: "wednesday",
        4: "thursday",
        5: "friday",
        6: "saturday",
    }

    for hour in data.get("hours", []):
        if all(key in hour for key in ["day", "is_open", "opentime", "closetime"]):
            regular_hours.append(
                {
                    "day": day_mapping[hour["day"]],
                    "is_open": hour["is_open"],
                    "is_24hour": hour.get("is_24hour", False),
                    "open_time": hour["opentime"],
                    "close_time": hour["closetime"],
                }
            )

    # Map address
    physical_address = {
        "street1": data.get("address"),
        "city": data.get("city"),
        "province": data.get("province"),
        "postal_code": data.get("postal_code"),
        "country": "Canada",
    }

    # Map phone numbers
    phone_numbers = []
    if data.get("phone"):
        phone_numbers.append({"number": data["phone"]})

    return {
        "id": data["id"],
        "name": data["name"],
        "service_type": data["type"],
        "latitude": latitude,
        "longitude": longitude,
        "physical_address": physical_address,
        "phone_numbers": phone_numbers,
        "fax": data.get("fax"),
        "email": data.get("email"),
        "website": data.get("website"),
        "description": data.get("description"),
        "services": data.get("services", []),
        "languages": data.get("languages", []),
        "status": data.get("status"),
        "regular_hours": regular_hours,
        "hours_exceptions": data.get("hours_exceptions", []),
        "timezone_offset": data.get("tzoffset"),
        "wheelchair_accessible": data.get("wheelchair", "unknown"),
        "parking_type": data.get("parking"),
        "accepts_new_patients": data.get("new_patients", False),
        "wait_time": data.get("wait_time"),
        "has_online_booking": data.get("has_ebooking", False),
        "can_book": data.get("can_book", False),
        "data_source": "Empower",
        "last_updated": datetime.now().isoformat(),
    }


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
        "--data-dir", default="./data/empower", help="Directory to save data"
    )
    parser.add_argument(
        "--lat",
        type=float,
        default=44.051507,
        help="Latitude for search center",
    )
    parser.add_argument(
        "--long",
        type=float,
        default=-79.45811,
        help="Longitude for search center",
    )
    parser.add_argument(
        "--radius",
        type=float,
        default=100,
        help="Search radius in kilometers",
    )

    args = parser.parse_args()

    if not args.api_key:
        raise ValueError("EMPOWER_API_KEY is not set")

    fetcher = EmpowerDataFetcher(args.api_key, args.base_url)

    try:
        provider_ids = fetcher.collect_provider_ids(args.lat, args.long, args.radius)
        print(f"Collected {len(provider_ids)} provider IDs")
        fetcher.fetch_all_provider_details(provider_ids, args.data_dir)
    except Exception as e:
        print(f"Fatal error occurred: {e}")


if __name__ == "__main__":
    main()

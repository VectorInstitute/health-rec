"""Download data from the Empower API."""

import requests
from dotenv import load_dotenv
import argparse
import json
import os
from typing import List, Dict, Any
import time


def map_empower_data_to_service(data: Dict[str, Any]) -> Dict[str, Any]:
    """Map Empower API data to standardized Service format."""
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
        regular_hours.append(
            {
                "day": day_mapping[hour["day"]],
                "is_open": hour["is_open"],
                "is_24hour": hour["is_24hour"],
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

    return {
        "id": data["id"],
        "name": data["name"],
        "service_type": data["type"],
        "latitude": float(data["lat"]),
        "longitude": float(data["long"]),
        "physical_address": physical_address,
        "phone_numbers": [{"number": data["phone"]}] if data.get("phone") else [],
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
        "accepts_new_patients": data.get("new_patients"),
        "wait_time": data.get("wait_time"),
        "has_online_booking": data.get("has_ebooking", False),
        "can_book": data.get("can_book", False),
        "data_source": "Empower",
    }


class EmpowerDataFetcher:
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
        # Provider type mapping as per API documentation[1]
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
        data = response.json()

        # Map provider types in the response
        for provider in data.get("providers", []):
            if "type" in provider:
                provider["type"] = self.map_provider_type(provider["type"])

        return data  # type: ignore

    def fetch_provider_details(self, provider_id: int) -> Dict[str, Any]:
        """Fetch detailed information for a specific provider."""
        url = f"{self.base_url}/providers/{provider_id}"
        params: Dict[str, str] = {"api_key": self.api_key}

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        data = response.json()

        # Map provider type in the response
        if "type" in data:
            data["type"] = self.map_provider_type(data["type"])

        return data  # type: ignore

    def collect_provider_ids(self, lat: float, long: float, radius: float) -> List[int]:
        """Collect all provider IDs from paginated results."""
        provider_ids = []
        page = 1

        # Fetch first page to get total pages
        initial_response = self.fetch_providers_list(lat, long, radius, page)
        total_pages = initial_response["pages"]["total_pages"]

        print(f"Total pages to process: {total_pages}")

        # Process all pages
        while page <= total_pages:
            print(f"Fetching page {page}/{total_pages}")
            response = self.fetch_providers_list(lat, long, radius, page)

            # Extract provider IDs from current page
            for provider in response["providers"]:
                provider_ids.append(provider["id"])

            page += 1
            time.sleep(0.5)  # Rate limiting

        return provider_ids

    def fetch_all_provider_details(
        self, provider_ids: List[int], output_dir: str
    ) -> None:
        """Fetch and save mapped provider details."""
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "data-00.json")

        mapped_providers = []
        total_providers = len(provider_ids)

        for idx, provider_id in enumerate(provider_ids, 1):
            print(f"Fetching provider {idx}/{total_providers} (ID: {provider_id})")
            try:
                provider_details = self.fetch_provider_details(provider_id)
                mapped_provider = map_empower_data_to_service(provider_details)
                mapped_providers.append(mapped_provider)
                time.sleep(0.25)
            except requests.exceptions.RequestException as e:
                print(f"Error fetching provider {provider_id}: {e}")

        with open(output_file, "w") as f:
            json.dump(mapped_providers, f, indent=2)

        print(f"Saved all provider details to {output_file}")


def main() -> None:
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

    args = parser.parse_args()

    if not args.api_key:
        raise ValueError("EMPOWER_API_KEY is not set")
    # Initialize fetcher
    fetcher = EmpowerDataFetcher(args.api_key, args.base_url)

    # Parameters for the search
    lat = 44.051507
    long = -79.45811
    radius = 100  # km
    output_dir = args.data_dir

    try:
        # Collect all provider IDs
        provider_ids = fetcher.collect_provider_ids(lat, long, radius)
        print(f"Collected {len(provider_ids)} provider IDs")

        # Fetch and save detailed information for all providers
        fetcher.fetch_all_provider_details(provider_ids, output_dir)

    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    main()

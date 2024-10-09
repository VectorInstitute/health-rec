"""Download data from the 211 API."""

import os
import requests
from dotenv import load_dotenv
import json
import math
from pathlib import Path
import argparse
from typing import Dict, Any


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
    with open(file_name, "w") as f:
        json.dump(data, f, indent=2)


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

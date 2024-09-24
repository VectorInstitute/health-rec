"""Download data from the 211 API."""

import os
from typing import Dict
import requests
from dotenv import load_dotenv
import json
import math
from pathlib import Path


load_dotenv("./.env.development")

BASE_URL = "https://data.211support.org/api/v2/search"
API_KEY = os.getenv("211_API_KEY")
if not API_KEY:
    raise ValueError("211_API_KEY is not set")

PAGE_SIZE = 1000
DATASET = "on"
IS_GTA = True
if IS_GTA:
    DATA_DIR = "/mnt/data/211/gta"
else:
    DATA_DIR = f"/mnt/data/211/{DATASET}"
os.makedirs(DATA_DIR, exist_ok=True)


def create_payload(page_index: int) -> Dict[str, str]:
    """Create the payload for the API request."""
    payload = {
        "Dataset": DATASET,
        "Lang": "en",
        "Search": "match",
        "MatchMode": "all",
        "ExtCategory": "",
        "Distance": 100000000000,
        "SortOrder": "distance",
        "PageIndex": page_index,
        "PageSize": PAGE_SIZE,
        "Fields": "TaxonomyTerm,TaxonomyTerms,TaxonomyCodes,Eligibility,FeeStructureSource,OfficialName,PhysicalCity,UniqueIDPriorSystem",
    }

    if IS_GTA:
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


def fetch_data(page_index: int) -> Dict[str, str]:
    """Fetch data from the API for a given page index."""
    headers = {"Content-Type": "application/json"}
    params = {"key": API_KEY}

    response = requests.post(
        BASE_URL, headers=headers, params=params, json=create_payload(page_index)
    )
    response.raise_for_status()
    return response.json()


def save_to_file(data: Dict[str, str], file_name: str):
    """Save the data to a JSON file."""
    with open(file_name, "w") as f:
        json.dump(data, f, indent=2)


def main():
    first_page = fetch_data(0)
    total_records = first_page["RecordCount"]
    total_pages = math.ceil(total_records / PAGE_SIZE)

    print(f"Total records: {total_records}")
    print(f"Total pages: {total_pages}")

    for page in range(total_pages):
        print(f"Fetching page {page + 1} of {total_pages}")
        data = fetch_data(page)
        file_name = Path(f"data-{page:02d}.json")
        save_to_file(data, os.path.join(DATA_DIR, file_name))
        print(f"Saved data to {file_name}")


if __name__ == "__main__":
    main()

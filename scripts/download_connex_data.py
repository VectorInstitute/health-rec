import argparse
import json
import logging
import math
import os
from pathlib import Path
from typing import Dict, Any, List, Set

from common import RetryableSession
from fields import FIELDS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_payload(page_index: int, dataset: str, page_size: int) -> Dict[str, Any]:
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
        "SearchType": "proximity",  # Required parameter
        "Latitude": 43.6532,  # Toronto coordinates for proximity search
        "Longitude": -79.3832,
    }
    # logger.info(f"Creating payload for dataset {dataset}: {payload}")
    return payload

def download_dataset(
    api_key: str, 
    base_url: str, 
    dataset: str,
    output_dir: Path,
    page_size: int = 1000
) -> List[Dict[str, Any]]:
    """Download a complete dataset and return all services."""
    session = RetryableSession()
    all_services = []
    
    try:
        # Log the request details
        logger.info(f"Making request to {base_url}")
        logger.info(f"API Key (first 5 chars): {api_key[:5]}...")
        
        # Fetch first page to get total count
        payload = create_payload(0, dataset, page_size)
        response = session.post(
            base_url,
            headers={"Content-Type": "application/json"},
            params={"key": api_key},
            json=create_payload(0, dataset, page_size),
        )
        response.raise_for_status()
        first_page = response.json()
        
        # logger.info(f"API Response for dataset {dataset}: {first_page}")
        
        # Check if we got a valid response with RecordCount
        if "RecordCount" not in first_page:
            logger.error(f"Unexpected API response format. Keys available: {first_page.keys()}")
            raise ValueError(f"API response for dataset {dataset} missing RecordCount field")
            
        total_records = first_page["RecordCount"]
        total_pages = math.ceil(total_records / page_size)

        logger.info(f"Dataset {dataset} - Total records: {total_records}")
        logger.info(f"Dataset {dataset} - Total pages: {total_pages}")

        # Process all pages
        for page in range(total_pages):
            logger.info(f"Dataset {dataset} - Fetching page {page + 1} of {total_pages}")

            response = session.post(
                base_url,
                headers={"Content-Type": "application/json"},
                params={"key": api_key},
                json=create_payload(page, dataset, page_size),
            )
            response.raise_for_status()
            
            page_data = response.json()
            all_services.extend(page_data["Records"])
            
            # Save each page as we go
            file_path = output_dir / dataset / f"data-{page:02d}.json"
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w") as f:
                json.dump(page_data["Records"], f, indent=2)
            logger.info(f"Saved page data to {file_path}")

        return all_services

    except Exception as e:
        logger.error(f"Error downloading dataset {dataset}: {e}")
        raise

def find_connex_services(
    on_services: List[Dict[str, Any]], 
    cx_services: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Find services that exist in 211CX but not in ON dataset.
    We use the id field to identify unique services.
    """
    # Create sets of service IDs
    on_ids = {service["id"] for service in on_services}
    cx_ids = {service["id"] for service in cx_services}
    
    # Find IDs unique to CX dataset
    connex_ids = cx_ids - on_ids
    
    # Get the full service records for Connex services
    connex_services = [
        service for service in cx_services 
        if service["id"] in connex_ids
    ]
    
    return connex_services

def save_connex_data(
    connex_services: List[Dict[str, Any]], 
    output_dir: Path,
    batch_size: int = 1000
) -> None:
    """Save Connex services to JSON files in batches."""
    connex_dir = output_dir / "connex"
    connex_dir.mkdir(parents=True, exist_ok=True)
    
    # Save in batches
    for i in range(0, len(connex_services), batch_size):
        batch = connex_services[i:i + batch_size]
        file_path = connex_dir / f"data-{i//batch_size:02d}.json"
        with open(file_path, "w") as f:
            json.dump(batch, f, indent=2)
        logger.info(f"Saved {len(batch)} Connex services to {file_path}")

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download and compare 211 datasets to find Connex services."
    )
    parser.add_argument(
        "--api-key", default=os.getenv("211_API_KEY"), help="API key for 211 API"
    )
    parser.add_argument(
        "--base-url",
        default="https://data.211support.org/api/v2/search",
        help="Base URL for 211 API",
    )
    parser.add_argument(
        "--output-dir", 
        type=Path, 
        default=Path("./data/211cx"), 
        help="Directory to save data"
    )
    parser.add_argument(
        "--page-size", 
        type=int, 
        default=1000, 
        help="Number of records per page"
    )

    args = parser.parse_args()

    if not args.api_key:
        raise ValueError("211_API_KEY environment variable is not set")

    try:
        # Download both datasets
        logger.info("Downloading ON dataset...")
        on_services = download_dataset(
            args.api_key, args.base_url, "on", args.output_dir, args.page_size
        )
        
        logger.info("Downloading 211CX dataset...")
        cx_services = download_dataset(
            args.api_key, args.base_url, "211CX", args.output_dir, args.page_size
        )
        
        # Find Connex services
        logger.info("Identifying Connex services...")
        connex_services = find_connex_services(on_services, cx_services)
        logger.info(f"Found {len(connex_services)} unique Connex services")
        
        # Save Connex services
        save_connex_data(connex_services, args.output_dir)
        
        # Save summary
        summary = {
            "total_on_services": len(on_services),
            "total_cx_services": len(cx_services),
            "unique_connex_services": len(connex_services)
        }
        with open(args.output_dir / "summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Summary: {summary}")

    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main()
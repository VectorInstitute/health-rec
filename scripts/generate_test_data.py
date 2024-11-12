"""Generate test data for the health recommendation system."""

import argparse
import json
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from api.data import Address, PhoneNumber, Service

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def generate_dummy_service(service_id: int) -> Service:
    """Generate a dummy service with random data around Toronto."""
    # Generate random coordinates around Toronto
    latitude = random.uniform(43.5, 43.9)
    longitude = random.uniform(-79.7, -79.3)

    # Generate random phone number
    phone = PhoneNumber(
        number=f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
        type="primary",
    )

    # Generate random address
    address = Address(
        street1=f"{random.randint(1, 999)} {random.choice(['Main', 'Queen', 'King', 'Yonge'])} Street",
        city="Toronto",
        province="ON",
        postal_code=f"M{random.randint(1, 9)}{random.choice(['A', 'B', 'C', 'D', 'E'])}{random.randint(0, 9)} {random.choice(['A', 'B', 'C', 'D', 'E'])}{random.randint(0, 9)}{random.randint(0, 9)}",
        country="Canada",
    )

    # Generate random service type
    service_types = [
        "Medical Clinic",
        "Mental Health Center",
        "Community Support",
        "Emergency Services",
        "Addiction Services",
    ]
    service_type = random.choice(service_types)

    # Generate metadata
    metadata: Dict[str, Any] = {
        "type": service_type,
        "languages": ["English", "French"],
        "hours": [
            {
                "day": day,
                "is_open": True,
                "open_time": "09:00",
                "close_time": "17:00",
                "is_24hour": False,
            }
            for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        ],
        "website": f"https://example-{service_id}.com",
        "wheelchair_accessible": random.choice([True, False]),
        "accepts_new_patients": random.choice([True, False]),
    }

    return Service(
        id=str(service_id),
        name=f"Test Service {service_id}",
        description=f"This is a test service {service_id} providing {service_type.lower()} services.",
        latitude=latitude,
        longitude=longitude,
        phone_numbers=[phone],
        address=address,
        email=f"service{service_id}@example.com",
        metadata=metadata,
        last_updated=datetime.now(),
    )


def create_test_data(num_services: int, output_dir: Path) -> None:
    """Create test data and save to JSON file."""
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "data-00.json"

    # Generate services
    logger.info(f"Generating {num_services} test services...")
    services = [generate_dummy_service(i) for i in range(1, num_services + 1)]

    # Convert to JSON-serializable format
    json_services = [service.dict(exclude_none=True) for service in services]

    # Save to file
    with open(output_file, "w") as f:
        json.dump(json_services, f, indent=2, default=str)

    logger.info(f"Successfully saved {len(services)} services to {output_file}")


def main() -> None:
    """Main function to run the script."""
    parser = argparse.ArgumentParser(
        description="Generate test data for the health recommendation system."
    )
    parser.add_argument(
        "--num-services",
        type=int,
        default=320,
        help="Number of test services to generate",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./data/test_data"),
        help="Directory to save the test data",
    )

    args = parser.parse_args()

    try:
        create_test_data(args.num_services, args.output_dir)
    except Exception as e:
        logger.error(f"Error generating test data: {e}")
        raise


if __name__ == "__main__":
    main()

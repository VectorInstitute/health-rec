import argparse
import asyncio
import json
import logging
from typing import Dict, List, Any

import aiohttp
from tqdm.asyncio import tqdm_asyncio


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fetch_recommendation(
    session: aiohttp.ClientSession, query: Dict[str, Any], endpoint: str
) -> Dict[str, Any]:
    """Fetch recommendation from the RAG system API."""
    try:
        async with session.post(
            endpoint,
            json={"query": query["query"], "rerank": True},
        ) as response:
            if response.status == 200:
                result = await response.json()
                return {
                    "query": query["query"],
                    "answer": result["message"],
                    "context": [
                        str(service["id"]) for service in (result.get("services", []) or [])
                    ],
                    "ground_truth": query["context"],
                }
            else:
                logger.error(f"Error fetching recommendation: {response.status}")
                return None
    except Exception as e:
        logger.error(f"Exception during fetch: {e}")
        return None


async def process_samples(samples_file: str, output_file: str, batch_size: int = 5) -> None:
    """Process samples in batches and save results."""
    # Load samples
    with open(samples_file, "r") as f:
        samples = json.load(f)

    results = []
    async with aiohttp.ClientSession() as session:
        # Process in batches
        for i in range(0, len(samples), batch_size):
            batch = samples[i : i + batch_size]
            tasks = [fetch_recommendation(session, query) for query in batch]
            batch_results = await tqdm_asyncio.gather(*tasks)
            results.extend([r for r in batch_results if r is not None])

    # Save results
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    logger.info(f"Processed {len(results)} samples successfully")


def main() -> None:
    """Main function for the script."""
    parser = argparse.ArgumentParser(
        description="Collect RAG system outputs for evaluation."
    )
    parser.add_argument(
        "--input", required=True, help="Path to the synthetic dataset JSON file"
    )
    parser.add_argument(
        "--output", required=True, help="Path to save the processed results JSON file"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5,
        help="Number of queries to process in parallel",
    )
    parser.add_argument(
        "--endpoint",
        default="http://localhost:8005/recommend",
        help="URL endpoint for the RAG system API",
    )

    args = parser.parse_args()

    asyncio.run(process_samples(args.input, args.output, args.batch_size))


if __name__ == "__main__":
    main()
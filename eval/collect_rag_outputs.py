import argparse
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from tqdm import tqdm

import aiohttp
import chromadb
from chromadb.config import Settings
from chromadb.api.types import IncludeEnum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentFetcher:
    """Helper class to fetch document content from ChromaDB."""

    def __init__(self, host: str = "localhost", port: int = 8000):
        self.client = chromadb.HttpClient(
            host=host, port=port, settings=Settings(allow_reset=True)
        )

    def get_document_by_id(self, collection_name: str, doc_id: str) -> Optional[str]:
        """Fetch document content by ID."""
        try:
            collection = self.client.get_collection(collection_name)
            result = collection.get(ids=[str(doc_id)], include=[IncludeEnum.documents])
            if result and result["documents"] and result["documents"][0]:
                return result["documents"][0]
            return None
        except Exception as e:
            logger.error(f"Error fetching document {doc_id}: {e}")
            return None


async def fetch_recommendation(
    session: aiohttp.ClientSession,
    query: Dict[str, Any],
    endpoint: str,
    doc_fetcher: DocumentFetcher,
    collection_name: str,
) -> Optional[Dict[str, Any]]:
    """Fetch recommendation from the RAG system API and include document content."""
    try:
        async with session.post(
            endpoint,
            json={"query": query["query"]},
        ) as response:
            if response.status == 200:
                result = await response.json()

                # Fetch document content for retrieved services
                retrieved_contexts = []
                for service in result.get("services", []) or []:
                    doc_content = doc_fetcher.get_document_by_id(
                        collection_name, str(service["id"])
                    )
                    if doc_content:
                        retrieved_contexts.append(doc_content)

                # Fetch document content for ground truth
                ground_truth_contexts = []
                # Handle both single ID and list of IDs
                gt_ids = (
                    [query["context"]]
                    if isinstance(query["context"], (int, str))
                    else query["context"]
                )
                for gt_id in gt_ids:
                    doc_content = doc_fetcher.get_document_by_id(
                        collection_name, str(gt_id)
                    )
                    if doc_content:
                        ground_truth_contexts.append(doc_content)

                return {
                    "query": query["query"],
                    "answer": result["message"],
                    "context": retrieved_contexts,  # Now contains actual document content
                    "ground_truth": ground_truth_contexts,  # Now contains actual document content
                }
            else:
                logger.error(f"Error fetching recommendation: {response.status}")
                return None
    except Exception as e:
        logger.error(f"Exception during fetch: {e}")
        return None


async def process_samples(
    samples_file: str,
    output_file: str,
    endpoint: str,
    collection_name: str,
    chroma_host: str = "localhost",
    chroma_port: int = 8000,
    batch_size: int = 5,
) -> None:
    """Process samples in batches and save results."""
    # Load samples
    with open(samples_file, "r") as f:
        samples = json.load(f)

    # Initialize document fetcher
    doc_fetcher = DocumentFetcher(host=chroma_host, port=chroma_port)

    results: List[Dict[str, Any]] = []
    async with aiohttp.ClientSession() as session:
        # Set up progress bar for overall processing
        pbar = tqdm(total=len(samples), desc="Processing samples")

        # Process in batches
        for i in range(0, len(samples), batch_size):
            batch = samples[i : i + batch_size]
            tasks = [
                fetch_recommendation(
                    session, query, endpoint, doc_fetcher, collection_name
                )
                for query in batch
            ]
            batch_results = await asyncio.gather(*tasks)
            valid_results = [r for r in batch_results if r is not None]
            results.extend(valid_results)

            # Update progress bar with the number of successful results
            pbar.update(len(batch))
            pbar.set_postfix({"success": f"{len(valid_results)}/{len(batch)}"})

        pbar.close()

    # Save results
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    logger.info(f"Processed {len(results)}/{len(samples)} samples successfully")


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
    parser.add_argument(
        "--collection",
        default="test",
        help="Name of the ChromaDB collection",
    )
    parser.add_argument(
        "--chroma-host",
        default="localhost",
        help="ChromaDB host",
    )
    parser.add_argument(
        "--chroma-port",
        type=int,
        default=8006,
        help="ChromaDB port",
    )

    args = parser.parse_args()

    # Show overall progress message
    logger.info(f"Starting processing of samples from {args.input}")

    asyncio.run(
        process_samples(
            args.input,
            args.output,
            args.endpoint,
            args.collection,
            args.chroma_host,
            args.chroma_port,
            args.batch_size,
        )
    )


if __name__ == "__main__":
    main()

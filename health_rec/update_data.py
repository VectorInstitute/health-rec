"""
211 Service Update Data Loader.

This module provides functionality to update a ChromaDB collection with new data.

It compares existing entries with new data and
generates embeddings for changed or new entries.
"""

import hashlib
import json
import logging
from typing import Any, Dict, Optional, Tuple

from api.config import Config
from load_data import OpenAIEmbedding, get_or_create_collection, load_json_data


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def calculate_hash(content: Dict[str, Any]) -> str:
    """Calculate a hash for a dictionary content."""
    # Sort dictionary to ensure consistent hash
    content_str = json.dumps(content, sort_keys=True)
    return hashlib.sha256(content_str.encode()).hexdigest()


def prepare_document(
    service: Dict[str, Any], resource_name: str
) -> Tuple[str, Dict[str, Any], str]:
    """Prepare a document and metadata for a service entry."""
    metadata = {
        key: ", ".join(map(str, value))
        if isinstance(value, list)
        else str(value)
        if value is not None
        else ""
        for key, value in service.items()
    }
    metadata["resource"] = resource_name

    doc = " | ".join(f"{key}: {value}" for key, value in metadata.items() if value)
    service_id = str(service.get("id", " "))

    return doc, metadata, service_id


def update_data(
    file_path: str,
    host: str,
    port: int,
    collection_name: str,
    resource_name: str,
    openai_api_key: Optional[str] = None,
    embedding_model: str = Config.OPENAI_EMBEDDING,
    load_embeddings: bool = False,
) -> None:
    """
    Update a ChromaDB collection by comparing existing entries with new data.

    Only generates new embeddings for changed or new entries.

    Parameters
    ----------
    file_path : str
        Path to the JSON file containing the new data
    host : str
        The host address of the ChromaDB instance
    port : int
        The port number of the ChromaDB instance
    collection_name : str
        Name of the collection to update
    resource_name : str
        Name of the resource/data source (e.g., '211', 'Connex', 'Empower', 'Southlake')
    data_dir : str
        Directory containing JSON files to process
    openai_api_key : Optional[str]
        OpenAI API key for generating embeddings. If None, embeddings won't be generated
    embedding_model : str
        The OpenAI embedding model to use
    load_embeddings : bool
        Whether to load embeddings for the new data

    """
    logger.info("Starting update process")
    logger.info(f"File path: {file_path}")
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"Collection name: {collection_name}")
    try:
        services = load_json_data(file_path)
        logger.info(f"Loaded {len(services)} services from JSON file")

        collection = get_or_create_collection(host, port, collection_name)

        # Initialize OpenAI embedding function if API key provided
        openai_embedding = None
        if load_embeddings and openai_api_key:
            logger.info("Initializing OpenAI embedding function")
            openai_embedding = OpenAIEmbedding(
                api_key=openai_api_key, model=embedding_model
            )

        # Process each JSON file
        total_processed = 0
        total_updated = 0
        total_added = 0

        for service in services:
            total_processed += 1

            doc, metadata, service_id = prepare_document(service, resource_name)

            try:
                # Check if the document exists
                existing_result = collection.get(
                    ids=[service_id], include=["documents", "metadatas"]
                )

                needs_update = False
                if existing_result["ids"]:
                    # Compare existing document and metadata with new ones
                    existing_doc = existing_result["documents"][0]
                    existing_metadata = existing_result["metadatas"][0]

                    # generate new hash for metadata and document
                    new_metadata_hash, new_doc_hash = (
                        calculate_hash(metadata),
                        calculate_hash({"document": doc}),
                    )
                    old_metadata_hash, old_doc_hash = (
                        calculate_hash(existing_metadata),
                        calculate_hash({"document": existing_doc}),
                    )

                    if (
                        new_metadata_hash != old_metadata_hash
                        or new_doc_hash != old_doc_hash
                    ):
                        needs_update = True
                        logger.info(f"Update needed for service {service_id}")
                else:
                    # Document doesn't exist, mark for addition
                    needs_update = True
                    logger.info(f"New service found: {service_id}")

                if needs_update:
                    # Generate embedding if API key provided
                    embedding = None
                    if openai_embedding:
                        embedding = openai_embedding([doc])[0]

                    # Update or add the document
                    if existing_result["ids"]:
                        collection.update(
                            ids=[service_id],
                            embeddings=[embedding],
                            metadatas=[metadata],
                            documents=[doc],
                        )
                        total_updated += 1
                    else:
                        collection.add(
                            ids=[service_id],
                            embeddings=[embedding],
                            metadatas=[metadata],
                            documents=[doc],
                        )
                        total_added += 1

            except Exception as e:
                logger.error(f"Error processing service {service_id}: {e}")
                continue

        logger.info(
            f"Update complete. Processed: {total_processed}, "
            f"Updated: {total_updated}, Added: {total_added}"
        )

    except Exception as e:
        logger.error(f"Error updating collection: {e}")
        raise

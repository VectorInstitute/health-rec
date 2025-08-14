"""
Collection Management Script for Health-Rec RAG Application.

This script provides functionality to manage Chroma collections,
including adding, removing, updating, and inspecting collections with
data and embeddings.
"""

import argparse
import glob
import hashlib
import json
import logging
import os
from typing import Any, Dict, List

import chromadb
from chromadb.config import Settings

from api.config import Config
from load_data import load_data
from update_data import update_data


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_chroma_client() -> Any:
    """
    Get a Chroma client instance.

    Returns
    -------
    chromadb.HttpClient
        A Chroma client instance.
    """
    return chromadb.HttpClient(
        host=Config.CHROMA_HOST,
        port=Config.CHROMA_PORT,
        settings=Settings(allow_reset=True),
    )


def list_collections() -> List[str]:
    """
    List all collections in the Chroma database.

    Returns
    -------
    List[str]
        A list of collection names.
    """
    client = get_chroma_client()
    return [collection.name for collection in client.list_collections()]


def create_collection(name: str) -> None:
    """
    Create a new collection in the Chroma database.

    Parameters
    ----------
    name : str
        The name of the collection to create.
    """
    client = get_chroma_client()
    client.create_collection(name)
    logger.info(f"Created collection: {name}")


def delete_collection(name: str) -> None:
    """
    Delete a collection from the Chroma database.

    Parameters
    ----------
    name : str
        The name of the collection to delete.
    """
    client = get_chroma_client()
    client.delete_collection(name)
    logger.info(f"Deleted collection: {name}")


def load_data_to_collection(
    collection_name: str, resource_name: str, data_dir: str, load_embeddings: bool
) -> None:
    """
    Load data into a specified collection.

    Parameters
    ----------
    collection_name : str
        The name of the collection to load data into.
    resource_name : str
        The name of the resource/data source.
    data_dir : str
        The directory containing JSON files to load.
    load_embeddings : bool
        Whether to generate and load embeddings.
    """
    files = sorted(glob.glob(os.path.join(data_dir, "*.json")))
    logger.info(
        f"Loading data from {len(files)} files into collection: {collection_name}"
    )
    for file_path in files:
        load_data(
            file_path=file_path,
            host=Config.CHROMA_HOST,
            port=Config.CHROMA_PORT,
            collection_name=collection_name,
            resource_name=resource_name,
            openai_api_key=Config.OPENAI_API_KEY,
            load_embeddings=load_embeddings,
        )

    logger.info(f"Finished loading data into collection: {collection_name}")


def get_collection_details(name: str) -> Dict[str, Any]:
    """
    Get details about a specific collection.

    Parameters
    ----------
    name : str
        The name of the collection to inspect.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing details about the collection.
    """
    client = get_chroma_client()
    collection = client.get_collection(name)

    return {
        "name": name,
        "count": collection.count(),
        "metadata": collection.get(include=["metadatas"]),
    }


def print_collection_details(details: Dict[str, Any]) -> None:
    """
    Print details about a collection in a formatted manner.

    Parameters
    ----------
    details : Dict[str, Any]
        A dictionary containing details about the collection.
    """
    print(f"Collection Name: {details['name']}")
    print(f"Number of Documents: {details['count']}")


def calculate_hash(content: Dict[str, Any]) -> str:
    """Calculate a hash for a dictionary content."""
    # Sort dictionary to ensure consistent hash
    content_str = json.dumps(content, sort_keys=True)
    return hashlib.sha256(content_str.encode()).hexdigest()


def update_data_in_collection(
    collection_name: str,
    data_dir: str,
    load_embeddings: bool,
) -> None:
    """
    Update a ChromaDB collection by comparing existing entries with new data.

    Only generates new embeddings for changed or new entries.

    Parameters
    ----------
    collection_name : str
        Name of the collection to update
    data_dir : str
        Directory containing JSON files to process

    Notes
    -----
    Expects data files in the format: data-XX.json where XX is a number.

    """
    files = sorted(glob.glob(os.path.join(data_dir, "*.json")))
    logger.info(
        f"Loading data from {len(files)} files into collection: {collection_name}"
    )
    for file_path in files:
        update_data(
            file_path=file_path,
            host=Config.CHROMA_HOST,
            port=Config.CHROMA_PORT,
            collection_name=collection_name,
            openai_api_key=Config.OPENAI_API_KEY,
            load_embeddings=load_embeddings,
        )

    logger.info(f"Finished updating data into collection: {collection_name}")


def main() -> None:
    """Manage Chroma collections for Health-Rec RAG application."""
    parser = argparse.ArgumentParser(
        description="Manage Chroma collections for Health-Rec RAG application."
    )
    parser.add_argument(
        "action",
        choices=["list", "create", "delete", "load", "inspect", "update"],
        help="Action to perform",
    )
    parser.add_argument(
        "--collection_name",
        help="Name of the collection (required for create, delete, load, and inspect actions)",
    )
    parser.add_argument(
        "--data_dir",
        help="Directory containing JSON files to load (required for load action)",
    )
    parser.add_argument(
        "--load_embeddings",
        action="store_true",
        help="Generate and load embeddings (for load and update action)",
    )
    parser.add_argument(
        "--resource_name",
        help="Name of the resource/data source (optional, defaults to 'default')",
    )

    args = parser.parse_args()

    if args.action == "list":
        collections = list_collections()
        print("Available collections:")
        for collection in collections:
            print(f"- {collection}")
    elif args.action == "create":
        if not args.collection_name:
            parser.error("--collection_name is required for create action")
        create_collection(args.collection_name)
    elif args.action == "delete":
        if not args.collection_name:
            parser.error("--collection_name is required for delete action")
        delete_collection(args.collection_name)
    elif args.action == "load":
        if not args.collection_name or not args.data_dir or not args.resource_name:
            parser.error(
                "--collection_name, --data_dir, and --resource_name are required for load action"
            )
        load_data_to_collection(
            args.collection_name,
            args.resource_name,
            args.data_dir,
            args.load_embeddings,
        )
    elif args.action == "inspect":
        if not args.collection_name:
            parser.error("--collection_name is required for inspect action")
        details = get_collection_details(args.collection_name)
        print_collection_details(details)
    elif args.action == "update":
        if not args.collection_name or not args.data_dir:
            parser.error(
                "--collection_name and --data_dir are required for update action"
            )
        update_data_in_collection(
            collection_name=args.collection_name,
            data_dir=args.data_dir,
            load_embeddings=args.load_embeddings,
        )


if __name__ == "__main__":
    main()

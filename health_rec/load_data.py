"""
211 Service Data Loader and Embedder.

This module provides functionality to load 211 service data from a JSON file,
prepare it for storage in a Chroma database, and add OpenAI embeddings to the data.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple

import chromadb
import openai
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from tiktoken import get_encoding

from api.config import Config
from api.data import Service
from services.deduplication import remove_duplicates


# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class OpenAIEmbedding(EmbeddingFunction[Documents]):
    """A class to generate embeddings using OpenAI's API."""

    def __init__(self, api_key: str, model: str = Config.OPENAI_EMBEDDING):
        """Initialize the OpenAI embedding client."""
        self.client = openai.Client(api_key=api_key)
        self.model = model

    def __call__(self, texts: Documents) -> Embeddings:
        """Generate embeddings for the given texts.

        Parameters
        ----------
        texts (Documents): The texts to generate embeddings for.

        Returns
        -------
        Embeddings: The embeddings for the given texts.

        """
        try:
            response = self.client.embeddings.create(input=texts, model=self.model)
            return [data.embedding for data in response.data]  # type: ignore
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise


def load_json_data(file_path: str) -> List[Dict[str, Any]]:
    """Load 211 service data from a JSON file.

    Parameters
    ----------
    file_path (str): The path to the JSON file containing the service data.

    Returns
    -------
    List[Dict[str, Any]]: A list of dictionaries representing the service data.

    """
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            if not isinstance(data, list):
                raise ValueError("JSON file must contain a list of services")
            return data
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in file: {file_path}")
        raise


def prepare_documents(
    services: List[Dict[str, Any]],
    resource_name: str,
) -> Tuple[Documents, List[dict[str, str]], List[str]]:
    """Prepare documents, metadata, and IDs from service data for Chroma storage.

    Truncates documents that exceed the maximum token length for embeddings.
    Uses tiktoken for accurate OpenAI token counting.

    Parameters
    ----------
    services (List[Dict[str, Any]]): A list of dictionaries representing
    the service data.
    resource_name (str): The name of the resource/data source.

    Returns
    -------
    Tuple[Documents, List[Dict[str, Any]], List[str]]: A tuple containing the
    documents, metadata, and IDs.
    """
    documents: Documents = []
    metadatas: List[dict[str, str]] = []
    ids: List[str] = []

    # Get the appropriate tokenizer for the embedding model
    tokenizer = get_encoding("cl100k_base")  # Used by text-embedding API

    for service in services:
        metadata: dict[str, str] = {}
        for key, value in service.items():
            if isinstance(value, list):
                metadata[key] = ", ".join(map(str, value))
            elif isinstance(value, dict):
                # Convert dict to JSON string for ChromaDB compatibility
                metadata[key] = str(value)
            elif value is not None:
                metadata[key] = str(value)
            else:
                metadata[key] = ""
        metadata["resource"] = resource_name
        doc = " | ".join(f"{key}: {value}" for key, value in metadata.items() if value)

        # Count tokens in the document
        tokens = tokenizer.encode(doc)
        num_tokens = len(tokens)

        # Truncate document if it exceeds max token length
        if num_tokens > Config.EMBEDDING_MAX_CONTEXT_LENGTH:
            logger.warning(
                f"Document exceeds max token length ({num_tokens} > {Config.EMBEDDING_MAX_CONTEXT_LENGTH}). "
                f"Truncating document with ID: {service.get('id', 'unknown')}"
            )
            # Decode only the allowed number of tokens back to text
            doc = tokenizer.decode(tokens[: Config.EMBEDDING_MAX_CONTEXT_LENGTH])

        documents.append(doc)
        metadatas.append(metadata)
        ids.append(str(service.get("id", f"generated_{len(ids)}")))

    return documents, metadatas, ids


def get_or_create_collection(host: str, port: int, name: str) -> chromadb.Collection:
    """Get a Chroma collection or create a new one if it doesn't exist.

    Parameters
    ----------
    host (str): The host address of the Chroma database.
    port (int): The port number of the Chroma database.
    name (str): The name of the collection to get or create.

    Returns
    -------
    chromadb.Collection: The Chroma collection.

    """
    logger.info(f"Connecting to Chroma at {host}:{port}")
    chroma_client = chromadb.HttpClient(host=host, port=port)

    collection = chroma_client.get_or_create_collection(name=name)
    logger.info(f"Retrieved or created collection: {name}")
    return collection


def load_data(
    file_path: str,
    host: str,
    port: int,
    collection_name: str,
    resource_name: str,
    openai_api_key: Optional[str] = None,
    embedding_model: str = Config.OPENAI_EMBEDDING,
    batch_size: int = 100,
    load_embeddings: bool = False,
    remove_duplicates_before_load: bool = True,
) -> None:
    """Load data into Chroma database and add embeddings if OpenAI API key is provided.

    Parameters
    ----------
    file_path (str): The path to the JSON file containing the service data.
    host (str): The host address of the Chroma database.
    port (int): The port number of the Chroma database.
    collection_name (str): The name of the collection to load the data into.
    resource_name (str): The name of the resource/data source (e.g.,'211', 'Southlake').
    openai_api_key (Optional[str]): The OpenAI API key.
    embedding_model (str): The OpenAI embedding model to use.
    batch_size (int): The number of documents to process in a single batch.
    load_embeddings (bool): Whether to load embeddings into the collection.
    remove_duplicates_before_load (bool): Whether to remove duplicates before
        loading data.

    """
    logger.info("Starting the data loading process")
    logger.info(f"File path: {file_path}")
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"Collection name: {collection_name}")

    try:
        services_data = load_json_data(file_path)
        logger.info(f"Loaded {len(services_data)} services from JSON file")

        # Remove duplicates before processing if enabled
        if remove_duplicates_before_load:
            # Convert to Service objects for deduplication
            services = [Service(**service_data) for service_data in services_data]
            services, duplicates_removed = remove_duplicates(
                services, keep_strategy="most_recent"
            )
            if duplicates_removed > 0:
                logger.info(
                    f"Removed {duplicates_removed} duplicate services during data loading"
                )
            # Convert back to dict format
            services_data = [
                service.model_dump(exclude_none=True) for service in services
            ]

        documents, metadatas, ids = prepare_documents(services_data, resource_name)
        collection = get_or_create_collection(host, port, collection_name)

        if load_embeddings and openai_api_key:
            logger.info("OpenAI API key provided. Generating embeddings.")
            openai_embedding = OpenAIEmbedding(
                api_key=openai_api_key, model=embedding_model
            )

            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i : i + batch_size]
                batch_metadatas = metadatas[i : i + batch_size]
                batch_ids = ids[i : i + batch_size]

                embeddings = openai_embedding(batch_docs)
                collection.add(
                    documents=batch_docs,
                    metadatas=batch_metadatas,  # type: ignore
                    ids=batch_ids,
                    embeddings=embeddings,
                )
                logger.info(
                    f"Added documents {i} to {i + len(batch_docs)} with embeddings"
                )

            logger.info("Completed the data loading and embedding process")
        else:
            logger.info(
                "OpenAI API key not provided or load_embeddings is False. Adding documents without embeddings."
            )
            collection.add(documents=documents, metadatas=metadatas, ids=ids)  # type: ignore
            logger.info(
                "Data uploaded successfully, but embeddings were not generated."
            )

        logger.info("Data loading process completed")
    except Exception as e:
        logger.error(f"Error in data loading process: {e}")
        raise

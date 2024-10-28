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

from api.config import Config


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
            return [data.embedding for data in response.data]
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
) -> Tuple[Documents, List[Dict[str, Any]], List[str]]:
    """Prepare documents, metadata, and IDs from service data for Chroma storage.

    Parameters
    ----------
    services (List[Dict[str, Any]]): A list of dictionaries representing
    the service data.

    Returns
    -------
    Tuple[Documents, List[Dict[str, Any]], List[str]]: A tuple containing the
    documents, metadata, and IDs.

    """
    documents: Documents = []
    metadatas: List[Dict[str, Any]] = []
    ids: List[str] = []

    for service in services:
        metadata = {
            key: ", ".join(map(str, value))
            if isinstance(value, list)
            else str(value)
            if value is not None
            else ""
            for key, value in service.items()
        }
        doc = " | ".join(f"{key}: {value}" for key, value in metadata.items() if value)
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

    try:
        collection = chroma_client.get_collection(name=name)
        logger.info(f"Retrieved existing collection: {name}")
    except ValueError:
        logger.info(f"Creating new collection: {name}")
        collection = chroma_client.create_collection(name=name)

    return collection


def load_data(
    file_path: str,
    host: str,
    port: int,
    collection_name: str,
    openai_api_key: Optional[str] = None,
    embedding_model: str = Config.OPENAI_EMBEDDING,
    batch_size: int = 100,
    load_embeddings: bool = False,
) -> None:
    """Load data into Chroma database and add embeddings if OpenAI API key is provided.

    Parameters
    ----------
    file_path (str): The path to the JSON file containing the service data.
    host (str): The host address of the Chroma database.
    port (int): The port number of the Chroma database.
    collection_name (str): The name of the collection to load the data into.
    openai_api_key (Optional[str]): The OpenAI API key.
    embedding_model (str): The OpenAI embedding model to use.
    batch_size (int): The number of documents to process in a single batch.
    load_embeddings (bool): Whether to load embeddings into the collection.

    """
    logger.info("Starting the data loading process")
    logger.info(f"File path: {file_path}")
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"Collection name: {collection_name}")

    try:
        services = load_json_data(file_path)
        logger.info(f"Loaded {len(services)} services from JSON file")

        documents, metadatas, ids = prepare_documents(services)
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
                    f"Added documents {i} to {i+len(batch_docs)} with embeddings"
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

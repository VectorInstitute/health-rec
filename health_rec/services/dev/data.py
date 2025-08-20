"""Data services for development."""

from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection

# IncludeEnum no longer exists in ChromaDB 1.0, use literal strings instead
from api.config import Config
from services.utils import _metadata_to_service


class ChromaService:
    """ChromaDB service for development."""

    def __init__(self) -> None:
        """Initialize the ChromaDB service."""
        self.client = chromadb.HttpClient(
            host=Config.CHROMA_HOST, port=Config.CHROMA_PORT
        )
        self.collection: Collection = self.client.get_collection(Config.COLLECTION_NAME)

    async def get_all_services(self) -> Any:
        """
        Get all services from the ChromaDB collection.

        Returns
        -------
        List[Service]
            A list of services.
        """
        result = self.collection.get(include=["metadatas"])
        if result["metadatas"] is not None:
            return [_metadata_to_service(metadata) for metadata in result["metadatas"]]
        return []

    async def get_services_count(self) -> Any:
        """
        Get the number of services in the ChromaDB collection.

        Returns
        -------
        int
            The number of services.
        """
        return self.collection.count()

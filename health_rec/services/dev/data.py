"""Data services for development."""

from typing import List

import chromadb
from chromadb.api.models.Collection import Collection

from api.config import Config
from api.data import Service
from services.utils import _metadata_to_service


class ChromaService:
    """ChromaDB service for development."""

    def __init__(self):
        """Initialize the ChromaDB service."""
        self.client: chromadb.HttpClient = chromadb.HttpClient(
            host=Config.CHROMA_HOST, port=Config.CHROMA_PORT
        )
        self.collection: Collection = self.client.get_collection(Config.COLLECTION_NAME)

    async def get_all_services(self) -> List[Service]:
        """
        Get all services from the ChromaDB collection.

        Returns
        -------
        List[Service]
            A list of services.
        """
        result = self.collection.get(include=["metadatas"])
        return [_metadata_to_service(metadata) for metadata in result["metadatas"]]

    async def get_services_count(self) -> int:
        """
        Get the number of services in the ChromaDB collection.

        Returns
        -------
        int
            The number of services.
        """
        return self.collection.count()

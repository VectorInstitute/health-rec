"""Data services for development."""

from typing import List

import chromadb

from api.config import Config
from api.data import Service


class ChromaService:
    """ChromaDB service for development."""

    def __init__(self):
        """Initialize the ChromaDB service."""
        self.client = chromadb.HttpClient(
            host=Config.CHROMA_HOST, port=Config.CHROMA_PORT
        )
        self.collection = self.client.get_collection("test")

    async def get_all_services(self) -> List[Service]:
        """Get all services from the ChromaDB collection.

        Returns
        -------
        List[Service]
            A list of services.

        """
        result = self.collection.get(include=["metadatas"])
        services = []
        for metadata in result["metadatas"]:
            if "ServiceArea" in metadata and isinstance(metadata["ServiceArea"], str):
                metadata["ServiceArea"] = [metadata["ServiceArea"]]
            if "Latitude" in metadata:
                metadata["Latitude"] = float(metadata["Latitude"])
            if "Longitude" in metadata:
                metadata["Longitude"] = float(metadata["Longitude"])

            service = Service(
                id=metadata["id"],
                public_name=metadata["PublicName"],
                description=metadata["Description"],
                service_area=metadata["ServiceArea"],
                latitude=float(metadata["Latitude"]),
                longitude=float(metadata["Longitude"]),
            )
            services.append(service)
        return services

    async def get_services_count(self) -> int:
        """Get the number of services in the ChromaDB collection.

        Returns
        -------
        int
            The number of services.

        """
        return self.collection.count()

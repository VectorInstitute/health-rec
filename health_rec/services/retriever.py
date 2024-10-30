import logging
from dataclasses import dataclass
from typing import List

import chromadb
import openai
from chromadb.api.models.Collection import Collection
from chromadb.api.types import QueryResult

from api.config import Config
from api.data import ServiceDocument
from services.utils import _parse_chroma_result


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Retriever:
    """Service for retrieving documents using ChromaDB vector similarity search."""

    def __init__(self) -> None:
        """Initialize the retriever service."""
        self.client = openai.Client(api_key=Config.OPENAI_API_KEY)
        self.embedding_model = Config.OPENAI_EMBEDDING
        self.chroma_client = chromadb.HttpClient(
            host=Config.CHROMA_HOST,
            port=Config.CHROMA_PORT
        )
        self.collection: Collection = self.chroma_client.get_collection(
            name=Config.COLLECTION_NAME
        )

    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for the input text.

        Parameters
        ----------
        text : str
            The text to generate an embedding for.

        Returns
        -------
        List[float]
            The generated embedding vector.

        Raises
        ------
        ValueError
            If there's an error generating the embedding.
        """
        try:
            return (
                self.client.embeddings.create(
                    input=[text],
                    model=self.embedding_model
                )
                .data[0]
                .embedding
            )
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise ValueError("Failed to generate embedding") from e

    def retrieve(self, query: str, n_results: int = 5) -> List[ServiceDocument]:
        """
        Retrieve relevant documents based on the query.

        Parameters
        ----------
        query : str
            The search query.

        Returns
        -------
        List[ServiceDocument]
            List of retrieved service documents.

        Raises
        ------
        Exception
            If there's an error during the retrieval process.
        """
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query)

            # Retrieve documents from ChromaDB
            results: QueryResult = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results
            )

            # Parse and return results
            return _parse_chroma_result(results)

        except Exception as e:
            logger.error(f"Error in Retriever.retrieve: {e}")
            raise
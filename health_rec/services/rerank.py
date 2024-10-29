"""Service for re-ranking retrieved health services using LLM."""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

import chromadb
import openai
from chromadb.api.models.Collection import Collection
from chromadb.api.types import QueryResult

from api.config import Config
from api.data import Service, ServiceDocument
from services.utils import _metadata_to_service, _parse_chroma_result


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class RerankingConfig:
    """Configuration for re-ranking parameters."""

    retrieval_k: int = 20  # Number of services to retrieve initially
    output_k: int = 5  # Number of services to return after re-ranking
    max_content_length: int = 150  # Maximum length of service content to consider


class ReRankingService:
    """Service for re-ranking retrieved health services using LLM.

    Based on RankGPT: https://arxiv.org/abs/2304.09542

    """

    def __init__(self, config: Optional[RerankingConfig] = None) -> None:
        """Initialize the re-ranking service."""
        self.client = openai.Client(api_key=Config.OPENAI_API_KEY)
        self.embedding_model = Config.OPENAI_EMBEDDING
        self.chroma_client = chromadb.HttpClient(
            host=Config.CHROMA_HOST, port=Config.CHROMA_PORT
        )
        self.services_collection: Collection = self.chroma_client.get_collection(
            name=Config.COLLECTION_NAME
        )
        self.config = config or RerankingConfig()

    def _create_ranking_prompt(
        self, query: str, services: List[Service]
    ) -> List[Dict[str, str]]:
        """Create the prompt for ranking services."""
        messages = [
            {
                "role": "system",
                "content": "You are a health service recommender that ranks services based on their relevance to a user's query. Respond only with the ranked service numbers in descending order of relevance, separated by '>'.",
            },
            {
                "role": "user",
                "content": f"I will provide you with {len(services)} services, each indicated by number identifier []. \nRank these services based on their relevance to query: {query}",
            },
            {
                "role": "assistant",
                "content": "I'll rank the services. Please provide them.",
            },
        ]

        # Add each service as a separate message
        for i, service in enumerate(services, 1):
            content = f"{service.public_name or ''}\n{service.description or ''}\n{service.eligibility or ''}"
            content = " ".join(content.split()[: self.config.max_content_length])
            messages.append({"role": "user", "content": f"[{i}] {content}"})
            messages.append(
                {"role": "assistant", "content": f"Received service [{i}]."}
            )

        # Add final ranking request
        messages.append(
            {
                "role": "user",
                "content": f"""For the query "{query}", rank the services from most to least relevant.
            Respond only with service numbers in the format: [X] > [Y] > [Z]""",
            }
        )

        return messages

    def _process_ranking_response(
        self, response: str, services: QueryResult
    ) -> List[ServiceDocument]:
        """Process the LLM's ranking response and return reordered services."""
        try:
            documents: List[ServiceDocument] = _parse_chroma_result(services)
            # Extract numbers from the response
            rankings = [
                int(x) - 1
                for x in "".join(c if c.isdigit() else " " for c in response).split()
            ]

            # Remove any invalid indices
            valid_rankings = [i for i in rankings if 0 <= i < len(documents)]

            # Add any missing indices at the end
            all_indices = set(range(len(documents)))
            missing_indices = [i for i in all_indices if i not in valid_rankings]
            rankings = valid_rankings + missing_indices

            # Return reordered services limited to output_k
            return [documents[i] for i in rankings[: self.config.output_k]]

        except Exception as e:
            logger.error(f"Error processing ranking response: {e}")
            # Fall back to original order if parsing fails
            return documents[: self.config.output_k]

    def rerank(self, query: str, query_embedding: List[float]) -> List[ServiceDocument]:
        """
        Generate re-ranked list of services for the query.

        Parameters
        ----------
        query : str
            The user's input query.

        Returns
        -------
        List[Service]
            The re-ranked list of services.
        """
        # Retrieve initial services
        results = self.services_collection.query(
            query_embeddings=query_embedding, n_results=self.config.retrieval_k
        )

        # Convert to Service objects
        services = [
            _metadata_to_service(meta)
            for meta in (results["metadatas"][0] if results["metadatas"] else [])
        ]

        if not services:
            return []

        # Create ranking prompt
        messages = self._create_ranking_prompt(query, services)

        # Get re-ranking from LLM
        completion = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,  # type: ignore
            temperature=0,
        )

        response_content = completion.choices[0].message.content
        if response_content is None:
            raise ValueError("Received empty response from OpenAI API")

        # Process and return results
        return self._process_ranking_response(response_content, results)

"""Service for re-ranking retrieved health services using LLM."""

import logging
from typing import Dict, List

import openai

from api.config import Config
from api.data import ServiceDocument


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ReRankingService:
    """Service for re-ranking retrieved health services using LLM."""

    def __init__(self) -> None:
        """Initialize the re-ranking service."""
        self.client = openai.Client(api_key=Config.OPENAI_API_KEY)
        self.max_content_length = Config.MAX_CONTEXT_LENGTH

    def _create_ranking_prompt(
        self, query: str, services: List[ServiceDocument]
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

        for i, service in enumerate(services, 1):
            content = f"{service.metadata.get('Description', '')}\n{service.metadata.get('Eligibility', '')}"
            content = " ".join(content.split()[: self.max_content_length])
            messages.append({"role": "user", "content": f"[{i}] {content}"})
            messages.append(
                {"role": "assistant", "content": f"Received service [{i}]."}
            )

        messages.append(
            {
                "role": "user",
                "content": f"""For the query "{query}", rank the services from most to least relevant.
            Respond only with service numbers in the format: [X] > [Y] > [Z]""",
            }
        )

        return messages

    def rerank(
        self, query: str, services: List[ServiceDocument]
    ) -> List[ServiceDocument]:
        """Rerank the provided services based on the query.

        Parameters
        ----------
        query : str
            The query for which the services are being reranked.
        services : List[ServiceDocument]
            The list of services to be reranked.

        Returns
        -------
        List[ServiceDocument]
            The reranked services.

        """
        if not services:
            return []

        try:
            messages = self._create_ranking_prompt(query, services)
            completion = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,  # type: ignore
                temperature=0,
            )

            response_content = completion.choices[0].message.content
            if response_content is None:
                raise ValueError("Received empty response from OpenAI API")

            # Extract rankings from response
            rankings = [
                int(x) - 1
                for x in "".join(
                    c if c.isdigit() else " " for c in response_content
                ).split()
            ]

            # Remove invalid indices and add missing ones
            valid_rankings = [i for i in rankings if 0 <= i < len(services)]
            all_indices = set(range(len(services)))
            missing_indices = [i for i in all_indices if i not in valid_rankings]
            rankings = valid_rankings + missing_indices

            # Return reordered services
            return [services[i] for i in rankings]

        except Exception as e:
            logger.error(f"Error in reranking: {e}")
            return services

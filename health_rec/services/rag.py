"""Module to provide a RAG (Retrieval-Augmented Generation) service."""

import logging
from typing import List, Tuple

import openai

from api.config import Config
from api.data import Query, RecommendationResponse, ServiceDocument
from services.emergency import get_emergency_services_message
from services.ranking import _calculate_distance
from services.rerank import ReRankingService
from services.retriever import Retriever
from services.utils import _metadata_to_service


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RAGService:
    """RAG service with optional reranking and location filtering."""

    def __init__(self) -> None:
        """Initialize the RAG service."""
        self.client = openai.Client(api_key=Config.OPENAI_API_KEY)
        self.retriever = Retriever()
        self.reranker = ReRankingService()

    def _filter_by_location(
        self,
        services: List[ServiceDocument],
        location: Tuple[float, float],
        radius: float,
    ) -> List[ServiceDocument]:
        """Filter services by location and radius."""
        filtered_services = []
        for service in services:
            if service.metadata.get("latitude") and service.metadata.get("longitude"):
                service_location = (
                    float(service.metadata["latitude"]),
                    float(service.metadata["longitude"]),
                )
                distance = _calculate_distance(service_location, location)
                if distance <= radius:
                    service.distance = distance
                    filtered_services.append(service)
        return filtered_services

    def _generate_response(self, query: str, context: str) -> RecommendationResponse:
        """Generate a response using the RAG prompt."""
        generation_template = """
        You are an expert with deep knowledge of health and community services. You will be providing a recommendation to an individual who is seeking help. The individual is seeking help with the following query:

        <QUERY>
        {query}
        </QUERY>

        If you determine that the individual has an emergency need, respond with only the word "EMERGENCY" (in all caps).
        If you determine that the individual's query is not for a health or community service, respond with an appropriate out of scope message in relation to the query. Structure your response as follows:
        Response: A brief explanation of why the query is out of scope.
        Reasoning: Provide more detailed reasoning for why this query cannot be answered within the context of health and community services.
        If no services are found within the context, respond with the word "NO_SERVICES_FOUND" (in all caps).

        If the individual does not need emergency help and the query is within scope, use only the following service context enclosed by the <CONTEXT> tag to provide a service recommendation.

        <CONTEXT>
        {context}
        </CONTEXT>

        Your response for in-scope queries should be structured as follows:
        Overview: A brief overview of the most relevant service.
        Reasoning: Why this service is recommended and any other helpful information.

        Do not use any special formatting or markdown in your response.
        """

        try:
            completion = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "user",
                        "content": generation_template.format(
                            query=query, context=context
                        ),
                    }
                ],
                max_tokens=500,
            )

            response_content = completion.choices[0].message.content
            if response_content is None:
                raise ValueError("Received empty response from OpenAI API")

            response_content = response_content.strip()
            if response_content == "EMERGENCY":
                return RecommendationResponse(
                    is_emergency=True,
                    message=get_emergency_services_message(),
                    is_out_of_scope=False,
                    services=[],
                )
            if response_content == "NO_SERVICES_FOUND":
                return RecommendationResponse(
                    is_emergency=False,
                    message="No services found within the specified criteria.",
                    is_out_of_scope=False,
                    services=[],
                    no_services_found=True,
                )
            if response_content.startswith("Response:"):
                return RecommendationResponse(
                    is_emergency=False,
                    message=response_content,
                    is_out_of_scope=True,
                    services=[],
                )
            return RecommendationResponse(
                is_emergency=False,
                message=response_content,
                is_out_of_scope=False,
                services=[],
            )

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    def generate(
        self,
        query: Query,
    ) -> RecommendationResponse:
        """
        Generate a response based on the input query using RAG methodology.

        Parameters
        ----------
        query : Query
            The user's input query with optional location data and reraanking flag.


        Returns
        -------
        RecommendationResponse
            The generated recommendation response.
        """
        try:
            # Retrieve services with appropriate n_results
            n_results = Config.RERANKER_MAX_SERVICES if query.rerank else Config.TOP_K
            services = self.retriever.retrieve(query.query, n_results=n_results)

            # Apply location filtering if location data is provided
            if query.latitude and query.longitude and query.radius:
                location = (query.latitude, query.longitude)
                services = self._filter_by_location(services, location, query.radius)

            if not services:
                return RecommendationResponse(
                    message="No services found within the specified criteria.",
                    is_emergency=False,
                    is_out_of_scope=False,
                    services=[],
                    no_services_found=True,
                )

            # Apply reranking if requested and take top 5
            if query.rerank:
                services = self.reranker.rerank(query.query, services)
                services = services[: Config.TOP_K]

            # Prepare context for response generation with truncation
            context = "\n".join(
                [
                    " ".join(service.document.split()[: Config.MAX_CONTEXT_LENGTH])
                    for service in services
                ]
            )

            # Generate the response
            response = self._generate_response(query.query, context)

            # Add services to the response if it's not emergency or out of scope
            if not response.is_emergency and not response.is_out_of_scope:
                response.services = [_metadata_to_service(s.metadata) for s in services]

            return response

        except Exception as e:
            logger.error(f"Error in RAG generation: {e}")
            raise

"""Module to provide a RAG (Retrieval-Augmented Generation) service."""

import logging
from typing import List, Tuple

import chromadb
import openai
from chromadb.api.models.Collection import Collection

from api.config import Config
from api.data import Query, RecommendationResponse, Service, ServiceDocument
from services.emergency import get_emergency_services_message
from services.ranking import RankingService
from services.rerank import RerankingConfig, ReRankingService
from services.utils import _metadata_to_service


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RAGService:
    """RAG service."""

    def __init__(self) -> None:
        """Initialize the RAG service."""
        self.client: openai.Client = openai.Client(api_key=Config.OPENAI_API_KEY)
        self.embedding_model: str = Config.OPENAI_EMBEDDING
        self.chroma_client = chromadb.HttpClient(
            host=Config.CHROMA_HOST, port=Config.CHROMA_PORT
        )
        self.services_collection: Collection = self.chroma_client.get_collection(
            name=Config.COLLECTION_NAME
        )
        self.ranking_service = RankingService(relevancy_weight=Config.RELEVANCY_WEIGHT)
        self.reranking_service = ReRankingService(RerankingConfig())

    def generate(self, query: Query) -> RecommendationResponse:
        """
        Generate a response based on the input query using RAG methodology.

        Parameters
        ----------
        query : Query
            The user's input query for which a recommendation is requested.

        Returns
        -------
        RecommendationResponse
            An object containing the generated recommendation and relevant services.

        Raises
        ------
        ValueError
            If there's an error generating the embedding for the query.
        """
        query_embedding = self._generate_query_embedding(query.query)
        service_documents = self._retrieve_and_rank_services(query, query_embedding)
        context, no_services_found = self._prepare_context(service_documents)
        response = self._generate_response(query.query, context)

        if response.is_out_of_scope or response.is_emergency:
            return RecommendationResponse(
                is_emergency=response.is_emergency,
                message=response.message,
                is_out_of_scope=response.is_out_of_scope,
                services=[],
            )

        services = self._convert_documents_to_services(service_documents)

        return RecommendationResponse(
            message=response.message,
            is_emergency=response.is_emergency,
            is_out_of_scope=response.is_out_of_scope,
            services=services,
            no_services_found=no_services_found,
        )

    def _generate_query_embedding(self, query_text: str) -> List[float]:
        """Generate embedding for the query."""
        try:
            return (
                self.client.embeddings.create(
                    input=[query_text], model=self.embedding_model
                )
                .data[0]
                .embedding
            )
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise ValueError("Failed to generate embedding for the query") from e

    def _retrieve_and_rank_services(
        self, query: Query, query_embedding: List[float]
    ) -> List[ServiceDocument]:
        """Retrieve and rank services based on the query."""
        service_documents = self.reranking_service.rerank(query.query, query_embedding)

        user_location = (
            (query.latitude, query.longitude)
            if query.latitude and query.longitude
            else None
        )
        service_documents = self.ranking_service.rank_services(
            service_documents, user_location
        )
        if query.radius:
            logger.info(f"Filtering services by radius: {query.radius}")
            service_documents = [
                doc for doc in service_documents if doc.distance <= query.radius
            ]
            for service in service_documents:
                logger.info(
                    f"Service name: {service.metadata['PublicName']}, distance: {service.distance}"
                )
        return list(service_documents)

    def _prepare_context(
        self, service_documents: List[ServiceDocument]
    ) -> Tuple[str, bool]:
        """Prepare context from service documents."""
        context = "\n".join([service.document for service in service_documents])
        no_services_found = False
        if not context:
            context = "No services found within the specified radius."
            no_services_found = True
        return context, no_services_found

    def _convert_documents_to_services(
        self, service_documents: List[ServiceDocument]
    ) -> List[Service]:
        """Convert ServiceDocument objects to Service objects."""
        return [_metadata_to_service(doc.metadata) for doc in service_documents]

    def _generate_response(self, query: str, context: str) -> RecommendationResponse:
        """
        Generate a response based on the input query and context using RAG methodology.

        Parameters
        ----------
        query : str
            The user's input query for which a recommendation is requested.
        context : str
            The context of relevant services.

        Returns
        -------
        RecommendationResponse
            An object containing the generated recommendation and relevant services.
        """
        generation_template = """
        You are an expert with deep knowledge of health and community services. You will be providing a recommendation to an individual who is seeking help. The individual is seeking help with the following query:

        <QUERY>
        {discover}
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

        completion = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user",
                    "content": generation_template.format(
                        context=context, discover=query
                    ),
                }
            ],
            max_tokens=500,
        )
        response_content = completion.choices[0].message.content
        if response_content is None:
            logger.error("Received empty response from OpenAI API")
            raise ValueError("Received empty response from OpenAI API")

        response_content = response_content.strip()
        if response_content == "EMERGENCY":
            return RecommendationResponse(
                is_emergency=True,
                message=get_emergency_services_message(),
                is_out_of_scope=False,
            )
        if response_content.startswith("Response:"):
            return RecommendationResponse(
                is_emergency=False,
                message=response_content,
                is_out_of_scope=True,
            )
        if response_content == "NO_SERVICES_FOUND":
            return RecommendationResponse(
                is_emergency=False,
                message=response_content,
                is_out_of_scope=False,
                no_services_found=True,
            )
        return RecommendationResponse(
            is_emergency=False,
            message=response_content,
            is_out_of_scope=False,
        )

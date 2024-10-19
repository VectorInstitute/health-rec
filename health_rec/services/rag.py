"""Module to provide a RAG (Retrieval-Augmented Generation) service."""

import logging
from typing import List

import chromadb
import openai
from chromadb.api.models.Collection import Collection

from api.config import Config
from api.data import RecommendationResponse, RecommendationServices, Service, ServiceDocument, Query
from services.emergency import get_emergency_services_message
from services.utils import _parse_chroma_result, _metadata_to_service
from services.ranking import RankingService


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
        # TODO: user defines the weight when starting the app or in the config file
        self.ranking_service = RankingService(relevancy_weight=0.1)

    def generate(self, query: Query) -> RecommendationServices:
        """
        Generate a response based on the input query using RAG methodology.

        Parameters
        ----------
        query : str
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
        try:
            query_embedding = (
                self.client.embeddings.create(input=[query.query_str], model=self.embedding_model)
                .data[0]
                .embedding
            )
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise ValueError("Failed to generate embedding for the query") from e

        chroma_results = self.services_collection.query(
            query_embeddings=query_embedding, n_results=3
        )
        
        service_documents = _parse_chroma_result(chroma_results)

        context: str = "\n".join([service.document for service in service_documents])

        response = self._generate_response(query, context)
        
        user_location = None
        if  query.latitude and query.longitude:
            user_location=(query.latitude, query.longitude)
        services: List[Service] = self.ranking_service.rank_services(
                service_documents, user_location
            )
        logger.info(f"Generated recommendation: {response}")
        logger.info("\n-------------------\n")
        logger.info(f"Ranked services: {services}")
        if response.is_out_of_scope or response.is_emergency:
            services = []
        
        return RecommendationServices(message=response.message, is_emergency=response.is_emergency, 
                                          is_out_of_scope=response.is_out_of_scope, services=services)


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
        RAGOutput
            An object containing the generated recommendation and relevant services.
        """
        generation_template: str = """
        You are an expert with deep knowledge of health and community services in the Greater Toronto Area (GTA). You will be providing a recommendation to an individual who is seeking help. The individual is seeking help with the following query:

        <QUERY>
        {discover}
        </QUERY>

        If you determine that the individual has an emergency need, respond with only the word "EMERGENCY" (in all caps).
        If you determine that the individual's query is not for a health or community service in the GTA, respond with an appropriate out of scope message in relation to the query. Structure your response as follows:
        Response: A brief explanation of why the query is out of scope.
        Reasoning: Provide more detailed reasoning for why this query cannot be answered within the context of GTA health and community services.

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
        return RecommendationResponse(
            is_emergency=False,
            message=response_content,
            is_out_of_scope=False,
        )

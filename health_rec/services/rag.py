"""Module to provide a RAG (Retrieval-Augmented Generation) service."""

import logging
from typing import List

import chromadb
import openai
from chromadb.api.models.Collection import Collection

from api.config import Config
from api.data import RecommendationResponse, Service, ServiceDocument
from services.emergency import get_emergency_services_message
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

    def generate(self, query: str) -> RecommendationResponse:
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
                self.client.embeddings.create(input=[query], model=self.embedding_model)
                .data[0]
                .embedding
            )
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise ValueError("Failed to generate embedding for the query") from e

        chroma_results = self.services_collection.query(
            query_embeddings=query_embedding, n_results=5
        )
        parsed_results: List[ServiceDocument] = [
            ServiceDocument(id=id_, document=doc, metadata=meta)
            for id_, doc, meta in zip(
                chroma_results["ids"][0] if chroma_results["ids"] else [],
                chroma_results["documents"][0] if chroma_results["documents"] else [],
                chroma_results["metadatas"][0] if chroma_results["metadatas"] else [],
            )
        ]
        services: List[Service] = [
            _metadata_to_service(service.metadata) for service in parsed_results
        ]
        context: str = "\n".join([service.document for service in parsed_results])

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
                services=[],
                is_out_of_scope=False,
            )
        if response_content.startswith("Response:"):
            return RecommendationResponse(
                is_emergency=False,
                message=response_content,
                services=[],
                is_out_of_scope=True,
            )
        return RecommendationResponse(
            is_emergency=False,
            message=response_content,
            services=services,
            is_out_of_scope=False,
        )

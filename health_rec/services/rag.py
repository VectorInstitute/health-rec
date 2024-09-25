"""Module to provide a RAG (Retrieval-Augmented Generation) service."""

import logging
from typing import List

import chromadb
import openai
from chromadb.api.models.Collection import Collection

from api.config import Config
from api.data import RAGOutput, Service, ServiceDocument
from services.emergency import get_emergency_services_message
from services.utils import _metadata_to_service


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RAGService:
    """RAG service."""

    def __init__(self):
        """Initialize the RAG service."""
        self.client: openai.Client = openai.Client(api_key=Config.OPENAI_API_KEY)
        self.embedding_model: str = Config.OPENAI_EMBEDDING
        self.chroma_client: chromadb.HttpClient = chromadb.HttpClient(
            host=Config.CHROMA_HOST, port=Config.CHROMA_PORT
        )
        self.services_collection: Collection = self.chroma_client.get_collection(
            name=Config.COLLECTION_NAME
        )

    def generate(self, query: str) -> RAGOutput:
        """
        Generate a response based on the input query using RAG methodology.

        Parameters
        ----------
        query : str
            The user's input query for which a recommendation is requested.

        Returns
        -------
        RAGOutput
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
        You are an expert with deep knowledge of Toronto community services. You will be providing a recommendation to an individual who is seeking help. The individual is seeking help with the following query:

        <QUERY>
        {discover}
        </QUERY>

        If you determine that the individual has an emergency need, respond with only the word "EMERGENCY" (in all caps).

        If the individual does not need emergency help, use only the following service context enclosed by the <CONTEXT> tag to provide a service recommendation.

        <CONTEXT>
        {context}
        </CONTEXT>

        Your response should be structured as follows:
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
        response_content = completion.choices[0].message.content.strip()
        if response_content == "EMERGENCY":
            return RAGOutput(
                is_emergency=True, message=get_emergency_services_message(), services=[]
            )
        return RAGOutput(
            is_emergency=False, message=response_content, services=services
        )

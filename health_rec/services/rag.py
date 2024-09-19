"""Module to provide a RAG (Retrieval-Augmented Generation) service."""

import logging
from typing import Any, Dict, List

import chromadb
import openai

from api.config import Config
from api.data import RAGOutput, ServiceDocument
from services.emergency import get_emergency_services_message


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RAGService:
    """RAG service."""

    @staticmethod
    def generate(query: str) -> RAGOutput:
        """Generate a response based on the input query using RAG methodology.

        Parameters
        ----------
        query : str
            The user's input query for which a recommendation is requested.

        Returns
        -------
        RAGOutput
            An object containing the generated recommendation and relevant services.

        """
        client = openai.Client(api_key=Config.OPENAI_API_KEY)
        embedding_model = Config.OPENAI_EMBEDDING

        try:
            query_embedding = (
                client.embeddings.create(input=[query], model=embedding_model)
                .data[0]
                .embedding
            )
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise ValueError("Failed to generate embedding for the query") from e

        chroma_client = chromadb.HttpClient(
            host=Config.CHROMA_HOST, port=Config.CHROMA_PORT
        )
        services_collection = chroma_client.get_collection(name="test")
        chroma_results = services_collection.query(
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
        services: List[Dict[str, Any]] = [
            service.metadata for service in parsed_results
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

        completion = client.chat.completions.create(
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

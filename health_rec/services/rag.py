"""Module to provide a RAG (Retrieval-Augmented Generation) service."""

from typing import Any, Dict, List

import chromadb
import openai

from api.config import Config
from api.schemas import ChromaDocument, RagGeneration


class RagService:
    """RAG service."""

    @staticmethod
    def generate(query: str) -> RagGeneration:
        """
        Generate a response based on the input query using RAG methodology.

        Parameters
        ----------
        query : str
            The user's input query.

        Returns
        -------
        RagGeneration
            An object containing the generated message and relevant services.

        Notes
        -----
        This method performs the following steps:
        1. Generates an embedding for the input query.
        2. Queries a Chroma database for relevant documents.
        3. Constructs a context from the retrieved documents.
        4. Generates a response using OpenAI's GPT model.
        """
        client = openai.Client(api_key=Config.OPENAI_API_KEY)
        query_embedding = (
            client.embeddings.create(
                input=[query], model=Config.OPENAI_EMBEDDING or "text-embedding-ada-002"
            )
            .data[0]
            .embedding
        )

        chroma_client = chromadb.HttpClient(
            host=Config.CHROMA_HOST, port=Config.CHROMA_PORT
        )

        services_collection = chroma_client.get_collection(name="211_central")

        chroma_results = services_collection.query(
            query_embeddings=query_embedding, n_results=5
        )

        parsed_results: List[ChromaDocument] = [
            ChromaDocument(id=id_, document=doc, metadata=meta)
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

        generation_template: str = """You are an expert with deep knowledge of Toronto community services. You will be providing a recommendation to an individual who is seeking help. The individual is seeking help with the following query:

        <QUERY>
            {discover}
        </QUERY>

        If you determine that individual has an emergency need. Respond with only the text enclosed in in the <EMERGENCY SERVICES> tag. DO NOT provide any other information and do not include the <EMERGENCY SERVICES> tag in your response.

        <EMERGENCY SERVICES>
            **In an emergency, call 9‑1‑1.**

            * At home, you can dial 9‑1‑1 directly. At a business or other location, you may need to dial an outside line before dialing 9‑1‑1.

            * At a pay phone, dial 9‑1‑1; the call is free. When using a cellular phone, be prepared to give the exact location of the emergency; the call is free.

            * For TTY access (Telephone Device for the Deaf), press the space bar announcer key repeatedly until a response is received. Deaf, deafened, Hard of Hearing, or Speech Impaired persons may register for Text with 9-1-1 Service.

            **If you do not speak English,** stay on the line while the call taker contacts the telephone translations service.

            When you call, remain calm and speak clearly. Identify which emergency service you require (police, fire, or ambulance) and be prepared to provide the following information: a description of what is happening, the location, and your name, address, and telephone number.

            Please remain on the line to provide additional information if requested by the call taker. Do not hang up until the call taker tells you to.
        </EMERGENCY SERVICES>

        If the individual does not need emergency help. Using only the following service context enclosed by the <CONTEXT> tag to provide a short service recommendation.
        The recommendation should focus on the most relevant service and should consist of two short sections. Section one is an overview of the service and section two provides the reasoning and any other helpful information.

        Your response should be always be formatted as GitHub Markdown.

        <CONTEXT>
            {context}
        </CONTEXT>

        """

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": generation_template.format(
                        context=context, discover=query
                    ),
                },
            ],
            max_tokens=500,
        )

        print(completion.choices[0].message.content)

        return RagGeneration(
            message=completion.choices[0].message.content, services=services
        )

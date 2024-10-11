"""Backend API routes."""

import logging
from typing import Any, List

from fastapi import APIRouter, Depends

from api.data import RecommendationResponse, Service
from services.dev.data import ChromaService
from services.rag import RAGService


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter()

# Create a single instance of RAGService to be used across requests
rag_service = RAGService()


@router.get("/recommend", response_model=RecommendationResponse)
async def recommend(query: str) -> RecommendationResponse:
    """
    Generate a recommendation based on the input query.

    Parameters
    ----------
    query : str
        The user's input query for which a recommendation is requested.

    Returns
    -------
    RecommendationResponse
        An object containing the generated recommendation and relevant services.

    Notes
    -----
    This function logs the incoming query and uses the RagService to generate
    a response based on the query.
    """
    logger.info(f"Request query: {query}")
    generation = rag_service.generate(query)
    logger.info(f"Generation: {generation}")
    return RecommendationResponse(**generation.dict())


@router.get("/services/all", response_model=List[Service])
async def get_all_services(
    chroma_service: ChromaService = Depends(ChromaService),  # noqa: B008
) -> Any:
    """
    Get all services from the ChromaDB collection.

    Returns
    -------
    List[Service]
        A list of services.
    """
    return await chroma_service.get_all_services()


@router.get("/services/count", response_model=int)
async def get_services_count(
    chroma_service: ChromaService = Depends(ChromaService),  # noqa: B008
) -> Any:
    """
    Get the number of services in the ChromaDB collection.

    Returns
    -------
    int
        The number of services.
    """
    return await chroma_service.get_services_count()

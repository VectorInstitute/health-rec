"""Backend API routes."""

import logging

from fastapi import APIRouter

from api.schemas import GetRecommendationResponse
from services.rag import RagService


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter()


@router.get("/recommend", response_model=GetRecommendationResponse)
async def recommend(query: str) -> GetRecommendationResponse:
    """
    Generate a recommendation based on the input query.

    Parameters
    ----------
    query : str
        The user's input query for which a recommendation is requested.

    Returns
    -------
    GetRecommendationResponse
        An object containing the generated recommendation and relevant services.

    Notes
    -----
    This function logs the incoming query and uses the RagService to generate
    a response based on the query.
    """
    logger.info(f"Request query: {query}")
    generation = RagService.generate(query)

    return GetRecommendationResponse(**generation.dict())

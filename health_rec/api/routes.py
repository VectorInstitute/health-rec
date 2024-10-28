"""Backend API routes."""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException

from api.data import (
    Query,
    RecommendationResponse,
    RefineRequest,
    Service,
)
from services.dev.data import ChromaService
from services.rag import RAGService
from services.refine import RefineService
from services.rerank import ReRankingService, RerankingConfig


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter()

rag_service = RAGService()
refine_service = RefineService()
rerank_service = ReRankingService(RerankingConfig())


@router.get("/questions", response_model=dict)
async def get_additional_questions(
    query: str, recommendation: str
) -> Dict[str, List[str]]:
    """
    Generate additional questions based on the query and recommendation.

    Parameters
    ----------
    query : str
        The user's original query.
    recommendation : str
        The recommendation message previously generated.

    Returns
    -------
    Dict[str, List[str]]
        A dictionary with the generated questions.
    """
    try:
        questions = refine_service.generate_questions(query, recommendation)
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/refine_recommendations", response_model=RecommendationResponse)
async def refine_recommendations(
    request: RefineRequest = Body(...),  # noqa: B008
) -> RecommendationResponse:
    """
    Refine the recommendations based on the user's additional questions.

    Parameters
    ----------
    request : RefineRequest
        The request object containing the original query, questions,
        answers, and previous recommendation.

    Returns
    -------
    RecommendationResponse
        An object containing the refined recommendation, relevant services,
        and new additional questions.

    Raises
    ------
    HTTPException
        If there's an error refining the recommendations.
    """
    try:
        refined_query = refine_service.improve_query(
            request.query.query,
            request.questions,
            request.answers,
            request.recommendation,
        )
        logger.info(f"Refined query: {refined_query}")
        return rag_service.generate(
            Query(
                query=refined_query,
                latitude=request.query.latitude,
                longitude=request.query.longitude,
                radius=request.query.radius,
            )
        )
    except Exception as e:
        logger.error(f"Error in refine_recommendations: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e)) from e


@router.post("/recommend", response_model=RecommendationResponse)
async def recommend(query: Query) -> RecommendationResponse:  # noqa: F811
    """
    Generate a recommendation based on the input query.

    Parameters
    ----------
    query : Query
        The user's input (query, location (optional), radius (optional)).

    Returns
    -------
    RecommendationResponse
        An object containing the generated recommendation and relevant services.

    Notes
    -----
    This function logs the incoming query and uses the RagService to generate
    a response based on the query.
    """
    logger.info(f"Received query: {query}")
    return rag_service.generate(query)


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

@router.get("/rerank", response_model=List[Service])
async def rerank_recommendations(
    query: str,
    retrieval_k: Optional[int] = 20,
    output_k: Optional[int] = 5
) -> List[Service]:
    """
    Generate re-ranked list of services based on the input query.

    Parameters
    ----------
    query : str
        The user's input query.
    retrieval_k : Optional[int]
        Number of services to retrieve initially. Default is 10.
    output_k : Optional[int]
        Number of services to return after re-ranking. Default is 5.

    Returns
    -------
    List[Service]
        A list of services ordered by relevance to the query.
    """
    try:
        config = RerankingConfig(
            retrieval_k=min(max(1, retrieval_k), 20),  # Limit between 1 and 20
            output_k=min(max(1, output_k), retrieval_k),  # Cannot be more than retrieval_k
        )
        rerank_service.config = config
        return rerank_service.rerank(query)
    except Exception as e:
        logger.error(f"Error in rerank_recommendations: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
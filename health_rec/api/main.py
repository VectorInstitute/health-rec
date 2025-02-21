"""
Main module for the FastAPI application.

This module sets up the FastAPI application, configures CORS middleware,
and includes the main router.
"""

import logging
from typing import Dict

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.config import Config, FastAPIConfig
from api.routes import router as api_router


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Add this before app initialization
def log_configuration() -> None:
    """Log the current configuration values."""
    logger.info("=== Health Rec API Configuration ===")
    logger.info(f"OPENAI_MODEL: {Config.OPENAI_MODEL}")
    logger.info(f"OPENAI_EMBEDDING: {Config.OPENAI_EMBEDDING}")
    logger.info(f"CHROMA_HOST: {Config.CHROMA_HOST}")
    logger.info(f"CHROMA_PORT: {Config.CHROMA_PORT}")
    logger.info(f"COLLECTION_NAME: {Config.COLLECTION_NAME}")
    logger.info(f"RELEVANCY_WEIGHT: {Config.RELEVANCY_WEIGHT}")
    logger.info(f"EMBEDDING_MAX_CONTEXT_LENGTH: {Config.EMBEDDING_MAX_CONTEXT_LENGTH}")
    logger.info(f"MAX_CONTEXT_LENGTH: {Config.MAX_CONTEXT_LENGTH}")
    logger.info(f"TOP_K: {Config.TOP_K}")
    logger.info(f"RERANKER_MAX_CONTEXT_LENGTH: {Config.RERANKER_MAX_CONTEXT_LENGTH}")
    logger.info(f"RERANKER_MAX_SERVICES: {Config.RERANKER_MAX_SERVICES}")
    logger.info("====================================")


log_configuration()

app = FastAPI(**FastAPIConfig().__dict__)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
app.include_router(api_router)


@app.get("/")
async def root() -> Dict[str, str]:
    """
    Root endpoint of the API.

    Returns
    -------
    Dict[str, str]
        A welcome message for the health-rec API.
    """
    return {"message": "Welcome to the health-rec API"}


@app.get("/healthcheck")
async def healthcheck() -> Dict[str, str]:
    """
    Health check endpoint.

    This endpoint can be used to verify that the API is running and responsive.

    Returns
    -------
    Dict[str, str]
        A dictionary indicating the health status of the API.
    """
    return {"status": "healthy"}

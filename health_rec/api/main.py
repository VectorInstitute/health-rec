"""
Main module for the FastAPI application.

This module sets up the FastAPI application, configures CORS middleware,
includes the main router, and loads data into Chroma on startup.
"""

import logging
import os
from typing import Dict

import chromadb
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.config import FastAPIConfig
from api.routes import router as api_router
from load_data import load_data


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


CHROMA_DB_HOST = os.getenv("CHROMA_HOST", "chromadb")
CHROMA_DB_PORT = 8000
RELOAD_DATA = False


app = FastAPI(**FastAPIConfig().__dict__)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
app.include_router(api_router)


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize the application by loading data into Chroma on startup."""
    chroma_client = chromadb.HttpClient(host=CHROMA_DB_HOST, port=CHROMA_DB_PORT)
    # Check if collection exists and its dimension
    try:
        collection = chroma_client.get_collection("test")
        existing_dim = collection.count()
        if existing_dim > 0:
            sample = collection.get(limit=1, include=["embeddings"])
            existing_dim = len(sample["embeddings"][0])
    except ValueError:
        existing_dim = None

    collection_names = [
        collection.name for collection in chroma_client.list_collections()
    ]
    if "test" in collection_names and RELOAD_DATA:
        logger.info("Deleting existing collection")
        chroma_client.delete_collection("test")
        collection = chroma_client.create_collection("test")
        logger.info("Recreating collection due to dimension mismatch or non-existence")
        load_data(
            file_path="./data.json",
            host=CHROMA_DB_HOST,
            port=CHROMA_DB_PORT,
            collection_name="test",
            openai_api_key=os.getenv("OPENAI_API_KEY", "your_openai_api_key_here"),
        )
    else:
        logger.info("Collection exists already, and RELOAD_DATA is False")


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

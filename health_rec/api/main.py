"""
Main module for the FastAPI application.

This module sets up the FastAPI application, configures CORS middleware,
and includes the main router. It also provides a health check endpoint.
"""

from typing import Dict

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.config import FastAPIConfig
from api.routes import router as api_router


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

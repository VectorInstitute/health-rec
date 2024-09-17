"""API for health service recommendation."""

from app.api import recommend
from fastapi import APIRouter


router = APIRouter()

router.include_router(recommend.router)

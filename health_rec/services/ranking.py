"""Ranking service based on location and relevancy score."""

import logging
from math import atan2, cos, radians, sin, sqrt
from typing import List, Optional, Tuple

from api.data import ServiceDocument


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RankingService:
    """Ranking service."""

    def __init__(self, relevancy_weight: float = 0.5) -> None:
        """Initialize the ranking service."""
        self.relevancy_weight: float = relevancy_weight
        self.distance_weight: float = 1.0 - relevancy_weight

    def rank_services(
        self,
        services: List[ServiceDocument],
        user_location: Optional[Tuple[float, float]],
    ) -> List[ServiceDocument]:
        """
        Rank services based on the specified strategy.

        Parameters
        ----------
        services : List[ServiceDocument]
            A list of service documents returned by ChromaDB to be ranked.
        user_location : Optional[Tuple[float, float]]
            The user's location as a tuple of latitude and longitude coordinates.

        Returns
        -------
        List[ServiceDocument]
            A list of ranked service documents based on the specified strategy.
        """
        if user_location is None:
            return self._rank_by_relevancy(services)

        return self._rank_by_relevancy_and_distance(services, user_location)

    def _rank_by_relevancy(
        self, services: List[ServiceDocument]
    ) -> List[ServiceDocument]:
        """Rank services by relevancy score."""
        services.sort(key=lambda service: service.relevancy_score, reverse=True)
        return services

    def _rank_by_relevancy_and_distance(
        self, services: List[ServiceDocument], user_location: Tuple[float, float]
    ) -> List[ServiceDocument]:
        """Rank services by relevancy score and distance."""
        for service in services:
            service_location = (
                float(service.metadata["latitude"]),
                float(service.metadata["longitude"]),
            )
            service.distance = _calculate_distance(service_location, user_location)
        services.sort(key=self._calculate_ranking_score, reverse=True)
        return services

    def _calculate_ranking_score(self, service: ServiceDocument) -> float:
        """
        Calculate the ranking score for a service based on the specified strategy.

        Parameters
        ----------
        service : ServiceDocument
            The service document for which the ranking score is calculated.

        Returns
        -------
        float
            The ranking score for the service based on the specified strategy.
        """
        # Convert cosine distance to cosine similarity
        cosine_similarity = 1 - service.relevancy_score

        # Normalize distance to a 0-1 range (assuming max distance of 100 km)
        normalized_distance = min(service.distance / 100, 1)

        # Calculate the ranking score
        return float(
            self.relevancy_weight * cosine_similarity
            + self.distance_weight * (1 - normalized_distance)
        )


def _calculate_distance(
    location1: Tuple[float, float], location2: Tuple[float, float]
) -> float:
    """
    Calculate the distance between two locations using the Haversine formula.

    Parameters
    ----------
    location1 : Tuple[float, float]
        The latitude and longitude coordinates of the first location.
    location2 : Tuple[float, float]
        The latitude and longitude coordinates of the second location.

    Returns
    -------
    float
        The distance between the two locations in kilometers.
    """
    lat1, lon1 = location1
    lat2, lon2 = location2

    # Radius of the Earth in kilometers (using double precision)
    radius: float = 6371.0088

    # Convert latitude and longitude from degrees to radians
    lat1_rad, lon1_rad = radians(lat1), radians(lon1)
    lat2_rad, lon2_rad = radians(lat2), radians(lon2)

    # Calculate the differences
    dlat, dlon = lat2_rad - lat1_rad, lon2_rad - lon1_rad

    # Calculate the distance using the Haversine formula
    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return radius * c

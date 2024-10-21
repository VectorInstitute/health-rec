"""Ranking service based on location and relevancy score."""

import logging
import math
from typing import List, Optional, Tuple

from api.data import Service, ServiceDocument
from services.utils import _metadata_to_service


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RankingService:
    """Ranking service."""

    def __init__(self, relevancy_weight: float = 0.5):
        """Initialize the ranking service."""
        self.relevancy_weight = relevancy_weight
        self.distance_weight = 1.0 - relevancy_weight

    def rank_services(
        self,
        services: List[ServiceDocument],
        user_location: Optional[Tuple[float, float]],
    ) -> List[Service]:
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
        List[Service]
            A list of ranked services based on the specified strategy.

        """
        if user_location is None:
            services.sort(key=lambda service: service.relevancy_score, reverse=True)
            return [_metadata_to_service(service.metadata) for service in services]
        for service in services:
            service_location = (
                float(service.metadata["Latitude"]),
                float(service.metadata["Longitude"]),
            )
            service.distance = _calculate_distance(service_location, user_location)
            logger.info(
                f"Service: {service.metadata['PublicName']}, Distance: {service.distance}"
            )

        # TODO remove the following lines later
        scores = {
            service.metadata["PublicName"]: self._calculate_ranking_score(service)
            for service in services
        }
        logger.info(f"Services and their scores: \n {scores}")
        services.sort(
            key=lambda service: self._calculate_ranking_score(service), reverse=True
        )
        return [_metadata_to_service(service.metadata) for service in services]

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
        return float(
            self.relevancy_weight * service.relevancy_score
            + self.distance_weight * (1 / service.distance)
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

    # Radius of the Earth in kilometers
    radius = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Calculate the differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Calculate the distance using the Haversine formula
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c

"""Common utilities for the project."""

import requests
from typing import List, Optional
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


class RetryableSession(requests.Session):
    """Session with retry capabilities."""

    def __init__(
        self,
        retries: int = 3,
        backoff_factor: float = 0.5,
        status_forcelist: Optional[List[int]] = None,
    ):
        """Initialize session with retry strategy."""
        super().__init__()

        if status_forcelist is None:
            status_forcelist = [403, 500, 502, 503, 504]

        retry_strategy = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            allowed_methods=["GET", "POST"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.mount("http://", adapter)
        self.mount("https://", adapter)

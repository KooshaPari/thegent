"""API client utilities."""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class APIClient:
    """API client."""

    def __init__(self, base_url: str) -> None:
        """Initialize API client.

        Args:
            base_url: Base URL
        """
        self.base_url = base_url
        self.client = httpx.Client(base_url=base_url)

    def get(self, path: str) -> dict[str, Any]:
        """GET request.

        Args:
            path: API path

        Returns:
            Response dictionary
        """
        response = self.client.get(path)
        return response.json()

    def post(self, path: str, data: dict[str, Any]) -> dict[str, Any]:
        """POST request.

        Args:
            path: API path
            data: Request data

        Returns:
            Response dictionary
        """
        response = self.client.post(path, json=data)
        return response.json()

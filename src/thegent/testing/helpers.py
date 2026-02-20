"""Testing helpers and utilities."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class TestHelpers:
    """Helper utilities for testing."""

    @staticmethod
    def assert_dict_contains(dict1: dict[str, Any], dict2: dict[str, Any]) -> bool:
        """Assert dict1 contains all keys from dict2.

        Args:
            dict1: First dictionary
            dict2: Second dictionary

        Returns:
            True if dict1 contains dict2
        """
        return all(key in dict1 and dict1[key] == dict2[key] for key in dict2)

    @staticmethod
    def mock_async_function(result: Any):
        """Create a mock async function.

        Args:
            result: Result to return

        Returns:
            Mock async function
        """

        async def mock_fn(*args, **kwargs):
            return result

        return mock_fn

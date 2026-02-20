"""Research: Add psutil for resource monitoring."""

from typing import Any

from thegent.research.library_replacements import use_psutil_monitoring


class LibraryPsutilResearch:
    """Research for psutil library."""

    def __init__(self) -> None:
        """Initialize psutil research."""

    def test_psutil(self) -> dict[str, Any]:
        """Test psutil functionality.

        Returns:
            Test results
        """
        metrics = use_psutil_monitoring()
        return {"status": "available" if metrics else "unavailable", "metrics": metrics}

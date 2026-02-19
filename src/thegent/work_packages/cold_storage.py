"""WP-42003: Cold-Storage Data Archiving (Planet-Scale)."""

from typing import Any


class ColdStorageArchiver:
    """Archive data to planet-scale cold storage."""

    def archive(self, data: Any, location: str) -> str:
        """Archive data."""
        return f"archive://{location}/data"

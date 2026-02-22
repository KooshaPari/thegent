"""Disk I/O queue depth monitoring."""

import logging

logger = logging.getLogger(__name__)


class DiskQueueDepth:
    """Disk queue depth monitoring."""

    def __init__(self) -> None:
        """Initialize disk queue depth."""

    def get_queue_depth(self, device: str) -> float:
        """Get queue depth for device.

        Args:
            device: Device name

        Returns:
            Queue depth
        """
        # Would use iostat or similar
        logger.info(f"Getting queue depth for {device}")
        return 0.0

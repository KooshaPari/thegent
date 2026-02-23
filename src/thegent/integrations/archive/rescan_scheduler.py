"""Full-rescan scheduler for periodic complete resyncs.

# @trace WL-207
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RescanConfig:
    """Configuration for full-rescan scheduling."""

    full_rescan_every_n_cycles: int = 10
    incremental_by_default: bool = True


class RescanScheduler:
    """Schedule periodic full-rescan passes in addition to incremental cycles."""

    def __init__(self, config: RescanConfig | None = None) -> None:
        """Initialize the rescan scheduler.

        Args:
            config: RescanConfig instance (default: RescanConfig()).
        """
        self.config = config or RescanConfig()

    def should_full_rescan(self, cycle_number: int) -> bool:
        """Determine if a full rescan should occur at this cycle number.

        Args:
            cycle_number: The current cycle number (1-indexed).

        Returns:
            True if a full rescan should occur, False for incremental.

        Raises:
            ValueError: If cycle_number is less than 1.
        """
        if cycle_number < 1:
            raise ValueError("cycle_number must be >= 1")

        # Every N cycles, perform full rescan
        return cycle_number % self.config.full_rescan_every_n_cycles == 0

    def next_full_rescan_cycle(self, current_cycle: int) -> int:
        """Calculate the next cycle number when a full rescan will occur.

        Args:
            current_cycle: The current cycle number (1-indexed).

        Returns:
            The next cycle number where a full rescan will occur.

        Raises:
            ValueError: If current_cycle is less than 1.
        """
        if current_cycle < 1:
            raise ValueError("current_cycle must be >= 1")

        # Find the next multiple of full_rescan_every_n_cycles
        interval = self.config.full_rescan_every_n_cycles
        return ((current_cycle // interval) + 1) * interval

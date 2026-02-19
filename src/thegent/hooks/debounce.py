"""Implement debounce subcommand (file-based coordination)."""

import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class DebounceSubcommand:
    """Debounce subcommand for file-based coordination."""

    def __init__(self, debounce_dir: Path | None = None):
        """Initialize debounce.
        
        Args:
            debounce_dir: Directory for debounce files
        """
        self.debounce_dir = debounce_dir or Path(".debounce")
        self.debounce_dir.mkdir(parents=True, exist_ok=True)

    def debounce(self, key: str, delay_seconds: float = 1.0) -> bool:
        """Check if operation should be debounced.
        
        Args:
            key: Debounce key
            delay_seconds: Delay in seconds
            
        Returns:
            True if should proceed, False if debounced
        """
        debounce_file = self.debounce_dir / f"{key}.lock"
        
        if debounce_file.exists():
            # Check if delay has passed
            last_time = debounce_file.stat().st_mtime
            elapsed = time.time() - last_time
            if elapsed < delay_seconds:
                logger.debug(f"Debouncing {key}: {elapsed:.2f}s < {delay_seconds}s")
                return False
        
        # Update debounce file
        debounce_file.touch()
        return True

    def clear(self, key: str) -> None:
        """Clear debounce for a key.
        
        Args:
            key: Debounce key
        """
        debounce_file = self.debounce_dir / f"{key}.lock"
        if debounce_file.exists():
            debounce_file.unlink()
            logger.info(f"Cleared debounce for {key}")

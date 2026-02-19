"""Reusable helper library for common patterns."""

import logging
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)


class ReusableHelpers:
    """Collection of reusable helper functions."""

    @staticmethod
    def safe_execute(func: Callable, *args, **kwargs) -> tuple[Any, Exception | None]:
        """Safely execute a function with error handling.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Tuple of (result, error)
        """
        try:
            result = func(*args, **kwargs)
            return result, None
        except Exception as e:
            logger.error(f"Error executing {func.__name__}: {e}")
            return None, e

    @staticmethod
    def retry_on_failure(
        func: Callable,
        max_retries: int = 3,
        delay: float = 1.0,
        *args,
        **kwargs,
    ) -> Any:
        """Retry a function on failure.
        
        Args:
            func: Function to retry
            max_retries: Maximum retry attempts
            delay: Delay between retries (seconds)
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
        """
        import time
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                time.sleep(delay)
        
        raise Exception("Max retries exceeded")

    @staticmethod
    def ensure_directory(path: Path) -> Path:
        """Ensure a directory exists.
        
        Args:
            path: Directory path
            
        Returns:
            Path object
        """
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def find_files(
        directory: Path,
        pattern: str = "*.py",
        recursive: bool = True,
    ) -> list[Path]:
        """Find files matching a pattern.
        
        Args:
            directory: Directory to search
            pattern: File pattern
            recursive: Search recursively
            
        Returns:
            List of matching file paths
        """
        if recursive:
            return list(directory.rglob(pattern))
        return list(directory.glob(pattern))

    @staticmethod
    def read_json_safe(file_path: Path) -> dict[str, Any] | None:
        """Safely read a JSON file.
        
        Args:
            file_path: JSON file path
            
        Returns:
            Parsed JSON or None
        """
        import json
        
        try:
            return json.loads(file_path.read_text())
        except Exception as e:
            logger.error(f"Error reading JSON {file_path}: {e}")
            return None

    @staticmethod
    def read_file_efficiency(
        file_path: Path,
        offset: int = 0,
        limit: int | None = None,
    ) -> str:
        """Read a file with offset and limit.
        
        Args:
            file_path: File to read
            offset: Starting line (0-indexed)
            limit: Maximum number of lines to read
            
        Returns:
            File content as string
        """
        try:
            with open(file_path, "r") as f:
                lines = f.readlines()
                if limit is None:
                    return "".join(lines[offset:])
                return "".join(lines[offset : offset + limit])
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return ""

    @staticmethod
    def write_json_safe(file_path: Path, data: dict[str, Any]) -> bool:
        """Safely write a JSON file.
        
        Args:
            file_path: JSON file path
            data: Data to write
            
        Returns:
            True if successful
        """
        import json
        
        try:
            file_path.write_text(json.dumps(data, indent=2))
            return True
        except Exception as e:
            logger.error(f"Error writing JSON {file_path}: {e}")
            return False

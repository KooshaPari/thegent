"""Reusable helper library for common patterns."""

import contextlib
import functools
import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

from tenacity import retry, stop_after_attempt, wait_fixed

logger = logging.getLogger(__name__)


class ReusableHelpers:
    """Collection of reusable helper functions."""

    @staticmethod
    def error_handler(func: Callable) -> Callable:
        """Decorator that logs exceptions and returns a safe default.

        For methods returning ``list`` the default is ``[]``.
        For methods returning ``bool`` the default is ``False``.
        For all other return types the default is ``None``.

        This decorator wraps the function so that unhandled exceptions are
        logged at ERROR level and a sensible empty/falsy value is returned
        instead of propagating the exception.

        Args:
            func: The method to wrap.

        Returns:
            Wrapped callable.
        """
        hints = {}
        with contextlib.suppress(AttributeError):
            hints = func.__annotations__

        return_hint = hints.get("return", None)

        @functools.wraps(func)
        def _wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                logger.error("Error in %s: %s", func.__name__, exc)
                # Return sensible default based on annotation
                if return_hint is not None:
                    if return_hint in (list, "list[dict[str, Any]]") or (
                        isinstance(return_hint, str) and return_hint.startswith("list")
                    ):
                        return []
                    if return_hint is bool or return_hint == "bool":
                        return False
                return None

        return _wrapper

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
        """Retry a function on failure using tenacity.

        Args:
            func: Function to retry
            max_retries: Maximum retry attempts
            delay: Delay between retries (seconds)
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result
        """

        @retry(
            stop=stop_after_attempt(max_retries),
            wait=wait_fixed(delay),
            reraise=True,
        )
        def _execute_with_retry():
            return func(*args, **kwargs)

        return _execute_with_retry()

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
            with open(file_path) as f:
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

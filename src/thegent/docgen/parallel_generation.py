"""Parallel documentation generation."""

import logging
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ParallelGenerator:
    """Generate documentation in parallel."""

    def __init__(self, max_workers: int = 4, use_processes: bool = False) -> None:
        """Initialize parallel generator.

        Args:
            max_workers: Maximum number of workers
            use_processes: Use processes instead of threads
        """
        self.max_workers = max_workers
        self.use_processes = use_processes

    def generate_parallel(
        self,
        files: list[Path],
        generator_func: Callable[[Path], dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Generate documentation in parallel.

        Args:
            files: List of files to process
            generator_func: Function to generate docs for each file

        Returns:
            List of generation results
        """
        executor_class = ProcessPoolExecutor if self.use_processes else ThreadPoolExecutor

        with executor_class(max_workers=self.max_workers) as executor:
            futures = [executor.submit(generator_func, file_path) for file_path in files]
            results = []

            for future in futures:
                self._collect_future_result(results, future)

        return results

    def _collect_future_result(self, results: list[Any], future: Any) -> None:
        """Collect the result of a single future safely."""
        try:
            result = future.result()
            results.append(result)
        except Exception as e:
            logger.error(f"Error in parallel generation: {e}")
            results.append({"error": str(e)})

    def generate_batch(
        self,
        files: list[Path],
        generator_func: Callable[[Path], dict[str, Any]],
        batch_size: int = 10,
    ) -> list[dict[str, Any]]:
        """Generate documentation in batches.

        Args:
            files: List of files to process
            generator_func: Function to generate docs
            batch_size: Size of each batch

        Returns:
            List of generation results
        """
        all_results = []

        for i in range(0, len(files), batch_size):
            batch = files[i : i + batch_size]
            logger.info(f"Processing batch {i // batch_size + 1} ({len(batch)} files)")
            batch_results = self.generate_parallel(batch, generator_func)
            all_results.extend(batch_results)

        return all_results

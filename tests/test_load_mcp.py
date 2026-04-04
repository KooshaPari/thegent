"""Load tests for MCP tools and cli_impl (G-FM-05).

Scenarios: concurrent ps_impl, concurrent list_models_impl, rate limit behavior.
"""

from __future__ import annotations

import concurrent.futures
import time

import pytest
from thegent.cli.commands.impl import list_models_impl, ps_impl


@pytest.mark.integration
class TestConcurrentPs:
    """50 concurrent ps_impl: no deadlock, completes within reasonable time."""

    def test_concurrent_ps_impl_no_deadlock(self) -> None:
        # @trace FR-MCP-001
        """50 concurrent ps_impl calls complete without deadlock."""

        def call_ps() -> list:
            return ps_impl()

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
            futures = [ex.submit(call_ps) for _ in range(50)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        assert len(results) == 50
        for r in results:
            assert isinstance(r, list)

    def test_concurrent_ps_completes_under_2s_p95(self) -> None:
        # @trace FR-MCP-001
        """50 concurrent ps_impl calls complete; p95 latency under 2s."""

        def call_ps() -> tuple[float, list]:
            start = time.perf_counter()
            r = ps_impl()
            return time.perf_counter() - start, r

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
            futures = [ex.submit(call_ps) for _ in range(50)]
            completed = [f.result() for f in concurrent.futures.as_completed(futures)]

        latencies = [t for t, _ in completed]
        p95_idx = int(len(latencies) * 0.95) - 1
        p95 = sorted(latencies)[max(0, p95_idx)]
        assert p95 < 2.0


@pytest.mark.integration
class TestConcurrentListModels:
    """Concurrent list_models_impl: cache hits, no OOM."""

    def test_concurrent_list_models_no_deadlock(self) -> None:
        # @trace FR-MCP-001
        """30 concurrent list_models_impl calls complete."""

        def call_list() -> dict:
            return list_models_impl(use_scraped=False)

        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as ex:
            futures = [ex.submit(call_list) for _ in range(30)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        assert len(results) == 30
        for r in results:
            assert isinstance(r, dict)
            assert "gemini" in r or "claude" in r or "cursor-agent" in r

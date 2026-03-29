"""Tests for WL-072: NeverIdleLoop persistent event loop."""

from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.requirement("FR-OPT-003")
class TestNeverIdleLoopPersistentLoop:
    """Verify NeverIdleLoop reuses a single asyncio event loop."""

    def _make_loop(self, tmp_path: Path) -> "NeverIdleLoop":
        """Create a NeverIdleLoop with mocked components."""
        with (
            patch("thegent.sitback.never_idle.BackgroundTaskWatcher"),
            patch("thegent.sitback.never_idle.GardeningManager"),
        ):
            from thegent.sitback.never_idle import NeverIdleLoop

            return NeverIdleLoop(
                session_dir=tmp_path / "sessions",
                sleep_interval=1,
                project_root=tmp_path,
            )

    def _teardown_loop(self, loop_instance):
        """Ensure the async event loop thread is cleaned up."""
        if loop_instance._async_loop.is_running():
            loop_instance._async_loop.call_soon_threadsafe(loop_instance._async_loop.stop)
            loop_instance._async_thread.join(timeout=5)

    def test_async_loop_set_after_init(self, tmp_path: Path):
        """_async_loop is a running event loop immediately after __init__."""
        loop_instance = self._make_loop(tmp_path)
        assert loop_instance._async_loop is not None
        assert loop_instance._async_loop.is_running()
        self._teardown_loop(loop_instance)

    def test_same_loop_reused_across_run_once(self, tmp_path: Path):
        """_run_once uses the same _async_loop each time (no new loops)."""
        loop_instance = self._make_loop(tmp_path)
        loop_before = loop_instance._async_loop

        # Mock watcher and gardening to be no-ops
        loop_instance._watcher.run_once = MagicMock(return_value=[])

        async def fake_step(step):
            return {"needs_attention": False}

        loop_instance._gardening.run_step = fake_step

        loop_instance._run_once()
        loop_instance._run_once()

        assert loop_instance._async_loop is loop_before
        self._teardown_loop(loop_instance)

    def test_async_thread_stopped_after_stop(self, tmp_path: Path):
        """After start() + stop(), the dedicated async thread is no longer alive."""
        loop_instance = self._make_loop(tmp_path)

        # Mock watcher and gardening to be no-ops
        loop_instance._watcher.run_once = MagicMock(return_value=[])

        async def fake_step(step):
            return {"needs_attention": False}

        loop_instance._gardening.run_step = fake_step

        # Must call start() so that stop() actually shuts down the async loop
        loop_instance.start()
        time.sleep(0.2)  # Let the loop thread spin up
        loop_instance.stop()

        assert not loop_instance._async_thread.is_alive()

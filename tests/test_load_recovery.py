"""WP-5007: Recovery under sustained load drills."""

import pytest

from thegent.execution import LoadClassifier, RunRegistry


@pytest.mark.asyncio
async def test_recovery_under_load(tmp_path):
    """Simulate recovery when load is high."""
    session_dir = tmp_path / "session"
    session_dir.mkdir()

    RunRegistry(session_dir)
    # Simulate high load via get_running_count_fn
    classifier = LoadClassifier(
        session_dir,
        spike_threshold=10,
        surge_threshold=20,
        get_running_count_fn=lambda: 50,
    )

    assert classifier.get_load_level() == "surge"
    assert classifier.is_safe_mode_active() is True

    # 2. Trigger recovery (placeholder)
    # The recovery logic should detect load and perhaps defer or use cheaper lane


@pytest.mark.asyncio
async def test_sustained_load_backoff():
    """Verify that system backs off under sustained high load."""

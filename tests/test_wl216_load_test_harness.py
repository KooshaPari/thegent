"""Tests for WL-216: 1k+ Item Load Tests.

# @trace WL-216
"""

from __future__ import annotations

import pytest

from thegent.integrations.load_test_harness import LoadTestConfig, LoadTestHarness


class TestLoadTestConfig:
    """Tests for LoadTestConfig dataclass."""

    @pytest.mark.requirement("WL-216")
    def test_load_test_config_defaults(self):
        """# @trace WL-216 — LoadTestConfig has expected default values."""
        config = LoadTestConfig()
        assert config.item_count == 1000
        assert config.batch_size == 100

    @pytest.mark.requirement("WL-216")
    def test_load_test_config_custom_values(self):
        """# @trace WL-216 — LoadTestConfig can be created with custom values."""
        config = LoadTestConfig(item_count=5000, batch_size=250)
        assert config.item_count == 5000
        assert config.batch_size == 250


class TestLoadTestHarness:
    """Tests for LoadTestHarness class."""

    @pytest.mark.requirement("WL-216")
    def test_generate_items_count(self):
        """# @trace WL-216 — generate_items returns correct number of items."""
        config = LoadTestConfig(item_count=100)
        items = LoadTestHarness.generate_items(config)
        assert len(items) == 100

    @pytest.mark.requirement("WL-216")
    def test_generate_items_structure(self):
        """# @trace WL-216 — generated items have id and value fields."""
        config = LoadTestConfig(item_count=10)
        items = LoadTestHarness.generate_items(config)
        for i, item in enumerate(items):
            assert "id" in item
            assert "value" in item
            assert item["id"] == i
            assert item["value"] == f"item_{i}"

    @pytest.mark.requirement("WL-216")
    def test_generate_items_1000_plus(self):
        """# @trace WL-216 — generate_items can handle 1000+ items."""
        config = LoadTestConfig(item_count=1234)
        items = LoadTestHarness.generate_items(config)
        assert len(items) == 1234

    @pytest.mark.requirement("WL-216")
    def test_run_batch_single_batch(self):
        """# @trace WL-216 — run_batch with batch_size >= item_count returns single batch."""
        items = [{"id": i, "value": f"item_{i}"} for i in range(50)]
        batches = LoadTestHarness.run_batch(items, batch_size=100)
        assert len(batches) == 1
        assert len(batches[0]) == 50

    @pytest.mark.requirement("WL-216")
    def test_run_batch_multiple_batches(self):
        """# @trace WL-216 — run_batch splits items into multiple batches."""
        items = [{"id": i, "value": f"item_{i}"} for i in range(250)]
        batches = LoadTestHarness.run_batch(items, batch_size=100)
        assert len(batches) == 3
        assert len(batches[0]) == 100
        assert len(batches[1]) == 100
        assert len(batches[2]) == 50

    @pytest.mark.requirement("WL-216")
    def test_run_batch_exact_division(self):
        """# @trace WL-216 — run_batch handles exact division evenly."""
        items = [{"id": i, "value": f"item_{i}"} for i in range(300)]
        batches = LoadTestHarness.run_batch(items, batch_size=100)
        assert len(batches) == 3
        assert all(len(batch) == 100 for batch in batches)

    @pytest.mark.requirement("WL-216")
    def test_run_batch_empty_items(self):
        """# @trace WL-216 — run_batch handles empty items list."""
        batches = LoadTestHarness.run_batch([], batch_size=100)
        assert len(batches) == 0

    @pytest.mark.requirement("WL-216")
    def test_summarize_empty_batches(self):
        """# @trace WL-216 — summarize handles empty batches list."""
        summary = LoadTestHarness.summarize([])
        assert summary == {"total": 0, "batches": 0}

    @pytest.mark.requirement("WL-216")
    def test_summarize_single_batch(self):
        """# @trace WL-216 — summarize correctly tallies single batch."""
        batches = [[{"id": i, "value": f"item_{i}"} for i in range(50)]]
        summary = LoadTestHarness.summarize(batches)
        assert summary == {"total": 50, "batches": 1}

    @pytest.mark.requirement("WL-216")
    def test_summarize_multiple_batches(self):
        """# @trace WL-216 — summarize correctly tallies multiple batches."""
        batches = [
            [{"id": i, "value": f"item_{i}"} for i in range(100)],
            [{"id": i, "value": f"item_{i}"} for i in range(100)],
            [{"id": i, "value": f"item_{i}"} for i in range(50)],
        ]
        summary = LoadTestHarness.summarize(batches)
        assert summary == {"total": 250, "batches": 3}

    @pytest.mark.requirement("WL-216")
    def test_full_workflow_1000_items(self):
        """# @trace WL-216 — full workflow with 1000 items."""
        config = LoadTestConfig(item_count=1000, batch_size=100)
        items = LoadTestHarness.generate_items(config)
        batches = LoadTestHarness.run_batch(items, batch_size=config.batch_size)
        summary = LoadTestHarness.summarize(batches)

        assert summary["total"] == 1000
        assert summary["batches"] == 10

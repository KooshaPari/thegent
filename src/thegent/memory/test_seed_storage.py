"""Tests for seed storage with JSONL persistence."""

from __future__ import annotations

import orjson as json
import tempfile
from pathlib import Path

import pytest

from .seed_detector import Seed, SeedSource
from .seed_storage import SeedStorage


@pytest.fixture
def temp_storage_dir():
    """Create temporary directory for storage tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def storage(temp_storage_dir):
    """Create SeedStorage instance with temp directory."""
    storage_path = temp_storage_dir / "seeds.jsonl"
    return SeedStorage(storage_path=storage_path)


@pytest.fixture
def sample_seed():
    """Create sample seed for testing."""
    return Seed(
        id="test1",
        text="What if we optimized the database?",
        source=SeedSource.USER_PROMPT,
        confidence=0.9,
        timestamp="2026-02-19T00:00:00Z",
        tags=["performance", "database"],
        status="new",
        detected_by="explicit_marker",
    )


class TestSeedStorageWrite:
    """Test writing seeds to storage."""

    def test_store_seed(self, storage, sample_seed):
        """Test storing a single seed."""
        seed_id = storage.store_seed(sample_seed)

        assert seed_id == "test1"
        assert storage.storage_path.exists()

    def test_store_seed_creates_directory(self, temp_storage_dir):
        """Test that storing seed creates necessary directories."""
        nested_path = temp_storage_dir / "docs" / "research" / "seeds.jsonl"
        storage = SeedStorage(storage_path=nested_path)

        seed = Seed(
            id="test",
            text="Test",
            source=SeedSource.USER_PROMPT,
            confidence=0.9,
            timestamp="2026-02-19T00:00:00Z",
            tags=[],
        )
        storage.store_seed(seed)

        assert nested_path.exists()

    def test_store_multiple_seeds(self, storage):
        """Test storing multiple seeds."""
        seed1 = Seed(
            id="s1",
            text="Seed 1",
            source=SeedSource.USER_PROMPT,
            confidence=0.9,
            timestamp="2026-02-19T00:00:00Z",
            tags=[],
        )
        seed2 = Seed(
            id="s2",
            text="Seed 2",
            source=SeedSource.AGENT_OUTPUT,
            confidence=0.8,
            timestamp="2026-02-19T00:00:01Z",
            tags=["test"],
        )

        storage.store_seed(seed1)
        storage.store_seed(seed2)

        # Verify both are in file
        with open(storage.storage_path) as f:
            lines = f.readlines()

        assert len(lines) == 2

    def test_duplicate_seed_prevention(self, storage, sample_seed):
        """Test that duplicate seeds are not stored."""
        storage.store_seed(sample_seed)
        second_id = storage.store_seed(sample_seed)

        assert second_id == "test1"

        # Verify only one copy exists
        with open(storage.storage_path) as f:
            lines = [l.strip() for l in f if l.strip()]

        assert len(lines) == 1

    def test_jsonl_format(self, storage, sample_seed):
        """Test that seeds are stored in JSONL format."""
        storage.store_seed(sample_seed)

        with open(storage.storage_path) as f:
            line = f.readline()

        # Should be valid JSON
        data = json.loads(line)
        assert data["id"] == "test1"
        assert data["text"] == "What if we optimized the database?"


class TestSeedStorageRead:
    """Test reading seeds from storage."""

    def test_load_empty_storage(self, storage):
        """Test loading from non-existent file."""
        seeds = storage.load_seeds()
        assert seeds == []

    def test_load_single_seed(self, storage, sample_seed):
        """Test loading a single seed."""
        storage.store_seed(sample_seed)
        seeds = storage.load_seeds()

        assert len(seeds) == 1
        assert seeds[0].id == "test1"
        assert seeds[0].text == "What if we optimized the database?"

    def test_load_multiple_seeds(self, storage):
        """Test loading multiple seeds."""
        seed1 = Seed(
            id="s1",
            text="Seed 1",
            source=SeedSource.USER_PROMPT,
            confidence=0.9,
            timestamp="2026-02-19T00:00:00Z",
            tags=[],
        )
        seed2 = Seed(
            id="s2",
            text="Seed 2",
            source=SeedSource.AGENT_OUTPUT,
            confidence=0.8,
            timestamp="2026-02-19T00:00:01Z",
            tags=[],
        )

        storage.store_seed(seed1)
        storage.store_seed(seed2)

        seeds = storage.load_seeds()
        assert len(seeds) == 2
        assert seeds[0].id == "s1"
        assert seeds[1].id == "s2"

    def test_load_preserves_metadata(self, storage):
        """Test that loading preserves seed metadata."""
        original = Seed(
            id="test",
            text="Test seed",
            source=SeedSource.CLAUDE_HISTORY,
            confidence=0.75,
            timestamp="2026-02-19T12:00:00Z",
            tags=["tag1", "tag2"],
            status="developing",
            detected_by="llm",
        )

        storage.store_seed(original)
        loaded = storage.load_seeds()[0]

        assert loaded.id == original.id
        assert loaded.text == original.text
        assert loaded.source == original.source
        assert loaded.confidence == original.confidence
        assert loaded.timestamp == original.timestamp
        assert loaded.tags == original.tags
        assert loaded.status == original.status
        assert loaded.detected_by == original.detected_by


class TestSeedStorageQuery:
    """Test querying seeds."""

    @pytest.fixture
    def populated_storage(self, storage):
        """Create storage with multiple seeds."""
        seeds = [
            Seed(
                id="s1",
                text="Performance issue",
                source=SeedSource.USER_PROMPT,
                confidence=0.9,
                timestamp="2026-02-19T00:00:00Z",
                tags=["performance"],
                status="new",
            ),
            Seed(
                id="s2",
                text="Security concern",
                source=SeedSource.AGENT_OUTPUT,
                confidence=0.8,
                timestamp="2026-02-19T00:00:01Z",
                tags=["security"],
                status="developing",
            ),
            Seed(
                id="s3",
                text="API design",
                source=SeedSource.CLAUDE_HISTORY,
                confidence=0.7,
                timestamp="2026-02-19T00:00:02Z",
                tags=["api"],
                status="implemented",
            ),
        ]

        for seed in seeds:
            storage.store_seed(seed)

        return storage

    def test_find_by_id(self, populated_storage):
        """Test finding seed by ID."""
        seed = populated_storage.find_by_id("s1")

        assert seed is not None
        assert seed.id == "s1"
        assert "Performance" in seed.text

    def test_find_by_id_not_found(self, populated_storage):
        """Test finding non-existent seed by ID."""
        seed = populated_storage.find_by_id("nonexistent")
        assert seed is None

    def test_find_by_text(self, populated_storage):
        """Test finding seed by text."""
        seed = populated_storage.find_by_text("Performance issue")

        assert seed is not None
        assert seed.id == "s1"

    def test_find_by_text_not_found(self, populated_storage):
        """Test finding non-existent seed by text."""
        seed = populated_storage.find_by_text("Nonexistent text")
        assert seed is None

    def test_find_by_status(self, populated_storage):
        """Test finding seeds by status."""
        new_seeds = populated_storage.find_by_status("new")
        assert len(new_seeds) == 1
        assert new_seeds[0].id == "s1"

        dev_seeds = populated_storage.find_by_status("developing")
        assert len(dev_seeds) == 1
        assert dev_seeds[0].id == "s2"

    def test_find_by_tag(self, populated_storage):
        """Test finding seeds by tag."""
        perf_seeds = populated_storage.find_by_tag("performance")
        assert len(perf_seeds) == 1
        assert perf_seeds[0].id == "s1"

        security_seeds = populated_storage.find_by_tag("security")
        assert len(security_seeds) == 1
        assert security_seeds[0].id == "s2"

    def test_find_by_source(self, populated_storage):
        """Test finding seeds by source."""
        user_seeds = populated_storage.find_by_source(SeedSource.USER_PROMPT)
        assert len(user_seeds) == 1
        assert user_seeds[0].id == "s1"

        agent_seeds = populated_storage.find_by_source(SeedSource.AGENT_OUTPUT)
        assert len(agent_seeds) == 1
        assert agent_seeds[0].id == "s2"


class TestSeedStorageUpdate:
    """Test updating seeds."""

    def test_update_status(self, storage, sample_seed):
        """Test updating seed status."""
        storage.store_seed(sample_seed)
        result = storage.update_seed("test1", status="developing")

        assert result is True

        updated = storage.find_by_id("test1")
        assert updated.status == "developing"

    def test_update_tags(self, storage, sample_seed):
        """Test updating seed tags."""
        storage.store_seed(sample_seed)
        result = storage.update_seed("test1", tags=["new_tag"])

        assert result is True

        updated = storage.find_by_id("test1")
        assert "new_tag" in updated.tags

    def test_update_context(self, storage, sample_seed):
        """Test updating seed context."""
        storage.store_seed(sample_seed)
        context = "Some additional context"
        result = storage.update_seed("test1", context=context)

        assert result is True

        updated = storage.find_by_id("test1")
        assert updated.context == context

    def test_update_nonexistent_seed(self, storage):
        """Test updating non-existent seed."""
        result = storage.update_seed("nonexistent", status="developing")
        assert result is False

    def test_update_multiple_fields(self, storage, sample_seed):
        """Test updating multiple fields at once."""
        storage.store_seed(sample_seed)
        storage.update_seed("test1", status="developed", tags=["tag1", "tag2"])

        updated = storage.find_by_id("test1")
        assert updated.status == "developed"
        assert updated.tags == ["tag1", "tag2"]


class TestSeedStorageArchive:
    """Test archiving seeds."""

    def test_archive_seed(self, storage, sample_seed):
        """Test archiving a seed."""
        storage.store_seed(sample_seed)
        result = storage.archive_seed("test1")

        assert result is True

        archived = storage.find_by_id("test1")
        assert archived.status == "archived"

    def test_delete_seed(self, storage, sample_seed):
        """Test deleting (archiving) a seed."""
        storage.store_seed(sample_seed)
        result = storage.delete_seed("test1")

        assert result is True

        deleted = storage.find_by_id("test1")
        assert deleted.status == "archived"

    def test_delete_nonexistent_seed(self, storage):
        """Test deleting non-existent seed."""
        result = storage.delete_seed("nonexistent")
        assert result is False


class TestSeedStorageStats:
    """Test statistics generation."""

    @pytest.fixture
    def populated_storage(self, storage):
        """Create storage with seeds of various statuses."""
        seeds = [
            Seed(
                id="s1",
                text="Seed 1",
                source=SeedSource.USER_PROMPT,
                confidence=0.9,
                timestamp="2026-02-19T00:00:00Z",
                tags=[],
                status="new",
            ),
            Seed(
                id="s2",
                text="Seed 2",
                source=SeedSource.AGENT_OUTPUT,
                confidence=0.8,
                timestamp="2026-02-19T00:00:01Z",
                tags=[],
                status="developing",
            ),
            Seed(
                id="s3",
                text="Seed 3",
                source=SeedSource.CLAUDE_HISTORY,
                confidence=0.7,
                timestamp="2026-02-19T00:00:02Z",
                tags=[],
                status="implemented",
            ),
            Seed(
                id="s4",
                text="Seed 4",
                source=SeedSource.USER_PROMPT,
                confidence=0.4,
                timestamp="2026-02-19T00:00:03Z",
                tags=[],
                status="new",
            ),
        ]

        for seed in seeds:
            storage.store_seed(seed)

        return storage

    def test_stats_total_count(self, populated_storage):
        """Test total seed count in stats."""
        stats = populated_storage.get_stats()
        assert stats["total"] == 4

    def test_stats_by_status(self, populated_storage):
        """Test stats breakdown by status."""
        stats = populated_storage.get_stats()

        assert stats["by_status"]["new"] == 2
        assert stats["by_status"]["developing"] == 1
        assert stats["by_status"]["implemented"] == 1

    def test_stats_by_source(self, populated_storage):
        """Test stats breakdown by source."""
        stats = populated_storage.get_stats()

        assert stats["by_source"]["user_prompt"] == 2
        assert stats["by_source"]["agent_output"] == 1
        assert stats["by_source"]["claude_history"] == 1

    def test_stats_by_confidence(self, populated_storage):
        """Test stats breakdown by confidence level."""
        stats = populated_storage.get_stats()

        # 0.9 (high), 0.8 (medium), 0.7 (medium), 0.4 (low)
        assert stats["by_confidence"]["high"] == 1
        assert stats["by_confidence"]["medium"] == 2
        assert stats["by_confidence"]["low"] == 1

    def test_stats_avg_confidence(self, populated_storage):
        """Test average confidence calculation."""
        stats = populated_storage.get_stats()

        expected_avg = (0.9 + 0.8 + 0.7 + 0.4) / 4
        assert abs(stats["avg_confidence"] - expected_avg) < 0.01


class TestSeedStorageExport:
    """Test exporting seeds to markdown."""

    def test_export_markdown_content(self, populated_storage):
        """Test markdown export content."""
        markdown = populated_storage.export_markdown()

        assert "# Idea Seeds" in markdown
        assert "Seed 1" in markdown
        assert "Seed 2" in markdown
        assert "Total seeds: 2" in markdown

    def test_export_markdown_by_status(self, populated_storage):
        """Test markdown export groups by status."""
        markdown = populated_storage.export_markdown()

        assert "## New" in markdown
        assert "## Developing" in markdown

    def test_export_to_file(self, storage, populated_storage, temp_storage_dir):
        """Test exporting markdown to file."""
        output_path = temp_storage_dir / "seeds.md"
        markdown = populated_storage.export_markdown(output_path)

        assert output_path.exists()

        with open(output_path) as f:
            content = f.read()

        assert content == markdown
        assert "# Idea Seeds" in content

    @pytest.fixture
    def populated_storage(self, storage):
        """Create storage with multiple seeds."""
        seeds = [
            Seed(
                id="s1",
                text="Seed 1",
                source=SeedSource.USER_PROMPT,
                confidence=0.9,
                timestamp="2026-02-19T00:00:00Z",
                tags=["tag1"],
                status="new",
            ),
            Seed(
                id="s2",
                text="Seed 2",
                source=SeedSource.AGENT_OUTPUT,
                confidence=0.8,
                timestamp="2026-02-19T00:00:01Z",
                tags=["tag2"],
                status="developing",
            ),
        ]

        for seed in seeds:
            storage.store_seed(seed)

        return storage

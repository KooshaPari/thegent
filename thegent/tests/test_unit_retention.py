"""Tests for WP-3006: Compliance evidence retention."""

import time
from unittest.mock import MagicMock

import pytest

from thegent.config import ThegentSettings
from thegent.governance.retention import EvidenceRetentionManager


@pytest.fixture
def mock_settings(tmp_path):
    settings = MagicMock(spec=ThegentSettings)
    settings.session_dir = tmp_path / "session"
    settings.session_dir.mkdir(parents=True)
    return settings


def test_retention_manager_archives_old_files(mock_settings):
    evidence_dir = mock_settings.session_dir / "evidence"
    evidence_dir.mkdir()

    # Create an old file and a new file
    old_file = evidence_dir / "old_evidence.json"
    new_file = evidence_dir / "new_evidence.json"

    old_file.write_text("old data")
    new_file.write_text("new data")

    # Set mtime back 31 days
    old_time = time.time() - (31 * 86400)
    import os

    os.utime(old_file, (old_time, old_time))

    manager = EvidenceRetentionManager(mock_settings)
    manager.retention_days = 30

    results = manager.enforce_retention()

    assert results["archived"] == 1
    assert not old_file.exists()
    assert new_file.exists()
    assert (mock_settings.session_dir / "archive" / "old_evidence.json").exists()


def test_retention_manager_list_archived(mock_settings):
    archive_dir = mock_settings.session_dir / "archive"
    archive_dir.mkdir(parents=True)

    (archive_dir / "archived_1.json").write_text("data")

    manager = EvidenceRetentionManager(mock_settings)
    archived = manager.list_archived()

    assert "archived_1.json" in archived
    assert len(archived) == 1

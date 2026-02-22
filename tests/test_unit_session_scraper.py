from __future__ import annotations

import json
from pathlib import Path

from thegent.orchestration.state.session_scraper import SessionScraper


class _Pane:
    def __init__(self, pane_id: str) -> None:
        self.pane_id = pane_id


def test_collect_snapshot_extracts_structured_fields(monkeypatch, tmp_path: Path) -> None:
    scraper = SessionScraper(project_root=tmp_path)

    sample_capture = """
> add force flag to dex
$ rg --files
fact: dex should always include --search
decision: map continue to resume
edited src/thegent/cli/apps/main.py
tracking #wl155 #session-memory
"""

    monkeypatch.setattr("thegent.orchestration.state.session_scraper.list_tmux_panes", lambda: [_Pane("%1")])
    monkeypatch.setattr("thegent.orchestration.state.session_scraper.is_claude_code_pane", lambda pane: True)
    monkeypatch.setattr(
        "thegent.orchestration.state.session_scraper.capture_tmux_pane",
        lambda pane_id, last_lines=150: sample_capture,
    )
    monkeypatch.setattr("thegent.orchestration.state.session_scraper.SessionScraper.scrape_claude_history", lambda self: [])
    monkeypatch.setattr("thegent.orchestration.state.session_scraper.SessionScraper.scrape_ante_history", lambda self: [])

    snapshot = scraper.collect_snapshot(trigger="tool_use")

    assert snapshot.trigger == "tool_use"
    assert "add force flag to dex" in snapshot.prompts
    assert "rg --files" in snapshot.commands
    assert "src/thegent/cli/apps/main.py" in snapshot.files
    assert "dex should always include --search" in snapshot.facts
    assert "map continue to resume" in snapshot.decisions
    assert "wl155" in snapshot.tags
    assert "session-memory" in snapshot.tags
    assert "tmux:%1" in snapshot.sources


def test_persist_snapshot_writes_json(monkeypatch, tmp_path: Path) -> None:
    scraper = SessionScraper(project_root=tmp_path)

    monkeypatch.setattr("thegent.orchestration.state.session_scraper.list_tmux_panes", lambda: [])
    monkeypatch.setattr("thegent.orchestration.state.session_scraper.SessionScraper.scrape_claude_history", lambda self: ["p1"])
    monkeypatch.setattr("thegent.orchestration.state.session_scraper.SessionScraper.scrape_ante_history", lambda self: ["p2"])

    out_dir = tmp_path / "snapshots"
    path = scraper.persist_snapshot(trigger="periodic", out_dir=out_dir)

    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["trigger"] == "periodic"
    assert data["prompts"] == ["p1", "p2"]
    assert data["sources"] == ["claude-history", "ante-history"]


def test_list_snapshots_filters_by_trigger_and_tag(monkeypatch, tmp_path: Path) -> None:
    scraper = SessionScraper(project_root=tmp_path)
    snapshots_dir = tmp_path / "snapshots"
    snapshots_dir.mkdir()

    payload_a = {
        "snapshot_id": "snapshot-a",
        "trigger": "tool_use",
        "captured_at": "2026-02-22T00:00:00+00:00",
        "project_root": str(tmp_path),
        "prompts": [],
        "commands": [],
        "files": [],
        "facts": [],
        "decisions": [],
        "tags": ["wl155"],
        "sources": [],
    }
    payload_b = {**payload_a, "snapshot_id": "snapshot-b", "trigger": "error", "tags": ["wl156"]}

    path_a = snapshots_dir / "snapshot-a.json"
    path_b = snapshots_dir / "snapshot-b.json"
    path_a.write_text(json.dumps(payload_a), encoding="utf-8")
    path_b.write_text(json.dumps(payload_b), encoding="utf-8")

    tool_use = scraper.list_snapshots(trigger="tool_use", root_dir=snapshots_dir)
    assert len(tool_use) == 1
    assert tool_use[0].name == "snapshot-a.json"

    wl156 = scraper.list_snapshots(tag="wl156", root_dir=snapshots_dir)
    assert len(wl156) == 1
    assert wl156[0].name == "snapshot-b.json"


def test_latest_snapshot_and_markdown_export(tmp_path: Path) -> None:
    scraper = SessionScraper(project_root=tmp_path)
    snapshots_dir = tmp_path / "snapshots"
    snapshots_dir.mkdir()

    payload = {
        "snapshot_id": "snapshot-z",
        "trigger": "session_change",
        "captured_at": "2026-02-22T00:00:00+00:00",
        "project_root": str(tmp_path),
        "prompts": ["p"],
        "commands": ["rg --files"],
        "files": ["src/app.py"],
        "facts": ["f"],
        "decisions": ["d"],
        "tags": ["wl156"],
        "sources": ["tmux:%1"],
    }
    json_path = snapshots_dir / "snapshot-z.json"
    json_path.write_text(json.dumps(payload), encoding="utf-8")

    loaded = scraper.latest_snapshot(root_dir=snapshots_dir)
    assert loaded is not None
    assert loaded.snapshot_id == "snapshot-z"
    assert loaded.trigger == "session_change"

    md_path = scraper.export_snapshot_markdown(json_path)
    content = md_path.read_text(encoding="utf-8")
    assert "# Session Snapshot: snapshot-z" in content
    assert "## Commands" in content
    assert "`rg --files`" in content


def test_summarize_snapshots_and_index_exports(tmp_path: Path) -> None:
    scraper = SessionScraper(project_root=tmp_path)
    snapshots_dir = tmp_path / "snapshots"
    snapshots_dir.mkdir()

    payload_a = {
        "snapshot_id": "snapshot-1",
        "trigger": "tool_use",
        "captured_at": "2026-02-22T00:00:00+00:00",
        "project_root": str(tmp_path),
        "prompts": ["p1", "p2"],
        "commands": ["c1"],
        "files": ["f1.py"],
        "facts": [],
        "decisions": [],
        "tags": ["wl155", "memory"],
        "sources": [],
    }
    payload_b = {
        "snapshot_id": "snapshot-2",
        "trigger": "error",
        "captured_at": "2026-02-22T01:00:00+00:00",
        "project_root": str(tmp_path),
        "prompts": ["p3"],
        "commands": ["c2", "c3"],
        "files": ["f2.py", "f3.py"],
        "facts": [],
        "decisions": [],
        "tags": ["wl156"],
        "sources": [],
    }
    (snapshots_dir / "snapshot-1.json").write_text(json.dumps(payload_a), encoding="utf-8")
    (snapshots_dir / "snapshot-2.json").write_text(json.dumps(payload_b), encoding="utf-8")

    summary = scraper.summarize_snapshots(root_dir=snapshots_dir)
    assert summary["total_snapshots"] == 2
    assert summary["total_prompts"] == 3
    assert summary["total_commands"] == 3
    assert summary["total_files"] == 3
    assert summary["trigger_counts"]["tool_use"] == 1
    assert summary["trigger_counts"]["error"] == 1
    assert summary["tag_counts"]["wl155"] == 1
    assert summary["tag_counts"]["wl156"] == 1

    index_json = scraper.persist_snapshot_index(root_dir=snapshots_dir, out_path=tmp_path / "snapshot-index.json")
    assert index_json.exists()
    index_data = json.loads(index_json.read_text(encoding="utf-8"))
    assert index_data["total_snapshots"] == 2

    index_md = scraper.export_snapshot_index_markdown(root_dir=snapshots_dir, out_path=tmp_path / "snapshot-index.md")
    assert index_md.exists()
    md_content = index_md.read_text(encoding="utf-8")
    assert "# Snapshot Index" in md_content
    assert "## Trigger Counts" in md_content
    assert "tool_use: 1" in md_content

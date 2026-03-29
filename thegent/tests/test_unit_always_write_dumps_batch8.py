from __future__ import annotations

import os
from pathlib import Path

from thegent.research.always_write_dumps import ConversationDumper


def _write_dump(
    docs_dir: Path,
    *,
    category: str,
    name: str,
    suffix: str,
    mtime: int,
) -> Path:
    category_dir = docs_dir / category
    category_dir.mkdir(parents=True, exist_ok=True)
    dump_path = category_dir / f"conversation-{name}{suffix}"
    dump_path.write_text("x", encoding="utf-8")
    os.utime(dump_path, (mtime, mtime))
    return dump_path


def test_latest_dump_by_category_returns_latest_markdown_per_category(
    tmp_path: Path,
) -> None:
    dumper = ConversationDumper(docs_dir=tmp_path)
    latest_execution = _write_dump(
        tmp_path,
        category="execution",
        name="exec-new",
        suffix=".md",
        mtime=2,
    )
    _write_dump(
        tmp_path,
        category="execution",
        name="exec-old",
        suffix=".md",
        mtime=1,
    )
    latest_research = _write_dump(
        tmp_path,
        category="research",
        name="research-new",
        suffix=".md",
        mtime=4,
    )
    _write_dump(
        tmp_path,
        category="research",
        name="research-old",
        suffix=".md",
        mtime=3,
    )

    latest = dumper.latest_dump_by_category()

    assert {k: Path(v) for k, v in latest.items()} == {
        "execution": latest_execution,
        "research": latest_research,
    }


def test_latest_dump_by_category_json_only_returns_latest_json_per_category(
    tmp_path: Path,
) -> None:
    dumper = ConversationDumper(docs_dir=tmp_path)
    latest_execution = _write_dump(
        tmp_path,
        category="execution",
        name="exec-new",
        suffix=".json",
        mtime=11,
    )
    _write_dump(
        tmp_path,
        category="execution",
        name="exec-old",
        suffix=".json",
        mtime=10,
    )
    latest_research = _write_dump(
        tmp_path,
        category="research",
        name="research-new",
        suffix=".json",
        mtime=13,
    )
    _write_dump(
        tmp_path,
        category="research",
        name="research-old",
        suffix=".json",
        mtime=12,
    )

    latest = dumper.latest_dump_by_category(json_only=True)

    assert {k: Path(v) for k, v in latest.items()} == {
        "execution": latest_execution,
        "research": latest_research,
    }


def test_dump_index_payload_includes_latest_by_category_key(tmp_path: Path) -> None:
    dumper = ConversationDumper(docs_dir=tmp_path)

    payload = dumper.dump_index_payload()

    assert "latest_by_category" in payload


def test_export_dump_index_markdown_includes_latest_by_category_section(
    tmp_path: Path,
) -> None:
    dumper = ConversationDumper(docs_dir=tmp_path)

    markdown_path = dumper.export_dump_index_markdown()
    markdown = markdown_path.read_text(encoding="utf-8")

    assert "Latest By Category" in markdown


def test_empty_docs_dir_yields_empty_latest_by_category_mapping(tmp_path: Path) -> None:
    dumper = ConversationDumper(docs_dir=tmp_path)

    assert dumper.latest_dump_by_category() == {}
    assert dumper.latest_dump_by_category(json_only=True) == {}
    assert dumper.dump_index_payload()["latest_by_category"] == {}

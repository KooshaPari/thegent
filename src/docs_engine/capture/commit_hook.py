"""Write WorklogEntry on every commit.

# @trace FR-DOCS-005
"""

from __future__ import annotations

import datetime
from pathlib import Path

from thegent.infra.fast_yaml_parser import yaml_dump

from docs_engine.db.indexer import DocIndexer
from docs_engine.schema.base import DocFrontmatter, DocStatus, DocType


def write_worklog_entry(
    docs_root: Path,
    db_path: Path,
    commit_sha: str,
    commit_msg: str,
    files_changed: list[str],
) -> Path:
    worklogs_dir = docs_root / "worklogs"
    worklogs_dir.mkdir(parents=True, exist_ok=True)
    seq = len(list(worklogs_dir.glob("WL-*.md"))) + 1
    path = worklogs_dir / f"WL-{seq:04d}.md"

    today = datetime.date.today().isoformat()
    fm = DocFrontmatter(
        type=DocType.WORKLOG,
        status=DocStatus.PUBLISHED,
        date=today,
        title=f"WL-{seq:04d}: {commit_msg[:60]}",
        layer=3,
        git_commit=commit_sha,
    )
    fm_dict = {k: v for k, v in fm.model_dump(mode="json").items() if v not in ("", [], None)}
    fm_str = yaml_dump(fm_dict, default_flow_style=False, allow_unicode=True)

    files_section = "\n".join(f"- `{f}`" for f in files_changed) if files_changed else "- (none)"
    body = (
        f"# WL-{seq:04d}: {commit_msg}\n\n"
        f"## What Changed\n{commit_msg}\n\n"
        f"## Files Touched\n{files_section}\n\n"
        "## Next\n"
        "- Add follow-up tasks for regression coverage or integration hardening if needed.\n"
        "- Link any impacted Work Stream items to close the loop.\n"
    )
    path.write_text(f"---\n{fm_str}---\n\n{body}")

    indexer = DocIndexer(db_path)
    indexer.init_schema()
    indexer.upsert_doc(str(path.relative_to(docs_root)), fm.model_dump())
    return path

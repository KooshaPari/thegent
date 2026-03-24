"""Write conversation dumps to docs/research/ and index them.

# @trace FR-DOCS-004
"""

from __future__ import annotations

import datetime
from pathlib import Path

from thegent.infra.fast_yaml_parser import yaml_dump

from docs_engine.db.indexer import DocIndexer
from docs_engine.schema.base import DocFrontmatter, DocStatus, DocType


def write_conversation_dump(
    docs_root: Path,
    db_path: Path,
    session_id: str,
    content: str,
) -> Path:
    today = datetime.date.today().isoformat()
    filename = f"CONVERSATION_DUMP_{today}.md"
    path = docs_root / "research" / filename
    path.parent.mkdir(parents=True, exist_ok=True)

    fm = DocFrontmatter(
        type=DocType.CONVERSATION_DUMP,
        status=DocStatus.DRAFT,
        date=today,
        title=f"Conversation Dump {today}",
        layer=0,
        session_id=session_id,
    )
    fm_dict = {k: v for k, v in fm.model_dump(mode="json").items() if v not in ("", [], None)}
    fm_str = yaml_dump(fm_dict, default_flow_style=False, allow_unicode=True)

    if path.exists():
        path.write_text(path.read_text() + f"\n\n---\n\n{content}")
    else:
        path.write_text(f"---\n{fm_str}---\n\n{content}")

    indexer = DocIndexer(db_path)
    indexer.init_schema()
    indexer.upsert_doc(str(path.relative_to(docs_root)), fm.model_dump())
    return path

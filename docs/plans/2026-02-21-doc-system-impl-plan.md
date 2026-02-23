# Agent-Driven Documentation System — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a fully agentic doc system: capture → index (SQLite) → promote → surface (VitePress), covering all 26 doc types across 5 lifecycle layers with MCP tools, CLI, git hooks, and a semantic knowledge extractor.

**Architecture:** `docs_engine` Python package in `thegent/` owns schema validation (Pydantic), SQLite indexing (via watchdog), capture hooks (session/commit/test), sidebar generation, semantic extraction, and FastMCP tool registration. VitePress consumes the SQLite index via TypeScript data loaders. A workspace-level VitePress hub replaces MkDocs.

**Tech Stack:** Python (Pydantic, typer, watchdog, Jinja2, structlog, orjson), SQLite (stdlib), FastMCP, VitePress (Vue 3, TypeScript), git-cliff (Rust CLI), watchdog for fs events.

**Design doc:** `docs/plans/2026-02-21-doc-system-design.md`

---

## Phase 1 — Foundation: Schema + DB + DocWriter

### Task 1: Package scaffold + base Pydantic schema

**Files:**
- Create: `thegent/docs_engine/__init__.py`
- Create: `thegent/docs_engine/schema/__init__.py`
- Create: `thegent/docs_engine/schema/base.py`
- Create: `thegent/docs_engine/schema/registry.py`
- Test: `thegent/tests/docs_engine/test_schema_base.py`

**Step 1: Write failing tests**

```python
# thegent/tests/docs_engine/test_schema_base.py
import pytest
from docs_engine.schema.base import DocFrontmatter, DocType, DocStatus, DocLayer

def test_base_schema_requires_type():
    with pytest.raises(Exception):
        DocFrontmatter(status="draft", date="2026-02-21", title="x", layer=1)

def test_base_schema_valid():
    doc = DocFrontmatter(
        type=DocType.IDEA,
        status=DocStatus.DRAFT,
        date="2026-02-21",
        title="My idea",
        layer=DocLayer.INFORMAL,
    )
    assert doc.type == DocType.IDEA
    assert doc.layer == DocLayer.INFORMAL

def test_base_schema_rejects_invalid_status():
    with pytest.raises(Exception):
        DocFrontmatter(type=DocType.IDEA, status="NOPE", date="2026-02-21", title="x", layer=1)
```

**Step 2: Run to verify failure**

```bash
cd thegent && uv run pytest tests/docs_engine/test_schema_base.py -v
```
Expected: `ModuleNotFoundError: No module named 'docs_engine'`

**Step 3: Implement**

```python
# thegent/docs_engine/schema/base.py
from __future__ import annotations
from enum import StrEnum
from typing import Optional
from pydantic import BaseModel, Field
import datetime

class DocType(StrEnum):
    CONVERSATION_DUMP = "conversation-dump"
    SESSION_MEMORY = "session-memory"
    SCRATCH = "scratch"
    AGENT_WORKLOG = "agent-worklog"
    IDEA = "idea"
    RESEARCH = "research"
    DEBUG_LOG = "debug-log"
    CHANGE_PROPOSAL = "change-proposal"
    WORKLOG = "worklog"
    PRD = "prd"
    FR = "fr"
    ADR = "adr"
    USER_JOURNEY = "user-journey"
    IMPL_PLAN = "impl-plan"
    CONTEXT_DOC = "context-doc"
    ARCH_DOC = "arch-doc"
    DESIGN_DOC = "design-doc"
    SPRINT_PLAN = "sprint-plan"
    CHANGE_DESIGN = "change-design"
    CHANGE_TASKS = "change-tasks"
    TEST_LOG = "test-log"
    CHANGELOG = "changelog"
    COMPLETION_REPORT = "completion-report"
    SPRINT_RETRO = "sprint-retro"
    EPIC_RETRO = "epic-retro"
    INCIDENT_RETRO = "incident-retro"
    KB_EXTRACT = "kb-extract"

class DocStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    STAGING = "staging"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"

class DocLayer(int):
    RAW = 0
    INFORMAL = 1
    FORMAL = 2
    AUDIT = 3
    KB = 4

class DocFrontmatter(BaseModel):
    type: DocType
    status: DocStatus
    date: str  # YYYY-MM-DD
    title: str
    layer: int = Field(ge=0, le=4)
    relates_to: list[str] = Field(default_factory=list)
    traces_to: list[str] = Field(default_factory=list)
    author: str = "agent"
    session_id: str = ""
    git_commit: str = ""
    tags: list[str] = Field(default_factory=list)
```

```python
# thegent/docs_engine/schema/__init__.py
from .base import DocFrontmatter, DocType, DocStatus, DocLayer
from .registry import SCHEMA_REGISTRY

__all__ = ["DocFrontmatter", "DocType", "DocStatus", "DocLayer", "SCHEMA_REGISTRY"]
```

```python
# thegent/docs_engine/schema/registry.py
from .base import DocType, DocFrontmatter

SCHEMA_REGISTRY: dict[DocType, type[DocFrontmatter]] = {
    t: DocFrontmatter for t in DocType
}
```

```python
# thegent/docs_engine/__init__.py
"""Agent-driven documentation system for thegent."""
__version__ = "0.1.0"
```

**Step 4: Register package in pyproject.toml**

In `thegent/pyproject.toml`, under `[tool.uv.sources]` or packages list, ensure `docs_engine` is discoverable. Add to dependencies:
```toml
"jinja2>=3.1",
"watchdog>=4.0",
```

**Step 5: Run tests to verify pass**

```bash
cd thegent && uv run pytest tests/docs_engine/test_schema_base.py -v
```
Expected: 3 PASSED

**Step 6: Commit**

```bash
git add thegent/docs_engine/ thegent/tests/docs_engine/test_schema_base.py thegent/pyproject.toml
git commit -m "feat(docs-engine): add base Pydantic frontmatter schema + DocType/Status/Layer enums"
```

---

### Task 2: SQLite DB schema + indexer

**Files:**
- Create: `thegent/docs_engine/db/__init__.py`
- Create: `thegent/docs_engine/db/schema.sql`
- Create: `thegent/docs_engine/db/indexer.py`
- Create: `thegent/docs_engine/db/queries.py`
- Test: `thegent/tests/docs_engine/test_db_indexer.py`

**Step 1: Write failing tests**

```python
# thegent/tests/docs_engine/test_db_indexer.py
import pytest
import tempfile
from pathlib import Path
from docs_engine.db.indexer import DocIndexer
from docs_engine.db.queries import DocQueries

@pytest.fixture
def tmp_db(tmp_path):
    db_path = tmp_path / "test.db"
    indexer = DocIndexer(db_path)
    indexer.init_schema()
    return indexer, DocQueries(db_path)

def test_index_doc(tmp_db):
    indexer, queries = tmp_db
    indexer.upsert_doc(
        path="docs/ideas/2026-02-21-test.md",
        frontmatter={"type": "idea", "status": "draft", "title": "Test idea", "layer": 1, "date": "2026-02-21"},
    )
    results = queries.get_by_type("idea")
    assert len(results) == 1
    assert results[0]["title"] == "Test idea"

def test_update_doc_status(tmp_db):
    indexer, queries = tmp_db
    indexer.upsert_doc(
        path="docs/ideas/2026-02-21-test.md",
        frontmatter={"type": "idea", "status": "draft", "title": "Test", "layer": 1, "date": "2026-02-21"},
    )
    indexer.upsert_doc(
        path="docs/ideas/2026-02-21-test.md",
        frontmatter={"type": "idea", "status": "active", "title": "Test", "layer": 1, "date": "2026-02-21"},
    )
    results = queries.get_by_type("idea")
    assert results[0]["status"] == "active"  # upsert replaces

def test_search_by_title(tmp_db):
    indexer, queries = tmp_db
    indexer.upsert_doc("a.md", {"type": "research", "status": "active", "title": "SQLite performance", "layer": 1, "date": "2026-02-21"})
    indexer.upsert_doc("b.md", {"type": "research", "status": "active", "title": "VitePress setup", "layer": 1, "date": "2026-02-21"})
    results = queries.search("SQLite")
    assert len(results) == 1
    assert "SQLite" in results[0]["title"]
```

**Step 2: Run to verify failure**

```bash
cd thegent && uv run pytest tests/docs_engine/test_db_indexer.py -v
```

**Step 3: Implement**

```sql
-- thegent/docs_engine/db/schema.sql
CREATE TABLE IF NOT EXISTS docs (
    path TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    status TEXT NOT NULL,
    title TEXT NOT NULL,
    layer INTEGER NOT NULL,
    date TEXT NOT NULL,
    author TEXT DEFAULT 'agent',
    session_id TEXT DEFAULT '',
    git_commit TEXT DEFAULT '',
    tags TEXT DEFAULT '[]',  -- JSON array
    relates_to TEXT DEFAULT '[]',
    traces_to TEXT DEFAULT '[]',
    indexed_at TEXT NOT NULL,
    content_hash TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS relations (
    source_path TEXT NOT NULL,
    target_path TEXT NOT NULL,
    relation_type TEXT NOT NULL,  -- relates_to | traces_to | supersedes
    PRIMARY KEY (source_path, target_path, relation_type)
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,  -- created | promoted | committed | tagged
    doc_path TEXT,
    git_ref TEXT DEFAULT '',
    timestamp TEXT NOT NULL,
    metadata TEXT DEFAULT '{}'  -- JSON
);

CREATE INDEX IF NOT EXISTS idx_docs_type ON docs(type);
CREATE INDEX IF NOT EXISTS idx_docs_status ON docs(status);
CREATE INDEX IF NOT EXISTS idx_docs_layer ON docs(layer);
CREATE INDEX IF NOT EXISTS idx_docs_date ON docs(date);
CREATE VIRTUAL TABLE IF NOT EXISTS docs_fts USING fts5(path, title, content=docs);
```

```python
# thegent/docs_engine/db/indexer.py
import sqlite3
import orjson
import datetime
from pathlib import Path

class DocIndexer:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema(self) -> None:
        schema_sql = (Path(__file__).parent / "schema.sql").read_text()
        with self._conn() as conn:
            conn.executescript(schema_sql)

    def upsert_doc(self, path: str, frontmatter: dict) -> None:
        now = datetime.datetime.utcnow().isoformat()
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO docs (path, type, status, title, layer, date, author,
                    session_id, git_commit, tags, relates_to, traces_to, indexed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                    type=excluded.type, status=excluded.status, title=excluded.title,
                    layer=excluded.layer, date=excluded.date, indexed_at=excluded.indexed_at,
                    tags=excluded.tags, relates_to=excluded.relates_to, traces_to=excluded.traces_to
                """,
                (
                    path,
                    frontmatter.get("type", ""),
                    frontmatter.get("status", "draft"),
                    frontmatter.get("title", ""),
                    frontmatter.get("layer", 0),
                    frontmatter.get("date", ""),
                    frontmatter.get("author", "agent"),
                    frontmatter.get("session_id", ""),
                    frontmatter.get("git_commit", ""),
                    orjson.dumps(frontmatter.get("tags", [])).decode(),
                    orjson.dumps(frontmatter.get("relates_to", [])).decode(),
                    orjson.dumps(frontmatter.get("traces_to", [])).decode(),
                    now,
                ),
            )
```

```python
# thegent/docs_engine/db/queries.py
import sqlite3
import orjson
from pathlib import Path

class DocQueries:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_by_type(self, doc_type: str) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM docs WHERE type=? ORDER BY date DESC", (doc_type,)).fetchall()
        return [dict(r) for r in rows]

    def get_by_status(self, status: str) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM docs WHERE status=? ORDER BY date DESC", (status,)).fetchall()
        return [dict(r) for r in rows]

    def search(self, query: str) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM docs WHERE title LIKE ? ORDER BY date DESC",
                (f"%{query}%",)
            ).fetchall()
        return [dict(r) for r in rows]
```

**Step 4: Run tests**

```bash
cd thegent && uv run pytest tests/docs_engine/test_db_indexer.py -v
```
Expected: 3 PASSED

**Step 5: Commit**

```bash
git add thegent/docs_engine/db/
git commit -m "feat(docs-engine): add SQLite indexer with upsert, FTS table, relations/events schema"
```

---

### Task 3: Markdown frontmatter parser + DocWriter

**Files:**
- Create: `thegent/docs_engine/capture/writer.py`
- Create: `thegent/docs_engine/capture/__init__.py`
- Test: `thegent/tests/docs_engine/test_writer.py`

**Step 1: Write failing tests**

```python
# thegent/tests/docs_engine/test_writer.py
import pytest
from pathlib import Path
from docs_engine.capture.writer import DocWriter
from docs_engine.schema.base import DocType, DocStatus

def test_write_idea_creates_file(tmp_path):
    db = tmp_path / "test.db"
    docs_root = tmp_path / "docs"
    writer = DocWriter(docs_root=docs_root, db_path=db)
    path = writer.new(DocType.IDEA, title="Test idea", extra={"tags": ["test"]})
    assert path.exists()
    content = path.read_text()
    assert "type: idea" in content
    assert "Test idea" in content

def test_write_indexes_to_db(tmp_path):
    db = tmp_path / "test.db"
    docs_root = tmp_path / "docs"
    writer = DocWriter(docs_root=docs_root, db_path=db)
    writer.new(DocType.IDEA, title="Indexed idea")
    from docs_engine.db.queries import DocQueries
    results = DocQueries(db).get_by_type("idea")
    assert len(results) == 1

def test_write_rejects_invalid_schema(tmp_path):
    db = tmp_path / "test.db"
    docs_root = tmp_path / "docs"
    writer = DocWriter(docs_root=docs_root, db_path=db)
    with pytest.raises(ValueError, match="title"):
        writer.new(DocType.IDEA, title="")  # empty title not allowed
```

**Step 2: Run to verify failure**

```bash
cd thegent && uv run pytest tests/docs_engine/test_writer.py -v
```

**Step 3: Implement**

```python
# thegent/docs_engine/capture/writer.py
import datetime
from pathlib import Path
import yaml
from jinja2 import Environment, FileSystemLoader
from docs_engine.schema.base import DocFrontmatter, DocType, DocStatus, LAYER_FOR_TYPE
from docs_engine.db.indexer import DocIndexer

LAYER_FOR_TYPE: dict[DocType, int] = {
    DocType.CONVERSATION_DUMP: 0, DocType.SESSION_MEMORY: 0,
    DocType.SCRATCH: 0, DocType.AGENT_WORKLOG: 0,
    DocType.IDEA: 1, DocType.RESEARCH: 1, DocType.DEBUG_LOG: 1,
    DocType.CHANGE_PROPOSAL: 1, DocType.WORKLOG: 1,
    DocType.PRD: 2, DocType.FR: 2, DocType.ADR: 2,
    DocType.USER_JOURNEY: 2, DocType.IMPL_PLAN: 2,
    DocType.CONTEXT_DOC: 2, DocType.ARCH_DOC: 2, DocType.DESIGN_DOC: 2,
    DocType.SPRINT_PLAN: 3, DocType.CHANGE_DESIGN: 3, DocType.CHANGE_TASKS: 3,
    DocType.TEST_LOG: 3, DocType.CHANGELOG: 3, DocType.COMPLETION_REPORT: 3,
    DocType.SPRINT_RETRO: 4, DocType.EPIC_RETRO: 4,
    DocType.INCIDENT_RETRO: 4, DocType.KB_EXTRACT: 4,
}

PATH_PATTERN: dict[DocType, str] = {
    DocType.IDEA: "ideas/{date}-{slug}.md",
    DocType.RESEARCH: "research/{slug}.md",
    DocType.DEBUG_LOG: "debug/{date}-{slug}.md",
    DocType.WORKLOG: "worklogs/WL-{seq:04d}.md",
    DocType.ADR: "adr/ADR-{seq:03d}-{slug}.md",
    DocType.TEST_LOG: "test-logs/{date}-{slug}.md",
    DocType.COMPLETION_REPORT: "reports/{date}-{slug}-complete.md",
    DocType.SPRINT_RETRO: "retros/SPRINT-{seq:03d}-retro.md",
    DocType.KB_EXTRACT: "kb/{topic}/{date}-{slug}.md",
}

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

class DocWriter:
    def __init__(self, docs_root: Path, db_path: Path) -> None:
        self._docs_root = docs_root
        self._indexer = DocIndexer(db_path)
        self._indexer.init_schema()
        self._jinja = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

    def new(self, doc_type: DocType, title: str, **extra) -> Path:
        if not title or not title.strip():
            raise ValueError("title must not be empty")
        today = datetime.date.today().isoformat()
        slug = title.lower().replace(" ", "-")[:50]
        layer = LAYER_FOR_TYPE[doc_type]
        fm = DocFrontmatter(
            type=doc_type,
            status=DocStatus.DRAFT,
            date=today,
            title=title,
            layer=layer,
            **{k: v for k, v in extra.items() if k in DocFrontmatter.model_fields},
        )
        path = self._resolve_path(doc_type, slug, today)
        path.parent.mkdir(parents=True, exist_ok=True)
        content = self._render(doc_type, fm, title)
        path.write_text(content)
        self._indexer.upsert_doc(str(path.relative_to(self._docs_root)), fm.model_dump())
        return path

    def _resolve_path(self, doc_type: DocType, slug: str, date: str) -> Path:
        pattern = PATH_PATTERN.get(doc_type, f"{doc_type.value}/{date}-{{slug}}.md")
        rel = pattern.format(date=date, slug=slug, seq=1, topic=slug)
        return self._docs_root / rel

    def _render(self, doc_type: DocType, fm: DocFrontmatter, title: str) -> str:
        fm_str = yaml.dump(fm.model_dump(exclude_none=True), default_flow_style=False)
        tpl_name = f"{doc_type.value}.md.j2"
        try:
            tpl = self._jinja.get_template(tpl_name)
            body = tpl.render(title=title, fm=fm)
        except Exception:
            body = f"# {title}\n\n<!-- TODO: fill in content -->\n"
        return f"---\n{fm_str}---\n\n{body}"
```

**Step 4: Run tests**

```bash
cd thegent && uv run pytest tests/docs_engine/test_writer.py -v
```
Expected: 3 PASSED

**Step 5: Commit**

```bash
git add thegent/docs_engine/capture/ thegent/tests/docs_engine/test_writer.py
git commit -m "feat(docs-engine): add DocWriter - validates schema, renders template, writes file, indexes to SQLite"
```

---

### Task 4: Jinja2 templates for core doc types

**Files:**
- Create: `thegent/docs_engine/templates/idea.md.j2`
- Create: `thegent/docs_engine/templates/research.md.j2`
- Create: `thegent/docs_engine/templates/adr.md.j2`
- Create: `thegent/docs_engine/templates/worklog.md.j2`
- Create: `thegent/docs_engine/templates/test-log.md.j2`
- Create: `thegent/docs_engine/templates/completion-report.md.j2`
- Create: `thegent/docs_engine/templates/sprint-retro.md.j2`
- Create: `thegent/docs_engine/templates/kb-extract.md.j2`

These are static templates — no failing test required, just create them. Templates should have placeholder sections matching the metadata schema from the design doc.

```jinja2
{# idea.md.j2 #}
# {{ title }}

## Hypothesis
<!-- What is the core idea? What problem does it solve? -->

## Context
<!-- What triggered this idea? Session / conversation / observation? -->

## Open Questions
<!-- What needs to be researched or decided before this can progress? -->

## Next Step
<!-- promote to research / archive / spike -->
```

```jinja2
{# research.md.j2 #}
# {{ title }}

## Background
<!-- Problem space, motivation, prior art -->

## Findings
<!-- What was discovered? -->

## Gaps
<!-- What is still unknown? -->

## Sources
<!-- URLs, session IDs, conversation dumps referenced -->

## Next Step
<!-- promote to DesignDoc / FR / archive -->
```

```jinja2
{# adr.md.j2 #}
# {{ title }}

## Context
<!-- Problem statement and constraints -->

## Decision
<!-- What was decided -->

## Rationale
<!-- Why this decision -->

## Alternatives Considered

### Alternative 1
- **Pros:**
- **Cons:**
- **Rejected because:**

## Consequences

### Positive

### Negative

### Risks

## Implementation Notes

## References
```

```jinja2
{# worklog.md.j2 #}
# Worklog: {{ title }}

## What Changed
<!-- Brief description of the change -->

## Why
<!-- Motivation / linked FR or story -->

## Files Touched
<!-- List of files modified -->

## Next
<!-- What comes after this change -->
```

```jinja2
{# test-log.md.j2 #}
# Test Log: {{ title }}

## Run Summary
| Metric | Value |
|--------|-------|
| Total | |
| Passed | |
| Failed | |
| Coverage | |

## Failed Tests
<!-- List failing tests with error summaries -->

## Coverage Delta
<!-- +/- coverage from prior run -->

## FRs Covered
<!-- FR-XXX-NNN list -->
```

```jinja2
{# completion-report.md.j2 #}
# Completion Report: {{ title }}

## Summary
<!-- What was built / delivered -->

## Metrics
| Metric | Value |
|--------|-------|
| FRs Closed | |
| Tests Added | |
| Coverage | |
| LOC | |

## FRs Closed

## Known Issues / Follow-ups
```

```jinja2
{# sprint-retro.md.j2 #}
# Sprint Retrospective: {{ title }}

## What Worked Well

## What Didn't Work

## Action Items
| Action | Owner | Due |
|--------|-------|-----|

## Lessons → KB
<!-- Lessons that should be extracted to knowledge base -->
```

```jinja2
{# kb-extract.md.j2 #}
# KB: {{ title }}

**Topic:** {{ fm.tags | join(', ') }}
**Source docs:** {{ fm.relates_to | join(', ') }}

## Extracted Content

## Patterns / Rules Established

## Decisions Referenced

## Related KB Entries
```

**Step: Commit**

```bash
git add thegent/docs_engine/templates/
git commit -m "feat(docs-engine): add Jinja2 templates for all 8 core doc types"
```

---

## Phase 2 — Capture Pipeline

### Task 5: Session-end hook integration

**Files:**
- Create: `thegent/docs_engine/capture/session_hook.py`
- Modify: `thegent/hooks/session-end-write-dump.sh` — add call to `docs_engine.capture.session_hook`
- Test: `thegent/tests/docs_engine/test_session_hook.py`

**Step 1: Write failing tests**

```python
# thegent/tests/docs_engine/test_session_hook.py
import pytest
from pathlib import Path
from docs_engine.capture.session_hook import write_conversation_dump

def test_dump_creates_file(tmp_path):
    docs_root = tmp_path / "docs"
    db = tmp_path / "test.db"
    path = write_conversation_dump(
        docs_root=docs_root,
        db_path=db,
        session_id="test-sess-001",
        content="## Issues Addressed\n\nFixed the thing.\n",
    )
    assert path.exists()
    text = path.read_text()
    assert "session_id: test-sess-001" in text
    assert "Fixed the thing" in text

def test_dump_indexed_as_raw(tmp_path):
    docs_root = tmp_path / "docs"
    db = tmp_path / "test.db"
    write_conversation_dump(docs_root=docs_root, db_path=db, session_id="x", content="content")
    from docs_engine.db.queries import DocQueries
    results = DocQueries(db).get_by_type("conversation-dump")
    assert len(results) == 1
    assert results[0]["layer"] == 0
```

**Step 2: Run to verify failure**

```bash
cd thegent && uv run pytest tests/docs_engine/test_session_hook.py -v
```

**Step 3: Implement**

```python
# thegent/docs_engine/capture/session_hook.py
import datetime
from pathlib import Path
from docs_engine.schema.base import DocType, DocStatus, DocFrontmatter
from docs_engine.db.indexer import DocIndexer
import yaml

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
    fm_str = yaml.dump(fm.model_dump(exclude_none=True), default_flow_style=False)
    full_content = f"---\n{fm_str}---\n\n{content}"

    if path.exists():
        existing = path.read_text()
        path.write_text(existing + f"\n\n---\n\n{content}")
    else:
        path.write_text(full_content)

    indexer = DocIndexer(db_path)
    indexer.init_schema()
    indexer.upsert_doc(str(path.relative_to(docs_root)), fm.model_dump())
    return path
```

**Step 4: Modify session-end-write-dump.sh**

Find the line in `thegent/hooks/session-end-write-dump.sh` where the dump is written (likely an `echo` or `cat` redirect). Add after it:

```bash
# Index dump into docs-engine SQLite
if command -v uv &>/dev/null; then
    uv run --project "${THEGENT_ROOT}" python -c "
from docs_engine.capture.session_hook import write_conversation_dump
from pathlib import Path
# Already written by shell hook; just index it
from docs_engine.db.indexer import DocIndexer
import datetime, os
db = Path(os.environ.get('DOCS_ENGINE_DB', '${THEGENT_ROOT}/.docs-engine/index.db'))
" 2>/dev/null || true
fi
```

Note: The hook already writes the dump file. We just need to ensure the indexer picks it up via the watchdog watcher (Task 8) rather than inline here to avoid shell complexity.

**Step 5: Run tests**

```bash
cd thegent && uv run pytest tests/docs_engine/test_session_hook.py -v
```
Expected: 2 PASSED

**Step 6: Commit**

```bash
git add thegent/docs_engine/capture/session_hook.py thegent/tests/docs_engine/test_session_hook.py
git commit -m "feat(docs-engine): session-end hook writes conversation dump + indexes to SQLite"
```

---

### Task 6: Commit hook — WorklogEntry writer

**Files:**
- Create: `thegent/docs_engine/capture/commit_hook.py`
- Create: `thegent/hooks/post-commit-worklog.sh`
- Test: `thegent/tests/docs_engine/test_commit_hook.py`

**Step 1: Write failing tests**

```python
# thegent/tests/docs_engine/test_commit_hook.py
import pytest
from pathlib import Path
from docs_engine.capture.commit_hook import write_worklog_entry

def test_worklog_created(tmp_path):
    docs_root = tmp_path / "docs"
    db = tmp_path / "test.db"
    path = write_worklog_entry(
        docs_root=docs_root,
        db_path=db,
        commit_sha="abc1234",
        commit_msg="feat: add thing",
        files_changed=["src/foo.py"],
    )
    assert path.exists()
    text = path.read_text()
    assert "abc1234" in text
    assert "feat: add thing" in text

def test_worklog_sequential_numbering(tmp_path):
    docs_root = tmp_path / "docs"
    db = tmp_path / "test.db"
    p1 = write_worklog_entry(docs_root=docs_root, db_path=db, commit_sha="a", commit_msg="first", files_changed=[])
    p2 = write_worklog_entry(docs_root=docs_root, db_path=db, commit_sha="b", commit_msg="second", files_changed=[])
    assert p1.name == "WL-0001.md"
    assert p2.name == "WL-0002.md"
```

**Step 2: Run to verify failure**

```bash
cd thegent && uv run pytest tests/docs_engine/test_commit_hook.py -v
```

**Step 3: Implement**

```python
# thegent/docs_engine/capture/commit_hook.py
import datetime
import yaml
from pathlib import Path
from docs_engine.schema.base import DocFrontmatter, DocType, DocStatus
from docs_engine.db.indexer import DocIndexer

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
    fm_str = yaml.dump(fm.model_dump(exclude_none=True), default_flow_style=False)
    body = f"# WL-{seq:04d}: {commit_msg}\n\n## What Changed\n{commit_msg}\n\n## Files Touched\n"
    body += "\n".join(f"- `{f}`" for f in files_changed)
    body += "\n\n## Next\n<!-- TODO -->\n"
    path.write_text(f"---\n{fm_str}---\n\n{body}")

    indexer = DocIndexer(db_path)
    indexer.init_schema()
    indexer.upsert_doc(str(path.relative_to(docs_root)), fm.model_dump())
    return path
```

```bash
#!/usr/bin/env bash
# thegent/hooks/post-commit-worklog.sh
set -euo pipefail
THEGENT_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
DOCS_ROOT="${THEGENT_ROOT}/docs"
DB_PATH="${THEGENT_ROOT}/.docs-engine/index.db"

SHA=$(git rev-parse HEAD)
MSG=$(git log -1 --pretty=%s)
FILES=$(git diff-tree --no-commit-id -r --name-only HEAD | tr '\n' ',' | sed 's/,$//')

uv run --project "${THEGENT_ROOT}" python -c "
from docs_engine.capture.commit_hook import write_worklog_entry
from pathlib import Path
write_worklog_entry(
    docs_root=Path('${DOCS_ROOT}'),
    db_path=Path('${DB_PATH}'),
    commit_sha='${SHA}',
    commit_msg='${MSG}',
    files_changed='${FILES}'.split(',') if '${FILES}' else [],
)
print('docs-engine: worklog entry written')
"
```

Register in `thegent/hooks/hook-config.yaml`:
```yaml
post-commit:
  - post-commit-worklog.sh
```

**Step 4: Run tests**

```bash
cd thegent && uv run pytest tests/docs_engine/test_commit_hook.py -v
```
Expected: 2 PASSED

**Step 5: Commit**

```bash
git add thegent/docs_engine/capture/commit_hook.py thegent/hooks/post-commit-worklog.sh thegent/tests/docs_engine/test_commit_hook.py thegent/hooks/hook-config.yaml
git commit -m "feat(docs-engine): post-commit hook writes WorklogEntry with sequential WL-{NNN} numbering"
```

---

### Task 7: typer CLI — `docs` subcommand

**Files:**
- Create: `thegent/docs_engine/cli/commands.py`
- Create: `thegent/docs_engine/cli/__init__.py`
- Modify: `thegent/commands/` — register `docs` as subcommand in main CLI dispatch
- Test: `thegent/tests/docs_engine/test_cli.py`

**Step 1: Write failing tests**

```python
# thegent/tests/docs_engine/test_cli.py
import pytest
from typer.testing import CliRunner
from docs_engine.cli.commands import app

runner = CliRunner()

def test_new_idea_creates_file(tmp_path, monkeypatch):
    monkeypatch.setenv("DOCS_ROOT", str(tmp_path / "docs"))
    monkeypatch.setenv("DOCS_ENGINE_DB", str(tmp_path / "test.db"))
    result = runner.invoke(app, ["new", "idea", "My test idea"])
    assert result.exit_code == 0
    assert "Created" in result.output

def test_search_returns_results(tmp_path, monkeypatch):
    monkeypatch.setenv("DOCS_ROOT", str(tmp_path / "docs"))
    monkeypatch.setenv("DOCS_ENGINE_DB", str(tmp_path / "test.db"))
    runner.invoke(app, ["new", "idea", "Searchable idea"])
    result = runner.invoke(app, ["search", "Searchable"])
    assert result.exit_code == 0
    assert "Searchable" in result.output

def test_index_rebuild(tmp_path, monkeypatch):
    monkeypatch.setenv("DOCS_ROOT", str(tmp_path / "docs"))
    monkeypatch.setenv("DOCS_ENGINE_DB", str(tmp_path / "test.db"))
    result = runner.invoke(app, ["index", "rebuild"])
    assert result.exit_code == 0
```

**Step 2: Run to verify failure**

```bash
cd thegent && uv run pytest tests/docs_engine/test_cli.py -v
```

**Step 3: Implement**

```python
# thegent/docs_engine/cli/commands.py
import os
from pathlib import Path
import typer
from docs_engine.schema.base import DocType
from docs_engine.capture.writer import DocWriter
from docs_engine.db.queries import DocQueries
from docs_engine.db.indexer import DocIndexer

app = typer.Typer(name="docs", help="Agent-driven documentation system")

def _docs_root() -> Path:
    return Path(os.environ.get("DOCS_ROOT", Path.cwd() / "docs"))

def _db_path() -> Path:
    p = Path(os.environ.get("DOCS_ENGINE_DB", Path.home() / ".thegent" / "docs-engine" / "index.db"))
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

@app.command("new")
def new_doc(
    doc_type: str = typer.Argument(..., help="Doc type (idea, research, adr, worklog, etc.)"),
    title: str = typer.Argument(..., help="Document title"),
) -> None:
    """Create a new doc of the specified type."""
    try:
        dtype = DocType(doc_type)
    except ValueError:
        typer.echo(f"Unknown type: {doc_type}. Valid: {[t.value for t in DocType]}", err=True)
        raise typer.Exit(1)
    writer = DocWriter(docs_root=_docs_root(), db_path=_db_path())
    path = writer.new(dtype, title=title)
    typer.echo(f"Created: {path}")

@app.command("search")
def search_docs(query: str = typer.Argument(...)) -> None:
    """Full-text search across all indexed docs."""
    results = DocQueries(_db_path()).search(query)
    if not results:
        typer.echo("No results.")
        return
    for r in results:
        typer.echo(f"[{r['type']}] {r['title']}  ({r['path']})")

@app.command("index")
def index_cmd(action: str = typer.Argument("rebuild")) -> None:
    """Manage the SQLite doc index."""
    if action == "rebuild":
        indexer = DocIndexer(_db_path())
        indexer.init_schema()
        docs_root = _docs_root()
        count = 0
        for md_file in docs_root.rglob("*.md"):
            try:
                import re
                text = md_file.read_text()
                if text.startswith("---"):
                    fm_raw = re.split(r"^---\s*$", text, maxsplit=2, flags=re.M)[1]
                    import yaml as _yaml
                    fm = _yaml.safe_load(fm_raw)
                    if fm and "type" in fm:
                        indexer.upsert_doc(str(md_file.relative_to(docs_root)), fm)
                        count += 1
            except Exception:
                pass
        typer.echo(f"Indexed {count} documents.")
    else:
        typer.echo(f"Unknown action: {action}", err=True)
        raise typer.Exit(1)
```

**Step 4: Run tests**

```bash
cd thegent && uv run pytest tests/docs_engine/test_cli.py -v
```
Expected: 3 PASSED

**Step 5: Commit**

```bash
git add thegent/docs_engine/cli/ thegent/tests/docs_engine/test_cli.py
git commit -m "feat(docs-engine): typer CLI - docs new / search / index rebuild"
```

---

## Phase 3 — VitePress Wiring

### Task 8: Evolved sidebar generator

**Files:**
- Create: `thegent/docs_engine/sidebar/generator.py`
- Create: `thegent/docs_engine/sidebar/__init__.py`
- Modify: `thegent/docs/.vitepress/config.ts` — import sidebar-auto instead of sidebar
- Test: `thegent/tests/docs_engine/test_sidebar_generator.py`

**Step 1: Write failing tests**

```python
# thegent/tests/docs_engine/test_sidebar_generator.py
import pytest
from pathlib import Path
from docs_engine.sidebar.generator import SidebarGenerator

def test_generates_sidebar_from_dir(tmp_path):
    # Create sample doc structure
    (tmp_path / "guides").mkdir()
    (tmp_path / "guides" / "quick-start.md").write_text("# Quick Start\n")
    (tmp_path / "reference").mkdir()
    (tmp_path / "reference" / "api.md").write_text("# API\n")

    gen = SidebarGenerator(docs_root=tmp_path)
    sidebar = gen.generate()
    assert "/guides/" in sidebar or "guides" in sidebar

def test_excludes_raw_layer_dirs(tmp_path):
    (tmp_path / "scratch").mkdir()
    (tmp_path / "scratch" / "note.md").write_text("# scratch\n")
    (tmp_path / "guides").mkdir()
    (tmp_path / "guides" / "intro.md").write_text("# Intro\n")
    gen = SidebarGenerator(docs_root=tmp_path)
    sidebar = gen.generate()
    assert "scratch" not in sidebar
    assert "guides" in sidebar
```

**Step 2: Run to verify failure**

```bash
cd thegent && uv run pytest tests/docs_engine/test_sidebar_generator.py -v
```

**Step 3: Implement**

```python
# thegent/docs_engine/sidebar/generator.py
import re
from pathlib import Path

EXCLUDED_DIRS = {"scratch", "node_modules", ".vitepress", "dist", "docset", "plans", "research", "context"}
INFORMAL_DIRS = {"ideas", "debug", "worklogs", "changes"}

class SidebarGenerator:
    def __init__(self, docs_root: Path) -> None:
        self._root = docs_root

    def generate(self) -> str:
        """Generate sidebar-auto.ts content from directory structure."""
        sections = {}
        for md in sorted(self._root.rglob("*.md")):
            parts = md.relative_to(self._root).parts
            if not parts or parts[0] in EXCLUDED_DIRS:
                continue
            section = parts[0] if len(parts) > 1 else "/"
            if section not in sections:
                sections[section] = []
            title = self._extract_title(md)
            path = "/" + "/".join(md.relative_to(self._root).with_suffix("").parts)
            sections[section].append({"text": title, "link": path})

        lines = ["// AUTO-GENERATED by docs_engine.sidebar.generator — DO NOT EDIT\n"]
        lines.append("import type { DefaultTheme } from 'vitepress'\n\n")
        lines.append("export const sidebar: DefaultTheme.SidebarMulti = {\n")
        for section, items in sections.items():
            key = f"/{section}/" if section != "/" else "/"
            items_str = ",\n    ".join(
                f"{{ text: {repr(i['text'])}, link: {repr(i['link'])} }}" for i in items
            )
            lines.append(f"  {repr(key)}: [\n    {items_str}\n  ],\n")
        lines.append("}\n")
        return "".join(lines)

    def write(self, output: Path) -> None:
        output.write_text(self.generate())

    @staticmethod
    def _extract_title(path: Path) -> str:
        try:
            first_line = path.read_text().split("\n")[0]
            if first_line.startswith("#"):
                return first_line.lstrip("#").strip()
        except Exception:
            pass
        return path.stem.replace("-", " ").title()
```

**Step 4: Fix config.ts import**

In `thegent/docs/.vitepress/config.ts`, change:
```typescript
// FROM:
import { sidebar } from './sidebar'
// TO:
import { sidebar } from './sidebar-auto'
```

Add to `package.json` `docs:build` script: `docs:sidebar` runs first:
```json
"docs:build": "bun run docs:sidebar && vitepress build docs"
```

**Step 5: Run tests**

```bash
cd thegent && uv run pytest tests/docs_engine/test_sidebar_generator.py -v
```
Expected: 2 PASSED

**Step 6: Commit**

```bash
git add thegent/docs_engine/sidebar/ thegent/docs/.vitepress/config.ts thegent/package.json thegent/tests/docs_engine/test_sidebar_generator.py
git commit -m "feat(docs-engine): evolved sidebar generator + wire sidebar-auto.ts into VitePress config"
```

---

### Task 9: VitePress data loaders (TypeScript)

**Files:**
- Create: `thegent/docs/.vitepress/data/audit-log.data.ts`
- Create: `thegent/docs/.vitepress/data/kb-graph.data.ts`
- Create: `thegent/docs/.vitepress/data/sprint-board.data.ts`

These loaders call the SQLite DB via a small Python HTTP server started as part of `docs:dev` OR read from pre-exported JSON files that `docs:generate` produces.

**Simplest approach (no HTTP server):** Export loader data to JSON at build time, VitePress reads JSON.

Add to `docs_engine/cli/commands.py`:

```python
@app.command("export")
def export_for_vitepress(
    output_dir: str = typer.Option(".vitepress/data", help="Output dir for JSON data files"),
) -> None:
    """Export SQLite data as JSON for VitePress data loaders."""
    import orjson
    out = _docs_root() / output_dir
    out.mkdir(parents=True, exist_ok=True)
    q = DocQueries(_db_path())

    # audit-log: worklogs + test-logs sorted by date
    audit = q.get_by_type("worklog") + q.get_by_type("test-log") + q.get_by_type("completion-report")
    audit.sort(key=lambda x: x.get("date", ""), reverse=True)
    (out / "audit-log.json").write_bytes(orjson.dumps(audit))

    # kb-graph: all docs with relates_to relations
    all_docs = []
    for dtype in ["kb-extract", "research", "adr", "design-doc"]:
        all_docs.extend(q.get_by_type(dtype))
    (out / "kb-graph.json").write_bytes(orjson.dumps(all_docs))

    # sprint-board: sprint plans + stories
    sprints = q.get_by_type("sprint-plan")
    (out / "sprint-board.json").write_bytes(orjson.dumps(sprints))
    typer.echo(f"Exported data loaders to {out}")
```

```typescript
// thegent/docs/.vitepress/data/audit-log.data.ts
import auditLog from './audit-log.json'
export default { load: () => auditLog }
```

```typescript
// thegent/docs/.vitepress/data/kb-graph.data.ts
import kbGraph from './kb-graph.json'
export default { load: () => kbGraph }
```

```typescript
// thegent/docs/.vitepress/data/sprint-board.data.ts
import sprintBoard from './sprint-board.json'
export default { load: () => sprintBoard }
```

Add `docs:export` to `package.json`:
```json
"docs:export": "uv run python -m docs_engine.cli.commands export",
"docs:build": "bun run docs:sidebar && bun run docs:export && vitepress build docs"
```

**Commit:**

```bash
git add thegent/docs/.vitepress/data/ thegent/package.json
git commit -m "feat(docs-engine): VitePress data loaders - audit log, KB graph, sprint board exported from SQLite"
```

---

### Task 10: Vue components — AuditTimeline + KBGraph + DocStatusBadge

**Files:**
- Create: `thegent/docs/.vitepress/theme/components/AuditTimeline.vue`
- Create: `thegent/docs/.vitepress/theme/components/KBGraph.vue`
- Create: `thegent/docs/.vitepress/theme/components/DocStatusBadge.vue`
- Modify: `thegent/docs/.vitepress/theme/index.ts` — register components globally

```vue
<!-- AuditTimeline.vue -->
<script setup lang="ts">
import { useData } from 'vitepress'
import auditLog from '../data/audit-log.json'

interface AuditEntry {
  type: string; title: string; date: string; path: string; git_commit: string;
}
const entries: AuditEntry[] = auditLog
</script>
<template>
  <div class="audit-timeline">
    <div v-for="entry in entries" :key="entry.path" class="audit-entry">
      <span class="audit-date">{{ entry.date }}</span>
      <span class="audit-type">{{ entry.type }}</span>
      <a :href="'/' + entry.path.replace('.md', '')">{{ entry.title }}</a>
      <code v-if="entry.git_commit" class="audit-sha">{{ entry.git_commit.slice(0, 7) }}</code>
    </div>
  </div>
</template>
<style scoped>
.audit-timeline { display: flex; flex-direction: column; gap: 0.5rem; }
.audit-entry { display: flex; gap: 1rem; align-items: baseline; }
.audit-date { color: var(--vp-c-text-2); font-size: 0.8em; min-width: 6em; }
.audit-type { font-size: 0.75em; background: var(--vp-c-bg-soft); padding: 0.1em 0.4em; border-radius: 3px; }
.audit-sha { font-size: 0.7em; color: var(--vp-c-text-3); }
</style>
```

```vue
<!-- DocStatusBadge.vue -->
<script setup lang="ts">
const props = defineProps<{ status: string }>()
const colors: Record<string, string> = {
  draft: '#888', active: '#3b82f6', staging: '#f59e0b',
  published: '#10b981', archived: '#6b7280', deprecated: '#ef4444',
}
</script>
<template>
  <span class="status-badge" :style="{ background: colors[status] ?? '#888' }">
    {{ status }}
  </span>
</template>
<style scoped>
.status-badge { font-size: 0.7em; padding: 0.15em 0.5em; border-radius: 999px; color: white; font-weight: 600; }
</style>
```

```vue
<!-- KBGraph.vue — lightweight knowledge graph using SVG -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import kbData from '../data/kb-graph.json'

interface KBNode { path: string; title: string; type: string; relates_to: string[] }
const nodes: KBNode[] = kbData

const svgRef = ref<SVGElement | null>(null)
// Simple force-directed placeholder — replace with vis.js/d3 for production
const nodePositions = nodes.map((n, i) => ({
  ...n,
  x: 100 + (i % 5) * 160,
  y: 100 + Math.floor(i / 5) * 120,
}))
</script>
<template>
  <div class="kb-graph-container">
    <svg ref="svgRef" width="100%" height="400" viewBox="0 0 900 400">
      <circle v-for="n in nodePositions" :key="n.path"
        :cx="n.x" :cy="n.y" r="20"
        fill="var(--vp-c-brand)" opacity="0.8" />
      <text v-for="n in nodePositions" :key="n.path + '-label'"
        :x="n.x" :y="n.y + 35" text-anchor="middle" font-size="11"
        fill="var(--vp-c-text-1)">{{ n.title.slice(0, 20) }}</text>
    </svg>
    <p class="kb-graph-note">{{ nodes.length }} knowledge nodes indexed</p>
  </div>
</template>
<style scoped>
.kb-graph-container { border: 1px solid var(--vp-c-divider); border-radius: 8px; padding: 1rem; }
.kb-graph-note { font-size: 0.75em; color: var(--vp-c-text-3); margin-top: 0.5rem; }
</style>
```

Register globally in `thegent/docs/.vitepress/theme/index.ts`:
```typescript
import AuditTimeline from './components/AuditTimeline.vue'
import KBGraph from './components/KBGraph.vue'
import DocStatusBadge from './components/DocStatusBadge.vue'

// In enhanceApp:
app.component('AuditTimeline', AuditTimeline)
app.component('KBGraph', KBGraph)
app.component('DocStatusBadge', DocStatusBadge)
```

**Commit:**

```bash
git add thegent/docs/.vitepress/theme/components/
git commit -m "feat(docs-engine): AuditTimeline, KBGraph, DocStatusBadge Vue components for VitePress"
```

---

## Phase 4 — Git Integration

### Task 11: git-cliff integration for Changelog

**Files:**
- Create: `thegent/docs_engine/git/cliff.py`
- Create: `thegent/cliff.toml` (git-cliff config)
- Create: `thegent/hooks/post-tag-changelog.sh`
- Test: `thegent/tests/docs_engine/test_cliff.py`

**Step 1: Write failing test**

```python
# thegent/tests/docs_engine/test_cliff.py
import pytest
import subprocess
from docs_engine.git.cliff import run_cliff

def test_cliff_returns_changelog_string(tmp_path, monkeypatch):
    # Mock subprocess for unit test
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw:
        type("R", (), {"returncode": 0, "stdout": "## v1.0.0\n- feat: add thing\n"})()
    )
    result = run_cliff(repo_path=tmp_path)
    assert "feat: add thing" in result

def test_cliff_raises_on_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw:
        type("R", (), {"returncode": 1, "stdout": "", "stderr": "error"})()
    )
    with pytest.raises(RuntimeError, match="git-cliff failed"):
        run_cliff(repo_path=tmp_path)
```

**Step 2: Run to verify failure**

```bash
cd thegent && uv run pytest tests/docs_engine/test_cliff.py -v
```

**Step 3: Implement**

```python
# thegent/docs_engine/git/cliff.py
import subprocess
from pathlib import Path

def run_cliff(repo_path: Path, tag: str = "") -> str:
    """Run git-cliff and return changelog content. Raises RuntimeError on failure."""
    cmd = ["git-cliff", "--output", "-"]
    if tag:
        cmd += ["--tag", tag]
    result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"git-cliff failed: {result.stderr}")
    return result.stdout

def write_changelog(repo_path: Path, changelog_path: Path, tag: str = "") -> None:
    """Run git-cliff and write CHANGELOG.md."""
    content = run_cliff(repo_path, tag)
    changelog_path.write_text(content)
```

```toml
# thegent/cliff.toml
[changelog]
header = "# Changelog\n\n"
body = """
{% for group, commits in commits | group_by(attribute="group") %}
### {{ group | upper_first }}
{% for commit in commits %}
- {{ commit.message | upper_first }}{% endfor %}
{% endfor %}
"""
trim = true

[git]
conventional_commits = true
commit_parsers = [
  { message = "^feat", group = "Features" },
  { message = "^fix", group = "Bug Fixes" },
  { message = "^refactor", group = "Refactors" },
  { message = "^docs", group = "Documentation" },
  { message = "^test", group = "Tests" },
  { message = "^chore", group = "Chores" },
]
```

```bash
#!/usr/bin/env bash
# thegent/hooks/post-tag-changelog.sh
set -euo pipefail
THEGENT_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
TAG=$(git describe --tags --abbrev=0)
uv run --project "${THEGENT_ROOT}" python -c "
from docs_engine.git.cliff import write_changelog
from pathlib import Path
write_changelog(Path('${THEGENT_ROOT}'), Path('${THEGENT_ROOT}/CHANGELOG.md'), tag='${TAG}')
print('docs-engine: CHANGELOG.md updated for tag ${TAG}')
"
```

Register in `hook-config.yaml`:
```yaml
post-tag:
  - post-tag-changelog.sh
```

**Step 4: Run tests**

```bash
cd thegent && uv run pytest tests/docs_engine/test_cliff.py -v
```
Expected: 2 PASSED

**Step 5: Commit**

```bash
git add thegent/docs_engine/git/cliff.py thegent/cliff.toml thegent/hooks/post-tag-changelog.sh thegent/tests/docs_engine/test_cliff.py thegent/hooks/hook-config.yaml
git commit -m "feat(docs-engine): git-cliff integration - post-tag hook generates CHANGELOG.md from conventional commits"
```

---

## Phase 5 — Semantic Indexer

### Task 12: Nightly knowledge extractor

**Files:**
- Create: `thegent/docs_engine/semantic/indexer.py`
- Create: `thegent/docs_engine/semantic/__init__.py`
- Test: `thegent/tests/docs_engine/test_semantic_indexer.py`

**Step 1: Write failing tests**

```python
# thegent/tests/docs_engine/test_semantic_indexer.py
import pytest
from pathlib import Path
from docs_engine.semantic.indexer import SemanticIndexer

SAMPLE_DUMP = """
## Issues Addressed
Fixed the concurrency bug in execution.py.

## Research Findings
Using rustworkx instead of networkx gives 10x speedup for DAG operations.

## Decisions Made
ADR-023: Use rustworkx for all DAG processing in thegent.

## Open Questions
Should we also migrate trace to rustworkx?
"""

def test_extracts_decisions(tmp_path):
    docs_root = tmp_path / "docs"
    db = tmp_path / "test.db"
    dump = docs_root / "research" / "CONVERSATION_DUMP_2026-02-21.md"
    dump.parent.mkdir(parents=True)
    dump.write_text(f"---\ntype: conversation-dump\nstatus: draft\ntitle: Test\nlayer: 0\ndate: 2026-02-21\n---\n\n{SAMPLE_DUMP}")

    indexer = SemanticIndexer(docs_root=docs_root, db_path=db)
    extracts = indexer.extract_from_file(dump)
    assert any("rustworkx" in e["content"] for e in extracts)

def test_extract_writes_kb_file(tmp_path):
    docs_root = tmp_path / "docs"
    db = tmp_path / "test.db"
    dump = docs_root / "research" / "CONVERSATION_DUMP_2026-02-21.md"
    dump.parent.mkdir(parents=True)
    dump.write_text(f"---\ntype: conversation-dump\nstatus: draft\ntitle: Test\nlayer: 0\ndate: 2026-02-21\n---\n\n{SAMPLE_DUMP}")

    indexer = SemanticIndexer(docs_root=docs_root, db_path=db)
    written = indexer.run_on_file(dump)
    assert len(written) > 0
    assert written[0].exists()
```

**Step 2: Run to verify failure**

```bash
cd thegent && uv run pytest tests/docs_engine/test_semantic_indexer.py -v
```

**Step 3: Implement** (regex-based extraction; LLM-assisted extraction is a future enhancement)

```python
# thegent/docs_engine/semantic/indexer.py
import re
import datetime
import yaml
from pathlib import Path
from docs_engine.capture.writer import DocWriter
from docs_engine.schema.base import DocType

SECTION_PATTERNS = {
    "decisions": re.compile(r"(?:## (?:Decisions?|Decision[s]? Made|ADR)\n)(.*?)(?=\n## |\Z)", re.S | re.I),
    "findings": re.compile(r"(?:## (?:Research Findings?|Findings?|Key Findings)\n)(.*?)(?=\n## |\Z)", re.S | re.I),
    "lessons": re.compile(r"(?:## (?:Lessons?|What (?:Worked|Didn.t))\n)(.*?)(?=\n## |\Z)", re.S | re.I),
    "patterns": re.compile(r"(?:## (?:Patterns?|Best Practices?|Rules)\n)(.*?)(?=\n## |\Z)", re.S | re.I),
}

class SemanticIndexer:
    def __init__(self, docs_root: Path, db_path: Path) -> None:
        self._docs_root = docs_root
        self._db_path = db_path
        self._writer = DocWriter(docs_root=docs_root, db_path=db_path)

    def extract_from_file(self, path: Path) -> list[dict]:
        content = path.read_text()
        extracts = []
        for category, pattern in SECTION_PATTERNS.items():
            for match in pattern.finditer(content):
                text = match.group(1).strip()
                if len(text) > 20:
                    extracts.append({"category": category, "content": text, "source": str(path)})
        return extracts

    def run_on_file(self, path: Path) -> list[Path]:
        extracts = self.extract_from_file(path)
        written = []
        for extract in extracts:
            title = f"{extract['category'].title()} from {path.stem}"
            kb_path = self._writer.new(
                DocType.KB_EXTRACT,
                title=title,
                tags=[extract["category"]],
                relates_to=[str(path.relative_to(self._docs_root))],
            )
            body = kb_path.read_text()
            kb_path.write_text(body + f"\n{extract['content']}\n")
            written.append(kb_path)
        return written

    def run_nightly(self) -> int:
        """Process all raw Layer 0 docs not yet indexed. Returns count of extracts written."""
        raw_dirs = [self._docs_root / "research"]
        count = 0
        for d in raw_dirs:
            if not d.exists():
                continue
            for md in d.glob("CONVERSATION_DUMP_*.md"):
                written = self.run_on_file(md)
                count += len(written)
        return count
```

**Step 4: Add `docs semantic` CLI command**

In `docs_engine/cli/commands.py` add:
```python
@app.command("semantic")
def semantic_cmd(action: str = typer.Argument("run")) -> None:
    """Run semantic knowledge extractor."""
    from docs_engine.semantic.indexer import SemanticIndexer
    if action == "run":
        indexer = SemanticIndexer(docs_root=_docs_root(), db_path=_db_path())
        count = indexer.run_nightly()
        typer.echo(f"Semantic indexer: {count} KB extracts written.")
```

**Step 5: Run tests**

```bash
cd thegent && uv run pytest tests/docs_engine/test_semantic_indexer.py -v
```
Expected: 2 PASSED

**Step 6: Commit**

```bash
git add thegent/docs_engine/semantic/ thegent/tests/docs_engine/test_semantic_indexer.py
git commit -m "feat(docs-engine): nightly semantic indexer - extracts decisions/findings/lessons from ConversationDumps → KB"
```

---

## Phase 6 — MCP Tools

### Task 13: FastMCP registration of thegent_doc_* tools

**Files:**
- Create: `thegent/docs_engine/mcp/tools.py`
- Create: `thegent/docs_engine/mcp/__init__.py`
- Modify: `thegent/mcp/` — import and register doc tools with existing FastMCP server
- Test: `thegent/tests/docs_engine/test_mcp_tools.py`

**Step 1: Write failing tests**

```python
# thegent/tests/docs_engine/test_mcp_tools.py
import pytest
from docs_engine.mcp.tools import DocMCPTools
from pathlib import Path

def test_doc_new_returns_path(tmp_path):
    tools = DocMCPTools(docs_root=tmp_path / "docs", db_path=tmp_path / "test.db")
    result = tools.doc_new(doc_type="idea", title="MCP test idea")
    assert "Created" in result or ".md" in result

def test_doc_search_returns_results(tmp_path):
    tools = DocMCPTools(docs_root=tmp_path / "docs", db_path=tmp_path / "test.db")
    tools.doc_new("idea", "Searchable via MCP")
    result = tools.doc_search("Searchable")
    assert "Searchable" in result

def test_doc_get_returns_content(tmp_path):
    tools = DocMCPTools(docs_root=tmp_path / "docs", db_path=tmp_path / "test.db")
    path = tools.doc_new("idea", "Gettable idea")
    # Extract path from result string
    doc_path = path.split("Created: ")[-1].strip()
    result = tools.doc_get(doc_path)
    assert "Gettable idea" in result
```

**Step 2: Run to verify failure**

```bash
cd thegent && uv run pytest tests/docs_engine/test_mcp_tools.py -v
```

**Step 3: Implement**

```python
# thegent/docs_engine/mcp/tools.py
import os
from pathlib import Path
from docs_engine.schema.base import DocType
from docs_engine.capture.writer import DocWriter
from docs_engine.db.queries import DocQueries
import orjson

class DocMCPTools:
    """Wraps docs_engine for FastMCP registration."""

    def __init__(self, docs_root: Path | None = None, db_path: Path | None = None) -> None:
        self._docs_root = docs_root or Path(os.environ.get("DOCS_ROOT", "docs"))
        self._db_path = db_path or Path(os.environ.get("DOCS_ENGINE_DB", Path.home() / ".thegent/docs-engine/index.db"))
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._writer = DocWriter(self._docs_root, self._db_path)
        self._queries = DocQueries(self._db_path)

    def doc_new(self, doc_type: str, title: str, **kwargs) -> str:
        dtype = DocType(doc_type)
        path = self._writer.new(dtype, title=title, **kwargs)
        return f"Created: {path}"

    def doc_search(self, query: str) -> str:
        results = self._queries.search(query)
        if not results:
            return "No results found."
        lines = [f"[{r['type']}] {r['title']} — {r['path']}" for r in results[:10]]
        return "\n".join(lines)

    def doc_get(self, path: str) -> str:
        full = self._docs_root / path
        if not full.exists():
            raise FileNotFoundError(f"Doc not found: {path}")
        return full.read_text()

    def doc_status(self, path: str) -> str:
        rows = self._queries.search(path)
        if not rows:
            return f"Not indexed: {path}"
        r = rows[0]
        return f"type={r['type']} status={r['status']} layer={r['layer']} date={r['date']}"

    def doc_relate(self, source: str, target: str, relation_type: str = "relates_to") -> str:
        from docs_engine.db.indexer import DocIndexer
        indexer = DocIndexer(self._db_path)
        indexer.init_schema()
        import sqlite3
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO relations(source_path, target_path, relation_type) VALUES(?,?,?)",
                (source, target, relation_type),
            )
        return f"Related: {source} --{relation_type}--> {target}"

    def doc_kb_query(self, topic: str) -> str:
        results = self._queries.get_by_type("kb-extract")
        filtered = [r for r in results if topic.lower() in r["title"].lower()]
        if not filtered:
            return f"No KB entries for topic: {topic}"
        return "\n".join(f"- {r['title']} ({r['path']})" for r in filtered[:10])

    def doc_sprint_board(self, sprint_id: str) -> str:
        results = self._queries.get_by_type("sprint-plan")
        for r in results:
            if sprint_id in r["path"]:
                return self.doc_get(r["path"])
        return f"Sprint not found: {sprint_id}"
```

**Register with FastMCP** in `thegent/mcp/` (find existing FastMCP server registration file):

```python
# In thegent/mcp/server.py or equivalent — add after existing tool registrations:
from docs_engine.mcp.tools import DocMCPTools

_doc_tools = DocMCPTools()

@mcp.tool()
def thegent_doc_new(doc_type: str, title: str) -> str:
    """Create a new doc of the specified type."""
    return _doc_tools.doc_new(doc_type, title)

@mcp.tool()
def thegent_doc_search(query: str) -> str:
    """Search all indexed docs by title/content."""
    return _doc_tools.doc_search(query)

@mcp.tool()
def thegent_doc_get(path: str) -> str:
    """Get doc content by path."""
    return _doc_tools.doc_get(path)

@mcp.tool()
def thegent_doc_status(path: str) -> str:
    """Get doc lifecycle status."""
    return _doc_tools.doc_status(path)

@mcp.tool()
def thegent_doc_relate(source: str, target: str, relation_type: str = "relates_to") -> str:
    """Add bidirectional link between two docs."""
    return _doc_tools.doc_relate(source, target, relation_type)

@mcp.tool()
def thegent_doc_kb_query(topic: str) -> str:
    """Query the knowledge base by topic."""
    return _doc_tools.doc_kb_query(topic)

@mcp.tool()
def thegent_doc_sprint_board(sprint_id: str) -> str:
    """Get sprint board for a given sprint ID."""
    return _doc_tools.doc_sprint_board(sprint_id)
```

**Step 4: Run tests**

```bash
cd thegent && uv run pytest tests/docs_engine/test_mcp_tools.py -v
```
Expected: 3 PASSED

**Step 5: Commit**

```bash
git add thegent/docs_engine/mcp/ thegent/tests/docs_engine/test_mcp_tools.py
git commit -m "feat(docs-engine): FastMCP registration of 7 thegent_doc_* tools (new/search/get/status/relate/kb-query/sprint-board)"
```

---

## Phase 7 — Federation Hub

### Task 14: Replace MkDocs with VitePress federation hub

**Files:**
- Create: `kush/docs-hub/.vitepress/config.ts`
- Create: `kush/docs-hub/index.md`
- Create: `kush/docs-hub/package.json`
- Delete: `kush/mkdocs.yml` (after verifying hub is live)

**Step 1: Create hub package**

```json
// kush/docs-hub/package.json
{
  "name": "kush-docs-hub",
  "private": true,
  "scripts": {
    "dev": "vitepress dev .",
    "build": "vitepress build .",
    "preview": "vitepress preview ."
  },
  "devDependencies": {
    "vitepress": "^1.6.0"
  }
}
```

```typescript
// kush/docs-hub/.vitepress/config.ts
import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'kush — Agent Dev Hub',
  description: 'Cross-project documentation hub',
  base: '/',
  ignoreDeadLinks: true,
  themeConfig: {
    nav: [
      { text: 'thegent', link: '/thegent/' },
      { text: 'trace', link: '/trace/' },
      { text: 'Research', link: '/research/' },
      { text: 'Specs', link: '/specs/' },
    ],
    sidebar: {
      '/thegent/': [
        { text: 'thegent Docs', link: '/thegent/' },
        { text: 'Architecture', link: '/thegent/ARCHITECTURE_LAYERS' },
        { text: 'Guides', link: '/thegent/guides/' },
      ],
      '/trace/': [
        { text: 'trace Docs', link: '/trace/' },
        { text: 'Reference', link: '/trace/reference/' },
      ],
    },
  },
})
```

```markdown
<!-- kush/docs-hub/index.md -->
---
layout: home
hero:
  name: kush Dev Hub
  text: Agent-Driven Development
  tagline: thegent + trace + workspace documentation
  actions:
    - theme: brand
      text: thegent Docs
      link: /thegent/
    - theme: alt
      text: trace Docs
      link: /trace/
features:
  - title: Knowledge Base
    details: Nightly-extracted decisions, findings, and lessons
  - title: Audit Log
    details: Append-only worklog from every commit
  - title: Specs
    details: PRD, FR, ADR, User Journeys across all projects
---
```

**Step 2: Install and verify**

```bash
cd kush/docs-hub && bun install && bun run dev
```

**Step 3: Commit + deprecate MkDocs**

```bash
git add kush/docs-hub/
git commit -m "feat(federation): VitePress hub replaces MkDocs as workspace documentation aggregator"
# After verifying hub works:
git rm kush/mkdocs.yml
git commit -m "chore: remove mkdocs.yml - replaced by VitePress federation hub"
```

---

## Final Validation

### Task 15: Run full quality gate + coverage check

```bash
cd thegent && task quality
```

Expected: ruff PASS, pyright PASS, tach PASS, all tests PASS, coverage ≥ 85% on new modules.

```bash
uv run pytest tests/docs_engine/ -v --cov=docs_engine --cov-report=term-missing
```

Expected: All tests green, no gaps in schema.py, indexer.py, writer.py, cliff.py core paths.

```bash
git tag -a v0.1.0-docs-engine -m "feat: agent-driven documentation system v0.1"
# Triggers post-tag-changelog.sh → CHANGELOG.md updated
```

---

## Summary

| Phase | Tasks | New Files | LOC est. |
|-------|-------|-----------|---------|
| P1 Foundation | 4 | schema/, db/, templates/, writer.py | ~450 |
| P2 Capture | 3 | session_hook, commit_hook, CLI | ~250 |
| P3 VitePress | 3 | sidebar gen, data loaders, Vue components | ~300 |
| P4 Git | 1 | cliff.py, hooks | ~80 |
| P5 Semantic | 1 | semantic/indexer.py | ~120 |
| P6 MCP | 1 | mcp/tools.py + FastMCP reg | ~120 |
| P7 Federation | 1 | docs-hub/ | ~80 |
| **Total** | **14** | **~40 files** | **~1,400** |

All tasks follow TDD. Max function 40 lines. Max complexity 10. Zero silent failures.

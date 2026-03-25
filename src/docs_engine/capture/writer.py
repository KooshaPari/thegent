"""DocWriter — validate schema, render template, write file, index to SQLite.

# @trace FR-DOCS-003
"""

from __future__ import annotations

import datetime
import re
from pathlib import Path

from thegent.infra.fast_yaml_parser import yaml_dump

from docs_engine.db.indexer import DocIndexer
from docs_engine.schema.base import DocFrontmatter, DocStatus, DocType

LAYER_FOR_TYPE: dict[DocType, int] = {
    DocType.CONVERSATION_DUMP: 0,
    DocType.SESSION_MEMORY: 0,
    DocType.SCRATCH: 0,
    DocType.AGENT_WORKLOG: 0,
    DocType.IDEA: 1,
    DocType.RESEARCH: 1,
    DocType.DEBUG_LOG: 1,
    DocType.CHANGE_PROPOSAL: 1,
    DocType.WORKLOG: 1,
    DocType.PRD: 2,
    DocType.FR: 2,
    DocType.ADR: 2,
    DocType.USER_JOURNEY: 2,
    DocType.IMPL_PLAN: 2,
    DocType.CONTEXT_DOC: 2,
    DocType.ARCH_DOC: 2,
    DocType.DESIGN_DOC: 2,
    DocType.SPRINT_PLAN: 3,
    DocType.CHANGE_DESIGN: 3,
    DocType.CHANGE_TASKS: 3,
    DocType.TEST_LOG: 3,
    DocType.CHANGELOG: 3,
    DocType.COMPLETION_REPORT: 3,
    DocType.SPRINT_RETRO: 4,
    DocType.EPIC_RETRO: 4,
    DocType.INCIDENT_RETRO: 4,
    DocType.KB_EXTRACT: 4,
}

_PATH_PATTERNS: dict[DocType, str] = {
    DocType.CONVERSATION_DUMP: "research/CONVERSATION_DUMP_{date}.md",
    DocType.SCRATCH: "scratch/{date}-{slug}.md",
    DocType.IDEA: "ideas/{date}-{slug}.md",
    DocType.RESEARCH: "research/{slug}.md",
    DocType.DEBUG_LOG: "debug/{date}-{slug}.md",
    DocType.CHANGE_PROPOSAL: "changes/{slug}/proposal.md",
    DocType.WORKLOG: "worklogs/WL-{seq:04d}.md",
    DocType.PRD: "PRD.md",
    DocType.FR: "FUNCTIONAL_REQUIREMENTS.md",
    DocType.ADR: "adr/ADR-{seq:03d}-{slug}.md",
    DocType.USER_JOURNEY: "USER_JOURNEYS.md",
    DocType.IMPL_PLAN: "PLAN.md",
    DocType.CONTEXT_DOC: "context/{slug}.md",
    DocType.ARCH_DOC: "reference/ARCHITECTURE_{slug}.md",
    DocType.DESIGN_DOC: "plans/{date}-{slug}-design.md",
    DocType.SPRINT_PLAN: "sprints/SPRINT-{seq:03d}.md",
    DocType.CHANGE_DESIGN: "changes/{slug}/design.md",
    DocType.CHANGE_TASKS: "changes/{slug}/tasks.md",
    DocType.TEST_LOG: "test-logs/{date}-{slug}.md",
    DocType.COMPLETION_REPORT: "reports/{date}-{slug}-complete.md",
    DocType.SPRINT_RETRO: "retros/SPRINT-{seq:03d}-retro.md",
    DocType.EPIC_RETRO: "retros/EPIC-{slug}-retro.md",
    DocType.INCIDENT_RETRO: "retros/INCIDENT-{slug}-retro.md",
    DocType.KB_EXTRACT: "kb/{date}-{slug}.md",
}

_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def _slugify(text: str) -> str:
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    return slug[:50]


def _render_frontmatter(fm: DocFrontmatter) -> str:
    fm_dict = fm.model_dump(mode="json")
    fm_dict = {k: v for k, v in fm_dict.items() if v not in ("", [], None)}
    rendered = yaml_dump(fm_dict, default_flow_style=False, allow_unicode=True)
    if rendered is None:
        raise ValueError("yaml_dump returned None without a stream target")
    return rendered


def _render_body(fm: DocFrontmatter, title: str) -> str:
    tpl_path = _TEMPLATES_DIR / f"{fm.type.value}.md.j2"
    from jinja2 import Environment, FileSystemLoader

    env = Environment(loader=FileSystemLoader(str(_TEMPLATES_DIR)), autoescape=False)  # noqa: S701 -- templates are agent-authored markdown, not user-facing HTML
    if tpl_path.exists():
        return env.get_template(f"{fm.type.value}.md.j2").render(title=title, fm=fm)

    available = sorted({p.name for p in _TEMPLATES_DIR.glob("*.md.j2")})
    raise ValueError(f"Missing template for doc type {fm.type.value!r}; available templates: {', '.join(available)}")


class DocWriter:
    def __init__(self, docs_root: Path, db_path: Path) -> None:
        self._docs_root = docs_root
        self._indexer = DocIndexer(db_path)
        self._indexer.init_schema()

    def new(self, doc_type: DocType, title: str, **extra: object) -> Path:
        if not title or not title.strip():
            raise ValueError("title must not be empty")

        today = datetime.date.today().isoformat()
        slug = _slugify(title)
        layer = LAYER_FOR_TYPE[doc_type]

        fm_data: dict[str, object] = {
            "type": doc_type,
            "status": DocStatus.DRAFT,
            "date": today,
            "title": title.strip(),
            "layer": layer,
        }
        valid_fields = set(DocFrontmatter.model_fields)
        fm_data.update({k: v for k, v in extra.items() if k in valid_fields})

        fm = DocFrontmatter(**fm_data)  # type: ignore[arg-type]
        path = self._resolve_path(doc_type, slug, today)
        path.parent.mkdir(parents=True, exist_ok=True)
        fm_str = _render_frontmatter(fm)
        body = _render_body(fm, title.strip())
        path.write_text(f"---\n{fm_str}---\n\n{body}")
        self._indexer.upsert_doc(str(path.relative_to(self._docs_root)), fm.model_dump())
        return path

    def _resolve_path(self, doc_type: DocType, slug: str, date: str) -> Path:
        pattern = _PATH_PATTERNS.get(doc_type, "{doc_type}/{date}-{slug}.md")
        seq = self._next_seq(doc_type)
        rel = pattern.format(date=date, slug=slug, seq=seq, doc_type=doc_type.value)
        return self._docs_root / rel

    def _next_seq(self, doc_type: DocType) -> int:
        pattern = _PATH_PATTERNS.get(doc_type, "")
        if "{seq" not in pattern:
            return 1
        subdir = pattern.split("/")[0]
        subdir_path = self._docs_root / subdir
        existing = list(subdir_path.glob("*.md")) if subdir_path.exists() else []
        return len(existing) + 1

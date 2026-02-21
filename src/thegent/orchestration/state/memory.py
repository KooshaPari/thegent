import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, StrEnum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class MemoryCategory(StrEnum):
    NOTE = "note"
    LESSON_POSITIVE = "lesson_positive"
    LESSON_NEGATIVE = "lesson_negative"
    ISSUE = "issue"
    QUESTION = "question"
    FRICTION = "friction"
    USER_PROMPT = "user_prompt"


class FrictionScope(StrEnum):
    AGENT = "agent"  # General LLM/Agent behavior issues
    EPHEMERAL = "ephemeral"  # Environmental/transient issues (e.g. network)
    PROJECT = "project"  # Issues specific to this codebase
    PROCESS = "process"  # Workflow/governance friction


@dataclass
class MemoryFragment:
    content: str
    category: MemoryCategory
    source_agent: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    scope: FrictionScope | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: f"{int(time.time() * 1000):x}")


class MemorySystem:
    """MTSP-17: Dual Issue & Memory Collection System.
    Append-only audit log for agent observations, synthesized into formal docs.
    """

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.memory_dir = project_root / ".thegent" / "memory"
        self.audit_log = self.memory_dir / "audit.jsonl"
        self.memory_dir.mkdir(parents=True, exist_ok=True)

    def record(
        self,
        content: str,
        category: MemoryCategory,
        agent_id: str,
        scope: FrictionScope | None = None,
        metadata: dict[str, Any | None] | None = None,
    ) -> MemoryFragment:
        fragment = MemoryFragment(
            content=content, category=category, source_agent=agent_id, scope=scope, metadata=metadata or {}
        )

        with open(self.audit_log, "a") as f:
            f.write(
                json.dumps(
                    {
                        "id": fragment.id,
                        "ts": fragment.timestamp,
                        "cat": fragment.category,
                        "agent": fragment.source_agent,
                        "scope": fragment.scope,
                        "msg": fragment.content,
                        "meta": fragment.metadata,
                    }
                )
                + "\n"
            )

        return fragment

    def get_recent(self, limit: int = 50, category: MemoryCategory | None = None) -> list[MemoryFragment]:
        fragments = []
        if not self.audit_log.exists():
            return []

        with open(self.audit_log) as f:
            lines = f.readlines()

        for line in reversed(lines):
            try:
                data = json.loads(line)
                if category and data["cat"] != category:
                    continue
                fragments.append(
                    MemoryFragment(
                        id=data["id"],
                        timestamp=data["ts"],
                        category=MemoryCategory(data["cat"]),
                        source_agent=data["agent"],
                        scope=FrictionScope(data["scope"]) if data.get("scope") else None,
                        content=data["msg"],
                        metadata=data.get("meta", {}),
                    )
                )
                if len(fragments) >= limit:
                    break
            except Exception as e:
                logger.error(f"Error parsing memory line: {e}")

        return fragments

    def synthesize_to_markdown(self) -> str:
        """Helper to generate a summary for an agent to incorporate."""
        fragments = self.get_recent(limit=200)
        if not fragments:
            return "No recent memory fragments to synthesize."

        sections = {cat: [] for cat in MemoryCategory}

        for f in fragments:
            scope_prefix = f"[{f.scope.upper()}] " if f.scope else ""
            sections[f.category].append(f"- {scope_prefix}{f.content} (Agent: {f.source_agent})")

        md = [f"# Memory Synthesis: {datetime.now().strftime('%Y-%m-%d %H:%M')}"]

        title_map = {
            MemoryCategory.NOTE: "General Notes",
            MemoryCategory.LESSON_POSITIVE: "Positive Rules (Good Practices)",
            MemoryCategory.LESSON_NEGATIVE: "Negative Rules (Lessons Learned)",
            MemoryCategory.ISSUE: "Issue Board",
            MemoryCategory.QUESTION: "Question Board",
            MemoryCategory.FRICTION: "Friction Board",
            MemoryCategory.USER_PROMPT: "User Prompt History (Session Audit)",
        }

        for cat, lines in sections.items():
            if lines:
                md.append(f"\n## {title_map[cat]}")
                md.extend(lines)

        return "\n".join(md)

"""CLAUDE.md: always write conversation dumps to docs/."""

import json
import logging
import re
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ConversationDumper:
    """Always write conversation dumps to docs/."""

    def __init__(self, docs_dir: Path = Path("docs/dumps")) -> None:
        self.docs_dir = docs_dir
        self.docs_dir.mkdir(parents=True, exist_ok=True)

    def dump_conversation(
        self,
        conversation_id: str,
        content: str,
        *,
        prompt: str | None = None,
        synthesis: str | None = None,
        category: str = "execution",
        tags: list[str] | None = None,
        metadata: dict | None = None,
    ) -> Path:
        """Dump conversation content to a file.

        Args:
            conversation_id: Unique identifier for the conversation
            content: Conversation content to dump
            prompt: Original prompt text
            synthesis: Agent synthesis/summary text
            category: run category (execution/research/planning)
            tags: optional tags
            metadata: optional structured metadata

        Returns:
            Path to the created dump file
        """
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = f"conversation-{conversation_id}-{timestamp}.md"
        target_dir = self.docs_dir / category
        target_dir.mkdir(parents=True, exist_ok=True)
        dump_path = target_dir / filename

        try:
            if tags is None:
                tags = self._infer_tags(content)
            lines = [
                "---",
                f"conversation_id: {conversation_id}",
                f"timestamp: {timestamp}",
                f"category: {category}",
            ]
            if tags:
                lines.append(f"tags: {json.dumps(tags)}")
            if metadata:
                lines.append(f"metadata: {json.dumps(metadata, ensure_ascii=False)}")
            lines.extend(["---", "", "# Prompt", "", (prompt or ""), "", "# Synthesis", "", (synthesis or content), "", "# Full Output", "", content, ""])
            dump_path.write_text("\n".join(lines), encoding="utf-8")
            logger.info(f"Conversation dump written to {dump_path}")
            return dump_path
        except Exception as e:
            logger.error(f"Error writing conversation dump {dump_path}: {e}")
            raise

    def list_dumps(self) -> list[Path]:
        """List all conversation dumps.

        Returns:
            List of paths to dump files
        """
        return sorted(self.docs_dir.glob("**/conversation-*.md"), reverse=True)

    @staticmethod
    def _infer_tags(content: str) -> list[str]:
        raw_tags = re.findall(r"#([A-Za-z0-9_-]{2,})", content)
        if "decision:" in content.lower():
            raw_tags.append("decision")
        if "fact:" in content.lower():
            raw_tags.append("fact")
        seen: set[str] = set()
        tags: list[str] = []
        for tag in raw_tags:
            normalized = tag.strip().lower()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            tags.append(normalized)
        return tags

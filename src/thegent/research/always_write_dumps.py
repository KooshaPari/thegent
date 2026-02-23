"""CLAUDE.md: always write conversation dumps to docs/."""

import orjson as json
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
        write_json_companion: bool = True,
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
            write_json_companion: whether to write a JSON companion dump

        Returns:
            Path to the created dump file
        """
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = f"conversation-{conversation_id}-{timestamp}.md"
        json_filename = f"conversation-{conversation_id}-{timestamp}.json"
        target_dir = self.docs_dir / category
        target_dir.mkdir(parents=True, exist_ok=True)
        dump_path = target_dir / filename
        json_path = target_dir / json_filename

        try:
            if tags is None:
                tags = self._infer_tags(content)
            dump_metadata = dict(metadata or {})
            if write_json_companion:
                dump_metadata["json_companion_path"] = str(json_path)
                self.dump_conversation_json(
                    conversation_id=conversation_id,
                    content=content,
                    prompt=prompt,
                    synthesis=synthesis,
                    category=category,
                    tags=tags,
                    metadata=dump_metadata,
                    timestamp=timestamp,
                )
            lines = [
                "---",
                f"conversation_id: {conversation_id}",
                f"timestamp: {timestamp}",
                f"category: {category}",
            ]
            if tags:
                lines.append(f"tags: {json.dumps(tags).decode().decode()}")
            if dump_metadata:
                lines.append(f"metadata: {json.dumps(dump_metadata, ensure_ascii=False).decode().decode()}")
            lines.extend(
                [
                    "---",
                    "",
                    "# Prompt",
                    "",
                    (prompt or ""),
                    "",
                    "# Synthesis",
                    "",
                    (synthesis or content),
                    "",
                    "# Full Output",
                    "",
                    content,
                    "",
                ]
            )
            dump_path.write_text("\n".join(lines), encoding="utf-8")
            logger.info(f"Conversation dump written to {dump_path}")
            return dump_path
        except Exception as e:
            logger.error(f"Error writing conversation dump {dump_path}: {e}")
            raise

    def dump_conversation_json(
        self,
        conversation_id: str,
        content: str,
        *,
        prompt: str | None = None,
        synthesis: str | None = None,
        category: str = "execution",
        tags: list[str] | None = None,
        metadata: dict | None = None,
        timestamp: str | None = None,
    ) -> Path:
        """Dump conversation content to a JSON file.

        Mirrors the markdown dump fields and writes in the same category folder.
        """
        resolved_timestamp = timestamp or datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        target_dir = self.docs_dir / category
        target_dir.mkdir(parents=True, exist_ok=True)
        dump_path = target_dir / f"conversation-{conversation_id}-{resolved_timestamp}.json"
        payload = {
            "conversation_id": conversation_id,
            "timestamp": resolved_timestamp,
            "category": category,
            "tags": tags or self._infer_tags(content),
            "metadata": metadata or {},
            "prompt": prompt or "",
            "synthesis": synthesis or content,
            "full_output": content,
        }
        try:
            dump_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2).decode().decode() + "\n",
                encoding="utf-8",
            )
            logger.info(f"Conversation JSON dump written to {dump_path}")
            return dump_path
        except Exception as e:
            logger.error(f"Error writing conversation JSON dump {dump_path}: {e}")
            raise

    def list_dumps(self) -> list[Path]:
        """List all conversation dumps.

        Returns:
            List of paths to dump files
        """
        return sorted(self.docs_dir.glob("**/conversation-*.md"), reverse=True)

    def list_dumps_json(self) -> list[Path]:
        """List all conversation JSON dumps recursively.

        Returns:
            List of paths to JSON dump files
        """
        return sorted(self.docs_dir.glob("**/conversation-*.json"), reverse=True)

    def latest_dump(self, category: str | None = None, json_only: bool = False) -> Path | None:
        """Return the most recently modified dump path.

        Args:
            category: Optional category folder name to scope the lookup.
            json_only: If true, search JSON dumps; otherwise markdown dumps.

        Returns:
            Path to the latest matching dump, or None if no dump exists.
        """
        suffix = ".json" if json_only else ".md"
        if category:
            search_dir = self.docs_dir / category
            paths = list(search_dir.glob(f"conversation-*{suffix}"))
        else:
            paths = list(self.docs_dir.glob(f"**/conversation-*{suffix}"))
        if not paths:
            return None
        return max(paths, key=lambda p: (p.stat().st_mtime, str(p)))

    def latest_dump_by_category(self, json_only: bool = False) -> dict[str, str]:
        """Return latest dump path strings keyed by category.

        Args:
            json_only: If true, resolve latest JSON dumps per category.

        Returns:
            Mapping of category -> latest dump path string.
        """
        suffix = ".json" if json_only else ".md"
        category_names: set[str] = set()
        for dump_path in self.docs_dir.glob(f"**/conversation-*{suffix}"):
            relative_path = dump_path.relative_to(self.docs_dir)
            parts = relative_path.parts
            category = parts[0] if len(parts) > 1 else "uncategorized"
            category_names.add(category)

        latest_by_category: dict[str, str] = {}
        for category in sorted(category_names):
            latest = self.latest_dump(category=category, json_only=json_only)
            if latest is not None:
                latest_by_category[category] = str(latest)
        return latest_by_category

    def load_dump_json(self, path: Path) -> dict | None:
        """Load a dump JSON payload, failing open on parse errors.

        If a markdown path is provided, this resolves its JSON companion.
        """
        candidate = path
        if candidate.suffix.lower() == ".md":
            candidate = candidate.with_suffix(".json")
        if not candidate.exists():
            return None
        try:
            payload = json.loads(candidate.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            logger.warning("Failed to parse JSON companion %s: %s", candidate, exc)
            return None
        except OSError as exc:
            logger.warning("Failed to read JSON companion %s: %s", candidate, exc)
            return None
        if isinstance(payload, dict):
            return payload
        return None

    def summarize_dump_categories(self) -> dict[str, int]:
        """Return markdown dump counts keyed by category directory."""
        counts: dict[str, int] = {}
        for dump_path in self.docs_dir.glob("**/conversation-*.md"):
            relative_path = dump_path.relative_to(self.docs_dir)
            parts = relative_path.parts
            category = parts[0] if len(parts) > 1 else "uncategorized"
            counts[category] = counts.get(category, 0) + 1
        return dict(sorted(counts.items()))

    def list_dump_categories(self) -> list[str]:
        """Return sorted category names that contain markdown dumps."""
        return sorted(self.summarize_dump_categories())

    def dump_index_payload(self) -> dict:
        """Build the dump index payload without writing it to disk."""
        latest_md = self.latest_dump()
        latest_json = self.latest_dump(json_only=True)
        latest_by_category = self.latest_dump_by_category()
        return {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "docs_dir": str(self.docs_dir),
            "categories": self.summarize_dump_categories(),
            "latest_dump": str(latest_md) if latest_md else None,
            "latest_json_dump": str(latest_json) if latest_json else None,
            "latest_by_category": latest_by_category,
        }

    def persist_dump_index(self, out_path: Path | None = None) -> Path:
        """Write a JSON index with category counts and latest dump paths."""
        target_path = out_path or (self.docs_dir / "dump_index.json")
        target_path.parent.mkdir(parents=True, exist_ok=True)
        payload = self.dump_index_payload()
        target_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2).decode().decode() + "\n",
            encoding="utf-8",
        )
        logger.info(f"Dump index written to {target_path}")
        return target_path

    def export_dump_index_markdown(self, out_path: Path | None = None) -> Path:
        """Write a markdown summary of category counts and latest dumps."""
        target_path = out_path or (self.docs_dir / "dump_index.md")
        target_path.parent.mkdir(parents=True, exist_ok=True)
        payload = self.dump_index_payload()
        category_counts = payload["categories"]
        total_markdown_dumps = sum(category_counts.values())
        latest_md = payload["latest_dump"]
        latest_json = payload["latest_json_dump"]
        latest_by_category = payload.get("latest_by_category") or {}
        latest_json_by_category = self.latest_dump_by_category(json_only=True)
        lines = [
            "# Dump Index",
            "",
            f"- Generated at: {payload['generated_at']}",
            f"- Docs dir: `{payload['docs_dir']}`",
            f"- Total markdown dumps: {total_markdown_dumps}",
            f"- Latest markdown dump: `{latest_md}`" if latest_md else "- Latest markdown dump: _none_",
            f"- Latest JSON dump: `{latest_json}`" if latest_json else "- Latest JSON dump: _none_",
            "",
            "## Category Counts",
            "",
        ]
        if category_counts:
            lines.append("| Category | Markdown Dumps |")
            lines.append("| --- | ---: |")
            for category, count in category_counts.items():
                lines.append(f"| `{category}` | {count} |")
        else:
            lines.append("_No markdown dumps found._")
        lines.append("")
        lines.append("## Latest By Category")
        lines.append("")
        if latest_by_category or latest_json_by_category:
            lines.append("| Category | Latest Markdown Dump | Latest JSON Dump |")
            lines.append("| --- | --- | --- |")
            all_categories = sorted(set(latest_by_category) | set(latest_json_by_category))
            for category in all_categories:
                category_latest_md = latest_by_category.get(category)
                category_latest_json = latest_json_by_category.get(category)
                md_display = f"`{category_latest_md}`" if category_latest_md else "_none_"
                json_display = f"`{category_latest_json}`" if category_latest_json else "_none_"
                lines.append(f"| `{category}` | {md_display} | {json_display} |")
        else:
            lines.append("_No latest dumps by category found._")
        lines.append("")
        target_path.write_text("\n".join(lines), encoding="utf-8")
        logger.info(f"Dump index markdown written to {target_path}")
        return target_path

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

"""Conversation dumper for auto-writing conversation dumps to docs/dumps.

This module provides functionality to automatically dump conversations
with timestamp, model, prompt, and response to configurable locations.

# @trace CONV-DUMP-001
"""

from __future__ import annotations

import orjson as json
import logging
from dataclasses import dataclass, field
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_DUMPS_DIR = Path("docs/dumps")


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class ConversationRecord:
    """A single conversation record with metadata."""

    conversation_id: str
    timestamp: datetime
    model: str
    prompt: str
    response: str
    agent_synthesis: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_markdown(self) -> str:
        """Convert conversation to markdown format.

        Returns:
            Formatted markdown string
        """
        header = f"# Conversation: {self.conversation_id}\n\n"
        meta = f"**Timestamp:** {self.timestamp.isoformat()}\n"
        meta += f"**Model:** {self.model}\n"
        if self.metadata:
            meta += f"**Metadata:** {json.dumps(self.metadata, indent=2)}\n"
        meta += "\n## Prompt\n\n"
        prompt_block = f"{self.prompt}\n\n"
        response_block = f"## Response\n\n{self.response}\n\n"
        synthesis_block = ""
        if self.agent_synthesis:
            synthesis_block = f"## Agent Synthesis\n\n{self.agent_synthesis}\n"
        return header + meta + prompt_block + response_block + synthesis_block

    def to_json(self) -> dict[str, Any]:
        """Convert conversation to JSON-serializable dict.

        Returns:
            Dictionary representation
        """
        return {
            "conversation_id": self.conversation_id,
            "timestamp": self.timestamp.isoformat(),
            "model": self.model,
            "prompt": self.prompt,
            "response": self.response,
            "agent_synthesis": self.agent_synthesis,
            "metadata": self.metadata,
        }


# ---------------------------------------------------------------------------
# Conversation Dumper
# ---------------------------------------------------------------------------


class ConversationDumper:
    """Auto-write conversation dumps to a configurable directory.

    Dumps include timestamp, model, prompt, and response.
    Files are named with conversation_id and timestamp.

    # @trace CONV-DUMP-001
    """

    def __init__(self, dumps_dir: Path | str | None = None) -> None:
        """Initialize the conversation dumper.

        Args:
            dumps_dir: Directory to write dumps to. Defaults to docs/dumps.
        """
        self.dumps_dir = Path(dumps_dir) if dumps_dir else DEFAULT_DUMPS_DIR

    @property
    def dumps_directory(self) -> Path:
        """Return the dumps directory path."""
        return self.dumps_dir

    def ensure_directory(self) -> None:
        """Ensure the dumps directory exists.

        Creates the directory and any necessary parent directories.
        """
        self.dumps_dir.mkdir(parents=True, exist_ok=True)
        logger.debug("Ensured dumps directory exists: %s", self.dumps_dir)

    def dump_conversation(
        self,
        conversation_id: str,
        model: str,
        prompt: str,
        response: str,
        agent_synthesis: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Path:
        """Dump a conversation to a file.

        Args:
            conversation_id: Unique identifier for the conversation
            model: The model used for the conversation
            prompt: The prompt sent to the model
            response: The response from the model
            agent_synthesis: Optional agent synthesis/summary
            metadata: Optional additional metadata

        Returns:
            Path to the created dump file

        Raises:
            IOError: If writing the file fails
        """
        self.ensure_directory()

        timestamp = datetime.now(tz=UTC)
        record = ConversationRecord(
            conversation_id=conversation_id,
            timestamp=timestamp,
            model=model,
            prompt=prompt,
            response=response,
            agent_synthesis=agent_synthesis,
            metadata=metadata or {},
        )

        # Generate filename: conversation-{id}-{timestamp}.md
        timestamp_str = timestamp.strftime("%Y-%m-%d-%H-%M-%S-%f")
        filename = f"conversation-{conversation_id}-{timestamp_str}.md"
        dump_path = self.dumps_dir / filename

        try:
            content = record.to_markdown()
            dump_path.write_text(content, encoding="utf-8")
            logger.info("Conversation dump written to %s", dump_path)
            return dump_path
        except Exception as e:
            logger.error("Error writing conversation dump to %s: %s", dump_path, e)
            raise OSError(f"Failed to write conversation dump: {e}") from e

    def dump_conversation_json(
        self,
        conversation_id: str,
        model: str,
        prompt: str,
        response: str,
        agent_synthesis: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Path:
        """Dump a conversation to a JSON file.

        Args:
            conversation_id: Unique identifier for the conversation
            model: The model used for the conversation
            prompt: The prompt sent to the model
            response: The response from the model
            agent_synthesis: Optional agent synthesis/summary
            metadata: Optional additional metadata

        Returns:
            Path to the created dump file

        Raises:
            IOError: If writing the file fails
        """
        self.ensure_directory()

        timestamp = datetime.now(tz=UTC)
        record = ConversationRecord(
            conversation_id=conversation_id,
            timestamp=timestamp,
            model=model,
            prompt=prompt,
            response=response,
            agent_synthesis=agent_synthesis,
            metadata=metadata or {},
        )

        # Generate filename: conversation-{id}-{timestamp}.json
        timestamp_str = timestamp.strftime("%Y-%m-%d-%H-%M-%S-%f")
        filename = f"conversation-{conversation_id}-{timestamp_str}.json"
        dump_path = self.dumps_dir / filename

        try:
            content = json.dumps(record.to_json(), indent=2, ensure_ascii=False)
            dump_path.write_text(content, encoding="utf-8")
            logger.info("Conversation dump (JSON) written to %s", dump_path)
            return dump_path
        except Exception as e:
            logger.error("Error writing conversation dump (JSON) to %s: %s", dump_path, e)
            raise OSError(f"Failed to write conversation dump: {e}") from e

    def list_dumps(self, conversation_id: str | None = None) -> list[Path]:
        """List all conversation dumps.

        Args:
            conversation_id: Optional filter by conversation ID

        Returns:
            List of paths to dump files, sorted by modification time (newest first)
        """
        if not self.dumps_dir.exists():
            return []

        if conversation_id:
            pattern = f"conversation-{conversation_id}-*.md"
        else:
            pattern = "conversation-*.md"

        dumps = list(self.dumps_dir.glob(pattern))
        # Sort by modification time, newest first
        dumps.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return dumps

    def list_dumps_json(self, conversation_id: str | None = None) -> list[Path]:
        """List all JSON conversation dumps.

        Args:
            conversation_id: Optional filter by conversation ID

        Returns:
            List of paths to JSON dump files, sorted by modification time (newest first)
        """
        if not self.dumps_dir.exists():
            return []

        if conversation_id:
            pattern = f"conversation-{conversation_id}-*.json"
        else:
            pattern = "conversation-*.json"

        dumps = list(self.dumps_dir.glob(pattern))
        # Sort by modification time, newest first
        dumps.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return dumps

    def get_dump(self, dump_path: Path) -> ConversationRecord | None:
        """Read a conversation dump from a file.

        Args:
            dump_path: Path to the dump file

        Returns:
            ConversationRecord if the file exists and is valid, None otherwise
        """
        if not dump_path.exists():
            logger.warning("Dump file does not exist: %s", dump_path)
            return None

        try:
            content = dump_path.read_text(encoding="utf-8")

            # Try JSON first
            if dump_path.suffix == ".json":
                data = json_loads(content)
                return ConversationRecord(
                    conversation_id=data["conversation_id"],
                    timestamp=datetime.fromisoformat(data["timestamp"]),
                    model=data["model"],
                    prompt=data["prompt"],
                    response=data["response"],
                    agent_synthesis=data.get("agent_synthesis"),
                    metadata=data.get("metadata", {}),
                )

            # Parse markdown - extract from prompt/response sections
            # This is a best-effort parse
            lines = content.splitlines()
            in_prompt = False
            in_response = False
            prompt_lines: list[str] = []
            response_lines: list[str] = []

            for line in lines:
                if line.strip() == "## Prompt":
                    in_prompt = True
                    in_response = False
                    continue
                if line.strip() == "## Response":
                    in_prompt = False
                    in_response = True
                    continue
                if line.startswith("## "):
                    in_prompt = False
                    in_response = False

                if in_prompt:
                    prompt_lines.append(line)
                elif in_response:
                    response_lines.append(line)

            # Extract metadata from header
            # Filename format: conversation-{id}-{timestamp}.md
            # Timestamp is YYYY-MM-DD-HH-MM-SS-ffffff (7 parts)
            stem = dump_path.stem.replace("conversation-", "")
            parts = stem.split("-")
            # The conversation_id is everything except the last 7 parts (timestamp)
            if len(parts) >= 7:
                conversation_id = "-".join(parts[:-7])
            else:
                conversation_id = parts[0]
            model = "unknown"

            for line in lines:
                if line.startswith("**Model:**"):
                    model = line.split(":**")[1].strip()

            return ConversationRecord(
                conversation_id=conversation_id,
                timestamp=datetime.fromtimestamp(dump_path.stat().st_mtime, tz=UTC),
                model=model,
                prompt="\n".join(prompt_lines).strip(),
                response="\n".join(response_lines).strip(),
                metadata={},
            )
        except Exception as e:
            logger.error("Error reading dump file %s: %s", dump_path, e)
            return None


# ---------------------------------------------------------------------------
# Convenience factory
# ---------------------------------------------------------------------------


def get_dumper(dumps_dir: Path | str | None = None) -> ConversationDumper:
    """Get a ConversationDumper instance.

    Args:
        dumps_dir: Optional custom dumps directory

    Returns:
        Configured ConversationDumper instance
    """
    return ConversationDumper(dumps_dir=dumps_dir)

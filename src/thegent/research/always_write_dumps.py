"""CLAUDE.md: always write conversation dumps to docs/."""

import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ConversationDumper:
    """Always write conversation dumps to docs/."""

    def __init__(self, docs_dir: Path = Path("docs/dumps")) -> None:
        self.docs_dir = docs_dir
        self.docs_dir.mkdir(parents=True, exist_ok=True)

    def dump_conversation(self, conversation_id: str, content: str) -> Path:
        """Dump conversation content to a file.

        Args:
            conversation_id: Unique identifier for the conversation
            content: Conversation content to dump

        Returns:
            Path to the created dump file
        """
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = f"conversation-{conversation_id}-{timestamp}.md"
        dump_path = self.docs_dir / filename

        try:
            dump_path.write_text(content)
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
        return sorted(self.docs_dir.glob("conversation-*.md"), reverse=True)

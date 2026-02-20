"""Research: Always write conversation dumps to docs/."""

from pathlib import Path
from typing import Any

from thegent.research.always_dumps import ConversationDumpWriter


class AlwaysWriteDumpsResearch:
    """Research for always writing dumps."""

    def __init__(self) -> None:
        """Initialize always dumps research."""
        self.writer = ConversationDumpWriter(Path("docs/conversation_dumps"))

    def test_dump_writing(self, conversation: dict[str, Any]) -> Path:
        """Test writing a dump.

        Args:
            conversation: Conversation data

        Returns:
            Path to written dump
        """
        return self.writer.write_dump(conversation)

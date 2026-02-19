"""Always write conversation dumps to docs/."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ConversationDumpWriter:
    """Writer for conversation dumps."""

    def __init__(self, output_dir: Path | None = None):
        """Initialize dump writer.
        
        Args:
            output_dir: Output directory for dumps
        """
        self.output_dir = output_dir or Path("docs/conversation_dumps")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_dump(self, conversation: dict[str, Any], prefix: str = "conversation") -> Path:
        """Write conversation dump to file.
        
        Args:
            conversation: Conversation data
            prefix: File prefix
            
        Returns:
            Path to written file
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.json"
        file_path = self.output_dir / filename
        
        with open(file_path, "w") as f:
            json.dump(conversation, f, indent=2)
        
        logger.info(f"Wrote conversation dump: {file_path}")
        return file_path

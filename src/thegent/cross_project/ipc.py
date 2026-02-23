"""File-based IPC protocol for cross-project agents."""

import orjson as json
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class CrossProjectIPC:
    """File-based IPC for cross-project agents."""

    def __init__(self, ipc_dir: Path | None = None) -> None:
        """Initialize cross-project IPC.

        Args:
            ipc_dir: IPC directory
        """
        self.ipc_dir = ipc_dir or Path("~/.thegent/ipc").expanduser()
        self.ipc_dir.mkdir(parents=True, exist_ok=True)

    def send_message(self, target_project: str, message: dict[str, Any]) -> Path:
        """Send message to target project.

        Args:
            target_project: Target project name
            message: Message dictionary

        Returns:
            Path to message file
        """
        message_file = self.ipc_dir / f"{target_project}_{int(time.time())}.json"
        message_file.write_text(json.dumps(message, indent=2))
        logger.info(f"Sent message to {target_project}")
        return message_file

    def receive_messages(self, project: str) -> list[dict[str, Any]]:
        """Receive messages for project.

        Args:
            project: Project name

        Returns:
            List of messages
        """
        messages = []
        for msg_file in self.ipc_dir.glob(f"{project}_*.json"):
            msg = self._read_message_file(msg_file)
            if msg is not None:
                messages.append(msg)
                msg_file.unlink()  # Consume message

        logger.info(f"Received {len(messages)} messages for {project}")
        return messages

    def _read_message_file(self, msg_file: Path) -> dict[str, Any] | None:
        """Read and parse a single message file."""
        try:
            return json.loads(msg_file.read_text())
        except Exception as e:
            logger.error(f"Error reading message {msg_file}: {e}")
            return None

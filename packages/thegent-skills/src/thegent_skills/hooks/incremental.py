"""Implement incremental-check/record subcommands (manifest-based)."""

import orjson as json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class IncrementalSubcommands:
    """Incremental check/record subcommands."""

    def __init__(self, manifest_path: Path | None = None) -> None:
        """Initialize incremental subcommands.

        Args:
            manifest_path: Manifest file path
        """
        self.manifest_path = manifest_path or Path(".incremental-manifest.json")
        self.manifest: dict[str, Any] = self._load_manifest()

    def _load_manifest(self) -> dict[str, Any]:
        """Load manifest.

        Returns:
            Manifest dictionary
        """
        if self.manifest_path.exists():
            try:
                return json.loads(self.manifest_path.read_text())
            except Exception:
                return {}
        return {}

    def check(self, file_path: Path) -> bool:
        """Check if file needs processing.

        Args:
            file_path: File to check

        Returns:
            True if needs processing
        """
        file_str = str(file_path)
        last_hash = self.manifest.get(file_str)
        current_hash = self._file_hash(file_path)

        if last_hash != current_hash:
            logger.info(f"File {file_path} changed, needs processing")
            return True

        return False

    def record(self, file_path: Path) -> None:
        """Record file as processed.

        Args:
            file_path: File to record
        """
        file_str = str(file_path)
        self.manifest[file_str] = self._file_hash(file_path)
        self._save_manifest()

    def _file_hash(self, file_path: Path) -> str:
        """Calculate file hash.

        Args:
            file_path: File path

        Returns:
            File hash
        """
        import hashlib

        if file_path.exists():
            content = file_path.read_bytes()
            return hashlib.sha256(content).hexdigest()
        return ""

    def _save_manifest(self) -> None:
        """Save manifest."""
        self.manifest_path.write_text(json.dumps(self.manifest, indent=2))

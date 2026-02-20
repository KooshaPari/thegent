"""Incremental documentation generation (only changed files)."""

import hashlib
import json
import logging
from datetime import UTC, datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class IncrementalGenerator:
    """Generate documentation only for changed files."""

    def __init__(self, manifest_path: Path | None = None) -> None:
        """Initialize incremental generator.

        Args:
            manifest_path: Path to manifest file
        """
        self.manifest_path = manifest_path or Path(".docgen-manifest.json")
        self.manifest: dict[str, Any] = self._load_manifest()

    def _load_manifest(self) -> dict[str, Any]:
        """Load generation manifest.

        Returns:
            Manifest dictionary
        """
        if self.manifest_path.exists():
            try:
                return json.loads(self.manifest_path.read_text())
            except Exception as e:
                logger.warning(f"Could not load manifest: {e}")
        return {"files": {}, "last_generated": None}

    def _generate_file_doc(self, results: list[Any], file_path: Path, generator_func: Any) -> None:
        """Generate docs for a single file safely."""
        try:
            result = generator_func(file_path)
            results.append(result)
        except Exception as e:
            logger.error(f"Error generating docs for {file_path}: {e}")
            results.append({"error": str(e), "file": str(file_path)})

    def _save_manifest(self) -> None:
        """Save generation manifest."""
        self.manifest["last_generated"] = datetime.now(UTC).isoformat()
        self.manifest_path.write_text(json.dumps(self.manifest, indent=2))

    def _file_hash(self, file_path: Path) -> str:
        """Calculate file hash.

        Args:
            file_path: File path

        Returns:
            File hash
        """
        content = file_path.read_text()
        return hashlib.sha256(content.encode()).hexdigest()

    def get_changed_files(self, files: list[Path]) -> list[Path]:
        """Get list of changed files.

        Args:
            files: List of files to check

        Returns:
            List of changed files
        """
        changed = []

        for file_path in files:
            file_str = str(file_path)
            current_hash = self._file_hash(file_path)

            if file_str not in self.manifest["files"]:
                # New file
                changed.append(file_path)
                self.manifest["files"][file_str] = {
                    "hash": current_hash,
                    "last_modified": datetime.now(UTC).isoformat(),
                }
            elif self.manifest["files"][file_str]["hash"] != current_hash:
                # Changed file
                changed.append(file_path)
                self.manifest["files"][file_str] = {
                    "hash": current_hash,
                    "last_modified": datetime.now(UTC).isoformat(),
                }

        return changed

    def generate_incremental(
        self,
        files: list[Path],
        generator_func: callable,
    ) -> dict[str, Any]:
        """Generate documentation incrementally.

        Args:
            files: List of files to check
            generator_func: Function to generate docs

        Returns:
            Generation results
        """
        changed_files = self.get_changed_files(files)

        logger.info(f"Found {len(changed_files)} changed files out of {len(files)}")

        results = []
        for file_path in changed_files:
            self._generate_file_doc(results, file_path, generator_func)

        self._save_manifest()

        return {
            "total_files": len(files),
            "changed_files": len(changed_files),
            "generated": len(results),
            "results": results,
        }

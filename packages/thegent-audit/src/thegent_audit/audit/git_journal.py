"""Git journal classes for shadow audit.

Extracted from shadow_audit_git.py for maintainability.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any


logger = logging.getLogger(__name__)


def _scrub_secrets(content: str) -> str:
    """Remove potential secrets from content.
    
    Args:
        content: Content to scrub
        
    Returns:
        Scrubbed content
    """
    import re
    
    # Scrub API keys
    content = re.sub(r'sk-[a-zA-Z0-9]{20,}', 'sk-***REDACTED***', content)
    content = re.sub(r'api[_-]?key["\s:=]+["\']?[^"\s\'"]+["\']?', 'api_key=***REDACTED***', content, flags=re.IGNORECASE)
    
    # Scrub tokens
    content = re.sub(r'Bearer\s+[a-zA-Z0-9_-]+', 'Bearer ***REDACTED***', content)
    content = re.sub(r'token["\s:=]+["\']?[^"\s\'"]+["\']?', 'token=***REDACTED***', content, flags=re.IGNORECASE)
    
    # Scrub passwords
    content = re.sub(r'password["\s:=]+["\']?[^"\s\'"]+["\']?', 'password=***REDACTED***', content, flags=re.IGNORECASE)
    
    return content


def _new_id() -> str:
    """Generate a new unique ID."""
    import uuid
    return uuid.uuid4().hex[:8]


def _now_iso() -> str:
    """Get current time in ISO format."""
    return datetime.now(UTC).isoformat()


@dataclass
class JournalEntry:
    """A single journal entry."""
    id: str = field(default_factory=_new_id)
    timestamp: str = field(default_factory=_now_iso)
    agent: str = ""
    action: str = ""
    target: str = ""
    result: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "agent": self.agent,
            "action": self.action,
            "target": self.target,
            "result": self.result,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "JournalEntry":
        """Create from dictionary."""
        return cls(
            id=data.get("id", _new_id()),
            timestamp=data.get("timestamp", _now_iso()),
            agent=data.get("agent", ""),
            action=data.get("action", ""),
            target=data.get("target", ""),
            result=data.get("result", ""),
            metadata=data.get("metadata", {}),
        )


class GitJournal:
    """Git-based journal for audit trails.
    
    Stores audit entries as JSON files in a git-tracked directory.
    """
    
    def __init__(self, journal_dir: Path | str):
        """Initialize the journal.
        
        Args:
            journal_dir: Directory to store journal entries
        """
        self.journal_dir = Path(journal_dir).expanduser()
        self.journal_dir.mkdir(parents=True, exist_ok=True)
        self._entries_dir = self.journal_dir / "entries"
        self._entries_dir.mkdir(exist_ok=True)
    
    def add_entry(
        self,
        agent: str,
        action: str,
        target: str,
        result: str,
        metadata: dict[str, Any] | None = None,
    ) -> JournalEntry:
        """Add a journal entry.
        
        Args:
            agent: Agent that performed the action
            action: Action performed
            target: Target of the action
            result: Result of the action
            metadata: Optional additional metadata
            
        Returns:
            The created entry
        """
        entry = JournalEntry(
            agent=agent,
            action=action,
            target=_scrub_secrets(target),
            result=_scrub_secrets(result),
            metadata=metadata or {},
        )
        
        # Write to file
        entry_file = self._entries_dir / f"{entry.id}.json"
        import orjson as json
        entry_file.write_text(json.dumps(entry.to_dict(), indent=2))
        
        return entry
    
    def get_entry(self, entry_id: str) -> JournalEntry | None:
        """Get an entry by ID.
        
        Args:
            entry_id: Entry ID
            
        Returns:
            Entry or None if not found
        """
        entry_file = self._entries_dir / f"{entry_id}.json"
        
        if not entry_file.exists():
            return None
        
        import orjson as json
        data = json.loads(entry_file.read_text())
        return JournalEntry.from_dict(data)
    
    def list_entries(
        self,
        agent: str | None = None,
        action: str | None = None,
        limit: int = 100,
    ) -> list[JournalEntry]:
        """List journal entries.
        
        Args:
            agent: Filter by agent
            action: Filter by action
            limit: Maximum entries to return
            
        Returns:
            List of entries
        """
        entries = []
        
        for entry_file in sorted(
            self._entries_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        ):
            try:
                import orjson as json
                data = json.loads(entry_file.read_text())
                entry = JournalEntry.from_dict(data)
                
                # Apply filters
                if agent and entry.agent != agent:
                    continue
                if action and entry.action != action:
                    continue
                
                entries.append(entry)
                
                if len(entries) >= limit:
                    break
            except Exception as e:
                logger.warning(f"Failed to read entry {entry_file}: {e}")
        
        return entries
    
    def commit(self, message: str = "Journal update") -> bool:
        """Commit journal changes to git.
        
        Args:
            message: Commit message
            
        Returns:
            True if successful
        """
        import subprocess
        
        try:
            # Check if git repo
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.journal_dir,
                capture_output=True,
                text=True,
            )
            
            if result.returncode != 0:
                # Not a git repo, initialize
                subprocess.run(
                    ["git", "init"],
                    cwd=self.journal_dir,
                    check=True,
                )
            
            # Add all entries
            subprocess.run(
                ["git", "add", "entries/"],
                cwd=self.journal_dir,
                check=True,
            )
            
            # Commit
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.journal_dir,
                capture_output=True,
                text=True,
            )
            
            # Ignore "nothing to commit" error
            if result.returncode != 0 and "nothing to commit" not in result.stdout:
                logger.warning(f"Git commit failed: {result.stderr}")
                return False
            
            return True
        except Exception as e:
            logger.warning(f"Git operation failed: {e}")
            return False


__all__ = [
    "JournalEntry",
    "GitJournal",
    "_scrub_secrets",
    "_new_id",
    "_now_iso",
]

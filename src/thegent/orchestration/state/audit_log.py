"""ShadowAuditGit: git-backed audit log for agent episodes (wp-71002).

Maintains a separate git repository at ``~/.thegent/audit/`` that records
file snapshots (with secrets scrubbed) for every episode transaction.

# @trace FR-VCS-001
"""

from __future__ import annotations

import logging
import re
import shutil
import subprocess
from pathlib import Path

from thegent.governance.native_secret_scan import scan_secrets

_log = logging.getLogger(__name__)

_DEFAULT_AUDIT_PATH = Path.home() / ".thegent" / "audit"


class ShadowAuditGit:
    """Git-backed shadow audit repository.

    Args:
        audit_path: Root directory for the audit git repo.
            Defaults to ``~/.thegent/audit/``.
    """

    def __init__(self, audit_path: Path = _DEFAULT_AUDIT_PATH) -> None:
        self._audit_path = Path(audit_path)

    @property
    def path(self) -> Path:
        return self._audit_path

    def init_shadow_repo(self) -> None:
        """Initialize the shadow audit git repository.

        Idempotent: if the repo already exists, this is a no-op.
        """
        if (self._audit_path / ".git").is_dir():
            _log.debug("Shadow audit repo already initialized at %s", self._audit_path)
            return

        self._audit_path.mkdir(parents=True, exist_ok=True)
        self._git("init")
        self._git("config", "user.email", "thegent-audit@localhost")
        self._git("config", "user.name", "thegent-audit")

        # Create initial commit so the repo has a HEAD
        readme = self._audit_path / "README.md"
        readme.write_text("# thegent audit log\n\nAuto-managed by ShadowAuditGit.\n")
        self._git("add", "README.md")
        self._git("commit", "-m", "init: shadow audit repository")
        _log.info("Initialized shadow audit repo at %s", self._audit_path)

    def commit_transaction(
        self,
        episode_id: str,
        changed_files: list[Path],
        message: str,
        remote_host: str | None = None,
    ) -> None:
        """Stage file snapshots (scrubbed) and commit to the audit repo.

        Args:
            episode_id: Episode identifier to include in commit message.
            changed_files: List of file paths to snapshot into the audit repo.
            message: Commit message (episode_id will be prepended).
            remote_host: If provided, indicates the worker host where change occurred.
        """
        if not changed_files:
            return

        snapshots_dir = self._audit_path / "snapshots"
        if remote_host:
            snapshots_dir = snapshots_dir / remote_host
        snapshots_dir.mkdir(parents=True, exist_ok=True)

        for file_path in changed_files:
            if not file_path.exists():
                raise FileNotFoundError(f"Cannot snapshot non-existent file: {file_path}")
            content = file_path.read_text(encoding="utf-8", errors="replace")
            findings = scan_secrets(content)
            if findings:
                secret_line_nums = {m.line for m in findings}
                lines = content.splitlines(keepends=True)
                content = "".join(
                    "[REDACTED]\n" if (idx + 1) in secret_line_nums else ln for idx, ln in enumerate(lines)
                )
            dest = snapshots_dir / file_path.name
            dest.write_text(content, encoding="utf-8")
        self._git("add", "-A")

        commit_msg = f"[{episode_id}] {message}"
        if remote_host:
            commit_msg = f"({remote_host}) {commit_msg}"
        self._git("commit", "-m", commit_msg, "--allow-empty")

    def get_log(
        self,
        limit: int = 20,
        episode_id: str | None = None,
    ) -> list[dict[str, str]]:
        """Query the audit git log.

        Args:
            limit: Maximum number of entries to return.
            episode_id: If provided, filter to commits containing this ID.

        Returns:
            List of dicts with keys: hash, message, date.
        """
        args = ["log", f"--max-count={limit}", "--format=%H|%s|%aI"]
        if episode_id:
            args.extend(["--grep", episode_id])

        result = self._git(*args)
        entries: list[dict[str, str]] = []
        for line in result.stdout.strip().splitlines():
            if not line:
                continue
            parts = line.split("|", 2)
            if len(parts) == 3:
                entries.append(
                    {
                        "hash": parts[0],
                        "message": parts[1],
                        "date": parts[2],
                    }
                )
        return entries

    def get_diff(self, commit_hash: str) -> str:
        """Return the diff for a specific commit.

        Args:
            commit_hash: The git commit hash to diff.

        Returns:
            The diff output as a string.
        """
        result = self._git("diff", f"{commit_hash}~1", commit_hash)
        return result.stdout

    # -- Internal -----------------------------------------------------------

    def _git(self, *args: str) -> subprocess.CompletedProcess[str]:
        """Run a git command in the audit repo directory."""
        cmd = ["git", *args]
        return subprocess.run(
            cmd,
            cwd=self._audit_path,
            capture_output=True,
            text=True,
            check=True,
        )

    @staticmethod
    def _scrub_secrets(content: str) -> str:
        """Replace detected secrets in content with redaction markers."""
        matches = scan_secrets(content)
        if not matches:
            return content

        lines = content.splitlines()
        for match in matches:
            line_idx = match.line - 1
            if 0 <= line_idx < len(lines):
                # Replace the secret portion with the masked version
                lines[line_idx] = re.sub(
                    r"(=\s*)\S+",
                    rf"\g<1>[REDACTED:{match.kind}]",
                    lines[line_idx],
                    count=1,
                )
        return "\n".join(lines)

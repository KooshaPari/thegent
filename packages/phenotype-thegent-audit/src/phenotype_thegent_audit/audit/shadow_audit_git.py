"""Shadow audit Git log with secret scrubbing.

Tracks all git operations as immutable audit entries in SQLite, with
automatic secret scrubbing via the native secret scanner before storage.

Also provides GitJournal for micro-commit journaling using git refs
that never get pushed (local-only audit trail).

WBS: wp-71002-shadow-git
FR Traceability: FR-VER-003 (shadow audit log with secret scrubbing)
"""

from __future__ import annotations
from phenotype_thegent_core.infra.shim_subprocess import run as shim_run

import asyncio
import hashlib
import logging
import orjson as json
import os
import re
import sqlite3
import subprocess
import uuid
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from phenotype_thegent_audit.audit.constants import DEFAULT_DB_PATH
from phenotype_thegent_audit.audit.secret_scrubbing import SECRET_PATTERNS, scrub_secrets as _scrub_secrets

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Re-export for backwards compatibility
# Fixed - removed duplicate


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


def _new_id() -> str:
    return uuid.uuid4().hex[:12]


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


class AuditEntry(BaseModel):
    """An immutable audit log entry for a git commit."""

    id: str = Field(default_factory=_new_id)
    project_id: str
    sha: str
    message: str
    diff: str
    created_at: str = Field(default_factory=_now_iso)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dict."""
        return self.model_dump()


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_AUDIT_SCHEMA_SQL = """\
CREATE TABLE IF NOT EXISTS audit_entries (
    id         TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    sha        TEXT NOT NULL,
    message    TEXT NOT NULL,
    diff       TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""

# ---------------------------------------------------------------------------
# ShadowAuditGit
# ---------------------------------------------------------------------------


class ShadowAuditGit:
    """Tracks git operations as immutable audit entries with secret scrubbing.

    All commit messages and diffs are scrubbed for secrets before storage.
    Uses the same SQLite database as ProjectRegistry (shared DB path).

    Parameters
    ----------
    db_path:
        Path to the SQLite database file.  Defaults to ``~/.thegent/registry.db``.
    """

    def __init__(self, db_path: Path | str | None = None) -> None:
        import os

        if db_path is None:
            env_path = os.environ.get("THGENT_REGISTRY_DB")
            self._db_path = Path(env_path) if env_path else _DEFAULT_DB_PATH
        else:
            self._db_path = Path(db_path)

        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self._db_path))
        self._conn.row_factory = sqlite3.Row
        journal_mode_cursor = self._conn.execute("PRAGMA journal_mode=WAL")
        journal_mode_cursor.fetchone()
        journal_mode_cursor.close()
        foreign_keys_cursor = self._conn.execute("PRAGMA foreign_keys=ON")
        foreign_keys_cursor.close()
        self._conn.executescript(_AUDIT_SCHEMA_SQL)
        self._conn.commit()
        log.debug("shadow_audit_git.init db_path=%s", self._db_path)

    def record_commit(
        self,
        project_id: str,
        sha: str,
        message: str,
        diff: str,
    ) -> AuditEntry:
        """Record a git commit as an immutable audit entry.

        Both the message and diff are scrubbed for secrets before storage.
        """
        scrubbed_message = _scrub_secrets(message)
        scrubbed_diff = _scrub_secrets(diff)

        entry = AuditEntry(
            project_id=project_id,
            sha=sha,
            message=scrubbed_message,
            diff=scrubbed_diff,
        )
        self._conn.execute(
            "INSERT INTO audit_entries (id, project_id, sha, message, diff, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (entry.id, entry.project_id, entry.sha, entry.message, entry.diff, entry.created_at),
        )
        self._conn.commit()
        log.info("shadow_audit_git.record_commit sha=%s project=%s", sha, project_id)
        return entry

    def get_audit_log(self, project_id: str, limit: int | None = None) -> list[AuditEntry]:
        """Return audit entries for a project, ordered by creation time.

        Parameters
        ----------
        project_id:
            The project whose audit log to retrieve.
        limit:
            Maximum number of entries to return.  None means all.
        """
        query = (
            "SELECT id, project_id, sha, message, diff, created_at "
            "FROM audit_entries WHERE project_id = ? ORDER BY created_at"
        )
        params: list[Any] = [project_id]
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)

        rows = self._conn.execute(query, params).fetchall()
        return [
            AuditEntry(
                id=r["id"],
                project_id=r["project_id"],
                sha=r["sha"],
                message=r["message"],
                diff=r["diff"],
                created_at=r["created_at"],
            )
            for r in rows
        ]

    def export_audit(self, project_id: str, path: Path | str) -> None:
        """Export the audit log for a project to a JSON file."""
        entries = self.get_audit_log(project_id)
        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(json.dumps([e.to_dict() for e in entries]))
        log.info("shadow_audit_git.export_audit project=%s path=%s", project_id, dest)


# ---------------------------------------------------------------------------
# GitJournal: Micro-commit journaling using git refs (never pushed)
# ---------------------------------------------------------------------------


class GitJournal:
    """Git-based journaling system for granular file change audit.

    Creates micro-commits for every file change using git's plumbing
    commands. All commits are stored in refs/audit/* namespace which
    is excluded from push by default.

    Key features:
    - Micro-commits on every file change (journaling)
    - Local-only refs (never pushed to remote)
    - Tracks secrets/sensitive files locally
    - Works with or without worktrees
    - Uses git's object model directly (efficient, no file copying)

    Usage:
        journal = GitJournal(repo_path, session_id="run-123")
        journal.record_file_change(path, content, action="modified")
        journal.finalize_session()
    """

    # Ref namespace for audit commits (excluded from push)
    AUDIT_REF_PREFIX = "refs/audit"

    def __init__(
        self,
        repo_root: Path | str,
        session_id: str,
        *,
        track_secrets: bool = True,
        auto_commit: bool = True,
    ) -> None:
        """Initialize the git journal.

        Args:
            repo_root: Path to git repository root
            session_id: Unique session identifier for grouping commits
            track_secrets: Whether to track files that may contain secrets
            auto_commit: Whether to auto-commit on record_file_change
        """
        self.repo_root = Path(repo_root).resolve()
        if not self.repo_root.exists():
            raise FileNotFoundError(f"Repository path does not exist: {self.repo_root}")
        self.session_id = session_id
        self.track_secrets = track_secrets
        self.auto_commit = auto_commit

        # Audit ref for this session
        self.audit_ref = f"{self.AUDIT_REF_PREFIX}/{session_id}"

        # Current tree state (file_path -> blob_sha)
        self._current_tree: dict[str, str] = {}

        # Parent commit for next micro-commit
        self._parent_sha: str | None = None

        # Initialize from current HEAD if exists
        self._init_from_head()

        # Ensure audit refs are excluded from push
        self._configure_push_exclusion()

        log.info(
            "GitJournal.init repo=%s session=%s ref=%s",
            self.repo_root,
            self.session_id,
            self.audit_ref,
        )

    def _run_git(self, *args: str, input_data: bytes | None = None) -> str:
        """Run a git command and return stdout."""
        result = shim_run(
            ["git"] + list(args),
            cwd=self.repo_root,
            capture_output=True,
            input=input_data,
            timeout=30,
        )
        if result.returncode != 0:
            log.warning("git %s failed: %s", args[0], result.stderr.decode())
        return result.stdout.decode().strip()

    def _init_from_head(self) -> None:
        """Initialize tree state from current HEAD commit."""
        try:
            # Get HEAD commit SHA
            head_sha = self._run_git("rev-parse", "HEAD")
            if head_sha:
                self._parent_sha = head_sha

                # Get tree SHA from HEAD
                tree_sha = self._run_git("rev-parse", "HEAD^{tree}")

                # Load current tree state
                self._load_tree(tree_sha)

                log.debug("GitJournal._init_from_head sha=%s tree=%s", head_sha, tree_sha)
        except Exception as e:
            log.debug("GitJournal._init_from_head: no HEAD, starting fresh: %s", e)
            self._parent_sha = None
            self._current_tree = {}

    def _load_tree(self, tree_sha: str) -> None:
        """Load tree entries into _current_tree dict."""
        try:
            # ls-tree returns: mode type sha\tpath
            output = self._run_git("ls-tree", "-r", tree_sha)
            for line in output.split("\n"):
                if not line.strip():
                    continue
                parts = line.split("\t", 1)
                if len(parts) == 2:
                    mode_type_sha = parts[0].split()
                    if len(mode_type_sha) >= 3:
                        blob_sha = mode_type_sha[2]
                        file_path = parts[1]
                        self._current_tree[file_path] = blob_sha
        except Exception as e:
            log.warning("GitJournal._load_tree failed: %s", e)

    def _configure_push_exclusion(self) -> None:
        """Ensure audit refs are excluded from push."""
        # Check if already configured
        try:
            result = self._run_git("config", "--local", "--get", "remote.origin.push")
            if self.AUDIT_REF_PREFIX in result:
                return  # Already configured
        except Exception as e:
            log.debug("GitJournal._configure_push_exclusion: config check failed: %s", e)

        # Configure to exclude audit refs from push
        # Using negative refspec to exclude
        try:
            self._run_git("config", "--local", "--add", "remote.origin.push", f"!{self.AUDIT_REF_PREFIX}/*")
            log.info("GitJournal: configured audit refs to be excluded from push")
        except Exception as e:
            log.warning("GitJournal: failed to configure push exclusion: %s", e)

    def _hash_object(self, content: bytes) -> str:
        """Store content in git object database, return SHA."""
        result = shim_run(
            ["git", "hash-object", "-w", "--stdin"],
            cwd=self.repo_root,
            input=content,
            capture_output=True,
            timeout=10,
        )
        return result.stdout.decode().strip()

    def _create_tree(self, entries: dict[str, str]) -> str:
        """Create a tree object from path->sha entries."""
        # Build tree input format: mode type sha\tpath
        lines = []
        for path, sha in sorted(entries.items()):
            lines.append(f"100644 blob {sha}\t{path}")

        tree_input = "\n".join(lines).encode()
        result = shim_run(
            ["git", "mktree"],
            cwd=self.repo_root,
            input=tree_input,
            capture_output=True,
            timeout=30,
        )
        return result.stdout.decode().strip()

    def _create_commit(
        self,
        tree_sha: str,
        message: str,
        parent: str | None = None,
    ) -> str:
        """Create a commit object, return SHA."""
        # Build commit
        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = env.get("GIT_AUTHOR_NAME", "thegent-audit")
        env["GIT_AUTHOR_EMAIL"] = env.get("GIT_AUTHOR_EMAIL", "audit@thegent.dev")
        env["GIT_COMMITTER_NAME"] = env.get("GIT_COMMITTER_NAME", "thegent-audit")
        env["GIT_COMMITTER_EMAIL"] = env.get("GIT_COMMITTER_EMAIL", "audit@thegent.dev")

        cmd = ["git", "commit-tree", tree_sha, "-m", message]
        if parent:
            cmd.extend(["-p", parent])

        result = shim_run(
            cmd,
            cwd=self.repo_root,
            capture_output=True,
            env=env,
            timeout=10,
        )
        return result.stdout.decode().strip()

    def _update_ref(self, ref: str, sha: str) -> None:
        """Update a git ref to point to a commit."""
        self._run_git("update-ref", ref, sha)

    def record_file_change(
        self,
        file_path: str | Path,
        content: bytes | None = None,
        *,
        action: str = "modified",
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Record a file change as a micro-commit.

        Args:
            file_path: Path to the file (relative to repo root)
            content: File content (None for deletion)
            action: Action type (modified, created, deleted)
            metadata: Additional metadata to include in commit message

        Returns:
            The commit SHA
        """
        rel_path = str(Path(file_path).relative_to(self.repo_root) if Path(file_path).is_absolute() else file_path)

        # Update tree state
        if content is not None and action != "deleted":
            # Hash and store content
            blob_sha = self._hash_object(content)
            self._current_tree[rel_path] = blob_sha
        elif rel_path in self._current_tree:
            # Remove from tree
            del self._current_tree[rel_path]

        if not self.auto_commit:
            return ""

        # Create micro-commit
        tree_sha = self._create_tree(self._current_tree)

        # Build commit message
        msg_parts = [f"[audit] {action}: {rel_path}"]
        if metadata:
            msg_parts.append(f"metadata: {json.dumps(metadata).decode()}")
        msg_parts.append(f"session: {self.session_id}")
        msg_parts.append(f"timestamp: {datetime.now(UTC).isoformat()}")
        message = "\n".join(msg_parts)

        commit_sha = self._create_commit(tree_sha, message, self._parent_sha)
        self._parent_sha = commit_sha

        # Update audit ref
        self._update_ref(self.audit_ref, commit_sha)

        log.debug("GitJournal.record_file_change path=%s action=%s sha=%s", rel_path, action, commit_sha[:8])

        return commit_sha

    def record_snapshot(self, message: str = "snapshot") -> str:
        """Create a snapshot commit of current working tree state.

        This reads the actual working directory and creates a commit
        representing the current state, useful for periodic snapshots.
        """
        # Get all tracked files
        result = shim_run(
            ["git", "ls-files", "-z"],
            cwd=self.repo_root,
            capture_output=True,
            timeout=30,
        )
        tracked_files = result.stdout.decode().split("\0")

        new_tree: dict[str, str] = {}

        for file_path in tracked_files:
            if not file_path.strip():
                continue
            full_path = self.repo_root / file_path
            if full_path.exists() and full_path.is_file():
                try:
                    content = full_path.read_bytes()
                    # Check if should be excluded (secrets check if enabled)
                    if not self.track_secrets and self._might_contain_secrets(file_path):
                        continue
                    blob_sha = self._hash_object(content)
                    new_tree[file_path] = blob_sha
                except Exception as e:
                    log.warning("GitJournal: failed to read %s: %s", file_path, e)

        # Create tree and commit
        tree_sha = self._create_tree(new_tree)
        commit_message = f"[audit] {message}\nsession: {self.session_id}\ntimestamp: {datetime.now(UTC).isoformat()}"

        commit_sha = self._create_commit(tree_sha, commit_message, self._parent_sha)
        self._parent_sha = commit_sha
        self._current_tree = new_tree

        # Update audit ref
        self._update_ref(self.audit_ref, commit_sha)

        log.info("GitJournal.record_snapshot sha=%s files=%d", commit_sha[:8], len(new_tree))
        return commit_sha

    def _might_contain_secrets(self, file_path: str) -> bool:
        """Check if file path suggests it might contain secrets."""
        secret_patterns = [
            ".env",
            ".secrets",
            "credentials",
            "api_key",
            "private_key",
            ".pem",
            ".key",
            "secrets.yaml",
            "secrets.json",
            ".netrc",
        ]
        lower_path = file_path.lower()
        return any(p in lower_path for p in secret_patterns)

    def get_audit_log(self) -> list[dict[str, Any]]:
        """Get the audit log for this session as a list of commits."""
        try:
            # Get all commits in this audit ref
            result = self._run_git("log", "--format=%H|%s|%ai", self.audit_ref)

            entries = []
            for line in result.split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|", 2)
                if len(parts) >= 3:
                    entries.append(
                        {
                            "sha": parts[0],
                            "message": parts[1],
                            "timestamp": parts[2],
                        }
                    )

            return entries
        except Exception as e:
            log.warning("GitJournal.get_audit_log failed: %s", e)
            return []

    def get_file_history(self, file_path: str) -> list[dict[str, Any]]:
        """Get the history of a specific file in this audit session."""
        rel_path = str(Path(file_path).relative_to(self.repo_root) if Path(file_path).is_absolute() else file_path)

        try:
            result = self._run_git("log", "--format=%H|%s|%ai", "--", rel_path, self.audit_ref)

            entries = []
            for line in result.split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|", 2)
                if len(parts) >= 3:
                    entries.append(
                        {
                            "sha": parts[0],
                            "message": parts[1],
                            "timestamp": parts[2],
                            "file": rel_path,
                        }
                    )

            return entries
        except Exception:
            return []

    def finalize_session(self, message: str = "session complete") -> str:
        """Finalize the audit session with a summary commit."""
        # Create final snapshot
        final_sha = self.record_snapshot(f"final: {message}")
        log.info("GitJournal.finalize_session sha=%s", final_sha[:8])
        return final_sha

    def delete_session(self) -> None:
        """Delete the audit ref for this session (cleanup)."""
        try:
            self._run_git("update-ref", "-d", self.audit_ref)
            log.info("GitJournal.delete_session ref=%s", self.audit_ref)
        except Exception as e:
            log.warning("GitJournal.delete_session failed: %s", e)

    @classmethod
    def list_sessions(cls, repo_root: Path | str) -> list[dict[str, Any]]:
        """List all audit sessions in a repository."""
        repo_root = Path(repo_root).resolve()

        try:
            result = shim_run(
                [
                    "git",
                    "for-each-ref",
                    "--format=%(refname)|%(objectname)|%(committerdate:iso)",
                    f"{cls.AUDIT_REF_PREFIX}/",
                ],
                cwd=repo_root,
                capture_output=True,
                text=True,
                timeout=30,
            )

            sessions = []
            for line in result.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) >= 3:
                    ref = parts[0]
                    session_id = ref.replace(f"{cls.AUDIT_REF_PREFIX}/", "")
                    sessions.append(
                        {
                            "session_id": session_id,
                            "ref": ref,
                            "sha": parts[1],
                            "last_commit": parts[2],
                        }
                    )

            return sessions
        except Exception as e:
            log.warning("GitJournal.list_sessions failed: %s", e)
            return []

    @classmethod
    def prune_old_sessions(cls, repo_root: Path | str, max_age_days: int = 30) -> int:
        """Prune audit sessions older than max_age_days."""
        repo_root = Path(repo_root).resolve()
        sessions = cls.list_sessions(repo_root)
        pruned = 0

        cutoff = datetime.now(UTC) - timedelta(days=max_age_days)

        def _prune_session(session: dict[str, str]) -> bool:
            try:
                last_commit = datetime.fromisoformat(session["last_commit"].replace(" ", "T"))
                if last_commit.replace(tzinfo=UTC) < cutoff:
                    # Delete the ref
                    shim_run(
                        ["git", "update-ref", "-d", session["ref"]],
                        cwd=repo_root,
                        capture_output=True,
                        timeout=10,
                    )
                    log.info("Pruned audit session %s", session["session_id"])
                    return True
            except Exception as e:
                log.warning("Failed to prune session %s: %s", session["session_id"], e)

            return False

        for session in sessions:
            if _prune_session(session):
                pruned += 1

        return pruned

    @classmethod
    def gc(cls, repo_root: Path | str, *, aggressive: bool = False) -> dict[str, Any]:
        """Run git gc on audit refs to pack loose objects.

        This class method garbage collects all audit refs in the repository,
        reducing storage usage by packing loose objects.

        Args:
            repo_root: Path to git repository root
            aggressive: If True, run more thorough garbage collection

        Returns:
            Dictionary with gc results including success status and statistics
        """
        repo_root = Path(repo_root).resolve()

        log.info("GitJournal.gc: starting gc on audit refs (aggressive=%s)", aggressive)

        results: dict[str, Any] = {
            "success": False,
            "sessions_found": 0,
            "sessions_collected": 0,
            "aggressive": aggressive,
        }

        try:
            # Get all audit sessions
            sessions = cls.list_sessions(repo_root)
            results["sessions_found"] = len(sessions)

            # Run git gc on the repository
            cmd = ["git", "gc"]
            if aggressive:
                cmd.append("--aggressive")
            cmd.extend(["--prune=now"])

            gc_result = shim_run(
                cmd,
                cwd=repo_root,
                capture_output=True,
                timeout=180,
            )

            results["gc_returncode"] = gc_result.returncode
            results["success"] = gc_result.returncode == 0

            if gc_result.stderr:
                results["stderr"] = gc_result.stderr.decode()[:500]  # Truncate for safety

            # Optionally prune old sessions
            pruned = cls.prune_old_sessions(repo_root, max_age_days=0)
            results["sessions_collected"] = pruned

            log.info(
                "GitJournal.gc: completed sessions=%d pruned=%d success=%s",
                len(sessions),
                pruned,
                results["success"],
            )

        except subprocess.TimeoutExpired:
            log.error("GitJournal.gc: timeout")
            results["error"] = "timeout"
        except Exception as e:
            log.error("GitJournal.gc: error %s", e)
            results["error"] = str(e)

        return results


# ---------------------------------------------------------------------------
# Enhanced GitJournal with P1 features
# ---------------------------------------------------------------------------


class GitJournalEnhanced(GitJournal):
    """Enhanced GitJournal with native secret scanner, real-time watching,
    cryptographic attestation, and performance optimizations.

    P1 Enhancements:
    - Native secret scanner integration (BKM-11)
    - Real-time file change detection (watchman/FSMonitor)
    - Cryptographic attestation (SHA-256)
    - Performance optimizations (batching, caching, async)
    """

    def __init__(
        self,
        repo_root: Path | str,
        session_id: str,
        *,
        track_secrets: bool = True,
        auto_commit: bool = True,
        enable_watching: bool = False,
        enable_attestation: bool = False,
        batch_size: int = 10,
        cache_size: int = 1000,
    ) -> None:
        """Initialize enhanced git journal.

        Args:
            repo_root: Path to git repository root
            session_id: Unique session identifier
            track_secrets: Whether to track/scrub secrets
            auto_commit: Whether to auto-commit on changes
            enable_watching: Enable real-time file watching
            enable_attestation: Enable cryptographic attestation
            batch_size: Number of changes to batch before commit
            cache_size: Maximum entries in LRU blob cache (default: 1000)
        """
        super().__init__(
            repo_root,
            session_id,
            track_secrets=track_secrets,
            auto_commit=False,  # We handle commit logic ourselves
        )

        self.enable_watching = enable_watching
        self.enable_attestation = enable_attestation
        self.batch_size = batch_size

        # CAS optimization: LRU blob cache with configurable size
        self._cache_size = cache_size
        self._blob_cache: OrderedDict[bytes, str] = OrderedDict()  # content hash -> sha
        self._cache_hits = 0
        self._cache_misses = 0

        # Content deduplication registry
        self._content_registry: dict[str, str] = {}  # dedup key -> blob sha

        # Pending changes for batching
        self._pending_changes: list[tuple[str, bytes | None, str, dict | None]] = []
        self._attestations: list[dict[str, Any]] = []

        # Real-time watching
        self._watcher: Any | None = None
        if enable_watching:
            self._init_watcher()

        # Native secret scanner
        self._native_scanner_available = self._check_native_scanner()

        log.info(
            "GitJournalEnhanced.init session=%s watching=%s attestation=%s native_scanner=%s cache_size=%d",
            session_id,
            enable_watching,
            enable_attestation,
            self._native_scanner_available,
            cache_size,
        )

    def _check_native_scanner(self) -> bool:
        """Check if native secret scanner is available."""
        try:
            result = shim_run(
                ["hook-dispatcher", "scan-secrets", "--help"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return False

    def _scrub_with_native_scanner(self, content: str) -> str:
        """Scrub secrets using native scanner if available."""
        if not self._native_scanner_available:
            return _scrub_secrets(content)

        try:
            result = shim_run(
                ["hook-dispatcher", "scan-secrets", "--stdin", "--format", "json"],
                input=content.encode(),
                capture_output=True,
                timeout=10,
            )

            if result.returncode == 0:
                import json as json_module

                findings = json_module.loads(result.stdout)
                scrubbed = content
                for finding in findings:
                    # Replace the matched secret with redaction
                    matched = finding.get("matched", "")
                    kind = finding.get("kind", "SECRET")
                    if matched:
                        scrubbed = scrubbed.replace(matched, f"<REDACTED_{kind}>")
                return scrubbed
        except Exception as e:
            log.debug("Native scanner failed, using regex: %s", e)

        return _scrub_secrets(content)

    def _init_watcher(self) -> None:
        """Initialize real-time file watcher."""
        try:
            # Try watchman first
            result = shim_run(
                ["watchman", "watch", str(self.repo_root)],
                capture_output=True,
                timeout=5,
            )
            if result.returncode == 0:
                self._watcher = "watchman"
                log.info("GitJournal: watchman initialized for %s", self.repo_root)
                return
        except FileNotFoundError as e:
            log.debug("GitJournal._init_watcher: watchman binary not available: %s", e)

        try:
            # Try fswatch as fallback
            result = shim_run(
                ["fswatch", "--version"],
                capture_output=True,
                timeout=5,
            )
            if result.returncode == 0:
                self._watcher = "fswatch"
                log.info("GitJournal: fswatch available")
                return
        except FileNotFoundError as e:
            log.debug("GitJournal._init_watcher: fswatch binary not available: %s", e)

        # Try FSMonitor (Git 2.37+)
        try:
            result = shim_run(
                ["git", "fsmonitor--daemon", "start"],
                cwd=self.repo_root,
                capture_output=True,
                timeout=5,
            )
            if result.returncode == 0:
                self._watcher = "fsmonitor"
                log.info("GitJournal: FSMonitor daemon started")
                return
        except Exception as e:
            log.debug("GitJournal._init_watcher: fsmonitor initialization failed: %s", e)

        log.warning("GitJournal: no file watcher available")
        self._watcher = None

    def start_watching(self) -> None:
        """Start watching for file changes in real-time."""
        if not self._watcher:
            log.warning("GitJournal: no watcher configured")
            return

        if self._watcher == "watchman":
            self._start_watchman()
        elif self._watcher == "fswatch":
            self._start_fswatch()
        elif self._watcher == "fsmonitor":
            self._start_fsmonitor()

    def _start_watchman(self) -> None:
        """Start watchman subscription."""
        import json as json_module
        import threading

        def watch_thread():
            try:
                # Subscribe to changes
                cmd = [
                    "watchman",
                    "-j",
                ]
                request = json_module.dumps(
                    {
                        "subscribe": str(self.repo_root),
                        "name": f"thegent-audit-{self.session_id}",
                        "fields": ["name", "type", "exists", "new", "ctime"],
                    }
                )

                proc = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                # Send subscription request
                proc.stdin.write(request + "\n")
                proc.stdin.flush()

                # Process events
                while True:
                    line = proc.stdout.readline()
                    if not line:
                        break

                    try:
                        event = json_module.loads(line)
                        if "files" in event:
                            for f in event["files"]:
                                self._handle_file_event(f["name"], "modified" if f.get("exists") else "deleted")
                    except Exception as e:
                        log.debug("Watchman parse error: %s", e)

            except Exception as e:
                log.error("Watchman thread error: %s", e)

        thread = threading.Thread(target=watch_thread, daemon=True)
        thread.start()
        log.info("GitJournal: watchman thread started")

    def _start_fswatch(self) -> None:
        """Start fswatch monitoring."""
        import threading

        def watch_thread():
            try:
                proc = subprocess.Popen(
                    ["fswatch", "-r", "-e", ".git", str(self.repo_root)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                while True:
                    line = proc.stdout.readline()
                    if not line:
                        break

                    file_path = line.strip()
                    if file_path:
                        self._handle_file_event(file_path, "modified")

            except Exception as e:
                log.error("fswatch thread error: %s", e)

        thread = threading.Thread(target=watch_thread, daemon=True)
        thread.start()
        log.info("GitJournal: fswatch thread started")

    def _start_fsmonitor(self) -> None:
        """Start Git FSMonitor daemon."""
        try:
            shim_run(
                ["git", "fsmonitor--daemon", "start"],
                cwd=self.repo_root,
                capture_output=True,
                timeout=10,
            )
            log.info("GitJournal: FSMonitor daemon started")
        except Exception as e:
            log.warning("FSMonitor start failed: %s", e)

    def _handle_file_event(self, file_path: str, action: str) -> None:
        """Handle a file change event from watcher."""
        try:
            full_path = Path(file_path)
            if not full_path.is_relative_to(self.repo_root):
                return

            rel_path = str(full_path.relative_to(self.repo_root))

            # Skip git internals
            if rel_path.startswith(".git/"):
                return

            if action == "deleted":
                self.record_file_change(rel_path, None, action="deleted")
            elif full_path.exists() and full_path.is_file():
                content = full_path.read_bytes()
                self.record_file_change(rel_path, content, action="modified")

        except Exception as e:
            log.debug("File event handling error: %s", e)

    def _get_dedup_key(self, content: bytes) -> str:
        """Generate a deduplication key from content.

        Uses SHA-256 of content for content-addressable dedup.
        """
        return hashlib.sha256(content).hexdigest()

    def _hash_object_cached(self, content: bytes) -> str:
        """Hash object with LRU caching, deduplication, and hit/miss tracking.

        CAS optimization:
        1. Check content deduplication registry first
        2. Check LRU cache (move to end on hit)
        3. Store in git DB and update cache (with LRU eviction)
        """
        # Step 1: Content deduplication - check if we already have this content
        dedup_key = self._get_dedup_key(content)
        if dedup_key in self._content_registry:
            existing_sha = self._content_registry[dedup_key]
            log.debug("CAS: dedup hit for key=%s sha=%s", dedup_key[:8], existing_sha[:8])
            return existing_sha

        # Step 2: Check LRU cache
        content_hash = hashlib.sha256(content).digest()

        if content_hash in self._blob_cache:
            # Cache hit - move to end (most recently used)
            self._blob_cache.move_to_end(content_hash)
            self._cache_hits += 1
            sha = self._blob_cache[content_hash]

            # Also register for deduplication
            self._content_registry[dedup_key] = sha

            log.debug("CAS: cache hit sha=%s", sha[:8])
            return sha

        self._cache_misses += 1

        # Step 3: Store in git DB
        sha = self._hash_object(content)

        # Evict oldest entry if cache is full (LRU eviction)
        if len(self._blob_cache) >= self._cache_size:
            oldest_key = next(iter(self._blob_cache))
            del self._blob_cache[oldest_key]
            log.debug("CAS: evicted oldest entry, cache_size=%d", len(self._blob_cache))

        # Add to LRU cache (at end = most recently used)
        self._blob_cache[content_hash] = sha

        # Register for content deduplication
        self._content_registry[dedup_key] = sha

        log.debug("CAS: cached new sha=%s cache_size=%d", sha[:8], len(self._blob_cache))
        return sha

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics for monitoring."""
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total_requests * 100) if total_requests > 0 else 0.0

        return {
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "hit_rate_percent": round(hit_rate, 2),
            "cache_size": len(self._blob_cache),
            "cache_max": self._cache_size,
            "dedup_registry_size": len(self._content_registry),
        }

    def clear_cache(self) -> None:
        """Clear the LRU blob cache and deduplication registry."""
        self._blob_cache.clear()
        self._content_registry.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        log.info("GitJournalEnhanced: cache cleared")

    def _create_attestation(self, commit_sha: str, content_hash: str) -> dict[str, Any]:
        """Create cryptographic attestation for a commit."""
        timestamp = datetime.now(UTC).isoformat()

        attestation = {
            "version": "1.0",
            "commit_sha": commit_sha,
            "content_hash": content_hash,
            "timestamp": timestamp,
            "session_id": self.session_id,
            "attestor": "thegent-audit",
            "algorithm": "SHA-256",
        }

        # In production, this would use Sigstore for actual signing
        # For now, we create a verifiable hash chain
        attestation_data = f"{commit_sha}:{content_hash}:{timestamp}:{self.session_id}"
        attestation["signature"] = hashlib.sha256(attestation_data.encode()).hexdigest()

        return attestation

    def record_file_change(
        self,
        file_path: str | Path,
        content: bytes | None = None,
        *,
        action: str = "modified",
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Record a file change with batching and attestation.

        Overrides parent to add:
        - Native secret scanning
        - Batching for performance
        - Cryptographic attestation
        """
        rel_path = str(Path(file_path).relative_to(self.repo_root) if Path(file_path).is_absolute() else file_path)

        # Scrub secrets if content provided
        _content_hash = ""
        if content is not None and self.track_secrets:
            content_str = content.decode("utf-8", errors="replace")
            scrubbed = self._scrub_with_native_scanner(content_str)
            content = scrubbed.encode("utf-8")
            _content_hash = hashlib.sha256(content).hexdigest()

        # Add to pending changes
        self._pending_changes.append((rel_path, content, action, metadata))

        # Check if we should flush batch
        if len(self._pending_changes) >= self.batch_size:
            return self._flush_batch()

        # If not batching, commit immediately
        if self.auto_commit or len(self._pending_changes) == 1:
            return self._flush_batch()

        return ""

    def _flush_batch(self) -> str:
        """Flush pending changes as a single commit."""
        if not self._pending_changes:
            return ""

        # Process all pending changes
        for rel_path, content, action, _metadata in self._pending_changes:
            if content is not None and action != "deleted":
                blob_sha = self._hash_object_cached(content)
                self._current_tree[rel_path] = blob_sha
            elif rel_path in self._current_tree:
                del self._current_tree[rel_path]

        # Create batch commit
        tree_sha = self._create_tree(self._current_tree)

        # Build commit message with all changes
        changes_summary = [f"  - {path} ({action})" for path, _, action, _ in self._pending_changes]
        msg_parts = [
            f"[audit] batch: {len(self._pending_changes)} changes",
            f"session: {self.session_id}",
            f"timestamp: {datetime.now(UTC).isoformat()}",
            "changes:",
            *changes_summary,
        ]
        message = "\n".join(msg_parts)

        commit_sha = self._create_commit(tree_sha, message, self._parent_sha)
        self._parent_sha = commit_sha

        # Update audit ref
        self._update_ref(self.audit_ref, commit_sha)

        # Create attestation if enabled
        if self.enable_attestation:
            content_hash = hashlib.sha256(str(self._current_tree).encode()).hexdigest()
            attestation = self._create_attestation(commit_sha, content_hash)
            self._attestations.append(attestation)

        # Clear pending changes
        pending_count = len(self._pending_changes)
        self._pending_changes.clear()

        log.info(
            "GitJournalEnhanced._flush_batch sha=%s changes=%d attestation=%s",
            commit_sha[:8],
            pending_count,
            self.enable_attestation,
        )

        return commit_sha

    def get_attestations(self) -> list[dict[str, Any]]:
        """Get all attestations for this session."""
        return self._attestations.copy()

    def verify_attestation(self, attestation: dict[str, Any]) -> bool:
        """Verify an attestation's integrity."""
        # Reconstruct attestation data
        attestation_data = (
            f"{attestation['commit_sha']}:{attestation['content_hash']}:"
            f"{attestation['timestamp']}:{attestation['session_id']}"
        )

        expected_sig = hashlib.sha256(attestation_data.encode()).hexdigest()

        return attestation.get("signature") == expected_sig

    def finalize_session(self, message: str = "session complete") -> str:
        """Finalize session with attestation summary."""
        # Flush any remaining changes
        if self._pending_changes:
            self._flush_batch()

        # Create final snapshot
        final_sha = super().record_snapshot(f"final: {message}")

        # Create final attestation
        if self.enable_attestation:
            final_attestation = self._create_attestation(final_sha, "final")
            self._attestations.append(final_attestation)

        log.info(
            "GitJournalEnhanced.finalize_session sha=%s attestations=%d",
            final_sha[:8],
            len(self._attestations),
        )

        return final_sha

    def gc(self, *, aggressive: bool = False) -> dict[str, Any]:
        """Run git gc to pack loose objects in the audit ref namespace.

        Args:
            aggressive: If True, run more thorough garbage collection

        Returns:
            Dictionary with gc results
        """
        log.info("GitJournalEnhanced.gc: starting gc (aggressive=%s)", aggressive)

        try:
            # Run git gc on the repository
            cmd = ["git", "gc"]
            if aggressive:
                cmd.append("--aggressive")
            cmd.extend(["--prune=now", "--quiet"])

            result = shim_run(
                cmd,
                cwd=self.repo_root,
                capture_output=True,
                timeout=120,
            )

            success = result.returncode == 0
            stderr = result.stderr.decode() if result.stderr else ""

            log.info(
                "GitJournalEnhanced.gc: completed success=%s stderr=%s",
                success,
                stderr[:200] if stderr else "",
            )

            return {
                "success": success,
                "aggressive": aggressive,
                "stderr": stderr,
            }

        except subprocess.TimeoutExpired:
            log.error("GitJournalEnhanced.gc: timeout")
            return {"success": False, "aggressive": aggressive, "error": "timeout"}
        except Exception as e:
            log.error("GitJournalEnhanced.gc: error %s", e)
            return {"success": False, "aggressive": aggressive, "error": str(e)}

    def optimize_storage(self) -> dict[str, Any]:
        """Optimize storage by running git maintenance and repacking.

        This method performs comprehensive storage optimization:
        1. Repacks objects into packfiles
        2. Runs git gc
        3. Clears stale cache entries
        4. Returns optimization statistics

        Returns:
            Dictionary with optimization results
        """
        log.info("GitJournalEnhanced.optimize_storage: starting")

        results: dict[str, Any] = {
            "success": False,
            "cache_before": len(self._blob_cache),
            "dedup_before": len(self._content_registry),
        }

        try:
            # Step 1: Run git repack
            repack_result = shim_run(
                ["git", "repack", "-ad", "--quiet"],
                cwd=self.repo_root,
                capture_output=True,
                timeout=120,
            )
            results["repack_success"] = repack_result.returncode == 0

            # Step 2: Run git gc
            gc_result = self.gc(aggressive=False)
            results["gc_success"] = gc_result.get("success", False)

            # Step 3: Prune unreachable objects
            prune_result = shim_run(
                ["git", "prune", "--expire=now", "--verbose"],
                cwd=self.repo_root,
                capture_output=True,
                timeout=60,
            )
            results["prune_success"] = prune_result.returncode == 0

            # Step 4: Clear stale cache entries (optional optimization)
            stale_removed = 0
            if len(self._blob_cache) > self._cache_size:
                stale_removed = len(self._blob_cache) - self._cache_size
                # Keep only the most recent entries
                while len(self._blob_cache) > self._cache_size:
                    self._blob_cache.popitem(last=False)

            results["stale_entries_removed"] = stale_removed

            # Get cache stats after optimization
            cache_stats = self.get_cache_stats()
            results["cache_after"] = len(self._blob_cache)
            results["dedup_after"] = len(self._content_registry)
            results["cache_stats"] = cache_stats
            results["success"] = True

            log.info(
                "GitJournalEnhanced.optimize_storage: completed "
                "cache_before=%d cache_after=%d dedup_before=%d dedup_after=%d",
                results["cache_before"],
                results["cache_after"],
                results["dedup_before"],
                results["dedup_after"],
            )

        except Exception as e:
            log.error("GitJournalEnhanced.optimize_storage: error %s", e)
            results["error"] = str(e)

        return results

    def get_performance_stats(self) -> dict[str, Any]:
        """Get performance statistics including cache hit/miss tracking."""
        cache_stats = self.get_cache_stats()

        return {
            "blob_cache_size": len(self._blob_cache),
            "blob_cache_max": self._cache_size,
            "cache_hits": cache_stats["cache_hits"],
            "cache_misses": cache_stats["cache_misses"],
            "cache_hit_rate_percent": cache_stats["hit_rate_percent"],
            "dedup_registry_size": len(self._content_registry),
            "pending_changes": len(self._pending_changes),
            "attestations": len(self._attestations),
            "native_scanner": self._native_scanner_available,
            "watcher": self._watcher,
            "batch_size": self.batch_size,
        }


# ---------------------------------------------------------------------------
# Async GitJournal for high-performance scenarios
# ---------------------------------------------------------------------------


class GitJournalAsync:
    """Async wrapper around GitJournal for high-performance scenarios.

    Provides async API for non-blocking git operations.
    """

    _executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="git-journal-")

    def __init__(self, journal: GitJournal | GitJournalEnhanced):
        """Wrap a journal instance for async operations."""
        self._journal = journal

    @classmethod
    def create(
        cls,
        repo_root: Path | str,
        session_id: str,
        **kwargs,
    ) -> "GitJournalAsync":
        """Create a new async journal."""
        enhanced = kwargs.pop("enhanced", True)
        if enhanced:
            journal = GitJournalEnhanced(repo_root, session_id, **kwargs)
        else:
            journal = GitJournal(repo_root, session_id, **kwargs)
        return cls(journal)

    async def record_file_change(
        self,
        file_path: str | Path,
        content: bytes | None = None,
        **kwargs,
    ) -> str:
        """Record file change asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self._journal.record_file_change,
            file_path,
            content,
        )

    async def record_snapshot(self, message: str = "snapshot") -> str:
        """Create snapshot asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self._journal.record_snapshot,
            message,
        )

    async def get_audit_log(self) -> list[dict[str, Any]]:
        """Get audit log asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, self._journal.get_audit_log)

    async def finalize_session(self, message: str = "session complete") -> str:
        """Finalize session asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self._journal.finalize_session,
            message,
        )

    def __getattr__(self, name):
        """Delegate to wrapped journal."""
        return getattr(self._journal, name)


__all__ = [
    "AuditEntry",
    "GitJournal",
    "GitJournalAsync",
    "GitJournalEnhanced",
    "ShadowAuditGit",
]

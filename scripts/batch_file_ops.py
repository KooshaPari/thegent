#!/usr/bin/env python3
"""
Batch File Operations Module

Provides efficient batch operations for reading, writing, editing, and deleting files
with atomic transactions, rollback support, and error recovery.

This module reduces tool call verbosity by 3-5x when performing multi-file operations,
which are common in refactoring, spec generation, and agent-driven automation.

Usage:
    from batch_file_ops import batch_read_files, batch_write_files, batch_edit_files

    # Read multiple files atomically
    files = batch_read_files(["/path/to/file1.py", "/path/to/file2.py"])

    # Write multiple files atomically
    batch_write_files([
        ("/path/to/file1.py", "content 1"),
        ("/path/to/file2.py", "content 2"),
    ])

    # Edit multiple files with search/replace
    batch_edit_files([
        ("/path/to/file1.py", "old_text", "new_text"),
        ("/path/to/file2.py", "search", "replace"),
    ])

    # Delete multiple files atomically
    batch_delete_files(["/path/to/file1.py", "/path/to/file2.py"])
"""

import orjson as json
import shutil
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class BatchOperation:
    """Represents a single file operation in a batch."""

    file_path: str
    operation_type: str  # 'read', 'write', 'edit', 'delete'
    success: bool
    error_message: str | None = None
    result: Any | None = None
    timestamp: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class BatchOperationResult:
    """Result of a batch operation."""

    total: int
    successful: int
    failed: int
    operations: list[BatchOperation]
    errors: list[str]
    backup_dir: str | None = None
    duration_ms: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "total": self.total,
            "successful": self.successful,
            "failed": self.failed,
            "operations": [op.to_dict() for op in self.operations],
            "errors": self.errors,
            "backup_dir": self.backup_dir,
            "duration_ms": self.duration_ms,
        }


class BatchFileOps:
    """Manages batch file operations with atomic transactions and rollback support."""

    def __init__(self, create_backups: bool = True, verbose: bool = False):
        """
        Initialize batch file operations manager.

        Args:
            create_backups: If True, create backups before modifications (default: True)
            verbose: If True, log detailed operation information (default: False)
        """
        self.create_backups = create_backups
        self.verbose = verbose
        self.backup_dir: Path | None = None
        self.operations: list[BatchOperation] = []
        self.start_time: float | None = None

    def _log(self, message: str) -> None:
        """Log message if verbose mode is enabled."""
        if self.verbose:
            timestamp = datetime.now().isoformat()
            print(f"[{timestamp}] {message}", file=sys.stderr)

    def _create_backup_dir(self) -> Path:
        """Create backup directory if needed."""
        if not self.create_backups or self.backup_dir:
            return self.backup_dir or Path("/tmp")

        backup_dir = Path.home() / ".thegent" / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir = backup_dir
        self._log(f"Created backup directory: {self.backup_dir}")
        return self.backup_dir

    def _backup_file(self, file_path: Path) -> Path | None:
        """Create backup of a single file."""
        if not file_path.exists():
            return None

        backup_dir = self._create_backup_dir()
        # Preserve relative path structure in backup
        relative_path = file_path.relative_to("/") if file_path.is_absolute() else file_path
        backup_path = backup_dir / relative_path

        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_path)
        self._log(f"Backed up: {file_path} -> {backup_path}")
        return backup_path

    def _restore_from_backup(self, file_path: Path, backup_path: Path) -> bool:
        """Restore file from backup."""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_path, file_path)
            self._log(f"Restored: {file_path} from {backup_path}")
            return True
        except Exception as e:
            self._log(f"Failed to restore {file_path}: {e}")
            return False

    def batch_read_files(
        self,
        file_paths: list[str],
        offsets: dict[str, int] | None = None,
        limits: dict[str, int] | None = None,
        encoding: str = "utf-8",
    ) -> dict[str, str]:
        """
        Read multiple files atomically.

        Args:
            file_paths: List of file paths to read
            offsets: Optional dict mapping path -> offset line number
            limits: Optional dict mapping path -> limit line count
            encoding: File encoding (default: utf-8)

        Returns:
            Dictionary mapping file paths to contents
            Raises BatchFileOpsError if any read fails

        Raises:
            BatchFileOpsError: If any file cannot be read
        """
        self.start_time = time.time()
        self.operations = []
        offsets = offsets or {}
        limits = limits or {}
        result = {}
        errors = []

        for file_path_str in file_paths:
            try:
                file_path = Path(file_path_str)

                if not file_path.exists():
                    error_msg = f"File not found: {file_path}"
                    errors.append(error_msg)
                    self.operations.append(
                        BatchOperation(
                            file_path=file_path_str,
                            operation_type="read",
                            success=False,
                            error_message=error_msg,
                            timestamp=datetime.now().isoformat(),
                        )
                    )
                    continue

                offset = offsets.get(file_path_str, 0)
                limit = limits.get(file_path_str)

                if offset > 0 or limit:
                    # Read only needed lines
                    content_lines = []
                    with file_path.open(encoding=encoding) as f:
                        for _ in range(max(0, offset - 1)):
                            try:
                                next(f)
                            except StopIteration:
                                break
                        for lines_read, line in enumerate(f):
                            if limit and lines_read >= limit:
                                break
                            content_lines.append(line.rstrip("\n\r"))
                    content = "\n".join(content_lines)
                else:
                    content = file_path.read_text(encoding=encoding)

                result[file_path_str] = content
                self.operations.append(
                    BatchOperation(
                        file_path=file_path_str,
                        operation_type="read",
                        success=True,
                        result={"size": len(content), "lines": len(content.split("\n"))},
                        timestamp=datetime.now().isoformat(),
                    )
                )
                self._log(f"Read: {file_path} ({len(content)} bytes)")

            except Exception as e:
                error_msg = f"Error reading {file_path_str}: {e!s}"
                errors.append(error_msg)
                self.operations.append(
                    BatchOperation(
                        file_path=file_path_str,
                        operation_type="read",
                        success=False,
                        error_message=error_msg,
                        timestamp=datetime.now().isoformat(),
                    )
                )

        if errors:
            raise BatchFileOpsError(
                f"Failed to read {len(errors)} file(s)",
                errors=errors,
                result=BatchOperationResult(
                    total=len(file_paths),
                    successful=len(result),
                    failed=len(errors),
                    operations=self.operations,
                    errors=errors,
                    duration_ms=self._get_duration_ms(),
                ),
            )

        return result

    def batch_write_files(
        self,
        operations: list[tuple[str, str]],
        encoding: str = "utf-8",
        atomic: bool = True,
    ) -> BatchOperationResult:
        """
        Write multiple files atomically.

        Args:
            operations: List of (file_path, content) tuples
            encoding: File encoding (default: utf-8)
            atomic: If True, rollback all files on any failure (default: True)

        Returns:
            BatchOperationResult with operation details

        Raises:
            BatchFileOpsError: If atomic=True and any write fails
        """
        self.start_time = time.time()
        self.operations = []
        backups: dict[str, Path] = {}
        written_files: list[Path] = []
        errors = []

        try:
            # Create backups for all existing files
            for file_path_str, _ in operations:
                file_path = Path(file_path_str)
                backup_path = self._backup_file(file_path)
                if backup_path:
                    backups[file_path_str] = backup_path

            # Write all files
            for file_path_str, content in operations:
                try:
                    file_path = Path(file_path_str)
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(content, encoding=encoding)
                    written_files.append(file_path)

                    self.operations.append(
                        BatchOperation(
                            file_path=file_path_str,
                            operation_type="write",
                            success=True,
                            result={"size": len(content), "lines": len(content.split("\n"))},
                            timestamp=datetime.now().isoformat(),
                        )
                    )
                    self._log(f"Wrote: {file_path} ({len(content)} bytes)")

                except Exception as e:
                    error_msg = f"Error writing {file_path_str}: {e!s}"
                    errors.append(error_msg)
                    self.operations.append(
                        BatchOperation(
                            file_path=file_path_str,
                            operation_type="write",
                            success=False,
                            error_message=error_msg,
                            timestamp=datetime.now().isoformat(),
                        )
                    )

                    if atomic:
                        # Rollback on error
                        self._log(f"Atomic operation failed. Rolling back {len(written_files)} files...")
                        for written_path in written_files:
                            written_str = str(written_path)
                            if written_str in backups:
                                self._restore_from_backup(written_path, backups[written_str])
                            elif written_path.exists():
                                written_path.unlink()
                        raise

            return BatchOperationResult(
                total=len(operations),
                successful=len(written_files),
                failed=len(errors),
                operations=self.operations,
                errors=errors,
                backup_dir=str(self.backup_dir) if self.backup_dir else None,
                duration_ms=self._get_duration_ms(),
            )

        except Exception as e:
            if atomic and errors:
                raise BatchFileOpsError(
                    f"Atomic write failed after {len(written_files)} file(s)",
                    errors=errors,
                    result=BatchOperationResult(
                        total=len(operations),
                        successful=len(written_files),
                        failed=len(errors),
                        operations=self.operations,
                        errors=errors,
                        backup_dir=str(self.backup_dir) if self.backup_dir else None,
                        duration_ms=self._get_duration_ms(),
                    ),
                )
            raise

    def batch_edit_files(
        self,
        operations: list[tuple[str, str, str]],
        encoding: str = "utf-8",
        atomic: bool = True,
        count: int = 1,
    ) -> BatchOperationResult:
        """
        Edit multiple files with search/replace operations.

        Args:
            operations: List of (file_path, search_text, replace_text) tuples
            encoding: File encoding (default: utf-8)
            atomic: If True, rollback all edits on any failure (default: True)
            count: Number of replacements per file (default: 1, -1 for all)

        Returns:
            BatchOperationResult with operation details

        Raises:
            BatchFileOpsError: If atomic=True and any edit fails
        """
        self.start_time = time.time()
        self.operations = []
        backups: dict[str, Path] = {}
        edited_files: list[Path] = []
        errors = []

        try:
            # Create backups for all files
            for file_path_str, _, _ in operations:
                file_path = Path(file_path_str)
                backup_path = self._backup_file(file_path)
                if backup_path:
                    backups[file_path_str] = backup_path

            # Edit all files
            for file_path_str, search_text, replace_text in operations:
                try:
                    file_path = Path(file_path_str)

                    if not file_path.exists():
                        raise FileNotFoundError(f"File not found: {file_path}")

                    content = file_path.read_text(encoding=encoding)
                    original_content = content

                    # Perform replacement
                    if count == -1:
                        new_content = content.replace(search_text, replace_text)
                        replacements = content.count(search_text)
                    else:
                        new_content = content.replace(search_text, replace_text, count)
                        replacements = min(count, content.count(search_text))

                    if new_content == original_content:
                        error_msg = f"Search text not found in {file_path_str}"
                        errors.append(error_msg)
                        self.operations.append(
                            BatchOperation(
                                file_path=file_path_str,
                                operation_type="edit",
                                success=False,
                                error_message=error_msg,
                                timestamp=datetime.now().isoformat(),
                            )
                        )
                        if atomic:
                            raise ValueError(error_msg)
                        continue

                    file_path.write_text(new_content, encoding=encoding)
                    edited_files.append(file_path)

                    self.operations.append(
                        BatchOperation(
                            file_path=file_path_str,
                            operation_type="edit",
                            success=True,
                            result={"replacements": replacements, "size": len(new_content)},
                            timestamp=datetime.now().isoformat(),
                        )
                    )
                    self._log(f"Edited: {file_path} ({replacements} replacement(s))")

                except Exception as e:
                    error_msg = f"Error editing {file_path_str}: {e!s}"
                    errors.append(error_msg)
                    self.operations.append(
                        BatchOperation(
                            file_path=file_path_str,
                            operation_type="edit",
                            success=False,
                            error_message=error_msg,
                            timestamp=datetime.now().isoformat(),
                        )
                    )

                    if atomic:
                        # Rollback on error
                        self._log(f"Atomic operation failed. Rolling back {len(edited_files)} files...")
                        for edited_path in edited_files:
                            edited_str = str(edited_path)
                            if edited_str in backups:
                                self._restore_from_backup(edited_path, backups[edited_str])
                        raise

            return BatchOperationResult(
                total=len(operations),
                successful=len(edited_files),
                failed=len(errors),
                operations=self.operations,
                errors=errors,
                backup_dir=str(self.backup_dir) if self.backup_dir else None,
                duration_ms=self._get_duration_ms(),
            )

        except Exception as e:
            if atomic and errors:
                raise BatchFileOpsError(
                    f"Atomic edit failed after {len(edited_files)} file(s)",
                    errors=errors,
                    result=BatchOperationResult(
                        total=len(operations),
                        successful=len(edited_files),
                        failed=len(errors),
                        operations=self.operations,
                        errors=errors,
                        backup_dir=str(self.backup_dir) if self.backup_dir else None,
                        duration_ms=self._get_duration_ms(),
                    ),
                )
            raise

    def batch_delete_files(
        self,
        file_paths: list[str],
        atomic: bool = True,
    ) -> BatchOperationResult:
        """
        Delete multiple files atomically.

        Args:
            file_paths: List of file paths to delete
            atomic: If True, abort if any delete fails (default: True)

        Returns:
            BatchOperationResult with operation details

        Raises:
            BatchFileOpsError: If atomic=True and any delete fails
        """
        self.start_time = time.time()
        self.operations = []
        backups: dict[str, Path] = {}
        deleted_files: list[Path] = []
        errors = []

        try:
            # Create backups for all files
            for file_path_str in file_paths:
                file_path = Path(file_path_str)
                backup_path = self._backup_file(file_path)
                if backup_path:
                    backups[file_path_str] = backup_path

            # Delete all files
            for file_path_str in file_paths:
                try:
                    file_path = Path(file_path_str)

                    if not file_path.exists():
                        error_msg = f"File not found: {file_path}"
                        errors.append(error_msg)
                        self.operations.append(
                            BatchOperation(
                                file_path=file_path_str,
                                operation_type="delete",
                                success=False,
                                error_message=error_msg,
                                timestamp=datetime.now().isoformat(),
                            )
                        )
                        if atomic:
                            raise FileNotFoundError(error_msg)
                        continue

                    file_path.unlink()
                    deleted_files.append(file_path)

                    self.operations.append(
                        BatchOperation(
                            file_path=file_path_str,
                            operation_type="delete",
                            success=True,
                            timestamp=datetime.now().isoformat(),
                        )
                    )
                    self._log(f"Deleted: {file_path}")

                except Exception as e:
                    error_msg = f"Error deleting {file_path_str}: {e!s}"
                    errors.append(error_msg)
                    self.operations.append(
                        BatchOperation(
                            file_path=file_path_str,
                            operation_type="delete",
                            success=False,
                            error_message=error_msg,
                            timestamp=datetime.now().isoformat(),
                        )
                    )

                    if atomic:
                        # Restore on error
                        self._log(f"Atomic operation failed. Restoring {len(deleted_files)} files...")
                        for deleted_path in deleted_files:
                            deleted_str = str(deleted_path)
                            if deleted_str in backups:
                                self._restore_from_backup(deleted_path, backups[deleted_str])
                        raise

            return BatchOperationResult(
                total=len(file_paths),
                successful=len(deleted_files),
                failed=len(errors),
                operations=self.operations,
                errors=errors,
                backup_dir=str(self.backup_dir) if self.backup_dir else None,
                duration_ms=self._get_duration_ms(),
            )

        except Exception as e:
            if atomic and errors:
                raise BatchFileOpsError(
                    f"Atomic delete failed after {len(deleted_files)} file(s)",
                    errors=errors,
                    result=BatchOperationResult(
                        total=len(file_paths),
                        successful=len(deleted_files),
                        failed=len(errors),
                        operations=self.operations,
                        errors=errors,
                        backup_dir=str(self.backup_dir) if self.backup_dir else None,
                        duration_ms=self._get_duration_ms(),
                    ),
                )
            raise

    def _get_duration_ms(self) -> float | None:
        """Get operation duration in milliseconds."""
        if self.start_time is None:
            return None
        return (time.time() - self.start_time) * 1000


class BatchFileOpsError(Exception):
    """Exception raised by batch file operations."""

    def __init__(self, message: str, errors: list[str] | None = None, result=None):
        super().__init__(message)
        self.errors = errors or []
        self.result = result


# Module-level convenience functions
def batch_read_files(
    file_paths: list[str],
    offsets: dict[str, int] | None = None,
    limits: dict[str, int] | None = None,
    encoding: str = "utf-8",
    verbose: bool = False,
) -> dict[str, str]:
    """
    Read multiple files in a single operation.

    Args:
        file_paths: List of file paths to read
        offsets: Optional dict mapping path -> offset line number
        limits: Optional dict mapping path -> limit line count
        encoding: File encoding (default: utf-8)
        verbose: Enable verbose logging (default: False)

    Returns:
        Dictionary mapping file paths to contents
    """
    ops = BatchFileOps(create_backups=False, verbose=verbose)
    return ops.batch_read_files(file_paths, offsets=offsets, limits=limits, encoding=encoding)


def batch_write_files(
    operations: list[tuple[str, str]],
    encoding: str = "utf-8",
    atomic: bool = True,
    verbose: bool = False,
) -> BatchOperationResult:
    """
    Write multiple files in a single operation.

    Args:
        operations: List of (file_path, content) tuples
        encoding: File encoding (default: utf-8)
        atomic: If True, rollback all files on any failure (default: True)
        verbose: Enable verbose logging (default: False)

    Returns:
        BatchOperationResult with operation details
    """
    ops = BatchFileOps(create_backups=True, verbose=verbose)
    return ops.batch_write_files(operations, encoding=encoding, atomic=atomic)


def batch_edit_files(
    operations: list[tuple[str, str, str]],
    encoding: str = "utf-8",
    atomic: bool = True,
    count: int = 1,
    verbose: bool = False,
) -> BatchOperationResult:
    """
    Edit multiple files with search/replace in a single operation.

    Args:
        operations: List of (file_path, search_text, replace_text) tuples
        encoding: File encoding (default: utf-8)
        atomic: If True, rollback all edits on any failure (default: True)
        count: Number of replacements per file (default: 1, -1 for all)
        verbose: Enable verbose logging (default: False)

    Returns:
        BatchOperationResult with operation details
    """
    ops = BatchFileOps(create_backups=True, verbose=verbose)
    return ops.batch_edit_files(operations, encoding=encoding, atomic=atomic, count=count)


def batch_delete_files(
    file_paths: list[str],
    atomic: bool = True,
    verbose: bool = False,
) -> BatchOperationResult:
    """
    Delete multiple files in a single operation.

    Args:
        file_paths: List of file paths to delete
        atomic: If True, abort if any delete fails (default: True)
        verbose: Enable verbose logging (default: False)

    Returns:
        BatchOperationResult with operation details
    """
    ops = BatchFileOps(create_backups=True, verbose=verbose)
    return ops.batch_delete_files(file_paths, atomic=atomic)


def normalize_path(path: str, base: str | None = None) -> str:
    """
    Normalize file path to absolute form.

    Args:
        path: File path (relative or absolute)
        base: Optional base path for relative paths

    Returns:
        Absolute normalized path
    """
    p = Path(path).expanduser()
    if not p.is_absolute() and base:
        p = Path(base) / p
    return str(p.resolve())


if __name__ == "__main__":
    # CLI interface for testing
    import argparse

    parser = argparse.ArgumentParser(description="Batch file operations tool")
    parser.add_argument("--read", nargs="+", help="Read files")
    parser.add_argument("--write", nargs="+", help="Write files (pairs of path,content)")
    parser.add_argument("--edit", nargs="+", help="Edit files (triples of path,search,replace)")
    parser.add_argument("--delete", nargs="+", help="Delete files")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    try:
        if args.read:
            files = batch_read_files(args.read, verbose=args.verbose)
            if args.json:
                print(
                    json.dumps(
                        {k: v[:100] + "..." if len(v).decode().decode() > 100 else v for k, v in files.items()},
                        indent=2,
                    )
                )
            else:
                for path, content in files.items():
                    print(f"{path}: {len(content)} bytes")

        elif args.write and len(args.write) % 2 == 0:
            ops_list = [(args.write[i], args.write[i + 1]) for i in range(0, len(args.write), 2)]
            result = batch_write_files(ops_list, verbose=args.verbose)
            if args.json:
                print(json.dumps(result.to_dict().decode().decode(), indent=2))
            else:
                print(f"Wrote {result.successful}/{result.total} files")

        elif args.edit and len(args.edit) % 3 == 0:
            ops_list = [(args.edit[i], args.edit[i + 1], args.edit[i + 2]) for i in range(0, len(args.edit), 3)]
            result = batch_edit_files(ops_list, verbose=args.verbose)
            if args.json:
                print(json.dumps(result.to_dict().decode().decode(), indent=2))
            else:
                print(f"Edited {result.successful}/{result.total} files")

        elif args.delete:
            result = batch_delete_files(args.delete, verbose=args.verbose)
            if args.json:
                print(json.dumps(result.to_dict().decode().decode(), indent=2))
            else:
                print(f"Deleted {result.successful}/{result.total} files")

    except BatchFileOpsError as e:
        print(f"Error: {e}", file=sys.stderr)
        if e.result and args.json:
            print(json.dumps(e.result.to_dict().decode().decode(), indent=2), file=sys.stderr)
        sys.exit(1)

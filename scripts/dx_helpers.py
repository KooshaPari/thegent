#!/usr/bin/env python3
"""
DX/UX/AX Helper Utilities

Reduces verbosity and complexity of common operations.
"""

import sys
from pathlib import Path


def check_imports(modules: list[str], verbose: bool = False) -> bool:
    """Check if modules can be imported (replaces verbose python3 -c commands).

    Args:
        modules: List of module names to test
        verbose: Print success messages

    Returns:
        True if all imports succeed
    """
    failed = []
    for module in modules:
        try:
            __import__(module)
            if verbose:
                print(f"✅ {module}")
        except ImportError as e:
            failed.append((module, str(e)))
            if verbose:
                print(f"❌ {module}: {e}")

    if failed:
        if verbose:
            print(f"\nFailed imports: {len(failed)}/{len(modules)}")
        return False

    if verbose:
        print(f"✅ All {len(modules)} imports successful")
    return True


def batch_file_read(files: list[Path | str], max_size: int = 1000000) -> dict[str, str]:
    """Read multiple files efficiently (reduces tool calls).

    Args:
        files: List of file paths
        max_size: Maximum file size to read (bytes)

    Returns:
        Dict mapping file path -> content
    """
    results = {}
    for file_path in files:
        path = Path(file_path)
        if not path.exists():
            results[str(path)] = None
            continue

        if path.stat().st_size > max_size:
            results[str(path)] = f"<FILE_TOO_LARGE: {path.stat().st_size} bytes>"
            continue

        try:
            results[str(path)] = path.read_text(encoding="utf-8")
        except Exception as e:
            results[str(path)] = f"<ERROR: {e}>"

    return results


def batch_file_write(updates: dict[str, str]) -> dict[str, bool]:
    """Write multiple files efficiently (reduces tool calls).

    Args:
        updates: Dict mapping file path -> content

    Returns:
        Dict mapping file path -> success status
    """
    results = {}
    for file_path, content in updates.items():
        try:
            Path(file_path).write_text(content, encoding="utf-8")
            results[file_path] = True
        except Exception as e:
            results[file_path] = False
            print(f"Error writing {file_path}: {e}", file=sys.stderr)

    return results


def normalize_path(path: str | Path) -> Path:
    """Normalize path handling (consistent across operations).

    Args:
        path: Path string or Path object

    Returns:
        Normalized Path object
    """
    return Path(path).expanduser().resolve()


def get_workstream_items(count: int = 5, priority: str | None = "P1") -> list[dict]:
    """Get next workstream items (wrapper around workstream_helper).

    Args:
        count: Number of items to return
        priority: Filter by priority

    Returns:
        List of workstream items
    """
    try:
        from scripts.workstream_helper import get_next_items

        return get_next_items(count=count, priority=priority)
    except ImportError:
        # Fallback: read WORK_STREAM.md directly
        ws_path = Path(__file__).parent.parent / "docs" / "reference" / "WORK_STREAM.md"
        if not ws_path.exists():
            return []

        # Simple parser (basic implementation)
        content = ws_path.read_text()
        items = []
        in_backlog = False

        for line in content.split("\n"):
            if "## BACKLOG" in line:
                in_backlog = True
            elif line.startswith("##"):
                in_backlog = False
            elif in_backlog and line.startswith("|") and "ID" not in line and "----" not in line:
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 2:
                    items.append(
                        {
                            "id": parts[0],
                            "title": parts[1],
                            "priority": parts[3] if len(parts) > 3 else "",
                        }
                    )

        # Filter by priority and dependencies
        if priority:
            items = [item for item in items if item.get("priority") == priority]

        return items[:count]


if __name__ == "__main__":
    # CLI interface
    if len(sys.argv) > 1:
        if sys.argv[1] == "test-imports":
            modules = sys.argv[2:] if len(sys.argv) > 2 else ["thegent.infra"]
            success = check_imports(modules, verbose=True)
            sys.exit(0 if success else 1)
        elif sys.argv[1] == "workstream":
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            priority = sys.argv[3] if len(sys.argv) > 3 else "P1"
            items = get_workstream_items(count=count, priority=priority)
            for item in items:
                print(f"{item['id']}: {item['title']}")
        else:
            print(f"Unknown command: {sys.argv[1]}")
            sys.exit(1)
    else:
        print("DX Helpers CLI")
        print("Usage:")
        print("  python scripts/dx_helpers.py test-imports [module1] [module2] ...")
        print("  python scripts/dx_helpers.py workstream [count] [priority]")

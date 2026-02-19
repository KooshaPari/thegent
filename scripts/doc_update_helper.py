#!/usr/bin/env python3
"""
Documentation Update Helper

Reduces verbosity of repetitive documentation update patterns.
"""

import re
from datetime import datetime
from pathlib import Path


def update_status_section(file_path: Path, section_title: str, new_status: str, append: bool = False) -> bool:
    """Update a status section in a markdown file.

    Args:
        file_path: Path to markdown file
        section_title: Section title (e.g., "## Status")
        new_status: New status text
        append: Append instead of replace

    Returns:
        True if successful
    """
    if not file_path.exists():
        return False

    content = file_path.read_text(encoding="utf-8")

    # Find section
    pattern = rf"(^##+\s+{re.escape(section_title)}.*?\n)(.*?)(?=^##|\Z)"
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)

    if not match:
        # Add new section at end
        content += f"\n\n## {section_title}\n\n{new_status}\n"
    else:
        if append:
            new_content = match.group(1) + match.group(2) + f"\n{new_status}\n"
        else:
            new_content = match.group(1) + f"{new_status}\n"
        content = content[: match.start()] + new_content + content[match.end() :]

    file_path.write_text(content, encoding="utf-8")
    return True


def add_completion_entry(file_path: Path, task_id: str, agent: str = "auto", notes: str | None = None) -> bool:
    """Add a completion entry to a workstream or tracking file.

    Args:
        file_path: Path to tracking file
        task_id: Task ID
        agent: Agent name
        notes: Optional notes

    Returns:
        True if successful
    """
    if not file_path.exists():
        return False

    content = file_path.read_text(encoding="utf-8")

    # Find COMPLETED section
    pattern = r"(## COMPLETED.*?\n\|----\|.*?\n)(.*?)(?=\n##|\Z)"
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)

    if not match:
        # Add COMPLETED section
        content += "\n\n## COMPLETED\n\n| ID | Agent | Completed |\n|----|-------|-----------|\n"
        match = re.search(r"(## COMPLETED.*?\n\|----\|.*?\n)", content)

    if match:
        timestamp = datetime.now().isoformat()
        entry = f"| {task_id} | {agent} | {timestamp} |"
        if notes:
            entry += f" {notes}"
        entry += "\n"

        insert_point = match.end()
        content = content[:insert_point] + entry + content[insert_point:]
        file_path.write_text(content, encoding="utf-8")
        return True

    return False


def batch_update_status(updates: dict[str, dict[str, str]]) -> dict[str, bool]:
    """Batch update status sections in multiple files.

    Args:
        updates: Dict mapping file_path -> {section: status}

    Returns:
        Dict mapping file_path -> success
    """
    results = {}
    for file_path_str, updates_dict in updates.items():
        file_path = Path(file_path_str)
        success = True
        for section, status in updates_dict.items():
            if not update_status_section(file_path, section, status):
                success = False
        results[file_path_str] = success
    return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "complete":
            if len(sys.argv) < 4:
                print("Usage: python scripts/doc_update_helper.py complete <file> <task_id> [agent] [notes]")
                sys.exit(1)

            file_path = Path(sys.argv[2])
            task_id = sys.argv[3]
            agent = sys.argv[4] if len(sys.argv) > 4 else "auto"
            notes = sys.argv[5] if len(sys.argv) > 5 else None

            success = add_completion_entry(file_path, task_id, agent, notes)
            sys.exit(0 if success else 1)
        elif sys.argv[1] == "status":
            if len(sys.argv) < 5:
                print("Usage: python scripts/doc_update_helper.py status <file> <section> <status>")
                sys.exit(1)

            file_path = Path(sys.argv[2])
            section = sys.argv[3]
            status = sys.argv[4]

            success = update_status_section(file_path, section, status)
            sys.exit(0 if success else 1)
        else:
            print(f"Unknown command: {sys.argv[1]}")
            sys.exit(1)
    else:
        print("Doc Update Helper CLI")
        print("Usage:")
        print("  python scripts/doc_update_helper.py complete <file> <task_id> [agent] [notes]")
        print("  python scripts/doc_update_helper.py status <file> <section> <status>")

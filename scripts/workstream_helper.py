#!/usr/bin/env python3
"""
Work Stream Helper

Reduces verbosity and complexity of work stream operations.
"""

import re
from datetime import datetime
from pathlib import Path

WORK_STREAM_PATH = Path(__file__).parent.parent / "docs" / "reference" / "WORK_STREAM.md"


def parse_work_stream() -> dict[str, dict]:
    """
    Parse WORK_STREAM.md into structured data.

    Returns:
        Dict with 'backlog', 'claimed', 'completed' sections
    """
    if not WORK_STREAM_PATH.exists():
        return {"backlog": [], "claimed": [], "completed": []}

    content = WORK_STREAM_PATH.read_text(encoding="utf-8")

    result = {"backlog": [], "claimed": [], "completed": []}

    current_section = None

    for line in content.split("\n"):
        if "## BACKLOG" in line:
            current_section = "backlog"
        elif "## CLAIMED" in line:
            current_section = "claimed"
        elif "## COMPLETED" in line:
            current_section = "completed"
        elif line.startswith("|") and "ID" not in line and "----" not in line:
            # Parse table row
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 2:
                item = {
                    "id": parts[0],
                    "title": parts[1] if len(parts) > 1 else "",
                    "source": parts[2] if len(parts) > 2 else "",
                    "priority": parts[3] if len(parts) > 3 else "",
                    "depends": parts[4] if len(parts) > 4 else "",
                    "agent": parts[1] if current_section == "claimed" else None,
                    "timestamp": parts[2] if current_section == "claimed" else None,
                }
                result[current_section].append(item)

    return result


def find_unclaimed_items(priority: str | None = None) -> list[dict]:
    """
    Find unclaimed items from backlog.

    Args:
        priority: Filter by priority (P0, P1, P2, etc.)

    Returns:
        List of unclaimed items
    """
    ws = parse_work_stream()
    backlog = ws["backlog"]
    claimed_ids = {item["id"] for item in ws["claimed"]}

    unclaimed = [item for item in backlog if item["id"] not in claimed_ids]

    if priority:
        unclaimed = [item for item in unclaimed if item.get("priority") == priority]

    return unclaimed


def mark_completed(task_id: str, agent: str = "auto") -> bool:
    """
    Mark a task as completed in WORK_STREAM.md.

    Args:
        task_id: Task ID to mark complete
        agent: Agent name

    Returns:
        True if successful
    """
    ws = parse_work_stream()

    # Find task in backlog or claimed
    task = None
    for item in ws["backlog"] + ws["claimed"]:
        if item["id"] == task_id:
            task = item
            break

    if not task:
        return False

    # Read file
    content = WORK_STREAM_PATH.read_text(encoding="utf-8")

    # Remove from backlog/claimed
    content = re.sub(rf"\| {re.escape(task_id)}.*\n", "", content)

    # Add to completed
    completed_section = "## COMPLETED"
    if completed_section in content:
        # Find insertion point
        pattern = rf"({re.escape(completed_section)}.*?\n\|----\|.*?\n)"
        match = re.search(pattern, content)
        if match:
            insert_point = match.end()
            new_entry = f"| {task_id} | {agent} | {datetime.now().isoformat()} |\n"
            content = content[:insert_point] + new_entry + content[insert_point:]

    # Write back
    WORK_STREAM_PATH.write_text(content, encoding="utf-8")

    return True


def batch_mark_completed(task_ids: list[str], agent: str = "auto") -> dict[str, bool]:
    """
    Batch mark multiple tasks as completed.

    Args:
        task_ids: List of task IDs
        agent: Agent name

    Returns:
        Dict mapping task_id -> success
    """
    results = {}
    for task_id in task_ids:
        results[task_id] = mark_completed(task_id, agent)
    return results


def get_next_items(count: int = 5, priority: str | None = "P1") -> list[dict]:
    """
    Get next unclaimed items ready to work on.

    Args:
        count: Number of items to return
        priority: Filter by priority

    Returns:
        List of items ready to work on
    """
    unclaimed = find_unclaimed_items(priority=priority)

    # Filter by dependencies (only return items with satisfied deps)
    ws = parse_work_stream()
    completed_ids = {item["id"] for item in ws["completed"]}

    ready = []
    for item in unclaimed:
        depends = item.get("depends", "")
        if not depends or depends == "-":
            ready.append(item)
        else:
            # Check if dependencies are satisfied
            deps = [d.strip() for d in depends.split(",")]
            if all(dep in completed_ids for dep in deps):
                ready.append(item)

    return ready[:count]


if __name__ == "__main__":
    # Example usage
    next_items = get_next_items(count=5, priority="P1")
    print(f"Next {len(next_items)} items ready:")
    for item in next_items:
        print(f"  - {item['id']}: {item['title']}")

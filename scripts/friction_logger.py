#!/usr/bin/env python3
"""
Friction Logger

Logs friction points identified during agent workflows for continuous improvement.
"""

from datetime import datetime
from pathlib import Path
from typing import Any

FRICTION_LOG_PATH = Path(__file__).parent.parent / "docs" / "research" / "FRICTION_LOG.md"


def log_friction(
    category: str,  # dx, ux, ax
    friction_type: str,  # verbosity, complexity, error_handling, etc.
    location: str,  # file/function/pattern
    description: str,
    impact: str,  # time saved, complexity reduced, etc.
    solution: str | None = None,
    priority: str = "P2",
    metadata: dict[str, Any] | None = None,
) -> str:
    """
    Log a friction point for improvement.

    Args:
        category: dx, ux, or ax
        friction_type: Type of friction (verbosity, complexity, etc.)
        location: Where friction occurs
        description: Description of friction
        impact: Impact of fixing (time saved, etc.)
        solution: Proposed solution (optional)
        priority: P1 (blocking) or P2 (improvement)
        metadata: Additional metadata

    Returns:
        Task ID for the improvement task
    """
    timestamp = datetime.now().isoformat()
    task_id = f"{category}-improve-{friction_type}-{timestamp.split('T')[0]}"

    entry = {
        "task_id": task_id,
        "timestamp": timestamp,
        "category": category,
        "type": friction_type,
        "location": location,
        "description": description,
        "impact": impact,
        "solution": solution,
        "priority": priority,
        "metadata": metadata or {},
    }

    # Append to friction log
    log_entry = f"""
## {task_id}

- **Category**: {category.upper()}
- **Type**: {friction_type}
- **Location**: `{location}`
- **Description**: {description}
- **Impact**: {impact}
- **Solution**: {solution or "TBD"}
- **Priority**: {priority}
- **Timestamp**: {timestamp}

"""

    # Ensure log file exists
    FRICTION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Append to log
    with open(FRICTION_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(log_entry)

    return task_id


def generate_improvement_task(task_id: str, work_stream_path: Path | None = None) -> str:
    """
    Generate improvement task entry for WORK_STREAM.md.

    Args:
        task_id: Friction log task ID
        work_stream_path: Path to WORK_STREAM.md

    Returns:
        Task entry markdown
    """
    # Read friction log entry
    if not FRICTION_LOG_PATH.exists():
        return ""

    # Parse friction log (simplified - would need proper parsing)
    # For now, return template

    work_stream_path = work_stream_path or Path(__file__).parent.parent / "docs" / "reference" / "WORK_STREAM.md"

    return f"| {task_id} | [From friction log] | FRICTION_LOG.md | P2 | - |"


if __name__ == "__main__":
    # Example usage
    task_id = log_friction(
        category="dx",
        friction_type="verbosity",
        location="batch_file_ops.py",
        description="Multiple read_file calls could be batched",
        impact="Reduces tool calls by 50%",
        solution="Use batch_read_files helper",
        priority="P1",
    )
    print(f"Logged friction: {task_id}")

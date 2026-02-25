"""Migration tool for converting legacy task formats to YAML frontmatter."""

import re
from pathlib import Path
from typing import Any

from thegent.infra.fast_yaml_parser import yaml_load, yaml_dump


def migrate_work_stream_entry_to_task(
    task_id: str,
    title: str,
    source: str = "",
    priority: str = "P2",
    depends: str = "",
    work_stream_path: Path | None = None,
) -> dict[str, Any]:
    """Convert a WORK_STREAM.md table entry to a task dictionary.

    Args:
        task_id: Task ID
        title: Task title
        source: Source document
        priority: Priority (P1, P2, P3)
        depends: Dependencies (comma-separated or "-")
        work_stream_path: Optional path to WORK_STREAM.md for extracting full details

    Returns:
        Task dictionary ready for YAML frontmatter
    """
    # Parse dependencies
    depends_list = []
    if depends and depends.strip() and depends.strip() != "-":
        depends_list = [d.strip() for d in depends.split(",") if d.strip()]

    # Determine subagent type from ID or title
    subagent_type = "worker"
    if "research" in task_id.lower() or "research" in title.lower():
        subagent_type = "researcher"
    elif "review" in task_id.lower() or "review" in title.lower():
        subagent_type = "reviewer"
    elif "plan" in task_id.lower() or "plan" in title.lower():
        subagent_type = "planner"

    task = {
        "id": task_id,
        "title": title,
        "subagent_type": subagent_type,
        "priority": priority if priority in ["P1", "P2", "P3"] else "P2",
        "depends": depends_list,
        "source": source or None,
        "metadata": {
            "tags": [],
        },
    }

    # Try to extract more details from WORK_STREAM.md if available
    if work_stream_path and work_stream_path.exists():
        try:
            _text = work_stream_path.read_text(encoding="utf-8")
            # Look for task details in the document
            # This is a simple extraction - can be enhanced
            task["description"] = title  # Default to title
        except Exception:
            pass

    return task


def migrate_legacy_task_to_yaml_frontmatter(content: str) -> str:
    """Convert legacy task format to YAML frontmatter + Markdown.

    Args:
        content: Legacy task content

    Returns:
        YAML frontmatter + Markdown content
    """
    task: dict[str, Any] = {}

    # Extract TASK header
    task_match = re.search(r'TASK\s*\(([^:]+):\s*"([^"]+)"\)', content)
    if task_match:
        task["subagent_type"] = task_match.group(1).strip()
        task["description"] = task_match.group(2).strip()

    # Extract Task Input section
    input_match = re.search(r"Task Input:\s*\n(.*?)(?=Task Output:|$)", content, re.DOTALL)
    if input_match:
        input_content = input_match.group(1)

        # Extract Subagent Type
        subagent_match = re.search(r"Subagent Type:\s*(.+)", input_content)
        if subagent_match:
            task["subagent_type"] = subagent_match.group(1).strip()

        # Extract Prompt section
        prompt_match = re.search(r"Prompt:\s*\n(.*)", input_content, re.DOTALL)
        if prompt_match:
            prompt_content = prompt_match.group(1)

            # Extract ID
            id_match = re.search(r"\*\*ID:\*\*\s*(.+)", prompt_content)
            if id_match:
                task["id"] = id_match.group(1).strip()

            # Extract Title
            title_match = re.search(r"\*\*Title:\*\*\s*(.+)", prompt_content)
            if title_match:
                task["title"] = title_match.group(1).strip()

            # Extract Priority
            priority_match = re.search(r"\*\*Priority:\*\*\s*(P[123])", prompt_content)
            if priority_match:
                task["priority"] = priority_match.group(1)

            # Extract Depends
            depends_match = re.search(r"\*\*Depends:\*\*\s*(.+)", prompt_content)
            if depends_match:
                depends_str = depends_match.group(1).strip()
                if depends_str.lower() in ["none", "-", ""]:
                    task["depends"] = []
                else:
                    task["depends"] = [d.strip() for d in depends_str.split(",")]

            # Extract Implementation Details
            impl_match = re.search(r"### Implementation Details\s*\n(.*?)(?=###|$)", prompt_content, re.DOTALL)
            if impl_match:
                task["implementation_details"] = impl_match.group(1).strip()

            # Extract Steps
            steps_match = re.search(r"### Steps to Complete\s*\n(.*?)(?=###|$)", prompt_content, re.DOTALL)
            if steps_match:
                steps_content = steps_match.group(1)
                steps = []
                for line in steps_content.split("\n"):
                    step_match = re.match(r"(\d+)\.\s*(.+)", line.strip())
                    if step_match:
                        steps.append(
                            {
                                "number": int(step_match.group(1)),
                                "description": step_match.group(2).strip(),
                            }
                        )
                if steps:
                    task["steps"] = steps

            # Extract Deliverables
            deliverables_match = re.search(r"### Deliverables\s*\n(.*?)(?=###|$)", prompt_content, re.DOTALL)
            if deliverables_match:
                deliverables_content = deliverables_match.group(1)
                deliverables = []
                for line in deliverables_content.split("\n"):
                    if line.strip().startswith("- "):
                        deliverables.append(line.strip()[2:])
                if deliverables:
                    task["deliverables"] = deliverables

    # Set defaults
    if "id" not in task:
        task["id"] = "unknown-task"
    if "title" not in task:
        task["title"] = task.get("description", "Untitled Task")
    if "subagent_type" not in task:
        task["subagent_type"] = "worker"
    if "priority" not in task:
        task["priority"] = "P2"
    if "depends" not in task:
        task["depends"] = []

    # Build YAML frontmatter
    frontmatter = yaml.dump(task, default_flow_style=False, sort_keys=False, allow_unicode=True)

    # Build markdown body
    body_parts = []

    if task.get("description") and task["description"] != task.get("title"):
        body_parts.append(f"## Description\n\n{task['description']}\n")

    if task.get("implementation_details"):
        body_parts.append(f"## Implementation Details\n\n{task['implementation_details']}\n")

    if task.get("steps"):
        body_parts.append("## Steps to Complete\n")
        for step in task["steps"]:
            step_num = step.get("number", "")
            step_desc = step.get("description", "")
            body_parts.append(f"{step_num}. {step_desc}")
        body_parts.append("")

    if task.get("deliverables"):
        body_parts.append("## Deliverables\n")
        for deliverable in task["deliverables"]:
            body_parts.append(f"- {deliverable}")
        body_parts.append("")

    body = "\n".join(body_parts)

    # Combine frontmatter and body
    return f"---\n{frontmatter}---\n{body}"


def migrate_work_stream_to_tasks(
    work_stream_path: Path,
    tasks_dir: Path,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Migrate WORK_STREAM.md entries to task files.

    Args:
        work_stream_path: Path to WORK_STREAM.md
        tasks_dir: Directory to write task files
        dry_run: If True, don't write files, just return what would be created

    Returns:
        dict with migration results
    """
    if not work_stream_path.exists():
        return {"error": f"WORK_STREAM.md not found: {work_stream_path}"}

    tasks_dir.mkdir(parents=True, exist_ok=True)

    text = work_stream_path.read_text(encoding="utf-8")

    migrated = []
    skipped = []
    errors = []

    # Parse BACKLOG section
    in_backlog = False
    for line in text.splitlines():
        if line.strip().startswith("## BACKLOG") or line.strip().startswith("## PENDING"):
            in_backlog = True
            continue
        if in_backlog and line.strip().startswith("##"):
            break

        if in_backlog and line.strip().startswith("|") and "|" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3 and parts[1] and not parts[1].startswith("ID") and not all(c == "-" for c in parts[1]):
                task_id = parts[1]
                title = parts[2] if len(parts) > 2 else ""
                source = parts[3] if len(parts) > 3 else ""
                priority = parts[4] if len(parts) > 4 else "P2"
                depends = parts[5] if len(parts) > 5 else ""

                if not title:
                    skipped.append({"id": task_id, "reason": "No title"})
                    continue

                try:
                    task = migrate_work_stream_entry_to_task(
                        task_id=task_id,
                        title=title,
                        source=source,
                        priority=priority,
                        depends=depends,
                        work_stream_path=work_stream_path,
                    )

                    # Convert to YAML frontmatter format
                    task_file_content = f"""---
{yaml.dump(task, default_flow_style=False, sort_keys=False, allow_unicode=True)}---
## Description

{title}

"""

                    task_file_path = tasks_dir / f"{task_id}.md"

                    if not dry_run:
                        task_file_path.write_text(task_file_content, encoding="utf-8")

                    migrated.append(
                        {
                            "id": task_id,
                            "file": str(task_file_path),
                            "title": title,
                        }
                    )
                except Exception as e:
                    errors.append({"id": task_id, "error": str(e)})

    return {
        "migrated": migrated,
        "skipped": skipped,
        "errors": errors,
        "total": len(migrated) + len(skipped) + len(errors),
    }

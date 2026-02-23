"""Task parsing implementation."""

import orjson as json
import re
from pathlib import Path
from typing import Any

import yaml


class TaskParseError(Exception):
    """Error parsing task file."""


def parse_yaml_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter from markdown content.

    Args:
        content: Markdown content with YAML frontmatter

    Returns:
        Tuple of (frontmatter_dict, markdown_body)

    Raises:
        ValueError: If frontmatter is invalid or missing
    """
    # Match YAML frontmatter (--- ... ---)
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        # Try without trailing newline
        pattern = r"^---\s*\n(.*?)\n---\s*(.*)$"
        match = re.match(pattern, content, re.DOTALL)

    if not match:
        raise ValueError("No YAML frontmatter found")

    yaml_content = match.group(1)
    markdown_body = match.group(2)

    try:
        # Use safe_load to prevent YAML injection
        frontmatter = yaml.safe_load(yaml_content)
        if not isinstance(frontmatter, dict):
            raise ValueError("Frontmatter must be a dictionary")
        return frontmatter, markdown_body
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML frontmatter: {e}")


def detect_task_format(content: str) -> str:
    """Auto-detect task format.

    Args:
        content: File content

    Returns:
        Format type: 'yaml_frontmatter', 'legacy', 'json', or 'unknown'
    """
    if re.match(r"^---\s*\n", content):
        return "yaml_frontmatter"
    if content.strip().startswith("{"):
        try:
            json.loads(content)
            return "json"
        except Exception:
            pass
    if re.search(r"TASK\s*\(", content) or re.search(r"Task Input:", content):
        return "legacy"
    return "unknown"


def parse_task_file(file_path: Path) -> dict[str, Any]:
    """Parse a task file (auto-detects format).

    Args:
        file_path: Path to task file

    Returns:
        Parsed task dictionary

    Raises:
        TaskParseError: If file cannot be parsed
    """
    if not file_path.exists():
        raise TaskParseError(f"Task file not found: {file_path}")

    content = file_path.read_text(encoding="utf-8")

    # Handle empty file
    if not content.strip():
        raise TaskParseError("Task file is empty")

    # Handle BOM
    content = content.removeprefix("\ufeff")

    # Normalize line endings
    content = content.replace("\r\n", "\n").replace("\r", "\n")

    format_type = detect_task_format(content)

    try:
        if format_type == "yaml_frontmatter":
            frontmatter, body = parse_yaml_frontmatter(content)
            # Parse markdown sections into structured task fields
            task = parse_markdown_sections_to_fields(body, frontmatter)
            return task
        if format_type == "legacy":
            return parse_legacy_task(content)
        if format_type == "json":
            return json.loads(content)
        raise TaskParseError(f"Unknown task format: {format_type}")
    except Exception as e:
        raise TaskParseError(f"Failed to parse task file {file_path}: {e}") from e


def extract_markdown_sections(body: str) -> dict[str, str]:
    """Extract markdown sections by header.

    Args:
        body: Markdown body content

    Returns:
        Dictionary mapping section names to content
    """
    sections = {}
    current_section = None
    current_content = []

    for line in body.split("\n"):
        if line.startswith("## "):
            if current_section:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = line[3:].strip().lower().replace(" ", "_")
            current_content = []
        elif current_section:
            current_content.append(line)

    if current_section:
        sections[current_section] = "\n".join(current_content).strip()

    return sections


def parse_markdown_sections_to_fields(body: str, frontmatter: dict[str, Any]) -> dict[str, Any]:
    """Parse markdown sections into structured task fields.

    Args:
        body: Markdown body content
        frontmatter: Parsed frontmatter dictionary

    Returns:
        Updated task dictionary with parsed markdown sections
    """
    task = frontmatter.copy()
    sections = extract_markdown_sections(body)

    # Map section names to task fields
    section_mapping = {
        "description": "description",
        "implementation_details": "implementation_details",
    }

    for section_name, content in sections.items():
        # Map known sections
        if section_name in section_mapping:
            field_name = section_mapping[section_name]
            if field_name not in task or not task[field_name]:
                task[field_name] = content
        # Parse "Steps to Complete" into steps array
        elif section_name in ["steps_to_complete", "steps"]:
            if "steps" not in task or not task["steps"]:
                task["steps"] = parse_steps_from_markdown(content)
        # Parse "Deliverables" into deliverables array
        elif section_name == "deliverables":
            if "deliverables" not in task or not task["deliverables"]:
                task["deliverables"] = parse_list_from_markdown(content)
        # Parse "Acceptance Criteria" into acceptance_criteria array
        elif section_name in ["acceptance_criteria", "acceptance"]:
            if "acceptance_criteria" not in task or not task["acceptance_criteria"]:
                task["acceptance_criteria"] = parse_list_from_markdown(content)

    return task


def parse_steps_from_markdown(content: str) -> list[dict[str, Any]]:
    """Parse numbered steps from markdown content.

    Args:
        content: Markdown content with numbered steps

    Returns:
        List of step dictionaries
    """
    steps = []
    import re

    for line in content.split("\n"):
        line = line.strip()
        if not line:
            continue
        # Match numbered list: "1. Step description"
        match = re.match(r"(\d+)\.\s*(.+)", line)
        if match:
            steps.append({"number": int(match.group(1)), "description": match.group(2).strip()})
        # Match markdown checkbox: "- [ ] Step description"
        elif line.startswith(("- [ ]", "- ")):
            # Extract step number from context if available
            step_num = len(steps) + 1
            desc = line.replace("- [ ]", "").replace("- ", "").strip()
            if desc:
                steps.append({"number": step_num, "description": desc})

    return steps


def parse_list_from_markdown(content: str) -> list[str]:
    """Parse bullet list from markdown content.

    Args:
        content: Markdown content with bullet list

    Returns:
        List of strings
    """
    items = []
    for line in content.split("\n"):
        line = line.strip()
        if not line:
            continue
        # Match bullet points: "- Item" or "* Item"
        if line.startswith(("- ", "* ")):
            item = line[2:].strip()
            if item:
                items.append(item)
        # Match numbered list items (for deliverables)
        elif re.match(r"^\d+\.\s+", line):
            item = re.sub(r"^\d+\.\s+", "", line).strip()
            if item:
                items.append(item)

    return items


def parse_legacy_task(content: str) -> dict[str, Any]:
    """Parse legacy task format (backward compatibility).

    Args:
        content: Legacy task content

    Returns:
        Parsed task dictionary
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
                        steps.append({"number": int(step_match.group(1)), "description": step_match.group(2).strip()})
                task["steps"] = steps

            # Extract Deliverables
            deliverables_match = re.search(r"### Deliverables\s*\n(.*?)(?=###|$)", prompt_content, re.DOTALL)
            if deliverables_match:
                deliverables_content = deliverables_match.group(1)
                deliverables = []
                for line in deliverables_content.split("\n"):
                    if line.strip().startswith("- "):
                        deliverables.append(line.strip()[2:])
                task["deliverables"] = deliverables

    return task

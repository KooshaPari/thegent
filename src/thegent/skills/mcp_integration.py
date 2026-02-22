"""MCP integration for skills auto-discovery.

This module provides MCP tools for listing, getting, and running skills.
"""

import json
import logging
from typing import Any

from thegent.skills.discovery import (
    _get_thegent_root,
    discover_skills,
    load_skill,
    validate_skill,
)

logger = logging.getLogger(__name__)


def list_skills() -> str:
    """List all available skills.

    Returns:
        JSON string containing list of skills with their metadata.
    """
    skills = discover_skills()

    result = []
    for skill in skills:
        result.append(
            {
                "name": skill.name,
                "description": skill.description,
                "version": skill.version,
                "entrypoint": skill.entrypoint,
                "path": str(skill.path),
            }
        )

    return json.dumps(result, indent=2)


def get_skill(skill_name: str) -> str:
    """Get detailed information about a specific skill.

    Args:
        skill_name: Name of the skill to retrieve.

    Returns:
        JSON string with skill details and content.
    """
    skill = load_skill(skill_name)

    if skill is None:
        return json.dumps(
            {"error": f"Skill not found: {skill_name}", "available_skills": [s.name for s in discover_skills()]},
            indent=2,
        )

    return json.dumps(skill, indent=2)


def run_skill(skill_name: str, context: dict[str, Any] | None = None) -> str:
    """Execute a skill with optional context.

    Args:
        skill_name: Name of the skill to execute.
        context: Optional context for skill execution.

    Returns:
        JSON string with execution result.
    """
    skill = load_skill(skill_name)

    if skill is None:
        return json.dumps(
            {"error": f"Skill not found: {skill_name}", "available_skills": [s.name for s in discover_skills()]},
            indent=2,
        )

    entrypoint = skill.get("entrypoint", "")
    if not entrypoint:
        return json.dumps({"error": f"Skill {skill_name} has no entrypoint configured"}, indent=2)

    # For now, just return the skill info - actual execution would require
    # integrating with the agent system
    result = {
        "skill": skill_name,
        "entrypoint": entrypoint,
        "description": skill.get("description", ""),
        "version": skill.get("version", ""),
        "context": context or {},
        "status": "ready",
        "message": f"Skill '{skill_name}' is ready to execute with entrypoint '{entrypoint}'",
    }

    return json.dumps(result, indent=2)


def validate_skill_tool(skill_name: str) -> str:
    """Validate a skill by name.

    Args:
        skill_name: Name of the skill to validate.

    Returns:
        JSON string with validation results.
    """
    root = _get_thegent_root()
    skills_dir = root / "skills"
    skill_path = skills_dir / skill_name

    if not skill_path.exists():
        # Try to find by name from discovered skills
        skills = discover_skills()
        for skill in skills:
            if skill.name == skill_name:
                skill_path = skill.path
                break

    if not skill_path.exists():
        return json.dumps({"valid": False, "errors": [f"Skill not found: {skill_name}"]}, indent=2)

    result = validate_skill(skill_path)
    return json.dumps(result, indent=2)

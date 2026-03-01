"""Skill MCP tool handlers for list/activate scaffolding (WL-111)."""

from __future__ import annotations

import orjson as json
import time
from typing import Any, Protocol

from fastmcp.tools.tool import ToolResult

from thegent_skills.skills.discovery import discover_skills, load_skill


class SkillBackend(Protocol):
    def list_skills(self) -> list[dict[str, Any]]: ...

    def activate_skill(self, skill_name: str) -> dict[str, Any] | None: ...


class DiscoverySkillBackend:
    """Skill backend bound to the current discovery/load implementation."""

    def list_skills(self) -> list[dict[str, Any]]:
        skills = discover_skills()
        items = [
            {
                "name": skill.name,
                "description": skill.description,
                "version": skill.version,
                "entrypoint": skill.entrypoint,
                "path": str(skill.path),
            }
            for skill in skills
        ]
        return sorted(items, key=lambda item: (item["name"].casefold(), item["name"]))

    def activate_skill(self, skill_name: str) -> dict[str, Any] | None:
        return load_skill(skill_name)


def thegent_list_skills_impl(*, backend: SkillBackend) -> ToolResult:
    start_time = time.perf_counter()
    listed_skills = backend.list_skills()
    normalized_names: set[str] = set()
    normalized_skills: list[dict[str, Any]] = []
    for index, skill in enumerate(listed_skills):
        name = skill.get("name") if isinstance(skill, dict) else None
        if not isinstance(name, str):
            raise ValueError(f"Skill at index {index} must include non-empty string `name`.")
        cleaned_name = name.strip()
        if not cleaned_name:
            raise ValueError(f"Skill at index {index} must include non-empty string `name`.")
        folded_name = cleaned_name.casefold()
        if folded_name in normalized_names:
            raise ValueError(f"Duplicate skill name detected (case-insensitive): {cleaned_name}")
        normalized_names.add(folded_name)
        normalized_skill = dict(skill)
        normalized_skill["name"] = cleaned_name
        normalized_skills.append(normalized_skill)

    skills = sorted(normalized_skills, key=lambda item: (item["name"].casefold(), item["name"]))
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    payload = {"skills": skills}
    return ToolResult(
        content=json.dumps(payload).decode().decode(),
        structured_content=payload,
        meta={"execution_time_ms": elapsed_ms, "count": len(skills)},
    )


def thegent_activate_skill_impl(
    *,
    skill_name: Any,
    backend: SkillBackend,
    error_result_impl: Any,
) -> ToolResult:
    if not isinstance(skill_name, str):
        return error_result_impl("skill_name must be a string", "Provide skill_name as a string value.")
    cleaned = skill_name.strip()
    if not cleaned:
        return error_result_impl("skill_name must be non-empty", "Provide a valid skill name.")

    start_time = time.perf_counter()
    skill = backend.activate_skill(cleaned)
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    if skill is None:
        return error_result_impl(
            f"Skill not found: {cleaned}",
            "Call thegent_list_skills and retry with a listed name.",
            extra={"skill_name": cleaned},
        )
    payload = {"skill": skill}
    return ToolResult(
        content=json.dumps(payload).decode().decode(),
        structured_content=payload,
        meta={"execution_time_ms": elapsed_ms, "skill_name": cleaned},
    )

"""Helpers for skill prompt composition."""

from __future__ import annotations

from typing import Any

import typer


def inject_skill_instructions(prompt: str, skills: list[str] | None, *, console: Any) -> str:
    """Inject selected skill instructions into the prompt payload."""
    if not skills:
        return prompt

    from phenotype_thegent_skills.skills.discovery import load_skill

    sections: list[str] = []
    for name in skills:
        skill = load_skill(name)
        if skill is None:
            console.print(f"[red]Skill not found: {name}[/red]")
            raise typer.Exit(1)
        content = str(skill.get("content", "")).strip()
        if not content:
            console.print(f"[red]Skill has no content: {name}[/red]")
            raise typer.Exit(1)
        sections.append(f"## Skill: {name}\n{content}")

    return f"{prompt}\n\n# Activated Skills\n\n" + "\n\n".join(sections)

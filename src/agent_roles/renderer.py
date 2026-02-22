"""RoleRenderer — renders AgentRoleSpec to agents/<name>.md."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from agent_roles.spec import AgentRoleSpec

_TEMPLATE = """\
---
name: {name}
display_name: {display_name}
category: {category}
trigger: {trigger}
output_format: {output_format}
fr_traces: [{fr_traces}]
generated: {today}
---

# {display_name}

{description}

## Capabilities

{capabilities}

## Constraints

{constraints}

## Allowed Tools

{tools}
"""


class RoleRenderer:
    """Renders AgentRoleSpec instances to markdown files."""

    def __init__(self, agents_dir: Path) -> None:
        """Initialize RoleRenderer with target directory.

        Args:
            agents_dir: Directory to write rendered markdown files to

        Raises:
            OSError: If directory cannot be created
        """
        self._dir = Path(agents_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

    def render(self, spec: AgentRoleSpec) -> Path:
        """Render an AgentRoleSpec to markdown file.

        Args:
            spec: AgentRoleSpec to render

        Returns:
            Path to created markdown file

        Raises:
            OSError: If file cannot be written
        """
        content = _TEMPLATE.format(
            name=spec.name,
            display_name=spec.display_name,
            category=spec.category,
            trigger=spec.trigger,
            output_format=spec.output_format,
            fr_traces=", ".join(spec.fr_traces),
            today=date.today().isoformat(),
            description=spec.description,
            capabilities="\n".join(f"- {c}" for c in spec.capabilities),
            constraints="\n".join(f"- {c}" for c in spec.constraints),
            tools="\n".join(f"- `{t}`" for t in spec.tools_allowed),
        )
        path = self._dir / f"{spec.name}.md"
        path.write_text(content)
        return path

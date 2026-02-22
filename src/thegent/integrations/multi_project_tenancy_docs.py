"""Multi-project tenancy autosync documentation generator.

# @trace WL-199
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TenancyDocEntry:
    """A single project tenancy documentation entry."""

    project_id: str
    namespace: str
    description: str = ""


class MultiProjectTenancyDocs:
    """Manages and renders multi-project tenancy documentation."""

    def __init__(self) -> None:
        """Initialize the documentation registry."""
        self._entries: dict[str, TenancyDocEntry] = {}

    def register(
        self, project_id: str, namespace: str, description: str = ""
    ) -> TenancyDocEntry:
        """Register a project's tenancy namespace in documentation.

        Args:
            project_id: Unique project identifier.
            namespace: Namespace for isolation (e.g., 'prod', 'staging').
            description: Optional description of the project.

        Returns:
            The created TenancyDocEntry.
        """
        entry = TenancyDocEntry(
            project_id=project_id, namespace=namespace, description=description
        )
        self._entries[project_id] = entry
        return entry

    def get(self, project_id: str) -> TenancyDocEntry:
        """Retrieve a tenancy documentation entry.

        Args:
            project_id: The project ID to look up.

        Returns:
            The TenancyDocEntry for the project.

        Raises:
            KeyError: If project_id is not found.
        """
        if project_id not in self._entries:
            raise KeyError(f"Project {project_id} not found in registry")
        return self._entries[project_id]

    def render_markdown(self) -> str:
        """Render all registered projects as a markdown table.

        Returns:
            Markdown-formatted table of all registered projects.
        """
        if not self._entries:
            return "# Multi-Project Tenancy\n\nNo projects registered.\n"

        lines = ["# Multi-Project Tenancy\n", "| Project ID | Namespace | Description |"]
        lines.append("|------------|-----------|-------------|")

        for entry in self._entries.values():
            desc = entry.description or ""
            lines.append(f"| {entry.project_id} | {entry.namespace} | {desc} |")

        return "\n".join(lines) + "\n"

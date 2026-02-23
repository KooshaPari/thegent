"""Implement version switcher for documentation."""

import logging

logger = logging.getLogger(__name__)


class VersioningManager:
    """Manage documentation versioning."""

    def __init__(self, versions: list[str]) -> None:
        self.versions = versions

    def generate_version_switcher_html(self, current_version: str) -> str:
        """Generate HTML for version switcher.

        Args:
            current_version: Currently selected version

        Returns:
            Version switcher HTML content
        """
        options = []
        for v in self.versions:
            selected = "selected" if v == current_version else ""
            options.append(f'<option value="{v}" {selected}>{v}</option>')

        return f"""
<div class="version-switcher">
    <label for="doc-version">Version:</label>
    <select id="doc-version" onchange="window.location.href = '/' + this.value + '/'">
        {"".join(options)}
    </select>
</div>
"""

    def generate_version_manifest(self) -> str:
        """Generate version manifest for documentation site.

        Returns:
            JSON version manifest string
        """
        import json

        manifest = {
            "versions": self.versions,
            "latest": self.versions[-1] if self.versions else "unknown",
        }
        return json.dumps(manifest, indent=2).decode().decode()

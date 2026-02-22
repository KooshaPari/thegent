"""VitePress federation hub generator.

# @trace FR-DOCS-013
"""

from __future__ import annotations

import json
from pathlib import Path


class HubGenerator:
    """Generate a minimal VitePress hub site that links to project doc sites."""

    def __init__(self, hub_dir: Path, projects: dict[str, str]) -> None:
        self._hub = hub_dir
        self._projects = projects

    def generate(self) -> None:
        """Write hub files. Idempotent — safe to call multiple times."""
        self._hub.mkdir(parents=True, exist_ok=True)
        (self._hub / ".vitepress").mkdir(exist_ok=True)
        self._write_index()
        self._write_config()
        self._write_package_json()

    def _write_index(self) -> None:
        lines = ["# Documentation Hub\n", ""]
        for name, path in self._projects.items():
            lines.append(f"- [{name}]({path}/)")
        (self._hub / "index.md").write_text("\n".join(lines) + "\n")

    def _write_config(self) -> None:
        nav_items = [{"text": name, "link": f"{path}/"} for name, path in self._projects.items()]
        nav_json = json.dumps(nav_items, indent=2)
        config = f"""import {{ defineConfig }} from 'vitepress'

export default defineConfig({{
  title: 'Workspace Docs',
  description: 'Federation hub for all project documentation',
  themeConfig: {{
    nav: {nav_json},
  }},
}})
"""
        (self._hub / ".vitepress" / "config.ts").write_text(config)

    def _write_package_json(self) -> None:
        pkg = {
            "name": "docs-hub",
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": "vitepress dev",
                "build": "vitepress build",
                "preview": "vitepress preview",
            },
            "devDependencies": {
                "vitepress": "^1.0.0",
            },
        }
        (self._hub / "package.json").write_text(json.dumps(pkg, indent=2) + "\n")

"""VitePress ops docset generator for autosync.

# @trace WL-219
"""

from __future__ import annotations


class VitePressOpsDocset:
    """Generator for VitePress operations docsets."""

    @staticmethod
    def generate_nav(items: list[str]) -> list[dict[str, str]]:
        """Generate navigation items from a list of docset items.

        Args:
            items: List of item names/titles.

        Returns:
            List of dictionaries with 'text' and 'link' keys.
        """
        nav: list[dict[str, str]] = []
        for item in items:
            nav.append({"text": item, "link": f"/{item}"})
        return nav

    @staticmethod
    def render_index(title: str, items: list[str]) -> str:
        """Render a markdown index page for the docset.

        Args:
            title: Title for the index page.
            items: List of item names to include in the index.

        Returns:
            Markdown-formatted string with title and bullet list.
        """
        lines: list[str] = [f"# {title}", ""]
        for item in items:
            lines.append(f"- {item}")
        return "\n".join(lines)

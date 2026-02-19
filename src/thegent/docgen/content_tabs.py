"""Content tabs component for documentation."""

from typing import Any


class ContentTabs:
    """Content tabs component."""

    def __init__(self):
        """Initialize content tabs."""
        self.tabs: list[dict[str, Any]] = []

    def add_tab(self, label: str, content: str, default: bool = False) -> None:
        """Add a tab.
        
        Args:
            label: Tab label
            content: Tab content
            default: Whether this is the default tab
        """
        self.tabs.append({
            "label": label,
            "content": content,
            "default": default,
        })

    def render(self) -> str:
        """Render tabs HTML.
        
        Returns:
            HTML string
        """
        html = ['<div class="content-tabs">']
        html.append('<div class="tabs-header">')
        
        for i, tab in enumerate(self.tabs):
            active = "active" if (tab.get("default") and i == 0) or (i == 0 and not any(t.get("default") for t in self.tabs)) else ""
            html.append(f'<button class="tab-button {active}" data-tab="{i}">{tab["label"]}</button>')
        
        html.append('</div>')
        html.append('<div class="tabs-content">')
        
        for i, tab in enumerate(self.tabs):
            active = "active" if (tab.get("default") and i == 0) or (i == 0 and not any(t.get("default") for t in self.tabs)) else ""
            html.append(f'<div class="tab-panel {active}" data-panel="{i}">{tab["content"]}</div>')
        
        html.append('</div>')
        html.append('</div>')
        
        return "\n".join(html)

"""Sticky sidebar and header for documentation."""


class StickyNav:
    """Sticky navigation component for documentation."""

    def __init__(self, sidebar: bool = True, header: bool = True) -> None:
        """Initialize sticky navigation.

        Args:
            sidebar: Enable sticky sidebar
            header: Enable sticky header
        """
        self.sidebar_sticky = sidebar
        self.header_sticky = header

    def render_css(self) -> str:
        """Render CSS for sticky navigation.

        Returns:
            CSS string
        """
        css = []

        if self.sidebar_sticky:
            css.append("""
.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  z-index: 100;
}
""")

        if self.header_sticky:
            css.append("""
.header {
  position: sticky;
  top: 0;
  z-index: 200;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
""")

        return "\n".join(css)

    def render_html(self, sidebar_content: str = "", header_content: str = "") -> str:
        """Render HTML structure with sticky navigation.

        Args:
            sidebar_content: Sidebar HTML content
            header_content: Header HTML content

        Returns:
            HTML string
        """
        html = []

        if self.header_sticky:
            html.append(f'<header class="header">{header_content}</header>')

        html.append('<div class="layout">')

        if self.sidebar_sticky:
            html.append(f'<aside class="sidebar">{sidebar_content}</aside>')

        html.append('<main class="content">')
        html.append("<!-- Content goes here -->")
        html.append("</main>")
        html.append("</div>")

        return "\n".join(html)

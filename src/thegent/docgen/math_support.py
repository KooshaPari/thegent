"""KaTeX math support for documentation."""

from typing import Any


class MathSupport:
    """KaTeX math rendering support."""

    def __init__(self, auto_render: bool = True):
        """Initialize math support.
        
        Args:
            auto_render: Auto-render math expressions
        """
        self.auto_render = auto_render

    def render_script(self) -> str:
        """Render KaTeX script tags.
        
        Returns:
            HTML script tags
        """
        return '''<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
<script>
  document.addEventListener("DOMContentLoaded", function() {
    renderMathInElement(document.body, {
      delimiters: [
        {left: "$$", right: "$$", display: true},
        {left: "$", right: "$", display: false},
        {left: "\\\\[", right: "\\\\]", display: true},
        {left: "\\\\(", right: "\\\\)", display: false}
      ]
    });
  });
</script>'''

    def render_inline(self, expression: str) -> str:
        """Render inline math expression.
        
        Args:
            expression: Math expression
            
        Returns:
            HTML string
        """
        return f'<span class="math-inline">{expression}</span>'

    def render_block(self, expression: str) -> str:
        """Render block math expression.
        
        Args:
            expression: Math expression
            
        Returns:
            HTML string
        """
        return f'<div class="math-block">{expression}</div>'

"""Best-effort XML repair for malformed agent tool-call tags (WP-ROB-018).

Handles the most common failure modes:
- Unclosed tags: <TAG>content -> <TAG>content</TAG>
- Naked tags: <TAG attr -> <TAG>attr</TAG>
- Multiple root elements: wraps in <root>...</root>
"""

from __future__ import annotations

import re


class SloppyXMLRepair:
    """Repairs common XML malformation patterns produced by LLM tool-call output."""

    # Pattern for an attribute-style naked tag: <NAME attr_or_text (no closing >)
    _NAKED_TAG_RE = re.compile(r"^<([A-Za-z_][A-Za-z0-9_]*)\s+(.+)$", re.DOTALL)
    # Pattern for a properly opened but unclosed tag: <TAG>content (no </TAG>)
    _UNCLOSED_TAG_RE = re.compile(r"^<([A-Za-z_][A-Za-z0-9_]*)>(.+)$", re.DOTALL)
    # Detect multiple top-level elements
    _TOP_LEVEL_TAG_RE = re.compile(r"<([A-Za-z_][A-Za-z0-9_]*)[^/]*>")

    def repair(self, xml: str) -> str:
        """Attempt to repair malformed XML string.

        Rules applied in order:
        1. Naked tag (``<TAG attr``) -> ``<TAG>attr</TAG>``
        2. Unclosed tag (``<TAG>content``) -> ``<TAG>content</TAG>``
        3. Multiple top-level elements -> wrap in ``<root>...</root>``

        Args:
            xml: Potentially malformed XML string.

        Returns:
            Repaired XML string.
        """
        text = xml.strip()

        # Rule 1: naked tag missing the closing >
        m = self._NAKED_TAG_RE.match(text)
        if m:
            tag = m.group(1)
            content = m.group(2).strip()
            return f"<{tag}>{content}</{tag}>"

        # Rule 2: unclosed tag (has opening <TAG> but no matching </TAG>)
        m = self._UNCLOSED_TAG_RE.match(text)
        if m:
            tag = m.group(1)
            content = m.group(2)
            closing = f"</{tag}>"
            if closing not in text:
                return f"<{tag}>{content}</{tag}>"

        # Rule 3: multiple top-level elements -> wrap in <root>
        top_level = self._TOP_LEVEL_TAG_RE.findall(text)
        if len(top_level) > 1:
            return f"<root>\n{text}\n</root>"

        return text

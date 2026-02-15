"""Incremental XML Parser Engine for agent structured outputs.

Handles partial/streaming XML output from agents, extracts tags into a structured
dictionary, and provides error classification for malformed XML.
"""

import re
from typing import Any


class XMLParseError(Exception):
    """Base class for XML parsing errors."""


class MalformedTagError(XMLParseError):
    """Raised when a tag is structurally invalid."""


class TruncatedParseError(XMLParseError):
    """Raised when output is truncated with unclosed tags (streaming)."""


class InvalidTagError(XMLParseError):
    """Raised when a tag name is disallowed or invalid."""


# Strict error class codes for downstream routing/fallback
PARSE_OK = "parse_ok"
PARSE_TRUNCATED = "parse_truncated"
PARSE_INVALID_TAG = "parse_invalid_tag"
PARSE_MALFORMED = "parse_malformed"


class IncrementalXMLParser:
    """Parser for incremental/streaming XML extraction.

    Supports extracting tags like <TAG_NAME>Content</TAG_NAME> and handling
    partial tags during streaming.
    """

    def __init__(self, allowed_tags: list[str] | None = None, case_sensitive: bool = False) -> None:
        self.allowed_tags = allowed_tags
        self.case_sensitive = case_sensitive
        flags = 0 if case_sensitive else re.IGNORECASE
        # Regex for matching balanced tags: <TAG>content</TAG>
        # Supports DOTALL for multi-line content
        self._tag_pattern = re.compile(r"<([A-Z0-9_]+)>(.*?)</\1>", re.DOTALL | flags)
        # Regex for finding partial start tags: <TAG> (unclosed)
        self._start_tag_pattern = re.compile(r"<([A-Z0-9_]+)>", re.DOTALL | flags)

    def parse(self, text: str) -> dict[str, str]:
        """Parse all balanced tags from the text.

        Returns:
            Dictionary of tag_name -> content. If multiple instances of same tag,
            the last one wins (standard agent behavior). Keys are normalized to UPPERCASE
            if case_sensitive is False.
        """
        results: dict[str, str] = {}
        for match in self._tag_pattern.finditer(text):
            tag_name = match.group(1)
            if not self.case_sensitive:
                tag_name = tag_name.upper()

            content = match.group(2).strip()

            if self.allowed_tags:
                allowed = [t.upper() for t in self.allowed_tags] if not self.case_sensitive else self.allowed_tags
                if tag_name not in allowed:
                    continue

            results[tag_name] = content

        return results

    def get_partial_state(self, text: str) -> dict[str, Any]:
        """Detect any unclosed tags or partial tag starts at the end of the text (for streaming)."""
        flags = 0 if self.case_sensitive else re.IGNORECASE

        # 1. Check for a trailing partial tag like "<STATU" or "<STATUS" (no >)
        # Match < at the end followed by some alpha-numeric chars
        partial_tag_match = re.search(r"<([A-Z0-9_]*)$", text, flags)
        if partial_tag_match:
            return {
                "open_tag": None,
                "partial_content": "",
                "incomplete_tag": partial_tag_match.group(1),
                "is_truncated": True,
            }

        # 2. Check for unclosed balanced tags
        starts = list(self._start_tag_pattern.finditer(text))
        if not starts:
            return {"open_tag": None, "partial_content": "", "is_truncated": False}

        # Simple stack-based check for the last open tag
        stack = []
        for match in re.finditer(r"<(/?[A-Z0-9_]+)>", text, flags):
            tag = match.group(1)
            if tag.startswith("/"):
                closing = tag[1:]
                if not self.case_sensitive:
                    closing = closing.upper()
                if stack and stack[-1] == closing:
                    stack.pop()
            else:
                tag_name = tag
                if not self.case_sensitive:
                    tag_name = tag_name.upper()
                stack.append(tag_name)

        if stack:
            last_tag = stack[-1]
            # Extract content from last start tag to end of string
            # Find last occurrence of <TAG> case-insensitively
            if not self.case_sensitive:
                match = list(re.finditer(f"<{last_tag}>", text, re.IGNORECASE))
                if match:
                    last_start = match[-1].start()
                    content = text[last_start + len(last_tag) + 2 :]
                    return {"open_tag": last_tag, "partial_content": content, "is_truncated": True}
            else:
                last_start = text.rfind(f"<{last_tag}>")
                if last_start != -1:
                    content = text[last_start + len(last_tag) + 2 :]
                    return {"open_tag": last_tag, "partial_content": content, "is_truncated": True}

        return {"open_tag": None, "partial_content": "", "is_truncated": False}


def extract_tags(text: str, tags: list[str] | None = None) -> dict[str, str]:
    """Helper function for quick tag extraction."""
    parser = IncrementalXMLParser(allowed_tags=tags)
    return parser.parse(text)

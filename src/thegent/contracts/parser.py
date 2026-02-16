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
    partial tags during streaming. Maintains internal buffer for incremental feeds.
    """

    def __init__(
        self, allowed_tags: list[str] | None = None, case_sensitive: bool = False, strict: bool = False
    ) -> None:
        self.allowed_tags = allowed_tags
        self.case_sensitive = case_sensitive
        self.strict = strict
        self._buffer = ""
        self._committed_tags: dict[str, str] = {}

        flags = 0 if case_sensitive else re.IGNORECASE
        # Regex for matching balanced tags: <TAG>content</TAG>
        self._tag_pattern = re.compile(r"<([A-Z0-9_]+)>(.*?)</\1>", re.DOTALL | flags)
        # Regex for finding partial start tags: <TAG> (unclosed)
        self._start_tag_pattern = re.compile(r"<([A-Z0-9_]+)>", re.DOTALL | flags)
        # Regex for matching any start or end tag
        self._any_tag_pattern = re.compile(r"<(/?[A-Z0-9_]+)>", flags)

    def feed(self, chunk: str) -> dict[str, str]:
        """Feed a new chunk of text to the parser and return newly committed tags.

        Args:
            chunk: New text chunk from stream.

        Returns:
            Dictionary of NEWLY committed tags in this feed.
        """
        self._buffer += chunk

        old_tags = self._committed_tags.copy()
        self._committed_tags.update(self._extract_committed())

        # Return only the delta
        delta = {k: v for k, v in self._committed_tags.items() if k not in old_tags or old_tags[k] != v}
        return delta

    def reset(self) -> None:
        """Clear internal buffer and committed tags."""
        self._buffer = ""
        self._committed_tags = {}

    def parse(self, text: str) -> dict[str, str]:
        """One-shot parse of balanced tags. Does not affect internal state."""
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

    def _extract_committed(self) -> dict[str, str]:
        """Extract tags from the current buffer.

        Handles both properly closed tags <T>...</T> and 'effectively' closed tags
        where a new tag starts before the previous one closes (sloppy recovery).
        """
        new_tags: dict[str, str] = {}
        flags = 0 if self.case_sensitive else re.IGNORECASE

        # 1. Find all start tags
        starts = list(self._start_tag_pattern.finditer(self._buffer))
        if not starts:
            return new_tags

        for i, match in enumerate(starts):
            tag_name = match.group(1)
            if not self.case_sensitive:
                tag_name = tag_name.upper()

            if self.allowed_tags:
                allowed = [t.upper() for t in self.allowed_tags] if not self.case_sensitive else self.allowed_tags
                if tag_name not in allowed:
                    continue

            start_pos = match.end()

            # 2. Find explicit closing tag </TAG_NAME>
            closing_pattern = re.compile(f"</{re.escape(match.group(1))}>", flags)
            close_match = closing_pattern.search(self._buffer, start_pos)

            if close_match:
                content = self._buffer[start_pos : close_match.start()].strip()
                new_tags[tag_name] = content
            elif not self.strict:
                # 3. Sloppy: check if another tag starts later, effectively closing this one
                # but only if it's not the last tag in the buffer (which is still partial)
                if i < len(starts) - 1:
                    next_start = starts[i + 1].start()
                    content = self._buffer[start_pos:next_start].strip()
                    # If there's an interleaved </SOMETHING_ELSE>, strip it
                    content = re.sub(r"</?[A-Z0-9_]+>", "", content, flags=flags).strip()
                    new_tags[tag_name] = content

        return new_tags

    def get_all_tags(self, include_partial: bool = True) -> dict[str, str]:
        """Return all committed tags, optionally including the current partial tag."""
        tags = self._committed_tags.copy()
        if include_partial:
            partial = self.get_partial_state(self._buffer)
            if partial["open_tag"]:
                tags[partial["open_tag"]] = partial["partial_content"]
        return tags

    def get_partial_state(self, text: str | None = None) -> dict[str, Any]:
        """Detect any unclosed tags or partial tag starts at the end of the text."""
        text = text if text is not None else self._buffer
        flags = 0 if self.case_sensitive else re.IGNORECASE

        # 1. Check for a trailing partial tag like "<STATU" or "<STATUS" (no >)
        partial_tag_match = re.search(r"<([A-Z0-9_]*)$", text, flags)
        if partial_tag_match:
            return {
                "open_tag": None,
                "partial_content": "",
                "incomplete_tag": partial_tag_match.group(1),
                "is_truncated": True,
            }

        # 2. Check for unclosed balanced tags using a stack
        stack = []
        for match in self._any_tag_pattern.finditer(text):
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
            # Find last occurrence of <TAG> case-insensitively
            pattern = re.compile(f"<{re.escape(last_tag)}>", flags)
            matches = list(pattern.finditer(text))
            if matches:
                last_start = matches[-1].end()
                content = text[last_start:].strip()
                return {"open_tag": last_tag, "partial_content": content, "is_truncated": True}

        return {"open_tag": None, "partial_content": "", "is_truncated": False}


def extract_tags(text: str, tags: list[str] | None = None) -> dict[str, str]:
    """Helper function for quick tag extraction."""
    parser = IncrementalXMLParser(allowed_tags=tags)
    return parser.parse(text)

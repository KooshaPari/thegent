"""Incremental XML Parser Engine for agent structured outputs.

Handles partial/streaming XML output from agents, extracts tags into a structured
dictionary, and provides error classification for malformed XML.

BKM-02: When THGENT_USE_NATIVE_PARSER=1, uses thegent_parser Rust extension
for extract_xml_tags. Falls back to Python IncrementalXMLParser otherwise.
"""

import importlib.util
import logging
from collections.abc import Callable
from enum import StrEnum
from typing import Any

from thegent.config import ThegentSettings

_thegent_parser: Any = None
_log = logging.getLogger(__name__)


def _get_native_parser() -> Any:
    """Lazy import of thegent_parser native extension. Returns None if unavailable."""
    global _thegent_parser
    if _thegent_parser is not None:
        return _thegent_parser
    if not ThegentSettings().use_native_parser:
        return None
    for mod_path in ("thegent_parser.thegent_parser", "thegent_parser"):
        spec = importlib.util.find_spec(mod_path)
        if spec is not None and spec.loader is not None:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            _thegent_parser = mod
            return mod
    return None


class XMLParseError(Exception):
    """Base class for XML parsing errors."""


class MalformedTagError(XMLParseError):
    """Raised when a tag is structurally invalid."""


class TruncatedParseError(XMLParseError):
    """Raised when output is truncated with unclosed tags (streaming)."""


class InvalidTagError(XMLParseError):
    """Raised when a tag name is disallowed or invalid."""


class ParserState(StrEnum):
    """WP-7003: States for the canonical parser state machine."""

    IDLE = "idle"
    IN_TAG = "in_tag"
    IN_CONTENT = "in_content"
    ERROR = "error"


# Strict error class codes for downstream routing/fallback
PARSE_OK = "parse_ok"
PARSE_TRUNCATED = "parse_truncated"
PARSE_INVALID_TAG = "parse_invalid_tag"
PARSE_MALFORMED = "parse_malformed"


class IncrementalXMLParser:
    """Minimal Incremental XML parser implementation used for tag extraction and partial state detection.

    This is a lightweight implementation sufficient for tag extraction of simple
    <TAG>value</TAG> pairs and to detect obvious truncation/open-tag states.
    """

    def __init__(
        self, allowed_tags: list[str] | None = None, case_sensitive: bool = False, strict: bool = False
    ) -> None:
        self.allowed_tags = allowed_tags
        self.case_sensitive = case_sensitive
        self.strict = strict
        self._buffer = ""
        self._committed_tags: dict[str, str] = {}

    def parse(self, text: str) -> dict[str, str]:
        """Extract simple XML tags of the form <TAG>value</TAG> into a dict.

        This is intentionally permissive and meant as a best-effort extractor for
        structured agent outputs.

        OPT-007: Early-exit on structural failure detection to avoid full parse on bad input.
        """
        import re

        self._buffer = text or ""

        # OPT-007: Early-exit check for obvious structural failures before full parse
        # Check for unmatched angle brackets (structural failure indicator)
        open_brackets = self._buffer.count("<")
        close_brackets = self._buffer.count(">")
        if open_brackets != close_brackets and self.strict:
            # In strict mode, unmatched brackets indicate structural failure
            # Return empty dict early to avoid expensive regex matching
            return {}

        # Quick check for invalid nesting patterns (e.g., <TAG><OTHER without closing)
        # This is a lightweight heuristic before full regex parse
        if self.strict and "<" in self._buffer:
            # Check for patterns like <TAG><OTHER (nested open tags without proper closing)
            # This is a fast pre-check before expensive regex
            tag_open_positions = [i for i, char in enumerate(self._buffer) if char == "<"]
            if len(tag_open_positions) > 1:
                # Simple heuristic: if we have multiple opens but can't find matching closes,
                # likely structural issue (but allow streaming/partial content in non-strict mode)
                pass  # Continue to full parse in non-strict mode

        pattern = re.compile(r"<([A-Za-z0-9_\-]+)>(.*?)</\1>", re.DOTALL)
        tags: dict[str, str] = {}
        for m in pattern.finditer(self._buffer):
            key = m.group(1)
            val = m.group(2).strip()
            # OPT-007: Early-exit if we detect invalid tag name (structural failure)
            if self.allowed_tags and key not in self.allowed_tags:
                if self.strict:
                    # In strict mode, disallowed tag = structural failure, exit early
                    return {}
                # In non-strict mode, skip this tag but continue
                continue
            tags[key] = val
        self._committed_tags = tags.copy()
        return tags

    def get_partial_state(self, text: str) -> dict[str, bool]:
        """Return simple partial parse signals: whether an open tag is present or an incomplete tag."""
        buf = text or ""
        open_tag = False
        incomplete_tag = False
        # If last '<' occurs after last '>' we assume an open/incomplete tag
        last_lt = buf.rfind("<")
        last_gt = buf.rfind(">")
        if last_lt != -1 and last_lt > last_gt:
            open_tag = True
            # If there is no closing '>' at all, treat as incomplete
            if ">" not in buf:
                incomplete_tag = True
        return {"open_tag": open_tag, "incomplete_tag": incomplete_tag}

    def _extract_committed(self) -> dict[str, str]:
        return self._committed_tags.copy()


class StreamingXMLParser(IncrementalXMLParser):
    """WP-7003: Parser with strict state machine and checkpoint/recovery (WP-7004)."""

    def __init__(
        self, allowed_tags: list[str] | None = None, case_sensitive: bool = False, strict: bool = False
    ) -> None:
        super().__init__(allowed_tags, case_sensitive, strict)
        self.state = ParserState.IDLE
        self._checkpoints: list[dict[str, str]] = []
        self._on_state_change: list[Callable[[ParserState], None]] = []

    def add_state_listener(self, callback: Callable[[ParserState], None]) -> None:
        """Register a listener for state transitions."""
        self._on_state_change.append(callback)

    def _set_state(self, new_state: ParserState) -> None:
        if self.state != new_state:
            self.state = new_state
            for cb in self._on_state_change:
                cb(new_state)

    def feed(self, chunk: str) -> dict[str, str]:
        """Enhanced feed with state tracking."""
        self._buffer += chunk

        # Simple state inference based on buffer
        partial = self.get_partial_state(self._buffer)
        if partial.get("incomplete_tag"):
            self._set_state(ParserState.IN_TAG)
        elif partial["open_tag"]:
            self._set_state(ParserState.IN_CONTENT)
        else:
            self._set_state(ParserState.IDLE)

        old_tags = self._committed_tags.copy()
        self._committed_tags.update(self._extract_committed())

        delta = {k: v for k, v in self._committed_tags.items() if k not in old_tags or old_tags[k] != v}
        return delta

    def commit_checkpoint(self) -> str:
        """WP-7004: Create a recovery checkpoint of the current committed tags."""
        import hashlib
        import json

        state_data = json.dumps(self._committed_tags, sort_keys=True).decode().decode()
        checkpoint_id = hashlib.sha256(state_data.encode()).hexdigest()[:12]
        self._checkpoints.append(self._committed_tags.copy())
        return checkpoint_id

    def rollback(self) -> bool:
        """WP-7004: Revert to the last checkpoint."""
        if not self._checkpoints:
            return False
        self._committed_tags = self._checkpoints.pop()
        # Reset buffer to reflect rolled back state?
        # For simplicity, we just clear buffer as we can't easily 'undo' incoming stream chunks.
        self._buffer = ""
        self._set_state(ParserState.IDLE)
        return True


def extract_tags(text: str, tags: list[str] | None = None) -> dict[str, str]:
    """Helper function for quick tag extraction.

    BKM-02: Uses thegent_parser Rust extension when THGENT_USE_NATIVE_PARSER=1;
    otherwise falls back to Python IncrementalXMLParser.
    """
    native = _get_native_parser()
    if native is not None and hasattr(native, "extract_xml_tags"):
        try:
            return native.extract_xml_tags(text, allowed_tags=tags, case_sensitive=False)
        except Exception as exc:
            _log.debug("Native XML parser failed; falling back to Python parser: %s", exc)
    parser = IncrementalXMLParser(allowed_tags=tags)
    return parser.parse(text)

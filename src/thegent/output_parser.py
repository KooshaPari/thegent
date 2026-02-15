"""Condensed output extraction for agent streams.

Supports:
- JSONL / stream-json: Extract last assistant message (type=message, role=assistant).
- Plain text: Extract last meaningful block, stripping trailing noise.
- Structural validation: ParseResult with error_class for downstream routing/fallback.
"""

import json
import re
from dataclasses import dataclass
from typing import Any

# Error class codes for structural validation (aligned with contracts/parser)
PARSE_OK = "parse_ok"
PARSE_TRUNCATED = "parse_truncated"
PARSE_MALFORMED = "parse_malformed"
PARSE_EMPTY = "parse_empty"

# Schema version for extraction contract (Chunk 173 follow-up)
OUTPUT_PARSER_SCHEMA_VERSION = "output-parser-v1"

# Leading lines to strip (copilot: TIME CONSTRAINT echo, usage header, OK)
_LEADING_NOISE_PATTERNS = (
    r"^\[TIME CONSTRAINT:",
    r"^\[TIME CONSTRAINT\]",
    r"^\[TIME CONSTRAINT\].*tool calls",
    r"^You have approximately \d+ tool calls",
    r"^When done or when approaching",
    r"^Do not start new multi-step",
    r"^claude-haiku.*\d+\.\d+k input",
    r"^Model:.*with diff edit format",
    r"^\s*OK\s*$",
)

# QW-006: Cache compiled regex patterns as module singletons.
_LEADING_NOISE_RE = [re.compile(p, re.MULTILINE) for p in _LEADING_NOISE_PATTERNS]

# JSONL metadata lines to strip (codex: turn.completed, turn.started, thread.started, usage)
_JSONL_NOISE_PATTERNS = (
    r'^\s*\{\s*"type"\s*:\s*"turn\.(completed|started)"',
    r'^\s*\{\s*"type"\s*:\s*"thread\.started"',
    r'^\s*\{\s*"type"\s*:\s*"item\.completed".*"type"\s*:\s*"error"',
)
_JSONL_NOISE_RE = [re.compile(p, re.MULTILINE) for p in _JSONL_NOISE_PATTERNS]

# Trailing lines to strip from plain text (usage stats, copilot/cursor/claude verbosity)
_PLAIN_TEXT_NOISE_PATTERNS = (
    r"^Total usage est:",
    r"^Total duration \(API\):",
    r"^Total duration \(wall\):",
    r"^Total code changes:",
    r"^Usage by model:",
    r"^Tokens:.*sent.*received",
    r"^\[OK\] ",
    r"^\[INFO\] ",
    r"^\[TIME CONSTRAINT:",
    r"^\[TIME CONSTRAINT\]",
    r"^claude-haiku.*\d+\.\d+k input",
    r"^Model:.*with diff edit format",
    r"^Git repo:",
    r"^Repo-map:",
    r"^Detected dumb terminal",
    r"^Using .* model with API key",
    r"^Aider v[\d.]+",
    r"^Copilot CLI available",
    r"^Commit:",
    r"^Workspace:",
    r"^Reasoning:",
    r"^exit=\d+",
    r'^\s*\{\s*"type"\s*:',
)
_PLAIN_TEXT_NOISE_RE = [re.compile(p, re.MULTILINE) for p in _PLAIN_TEXT_NOISE_PATTERNS]

# Think pattern
_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


def _normalize_jsonl_line(line: str) -> str | None:
    """Normalize a line for JSONL parsing and filter non-JSON entries."""
    raw = line.strip()
    if not raw:
        return None
    if raw.startswith("data:"):
        raw = raw.split(":", 1)[1].strip()
    if raw.startswith("{") and raw.endswith("}"):
        return raw
    return None


def _coerce_text(value: Any) -> str:
    """Convert arbitrary JSON payload fragments to plain text."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        parts: list[str] = []
        for item in value:
            text = _coerce_text(item)
            if text:
                parts.append(text)
        return "\n".join(parts)
    if isinstance(value, dict):
        # Common content variants for chat APIs
        for key in ("text", "content", "message"):
            candidate = value.get(key)
            text = _coerce_text(candidate)
            if text:
                return text
        return str(value)
    return str(value)


def _extract_record_message(payload: dict[str, Any]) -> str:
    """Extract best-effort assistant-facing text from a JSON record."""
    # Nested item.content/message envelope first (direct and tool responses)
    item = payload.get("item")
    if isinstance(item, dict):
        item_type = item.get("type")
        if item_type != "error":
            content = item.get("content") or item.get("message") or item.get("text")
            text = _coerce_text(content)
            if text:
                return text
        # Some payload shapes put message under item.message.content
        if isinstance(item.get("message"), dict):
            message_content = item["message"].get("content") if isinstance(item["message"], dict) else item["message"]
            text = _coerce_text(message_content)
            if text:
                return text

    # Top-level content/text fields
    for key in ("content", "text", "result"):
        text = _coerce_text(payload.get(key))
        if text:
            return text

    # Message envelope variant: {"message":{"content":"..."}}
    message = payload.get("message")
    if isinstance(message, dict):
        for key in ("content", "text"):
            text = _coerce_text(message.get(key))
            if text:
                return text
    return ""


def _extract_from_jsonl(stdout: str) -> str | None:
    """Extract last assistant message from JSONL stream. Returns None if not JSONL."""
    last_content: str | None = None
    final_text: str | None = None  # droid completion.finalText
    saw_jsonl = False
    for line in stdout.splitlines():
        json_line = _normalize_jsonl_line(line)
        if json_line is None:
            continue
        try:
            obj = json.loads(json_line)
        except json.JSONDecodeError:
            continue
        saw_jsonl = True
        if not isinstance(obj, dict):
            continue
        msg_type = obj.get("type")
        role = obj.get("role")
        content = _extract_record_message(obj)
        # Codex Responses API: item.completed with item.content
        item = obj.get("item")
        if isinstance(item, dict):
            item_type = item.get("type")
            item_content = item.get("content") or item.get("message")
            if (item_type == "message" and item_content) or (item_content and item_type != "error"):
                extracted = _coerce_text(item_content)
                if extracted:
                    content = extracted
        final = obj.get("finalText")
        if msg_type == "completion" and final is not None:
            final_text = _coerce_text(final)
        elif (msg_type == "message" and role == "assistant" and content) or content:
            last_content = content if isinstance(content, str) else str(content)
    return (final_text or last_content) if saw_jsonl else None


def _strip_leading_noise(lines: list[str]) -> list[str]:
    """Strip up to first 5 leading lines that match noise (copilot header, etc.)."""
    out: list[str] = []
    stripped_count = 0
    for line in lines:
        if stripped_count >= 5:
            out.append(line)
            continue
        s = line.strip()
        if not s:
            out.append(line)
            continue
        # QW-006: Use pre-compiled regex singletons
        if any(p.search(s) for p in _LEADING_NOISE_RE):
            stripped_count += 1
            continue
        out.append(line)
    return out


def _extract_from_plain_text(stdout: str) -> str:
    """Extract last meaningful block from plain text."""
    lines = stdout.splitlines()
    # Strip leading noise (copilot: TIME CONSTRAINT echo, usage, OK)
    lines = _strip_leading_noise(lines)
    # Strip trailing noise
    meaningful: list[str] = []
    for line in reversed(lines):
        stripped = line.strip()
        if not stripped:
            continue
        # QW-006: Use pre-compiled regex singletons
        if any(p.search(stripped) for p in _PLAIN_TEXT_NOISE_RE):
            continue
        meaningful.insert(0, line)
    # Take last block (paragraph or last N lines)
    if not meaningful:
        return stdout.strip() or ""
    # Prefer last paragraph (split by blank lines)
    blocks = re.split(r"\n\s*\n", "\n".join(meaningful))
    last_block = blocks[-1].strip() if blocks else ""
    if last_block:
        return last_block
    # Fallback: last 15 lines
    return "\n".join(meaningful[-15:]).strip()


# Worker status report: **Summary**, **Items Done**, **Issues**, **Next Steps**
_WORKER_REPORT_START = re.compile(
    r"(\*\*Summary\*\*|##\s*Summary|##\s*Worker Status|##\s*Status Report)",
    re.IGNORECASE,
)


def _strip_think_blocks(text: str) -> str:
    """Remove <think>...</think> blocks from output."""
    # QW-006: Use pre-compiled regex singleton
    return _THINK_RE.sub("", text).strip()


def _extract_worker_report(text: str) -> str | None:
    """Extract worker status report block if present (Summary, Items Done, Issues, Next Steps)."""
    m = _WORKER_REPORT_START.search(text)
    if not m:
        return None
    start = m.start()
    return text[start:].strip()


def _unescape_content(text: str) -> str:
    """Replace literal \\n with real newlines for messaging display."""
    return text.replace("\\n", "\n").strip()


def _compact_report(text: str) -> str:
    """Compact worker report for messaging: prefer Summary as primary message."""
    text = _unescape_content(text)
    summary_m = re.search(r"\*\*Summary\*\*\s*(.+?)(?=\*\*[A-Za-z]|\Z)", text, re.DOTALL | re.IGNORECASE)
    if summary_m:
        summary = summary_m.group(1).strip()
        if len(summary) > 200:
            first_sent = re.split(r"[.!?]\s+", summary, maxsplit=1)[0]
            if first_sent:
                summary = first_sent.rstrip() + ("." if not first_sent.rstrip().endswith(".") else "")
        return summary
    return text


def extract_condensed(stdout: str) -> str:
    """Extract condensed/final output from agent stdout.

    Tries JSONL first (stream-json). Falls back to plain-text heuristics.
    Prefers worker status report block (Summary, Items Done, Issues, Next Steps) when present.
    Strips <think> blocks from final output.
    """
    if not stdout or not stdout.strip():
        return ""
    # Try JSONL
    condensed = _extract_from_jsonl(stdout)
    if condensed is None:
        condensed = _extract_from_plain_text(stdout)
    condensed = _strip_think_blocks(condensed or "").strip()
    if not condensed:
        return ""
    condensed = _unescape_content(condensed)
    # Prefer worker status report block for messaging-style output
    report = _extract_worker_report(condensed)
    if report and len(report) >= 20:
        return _compact_report(report)
    return condensed


def extract_condensed_structured(stdout: str) -> dict[str, Any]:
    """Extract condensed output with schema metadata for schema-aware consumers.

    Returns {"text": str, "schema_version": str}. Use when downstream needs
    versioned extraction contract for validation or replay.
    """
    text = extract_condensed(stdout)
    return {
        "text": text,
        "schema_version": OUTPUT_PARSER_SCHEMA_VERSION,
    }


@dataclass
class ParseResult:
    """Structured parse result with error classification for routing/fallback.

    Use error_class to decide retry, fallback, or alert:
    - parse_ok: extraction succeeded
    - parse_truncated: output likely truncated (streaming)
    - parse_malformed: JSON/XML parse failure
    - parse_empty: no extractable content
    """

    success: bool
    text: str
    error_class: str
    schema_version: str = OUTPUT_PARSER_SCHEMA_VERSION
    partial_state: dict[str, Any] | None = None


def extract_condensed_validated(stdout: str) -> ParseResult:
    """Extract condensed output with structural validation and error classification.

    Returns ParseResult with success, text, error_class for downstream routing.
    Detects truncation (unclosed XML tags), JSON malformation, and empty output.
    """
    if not stdout or not stdout.strip():
        return ParseResult(
            success=False,
            text="",
            error_class=PARSE_EMPTY,
        )

    # Try JSONL first
    condensed: str | None = _extract_from_jsonl(stdout)
    error_class = PARSE_OK

    if condensed is None:
        condensed = _extract_from_plain_text(stdout)

    condensed = _strip_think_blocks(condensed or "").strip()
    if not condensed:
        return ParseResult(
            success=False,
            text="",
            error_class=PARSE_EMPTY if error_class == PARSE_OK else error_class,
        )

    condensed = _unescape_content(condensed)
    report = _extract_worker_report(condensed)
    if report and len(report) >= 20:
        condensed = _compact_report(report)

    # Check for XML truncation (unclosed tags)
    partial_state: dict[str, Any] | None = None
    if "<" in condensed and ">" in condensed:
        try:
            from thegent.contracts.parser import IncrementalXMLParser

            parser = IncrementalXMLParser()
            ps = parser.get_partial_state(condensed)
            if ps.get("open_tag"):
                error_class = PARSE_TRUNCATED
                partial_state = ps
        except Exception:
            pass

    return ParseResult(
        success=error_class == PARSE_OK,
        text=condensed,
        error_class=error_class,
        partial_state=partial_state,
    )

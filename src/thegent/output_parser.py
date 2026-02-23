"""Condensed output extraction for agent streams.

Supports:
- JSONL / stream-json: Extract last assistant message (type=message, role=assistant).
- Plain text: Extract last meaningful block, stripping trailing noise.
- Structural validation: ParseResult with error_class for downstream routing/fallback.

BKM-02: When THGENT_USE_NATIVE_PARSER=1, uses thegent_parser Rust extension
for strip_think_blocks. Falls back to Python regex otherwise.
"""

import importlib.util
import json
import logging
import re
from dataclasses import dataclass
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
    # QW-006: Use pre-compiled regex singleton
    blocks = _PARAGRAPH_SPLIT_PATTERN.split("\n".join(meaningful))
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

# QW-006: Cached regex patterns for _compact_report
_SUMMARY_PATTERN = re.compile(
    r"\*\*Summary\*\*\s*(.+?)(?=\*\*[A-Za-z]|\Z)",
    re.DOTALL | re.IGNORECASE,
)
_SENTENCE_SPLIT_PATTERN = re.compile(r"[.!?]\s+")

# QW-006: Cached regex pattern for _extract_from_plain_text paragraph split
_PARAGRAPH_SPLIT_PATTERN = re.compile(r"\n\s*\n")


def _strip_think_blocks(text: str) -> str:
    """Remove <think>...</think> blocks from output.

    BKM-02: Uses thegent_parser Rust extension when THGENT_USE_NATIVE_PARSER=1;
    otherwise falls back to Python regex.
    """
    native = _get_native_parser()
    if native is not None and hasattr(native, "strip_think_blocks"):
        try:
            return native.strip_think_blocks(text)
        except Exception as exc:
            _log.debug("Native think-strip failed; using regex fallback: %s", exc)
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
    # QW-006: Use pre-compiled regex singletons
    summary_m = _SUMMARY_PATTERN.search(text)
    if summary_m:
        summary = summary_m.group(1).strip()
        if len(summary) > 200:
            first_sent = _SENTENCE_SPLIT_PATTERN.split(summary, maxsplit=1)[0]
            if first_sent:
                summary = first_sent.rstrip() + ("." if not first_sent.rstrip().endswith(".") else "")
        return summary
    return text


def _summarize_tool_input(obj: dict[str, Any]) -> str:
    """Produce short summary of tool call for condensed display (e.g. Search(pattern: "x", path: "y"))."""
    inp = obj.get("input") or obj.get("arguments") or {}
    if isinstance(inp, str):
        try:
            inp = json.loads(inp) if inp.strip().startswith("{") else {}
        except json.JSONDecodeError:
            return inp[:60] + ("..." if len(inp) > 60 else "")
    if not isinstance(inp, dict):
        return str(inp)[:60]
    parts: list[str] = []
    for k, v in list(inp.items())[:3]:
        v_str = str(v)
        if len(v_str) > 40:
            v_str = v_str[:37] + "..."
        parts.append(f"{k}: {v_str}")
    return ", ".join(parts) if parts else ""


def _truncate(text: str, max_len: int = 80) -> str:
    """Truncate text for condensed display."""
    text = text.strip().replace("\n", " ")
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def _parse_stream_jsonl(stdout: str) -> tuple[list[dict[str, Any]], bool]:
    """Parse JSONL stream into list of records. Returns (records, saw_jsonl)."""
    records: list[dict[str, Any]] = []
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
        if isinstance(obj, dict):
            records.append(obj)
    return records, saw_jsonl


def condense_stream_to_display(
    stdout: str,
    *,
    max_answer_len: int = 80,
    expandable_hint: str = "+{n} more tool uses (ctrl+o to expand)",
) -> str:
    """Produce Cursor-style condensed output from agent stream JSON.

    Parses JSONL stream and formats:
    - User answers: "User answered questions:" + bullets (Q → A)
    - Agent turns: "agent(task)" + first tool + "+N more tool uses"

    Returns empty string if input is not JSONL (caller should fall back to extract_condensed).
    Supports Gemini/Codex stream-json; Copilot plain text returns empty.
    """
    if not stdout or not stdout.strip():
        return ""
    records, saw_jsonl = _parse_stream_jsonl(stdout)
    if not saw_jsonl or not records:
        return ""

    user_answers: list[tuple[str, str]] = []
    agent_turns: list[dict[str, Any]] = []
    current_turn: dict[str, Any] | None = None
    pending_question: str | None = None

    for obj in records:
        item = obj.get("item")
        msg_type = obj.get("type") or (item.get("type") if isinstance(item, dict) else None)
        role = obj.get("role") or (item.get("role") if isinstance(item, dict) else None)

        if item and isinstance(item, dict):
            role = role or item.get("role")
            msg_type = msg_type or item.get("type")

        content = _extract_record_message(obj)
        if item and isinstance(item, dict):
            ic = item.get("content") or item.get("message")
            if ic:
                content = _coerce_text(ic) or content

        if msg_type == "message" and role == "user" and content:
            if pending_question:
                user_answers.append((_truncate(pending_question, max_answer_len), _truncate(content, max_answer_len)))
                if agent_turns and not agent_turns[-1].get("tool_uses"):
                    agent_turns.pop()
                pending_question = None
        elif msg_type == "message" and role == "assistant" and content:
            pending_question = content.split("\n")[0].strip() or None
            task_hint = content.split("\n")[0].strip() if content else ""
            current_turn = {
                "task_hint": _truncate(task_hint, 60),
                "tool_uses": [],
            }
            agent_turns.append(current_turn)
        elif msg_type == "tool_use" and current_turn is not None:
            tool_name = (
                obj.get("tool_name") or obj.get("name") or (item.get("tool_name") if isinstance(item, dict) else "")
            )
            if not tool_name and isinstance(item, dict):
                tool_name = item.get("name", "")
            tool_name = str(tool_name) if tool_name else "tool"
            inp_summary = _summarize_tool_input(obj) or (_summarize_tool_input(item) if isinstance(item, dict) else "")
            current_turn["tool_uses"].append({"name": tool_name, "input": inp_summary})

    lines: list[str] = []
    if user_answers:
        lines.append("User answered questions:")
        for q, a in user_answers:
            lines.append(f"  · {q} → {a}")
        lines.append("")

    for turn in agent_turns:
        task = turn.get("task_hint", "")
        tools = turn.get("tool_uses", [])
        if task:
            lines.append(task)
        if tools:
            first = tools[0]
            tool_line = f"{first['name']}({first['input']})" if first.get("input") else first["name"]
            lines.append(f"  {tool_line}")
            if len(tools) > 1:
                lines.append(f"  {expandable_hint.format(n=len(tools) - 1)}")
        lines.append("")

    out = "\n".join(lines).strip()
    return out or ""


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

    # ROB-002: Check for XML truncation (unclosed tags) with partial-state validity markers
    partial_state: dict[str, Any] | None = None
    if "<" in condensed and ">" in condensed:
        try:
            from thegent.contracts.parser import IncrementalXMLParser

            parser = IncrementalXMLParser()
            ps = parser.get_partial_state(condensed)
            if ps.get("open_tag"):
                error_class = PARSE_TRUNCATED
                # ROB-002: Partial-state validity markers - mark as invalid if incomplete
                partial_state = {
                    **ps,
                    "valid": False,  # ROB-002: Mark partial state as invalid to prevent exposure
                    "reason": "incomplete_xml_tags",
                    "can_use": False,  # ROB-002: Do not use partial state in downstream processing
                }
        except Exception:
            pass

    return ParseResult(
        success=error_class == PARSE_OK,
        text=condensed,
        error_class=error_class,
        partial_state=partial_state,
    )

"""CLI output parsing for agent sessions (Claude, Codex, Cursor)."""

import re

# typing.Dict is deprecated; use built-in dict in annotations
from pydantic import BaseModel, Field

from thegent.utils import strip_ansi


class TokenUsage(BaseModel):
    """Token usage statistics."""

    total: int = 0
    input: int = 0
    cached: int = 0
    output: int = 0
    reasoning: int | None = None


class SessionInfo(BaseModel):
    """Parsed session information."""

    agent: str
    session_id: str
    token_usage: TokenUsage | None = None
    mcp_errors: list[str] = Field(default_factory=list)


# Regex patterns
RESUME_RE = re.compile(r"(?:Union[claude, codex]|cursor) resume ([\w-]+)")
TOKEN_USAGE_RE = re.compile(
    r"Token usage: total=([\d,]+) input=([\d,]+) \(\+ ([\d,]+) cached\) output=([\d,]+)(?: \(reasoning ([\d,]+)\))?"
)
MCP_ERROR_RE = re.compile(r"⚠ MCP startup incomplete \(failed: (.*?)\)")


def parse_cli_output(text: str) -> list[SessionInfo]:
    """Parse CLI output for session information and token usage."""
    sessions = []

    # We might have multiple sessions in the output or different pieces of info spread out.
    # For now, let's look for resume commands and usage stats.

    current_usage: TokenUsage | None = None
    mcp_errors: list[str] = []

    # Clean text (remove ANSI)
    text = strip_ansi(text)
    lines = text.splitlines()

    for line in lines:
        line = line.strip()

        # Check for MCP errors
        mcp_match = MCP_ERROR_RE.search(line)
        if mcp_match:
            mcp_errors.append(mcp_match.group(1))

        # Check for Token Usage
        token_match = TOKEN_USAGE_RE.search(line)
        if token_match:

            def to_int(s: str | None) -> int:
                if s is None:
                    return 0
                return int(s.replace(",", ""))

            current_usage = TokenUsage(
                total=to_int(token_match.group(1)),
                input=to_int(token_match.group(2)),
                cached=to_int(token_match.group(3)),
                output=to_int(token_match.group(4)),
                reasoning=to_int(token_match.group(5)) if token_match.group(5) else None,
            )

        # Check for Session ID (resume command)
        resume_match = RESUME_RE.search(line)
        if resume_match:
            agent = "claude" if "claude resume" in line else ("codex" if "codex resume" in line else "cursor")
            session_id = resume_match.group(1)

            sessions.append(
                SessionInfo(agent=agent, session_id=session_id, token_usage=current_usage, mcp_errors=mcp_errors)
            )
            # Reset after finding a session ID as it's usually the end of a block
            current_usage = None
            mcp_errors = []

    return sessions

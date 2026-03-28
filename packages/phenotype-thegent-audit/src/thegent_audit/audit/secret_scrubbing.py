"""Secret scrubbing utilities."""

from __future__ import annotations

import logging
import re

log = logging.getLogger(__name__)

SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("openai_api_key", re.compile(r"sk-[a-zA-Z0-9]{48}")),
    ("openai_proj_key", re.compile(r"sk-proj-[a-zA-Z0-9_\-]{48,}")),
    ("anthropic_api_key", re.compile(r"sk-ant-[a-zA-Z0-9_\-]{90,}")),
    ("google_cloud_key", re.compile(r"AIza[0-9A-Za-z\-_]{35}")),
    ("slack_token", re.compile(r"xox[baprs]-[0-9A-Za-z\-]{10,}")),
    ("private_key_block", re.compile(r"-----BEGIN [A-Z ]+ PRIVATE KEY-----")),
    ("aws_access_key_id", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("github_pat", re.compile(r"ghp_[a-zA-Z0-9]{36}")),
    ("github_oauth", re.compile(r"gho_[a-zA-Z0-9]{36}")),
    ("github_app_token", re.compile(r"ghs_[a-zA-Z0-9]{36}")),
    (
        "generic_hex_secret",
        re.compile(r"(?i)(password|secret|token|api[_\-]?key)\s*[=:]\s*[0-9a-f]{20,}"),
    ),
    (
        "generic_base64_secret",
        re.compile(r"(?i)(password|secret|token|api[_\-]?key)\s*[=:]\s*[A-Za-z0-9+/]{32,}={0,2}"),
    ),
]


def scrub_secrets(content: str) -> str:
    """Replace detected secrets with redaction placeholders."""
    if not isinstance(content, str):
        log.warning(
            "scrub_secrets received non-string content of type %s; coercing to string",
            type(content).__name__,
        )
        content = str(content)

    result = content
    for kind, pattern in SECRET_PATTERNS:
        result = pattern.sub(f"<REDACTED_{kind.upper()}>", result)
    return result

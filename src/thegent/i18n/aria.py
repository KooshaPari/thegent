"""ARIA attribute helpers for thegent UX surfaces.

The operator cockpit, decision audit, and progress emitter render
plain-text dashboards (no HTML). To keep the rendered strings
machine-readable for screen readers and TUI inspection tools, we
attach WAI-ARIA-style key/value annotations as bracketed trailers at
the end of each pane:

    [1/4] Live Runs (3)  [role=status aria-live=polite aria-atomic=true]

This module centralizes the rendering helpers so that:

* every UX surface speaks the same dialect,
* tests can assert on the structured metadata without scraping
  free-form text,
* the rendering cost is O(1) per call (no string templating).

**Traces to**: L17 I18n/A11y (audit scorecard), FR-A11Y-001 (screen-reader
hints), WP-4010 (i18n scaffolding).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Final

# ---------------------------------------------------------------------------
# Public constants
# ---------------------------------------------------------------------------

_VALID_ROLES: Final[frozenset[str]] = frozenset(
    {
        "status",
        "log",
        "timer",
        "progressbar",
        "alert",
        "table",
        "row",
        "columnheader",
        "rowheader",
        "group",
        "region",
        "list",
        "listitem",
    }
)

_LIVE_VALUES: Final[frozenset[str]] = frozenset({"off", "polite", "assertive"})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _coerce_role(role: str) -> str:
    """Return ``role`` if it is a valid ARIA role, else ``"group"``."""
    return role if role in _VALID_ROLES else "group"


def _coerce_live(value: str | None) -> str | None:
    """Return ``value`` if it is a valid aria-live value, else ``None``."""
    if value is None:
        return None
    return value if value in _LIVE_VALUES else None


def aria_attributes(
    *,
    role: str = "group",
    aria_live: str | None = None,
    aria_atomic: bool = False,
    aria_label: str | None = None,
    aria_labelledby: str | None = None,
    aria_describedby: str | None = None,
    extra: Mapping[str, str] | None = None,
) -> str:
    """Return a compact ARIA annotation string.

    Example::

        aria_attributes(role="status", aria_live="polite", aria_atomic=True)
        # -> '[role=status aria-live=polite aria-atomic=true]'

    Unknown ``role`` values are silently downgraded to ``"group"`` so
    callers never accidentally emit invalid ARIA. Unknown ``aria_live``
    values are dropped.
    """
    parts: list[str] = [f"role={_coerce_role(role)}"]
    live = _coerce_live(aria_live)
    if live is not None:
        parts.append(f"aria-live={live}")
    if aria_atomic:
        parts.append("aria-atomic=true")
    if aria_label:
        # Quote labels that contain spaces.
        parts.append(f"aria-label={_quote(aria_label)}")
    if aria_labelledby:
        parts.append(f"aria-labelledby={_quote(aria_labelledby)}")
    if aria_describedby:
        parts.append(f"aria-describedby={_quote(aria_describedby)}")
    if extra:
        for key, value in extra.items():
            parts.append(f"{key}={_quote(value)}")
    return "[" + " ".join(parts) + "]"


def annotate(
    text: str,
    *,
    role: str = "group",
    aria_live: str | None = None,
    aria_atomic: bool = False,
    aria_label: str | None = None,
    extra: Mapping[str, str] | None = None,
) -> str:
    """Append an ARIA annotation trailer to ``text``.

    Convenience wrapper around :func:`aria_attributes` for the common
    case of "render this string plus its metadata".
    """
    return f"{text} {aria_attributes(role=role, aria_live=aria_live, aria_atomic=aria_atomic, aria_label=aria_label, extra=extra)}"


def parse_aria(annotation: str) -> Mapping[str, str]:
    """Parse an annotation produced by :func:`aria_attributes` back into a dict.

    Useful for tests and tooling that want to extract the structured
    metadata without re-running the renderer. Unrecognized tokens are
    ignored. Quoted values are unquoted.
    """
    text = annotation.strip()
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1]
    pairs: dict[str, str] = {}
    for token in _tokenize(text):
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        pairs[key.strip()] = _unquote(value.strip())
    return pairs


def is_valid_role(role: str) -> bool:
    """Return True if ``role`` is a recognized ARIA role."""
    return role in _VALID_ROLES


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _quote(value: str) -> str:
    """Quote ``value`` if it contains whitespace or quotes."""
    if not value or any(c in value for c in " \t\n\"'"):
        return '"' + value.replace('"', '\\"') + '"'
    return value


def _unquote(value: str) -> str:
    """Reverse of :func:`quote`."""
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return value[1:-1]
    return value


def _tokenize(text: str) -> Iterable[str]:
    """Yield space-separated tokens, respecting double-quoted values."""
    token: list[str] = []
    in_quote = False
    for ch in text:
        if ch == '"':
            in_quote = not in_quote
            token.append(ch)
            continue
        if ch.isspace() and not in_quote:
            if token:
                yield "".join(token)
                token = []
            continue
        token.append(ch)
    if token:
        yield "".join(token)


__all__ = [
    "annotate",
    "aria_attributes",
    "is_valid_role",
    "parse_aria",
]

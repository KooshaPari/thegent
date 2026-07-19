"""Progressive disclosure for thegent decisions (WP-4002, FR-015, FR-039, P-092).

When thegent makes a routing, override, or pre-check decision, a human operator
frequently only needs a one-line answer.  But under *dig-deeper* pressure, the
operator needs to follow the chain of reasoning all the way down to the policy
rule and audit-log line that produced the verdict.

This module provides:

* :class:`DisclosureLevel` — 0:CONCISE / 1:SUMMARY / 2:DETAILED / 3:DEEPDIVE
* :class:`DecisionExplanation` — a structured explanation object with
  progressive layers; renders shorter or longer based on the chosen level.
* :class:`ExplanationBuilder` — fluent helper for the runtime to assemble
  explanations without having to know the disclosure grammar.
* :func:`render_explanation` — convenience one-shot renderer.

The disclosure grammar maps directly onto the cockpit progress bar (P-081)
and the explanations companion (P-092).  Levels are designed so::

    level 0 -> one line
    level 1 -> three lines + badge
    level 2 -> ~10 lines + table
    level 3 -> full reasoning chain + audit refs

Traces to: FR-015 (progressive disclosure), FR-039 (transport hints),
          P-092 (explanations companion), WP-4002.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Iterable, Mapping, Sequence

_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Levels
# ---------------------------------------------------------------------------


class DisclosureLevel(IntEnum):
    """How much to disclose (IntEnum so callers can ++ / -- safely)."""

    CONCISE = 0
    SUMMARY = 1
    DETAILED = 2
    DEEPDIVE = 3


_LEVEL_NAMES = {
    DisclosureLevel.CONCISE: "CONCISE",
    DisclosureLevel.SUMMARY: "SUMMARY",
    DisclosureLevel.DETAILED: "DETAILED",
    DisclosureLevel.DEEPDIVE: "DEEPDIVE",
}


def _level_name(level: int) -> str:
    """Best-effort coercion of an arbitrary int to a level name."""
    try:
        return _LEVEL_NAMES[DisclosureLevel(level)]
    except (ValueError, KeyError):
        return f"L{level}"


# ---------------------------------------------------------------------------
# Explanation payload
# ---------------------------------------------------------------------------


@dataclass
class DecisionExplanation:
    """Structured explanation of a single thegent decision.

    Attributes are intentionally ``Any``-typed so callers can attach rich
    metadata (audit refs, hyperlinks, deep-dive breadcrumbs).  Empty
    attributes are skipped at render time.
    """

    title: str
    verdict: str = ""
    reason: str = ""
    reason_code: str = ""
    rule_id: str | None = None
    confidence: float | None = None
    citations: list[str] = field(default_factory=list)
    chain: list[str] = field(default_factory=list)
    rationale_steps: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    audit_refs: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    # source attribution (which subsystem produced this explanation)
    source: str = "policy_engine"

    def with_citation(self, ref: str) -> "DecisionExplanation":
        """Return self with a citation added; fluent helper."""
        if ref and ref not in self.citations:
            self.citations.append(ref)
        return self

    def with_chain_step(self, step: str) -> "DecisionExplanation":
        """Append a step to the reasoning chain."""
        if step and step not in self.chain:
            self.chain.append(step)
        return self

    def with_audit_ref(self, ref: str) -> "DecisionExplanation":
        if ref and ref not in self.audit_refs:
            self.audit_refs.append(ref)
        return self

    def with_action(self, action: str) -> "DecisionExplanation":
        if action and action not in self.actions:
            self.actions.append(action)
        return self


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------


class ExplanationBuilder:
    """Fluent builder for :class:`DecisionExplanation`.

    Typical use::

        e = (
            ExplanationBuilder()
            .title("Override applied")
            .verdict("ALLOW")
            .reason("hotfix")
            .confidence(0.92)
            .step("evaluated federated rule r1")
            .step("override active for r1")
            .citation("docs/governance/policies.md#r1")
            .build()
        )
        print(render_explanation(e, level=DisclosureLevel.SUMMARY))
    """

    def __init__(self) -> None:
        self._exp = DecisionExplanation(title="")

    def title(self, title: str) -> "ExplanationBuilder":
        self._exp.title = title
        return self

    def verdict(self, verdict: str) -> "ExplanationBuilder":
        self._exp.verdict = verdict
        return self

    def reason(self, reason: str) -> "ExplanationBuilder":
        self._exp.reason = reason
        return self

    def reason_code(self, code: str) -> "ExplanationBuilder":
        self._exp.reason_code = code
        return self

    def rule_id(self, rid: str) -> "ExplanationBuilder":
        self._exp.rule_id = rid
        return self

    def confidence(self, value: float | None) -> "ExplanationBuilder":
        self._exp.confidence = value
        return self

    def source(self, source: str) -> "ExplanationBuilder":
        self._exp.source = source
        return self

    def citation(self, ref: str) -> "ExplanationBuilder":
        self._exp.with_citation(ref)
        return self

    def step(self, description: str) -> "ExplanationBuilder":
        self._exp.with_chain_step(description)
        return self

    def rationale(self, *steps: str) -> "ExplanationBuilder":
        for s in steps:
            if s:
                self._exp.rationale_steps.append(s)
        return self

    def audit(self, ref: str) -> "ExplanationBuilder":
        self._exp.with_audit_ref(ref)
        return self

    def action(self, description: str) -> "ExplanationBuilder":
        self._exp.with_action(description)
        return self

    def metadata(self, **values: Any) -> "ExplanationBuilder":
        self._exp.metadata.update(values)
        return self

    def build(self) -> DecisionExplanation:
        """Return the built :class:`DecisionExplanation`.

        Calling ``build()`` does *not* invalidate the builder; additional calls
        return the same payload.  This is intentional — callers can keep
        appending rationale after the first build for incremental disclosure.
        """
        return self._exp


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------


def render_explanation(
    exp: DecisionExplanation,
    *,
    level: int | DisclosureLevel = DisclosureLevel.SUMMARY,
    width: int = 80,
) -> str:
    """Render ``exp`` at the requested disclosure level.

    Args:
        exp: the structured explanation payload.
        level: which disclosure level to render (0..3).  Higher levels emit
            strictly more detail; lower levels emit strictly less.
        width: target output width in columns.

    Returns:
        A multi-line, human-readable string safe to embed in TTYs and logs.
    """
    try:
        lvl = DisclosureLevel(level)
    except (ValueError, KeyError):
        lvl = DisclosureLevel.CONCISE

    if lvl == DisclosureLevel.CONCISE:
        return _render_concise(exp, width=width)
    if lvl == DisclosureLevel.SUMMARY:
        return _render_summary(exp, width=width)
    if lvl == DisclosureLevel.DETAILED:
        return _render_detailed(exp, width=width)
    return _render_deepdive(exp, width=width)


def _hr(width: int, char: str = "-") -> str:
    return char * max(8, width)


def _badge(verdict: str) -> str:
    v = (verdict or "").lower()
    if v in ("allow", "yes", "approved"):
        return "[OK]"
    if v in ("deny", "no", "blocked"):
        return "[DENY]"
    if v in ("warn", "warning"):
        return "[WARN]"
    if v:
        return f"[{v.upper()[:6]}]"
    return "[?]"


def _pad(text: str, width: int) -> str:
    if len(text) >= width:
        return text
    return text + " " * (width - len(text))


def _render_concise(exp: DecisionExplanation, *, width: int) -> str:
    badge = _badge(exp.verdict)
    summary = exp.reason or exp.title or "(no reason given)"
    return f"{badge} {summary}"


def _render_summary(exp: DecisionExplanation, *, width: int) -> str:
    lines = [
        f"{_pad(exp.title, width - 6)} {_badge(exp.verdict)}",
        _hr(width, "="),
    ]
    if exp.reason:
        lines.append(f"reason: {exp.reason}")
    if exp.reason_code:
        lines.append(f"reason_code: {exp.reason_code}")
    if exp.rule_id:
        lines.append(f"rule_id: {exp.rule_id}")
    if exp.confidence is not None:
        lines.append(f"confidence: {exp.confidence:.2f}")
    if exp.actions:
        lines.append("suggested actions:")
        for action in exp.actions:
            lines.append(f"  - {action}")
    return "\n".join(lines)


def _render_detailed(exp: DecisionExplanation, *, width: int) -> str:
    lines = [
        f"{_pad(exp.title, width - 6)} {_badge(exp.verdict)}",
        _hr(width, "="),
    ]
    if exp.reason:
        lines.append(f"reason:       {exp.reason}")
    if exp.reason_code:
        lines.append(f"reason_code:  {exp.reason_code}")
    if exp.rule_id:
        lines.append(f"rule_id:      {exp.rule_id}")
    if exp.confidence is not None:
        lines.append(f"confidence:   {exp.confidence:.2f}")
    if exp.source:
        lines.append(f"source:       {exp.source}")
    if exp.citations:
        lines.append("citations:")
        for c in exp.citations:
            lines.append(f"  - {c}")
    if exp.actions:
        lines.append("suggested actions:")
        for action in exp.actions:
            lines.append(f"  - {action}")
    if exp.chain:
        lines.append(_hr(width, "-"))
        lines.append("reasoning chain:")
        for i, step in enumerate(exp.chain, 1):
            lines.append(f"  {i}. {step}")
    if exp.metadata:
        lines.append(_hr(width, "-"))
        lines.append("metadata:")
        for k, v in sorted(exp.metadata.items()):
            lines.append(f"  {k}: {v}")
    return "\n".join(lines)


def _render_deepdive(exp: DecisionExplanation, *, width: int) -> str:
    lines = [
        f"{_pad(exp.title, width - 6)} {_badge(exp.verdict)}",
        _hr(width, "="),
    ]
    if exp.reason:
        lines.append(f"reason:          {exp.reason}")
    if exp.reason_code:
        lines.append(f"reason_code:     {exp.reason_code}")
    if exp.rule_id:
        lines.append(f"rule_id:         {exp.rule_id}")
    if exp.confidence is not None:
        lines.append(f"confidence:      {exp.confidence:.2f}")
    if exp.source:
        lines.append(f"source:          {exp.source}")
    if exp.citations:
        lines.append("citations:")
        for c in exp.citations:
            lines.append(f"  - {c}")
    if exp.actions:
        lines.append("suggested actions:")
        for action in exp.actions:
            lines.append(f"  - {action}")
    if exp.chain:
        lines.append(_hr(width, "-"))
        lines.append("reasoning chain:")
        for i, step in enumerate(exp.chain, 1):
            lines.append(f"  {i}. {step}")
    if exp.rationale_steps:
        lines.append(_hr(width, "-"))
        lines.append("rationale:")
        for i, step in enumerate(exp.rationale_steps, 1):
            lines.append(f"  [{i}] {step}")
    if exp.audit_refs:
        lines.append(_hr(width, "-"))
        lines.append("audit:")
        for r in exp.audit_refs:
            lines.append(f"  - {r}")
    if exp.metadata:
        lines.append(_hr(width, "-"))
        lines.append("metadata:")
        for k, v in sorted(exp.metadata.items()):
            lines.append(f"  {k}: {v}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Compose helper
# ---------------------------------------------------------------------------


def render_decision_chain(
    explanations: Sequence[DecisionExplanation],
    *,
    level: int | DisclosureLevel = DisclosureLevel.SUMMARY,
    width: int = 80,
    separator: str = "\n\n",
) -> str:
    """Render a sequence of explanations at the same level, joined cleanly."""
    try:
        lvl = DisclosureLevel(level)
    except (ValueError, KeyError):
        lvl = DisclosureLevel.CONCISE
    parts = [render_explanation(e, level=lvl, width=width) for e in explanations]
    return separator.join(p for p in parts if p)


# ---------------------------------------------------------------------------
# Re-export
# ---------------------------------------------------------------------------


__all__ = [
    "DecisionExplanation",
    "DisclosureLevel",
    "ExplanationBuilder",
    "render_decision_chain",
    "render_explanation",
]

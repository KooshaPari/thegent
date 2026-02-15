"""Input guardrails (NeMo-style) before policy checks. G-GP-02.

Validates prompt, agent, model, cwd before PolicyEngine.
See docs/governance/NEMO_GUARDRAILS_DESIGN.md.
"""

from __future__ import annotations

import contextlib
import os
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class GuardrailResult:
    """Result of input guardrail check."""

    passed: bool
    rail_id: str = ""
    reason: str = ""
    remediation: str = ""


@dataclass
class InputGuardrails:
    """Input validation rails before OPA/PolicyEngine. G-GP-02."""

    prompt_max_chars: int = 65536
    prompt_blocklist_patterns: list[str] = field(default_factory=list)
    agent_allowlist: list[str] = field(default_factory=list)  # Empty = allow all
    cwd_allowed_prefixes: list[str] = field(default_factory=list)  # Empty = allow all
    model_allowlist: list[str] = field(default_factory=list)  # Empty = allow all

    def check(
        self,
        prompt: str = "",
        agent: str = "",
        model: str | None = None,
        cwd: str | Path | None = None,
    ) -> GuardrailResult:
        """Validate inputs. Returns passed=True if all rails pass."""
        # prompt_length
        if prompt and len(prompt) > self.prompt_max_chars:
            return GuardrailResult(
                passed=False,
                rail_id="prompt_length",
                reason=f"Prompt exceeds {self.prompt_max_chars} chars ({len(prompt)})",
                remediation="Shorten prompt or increase THGENT_PROMPT_MAX_CHARS",
            )

        # prompt_blocklist
        for pat in self.prompt_blocklist_patterns:
            try:
                if re.search(pat, prompt or ""):
                    return GuardrailResult(
                        passed=False,
                        rail_id="prompt_blocklist",
                        reason="Prompt matched blocklist pattern",
                        remediation="Remove blocked content from prompt",
                    )
            except re.error:
                continue

        # agent_allowlist (empty = allow all)
        if self.agent_allowlist and agent and agent not in self.agent_allowlist:
            return GuardrailResult(
                passed=False,
                rail_id="agent_allowlist",
                reason=f"Agent '{agent}' not in allowlist",
                remediation=f"Use one of: {', '.join(self.agent_allowlist)}",
            )

        # cwd_restriction (empty = allow all)
        if self.cwd_allowed_prefixes and cwd:
            cwd_str = str(Path(cwd).resolve())
            if not any(cwd_str.startswith(p) for p in self.cwd_allowed_prefixes):
                return GuardrailResult(
                    passed=False,
                    rail_id="cwd_restriction",
                    reason=f"CWD {cwd_str} not under allowed prefixes",
                    remediation=f"Run from: {', '.join(self.cwd_allowed_prefixes)}",
                )

        # model_allowlist (empty = allow all)
        if self.model_allowlist and model and model not in self.model_allowlist:
            return GuardrailResult(
                passed=False,
                rail_id="model_allowlist",
                reason=f"Model '{model}' not in allowlist",
                remediation=f"Use one of: {', '.join(self.model_allowlist)}",
            )

        return GuardrailResult(passed=True)


def _guardrails_from_env() -> InputGuardrails:
    """Build InputGuardrails from env vars."""
    max_chars = 65536
    raw = os.environ.get("THGENT_PROMPT_MAX_CHARS", "").strip()
    if raw:
        with contextlib.suppress(ValueError):
            max_chars = int(raw)

    blocklist: list[str] = []
    raw = os.environ.get("THGENT_PROMPT_BLOCKLIST_PATTERNS", "").strip()
    if raw:
        blocklist = [p.strip() for p in raw.split(",") if p.strip()]

    allowlist: list[str] = []
    raw = os.environ.get("THGENT_AGENT_ALLOWLIST", "").strip()
    if raw:
        allowlist = [a.strip() for a in raw.split(",") if a.strip()]

    cwd_prefixes: list[str] = []
    raw = os.environ.get("THGENT_CWD_ALLOWED_PREFIXES", "").strip()
    if raw:
        cwd_prefixes = [p.strip() for p in raw.split(",") if p.strip()]

    return InputGuardrails(
        prompt_max_chars=max_chars,
        prompt_blocklist_patterns=blocklist,
        agent_allowlist=allowlist,
        cwd_allowed_prefixes=cwd_prefixes,
    )

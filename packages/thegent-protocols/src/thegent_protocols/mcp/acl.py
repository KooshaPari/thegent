"""GW-65: Per-tool ACLs for MCP gateway.

Defines access control rules for MCP tool execution.
Each rule maps an (agent_id / virtual_key_prefix) to a set of
allowed (server_id, tool) pairs or wildcard patterns.

# @trace FR-MCP-065
"""

from __future__ import annotations

import fnmatch
import logging
from dataclasses import dataclass, field

_log = logging.getLogger(__name__)


@dataclass
class AclRule:
    principal: str  # agent_id or virtual_key_prefix, e.g. "sk-tg-*", "agent:coder"
    allow: list[str]  # patterns: "filesystem:read_file", "filesystem:*", "*:*"
    deny: list[str] = field(default_factory=list)  # explicit deny list


@dataclass
class AclCheckResult:
    allowed: bool
    reason: str  # human-readable reason for deny


def _matches_principal(pattern: str, principal: str) -> bool:
    """Return True if the pattern matches the given principal.

    Supports fnmatch-style wildcards (e.g. 'sk-tg-*').
    """
    return fnmatch.fnmatch(principal, pattern)


def _matches_tool_pattern(pattern: str, server_id: str, tool: str) -> bool:
    """Return True if the 'server_id:tool' string matches pattern.

    Pattern examples:
      '*:*'             — matches any server and any tool
      'filesystem:*'    — matches any tool on the filesystem server
      'filesystem:read_file' — matches exactly
    """
    target = f"{server_id}:{tool}"
    return fnmatch.fnmatch(target, pattern)


class McpAcl:
    """ACL registry for MCP tool access control."""

    def __init__(self, rules: list[AclRule] | None = None) -> None:
        self._rules: list[AclRule] = list(rules) if rules else []

    def add_rule(self, rule: AclRule) -> None:
        """Append an ACL rule to the registry."""
        self._rules.append(rule)
        _log.debug("Added ACL rule for principal: %s", rule.principal)

    def check(
        self,
        principal: str,
        server_id: str,
        tool: str,
    ) -> AclCheckResult:
        """Check if principal can call server_id:tool.

        Deny rules take precedence over allow rules.
        If no rule matches, default is DENY.
        """
        matched_any_rule = False

        for rule in self._rules:
            if not _matches_principal(rule.principal, principal):
                continue
            matched_any_rule = True

            # Deny takes precedence over allow.
            for deny_pattern in rule.deny:
                if _matches_tool_pattern(deny_pattern, server_id, tool):
                    reason = (
                        f"Principal {principal!r} is explicitly denied "
                        f"{server_id}:{tool} by rule for {rule.principal!r}"
                    )
                    _log.debug("ACL DENY: %s", reason)
                    return AclCheckResult(allowed=False, reason=reason)

            for allow_pattern in rule.allow:
                if _matches_tool_pattern(allow_pattern, server_id, tool):
                    _log.debug(
                        "ACL ALLOW: principal=%s server=%s tool=%s",
                        principal,
                        server_id,
                        tool,
                    )
                    return AclCheckResult(allowed=True, reason="")

        if matched_any_rule:
            reason = f"Principal {principal!r} has no allow rule matching {server_id}:{tool}"
        else:
            reason = f"No ACL rule found for principal {principal!r}"
        _log.debug("ACL DENY (default): %s", reason)
        return AclCheckResult(allowed=False, reason=reason)

    def list_rules(self) -> list[AclRule]:
        """Return all registered rules."""
        return list(self._rules)


def check_mcp_acl(
    principal: str,
    server_id: str,
    tool: str,
    rules: list[AclRule],
) -> AclCheckResult:
    """Convenience: one-shot ACL check against the given rule list."""
    acl = McpAcl(rules=rules)
    return acl.check(principal, server_id, tool)

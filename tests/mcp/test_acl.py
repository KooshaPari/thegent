"""Tests for GW-65: Per-tool ACLs for MCP gateway.

# @trace FR-MCP-065
"""

from __future__ import annotations

import pytest
from thegent.mcp.acl import AclCheckResult, AclRule, McpAcl, check_mcp_acl


@pytest.mark.requirement("FR-MCP-065")
def test_wildcard_allow_all() -> None:
    rule = AclRule(principal="agent:admin", allow=["*:*"])
    acl = McpAcl(rules=[rule])
    result = acl.check("agent:admin", "filesystem", "read_file")
    assert result.allowed is True
    assert result.reason == ""


@pytest.mark.requirement("FR-MCP-065")
def test_server_wildcard() -> None:
    rule = AclRule(principal="agent:coder", allow=["filesystem:*"])
    acl = McpAcl(rules=[rule])
    assert acl.check("agent:coder", "filesystem", "read_file").allowed is True
    assert acl.check("agent:coder", "filesystem", "write_file").allowed is True
    # A different server should be denied.
    assert acl.check("agent:coder", "database", "query").allowed is False


@pytest.mark.requirement("FR-MCP-065")
def test_specific_allow() -> None:
    rule = AclRule(principal="agent:reader", allow=["filesystem:read_file"])
    acl = McpAcl(rules=[rule])
    assert acl.check("agent:reader", "filesystem", "read_file").allowed is True
    assert acl.check("agent:reader", "filesystem", "write_file").allowed is False


@pytest.mark.requirement("FR-MCP-065")
def test_deny_overrides_allow() -> None:
    rule = AclRule(
        principal="agent:coder",
        allow=["filesystem:*"],
        deny=["filesystem:delete_file"],
    )
    acl = McpAcl(rules=[rule])
    assert acl.check("agent:coder", "filesystem", "read_file").allowed is True
    result = acl.check("agent:coder", "filesystem", "delete_file")
    assert result.allowed is False
    assert result.reason != ""


@pytest.mark.requirement("FR-MCP-065")
def test_no_matching_rule_denies() -> None:
    acl = McpAcl(rules=[])
    result = acl.check("agent:unknown", "filesystem", "read_file")
    assert result.allowed is False
    assert result.reason != ""


@pytest.mark.requirement("FR-MCP-065")
def test_add_rule() -> None:
    acl = McpAcl()
    assert acl.check("agent:coder", "filesystem", "read_file").allowed is False
    acl.add_rule(AclRule(principal="agent:coder", allow=["filesystem:read_file"]))
    assert acl.check("agent:coder", "filesystem", "read_file").allowed is True


@pytest.mark.requirement("FR-MCP-065")
def test_list_rules() -> None:
    rules = [
        AclRule(principal="agent:a", allow=["*:*"]),
        AclRule(principal="agent:b", allow=["filesystem:*"]),
    ]
    acl = McpAcl(rules=rules)
    listed = acl.list_rules()
    assert len(listed) == 2
    principals = {r.principal for r in listed}
    assert principals == {"agent:a", "agent:b"}


@pytest.mark.requirement("FR-MCP-065")
def test_principal_prefix_match() -> None:
    rule = AclRule(principal="sk-tg-*", allow=["*:*"])
    acl = McpAcl(rules=[rule])
    assert acl.check("sk-tg-abc123", "filesystem", "read_file").allowed is True
    assert acl.check("sk-tg-xyz", "database", "query").allowed is True


@pytest.mark.requirement("FR-MCP-065")
def test_wrong_principal_denied() -> None:
    rule = AclRule(principal="agent:coder", allow=["*:*"])
    acl = McpAcl(rules=[rule])
    result = acl.check("agent:reviewer", "filesystem", "read_file")
    assert result.allowed is False
    assert result.reason != ""


@pytest.mark.requirement("FR-MCP-065")
def test_check_mcp_acl_convenience() -> None:
    rules = [AclRule(principal="agent:coder", allow=["filesystem:read_file"])]
    result = check_mcp_acl("agent:coder", "filesystem", "read_file", rules)
    assert isinstance(result, AclCheckResult)
    assert result.allowed is True


@pytest.mark.requirement("FR-MCP-065")
def test_deny_reason_set() -> None:
    rule = AclRule(
        principal="agent:limited",
        allow=["filesystem:*"],
        deny=["filesystem:write_file"],
    )
    acl = McpAcl(rules=[rule])
    result = acl.check("agent:limited", "filesystem", "write_file")
    assert result.allowed is False
    assert len(result.reason) > 0

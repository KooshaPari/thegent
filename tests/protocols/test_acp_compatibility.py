"""Compatibility tests for legacy thegent.acp import surfaces."""

from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass
from types import ModuleType


def _install_acp_test_stubs() -> None:
    registry_module = ModuleType("thegent_agents.agents.registry")
    registry_module.AGENT_NAMES = []
    registry_module.get_runner = lambda _name: None

    base_module = ModuleType("thegent_agents.agents.base")

    class AgentRunner:
        pass

    @dataclass
    class RunResult:
        exit_code: int
        stdout: str
        stderr: str
        timed_out: bool

    base_module.AgentRunner = AgentRunner
    base_module.RunResult = RunResult

    sys.modules["thegent_agents.agents.registry"] = registry_module
    sys.modules["thegent_agents.agents.base"] = base_module


def test_legacy_acp_package_reexports_authority_symbols() -> None:
    _install_acp_test_stubs()

    legacy_pkg = importlib.import_module("thegent.acp")
    legacy_client = importlib.import_module("thegent.acp.client")
    legacy_server = importlib.import_module("thegent.acp.server")
    authority_client = importlib.import_module("thegent_protocols.acp.client")
    authority_server = importlib.import_module("thegent_protocols.acp.server")

    assert legacy_pkg.ACPClientAdapter is authority_client.ACPClientAdapter
    assert legacy_pkg.ACPServerAdapter is authority_server.ACPServerAdapter
    assert legacy_client.ACPClientAdapter is authority_client.ACPClientAdapter
    assert legacy_server.ACPServerAdapter is authority_server.ACPServerAdapter
    assert legacy_server.AgentSession is authority_server.AgentSession
    assert legacy_server.main is authority_server.main

"""Regression coverage for the canonical dispatcher bus contract."""

from __future__ import annotations

from thegent.orchestration import MessageBus
from thegent.orchestration.dispatcher import SubAgentDispatcher


def test_sub_agent_dispatcher_accepts_explicit_message_bus() -> None:
    """The canonical dispatcher keeps its explicit bus and public API. # @trace AUDIT-LANE-WL681X-001"""
    bus = MessageBus()

    dispatcher = SubAgentDispatcher(bus=bus)

    assert dispatcher.bus is bus
    assert callable(dispatcher.dispatch)
    assert callable(dispatcher.dispatch_plan)

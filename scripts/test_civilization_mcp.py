#!/usr/bin/env python3
"""
Test suite for Civilization MCP Server (Phase 4A/4B/4C)

Tests:
- Phase 4A: MCP Server resources and tools
- Phase 4B: Heartbeat streaming
- Phase 4C: Agent message broker
"""

import unittest
import asyncio
import time
from pathlib import Path
import json

try:
    try:
        from agent_identity_system import GlobalAgentRegistry, AgentIdentityFactory, AgentRole, AgentLevel
        from civilization_mcp_server import CivilizationMCPServer, AgentMessageBroker, AgentMessage, create_mcp_server
    except ImportError:
        from scripts.agent_identity_system import GlobalAgentRegistry, AgentIdentityFactory, AgentRole, AgentLevel
        from scripts.civilization_mcp_server import (
            CivilizationMCPServer,
            AgentMessageBroker,
            AgentMessage,
            create_mcp_server,
        )
    IMPORTS_AVAILABLE = True
except ImportError as e:
    IMPORTS_AVAILABLE = False


class TestPhase4AResources(unittest.TestCase):
    """Phase 4A: Test MCP resources."""

    @unittest.skipIf(not IMPORTS_AVAILABLE, "Dependencies not available")
    def setUp(self):
        """Set up test fixtures."""
        # Create fresh registry for this test (don't use global)
        self.registry = GlobalAgentRegistry()
        self.initial_count = len(list(self.registry.agents.values()))
        self.factory = AgentIdentityFactory(self.registry)
        self.server = create_mcp_server(self.registry)

        # Create test agents
        self.l1_agent = self.factory.create_l1_agent("test_project")
        self.l2_agent = self.factory.create_l2_agent("test_project", AgentRole.BUILDER, self.l1_agent.agent_id)
        self.l3_agent = self.factory.create_l3_agent("test_project", self.l2_agent.agent_id)

    def test_resource_agent_read(self):
        """Test reading agent resource."""
        uri = f"civilization://agents/{self.l1_agent.agent_id}"
        result = self.server.read_resource(uri)

        assert "agent_id" in result
        assert result["agent_id"] == self.l1_agent.agent_id

    def test_resource_project_read(self):
        """Test reading project resource."""
        uri = "civilization://projects/test_project"
        result = self.server.read_resource(uri)

        assert "agents" in result
        assert result["count"] == 3  # L1 + L2 + L3

    def test_resource_statistics_read(self):
        """Test reading statistics resource."""
        uri = "civilization://statistics"
        result = self.server.read_resource(uri)

        assert "total_agents" in result
        assert "by_level" in result
        assert result["total_agents"] == 3

    def test_resource_hierarchy_read(self):
        """Test reading hierarchy resource."""
        uri = f"civilization://hierarchy/{self.l1_agent.agent_id}"
        result = self.server.read_resource(uri)

        assert "parent_id" in result
        assert result["parent_id"] == self.l1_agent.agent_id

    def test_resource_active_read(self):
        """Test reading active agents resource."""
        uri = "civilization://active"
        result = self.server.read_resource(uri)

        assert "active_agents" in result
        assert result["count"] >= 3

    def test_resource_stale_read(self):
        """Test reading stale agents resource."""
        uri = "civilization://stale"
        result = self.server.read_resource(uri)

        assert "stale_agents" in result
        assert result["count"] == 0  # No stale agents yet

    def test_resource_unknown(self):
        """Test reading unknown resource."""
        uri = "civilization://unknown"
        result = self.server.read_resource(uri)

        assert "error" in result


class TestPhase4ATools(unittest.TestCase):
    """Phase 4A: Test MCP tools."""

    @unittest.skipIf(not IMPORTS_AVAILABLE, "Dependencies not available")
    def setUp(self):
        """Set up test fixtures."""
        self.registry = GlobalAgentRegistry()
        self.factory = AgentIdentityFactory(self.registry)
        self.server = create_mcp_server(self.registry)

        self.l1_agent = self.factory.create_l1_agent("test_project")

    def test_tool_update_heartbeat(self):
        """Test update_heartbeat tool."""
        result = self.server.call_tool("update_heartbeat", {"agent_id": self.l1_agent.agent_id})

        assert result.get("success")
        assert "timestamp" in result

    def test_tool_unregister_agent(self):
        """Test unregister_agent tool."""
        result = self.server.call_tool("unregister_agent", {"agent_id": self.l1_agent.agent_id})

        assert result.get("success")

    def test_tool_get_civilization_status(self):
        """Test get_civilization_status tool."""
        result = self.server.call_tool("get_civilization_status", {})

        assert "total_agents" in result
        assert "by_level" in result

    def test_tool_query_agents_no_filter(self):
        """Test query_agents with no filters."""
        result = self.server.call_tool("query_agents", {"filters": {}})

        assert "agents" in result
        assert "count" in result

    def test_tool_query_agents_by_project(self):
        """Test query_agents filtered by project."""
        result = self.server.call_tool("query_agents", {"filters": {"project": "test_project"}})

        assert "agents" in result
        assert result["count"] == 1  # Just L1

    def test_tool_query_agents_by_status_active(self):
        """Test query_agents filtered by status (active)."""
        result = self.server.call_tool("query_agents", {"filters": {"status": "active"}})

        assert "agents" in result
        assert result["count"] >= 1

    def test_tool_unknown(self):
        """Test calling unknown tool."""
        result = self.server.call_tool("unknown_tool", {})

        assert "error" in result


class TestPhase4BHeartbeatStreaming(unittest.TestCase):
    """Phase 4B: Test heartbeat streaming."""

    @unittest.skipIf(not IMPORTS_AVAILABLE, "Dependencies not available")
    def setUp(self):
        """Set up test fixtures."""
        self.registry = GlobalAgentRegistry()
        self.factory = AgentIdentityFactory(self.registry)
        self.server = create_mcp_server(self.registry)

        self.l1_agent = self.factory.create_l1_agent("test_project")
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        """Clean up test fixtures."""
        self.server.heartbeat_stream_running = False
        self.loop.close()

    def test_heartbeat_stream_starts(self):
        """Test heartbeat stream can start."""

        async def run_test():
            task = asyncio.create_task(self.server.stream_heartbeats())
            await asyncio.sleep(0.1)
            self.server.heartbeat_stream_running = False
            await task

        self.loop.run_until_complete(run_test())
        assert not self.server.heartbeat_stream_running

    def test_subscribe_heartbeats(self):
        """Test subscribing to heartbeats."""

        async def run_test():
            await self.server.subscribe_heartbeats("test_subscriber")
            assert "test_subscriber" in self.server.heartbeat_subscribers

        self.loop.run_until_complete(run_test())

    def test_unsubscribe_heartbeats(self):
        """Test unsubscribing from heartbeats."""

        async def run_test():
            await self.server.subscribe_heartbeats("test_subscriber")
            await self.server.unsubscribe_heartbeats("test_subscriber")
            assert "test_subscriber" not in self.server.heartbeat_subscribers

        self.loop.run_until_complete(run_test())

    def test_broadcast_message(self):
        """Test broadcasting message."""

        async def run_test():
            await self.server._broadcast_message({"type": "test", "data": "test_data"})
            # Should complete without error
            return True

        result = self.loop.run_until_complete(run_test())
        assert result


class TestPhase4CMessageBroker(unittest.TestCase):
    """Phase 4C: Test agent message broker."""

    @unittest.skipIf(not IMPORTS_AVAILABLE, "Dependencies not available")
    def setUp(self):
        """Set up test fixtures."""
        self.registry = GlobalAgentRegistry()
        self.factory = AgentIdentityFactory(self.registry)
        self.server = create_mcp_server(self.registry)
        self.broker = self.server.message_broker

        self.l1_agent = self.factory.create_l1_agent("test_project")
        self.l2_agent = self.factory.create_l2_agent("test_project", AgentRole.BUILDER, self.l1_agent.agent_id)

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        """Clean up test fixtures."""
        self.loop.close()

    def test_message_creation(self):
        """Test creating agent message."""
        msg = AgentMessage(
            id="test123",
            from_agent=self.l1_agent.agent_id,
            to_agent=self.l2_agent.agent_id,
            type="heartbeat_request",
            payload={"status": "ok"},
            timestamp=time.time(),
        )

        assert msg.id == "test123"
        assert msg.type == "heartbeat_request"
        assert not msg.ack

    def test_message_to_dict(self):
        """Test converting message to dict."""
        msg = AgentMessage(
            id="test123",
            from_agent=self.l1_agent.agent_id,
            to_agent=self.l2_agent.agent_id,
            type="heartbeat_request",
            payload={"status": "ok"},
            timestamp=time.time(),
        )

        msg_dict = msg.to_dict()
        assert "id" in msg_dict
        assert "type" in msg_dict
        assert "payload" in msg_dict

    def test_send_direct_message(self):
        """Test sending direct message."""

        async def run_test():
            # Can't complete without MCP client, so just test it queues
            asyncio.create_task(
                self.broker.send_message(self.l1_agent.agent_id, self.l2_agent.agent_id, "test_type", {"test": "data"})
            )
            await asyncio.sleep(0.1)
            return True

        result = self.loop.run_until_complete(run_test())
        assert result

    def test_broker_message_history(self):
        """Test broker maintains message history."""
        # History starts empty
        stats = self.broker.get_message_stats()
        assert stats["total_messages"] == 0

    def test_register_handler(self):
        """Test registering message handler."""

        async def test_handler(msg: AgentMessage):
            pass

        self.broker.register_handler("test_type", test_handler)
        assert "test_type" in self.broker.routes

    def test_message_stats(self):
        """Test getting message statistics."""
        stats = self.broker.get_message_stats()

        assert "total_messages" in stats
        assert "queue_size" in stats
        assert "pending_acks" in stats
        assert "recent_messages" in stats


class TestPhase4Integration(unittest.TestCase):
    """Phase 4: Integration tests."""

    @unittest.skipIf(not IMPORTS_AVAILABLE, "Dependencies not available")
    def setUp(self):
        """Set up test fixtures."""
        self.registry = GlobalAgentRegistry()
        self.factory = AgentIdentityFactory(self.registry)
        self.server = create_mcp_server(self.registry)

        # Create full hierarchy
        self.l1 = self.factory.create_l1_agent("project_alpha")
        self.l2_builder = self.factory.create_l2_agent("project_alpha", AgentRole.BUILDER, self.l1.agent_id)
        self.l2_researcher = self.factory.create_l2_agent("project_alpha", AgentRole.RESEARCHER, self.l1.agent_id)
        self.l3 = self.factory.create_l3_agent("project_alpha", self.l2_builder.agent_id)

    def test_civilization_status_complete_hierarchy(self):
        """Test civilization status with complete hierarchy."""
        status = self.server.get_civilization_status()

        assert status["total_agents"] == 4
        assert status["by_level"]["L1"] == 1
        assert status["by_level"]["L2"] == 2
        assert status["by_level"]["L3"] == 1

    def test_query_all_agents(self):
        """Test querying all agents."""
        result = self.server.call_tool("query_agents", {"filters": {}})

        assert result["count"] == 4

    def test_query_by_level(self):
        """Test querying agents by level."""
        result = self.server.call_tool("query_agents", {"filters": {"level": "L2"}})

        assert result["count"] == 2

    def test_query_by_role(self):
        """Test querying agents by role."""
        result = self.server.call_tool("query_agents", {"filters": {"role": "BUILDER"}})

        assert result["count"] >= 1

    def test_resources_available(self):
        """Test all resources are available."""
        resources = self.server.get_all_resources()

        assert len(resources) == 6
        resource_uris = [r["uri"] for r in resources]
        assert "civilization://agents/{agent_id}" in resource_uris
        assert "civilization://projects/{project}" in resource_uris
        assert "civilization://statistics" in resource_uris

    def test_tools_available(self):
        """Test all tools are available."""
        tools = self.server.get_all_tools()

        assert len(tools) == 8
        tool_names = [t["name"] for t in tools]
        assert "update_heartbeat" in tool_names
        assert "get_civilization_status" in tool_names
        assert "query_agents" in tool_names
        assert "memory_search" in tool_names
        assert "memory_analytics_summary" in tool_names

    def test_mcp_server_enabled(self):
        """Test MCP server is enabled when registry available."""
        assert self.server.enabled

    def test_message_broker_enabled(self):
        """Test message broker is enabled."""
        assert self.server.message_broker.enabled


class TestPhase4BackwardCompatibility(unittest.TestCase):
    """Phase 4: Test backward compatibility with Phase 1-3."""

    @unittest.skipIf(not IMPORTS_AVAILABLE, "Dependencies not available")
    def setUp(self):
        """Set up test fixtures."""
        self.registry = GlobalAgentRegistry()
        self.factory = AgentIdentityFactory(self.registry)
        self.server = create_mcp_server(self.registry)

        # Create agents (Phase 1 style)
        self.l1 = self.factory.create_l1_agent("compat_project")
        self.l2 = self.factory.create_l2_agent("compat_project", AgentRole.RESEARCHER, self.l1.agent_id)

    def test_phase1_registry_still_works(self):
        """Test Phase 1 registry operations still work."""
        # Get agent
        agent = self.registry.get_agent(self.l1.agent_id)
        assert agent is not None

        # Get by project
        agents = self.registry.get_agents_by_project("compat_project")
        assert len(agents) == 2

    def test_phase1_heartbeat_still_works(self):
        """Test Phase 1 heartbeat updates still work."""
        before = self.l1.last_heartbeat
        time.sleep(0.01)
        self.registry.update_heartbeat(self.l1.agent_id)
        after = self.l1.last_heartbeat

        assert after > before

    def test_phase3_stale_detection_still_works(self):
        """Test Phase 3 stale detection still works."""
        stale = self.registry.get_stale_agents()
        # None should be stale immediately
        assert len(stale) == 0

    def test_mcp_server_graceful_disable(self):
        """Test MCP server gracefully handles disable."""
        # Create server without registry
        server = CivilizationMCPServer(None)
        result = server.read_resource("civilization://statistics")

        assert "error" in result


if __name__ == "__main__":
    unittest.main(verbosity=2)

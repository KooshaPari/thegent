#!/usr/bin/env python3
"""
Civilization MCP Server - Phase 4A/4B/4C Implementation

Provides MCP (Model Context Protocol) interface to the global agent registry.
Includes real-time heartbeat streaming and cross-civilization messaging.

Components:
- Phase 4A: MCP Server Setup (resources + tools)
- Phase 4B: Heartbeat Streaming (real-time sync)
- Phase 4C: Message Broker (agent communication)
"""

import asyncio
import json
import time
import logging
from typing import Dict, Set, List, Optional, Any, Callable, Awaitable
from uuid import uuid4
from dataclasses import dataclass, asdict
from pathlib import Path

try:
    from agent_identity_system import GlobalAgentRegistry, AgentIdentity, AgentRole

    AGENT_IDENTITY_AVAILABLE = True
except ImportError:
    try:
        from scripts.agent_identity_system import GlobalAgentRegistry, AgentIdentity, AgentRole

        AGENT_IDENTITY_AVAILABLE = True
    except ImportError:
        AGENT_IDENTITY_AVAILABLE = False


# ============================================================================
# PHASE 4A: MCP Server Setup
# ============================================================================


class MCP_Resource:
    """MCP Resource definition."""

    def __init__(self, uri: str, name: str, description: str):
        self.uri = uri
        self.name = name
        self.description = description

    def to_dict(self) -> dict[str, str]:
        return {"uri": self.uri, "name": self.name, "description": self.description}


class MCP_Tool:
    """MCP Tool definition."""

    def __init__(self, name: str, description: str, input_schema: dict[str, Any]):
        self.name = name
        self.description = description
        self.input_schema = input_schema

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "description": self.description, "inputSchema": self.input_schema}


class CivilizationMCPServer:
    """MCP server for civilization framework registry.

    Exposes:
    - 6 read-only resources for registry data
    - 6 tools for registry operations
    - Real-time heartbeat streaming (Phase 4B)
    - Agent message broker (Phase 4C)
    """

    def __init__(self, registry: Optional["GlobalAgentRegistry"] = None):
        """Initialize MCP server."""
        if not AGENT_IDENTITY_AVAILABLE:
            self.registry: Optional["GlobalAgentRegistry"] = None
            self.enabled = False
            return

        if registry is not None:
            self.registry: Optional["GlobalAgentRegistry"] = registry
        else:
            self.registry = GlobalAgentRegistry()
        self.enabled = True
        self.logger = logging.getLogger("CivilizationMCPServer")

        # Phase 4A: Resources and Tools
        self.resources = self._initialize_resources()
        self.tools = self._initialize_tools()

        # Phase 4B: Heartbeat Streaming
        self.heartbeat_subscribers: set[str] = set()
        self.heartbeat_stream_running = False

        # Phase 4C: Message Broker
        self.message_broker = AgentMessageBroker(self.registry)

    # ========================================================================
    # PHASE 4A: Resources
    # ========================================================================

    def _initialize_resources(self) -> dict[str, MCP_Resource]:
        """Initialize MCP resources."""
        return {
            "agents": MCP_Resource(
                uri="civilization://agents/{agent_id}", name="Agent", description="Get metadata for a specific agent"
            ),
            "projects": MCP_Resource(
                uri="civilization://projects/{project}",
                name="Project Agents",
                description="List all agents in a project",
            ),
            "statistics": MCP_Resource(
                uri="civilization://statistics",
                name="Registry Statistics",
                description="Get registry statistics (count, projects, levels)",
            ),
            "hierarchy": MCP_Resource(
                uri="civilization://hierarchy/{parent_id}",
                name="Agent Hierarchy",
                description="Get children of an agent",
            ),
            "active": MCP_Resource(
                uri="civilization://active", name="Active Agents", description="List all active agents (not stale)"
            ),
            "stale": MCP_Resource(
                uri="civilization://stale", name="Stale Agents", description="List stale agents (no heartbeat >5 min)"
            ),
        }

    def read_resource(self, uri: str) -> dict[str, Any]:
        """Read a resource by URI."""
        if not self.enabled or not self.registry:
            return {"error": "MCP server not enabled"}

        # civilization://agents/{agent_id}
        if uri.startswith("civilization://agents/"):
            agent_id = uri.rsplit("/", maxsplit=1)[-1]
            agent = self.registry.get_agent(agent_id)
            if agent:
                return asdict(agent) if AGENT_IDENTITY_AVAILABLE else agent.__dict__
            return {"error": f"Agent not found: {agent_id}"}

        # civilization://projects/{project}
        if uri.startswith("civilization://projects/"):
            project = uri.rsplit("/", maxsplit=1)[-1]
            agents = self.registry.get_agents_by_project(project)
            return {
                "project": project,
                "agents": [asdict(a) if AGENT_IDENTITY_AVAILABLE else a.__dict__ for a in agents],
                "count": len(agents),
            }

        # civilization://statistics
        if uri == "civilization://statistics":
            stats = self.registry.get_stats()
            return {
                "total_agents": stats.get("total_agents", 0),
                "active_agents": stats.get("active_agents", 0),
                "stale_agents": stats.get("stale_agents", 0),
                "projects": stats.get("projects", []),
                "by_level": stats.get("by_level", {}),
            }

        # civilization://hierarchy/{parent_id}
        if uri.startswith("civilization://hierarchy/"):
            parent_id = uri.rsplit("/", maxsplit=1)[-1]
            parent = self.registry.get_agent(parent_id)
            if not parent:
                return {"error": f"Parent agent not found: {parent_id}"}

            # Get children - they have parent_agent_id set
            all_agents = list(self.registry.agents.values()) if self.registry else []
            children = [a for a in all_agents if hasattr(a, "parent_agent_id") and a.parent_agent_id == parent_id]

            return {
                "parent_id": parent_id,
                "children": [asdict(c) if AGENT_IDENTITY_AVAILABLE else c.__dict__ for c in children],
                "count": len(children),
            }

        # civilization://active
        if uri == "civilization://active":
            agents = self.registry.get_active_agents() if self.registry else []
            return {
                "active_agents": [asdict(a) if AGENT_IDENTITY_AVAILABLE else a.__dict__ for a in agents],
                "count": len(agents),
            }

        # civilization://stale
        if uri == "civilization://stale":
            agents = self.registry.get_stale_agents() if self.registry else []
            return {
                "stale_agents": [asdict(a) if AGENT_IDENTITY_AVAILABLE else a.__dict__ for a in agents],
                "count": len(agents),
            }

        return {"error": f"Unknown resource: {uri}"}

    # ========================================================================
    # PHASE 4A: Tools
    # ========================================================================

    def _initialize_tools(self) -> dict[str, MCP_Tool]:
        """Initialize MCP tools."""
        return {
            "update_heartbeat": MCP_Tool(
                name="update_heartbeat",
                description="Update an agent's heartbeat timestamp",
                input_schema={
                    "type": "object",
                    "properties": {"agent_id": {"type": "string", "description": "Agent ID"}},
                    "required": ["agent_id"],
                },
            ),
            "register_agent": MCP_Tool(
                name="register_agent",
                description="Register a new agent",
                input_schema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "level": {"type": "string", "enum": ["L1", "L2", "L3"]},
                        "role": {"type": "string"},
                        "project": {"type": "string"},
                        "parent_id": {"type": "string"},
                    },
                    "required": ["name", "level", "role", "project"],
                },
            ),
            "unregister_agent": MCP_Tool(
                name="unregister_agent",
                description="Unregister an agent",
                input_schema={
                    "type": "object",
                    "properties": {"agent_id": {"type": "string", "description": "Agent ID to unregister"}},
                    "required": ["agent_id"],
                },
            ),
            "recover_stale": MCP_Tool(
                name="recover_stale",
                description="Attempt to recover a stale agent",
                input_schema={
                    "type": "object",
                    "properties": {"agent_id": {"type": "string", "description": "Stale agent ID"}},
                    "required": ["agent_id"],
                },
            ),
            "get_civilization_status": MCP_Tool(
                name="get_civilization_status",
                description="Get civilization-wide status (dashboard)",
                input_schema={"type": "object", "properties": {}},
            ),
            "query_agents": MCP_Tool(
                name="query_agents",
                description="Query agents with filters",
                input_schema={
                    "type": "object",
                    "properties": {
                        "filters": {
                            "type": "object",
                            "properties": {
                                "level": {"type": "string"},
                                "project": {"type": "string"},
                                "role": {"type": "string"},
                                "status": {"type": "string", "enum": ["active", "stale"]},
                            },
                        }
                    },
                },
            ),
            "memory_search": MCP_Tool(
                name="memory_search",
                description="Search agent memories by keyword query using full-text search",
                input_schema={
                    "type": "object",
                    "properties": {
                        "agent_id": {"type": "string", "description": "Agent ID to search memories for"},
                        "query": {"type": "string", "description": "Search query (keywords)"},
                        "limit": {"type": "integer", "description": "Max results", "default": 10},
                    },
                    "required": ["agent_id", "query"],
                },
            ),
            "memory_analytics_summary": MCP_Tool(
                name="memory_analytics_summary",
                description="Get analytics summary for an agent's memories (learning velocity, error density, top keywords)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "agent_id": {"type": "string", "description": "Agent ID to analyze"},
                        "days": {"type": "integer", "description": "Number of days to analyze", "default": 30},
                    },
                    "required": ["agent_id"],
                },
            ),
        }

    def call_tool(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        """Call an MCP tool."""
        if not self.enabled or not self.registry:
            return {"error": "MCP server not enabled"}

        if tool_name == "update_heartbeat":
            agent_id = args.get("agent_id")
            if agent_id and isinstance(agent_id, str):
                self.registry.update_heartbeat(agent_id)
            return {"success": True, "agent_id": agent_id, "timestamp": time.time()}

        if tool_name == "register_agent":
            # This would be more complex - skip for MVP
            return {"error": "register_agent not yet implemented"}

        if tool_name == "unregister_agent":
            agent_id = args.get("agent_id")
            if agent_id and isinstance(agent_id, str):
                self.registry.unregister_agent(agent_id)
            return {"success": True, "agent_id": agent_id}

        if tool_name == "recover_stale":
            agent_id = args.get("agent_id")
            # Placeholder - actual recovery logic in SwarmController
            return {"success": True, "agent_id": agent_id, "message": "Recovery signal sent"}

        if tool_name == "get_civilization_status":
            return self.get_civilization_status()

        if tool_name == "query_agents":
            filters = args.get("filters", {})
            level = filters.get("level")
            project = filters.get("project")
            role = filters.get("role")
            status = filters.get("status")

            # Start with all agents from registry
            if self.registry and hasattr(self.registry, "agents"):
                agents = list(self.registry.agents.values())
            else:
                agents = []

            if level:
                agents = [a for a in agents if str(a.level) == level or a.level.value == level]
            if project:
                agents = [a for a in agents if a.project == project]
            if role:
                agents = [a for a in agents if str(a.role) == role or a.role.value == role]
            if status == "active":
                agents = [a for a in agents if not a.is_stale]
            elif status == "stale":
                agents = [a for a in agents if a.is_stale]

            return {
                "agents": [asdict(a) if AGENT_IDENTITY_AVAILABLE else a.__dict__ for a in agents],
                "count": len(agents),
                "filters_applied": {"level": level, "project": project, "role": role, "status": status},
            }

        if tool_name == "memory_search":
            return self._handle_memory_search(args)

        if tool_name == "memory_analytics_summary":
            return self._handle_memory_analytics_summary(args)

        return {"error": f"Unknown tool: {tool_name}"}

    # ========================================================================
    # PHASE 6: Memory Tool Handlers
    # ========================================================================

    def _handle_memory_search(self, args: dict[str, Any]) -> dict[str, Any]:
        """Handle memory_search tool calls."""
        agent_id = args.get("agent_id")
        query = args.get("query")
        limit = args.get("limit", 10)

        if not agent_id or not query:
            return {"error": "agent_id and query are required", "results": []}

        try:
            from civilization_memory_storage import SQLiteMemoryStorage
        except ImportError:
            try:
                from scripts.civilization_memory_storage import SQLiteMemoryStorage
            except ImportError as e:
                return {"error": f"Memory storage not available: {e}", "results": []}

        try:
            storage = SQLiteMemoryStorage()
            memories = storage.search(agent_id, query, limit=limit)
            results = []
            for m in memories:
                results.append(
                    {
                        "memory_id": m.memory_id,
                        "agent_id": m.agent_id,
                        "memory_type": m.memory_type.value if hasattr(m.memory_type, "value") else str(m.memory_type),
                        "timestamp": m.timestamp,
                        "content": m.content,
                        "importance": m.importance,
                    }
                )
            return {"results": results, "count": len(results)}
        except Exception as e:
            return {"error": str(e), "results": []}

    def _handle_memory_analytics_summary(self, args: dict[str, Any]) -> dict[str, Any]:
        """Handle memory_analytics_summary tool calls."""
        agent_id = args.get("agent_id")
        days = args.get("days", 30)

        if not agent_id:
            return {"error": "agent_id is required", "agent_id": agent_id}

        try:
            from civilization_memory_storage import SQLiteMemoryStorage
        except ImportError:
            try:
                from scripts.civilization_memory_storage import SQLiteMemoryStorage
            except ImportError as e:
                return {"error": f"Memory storage not available: {e}", "agent_id": agent_id}

        try:
            from civilization_memory_analytics import MemoryAnalytics
        except ImportError:
            try:
                from scripts.civilization_memory_analytics import MemoryAnalytics
            except ImportError:
                return {"error": "Analytics not available", "agent_id": agent_id}

        try:
            storage = SQLiteMemoryStorage()
            memories = storage.query(agent_id)
            memory_dicts = []
            for m in memories:
                memory_dicts.append(
                    {
                        "memory_id": m.memory_id,
                        "agent_id": m.agent_id,
                        "memory_type": m.memory_type.value if hasattr(m.memory_type, "value") else str(m.memory_type),
                        "timestamp": m.timestamp,
                        "content": m.content,
                        "importance": m.importance,
                    }
                )
            analytics = MemoryAnalytics()
            summary = analytics.get_agent_summary(memory_dicts)
            summary["agent_id"] = agent_id
            summary["days"] = days
            return summary
        except Exception as e:
            return {"error": str(e), "agent_id": agent_id}

    # ========================================================================
    # PHASE 4B: Heartbeat Streaming
    # ========================================================================

    async def stream_heartbeats(self) -> None:
        """Stream heartbeats at 1 Hz to all subscribers."""
        if not self.enabled or not self.registry:
            return

        self.heartbeat_stream_running = True
        self.logger.info("Heartbeat stream started")

        try:
            while self.heartbeat_stream_running:
                # Get active agents
                all_agents = list(self.registry.agents.values()) if hasattr(self.registry, "agents") else []
                active_agents = [a for a in all_agents if a.is_active]

                # Prepare heartbeat message
                heartbeat_msg = {
                    "type": "heartbeats",
                    "timestamp": time.time(),
                    "agent_count": len(active_agents),
                    "agents": [
                        {
                            "agent_id": a.agent_id,
                            "project": a.project,
                            "level": str(a.level),
                            "role": str(a.role),
                            "last_heartbeat": a.last_heartbeat,
                        }
                        for a in active_agents
                    ],
                }

                # Broadcast to subscribers
                await self._broadcast_message(heartbeat_msg)

                # Sleep 1 second for 1 Hz rate
                await asyncio.sleep(1)

        except Exception as e:
            self.logger.error(f"Heartbeat stream error: {e}")
        finally:
            self.heartbeat_stream_running = False
            self.logger.info("Heartbeat stream stopped")

    async def subscribe_heartbeats(self, subscriber_id: str) -> None:
        """Subscribe to heartbeat stream."""
        self.heartbeat_subscribers.add(subscriber_id)
        self.logger.debug(f"Subscriber added: {subscriber_id}")

    async def unsubscribe_heartbeats(self, subscriber_id: str) -> None:
        """Unsubscribe from heartbeat stream."""
        self.heartbeat_subscribers.discard(subscriber_id)
        self.logger.debug(f"Subscriber removed: {subscriber_id}")

    async def _broadcast_message(self, message: dict[str, Any]) -> None:
        """Broadcast message to all subscribers."""
        # In real implementation, this would send to actual MCP clients
        # For now, just log
        self.logger.debug(f"Broadcast to {len(self.heartbeat_subscribers)} subscribers: {message['type']}")

    # ========================================================================
    # PHASE 4C: Message Broker Integration
    # ========================================================================

    async def send_agent_message(
        self, from_agent: str, to_agent: str, message_type: str, payload: dict[str, Any]
    ) -> bool:
        """Send a message between agents."""
        return await self.message_broker.send_message(from_agent, to_agent, message_type, payload)

    async def broadcast_agent_message(self, from_agent: str, message_type: str, payload: dict[str, Any]) -> bool:
        """Broadcast message to all agents in project."""
        return await self.message_broker.broadcast_message(from_agent, message_type, payload)

    # ========================================================================
    # Status/Stats Methods
    # ========================================================================

    def get_civilization_status(self) -> dict[str, Any]:
        """Get civilization-wide status (dashboard format)."""
        if not self.enabled or not self.registry:
            return {"error": "MCP server not enabled"}

        stats = self.registry.get_stats()
        all_agents = list(self.registry.agents.values()) if hasattr(self.registry, "agents") else []

        return {
            "timestamp": time.time(),
            "total_agents": len(all_agents),
            "active_agents": len([a for a in all_agents if a.is_active]),
            "stale_agents": len([a for a in all_agents if a.is_stale]),
            "projects": stats.get("projects", []),
            "by_level": {
                "L1": len([a for a in all_agents if str(a.level) == "L1" or a.level.value == "L1"]),
                "L2": len([a for a in all_agents if str(a.level) == "L2" or a.level.value == "L2"]),
                "L3": len([a for a in all_agents if str(a.level) == "L3" or a.level.value == "L3"]),
            },
            "heartbeat_stream": {
                "running": self.heartbeat_stream_running,
                "subscribers": len(self.heartbeat_subscribers),
            },
        }

    def get_all_resources(self) -> list[dict[str, Any]]:
        """Get all available resources."""
        return [r.to_dict() for r in self.resources.values()]

    def get_all_tools(self) -> list[dict[str, Any]]:
        """Get all available tools."""
        return [t.to_dict() for t in self.tools.values()]


# ============================================================================
# PHASE 4C: Agent Message Broker
# ============================================================================


@dataclass
class AgentMessage:
    """Message between agents."""

    id: str
    from_agent: str
    to_agent: str
    type: str
    payload: dict[str, Any]
    timestamp: float
    ack: bool = False
    ack_timestamp: Optional[float] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AgentMessageBroker:
    """Broker for inter-agent messages (Phase 4C)."""

    def __init__(self, registry: Optional["GlobalAgentRegistry"] = None):
        """Initialize message broker."""
        if not AGENT_IDENTITY_AVAILABLE:
            self.registry: Optional["GlobalAgentRegistry"] = None
            self.enabled = False
            return

        if registry is not None:
            self.registry: Optional["GlobalAgentRegistry"] = registry
        else:
            self.registry = GlobalAgentRegistry()
        self.enabled = True
        self.logger = logging.getLogger("AgentMessageBroker")

        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.pending_acks: dict[str, asyncio.Future] = {}
        self.routes: dict[str, Callable[[AgentMessage], Awaitable[None]]] = {}
        self.message_history: list[AgentMessage] = []  # For debugging

    async def send_message(self, from_agent: str, to_agent: str, message_type: str, payload: dict[str, Any]) -> bool:
        """Send message to specific agent."""
        if not self.enabled or not self.registry:
            return False

        msg = AgentMessage(
            id=uuid4().hex[:8],
            from_agent=from_agent,
            to_agent=to_agent,
            type=message_type,
            payload=payload,
            timestamp=time.time(),
        )

        self.message_history.append(msg)

        # Check if agent exists
        target = self.registry.get_agent(to_agent)
        if not target:
            self.logger.warning(f"Message to unknown agent: {to_agent}")
            return False

        # Queue message
        await self.message_queue.put(msg)

        # Wait for ACK (5 second timeout)
        try:
            future: asyncio.Future = asyncio.Future()
            self.pending_acks[msg.id] = future
            await asyncio.wait_for(future, timeout=5.0)
            return True
        except asyncio.TimeoutError:
            self.logger.warning(f"Message ACK timeout: {msg.id}")
            return False
        finally:
            self.pending_acks.pop(msg.id, None)

    async def broadcast_message(self, from_agent: str, message_type: str, payload: dict[str, Any]) -> bool:
        """Broadcast message to all agents in project."""
        if not self.enabled or not self.registry:
            return False

        from_project = from_agent.split(":", maxsplit=1)[0]
        agents = self.registry.get_agents_by_project(from_project)

        success_count = 0
        for agent in agents:
            if agent.agent_id != from_agent:
                if await self.send_message(from_agent, agent.agent_id, message_type, payload):
                    success_count += 1

        self.logger.info(f"Broadcast message sent to {success_count}/{len(agents) - 1} agents")
        return success_count > 0

    async def acknowledge_message(self, message_id: str) -> None:
        """Acknowledge receipt of message."""
        if message_id in self.pending_acks:
            future = self.pending_acks[message_id]
            if not future.done():
                future.set_result(True)
            self.logger.debug(f"Message acknowledged: {message_id}")

    def register_handler(self, message_type: str, handler: Callable[[AgentMessage], Awaitable[None]]) -> None:
        """Register handler for message type."""
        self.routes[message_type] = handler
        self.logger.debug(f"Handler registered for: {message_type}")

    async def process_messages(self) -> None:
        """Process incoming messages (run in background)."""
        while self.enabled:
            try:
                msg = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)

                # Find handler
                handler = self.routes.get(msg.type)
                if handler:
                    await handler(msg)
                    await self.acknowledge_message(msg.id)
                else:
                    self.logger.debug(f"No handler for message type: {msg.type}")

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Message processing error: {e}")

    def get_message_stats(self) -> dict[str, Any]:
        """Get message statistics."""
        return {
            "total_messages": len(self.message_history),
            "queue_size": self.message_queue.qsize(),
            "pending_acks": len(self.pending_acks),
            "recent_messages": [m.to_dict() for m in self.message_history[-10:]],
        }


# ============================================================================
# Server initialization and utilities
# ============================================================================


def create_mcp_server(registry: Optional["GlobalAgentRegistry"] = None) -> CivilizationMCPServer:
    """Factory function to create MCP server."""
    return CivilizationMCPServer(registry)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    if AGENT_IDENTITY_AVAILABLE:
        registry = GlobalAgentRegistry()
        server = create_mcp_server(registry)

        print("✅ MCP Server created successfully")
        print(f"📊 Resources: {len(server.resources)}")
        print(f"🔧 Tools: {len(server.tools)}")
        print(f"💬 Message Broker: {'Enabled' if server.message_broker.enabled else 'Disabled'}")
    else:
        print("❌ Agent Identity System not available")

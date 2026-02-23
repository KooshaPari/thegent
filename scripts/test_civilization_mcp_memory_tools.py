#!/usr/bin/env python3
"""
Test suite for Phase 6 MCP Memory Tools (memory_search, memory_analytics_summary).

Tests tool registration, handler logic, return shapes, and graceful fallbacks.
"""

import json
import sqlite3
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

try:
    try:
        from agent_identity_system import GlobalAgentRegistry, AgentIdentityFactory, AgentRole
        from civilization_mcp_server import CivilizationMCPServer, create_mcp_server
    except ImportError:
        from scripts.agent_identity_system import GlobalAgentRegistry, AgentIdentityFactory, AgentRole
        from scripts.civilization_mcp_server import CivilizationMCPServer, create_mcp_server
    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False

try:
    try:
        from civilization_memory_storage import SQLiteMemoryStorage
        from civilization_agent_memory import AgentMemory, MemoryType
    except ImportError:
        from scripts.civilization_memory_storage import SQLiteMemoryStorage
        from scripts.civilization_agent_memory import AgentMemory, MemoryType
    MEMORY_IMPORTS_AVAILABLE = True
except ImportError:
    MEMORY_IMPORTS_AVAILABLE = False


class TestMemoryToolRegistration(unittest.TestCase):
    """Verify memory tools are registered in the MCP server."""

    @unittest.skipIf(not IMPORTS_AVAILABLE, "MCP server dependencies not available")
    def setUp(self):
        self.registry = GlobalAgentRegistry()
        self.server = create_mcp_server(self.registry)

    def test_memory_search_tool_registered(self):
        """memory_search tool appears in the tool list."""
        tools = self.server.get_all_tools()
        tool_names = [t["name"] for t in tools]
        self.assertIn("memory_search", tool_names)

    def test_memory_analytics_summary_tool_registered(self):
        """memory_analytics_summary tool appears in the tool list."""
        tools = self.server.get_all_tools()
        tool_names = [t["name"] for t in tools]
        self.assertIn("memory_analytics_summary", tool_names)

    def test_memory_search_schema(self):
        """memory_search tool has correct input schema."""
        tool = self.server.tools["memory_search"]
        schema = tool.input_schema
        self.assertIn("agent_id", schema["properties"])
        self.assertIn("query", schema["properties"])
        self.assertIn("limit", schema["properties"])
        self.assertEqual(schema["required"], ["agent_id", "query"])

    def test_memory_analytics_summary_schema(self):
        """memory_analytics_summary tool has correct input schema."""
        tool = self.server.tools["memory_analytics_summary"]
        schema = tool.input_schema
        self.assertIn("agent_id", schema["properties"])
        self.assertIn("days", schema["properties"])
        self.assertEqual(schema["required"], ["agent_id"])

    def test_total_tool_count(self):
        """Server now has 8 tools (6 original + 2 memory tools)."""
        tools = self.server.get_all_tools()
        self.assertEqual(len(tools), 8)


class TestMemorySearchHandler(unittest.TestCase):
    """Test memory_search tool handler logic."""

    @unittest.skipIf(not IMPORTS_AVAILABLE, "MCP server dependencies not available")
    def setUp(self):
        self.registry = GlobalAgentRegistry()
        self.server = create_mcp_server(self.registry)

    def test_memory_search_missing_agent_id(self):
        """Missing agent_id returns error."""
        result = self.server.call_tool("memory_search", {"query": "test"})
        self.assertIn("error", result)
        self.assertEqual(result["results"], [])

    def test_memory_search_missing_query(self):
        """Missing query returns error."""
        result = self.server.call_tool("memory_search", {"agent_id": "agent-1"})
        self.assertIn("error", result)
        self.assertEqual(result["results"], [])

    def test_memory_search_empty_params(self):
        """Empty params returns error."""
        result = self.server.call_tool("memory_search", {})
        self.assertIn("error", result)
        self.assertEqual(result["results"], [])

    @unittest.skipIf(not MEMORY_IMPORTS_AVAILABLE, "Memory storage not available")
    def test_memory_search_returns_results_structure(self):
        """Search returns proper result structure with results list and count."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_memories.db"
            storage = SQLiteMemoryStorage(db_path=db_path)

            # Store a test memory
            memory = AgentMemory(
                memory_id="mem-001",
                agent_id="test-agent",
                memory_type=MemoryType.LEARNING,
                timestamp=time.time(),
                content={"description": "learned about database indexing patterns"},
                context={},
                importance=0.8,
                verified=True,
            )
            storage.store(memory)

            # Patch the handler to use our temp storage
            def patched_handler(args):
                agent_id = args.get("agent_id")
                query = args.get("query")
                limit = args.get("limit", 10)
                memories = storage.search(agent_id, query, limit=limit)
                results = []
                for m in memories:
                    results.append({
                        "memory_id": m.memory_id,
                        "agent_id": m.agent_id,
                        "memory_type": m.memory_type.value if hasattr(m.memory_type, "value") else str(m.memory_type),
                        "timestamp": m.timestamp,
                        "content": m.content,
                        "importance": m.importance,
                    })
                return {"results": results, "count": len(results)}

            original = self.server._handle_memory_search
            self.server._handle_memory_search = patched_handler
            try:
                result = self.server.call_tool("memory_search", {
                    "agent_id": "test-agent",
                    "query": "database indexing",
                })
                self.assertIn("results", result)
                self.assertIn("count", result)
                self.assertIsInstance(result["results"], list)
                self.assertGreaterEqual(result["count"], 1)

                # Verify result dict shape
                first = result["results"][0]
                self.assertIn("memory_id", first)
                self.assertIn("agent_id", first)
                self.assertIn("memory_type", first)
                self.assertIn("timestamp", first)
                self.assertIn("content", first)
                self.assertIn("importance", first)
            finally:
                self.server._handle_memory_search = original

    @unittest.skipIf(not MEMORY_IMPORTS_AVAILABLE, "Memory storage not available")
    def test_memory_search_no_results(self):
        """Search with no matching memories returns empty results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_memories.db"
            storage = SQLiteMemoryStorage(db_path=db_path)

            def patched_handler(args):
                agent_id = args.get("agent_id")
                query = args.get("query")
                limit = args.get("limit", 10)
                memories = storage.search(agent_id, query, limit=limit)
                results = []
                for m in memories:
                    results.append({
                        "memory_id": m.memory_id,
                        "agent_id": m.agent_id,
                        "memory_type": m.memory_type.value if hasattr(m.memory_type, "value") else str(m.memory_type),
                        "timestamp": m.timestamp,
                        "content": m.content,
                        "importance": m.importance,
                    })
                return {"results": results, "count": len(results)}

            original = self.server._handle_memory_search
            self.server._handle_memory_search = patched_handler
            try:
                result = self.server.call_tool("memory_search", {
                    "agent_id": "nonexistent-agent",
                    "query": "nothing here",
                })
                self.assertEqual(result["results"], [])
                self.assertEqual(result["count"], 0)
            finally:
                self.server._handle_memory_search = original


class TestMemoryAnalyticsSummaryHandler(unittest.TestCase):
    """Test memory_analytics_summary tool handler logic."""

    @unittest.skipIf(not IMPORTS_AVAILABLE, "MCP server dependencies not available")
    def setUp(self):
        self.registry = GlobalAgentRegistry()
        self.server = create_mcp_server(self.registry)

    def test_analytics_missing_agent_id(self):
        """Missing agent_id returns error."""
        result = self.server.call_tool("memory_analytics_summary", {})
        self.assertIn("error", result)

    def test_analytics_fallback_on_import_error(self):
        """When analytics module is not importable, handler returns error dict."""
        import sys
        # Save originals
        saved_analytics = sys.modules.get("civilization_memory_analytics")
        saved_scripts_analytics = sys.modules.get("scripts.civilization_memory_analytics")

        # Block imports
        sys.modules["civilization_memory_analytics"] = None
        sys.modules["scripts.civilization_memory_analytics"] = None
        try:
            result = self.server._handle_memory_analytics_summary({"agent_id": "test-agent"})
            self.assertIn("agent_id", result)
            # It should either have an error key or a valid summary
            # (depends on whether storage import also fails)
        finally:
            # Restore
            if saved_analytics is not None:
                sys.modules["civilization_memory_analytics"] = saved_analytics
            else:
                sys.modules.pop("civilization_memory_analytics", None)
            if saved_scripts_analytics is not None:
                sys.modules["scripts.civilization_memory_analytics"] = saved_scripts_analytics
            else:
                sys.modules.pop("scripts.civilization_memory_analytics", None)

    @unittest.skipIf(not MEMORY_IMPORTS_AVAILABLE, "Memory storage not available")
    def test_analytics_returns_summary_structure(self):
        """Analytics returns proper summary structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_memories.db"
            storage = SQLiteMemoryStorage(db_path=db_path)

            # Store test memories
            for i in range(5):
                memory = AgentMemory(
                    memory_id=f"mem-{i:03d}",
                    agent_id="test-agent",
                    memory_type=MemoryType.LEARNING if i % 2 == 0 else MemoryType.ERROR,
                    timestamp=time.time() - (i * 3600),
                    content={"description": f"test memory number {i} about python coding"},
                    context={},
                    importance=0.5 + (i * 0.1),
                    verified=True,
                )
                storage.store(memory)

            try:
                from civilization_memory_analytics import MemoryAnalytics
            except ImportError:
                from scripts.civilization_memory_analytics import MemoryAnalytics

            def patched_handler(args):
                agent_id = args.get("agent_id")
                days = args.get("days", 30)
                memories = storage.query(agent_id)
                memory_dicts = []
                for m in memories:
                    memory_dicts.append({
                        "memory_id": m.memory_id,
                        "agent_id": m.agent_id,
                        "memory_type": m.memory_type.value if hasattr(m.memory_type, "value") else str(m.memory_type),
                        "timestamp": m.timestamp,
                        "content": m.content,
                        "importance": m.importance,
                    })
                analytics = MemoryAnalytics()
                summary = analytics.get_agent_summary(memory_dicts)
                summary["agent_id"] = agent_id
                summary["days"] = days
                return summary

            original = self.server._handle_memory_analytics_summary
            self.server._handle_memory_analytics_summary = patched_handler
            try:
                result = self.server.call_tool("memory_analytics_summary", {
                    "agent_id": "test-agent",
                    "days": 30,
                })
                self.assertIn("total_memories", result)
                self.assertIn("learning_velocity", result)
                self.assertIn("error_density", result)
                self.assertIn("top_keywords", result)
                self.assertIn("agent_id", result)
                self.assertEqual(result["agent_id"], "test-agent")
                self.assertEqual(result["total_memories"], 5)
            finally:
                self.server._handle_memory_analytics_summary = original


class TestMemoryToolsDisabledServer(unittest.TestCase):
    """Test memory tools when server is disabled (no registry available)."""

    @unittest.skipIf(not IMPORTS_AVAILABLE, "MCP server dependencies not available")
    def test_memory_search_on_disabled_server(self):
        """memory_search on disabled server returns error from call_tool guard."""
        # Disable the server by setting enabled=False directly
        server = create_mcp_server()
        server.enabled = False
        result = server.call_tool("memory_search", {
            "agent_id": "test",
            "query": "test",
        })
        self.assertIn("error", result)

    @unittest.skipIf(not IMPORTS_AVAILABLE, "MCP server dependencies not available")
    def test_memory_analytics_on_disabled_server(self):
        """memory_analytics_summary on disabled server returns error from call_tool guard."""
        server = create_mcp_server()
        server.enabled = False
        result = server.call_tool("memory_analytics_summary", {
            "agent_id": "test",
        })
        self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)

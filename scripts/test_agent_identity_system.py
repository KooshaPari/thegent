#!/usr/bin/env python3
"""Tests for Agent Identity & Discovery System."""

import tempfile
from pathlib import Path
from unittest import TestCase
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_identity_system import (
    AgentIdentity,
    AgentLevel,
    AgentRole,
    GlobalAgentRegistry,
    AgentIdentityFactory,
)


class TestAgentIdentity(TestCase):
    """Tests for AgentIdentity dataclass."""

    def test_agent_id_format(self):
        """Test agent ID string format."""
        identity = AgentIdentity(
            project="thegent",
            uuid="abc123",
            level=AgentLevel.L1_STRATEGIC,
            role=AgentRole.COORDINATOR,
        )
        expected = "thegent:abc123:L1:coordinator"
        self.assertEqual(identity.agent_id, expected)

    def test_to_dict_conversion(self):
        """Test conversion to dictionary."""
        identity = AgentIdentity(
            project="thegent",
            uuid="abc123",
            level=AgentLevel.L2_WORKER,
            role=AgentRole.BUILDER,
        )
        data = identity.to_dict()
        self.assertEqual(data["project"], "thegent")
        self.assertEqual(data["level"], "L2")
        self.assertEqual(data["role"], "builder")

    def test_from_dict_conversion(self):
        """Test creation from dictionary."""
        data = {
            "project": "thegent",
            "uuid": "abc123",
            "level": "L1",
            "role": "coordinator",
            "created_at": 1234567890.0,
            "last_heartbeat": 1234567890.0,
            "capabilities": [],
            "scope_tags": {},
            "parent_agent_id": None,
            "child_agent_ids": [],
            "peer_agent_ids": [],
            "is_active": True,
            "status_message": "healthy",
            "session_id": None,
            "mcp_endpoint": None,
        }
        identity = AgentIdentity.from_dict(data)
        self.assertEqual(identity.project, "thegent")
        self.assertEqual(identity.level, AgentLevel.L1_STRATEGIC)
        self.assertEqual(identity.role, AgentRole.COORDINATOR)

    def test_roundtrip_conversion(self):
        """Test to_dict -> from_dict roundtrip."""
        identity1 = AgentIdentity(
            project="kush",
            uuid="xyz789",
            level=AgentLevel.L3_EXECUTOR,
            role=AgentRole.GENERIC,
            capabilities=["task_execution"],
        )
        data = identity1.to_dict()
        identity2 = AgentIdentity.from_dict(data)
        self.assertEqual(identity1.agent_id, identity2.agent_id)
        self.assertEqual(identity1.project, identity2.project)
        self.assertEqual(identity1.capabilities, identity2.capabilities)


class TestGlobalAgentRegistry(TestCase):
    """Tests for GlobalAgentRegistry."""

    def setUp(self):
        """Set up test registry."""
        self.temp_dir = tempfile.mkdtemp()
        self.registry_path = Path(self.temp_dir) / "registry.json"
        self.registry = GlobalAgentRegistry(str(self.registry_path))

    def tearDown(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_register_agent(self):
        """Test agent registration."""
        identity = AgentIdentity(
            project="test",
            uuid="test123",
            level=AgentLevel.L1_STRATEGIC,
            role=AgentRole.COORDINATOR,
        )
        agent_id = self.registry.register_agent(identity)
        self.assertIsNotNone(agent_id)
        self.assertEqual(agent_id, identity.agent_id)

    def test_get_agent(self):
        """Test retrieving agent."""
        identity = AgentIdentity(
            project="test",
            uuid="test123",
            level=AgentLevel.L1_STRATEGIC,
            role=AgentRole.COORDINATOR,
        )
        self.registry.register_agent(identity)
        retrieved = self.registry.get_agent(identity.agent_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.project, "test")

    def test_unregister_agent(self):
        """Test agent unregistration."""
        identity = AgentIdentity(
            project="test",
            uuid="test123",
            level=AgentLevel.L1_STRATEGIC,
            role=AgentRole.COORDINATOR,
        )
        self.registry.register_agent(identity)
        result = self.registry.unregister_agent(identity.agent_id)
        self.assertTrue(result)
        retrieved = self.registry.get_agent(identity.agent_id)
        self.assertIsNone(retrieved)

    def test_get_agents_by_project(self):
        """Test filtering agents by project."""
        for i in range(3):
            identity = AgentIdentity(
                project="project1",
                uuid=f"agent{i}",
                level=AgentLevel.L1_STRATEGIC,
                role=AgentRole.COORDINATOR,
            )
            self.registry.register_agent(identity)

        for i in range(2):
            identity = AgentIdentity(
                project="project2",
                uuid=f"agent_p2_{i}",
                level=AgentLevel.L2_WORKER,
                role=AgentRole.BUILDER,
            )
            self.registry.register_agent(identity)

        project1_agents = self.registry.get_agents_by_project("project1")
        project2_agents = self.registry.get_agents_by_project("project2")

        self.assertEqual(len(project1_agents), 3)
        self.assertEqual(len(project2_agents), 2)

    def test_get_agents_by_level(self):
        """Test filtering agents by level."""
        identity_l1 = AgentIdentity(
            project="test",
            uuid="l1",
            level=AgentLevel.L1_STRATEGIC,
            role=AgentRole.COORDINATOR,
        )
        identity_l2 = AgentIdentity(
            project="test",
            uuid="l2",
            level=AgentLevel.L2_WORKER,
            role=AgentRole.BUILDER,
        )
        self.registry.register_agent(identity_l1)
        self.registry.register_agent(identity_l2)

        l1_agents = self.registry.get_agents_by_level(AgentLevel.L1_STRATEGIC)
        l2_agents = self.registry.get_agents_by_level(AgentLevel.L2_WORKER)

        self.assertEqual(len(l1_agents), 1)
        self.assertEqual(len(l2_agents), 1)

    def test_set_relationship(self):
        """Test setting parent-child relationships."""
        parent = AgentIdentity(
            project="test",
            uuid="parent",
            level=AgentLevel.L1_STRATEGIC,
            role=AgentRole.COORDINATOR,
        )
        child = AgentIdentity(
            project="test",
            uuid="child",
            level=AgentLevel.L2_WORKER,
            role=AgentRole.BUILDER,
        )
        self.registry.register_agent(parent)
        self.registry.register_agent(child)

        result = self.registry.set_relationship(parent.agent_id, child.agent_id)
        self.assertTrue(result)

        # Verify relationship
        updated_parent = self.registry.get_agent(parent.agent_id)
        updated_child = self.registry.get_agent(child.agent_id)

        self.assertIn(child.agent_id, updated_parent.child_agent_ids)
        self.assertEqual(updated_child.parent_agent_id, parent.agent_id)

    def test_get_hierarchy(self):
        """Test hierarchy retrieval."""
        # Create hierarchy: L1 -> L2 -> L3
        parent = AgentIdentity(
            project="test",
            uuid="parent",
            level=AgentLevel.L1_STRATEGIC,
            role=AgentRole.COORDINATOR,
        )
        child1 = AgentIdentity(
            project="test",
            uuid="child1",
            level=AgentLevel.L2_WORKER,
            role=AgentRole.BUILDER,
        )
        child2 = AgentIdentity(
            project="test",
            uuid="child2",
            level=AgentLevel.L3_EXECUTOR,
            role=AgentRole.GENERIC,
        )

        self.registry.register_agent(parent)
        self.registry.register_agent(child1)
        self.registry.register_agent(child2)

        self.registry.set_relationship(parent.agent_id, child1.agent_id)
        self.registry.set_relationship(child1.agent_id, child2.agent_id)

        hierarchy = self.registry.get_hierarchy(parent.agent_id)
        self.assertEqual(hierarchy["agent_id"], parent.agent_id)
        self.assertEqual(len(hierarchy["children"]), 1)
        self.assertEqual(len(hierarchy["children"][0]["children"]), 1)

    def test_persistence_to_disk(self):
        """Test registry persistence to disk."""
        identity = AgentIdentity(
            project="test",
            uuid="persist",
            level=AgentLevel.L1_STRATEGIC,
            role=AgentRole.COORDINATOR,
        )
        self.registry.register_agent(identity)

        # Verify file was created
        self.assertTrue(self.registry_path.exists())

        # Load registry from same path
        registry2 = GlobalAgentRegistry(str(self.registry_path))
        retrieved = registry2.get_agent(identity.agent_id)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.project, "test")

    def test_get_stats(self):
        """Test registry statistics."""
        # Create various agents
        for level, role in [
            (AgentLevel.L1_STRATEGIC, AgentRole.COORDINATOR),
            (AgentLevel.L2_WORKER, AgentRole.BUILDER),
            (AgentLevel.L2_WORKER, AgentRole.RESEARCHER),
            (AgentLevel.L3_EXECUTOR, AgentRole.GENERIC),
        ]:
            identity = AgentIdentity(
                project="test",
                uuid=f"{level.value}_{role.value}",
                level=level,
                role=role,
            )
            self.registry.register_agent(identity)

        stats = self.registry.get_stats()
        self.assertEqual(stats["total_agents"], 4)
        self.assertEqual(stats["by_level"]["L1"], 1)
        self.assertEqual(stats["by_level"]["L2"], 2)
        self.assertEqual(stats["by_level"]["L3"], 1)


class TestAgentIdentityFactory(TestCase):
    """Tests for AgentIdentityFactory."""

    def setUp(self):
        """Set up test factory."""
        self.temp_dir = tempfile.mkdtemp()
        self.registry_path = Path(self.temp_dir) / "registry.json"
        self.registry = GlobalAgentRegistry(str(self.registry_path))
        self.factory = AgentIdentityFactory(self.registry)

    def tearDown(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_l1_agent(self):
        """Test L1 agent creation."""
        agent = self.factory.create_l1_agent("test")
        self.assertEqual(agent.level, AgentLevel.L1_STRATEGIC)
        self.assertEqual(agent.project, "test")

        # Verify it's registered
        retrieved = self.registry.get_agent(agent.agent_id)
        self.assertIsNotNone(retrieved)

    def test_create_l2_agent(self):
        """Test L2 agent creation with parent."""
        l1 = self.factory.create_l1_agent("test")
        l2 = self.factory.create_l2_agent("test", AgentRole.BUILDER, l1.agent_id)

        self.assertEqual(l2.level, AgentLevel.L2_WORKER)
        self.assertEqual(l2.parent_agent_id, l1.agent_id)

        # Verify relationship is set
        parent = self.registry.get_agent(l1.agent_id)
        self.assertIn(l2.agent_id, parent.child_agent_ids)

    def test_create_l3_agent(self):
        """Test L3 agent creation with parent."""
        l1 = self.factory.create_l1_agent("test")
        l2 = self.factory.create_l2_agent("test", AgentRole.BUILDER, l1.agent_id)
        l3 = self.factory.create_l3_agent("test", l2.agent_id)

        self.assertEqual(l3.level, AgentLevel.L3_EXECUTOR)
        self.assertEqual(l3.parent_agent_id, l2.agent_id)

        # Verify relationship is set
        parent = self.registry.get_agent(l2.agent_id)
        self.assertIn(l3.agent_id, parent.child_agent_ids)

    def test_create_full_hierarchy(self):
        """Test creating a complete hierarchy."""
        l1 = self.factory.create_l1_agent("test")
        l2_builder = self.factory.create_l2_agent(
            "test", AgentRole.BUILDER, l1.agent_id
        )
        self.factory.create_l2_agent("test", AgentRole.RESEARCHER, l1.agent_id)
        self.factory.create_l3_agent("test", l2_builder.agent_id)

        stats = self.registry.get_stats()
        self.assertEqual(stats["total_agents"], 4)
        self.assertEqual(stats["by_level"]["L1"], 1)
        self.assertEqual(stats["by_level"]["L2"], 2)
        self.assertEqual(stats["by_level"]["L3"], 1)


if __name__ == "__main__":
    import unittest
    unittest.main()

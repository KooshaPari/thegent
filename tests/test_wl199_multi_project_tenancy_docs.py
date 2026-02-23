"""Tests for WL-199: Multi-Project Tenancy Autosync Docs.

Verifies that TenancyDocEntry dataclass is created correctly,
MultiProjectTenancyDocs registers projects, retrieves entries,
and renders markdown tables properly.

# @trace WL-199
"""

from __future__ import annotations

import pytest

from thegent.integrations.multi_project_tenancy_docs import (
    MultiProjectTenancyDocs,
    TenancyDocEntry,
)


class TestTenancyDocEntry:
    """WL-199: TenancyDocEntry dataclass."""

    @pytest.mark.requirement("WL-199")
    def test_entry_creation_with_all_fields(self):
        """TenancyDocEntry can be created with project_id, namespace, and description."""
        entry = TenancyDocEntry(
            project_id="proj-123",
            namespace="prod",
            description="Production environment",
        )

        assert entry.project_id == "proj-123"
        assert entry.namespace == "prod"
        assert entry.description == "Production environment"

    @pytest.mark.requirement("WL-199")
    def test_entry_creation_without_description(self):
        """TenancyDocEntry description defaults to empty string."""
        entry = TenancyDocEntry(project_id="proj-456", namespace="staging")

        assert entry.project_id == "proj-456"
        assert entry.namespace == "staging"
        assert entry.description == ""


class TestMultiProjectTenancyDocs:
    """WL-199: MultiProjectTenancyDocs registration and retrieval."""

    @pytest.mark.requirement("WL-199")
    def test_register_project(self):
        """register() stores project entry and returns it."""
        docs = MultiProjectTenancyDocs()

        entry = docs.register(
            project_id="proj-a",
            namespace="prod",
            description="Primary production",
        )

        assert entry.project_id == "proj-a"
        assert entry.namespace == "prod"
        assert entry.description == "Primary production"

    @pytest.mark.requirement("WL-199")
    def test_register_multiple_projects(self):
        """Multiple projects can be registered independently."""
        docs = MultiProjectTenancyDocs()

        docs.register("proj-1", "dev")
        docs.register("proj-2", "prod", "Main production")
        docs.register("proj-3", "staging")

        assert docs.get("proj-1").namespace == "dev"
        assert docs.get("proj-2").namespace == "prod"
        assert docs.get("proj-3").namespace == "staging"

    @pytest.mark.requirement("WL-199")
    def test_get_existing_project(self):
        """get() returns the registered entry for a project."""
        docs = MultiProjectTenancyDocs()
        docs.register("proj-x", "test", "Test namespace")

        entry = docs.get("proj-x")

        assert entry.project_id == "proj-x"
        assert entry.namespace == "test"
        assert entry.description == "Test namespace"

    @pytest.mark.requirement("WL-199")
    def test_get_nonexistent_project_raises_keyerror(self):
        """get() raises KeyError for unregistered project."""
        docs = MultiProjectTenancyDocs()

        with pytest.raises(KeyError, match="Project missing-proj not found"):
            docs.get("missing-proj")

    @pytest.mark.requirement("WL-199")
    def test_render_markdown_empty(self):
        """render_markdown() handles empty registry."""
        docs = MultiProjectTenancyDocs()

        result = docs.render_markdown()

        assert "No projects registered" in result

    @pytest.mark.requirement("WL-199")
    def test_render_markdown_single_project(self):
        """render_markdown() includes single registered project in table."""
        docs = MultiProjectTenancyDocs()
        docs.register("proj-1", "prod", "Production")

        result = docs.render_markdown()

        assert "| proj-1 | prod | Production |" in result
        assert "| Project ID | Namespace | Description |" in result

    @pytest.mark.requirement("WL-199")
    def test_render_markdown_multiple_projects(self):
        """render_markdown() includes all projects in markdown table."""
        docs = MultiProjectTenancyDocs()
        docs.register("proj-a", "prod", "Production")
        docs.register("proj-b", "staging", "Staging")
        docs.register("proj-c", "dev")

        result = docs.render_markdown()

        assert "| proj-a | prod | Production |" in result
        assert "| proj-b | staging | Staging |" in result
        assert "| proj-c | dev |  |" in result

    @pytest.mark.requirement("WL-199")
    def test_render_markdown_is_valid_markdown(self):
        """render_markdown() returns valid markdown with table structure."""
        docs = MultiProjectTenancyDocs()
        docs.register("proj-x", "test", "Test project")

        result = docs.render_markdown()

        assert result.startswith("# Multi-Project Tenancy\n")
        assert "| Project ID | Namespace | Description |" in result
        assert "|------------|-----------|-------------|" in result

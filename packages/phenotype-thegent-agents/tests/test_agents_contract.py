"""Contract tests for thegent-agents package."""


class TestAgentsContract:
    """Test thegent-agents package contract."""

    def test_agents_import(self) -> None:
        """Test that phenotype_thegent_agents can be imported."""
        import phenotype_thegent_agents

        assert hasattr(phenotype_thegent_agents, "__all__")
        assert isinstance(phenotype_thegent_agents.__all__, list)

    def test_registry_exports(self) -> None:
        """Test that key registry exports are available."""
        from phenotype_thegent_agents import AGENT_LABELS
        from phenotype_thegent_agents import list_agent_names
        from phenotype_thegent_agents import list_droid_names
        from phenotype_thegent_agents import resolve_agent

        assert AGENT_LABELS is not None
        assert callable(list_agent_names)
        assert callable(list_droid_names)
        assert callable(resolve_agent)

    def test_backward_compat_thegent_agents(self) -> None:
        """Test backward compatibility: thegent.agents should still work."""
        from phenotype_thegent_agents.agents import AGENT_LABELS
        from phenotype_thegent_agents.agents import list_agent_names

        assert AGENT_LABELS is not None
        assert callable(list_agent_names)

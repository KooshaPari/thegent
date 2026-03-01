"""Contract tests for thegent-agents package."""



class TestAgentsContract:
    """Test thegent-agents package contract."""

    def test_agents_import(self) -> None:
        """Test that thegent_agents can be imported."""
        import thegent_agents

        assert hasattr(thegent_agents, "__all__")
        assert isinstance(thegent_agents.__all__, list)

    def test_registry_exports(self) -> None:
        """Test that key registry exports are available."""
        from thegent_agents import AGENT_LABELS
        from thegent_agents import list_agent_names
        from thegent_agents import list_droid_names
        from thegent_agents import resolve_agent

        assert AGENT_LABELS is not None
        assert callable(list_agent_names)
        assert callable(list_droid_names)
        assert callable(resolve_agent)

    def test_backward_compat_thegent_agents(self) -> None:
        """Test backward compatibility: thegent.agents should still work."""
        from thegent_agents.agents import AGENT_LABELS
        from thegent_agents.agents import list_agent_names

        assert AGENT_LABELS is not None
        assert callable(list_agent_names)

"""Contract tests for thegent-cli package."""



class TestCliContract:
    """Test thegent-cli package contract."""

    def test_cli_import(self) -> None:
        """Test that thegent_cli can be imported."""
        import thegent_cli

        assert hasattr(thegent_cli, "__all__")
        assert isinstance(thegent_cli.__all__, list)

    def test_shared_exports(self) -> None:
        """Test that key shared exports are available."""
        from thegent_cli import ThegentSettings
        from thegent_cli import console
        from thegent_cli import list_agent_names

        assert ThegentSettings is not None
        assert console is not None
        assert callable(list_agent_names)

    def test_backward_compat_thegent_cli(self) -> None:
        """Test backward compatibility: thegent.cli should still work."""
        from thegent_cli.cli import ThegentSettings
        from thegent_cli.cli import console

        assert ThegentSettings is not None
        assert console is not None

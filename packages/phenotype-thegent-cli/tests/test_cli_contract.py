"""Contract tests for thegent-cli package."""


class TestCliContract:
    """Test thegent-cli package contract."""

    def test_cli_import(self) -> None:
        """Test that phenotype_thegent_cli can be imported."""
        import phenotype_thegent_cli

        assert hasattr(phenotype_thegent_cli, "__all__")
        assert isinstance(phenotype_thegent_cli.__all__, list)

    def test_shared_exports(self) -> None:
        """Test that key shared exports are available."""
        from phenotype_thegent_cli import ThegentSettings
        from phenotype_thegent_cli import console
        from phenotype_thegent_cli import list_agent_names

        assert ThegentSettings is not None
        assert console is not None
        assert callable(list_agent_names)

    def test_backward_compat_thegent_cli(self) -> None:
        """Test backward compatibility: thegent.cli should still work."""
        from phenotype_thegent_cli.cli import ThegentSettings
        from phenotype_thegent_cli.cli import console

        assert ThegentSettings is not None
        assert console is not None

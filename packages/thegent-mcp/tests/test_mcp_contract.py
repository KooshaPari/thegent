"""Contract tests for thegent-mcp package."""



class TestMcpContract:
    """Test thegent-mcp package contract."""

    def test_mcp_import(self) -> None:
        """Test that thegent_mcp can be imported."""
        import thegent_mcp

        assert hasattr(thegent_mcp, "__all__")
        assert isinstance(thegent_mcp.__all__, list)

    def test_backward_compat_thegent_mcp(self) -> None:
        """Test backward compatibility: thegent.mcp should still work."""
        import thegent

        assert thegent.mcp is not None

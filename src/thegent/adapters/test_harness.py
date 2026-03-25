"""Simple test to verify harness imports and basic structure."""

def test_harness_imports():
    """Test that harness modules can be imported."""
    from thegent.adapters.harness_base import HarnessBase
    from thegent.adapters.claude_harness import ClaudeHarness
    from thegent.adapters.codex_harness import CodexHarness
    from thegent.use_cases.run_harness import RunHarness

    # Verify abstract base is abstract
    assert hasattr(HarnessBase, "get_binary_name")

    # Verify concrete implementations
    claude = ClaudeHarness()
    assert claude.get_binary_name() == "claude"
    assert claude.get_bypass_flag() == "--dangerously-skip-permissions"

    codex = CodexHarness()
    assert codex.get_binary_name() == "codex"
    assert codex.get_bypass_flag() == "--dangerously-bypass-approvals-and-sandbox"

    # Verify use case
    harness_use_case = RunHarness("claude")
    assert harness_use_case.harness is not None

    print("All harness imports and basic tests passed!")


if __name__ == "__main__":
    test_harness_imports()

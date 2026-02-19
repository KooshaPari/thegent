# E2E Tests for Agent-Only Environment

## 🎯 Purpose

In an agent-only environment where **NO humans test the system**, comprehensive E2E test coverage is **CRITICAL**.

## 📋 Coverage Requirements

### 100% Coverage Required

Every CLI command must have E2E tests covering:
1. ✅ Success scenario
2. ✅ Error scenario  
3. ✅ Help/usage output
4. ✅ Output validation

### Test Structure

```python
@pytest.mark.e2e
class TestCommandName:
    """E2E tests for thegent <command>."""
    
    def test_command_exits_zero(self):
        """Command exits with code 0."""
        result = runner.invoke(app, ["command", "args"])
        assert result.exit_code == 0
    
    def test_command_produces_expected_output(self):
        """Command produces expected output."""
        result = runner.invoke(app, ["command", "args"])
        assert "expected" in result.stdout
    
    def test_command_handles_errors_gracefully(self):
        """Command handles errors gracefully."""
        result = runner.invoke(app, ["command", "invalid-args"])
        assert result.exit_code != 0
        assert "error" in result.stderr.lower() or "error" in result.stdout.lower()
```

## 🚀 Running Tests

```bash
# Run all E2E tests
pytest tests/test_e2e_cli.py -v -m e2e

# Run specific test
pytest tests/test_e2e_cli.py::TestListAgents -v

# Run with coverage
pytest tests/test_e2e_cli.py --cov=src/thegent --cov-report=html -m e2e
```

## 📊 Coverage Analysis

Run coverage analysis:
```bash
python scripts/analyze_test_coverage.py
```

This generates:
- Coverage report: `docs/governance/test_coverage_report.json`
- Test templates: `tests/e2e/templates/`

## 🎯 Target: 100% E2E Coverage

Since agents are the only users, we need 100% coverage of all user journeys.

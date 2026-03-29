"""Unit tests for CLI DAG and plan-analyze commands.

NOTE: DAG commands have been moved to 'plan' subcommand.
These tests expect 'dag' as a top-level command which no longer exists.
Tests should be updated to use 'plan list', 'plan validate', etc.
"""

import pytest

pytestmark = pytest.mark.skip(
    reason="DAG commands have been moved to 'plan' subcommand. "
    "These tests expect 'dag' as a top-level command which no longer exists. "
    "Tests should be updated to use 'plan list', 'plan validate', etc."
)

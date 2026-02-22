"""Unit tests for CLI governance commands.

NOTE: Governance escalation commands are not yet implemented.
These tests are for future functionality under 'govern escalate' subcommand.
"""

import pytest

pytestmark = pytest.mark.skip(
    reason="Governance escalation commands are not yet implemented. "
    "Tests are for future functionality under 'govern escalate' subcommand."
)

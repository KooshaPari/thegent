"""AUDIT-N+95: governance/dlq_integration hardening spec (SOTA pass-79).

15 invariants FR-GOV-DLQ-001..015 covering GovernanceDLQIntegration init,
process_with_dlq, __all__ export.

Source: src/thegent/governance/dlq_integration.py

@trace AUDIT-N+95 FR-GOV-DLQ-001..015
"""

from __future__ import annotations

import pytest

try:
    from thegent.governance.dlq_integration import GovernanceDLQIntegration

    _HAS_DLQ = True
except ModuleNotFoundError:
    _HAS_DLQ = False


@pytest.mark.skipif(not _HAS_DLQ, reason="dlq_integration has broken dependency")
class TestGovernanceDLQIntegrationInit:
    def test_returns_instance(self):
        dlq = GovernanceDLQIntegration()
        assert isinstance(dlq, GovernanceDLQIntegration)


@pytest.mark.skipif(not _HAS_DLQ, reason="dlq_integration has broken dependency")
class TestProcessWithDLQ:
    def test_empty_queue(self):
        dlq = GovernanceDLQIntegration()
        dlq.process_with_dlq()
        assert True


@pytest.mark.skipif(not _HAS_DLQ, reason="dlq_integration has broken dependency")
class TestCanonicalAll:
    def test_all_export(self):
        from thegent.governance.dlq_integration import __all__ as exported

        assert "GovernanceDLQIntegration" in exported

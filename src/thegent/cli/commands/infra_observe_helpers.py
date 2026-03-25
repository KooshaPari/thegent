"""Backwards-compatibility wrapper.

This module has been moved to thegent.cli.commands.infra.{module}.
This wrapper maintains backwards compatibility for imports.

Deprecated: Import from thegent.cli.commands.infra.{module} instead.
"""

from __future__ import annotations

# Re-export all symbols from the moved module
from thegent.cli.commands.infra.infra_observe_helpers import *  # noqa: F401, F403

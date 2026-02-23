"""Compatibility shim - redirects to new autosync package.

DEPRECATED: Use thegent.autosync instead.
"""

import warnings

warnings.warn(
    "thegent.integrations.workstream_autosync is deprecated. "
    "Use thegent.autosync instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export from new location
from thegent.autosync import WorkstreamAutosyncRunner

__all__ = ["WorkstreamAutosyncRunner"]

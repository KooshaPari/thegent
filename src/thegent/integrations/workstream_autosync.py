"""Automatic Workstream Reflection (WL-160).

This module has been migrated to autosync package.
"""

import warnings
warnings.warn(
    "workstream_autosync migrated to thegent.autosync. Import from there.",
    DeprecationWarning,
    stacklevel=2
)

from thegent.autosync import WorkstreamAutosyncRunner

__all__ = ["WorkstreamAutosyncRunner"]

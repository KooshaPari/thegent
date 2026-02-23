"""Project CLI commands.

This module has been migrated to project_v2 package.
"""

import warnings
warnings.warn(
    "project module migrated to project_v2. Import from there.",
    DeprecationWarning,
    stacklevel=2
)

from thegent.project_v2 import (
    scaffold_greenfield,
    scaffold_brownfield,
    scaffold_brownfield_agdd,
    scaffold_brownfield_none,
    project_migrate,
    project_doctor,
)

__all__ = [
    "scaffold_greenfield",
    "scaffold_brownfield",
    "scaffold_brownfield_agdd",
    "scaffold_brownfield_none",
    "project_migrate", 
    "project_doctor",
]

"""Project package - modular project management.

Extracted from cli/apps/project.py
"""

from thegent.project_v2.scaffold import (
    scaffold_greenfield,
    scaffold_brownfield, 
    scaffold_brownfield_agdd,
    scaffold_brownfield_none,
)
from thegent.project_v2.migrate import (
    project_migrate,
    resolve_migration_template,
    resolve_migration_mode,
)
from thegent.project_v2.doctor import (
    project_doctor,
    doctor_check,
    doctor_fix,
)

__all__ = [
    "scaffold_greenfield",
    "scaffold_brownfield",
    "scaffold_brownfield_agdd", 
    "scaffold_brownfield_none",
    "project_migrate",
    "resolve_migration_template",
    "resolve_migration_mode",
    "project_doctor",
    "doctor_check",
    "doctor_fix",
]

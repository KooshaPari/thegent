"""Integration modules for external systems."""

# Import modules as they are implemented
try:
    from phenotype_thegent_planning.integration.manage_devkit import ManageDevkitIntegration
except ImportError:
    ManageDevkitIntegration = None

try:
    from phenotype_thegent_planning.integration.work_stream import WorkStreamIntegration
except ImportError:
    WorkStreamIntegration = None

try:
    from phenotype_thegent_planning.integration.plan_system import PlanSystemIntegration
except ImportError:
    PlanSystemIntegration = None

try:
    from phenotype_thegent_planning.integration.unified_config import UnifiedConfigManager
except ImportError:
    UnifiedConfigManager = None

try:
    from phenotype_thegent_planning.integration.harmonized_paths import HarmonizedPathManager
except ImportError:
    HarmonizedPathManager = None

try:
    from phenotype_thegent_planning.integration.consistency_checker import ConsistencyChecker
except ImportError:
    ConsistencyChecker = None

__all__ = [
    "ConsistencyChecker",
    "HarmonizedPathManager",
    "ManageDevkitIntegration",
    "PlanSystemIntegration",
    "UnifiedConfigManager",
    "WorkStreamIntegration",
]

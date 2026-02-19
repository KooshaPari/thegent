"""
thegent Governance Module

Comprehensive governance system for project management, quality assessment,
auditing, and task tracking.
"""

from .audit_framework import (
    AuditFinding,
    AuditFramework,
    AuditResult,
    AuditSeverity,
    AuditStatus,
    AuditType,
)
from .project_setup_enhanced import (
    CICDType,
    GovernanceLevel,
    ProjectGovernanceSetupEnhanced,
    ProjectStructure,
    ProjectType,
)
from .quality_matrix_enhanced import (
    QualityCategory,
    QualityLevel,
    QualityMatrix,
    QualityMatrixBuilderEnhanced,
    QualityMetric,
    TrendDirection,
)
from .reporting import (
    GovernanceReport,
    ReportFormat,
    ReportGenerator,
)
from .task_manager_enhanced import (
    Task,
    TaskConflict,
    TaskManagerEnhanced,
    TaskMaturity,
    TaskPriority,
    TaskStatus,
)

__all__ = [
    "AuditFinding",
    # Audit Framework
    "AuditFramework",
    "AuditResult",
    "AuditSeverity",
    "AuditStatus",
    "AuditType",
    "CICDType",
    "GovernanceLevel",
    "GovernanceReport",
    # Project Setup
    "ProjectGovernanceSetupEnhanced",
    "ProjectStructure",
    "ProjectType",
    "QualityCategory",
    "QualityLevel",
    "QualityMatrix",
    # Quality Matrix
    "QualityMatrixBuilderEnhanced",
    "QualityMetric",
    "ReportFormat",
    # Reporting
    "ReportGenerator",
    "Task",
    "TaskConflict",
    # Task Management
    "TaskManagerEnhanced",
    "TaskMaturity",
    "TaskPriority",
    "TaskStatus",
    "TrendDirection",
]

__version__ = "2.0.0"

"""
Quality Matrix System

Comprehensive quality assessment and tracking system for projects.
"""

import orjson as json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path


class QualityLevel(Enum):
    """Quality maturity levels."""

    CRITICAL = "critical"  # < 40%
    POOR = "poor"  # 40-60%
    FAIR = "fair"  # 60-75%
    GOOD = "good"  # 75-90%
    EXCELLENT = "excellent"  # > 90%


@dataclass
class QualityMetric:
    """Individual quality metric."""

    name: str
    category: str
    weight: float  # 0.0 to 1.0
    score: float  # 0.0 to 100.0
    threshold: float  # Minimum acceptable score
    status: str = "pending"  # pending, passing, failing
    details: dict = field(default_factory=dict)

    def calculate_status(self):
        """Calculate status based on score and threshold."""
        if self.score >= self.threshold:
            self.status = "passing"
        else:
            self.status = "failing"


@dataclass
class QualityCategory:
    """Category of quality metrics."""

    name: str
    weight: float
    metrics: list[QualityMetric] = field(default_factory=list)

    def calculate_score(self) -> float:
        """Calculate weighted category score."""
        if not self.metrics:
            return 0.0

        total_weight = sum(m.weight for m in self.metrics)
        if total_weight == 0:
            return 0.0

        weighted_sum = sum(m.score * m.weight for m in self.metrics)
        return weighted_sum / total_weight

    def get_status(self) -> str:
        """Get overall category status."""
        if not self.metrics:
            return "pending"

        failing = [m for m in self.metrics if m.status == "failing"]
        if failing:
            return "failing"
        return "passing"


@dataclass
class QualityMatrix:
    """Complete quality matrix for a project."""

    project_path: Path
    assessment_date: datetime
    overall_score: float = 0.0
    quality_level: QualityLevel = QualityLevel.CRITICAL

    categories: list[QualityCategory] = field(default_factory=list)

    # Standard categories
    code_quality: QualityCategory = None
    documentation: QualityCategory = None
    testing: QualityCategory = None
    security: QualityCategory = None
    performance: QualityCategory = None
    maintainability: QualityCategory = None
    governance: QualityCategory = None

    def __post_init__(self) -> None:
        """Initialize standard categories."""
        if self.code_quality is None:
            self.code_quality = QualityCategory("Code Quality", 0.20)
        if self.documentation is None:
            self.documentation = QualityCategory("Documentation", 0.15)
        if self.testing is None:
            self.testing = QualityCategory("Testing", 0.15)
        if self.security is None:
            self.security = QualityCategory("Security", 0.15)
        if self.performance is None:
            self.performance = QualityCategory("Performance", 0.10)
        if self.maintainability is None:
            self.maintainability = QualityCategory("Maintainability", 0.15)
        if self.governance is None:
            self.governance = QualityCategory("Governance", 0.10)

        self.categories = [
            self.code_quality,
            self.documentation,
            self.testing,
            self.security,
            self.performance,
            self.maintainability,
            self.governance,
        ]

    def calculate_overall_score(self):
        """Calculate overall quality score."""
        total_weight = sum(cat.weight for cat in self.categories)
        if total_weight == 0:
            self.overall_score = 0.0
            return

        weighted_sum = sum(cat.calculate_score() * cat.weight for cat in self.categories)
        self.overall_score = weighted_sum / total_weight

        # Determine quality level
        if self.overall_score >= 90:
            self.quality_level = QualityLevel.EXCELLENT
        elif self.overall_score >= 75:
            self.quality_level = QualityLevel.GOOD
        elif self.overall_score >= 60:
            self.quality_level = QualityLevel.FAIR
        elif self.overall_score >= 40:
            self.quality_level = QualityLevel.POOR
        else:
            self.quality_level = QualityLevel.CRITICAL

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "project_path": str(self.project_path),
            "assessment_date": self.assessment_date.isoformat(),
            "overall_score": self.overall_score,
            "quality_level": self.quality_level.value,
            "categories": [
                {
                    "name": cat.name,
                    "weight": cat.weight,
                    "score": cat.calculate_score(),
                    "status": cat.get_status(),
                    "metrics": [
                        {
                            "name": m.name,
                            "weight": m.weight,
                            "score": m.score,
                            "threshold": m.threshold,
                            "status": m.status,
                            "details": m.details,
                        }
                        for m in cat.metrics
                    ],
                }
                for cat in self.categories
            ],
        }

    def save(self, output_path: Path):
        """Save quality matrix to file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)


class QualityMatrixBuilder:
    """Builds quality matrices for projects."""

    def __init__(self, project_path: Path) -> None:
        self.project_path = Path(project_path)

    def build(self) -> QualityMatrix:
        """Build quality matrix for project."""
        matrix = QualityMatrix(
            project_path=self.project_path,
            assessment_date=datetime.now(),
        )

        # Assess each category
        self._assess_code_quality(matrix.code_quality)
        self._assess_documentation(matrix.documentation)
        self._assess_testing(matrix.testing)
        self._assess_security(matrix.security)
        self._assess_performance(matrix.performance)
        self._assess_maintainability(matrix.maintainability)
        self._assess_governance(matrix.governance)

        matrix.calculate_overall_score()
        return matrix

    def _assess_code_quality(self, category: QualityCategory):
        """Assess code quality."""
        # Linting
        lint_score = self._check_linting()
        category.metrics.append(
            QualityMetric(
                name="Linting",
                category="code_quality",
                weight=0.3,
                score=lint_score,
                threshold=8.0,
                details={"tool": "pylint/flake8"},
            )
        )

        # Type checking
        type_score = self._check_type_coverage()
        category.metrics.append(
            QualityMetric(
                name="Type Coverage",
                category="code_quality",
                weight=0.3,
                score=type_score,
                threshold=70.0,
                details={"tool": "mypy/pyright"},
            )
        )

        # Code complexity
        complexity_score = self._check_complexity()
        category.metrics.append(
            QualityMetric(
                name="Code Complexity",
                category="code_quality",
                weight=0.2,
                score=complexity_score,
                threshold=60.0,
                details={"tool": "radon/cyclomatic"},
            )
        )

        # Code style
        style_score = self._check_code_style()
        category.metrics.append(
            QualityMetric(
                name="Code Style",
                category="code_quality",
                weight=0.2,
                score=style_score,
                threshold=8.0,
                details={"tool": "black/isort"},
            )
        )

        for metric in category.metrics:
            metric.calculate_status()

    def _assess_documentation(self, category: QualityCategory):
        """Assess documentation quality."""
        # README exists and quality
        readme_score = self._check_readme()
        category.metrics.append(
            QualityMetric(
                name="README Quality",
                category="documentation",
                weight=0.25,
                score=readme_score,
                threshold=70.0,
            )
        )

        # API documentation
        api_docs_score = self._check_api_docs()
        category.metrics.append(
            QualityMetric(
                name="API Documentation",
                category="documentation",
                weight=0.25,
                score=api_docs_score,
                threshold=80.0,
            )
        )

        # Architecture docs
        arch_docs_score = self._check_architecture_docs()
        category.metrics.append(
            QualityMetric(
                name="Architecture Documentation",
                category="documentation",
                weight=0.25,
                score=arch_docs_score,
                threshold=60.0,
            )
        )

        # Code comments
        comments_score = self._check_code_comments()
        category.metrics.append(
            QualityMetric(
                name="Code Comments",
                category="documentation",
                weight=0.25,
                score=comments_score,
                threshold=50.0,
            )
        )

        for metric in category.metrics:
            metric.calculate_status()

    def _assess_testing(self, category: QualityCategory):
        """Assess testing quality."""
        # Test coverage
        coverage_score = self._check_test_coverage()
        category.metrics.append(
            QualityMetric(
                name="Test Coverage",
                category="testing",
                weight=0.4,
                score=coverage_score,
                threshold=80.0,
            )
        )

        # Test quality
        test_quality_score = self._check_test_quality()
        category.metrics.append(
            QualityMetric(
                name="Test Quality",
                category="testing",
                weight=0.3,
                score=test_quality_score,
                threshold=70.0,
            )
        )

        # Test execution
        test_exec_score = self._check_test_execution()
        category.metrics.append(
            QualityMetric(
                name="Test Execution",
                category="testing",
                weight=0.3,
                score=test_exec_score,
                threshold=90.0,
            )
        )

        for metric in category.metrics:
            metric.calculate_status()

    def _assess_security(self, category: QualityCategory):
        """Assess security."""
        # Dependency vulnerabilities
        vuln_score = self._check_vulnerabilities()
        category.metrics.append(
            QualityMetric(
                name="Dependency Vulnerabilities",
                category="security",
                weight=0.3,
                score=vuln_score,
                threshold=90.0,
            )
        )

        # Secret scanning
        secret_score = self._check_secrets()
        category.metrics.append(
            QualityMetric(
                name="Secret Scanning",
                category="security",
                weight=0.25,
                score=secret_score,
                threshold=100.0,
            )
        )

        # Security best practices
        practices_score = self._check_security_practices()
        category.metrics.append(
            QualityMetric(
                name="Security Practices",
                category="security",
                weight=0.25,
                score=practices_score,
                threshold=70.0,
            )
        )

        # Authentication/Authorization
        auth_score = self._check_auth()
        category.metrics.append(
            QualityMetric(
                name="Authentication/Authorization",
                category="security",
                weight=0.2,
                score=auth_score,
                threshold=60.0,
            )
        )

        for metric in category.metrics:
            metric.calculate_status()

    def _assess_performance(self, category: QualityCategory):
        """Assess performance."""
        # Performance benchmarks
        perf_score = self._check_performance()
        category.metrics.append(
            QualityMetric(
                name="Performance Benchmarks",
                category="performance",
                weight=0.5,
                score=perf_score,
                threshold=70.0,
            )
        )

        # Resource usage
        resource_score = self._check_resources()
        category.metrics.append(
            QualityMetric(
                name="Resource Usage",
                category="performance",
                weight=0.5,
                score=resource_score,
                threshold=60.0,
            )
        )

        for metric in category.metrics:
            metric.calculate_status()

    def _assess_maintainability(self, category: QualityCategory):
        """Assess maintainability."""
        # Code organization
        org_score = self._check_code_organization()
        category.metrics.append(
            QualityMetric(
                name="Code Organization",
                category="maintainability",
                weight=0.3,
                score=org_score,
                threshold=70.0,
            )
        )

        # Dependency management
        deps_score = self._check_dependencies()
        category.metrics.append(
            QualityMetric(
                name="Dependency Management",
                category="maintainability",
                weight=0.25,
                score=deps_score,
                threshold=70.0,
            )
        )

        # Changelog
        changelog_score = self._check_changelog()
        category.metrics.append(
            QualityMetric(
                name="Changelog",
                category="maintainability",
                weight=0.2,
                score=changelog_score,
                threshold=60.0,
            )
        )

        # Versioning
        version_score = self._check_versioning()
        category.metrics.append(
            QualityMetric(
                name="Versioning",
                category="maintainability",
                weight=0.25,
                score=version_score,
                threshold=70.0,
            )
        )

        for metric in category.metrics:
            metric.calculate_status()

    def _assess_governance(self, category: QualityCategory):
        """Assess governance."""
        # Governance structure
        gov_structure_score = self._check_governance_structure()
        category.metrics.append(
            QualityMetric(
                name="Governance Structure",
                category="governance",
                weight=0.3,
                score=gov_structure_score,
                threshold=70.0,
            )
        )

        # Quality gates
        gates_score = self._check_quality_gates()
        category.metrics.append(
            QualityMetric(
                name="Quality Gates",
                category="governance",
                weight=0.25,
                score=gates_score,
                threshold=70.0,
            )
        )

        # Audit processes
        audit_score = self._check_audits()
        category.metrics.append(
            QualityMetric(
                name="Audit Processes",
                category="governance",
                weight=0.25,
                score=audit_score,
                threshold=60.0,
            )
        )

        # Compliance
        compliance_score = self._check_compliance()
        category.metrics.append(
            QualityMetric(
                name="Compliance",
                category="governance",
                weight=0.2,
                score=compliance_score,
                threshold=70.0,
            )
        )

        for metric in category.metrics:
            metric.calculate_status()

    # Placeholder assessment methods (implement with actual checks)
    def _check_linting(self) -> float:
        """Check linting score."""
        # TODO: Implement actual linting check
        return 85.0

    def _check_type_coverage(self) -> float:
        """Check type coverage."""
        # TODO: Implement type coverage check
        return 75.0

    def _check_complexity(self) -> float:
        """Check code complexity."""
        # TODO: Implement complexity check
        return 70.0

    def _check_code_style(self) -> float:
        """Check code style."""
        # TODO: Implement style check
        return 80.0

    def _check_readme(self) -> float:
        """Check README quality."""
        readme_files = [
            self.project_path / "README.md",
            self.project_path / "README.rst",
        ]
        for readme in readme_files:
            if readme.exists():
                content = readme.read_text()
                score = 50.0
                if len(content) > 500:
                    score += 20
                if "##" in content:  # Has sections
                    score += 15
                if "```" in content:  # Has code examples
                    score += 15
                return min(100.0, score)
        return 0.0

    def _check_api_docs(self) -> float:
        """Check API documentation."""
        docs_dir = self.project_path / "docs"
        if docs_dir.exists():
            api_dirs = ["api", "reference", "apidocs"]
            for api_dir in api_dirs:
                if (docs_dir / api_dir).exists():
                    return 80.0
            return 40.0
        return 0.0

    def _check_architecture_docs(self) -> float:
        """Check architecture documentation."""
        docs_dir = self.project_path / "docs"
        if docs_dir.exists():
            arch_files = ["architecture.md", "ARCHITECTURE.md", "design.md"]
            for arch_file in arch_files:
                if (docs_dir / arch_file).exists():
                    return 80.0
        return 0.0

    def _check_code_comments(self) -> float:
        """Check code comments."""
        # TODO: Implement comment analysis
        return 60.0

    def _check_test_coverage(self) -> float:
        """Check test coverage."""
        # TODO: Implement coverage check
        return 70.0

    def _check_test_quality(self) -> float:
        """Check test quality."""
        # TODO: Implement test quality check
        return 75.0

    def _check_test_execution(self) -> float:
        """Check test execution."""
        # TODO: Implement test execution check
        return 90.0

    def _check_vulnerabilities(self) -> float:
        """Check for vulnerabilities."""
        # TODO: Implement vulnerability check
        return 95.0

    def _check_secrets(self) -> float:
        """Check for secrets."""
        # TODO: Implement secret scanning
        return 100.0

    def _check_security_practices(self) -> float:
        """Check security practices."""
        # TODO: Implement security practices check
        return 70.0

    def _check_auth(self) -> float:
        """Check authentication/authorization."""
        # TODO: Implement auth check
        return 60.0

    def _check_performance(self) -> float:
        """Check performance."""
        # TODO: Implement performance check
        return 70.0

    def _check_resources(self) -> float:
        """Check resource usage."""
        # TODO: Implement resource check
        return 65.0

    def _check_code_organization(self) -> float:
        """Check code organization."""
        # Check for proper directory structure
        if (self.project_path / "src").exists() or (self.project_path / "lib").exists():
            return 80.0
        return 50.0

    def _check_dependencies(self) -> float:
        """Check dependency management."""
        dep_files = ["requirements.txt", "pyproject.toml", "package.json", "Cargo.toml"]
        for dep_file in dep_files:
            if (self.project_path / dep_file).exists():
                return 80.0
        return 40.0

    def _check_changelog(self) -> float:
        """Check changelog."""
        changelog_files = ["CHANGELOG.md", "CHANGELOG.rst", "CHANGELOG.txt"]
        for changelog in changelog_files:
            if (self.project_path / changelog).exists():
                return 80.0
        return 0.0

    def _check_versioning(self) -> float:
        """Check versioning."""
        # Check for version file or in setup files
        version_files = ["VERSION", "__version__.py", "version.py"]
        for version_file in version_files:
            if (self.project_path / version_file).exists():
                return 80.0
        return 50.0

    def _check_governance_structure(self) -> float:
        """Check governance structure."""
        gov_dir = self.project_path / "governance"
        if gov_dir.exists():
            return 80.0
        return 0.0

    def _check_quality_gates(self) -> float:
        """Check quality gates."""
        gov_dir = self.project_path / "governance"
        if gov_dir and (gov_dir / "quality-gates.yaml").exists():
            return 80.0
        return 0.0

    def _check_audits(self) -> float:
        """Check audit processes."""
        gov_dir = self.project_path / "governance"
        if gov_dir and (gov_dir / "audit-config.yaml").exists():
            return 80.0
        return 0.0

    def _check_compliance(self) -> float:
        """Check compliance."""
        # Check for compliance files
        compliance_files = ["LICENSE", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md"]
        score = 0.0
        for comp_file in compliance_files:
            if (self.project_path / comp_file).exists():
                score += 33.33
        return min(100.0, score)

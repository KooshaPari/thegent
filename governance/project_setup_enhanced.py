"""
Enhanced Project Governance Setup System

Expanded with breadth, depth, robustness, and optimization.
"""

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from functools import lru_cache
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


class ProjectType(Enum):
    """Types of projects."""

    PYTHON = "python"
    NODE = "node"
    RUST = "rust"
    GO = "go"
    JAVA = "java"
    CPP = "cpp"
    CSHARP = "csharp"
    PHP = "php"
    RUBY = "ruby"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    DART = "dart"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class GovernanceLevel(Enum):
    """Governance maturity levels."""

    NONE = "none"
    BASIC = "basic"
    STANDARD = "standard"
    MATURE = "mature"
    EXCELLENT = "excellent"


class CICDType(Enum):
    """CI/CD system types."""

    GITHUB_ACTIONS = "github_actions"
    GITLAB_CI = "gitlab_ci"
    JENKINS = "jenkins"
    CIRCLE_CI = "circle_ci"
    TRAVIS_CI = "travis_ci"
    AZURE_PIPELINES = "azure_pipelines"
    BITBUCKET_PIPELINES = "bitbucket_pipelines"
    NONE = "none"


@dataclass
class FileCheck:
    """File check result."""

    path: Path
    exists: bool
    size: int = 0
    last_modified: datetime | None = None
    content_hash: str | None = None
    is_valid: bool = False
    issues: list[str] = field(default_factory=list)


@dataclass
class ProjectStructure:
    """Enhanced project structure assessment."""

    project_path: Path
    project_type: ProjectType
    governance_level: GovernanceLevel
    assessment_date: datetime = field(default_factory=datetime.now)

    # Basic files (expanded)
    has_readme: bool = False
    has_license: bool = False
    has_contributing: bool = False
    has_code_of_conduct: bool = False
    has_changelog: bool = False
    has_security_policy: bool = False
    has_support_file: bool = False
    has_issue_template: bool = False
    has_pr_template: bool = False

    # Directory structure (expanded)
    has_docs_dir: bool = False
    has_tests_dir: bool = False
    has_src_dir: bool = False
    has_lib_dir: bool = False
    has_config_dir: bool = False
    has_scripts_dir: bool = False
    has_tools_dir: bool = False

    # Tooling files (expanded)
    has_pyproject_toml: bool = False
    has_setup_py: bool = False
    has_setup_cfg: bool = False
    has_requirements_txt: bool = False
    has_requirements_dev_txt: bool = False
    has_pipfile: bool = False
    has_poetry_lock: bool = False
    has_package_json: bool = False
    has_package_lock_json: bool = False
    has_yarn_lock: bool = False
    has_cargo_toml: bool = False
    has_cargo_lock: bool = False
    has_go_mod: bool = False
    has_go_sum: bool = False
    has_pom_xml: bool = False
    has_build_gradle: bool = False
    has_cmake_lists: bool = False
    has_makefile: bool = False
    has_justfile: bool = False
    has_dockerfile: bool = False
    has_docker_compose: bool = False
    has_kubernetes_config: bool = False

    # CI/CD (expanded)
    ci_cd_type: CICDType = CICDType.NONE
    has_github_actions: bool = False
    has_gitlab_ci: bool = False
    has_jenkins: bool = False
    has_pre_commit_hooks: bool = False
    has_husky: bool = False
    has_git_hooks: bool = False

    # Governance (expanded)
    has_governance_dir: bool = False
    has_quality_gates: bool = False
    has_audit_config: bool = False
    has_policy_files: bool = False
    has_compliance_config: bool = False
    has_risk_register: bool = False

    # Documentation (expanded)
    has_architecture_docs: bool = False
    has_api_docs: bool = False
    has_contributor_guide: bool = False
    has_user_guide: bool = False
    has_developer_guide: bool = False
    has_deployment_guide: bool = False
    has_troubleshooting_guide: bool = False
    has_adr: bool = False  # Architecture Decision Records

    # Testing (expanded)
    has_unit_tests: bool = False
    has_integration_tests: bool = False
    has_e2e_tests: bool = False
    has_benchmarks: bool = False
    has_test_config: bool = False

    # Code quality (expanded)
    has_linter_config: bool = False
    has_formatter_config: bool = False
    has_type_checker_config: bool = False
    has_complexity_config: bool = False

    # Security (expanded)
    has_dependabot: bool = False
    has_security_scan: bool = False
    has_secret_scan: bool = False
    has_sbom: bool = False  # Software Bill of Materials

    # Metrics and tracking
    file_checks: dict[str, FileCheck] = field(default_factory=dict)
    missing_items: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def calculate_score(self) -> int:
        """Calculate comprehensive governance maturity score (0-200)."""
        score = 0

        # Basic files (30 points)
        score += 5 if self.has_readme else 0
        score += 5 if self.has_license else 0
        score += 4 if self.has_changelog else 0
        score += 4 if self.has_contributing else 0
        score += 3 if self.has_code_of_conduct else 0
        score += 3 if self.has_security_policy else 0
        score += 3 if self.has_issue_template else 0
        score += 3 if self.has_pr_template else 0

        # Structure (30 points)
        score += 6 if self.has_docs_dir else 0
        score += 6 if self.has_tests_dir else 0
        score += 4 if self.has_src_dir else 0
        score += 4 if self.has_config_dir else 0
        score += 3 if self.has_scripts_dir else 0
        score += 3 if self.has_tools_dir else 0
        score += 2 if self.has_lib_dir else 0
        score += 2 if self.has_support_file else 0

        # Tooling (25 points)
        tooling_score = 0
        if self.project_type == ProjectType.PYTHON:
            tooling_score += 5 if self.has_pyproject_toml else 0
            tooling_score += 3 if self.has_setup_py else 0
            tooling_score += 2 if self.has_requirements_txt else 0
        elif self.project_type == ProjectType.NODE:
            tooling_score += 5 if self.has_package_json else 0
            tooling_score += 2 if self.has_package_lock_json else 0
        elif self.project_type == ProjectType.RUST:
            tooling_score += 5 if self.has_cargo_toml else 0
            tooling_score += 2 if self.has_cargo_lock else 0
        elif self.project_type == ProjectType.GO:
            tooling_score += 5 if self.has_go_mod else 0
            tooling_score += 2 if self.has_go_sum else 0

        score += min(25, tooling_score)
        score += 3 if self.has_makefile else 0
        score += 2 if self.has_dockerfile else 0

        # CI/CD (25 points)
        ci_score = 0
        if self.has_github_actions or self.has_gitlab_ci:
            ci_score += 10
        elif self.has_jenkins:
            ci_score += 8

        score += ci_score
        score += 5 if self.has_pre_commit_hooks else 0
        score += 3 if self.has_git_hooks else 0

        # Governance (30 points)
        score += 8 if self.has_governance_dir else 0
        score += 6 if self.has_quality_gates else 0
        score += 5 if self.has_audit_config else 0
        score += 4 if self.has_policy_files else 0
        score += 4 if self.has_compliance_config else 0
        score += 3 if self.has_risk_register else 0

        # Documentation (30 points)
        score += 6 if self.has_architecture_docs else 0
        score += 6 if self.has_api_docs else 0
        score += 4 if self.has_contributor_guide else 0
        score += 4 if self.has_user_guide else 0
        score += 3 if self.has_developer_guide else 0
        score += 3 if self.has_deployment_guide else 0
        score += 2 if self.has_troubleshooting_guide else 0
        score += 2 if self.has_adr else 0

        # Testing (20 points)
        score += 6 if self.has_unit_tests else 0
        score += 5 if self.has_integration_tests else 0
        score += 4 if self.has_e2e_tests else 0
        score += 3 if self.has_benchmarks else 0
        score += 2 if self.has_test_config else 0

        # Code quality (10 points)
        score += 3 if self.has_linter_config else 0
        score += 3 if self.has_formatter_config else 0
        score += 2 if self.has_type_checker_config else 0
        score += 2 if self.has_complexity_config else 0

        return min(200, score)

    def assess(self):
        """Comprehensive assessment with recommendations."""
        score = self.calculate_score()

        if score < 40:
            self.governance_level = GovernanceLevel.NONE
        elif score < 80:
            self.governance_level = GovernanceLevel.BASIC
        elif score < 120:
            self.governance_level = GovernanceLevel.STANDARD
        elif score < 160:
            self.governance_level = GovernanceLevel.MATURE
        else:
            self.governance_level = GovernanceLevel.EXCELLENT

        # Generate missing items
        self._identify_missing_items()

        # Generate recommendations
        self._generate_recommendations(score)

        # Generate warnings
        self._generate_warnings()

    def _identify_missing_items(self):
        """Identify missing critical items."""
        if not self.has_readme:
            self.missing_items.append("README.md")
        if not self.has_license:
            self.missing_items.append("LICENSE")
        if not self.has_docs_dir:
            self.missing_items.append("docs/ directory")
        if not self.has_tests_dir:
            self.missing_items.append("tests/ directory")
        if not self.has_governance_dir:
            self.missing_items.append("governance/ directory")
        if not self.has_quality_gates:
            self.missing_items.append("Quality gates configuration")
        if self.ci_cd_type == CICDType.NONE:
            self.missing_items.append("CI/CD configuration")
        if not self.has_pre_commit_hooks:
            self.missing_items.append("Pre-commit hooks")

    def _generate_recommendations(self, score: int):
        """Generate recommendations based on score."""
        if score < 40:
            self.recommendations.extend(
                [
                    "Create basic project structure (README, LICENSE, docs/)",
                    "Set up version control and CI/CD",
                    "Add basic governance framework",
                    "Create testing infrastructure",
                ]
            )
        elif score < 80:
            self.recommendations.extend(
                [
                    "Enhance documentation structure",
                    "Add quality gates and testing framework",
                    "Set up audit and compliance checks",
                    "Configure code quality tools",
                ]
            )
        elif score < 120:
            self.recommendations.extend(
                [
                    "Enhance governance maturity",
                    "Add comprehensive quality matrices",
                    "Implement automated compliance checks",
                    "Improve test coverage",
                ]
            )
        elif score < 160:
            self.recommendations.extend(
                [
                    "Optimize governance processes",
                    "Enhance documentation completeness",
                    "Improve security posture",
                    "Add performance monitoring",
                ]
            )
        else:
            self.recommendations.extend(
                [
                    "Maintain excellence standards",
                    "Continuous improvement",
                    "Stay updated with best practices",
                ]
            )

    def _generate_warnings(self):
        """Generate warnings for potential issues."""
        if self.has_setup_py and not self.has_pyproject_toml:
            self.warnings.append("Consider migrating from setup.py to pyproject.toml")
        if self.has_package_json and not self.has_package_lock_json:
            self.warnings.append("Consider adding package-lock.json for reproducible builds")
        if self.has_dockerfile and not self.has_docker_compose:
            self.warnings.append("Consider adding docker-compose.yml for development")
        if not self.has_pre_commit_hooks:
            self.warnings.append("Pre-commit hooks can catch issues early")
        if not self.has_security_policy:
            self.warnings.append("Security policy helps with vulnerability reporting")


class ProjectGovernanceSetupEnhanced:
    """Enhanced project governance setup with expanded capabilities."""

    def __init__(self, project_path: Path) -> None:
        self.project_path = Path(project_path).resolve()
        if not self.project_path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")
        self.structure: ProjectStructure | None = None
        self._cache: dict[str, any] = {}

    @lru_cache(maxsize=128)
    def _file_exists(self, relative_path: str) -> bool:
        """Cached file existence check."""
        return (self.project_path / relative_path).exists()

    def analyze(self) -> ProjectStructure:
        """Comprehensive project analysis."""
        try:
            structure = ProjectStructure(
                project_path=self.project_path,
                project_type=self._detect_project_type(),
                governance_level=GovernanceLevel.NONE,
            )

            # Check all files and directories
            self._check_basic_files(structure)
            self._check_directories(structure)
            self._check_tooling_files(structure)
            self._check_ci_cd(structure)
            self._check_governance(structure)
            self._check_documentation(structure)
            self._check_testing(structure)
            self._check_code_quality(structure)
            self._check_security(structure)

            # Perform file checks
            self._perform_file_checks(structure)

            # Assess
            structure.assess()

            self.structure = structure
            return structure

        except Exception as e:
            logger.error(f"Error analyzing project {self.project_path}: {e}")
            raise

    def _detect_project_type(self) -> ProjectType:
        """Detect project type with expanded support."""
        checks = {
            ProjectType.PYTHON: [
                "pyproject.toml",
                "setup.py",
                "requirements.txt",
                "Pipfile",
                "poetry.lock",
                "setup.cfg",
            ],
            ProjectType.NODE: ["package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml", ".nvmrc"],
            ProjectType.RUST: ["Cargo.toml", "Cargo.lock"],
            ProjectType.GO: ["go.mod", "go.sum", "Gopkg.toml"],
            ProjectType.JAVA: ["pom.xml", "build.gradle", "build.gradle.kts"],
            ProjectType.CPP: ["CMakeLists.txt", "Makefile", ".cpp"],
            ProjectType.CSHARP: [".csproj", ".sln", "project.json"],
            ProjectType.PHP: ["composer.json", "composer.lock"],
            ProjectType.RUBY: ["Gemfile", "Gemfile.lock", "Rakefile"],
            ProjectType.SWIFT: ["Package.swift", ".xcodeproj"],
            ProjectType.KOTLIN: ["build.gradle.kts", "settings.gradle.kts"],
            ProjectType.DART: ["pubspec.yaml", "pubspec.lock"],
        }

        found_types = []
        for project_type, files in checks.items():
            for file_pattern in files:
                if file_pattern.startswith("."):
                    # Check for files with this extension
                    for path in self.project_path.rglob(f"*{file_pattern}"):
                        if path.is_file():
                            found_types.append(project_type)
                            break
                elif self._file_exists(file_pattern):
                    found_types.append(project_type)
                    break

        if len(found_types) > 1:
            return ProjectType.MIXED
        if found_types:
            return found_types[0]
        return ProjectType.UNKNOWN

    def _check_basic_files(self, structure: ProjectStructure):
        """Check for basic project files."""
        structure.has_readme = any(self._file_exists(f) for f in ["README.md", "README.rst", "README.txt"])
        structure.has_license = any(self._file_exists(f) for f in ["LICENSE", "LICENSE.txt", "LICENSE.md"])
        structure.has_contributing = self._file_exists("CONTRIBUTING.md")
        structure.has_code_of_conduct = self._file_exists("CODE_OF_CONDUCT.md")
        structure.has_changelog = any(self._file_exists(f) for f in ["CHANGELOG.md", "CHANGELOG.rst", "CHANGELOG.txt"])
        structure.has_security_policy = (
            self._file_exists("SECURITY.md") or (self.project_path / ".github" / "SECURITY.md").exists()
        )
        structure.has_support_file = self._file_exists("SUPPORT.md")
        structure.has_issue_template = (self.project_path / ".github" / "ISSUE_TEMPLATE").exists() or (
            self.project_path / ".gitlab" / "issue_templates"
        ).exists()
        structure.has_pr_template = (self.project_path / ".github" / "pull_request_template.md").exists() or (
            self.project_path / ".gitlab" / "merge_request_templates"
        ).exists()

    def _check_directories(self, structure: ProjectStructure):
        """Check for standard directories."""
        structure.has_docs_dir = (self.project_path / "docs").exists()
        structure.has_tests_dir = any(
            (self.project_path / d).exists() for d in ["tests", "test", "__tests__", "spec", "specs"]
        )
        structure.has_src_dir = any((self.project_path / d).exists() for d in ["src", "source", "lib", "libs"])
        structure.has_lib_dir = (self.project_path / "lib").exists()
        structure.has_config_dir = any((self.project_path / d).exists() for d in ["config", "conf", ".config"])
        structure.has_scripts_dir = (self.project_path / "scripts").exists()
        structure.has_tools_dir = (self.project_path / "tools").exists()

    def _check_tooling_files(self, structure: ProjectStructure):
        """Check for tooling configuration files."""
        # Python
        structure.has_pyproject_toml = self._file_exists("pyproject.toml")
        structure.has_setup_py = self._file_exists("setup.py")
        structure.has_setup_cfg = self._file_exists("setup.cfg")
        structure.has_requirements_txt = self._file_exists("requirements.txt")
        structure.has_requirements_dev_txt = self._file_exists("requirements-dev.txt")
        structure.has_pipfile = self._file_exists("Pipfile")
        structure.has_poetry_lock = self._file_exists("poetry.lock")

        # Node
        structure.has_package_json = self._file_exists("package.json")
        structure.has_package_lock_json = self._file_exists("package-lock.json")
        structure.has_yarn_lock = self._file_exists("yarn.lock")

        # Rust
        structure.has_cargo_toml = self._file_exists("Cargo.toml")
        structure.has_cargo_lock = self._file_exists("Cargo.lock")

        # Go
        structure.has_go_mod = self._file_exists("go.mod")
        structure.has_go_sum = self._file_exists("go.sum")

        # Java
        structure.has_pom_xml = self._file_exists("pom.xml")
        structure.has_build_gradle = any(self._file_exists(f) for f in ["build.gradle", "build.gradle.kts"])

        # C/C++
        structure.has_cmake_lists = self._file_exists("CMakeLists.txt")

        # Build tools
        structure.has_makefile = any(self._file_exists(f) for f in ["Makefile", "makefile", "GNUmakefile"])
        structure.has_justfile = self._file_exists("justfile")

        # Containerization
        structure.has_dockerfile = any(self._file_exists(f) for f in ["Dockerfile", "Dockerfile.dev"])
        structure.has_docker_compose = any(self._file_exists(f) for f in ["docker-compose.yml", "docker-compose.yaml"])
        structure.has_kubernetes_config = any(
            (self.project_path / "k8s").exists()
            or (self.project_path / "kubernetes").exists()
            or any(
                f.endswith((".yaml", ".yml")) and "k8s" in f.lower() for f in self.project_path.iterdir() if f.is_file()
            )
        )

    def _check_ci_cd(self, structure: ProjectStructure):
        """Check for CI/CD configuration."""
        github_workflows = self.project_path / ".github" / "workflows"
        structure.has_github_actions = github_workflows.exists() and any(
            github_workflows.glob("*.yml") or github_workflows.glob("*.yaml")
        )

        structure.has_gitlab_ci = self._file_exists(".gitlab-ci.yml")
        structure.has_jenkins = self._file_exists("Jenkinsfile")

        if structure.has_github_actions:
            structure.ci_cd_type = CICDType.GITHUB_ACTIONS
        elif structure.has_gitlab_ci:
            structure.ci_cd_type = CICDType.GITLAB_CI
        elif structure.has_jenkins:
            structure.ci_cd_type = CICDType.JENKINS
        else:
            structure.ci_cd_type = CICDType.NONE

        # Pre-commit hooks
        structure.has_pre_commit_hooks = self._file_exists(".pre-commit-config.yaml")
        structure.has_husky = (self.project_path / ".husky").exists()
        structure.has_git_hooks = (self.project_path / ".git" / "hooks").exists()

    def _check_governance(self, structure: ProjectStructure):
        """Check for governance files."""
        gov_dir = self.project_path / "governance"
        structure.has_governance_dir = gov_dir.exists()

        if structure.has_governance_dir:
            structure.has_quality_gates = (gov_dir / "quality-gates.yaml").exists()
            structure.has_audit_config = (gov_dir / "audit-config.yaml").exists()
            structure.has_policy_files = any(
                (gov_dir / f).exists() for f in ["policies.yaml", "compliance.yaml", "policy.md"]
            )
            structure.has_compliance_config = (gov_dir / "compliance.yaml").exists()
            structure.has_risk_register = (gov_dir / "risk-register.yaml").exists()

    def _check_documentation(self, structure: ProjectStructure):
        """Check for documentation."""
        if structure.has_docs_dir:
            docs_dir = self.project_path / "docs"
            structure.has_architecture_docs = any(
                (docs_dir / f).exists() for f in ["architecture.md", "ARCHITECTURE.md", "design.md", "DESIGN.md"]
            )
            structure.has_api_docs = any((docs_dir / d).exists() for d in ["api", "reference", "apidocs", "API"])
            structure.has_contributor_guide = (docs_dir / "CONTRIBUTING.md").exists()
            structure.has_user_guide = any(
                (docs_dir / f).exists() for f in ["user-guide.md", "USER_GUIDE.md", "usage.md"]
            )
            structure.has_developer_guide = any(
                (docs_dir / f).exists() for f in ["developer-guide.md", "DEVELOPER_GUIDE.md", "dev.md"]
            )
            structure.has_deployment_guide = any(
                (docs_dir / f).exists() for f in ["deployment.md", "DEPLOYMENT.md", "deploy.md"]
            )
            structure.has_troubleshooting_guide = any(
                (docs_dir / f).exists() for f in ["troubleshooting.md", "TROUBLESHOOTING.md", "faq.md"]
            )
            structure.has_adr = (docs_dir / "adr").exists() or any("adr" in str(f).lower() for f in docs_dir.iterdir())

    def _check_testing(self, structure: ProjectStructure):
        """Check for testing infrastructure."""
        if structure.has_tests_dir:
            test_dir = next(
                (
                    self.project_path / d
                    for d in ["tests", "test", "__tests__", "spec"]
                    if (self.project_path / d).exists()
                ),
                None,
            )
            if test_dir:
                # Check for test files
                test_files = (
                    list(test_dir.rglob("test_*.py"))
                    + list(test_dir.rglob("*_test.py"))
                    + list(test_dir.rglob("*.test.js"))
                    + list(test_dir.rglob("*.spec.js"))
                )
                structure.has_unit_tests = len(test_files) > 0

                # Check for integration tests
                integration_dirs = ["integration", "integration_tests", "e2e"]
                structure.has_integration_tests = any((test_dir / d).exists() for d in integration_dirs)
                structure.has_e2e_tests = (test_dir / "e2e").exists() or (test_dir / "end_to_end").exists()

        structure.has_benchmarks = any(self._file_exists(f) for f in ["benchmarks", "bench", "perf"]) or any(
            "benchmark" in str(p) for p in self.project_path.rglob("*")
        )

        structure.has_test_config = any(
            self._file_exists(f)
            for f in ["pytest.ini", ".pytest.ini", "tox.ini", "jest.config.js", "vitest.config.js", "test.config.js"]
        )

    def _check_code_quality(self, structure: ProjectStructure):
        """Check for code quality tools."""
        structure.has_linter_config = any(
            self._file_exists(f)
            for f in [
                ".pylintrc",
                ".flake8",
                ".eslintrc",
                ".eslintrc.js",
                ".eslintrc.json",
                "eslint.config.js",
                ".rubocop.yml",
                "clippy.toml",
                ".golangci.yml",
            ]
        )
        structure.has_formatter_config = any(
            self._file_exists(f)
            for f in [".black", "pyproject.toml", ".prettierrc", ".prettierrc.js", ".prettierrc.json", "rustfmt.toml"]
        )
        structure.has_type_checker_config = any(
            self._file_exists(f)
            for f in ["mypy.ini", ".mypy.ini", "pyrightconfig.json", "tsconfig.json", ".tsconfig.json"]
        )
        structure.has_complexity_config = any(self._file_exists(f) for f in [".radon", "complexity.yaml"])

    def _check_security(self, structure: ProjectStructure):
        """Check for security tools."""
        structure.has_dependabot = (self.project_path / ".github" / "dependabot.yml").exists() or (
            self.project_path / ".github" / "dependabot.yaml"
        ).exists()
        structure.has_security_scan = any(
            "security" in str(p).lower() or "snyk" in str(p).lower() or "safety" in str(p).lower()
            for p in self.project_path.rglob("*")
        )
        structure.has_secret_scan = any(
            ".secrets" in str(p) or "trufflehog" in str(p).lower() for p in self.project_path.rglob("*")
        )
        structure.has_sbom = any(self._file_exists(f) for f in ["sbom.json", "bom.json", "cyclonedx.json"])

    def _perform_file_checks(self, structure: ProjectStructure):
        """Perform detailed file checks."""
        important_files = ["README.md", "LICENSE", "CONTRIBUTING.md", "CHANGELOG.md", "pyproject.toml", "package.json"]

        for file_name in important_files:
            file_path = self.project_path / file_name
            if file_path.exists():
                try:
                    stat = file_path.stat()
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

                    check = FileCheck(
                        path=file_path,
                        exists=True,
                        size=stat.st_size,
                        last_modified=datetime.fromtimestamp(stat.st_mtime),
                        content_hash=content_hash,
                        is_valid=self._validate_file(file_name, content),
                    )

                    if not check.is_valid:
                        check.issues = self._identify_file_issues(file_name, content)

                    structure.file_checks[file_name] = check
                except Exception as e:
                    logger.warning(f"Error checking file {file_name}: {e}")

    def _validate_file(self, file_name: str, content: str) -> bool:
        """Validate file content."""
        if file_name == "README.md":
            return len(content) > 100 and "##" in content
        if file_name == "LICENSE":
            return len(content) > 200 and ("MIT" in content or "Apache" in content or "GPL" in content)
        if file_name == "CONTRIBUTING.md":
            return len(content) > 200
        return True

    def _identify_file_issues(self, file_name: str, content: str) -> list[str]:
        """Identify issues in file content."""
        issues = []
        if file_name == "README.md":
            if len(content) < 100:
                issues.append("README is too short")
            if "##" not in content:
                issues.append("README lacks sections")
            if "```" not in content:
                issues.append("README lacks code examples")
        elif file_name == "LICENSE":
            if len(content) < 200:
                issues.append("LICENSE file seems incomplete")
        return issues

    def setup_basic_structure(self, force: bool = False):
        """Set up basic project structure with enhanced features."""
        if not self.structure:
            self.analyze()

        try:
            # Create directories
            dirs = ["docs", "tests", "src", "config", "scripts", "tools", "governance"]
            for dir_name in dirs:
                dir_path = self.project_path / dir_name
                if not dir_path.exists() or force:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Created directory: {dir_path}")

            # Create basic files if missing
            if not self.structure.has_readme or force:
                self._create_enhanced_readme()

            if not self.structure.has_license or force:
                self._create_license()

            # Create governance files
            self._create_enhanced_governance_files()

            # Create CI/CD if missing
            if self.structure.ci_cd_type == CICDType.NONE:
                self._create_github_actions()

            # Create pre-commit hooks
            if not self.structure.has_pre_commit_hooks:
                self._create_pre_commit_config()

            logger.info(f"Basic structure setup complete for {self.project_path}")

        except Exception as e:
            logger.error(f"Error setting up structure: {e}")
            raise

    def _create_enhanced_readme(self):
        """Create enhanced README.md."""
        project_name = self.project_path.name
        readme_content = rf"""# {project_name}

[![Quality](https://img.shields.io/badge/quality-mature-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Overview

{project_name} is a [description of what the project does].

## Features

- Feature 1
- Feature 2
- Feature 3

## Getting Started

### Prerequisites

- Python 3.8+ (or appropriate runtime)
- [Other dependencies]

### Installation

\`\`\`bash
# Installation instructions
pip install {project_name.lower().replace(" ", "-")}
\`\`\`

### Quick Start

\`\`\`bash
# Quick start example
{project_name.lower()} --help
\`\`\`

## Documentation

- [Architecture](docs/architecture.md)
- [API Reference](docs/api/)
- [Contributing](CONTRIBUTING.md)
- [Deployment Guide](docs/deployment.md)

## Development

\`\`\`bash
# Setup development environment
make setup

# Run tests
make test

# Run linters
make lint
\`\`\`

## Testing

\`\`\`bash
# Run all tests
pytest

# Run with coverage
pytest --cov
\`\`\`

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

See [LICENSE](LICENSE) for license information.

## Support

For support, please [open an issue](.github/ISSUE_TEMPLATE) or see [SUPPORT.md](SUPPORT.md).
"""
        (self.project_path / "README.md").write_text(readme_content)

    def _create_license(self):
        """Create MIT LICENSE."""
        license_content = """MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        (self.project_path / "LICENSE").write_text(license_content)

    def _create_enhanced_governance_files(self):
        """Create enhanced governance configuration files."""
        gov_dir = self.project_path / "governance"
        gov_dir.mkdir(exist_ok=True)

        # Enhanced quality gates
        quality_gates = {
            "version": "2.0",
            "metadata": {
                "project": self.project_path.name,
                "created": datetime.now().isoformat(),
            },
            "gates": {
                "code_quality": {
                    "enabled": True,
                    "checks": [
                        "linting",
                        "type_checking",
                        "test_coverage",
                        "complexity",
                        "duplication",
                    ],
                    "thresholds": {
                        "test_coverage": 80,
                        "lint_score": 8.0,
                        "complexity": 10,
                        "duplication": 5,
                    },
                    "tools": {
                        "linting": ["pylint", "flake8", "ruff"],
                        "type_checking": ["mypy", "pyright"],
                        "coverage": ["pytest-cov", "coverage.py"],
                    },
                },
                "documentation": {
                    "enabled": True,
                    "checks": [
                        "readme_exists",
                        "api_docs_complete",
                        "architecture_documented",
                        "examples_provided",
                    ],
                    "thresholds": {
                        "doc_coverage": 80,
                    },
                },
                "security": {
                    "enabled": True,
                    "checks": [
                        "dependency_scan",
                        "secret_scan",
                        "vulnerability_check",
                        "sbom_generation",
                    ],
                    "tools": {
                        "dependency_scan": ["safety", "pip-audit"],
                        "secret_scan": ["trufflehog", "git-secrets"],
                    },
                },
                "performance": {
                    "enabled": True,
                    "checks": [
                        "benchmark_regression",
                        "memory_profiling",
                        "load_testing",
                    ],
                },
            },
        }

        with open(gov_dir / "quality-gates.yaml", "w") as f:
            yaml.dump(quality_gates, f, default_flow_style=False, sort_keys=False)

        # Enhanced audit config
        audit_config = {
            "version": "2.0",
            "metadata": {
                "project": self.project_path.name,
                "created": datetime.now().isoformat(),
            },
            "audits": {
                "code_review": {
                    "enabled": True,
                    "frequency": "on_commit",
                    "required_approvals": 1,
                    "checks": ["security", "performance", "documentation"],
                },
                "dependency_audit": {
                    "enabled": True,
                    "frequency": "weekly",
                    "tools": ["safety", "pip-audit", "npm audit"],
                },
                "security_audit": {
                    "enabled": True,
                    "frequency": "monthly",
                    "scope": ["code", "dependencies", "infrastructure"],
                },
                "documentation_audit": {
                    "enabled": True,
                    "frequency": "monthly",
                    "checks": ["completeness", "accuracy", "freshness"],
                },
                "performance_audit": {
                    "enabled": True,
                    "frequency": "quarterly",
                    "metrics": ["response_time", "throughput", "memory"],
                },
                "compliance_audit": {
                    "enabled": True,
                    "frequency": "quarterly",
                    "standards": ["license_compliance", "accessibility", "privacy"],
                },
            },
        }

        with open(gov_dir / "audit-config.yaml", "w") as f:
            yaml.dump(audit_config, f, default_flow_style=False, sort_keys=False)

    def _create_github_actions(self):
        """Create GitHub Actions workflow."""
        workflows_dir = self.project_path / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)

        workflow_content = """name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        pytest --cov
    - name: Run linters
      run: |
        pylint src/
        flake8 src/
"""
        (workflows_dir / "ci.yml").write_text(workflow_content)

    def _create_pre_commit_config(self):
        """Create pre-commit configuration."""
        pre_commit_config = """repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-toml
      - id: check-merge-conflict
      - id: detect-private-key

  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
"""
        (self.project_path / ".pre-commit-config.yaml").write_text(pre_commit_config)

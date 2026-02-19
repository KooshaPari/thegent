"""
Project Governance Setup System

Automatically sets up proper project structure, tooling, and governance
for projects that are missing these components.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import yaml


class ProjectType(Enum):
    """Types of projects."""

    PYTHON = "python"
    NODE = "node"
    RUST = "rust"
    GO = "go"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class GovernanceLevel(Enum):
    """Governance maturity levels."""

    NONE = "none"
    BASIC = "basic"
    STANDARD = "standard"
    MATURE = "mature"


@dataclass
class ProjectStructure:
    """Project structure assessment."""

    project_path: Path
    project_type: ProjectType
    governance_level: GovernanceLevel

    # File presence checks
    has_readme: bool = False
    has_license: bool = False
    has_contributing: bool = False
    has_code_of_conduct: bool = False
    has_changelog: bool = False
    has_docs_dir: bool = False
    has_tests_dir: bool = False
    has_ci_config: bool = False

    # Tooling checks
    has_pyproject_toml: bool = False
    has_setup_py: bool = False
    has_package_json: bool = False
    has_cargo_toml: bool = False
    has_go_mod: bool = False
    has_makefile: bool = False
    has_dockerfile: bool = False

    # Governance checks
    has_governance_dir: bool = False
    has_quality_gates: bool = False
    has_audit_config: bool = False
    has_policy_files: bool = False

    # Documentation checks
    has_architecture_docs: bool = False
    has_api_docs: bool = False
    has_contributor_guide: bool = False

    missing_items: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def calculate_score(self) -> int:
        """Calculate governance maturity score (0-100)."""
        score = 0

        # Basic files (20 points)
        if self.has_readme:
            score += 5
        if self.has_license:
            score += 5
        if self.has_changelog:
            score += 5
        if self.has_contributing:
            score += 5

        # Structure (20 points)
        if self.has_docs_dir:
            score += 10
        if self.has_tests_dir:
            score += 10

        # Tooling (20 points)
        tooling_files = [
            self.has_pyproject_toml,
            self.has_setup_py,
            self.has_package_json,
            self.has_cargo_toml,
            self.has_go_mod,
            self.has_makefile,
        ]
        if any(tooling_files):
            score += 10
        if self.has_ci_config:
            score += 10

        # Governance (25 points)
        if self.has_governance_dir:
            score += 10
        if self.has_quality_gates:
            score += 8
        if self.has_audit_config:
            score += 7

        # Documentation (15 points)
        if self.has_architecture_docs:
            score += 5
        if self.has_api_docs:
            score += 5
        if self.has_contributor_guide:
            score += 5

        return min(100, score)

    def assess(self):
        """Assess project and generate recommendations."""
        score = self.calculate_score()

        if score < 30:
            self.governance_level = GovernanceLevel.NONE
        elif score < 60:
            self.governance_level = GovernanceLevel.BASIC
        elif score < 85:
            self.governance_level = GovernanceLevel.STANDARD
        else:
            self.governance_level = GovernanceLevel.MATURE

        # Generate missing items list
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

        # Generate recommendations
        if self.governance_level == GovernanceLevel.NONE:
            self.recommendations.extend(
                [
                    "Create basic project structure (README, LICENSE, docs/)",
                    "Set up version control and CI/CD",
                    "Add basic governance framework",
                ]
            )
        elif self.governance_level == GovernanceLevel.BASIC:
            self.recommendations.extend(
                [
                    "Enhance documentation structure",
                    "Add quality gates and testing framework",
                    "Set up audit and compliance checks",
                ]
            )
        elif self.governance_level == GovernanceLevel.STANDARD:
            self.recommendations.extend(
                [
                    "Enhance governance maturity",
                    "Add comprehensive quality matrices",
                    "Implement automated compliance checks",
                ]
            )


class ProjectGovernanceSetup:
    """Sets up governance for projects."""

    def __init__(self, project_path: Path) -> None:
        self.project_path = Path(project_path)
        self.structure = None

    def analyze(self) -> ProjectStructure:
        """Analyze project structure."""
        structure = ProjectStructure(
            project_path=self.project_path,
            project_type=self._detect_project_type(),
            governance_level=GovernanceLevel.NONE,
        )

        # Check for files
        structure.has_readme = any((self.project_path / f).exists() for f in ["README.md", "README.rst", "README.txt"])
        structure.has_license = any((self.project_path / f).exists() for f in ["LICENSE", "LICENSE.txt", "LICENSE.md"])
        structure.has_contributing = (self.project_path / "CONTRIBUTING.md").exists()
        structure.has_code_of_conduct = (self.project_path / "CODE_OF_CONDUCT.md").exists()
        structure.has_changelog = any(
            (self.project_path / f).exists() for f in ["CHANGELOG.md", "CHANGELOG.rst", "CHANGELOG.txt"]
        )

        # Check for directories
        structure.has_docs_dir = (self.project_path / "docs").exists()
        structure.has_tests_dir = any((self.project_path / d).exists() for d in ["tests", "test", "__tests__", "spec"])
        structure.has_governance_dir = (self.project_path / "governance").exists()

        # Check for tooling files
        structure.has_pyproject_toml = (self.project_path / "pyproject.toml").exists()
        structure.has_setup_py = (self.project_path / "setup.py").exists()
        structure.has_package_json = (self.project_path / "package.json").exists()
        structure.has_cargo_toml = (self.project_path / "Cargo.toml").exists()
        structure.has_go_mod = (self.project_path / "go.mod").exists()
        structure.has_makefile = any((self.project_path / f).exists() for f in ["Makefile", "makefile", "GNUmakefile"])
        structure.has_dockerfile = (self.project_path / "Dockerfile").exists()

        # Check for CI config
        ci_dirs = [".github", ".gitlab", ".circleci", ".travis"]
        structure.has_ci_config = any((self.project_path / d).exists() for d in ci_dirs)

        # Check for governance files
        if structure.has_governance_dir:
            gov_dir = self.project_path / "governance"
            structure.has_quality_gates = (gov_dir / "quality-gates.yaml").exists()
            structure.has_audit_config = (gov_dir / "audit-config.yaml").exists()
            structure.has_policy_files = any((gov_dir / f).exists() for f in ["policies.yaml", "compliance.yaml"])

        # Check for documentation
        if structure.has_docs_dir:
            docs_dir = self.project_path / "docs"
            structure.has_architecture_docs = any(
                (docs_dir / f).exists() for f in ["architecture.md", "ARCHITECTURE.md", "design.md"]
            )
            structure.has_api_docs = any((docs_dir / d).exists() for d in ["api", "reference", "apidocs"])
            structure.has_contributor_guide = (docs_dir / "CONTRIBUTING.md").exists()

        structure.assess()
        self.structure = structure
        return structure

    def _detect_project_type(self) -> ProjectType:
        """Detect project type from files."""
        has_python = any(
            (self.project_path / f).exists() for f in ["pyproject.toml", "setup.py", "requirements.txt", "Pipfile"]
        )
        has_node = (self.project_path / "package.json").exists()
        has_rust = (self.project_path / "Cargo.toml").exists()
        has_go = (self.project_path / "go.mod").exists()

        types = []
        if has_python:
            types.append(ProjectType.PYTHON)
        if has_node:
            types.append(ProjectType.NODE)
        if has_rust:
            types.append(ProjectType.RUST)
        if has_go:
            types.append(ProjectType.GO)

        if len(types) > 1:
            return ProjectType.MIXED
        if types:
            return types[0]
        return ProjectType.UNKNOWN

    def setup_basic_structure(self):
        """Set up basic project structure."""
        if not self.structure:
            self.analyze()

        # Create directories
        (self.project_path / "docs").mkdir(exist_ok=True)
        (self.project_path / "tests").mkdir(exist_ok=True)
        (self.project_path / "governance").mkdir(exist_ok=True)

        # Create basic README if missing
        if not self.structure.has_readme:
            self._create_readme()

        # Create LICENSE if missing
        if not self.structure.has_license:
            self._create_license()

        # Create governance files
        self._create_governance_files()

    def _create_readme(self):
        """Create basic README.md."""
        readme_content = rf"""# {self.project_path.name}

## Overview

Project description goes here.

## Getting Started

### Prerequisites

- List prerequisites

### Installation

\`\`\`bash
# Installation instructions
\`\`\`

## Usage

\`\`\`bash
# Usage examples
\`\`\`

## Documentation

See [docs/](docs/) for detailed documentation.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

See [LICENSE](LICENSE) for license information.
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

    def _create_governance_files(self):
        """Create governance configuration files."""
        gov_dir = self.project_path / "governance"

        # Quality gates
        quality_gates = {
            "version": "1.0",
            "gates": {
                "code_quality": {
                    "enabled": True,
                    "checks": [
                        "linting",
                        "type_checking",
                        "test_coverage",
                    ],
                    "thresholds": {
                        "test_coverage": 80,
                        "lint_score": 8.0,
                    },
                },
                "documentation": {
                    "enabled": True,
                    "checks": [
                        "readme_exists",
                        "api_docs_complete",
                        "architecture_documented",
                    ],
                },
                "security": {
                    "enabled": True,
                    "checks": [
                        "dependency_scan",
                        "secret_scan",
                        "vulnerability_check",
                    ],
                },
            },
        }

        with open(gov_dir / "quality-gates.yaml", "w") as f:
            yaml.dump(quality_gates, f, default_flow_style=False)

        # Audit config
        audit_config = {
            "version": "1.0",
            "audits": {
                "code_review": {
                    "enabled": True,
                    "frequency": "on_commit",
                },
                "dependency_audit": {
                    "enabled": True,
                    "frequency": "weekly",
                },
                "security_audit": {
                    "enabled": True,
                    "frequency": "monthly",
                },
                "documentation_audit": {
                    "enabled": True,
                    "frequency": "monthly",
                },
            },
        }

        with open(gov_dir / "audit-config.yaml", "w") as f:
            yaml.dump(audit_config, f, default_flow_style=False)

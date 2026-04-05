#!/usr/bin/env python3
"""
Governance Validation Script for thegent

Validates that all 3 groups are complete:
1. Artifacts (CLAUDE.md, PRD.md, ADR.md, specs/)
2. Task Items (FRs with user stories, work packages, acceptance criteria)
3. Governance (AGENTS.md rules, CI/CD, linters)
"""

import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ValidationResult:
    group: str  # artifacts, tasks, governance
    item: str
    status: str  # ✅, ❌, ⚠️
    details: str = ""


class thegentGovernanceValidator:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.results: list[ValidationResult] = []

    def validate_all(self) -> tuple[int, int]:
        """Run all validations and return (passed, total)."""
        self._validate_artifacts()
        self._validate_task_items()
        self._validate_governance()
        return self._print_summary()

    def _validate_artifacts(self):
        """Group 1: Validate container documents."""
        artifacts = [
            ("CLAUDE.md", "AI assistant context"),
            ("PRD.md", "Product requirements"),
            ("ADR.md", "Architecture decisions"),
            ("AGENTS.md", "Agent interaction rules"),
            ("GOVERNANCE.md", "Governance rules"),
            ("specs/", "FR specifications directory"),
            ("specs/FR-THEGENT-001-detail.md", "Detailed FR spec"),
            ("specs/FR-THEGENT-002-detail.md", "Detailed FR spec"),
        ]

        for artifact, purpose in artifacts:
            path = self.repo_path / artifact
            exists = path.exists()
            status = "✅" if exists else "❌"
            details = f"Found: {path}" if exists else f"Missing: {purpose}"
            self.results.append(ValidationResult(
                group="ARTIFACTS",
                item=artifact,
                status=status,
                details=details
            ))

    def _validate_task_items(self):
        """Group 2: Validate actionable units of work."""
        # Check FR specs for completeness
        specs_dir = self.repo_path / "specs"
        if specs_dir.exists():
            fr_specs = list(specs_dir.glob("FR-*.md"))

            for spec in fr_specs:
                content = spec.read_text()
                fr_id = spec.stem

                # Check for user stories
                has_user_story = "## User Story" in content or "**As a**" in content
                # Check for acceptance criteria
                has_acceptance = "## Acceptance Criteria" in content
                has_checkboxes = "- [ ]" in content
                # Check for story points
                has_points = "## Story Points" in content
                # Check for work packages
                has_work_packages = "## Work Packages" in content or "| WP ID |" in content

                # FR completeness score
                score = sum([has_user_story, has_acceptance, has_checkboxes, has_points, has_work_packages])
                status = "✅" if score >= 4 else "⚠️" if score >= 2 else "❌"

                self.results.append(ValidationResult(
                    group="TASK ITEMS",
                    item=f"{fr_id} completeness",
                    status=status,
                    details=f"Score: {score}/5 (user_story:{has_user_story}, acceptance:{has_acceptance}, checkboxes:{has_checkboxes}, points:{has_points}, work_packages:{has_work_packages})"
                ))

        # Check for test FR annotations
        test_files_with_fr = 0
        for pattern in ["**/*test*.rs", "**/*_test.rs", "**/tests/*.rs"]:
            for test_file in self.repo_path.glob(pattern):
                content = test_file.read_text()
                if re.search(r'#\[trace_to\("FR-', content):
                    test_files_with_fr += 1

        status = "✅" if test_files_with_fr >= 3 else "⚠️" if test_files_with_fr > 0 else "❌"
        self.results.append(ValidationResult(
            group="TASK ITEMS",
            item="Test FR annotations",
            status=status,
            details=f"Found {test_files_with_fr} test files with #[trace_to] annotations"
        ))

    def _validate_governance(self):
        """Group 3: Validate enforcement mechanisms."""
        # CI/CD workflow
        ci_path = self.repo_path / ".github/workflows/traceability.yml"
        status = "✅" if ci_path.exists() else "❌"
        self.results.append(ValidationResult(
            group="GOVERNANCE",
            item="CI/CD workflow",
            status=status,
            details="FR traceability workflow" if ci_path.exists() else "Missing .github/workflows/traceability.yml"
        ))

        # AI attribution
        ai_path = self.repo_path / ".phenotype/ai-traceability.yaml"
        status = "✅" if ai_path.exists() else "❌"
        self.results.append(ValidationResult(
            group="GOVERNANCE",
            item="AI attribution",
            status=status,
            details="AI traceability file" if ai_path.exists() else "Missing .phenotype/ai-traceability.yaml"
        ))

        # Rust formatting
        rustfmt = self.repo_path / ".rustfmt.toml"
        status = "✅" if rustfmt.exists() else "⚠️"
        self.results.append(ValidationResult(
            group="GOVERNANCE",
            item="Rust formatting config",
            status=status,
            details="Found" if rustfmt.exists() else "Consider adding .rustfmt.toml"
        ))

        # Cargo clippy config
        cargo_config = self.repo_path / ".cargo/config.toml"
        status = "✅" if cargo_config.exists() else "⚠️"
        self.results.append(ValidationResult(
            group="GOVERNANCE",
            item="Cargo config",
            status=status,
            details="Found" if cargo_config.exists() else "Consider adding .cargo/config.toml"
        ))

    def _print_summary(self) -> tuple[int, int]:
        """Print validation summary and return (passed, total)."""
        print("╔════════════════════════════════════════════════════════════════╗")
        print("║     thegent GOVERNANCE VALIDATION                              ║")
        print("╚════════════════════════════════════════════════════════════════╝")
        print()

        # Group results
        artifacts = [r for r in self.results if r.group == "ARTIFACTS"]
        tasks = [r for r in self.results if r.group == "TASK ITEMS"]
        governance = [r for r in self.results if r.group == "GOVERNANCE"]

        # Print by group
        for group_name, group_results in [
            ("📋 ARTIFACTS", artifacts),
            ("🔧 TASK ITEMS", tasks),
            ("⚖️  GOVERNANCE", governance)
        ]:
            if group_results:
                print(f"\n{group_name}")
                print("─" * 65)
                for r in group_results:
                    print(f"  {r.status} {r.item:<40} {r.details}")

        # Summary
        passed = sum(1 for r in self.results if r.status == "✅")
        warnings = sum(1 for r in self.results if r.status == "⚠️")
        failed = sum(1 for r in self.results if r.status == "❌")
        total = len(self.results)

        print("\n" + "=" * 65)
        print(f"SUMMARY: {passed}/{total} passed, {warnings} warnings, {failed} failed")

        if failed == 0 and warnings == 0:
            print("✅ ALL VALIDATIONS PASSED - Ready for production")
        elif failed == 0:
            print("⚠️  VALIDATIONS PASSED WITH WARNINGS")
        else:
            print("❌ VALIDATIONS FAILED - Address issues before production")

        return passed, total


if __name__ == "__main__":
    import sys
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    validator = thegentGovernanceValidator(repo_path)
    passed, total = validator.validate_all()

    # Exit with error code if any failures
    sys.exit(0 if passed == total else 1)

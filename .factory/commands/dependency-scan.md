---
description: Plan a dependency and licensing scan for the repository
argument-hint: <scope-or-package>
---

Coordinate a dependency scan for `$ARGUMENTS`:

- Identify tools/scripts (`pip-audit`, `uv pip audit`, `npm audit` for frontend if applicable).
- Capture lockfiles to review (`uv.lock`, `requirements*.txt`, `package.json` if present).
- Note SBOM generation (`pip-licenses`, `cyclonedx-python`) and storage location.
- Flag remediation workflow (upgrades, pin adjustments, ADR updates).

Respond with:

Summary: <headline>
Commands:
- <tool>: <command>
Findings:
- <dependency>: <issue> — <severity>
Actions:
- <owner>: <remediation> — <due date>

# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 1.x     | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of **[01;31m[K# [m[Kthegent** seriously. If you discover a security vulnerability, please do NOT open a public issue. Instead, report it privately.

### What to include

- A detailed description of the vulnerability
- Steps to reproduce (proof of concept)
- Potential impact
- Any suggested fixes or mitigations

We will acknowledge your report within 48 hours and provide a timeline for resolution.

## Security Best Practices

Keep dependencies updated and review security advisories regularly.

## Dependency Scanning

# thegent regularly scans dependencies for known vulnerabilities:

- pip-audit — enforced via [`scripts/check_pip_audit_invariants.sh`](scripts/check_pip_audit_invariants.sh) (HIGH-severity ceiling, baseline snapshot at `help/audit/pip-audit-baseline.json`) and gated by the [`pip-audit` CI workflow](.github/workflows/pip-audit.yml).
- Dependabot for automated updates
- Security advisories from Safety DB

Run locally with `make pip-audit` (or `PIP_AUDIT_NO_NETWORK=1 make pip-audit` for the offline path).

## Threat Model

thegent maintains a STRIDE-per-component threat model at
[`docs/security/threat-model.md`](docs/security/threat-model.md). The model covers the
agent loop / orchestrator, tool registry, LLM provider abstraction, Python package supply
chain, CI workflows, MCP server, and Rust shim crates. It is reviewed on every major
release, on the addition of any new external dependency, and quarterly at minimum.

---

Thank you for helping keep the community secure!

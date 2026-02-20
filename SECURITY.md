# Security Policy 🔐

## Supported Versions

We provide security updates for the following versions of **thegent**:

| Version | Supported          |
| ------- | ------------------ |
| v2.0.x  | :white_check_mark: |
| < v2.0  | :x:                |

## Reporting a Vulnerability

We take the security of **thegent** seriously. If you discover a security vulnerability, please do NOT open a public issue. Instead, report it privately.

Please report any security concerns directly to the maintainers at [kooshapari@gmail.com](mailto:kooshapari@gmail.com).

### What to include in your report
- A detailed description of the vulnerability.
- Steps to reproduce (proof of concept).
- Potential impact on the system or user data.
- Any suggested fixes or mitigations.

We will acknowledge your report within 48 hours and provide a timeline for resolution.

## Hardening & Governance Measures

**thegent** is designed with security as a core architectural layer:

- **Rust Isolation**: High-performance Rust extensions handle sensitive path resolution and tool detection to minimize shell injection risks.
- **Stealth Protocol**: Built-in mechanisms to protect agent identity and bypass scraping blocks.
- **Credential Storage**: Uses system keychains or secure local encryption for provider API keys.
- **Audit Trails**: Detailed logging of all agent actions, including tool execution and reasoning steps.
- **Policy Enforcement**: Centralized `governance/` module to prevent agents from performing unsafe or non-compliant operations.

---
Thank you for helping keep the agentic ecosystem secure!

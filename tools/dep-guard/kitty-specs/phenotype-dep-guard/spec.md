# Specification: phenotype-dep-guard

## Overview
`phenotype-dep-guard` is a malicious dependency analysis system designed to detect supply chain attacks (e.g., litellm 1.82.7 .pth credential stealers). It employs a hybrid approach combining programmatic static analysis (AST/heuristics) with agentic LLM deep-diving (minimax-m2.7-highspeed, gpt-5-mini).

## Functional Requirements
- **FR1: Dependency Graph Resolution**: Support for PyPI (pip), npm, and Cargo (transitive dependencies).
- **FR2: Static Triage Layer**: Rapid heuristic scanning for suspicious patterns (e.g., `.pth` files, obfuscated strings, unexpected network activity in setup scripts).
- **FR3: Agentic Deep Analysis**: Automated LLM-driven research into flagged dependencies to determine intent.
- **FR4: Evidence Collection**: Hash-chained audit trails for all scan results and LLM reasoning steps.
- **FR5: Alerting & Remediation**: Confidence-scored alerts with automated PR creation for version pinning/removal.

## Technical Architecture (Hexagonal)
- **Ports**: 
  - `DependencyPort`: Resolves graphs.
  - `ScannerPort`: Heuristic/AST scanners.
  - `LLMPort`: Interface for minimax and gpt-5-mini via `forge -p`.
  - `AuditPort`: Immutable logging.
- **Adapters**:
  - `PipAdapter`, `NpmAdapter`.
  - `HeuristicScanner`, `SemgrepScanner`.
  - `ForgeLLMAdapter`.

## Execution Plan
1. **Phase 1**: Static Triage Core (Python/Rust).
2. **Phase 2**: LLM Orchestration (Forge integration).
3. **Phase 3**: AgilePlus Governance & Reporting.

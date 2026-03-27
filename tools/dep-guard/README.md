# phenotype-dep-guard

Malicious dependency analysis and supply chain security guard.

## Layer Contract

- layer_type: security_ops
- layer_name: phenotype-dep-guard
- versioning: semver

## Mission

Analyze direct and transitive dependencies for malicious code, vulnerabilities, and anomalous behavior.

1. High-velocity multi-source dependency resolution.
2. Heuristic and static triage (AST parsing, .pth/setup.py scanning).
3. Agentic LLM deep analysis (minimax-m2.7-highspeed, gpt-5-mini).
4. Reporting and alerting.

## Spec Kitty Workflow

```bash
spec-kitty research --feature layered-template-platform --force
```

Primary feature workspace:

- `kitty-specs/layered-template-platform/`

## Operational Workflow

1. Run `task check` before release.
2. Keep manifest/reconcile files aligned for any contract-affecting change.
3. Run `task release:prep` as final pre-release gate.

## Outputs

- Layer contract specs
- WP DAG and execution lanes
- Reconcile contract and acceptance criteria

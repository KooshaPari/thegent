# Packages

This directory contains product-bound Phenotype packages: domain packages, branded tools, engines, and shared internal components that are not positioned as neutral public libraries.

## Classification

See:

- [ADR-002: Package Classification Framework](../governance/adrs/0002-package-classification-framework.md)
- [ADR-006: Library vs Package Distinction](../governance/adrs/0006-library-vs-package-distinction.md)
- [ADR-007: Library vs Tool Distinction](../governance/adrs/ADR-007-library-vs-tool.md)

## Package Rules

- **Primary naming convention**: `phenotype-*`
- **Publishing**: internal or product-specific distribution
- **Coupling**: packages may depend on other packages and on reusable libraries in `libs/`

## Current Package Inventory

### Core Product Packages

- `phenotype-session/`
- `phenotype-agent/`
- `phenotype-auth/`
- `phenotype-config/`
- `phenotype-design/`
- `phenotype-docs/`
- `phenotype-research/`
- `phenotype-task/`
- `phenotype-skills-clone/`
- `phenotype-actions/`

### Tool and Platform Packages

- `phenotype-cli-core/`
- `phenotype-cli-extensions/`
- `phenotype-colab-extensions/`
- `phenotype-dep-guard/`
- `phenotype-forge/`

### Engines, Shared Runtime, and Language-Specific Product Packages

- `phenotype-auth-ts/`
- `phenotype-cipher/`
- `phenotype-config-client/`
- `phenotype-config-ts/`
- `phenotype-docs-engine/`
- `phenotype-evaluation/`
- `phenotype-gauge/`
- `phenotype-go-kit/`
- `phenotype-infrakit/`
- `phenotype-logger/`
- `phenotype-logging-zig/`
- `phenotype-metrics/`
- `phenotype-middleware-py/`
- `phenotype-nexus/`
- `phenotype-sdk/`
- `phenotype-shared/`
- `phenotype-task-engine/`
- `phenotype-tracing/`
- `phenotype-research-engine/`
- `phenotype-xdd/`
- `phenotype-xdd-lib/`

## Relationship to `libs/`

Use `packages/` when a component is product-bound, branded, or coupled to Phenotype-specific workflows.

Use `libs/` when a component is intended to be reusable, domain-neutral, and publishable with a neutral name.

## Validation Entry Points

Repository-level validation is driven by the root scripts:

```bash
# Tool/product package validation
bash ../scripts/test-tools.sh
bash ../scripts/build-tools.sh

# Library validation
bash ../scripts/test-all-libs.sh
bash ../scripts/build-all-libs.sh
bash ../scripts/verify-libs.sh
```

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md).

## License

Each package should declare its own license and publishing metadata.

# Architecture Boundary Templates — Hexagonal Architecture Enforcement

**Status:** Reference implementation for Items 6–8 (architecture, schema, changelog gates)

**Purpose:** Reusable boundary patterns to fail CI when domain imports infrastructure, breaking schemas appear, or versions/changelogs are missing.

---

## Part A: Architecture Boundary Tests (Item 6)

### Python + `tach`

**When:** Use in Python codebases (thegent, domain services, etc.)

**Installation & Setup:**

```bash
pip install tach
cd <repo>
tach init  # creates tach.yml
tach check  # validates bounds
```

**Hexagonal Architecture Rules (tach.yml pattern):**

```yaml
# tach.yml — Phenotype hexagonal boundaries

# Domain layer (business logic, entities, use cases)
modules:
  - path: src/domain
    allowed_dependencies:
      - src/shared  # only to shared utilities
    disallowed_dependencies:
      - src/infrastructure
      - src/adapters
      - src/external

  # Infrastructure layer (databases, APIs, logging)
  - path: src/infrastructure
    allowed_dependencies:
      - src/shared
      - src/domain  # CAN depend on domain (inverse not allowed)
    disallowed_dependencies:
      - src/adapters  # infra should not depend on specific adapters

  # Adapters / Application layer (HTTP routes, CLI, etc.)
  - path: src/adapters
    allowed_dependencies:
      - src/domain
      - src/infrastructure
      - src/shared
    disallowed_dependencies: []

  # Shared utilities (no dependencies)
  - path: src/shared
    allowed_dependencies: []
    disallowed_dependencies:
      - src/domain
      - src/infrastructure
      - src/adapters
```

**CI Integration (GitHub Actions):**

```yaml
# .github/workflows/lint-architecture.yml
name: Lint Architecture Boundaries

on: [pull_request, push]

jobs:
  tach:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install tach
      - run: tach check
```

---

### TypeScript + `eslint-plugin-boundaries`

**When:** Use in TypeScript/JavaScript codebases (heliosApp, phenotype-config-ts, etc.)

**Installation & Setup:**

```bash
npm install --save-dev eslint-plugin-boundaries
# or yarn add --dev eslint-plugin-boundaries
```

**Hexagonal Architecture Rules (.eslintrc.json pattern):**

```json
{
  "plugins": ["eslint-plugin-boundaries"],
  "rules": {
    "boundaries/element-types": [
      "error",
      {
        "default": "disallow",
        "rules": [
          {
            "from": ["domain"],
            "to": ["shared"],
            "allow": ["*"]
          },
          {
            "from": ["domain"],
            "to": ["infrastructure"],
            "disallow": ["*"]
          },
          {
            "from": ["domain"],
            "to": ["adapters"],
            "disallow": ["*"]
          },
          {
            "from": ["infrastructure"],
            "to": ["domain", "shared"],
            "allow": ["*"]
          },
          {
            "from": ["infrastructure"],
            "to": ["adapters"],
            "disallow": ["*"]
          },
          {
            "from": ["adapters"],
            "to": ["domain", "infrastructure", "shared"],
            "allow": ["*"]
          },
          {
            "from": ["shared"],
            "to": ["domain", "infrastructure", "adapters"],
            "disallow": ["*"]
          }
        ]
      }
    ]
  }
}
```

**Directory Structure (aligned with rules):**

```
src/
├── domain/           # Business logic, entities, use cases
├── infrastructure/   # DB, logging, external service clients
├── adapters/         # HTTP routes, CLI, event handlers
└── shared/           # Utilities, types, constants (no deps)
```

**CI Integration (GitHub Actions):**

```yaml
# .github/workflows/lint-architecture.yml
name: Lint Architecture Boundaries

on: [pull_request, push]

jobs:
  eslint-boundaries:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - run: npm install
      - run: npm run lint:boundaries
        # Script in package.json: eslint src --rule boundaries/element-types:error
```

---

## Part B: Schema Compatibility Checks (Item 7)

### OpenAPI + `openapi-diff`

**When:** Use for REST APIs with OpenAPI/Swagger specs (phenotype-config, heliosApp API, etc.)

**Installation & Setup:**

```bash
npm install --save-dev openapi-diff
```

**Configuration & Breaking Change Detection:**

```bash
#!/bin/bash
# scripts/check-schema-compat.sh

OLD_SPEC="docs/api/openapi.yaml"  # Current main spec
NEW_SPEC="docs/api/openapi.yaml"  # PR/branch spec

openapi-diff "$OLD_SPEC" "$NEW_SPEC" \
  --severity error \
  --break-on-incompatible

# Exit codes:
# 0 = no breaking changes
# 1 = breaking changes detected
# 2 = error in script execution
```

**JSON Schema + `json-schema-diff`:**

```bash
npm install --save-dev json-schema-diff

# Detect breaking changes in JSON schemas
json-schema-diff old-schema.json new-schema.json --check=breaking
```

**CI Integration:**

```yaml
# .github/workflows/schema-compat.yml
name: Check Schema Compatibility

on: [pull_request, push]

jobs:
  schema-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - run: npm install
      - run: bash scripts/check-schema-compat.sh
```

**Whitelist Breaking Changes (when intentional):**

```yaml
# .schema-breaking-changes.yml (in main only)
breaking_changes:
  - change: "Removed deprecated /v1/users endpoint"
    date: "2026-03-26"
    reason: "Migrate to /v2/users (added 2026-01-15)"
    migration_guide: "docs/migration/v1-v2-users.md"
```

---

## Part C: Changelog / Version Gate (Item 8)

### Requirements

**When:** Require CHANGELOG entry and version bump for:
- Any src/ or public API changes
- Major dependency upgrades
- Schema/contract changes (from Part B)

**Gate Logic:**

```bash
#!/bin/bash
# scripts/check-version-gate.sh

# 1. Detect if src/ or public API changed
CHANGED_FILES=$(git diff --name-only origin/main...)
HAS_SRC_CHANGE=$(echo "$CHANGED_FILES" | grep -E '^src/' | wc -l)
HAS_API_CHANGE=$(echo "$CHANGED_FILES" | grep -E 'schema|interface|contract' | wc -l)

# 2. Check CHANGELOG.md was updated
if [ "$HAS_SRC_CHANGE" -gt 0 ] || [ "$HAS_API_CHANGE" -gt 0 ]; then
  if ! echo "$CHANGED_FILES" | grep -q '^CHANGELOG.md$'; then
    echo "❌ CHANGELOG.md must be updated when src/ or API changes"
    exit 1
  fi
fi

# 3. Check version bump in package.json / pyproject.toml / Cargo.toml
# (varies by language/package manager)
```

**CHANGELOG Format (Keep It Simple):**

```markdown
# Changelog

## [Unreleased]

## [1.2.0] — 2026-03-26

### Added
- New `/v2/users` REST endpoint for bulk operations

### Changed
- Upgraded `phenotype-config` to 2.0 (see MIGRATION.md)

### Fixed
- OCC hash consistency in file read/write (#763)

### Deprecated
- `/v1/users` endpoint (use `/v2/users` instead; removal in v2.0)

## [1.1.0] — 2026-02-15
...
```

**CI Integration:**

```yaml
# .github/workflows/version-gate.yml
name: Version & Changelog Gate

on: [pull_request, push]

jobs:
  version-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for merge-base detection
      - run: bash scripts/check-version-gate.sh
```

---

## Part D: Implementation Checklist

**For each repository:**

- [ ] Item 6: Add tach (Python) or eslint-plugin-boundaries (TypeScript)
  - [ ] Create `.tach.yml` or update `.eslintrc.json`
  - [ ] Add GitHub Actions workflow for architecture check
  - [ ] Document allowed dependencies in ARCHITECTURE.md
  - [ ] Run locally: `tach check` or `npm run lint:boundaries`

- [ ] Item 7: Add schema compatibility check
  - [ ] Install `openapi-diff` or `json-schema-diff`
  - [ ] Create `scripts/check-schema-compat.sh`
  - [ ] Add GitHub Actions workflow
  - [ ] Document in API docs

- [ ] Item 8: Add version / changelog gate
  - [ ] Create `scripts/check-version-gate.sh`
  - [ ] Create CHANGELOG.md (if not present)
  - [ ] Add GitHub Actions workflow
  - [ ] Document in CONTRIBUTING.md

---

## References

- **tach:** https://github.com/gauge-sh/tach
- **eslint-plugin-boundaries:** https://github.com/javierbrea/eslint-plugin-boundaries
- **openapi-diff:** https://github.com/opticdev/optic-diff
- **json-schema-diff:** https://json-schema.org/tools

---

## Next Steps

1. Implement in **thegent** (Python tach) — PR to main
2. Implement in **heliosApp** (TypeScript eslint) — PR to main
3. Extend to secondary repos (AgilePlus, agentapi-plusplus, heliosCLI, phenotype-config)
4. Document enforcement across ecosystem in hub

---

**Last Updated:** 2026-03-26  
**Author:** Agent (Cursor / Forge)  
**Governance:** docs/governance/xdd-methodology-catalog.md (Item 6–8)

# ADR-005: Top-Level Directory Structure

**Date:** 2026-03-25
**Status:** Proposed
**Supersedes:** ADR-001 (Repository Organization)

---

## Context

The Phenotype ecosystem has grown organically, resulting in:
- 20+ `phenotype-*` repositories at the top level
- No clear separation between different types of projects
- Difficulty finding relevant repositories
- Inconsistent organization within repositories

This ADR establishes a **canonical top-level directory structure** that provides clear separation between:
1. Phenotype-domain bound packages
2. Extractable/marketable libraries
3. Applications
4. Infrastructure
5. Governance and tooling

---

## Decision

### Proposed Top-Level Structure

```
Phenotype/
├── repos/                    # Main workspace
│   ├── apps/                 # End-user applications
│   ├── packages/             # Phenotype-domain bound packages
│   ├── libs/                 # Extractable/marketable libraries
│   ├── services/             # Microservices
│   ├── infrastructure/       # IaC, Kubernetes, Terraform
│   ├── templates/            # Project templates
│   ├── governance/           # ADRs, standards, processes
│   ├── tools/                # Developer tooling
│   ├── skills/               # Agent skills
│   └── plans/                # Project plans and RFCs
│
├── docs/                     # Shared documentation
├── .github/                  # Organization-level GitHub config
└── README.md                 # Root README
```

### Directory Definitions

#### `apps/`

**Purpose:** End-user applications and CLIs

**Contents:**
- `phenotype-cli/` - Primary CLI application
- `phenotype-web/` - Web frontend application
- `phenotype-api/` - Backend API application
- `phenotype-desktop/` - Desktop application
- `phenotype-mobile/` - Mobile application

**Characteristics:**
- Deployable as complete units
- May depend on `packages/` and `libs/`
- Typically have their own CI/CD pipelines
- End-user facing

#### `packages/`

**Purpose:** Phenotype-domain bound packages (Type A)

**Contents:**
- `phenotype-config/` - Feature flags, secrets, versioning
- `phenotype-design/` - Design tokens, themes
- `phenotype-auth/` - Authentication logic
- `phenotype-agent/` - Agent core logic
- `phenotype-task/` - Task orchestration
- `phenotype-research/` - Research engine
- `phenotype-docs/` - Documentation engine

**Characteristics:**
- Phenotype-specific business logic
- May depend on `libs/`
- Not intended for external use
- Should be published to internal registry if needed

#### `libs/`

**Purpose:** Extractable/marketable libraries (Type B)

**Contents:**
- `hexagonal-rs/` - Rust hexagonal architecture
- `hexagonal-ts/` - TypeScript hexagonal architecture
- `hexagonal-py/` - Python hexagonal architecture
- `hexagonal-go/` - Go hexagonal architecture
- `xdd-lib/` - xDD utilities (property testing, contracts)
- `event-sourcing/` - Event sourcing patterns
- `state-machine/` - State machine implementation
- `policy-engine/` - Policy evaluation
- `cache-adapter/` - Caching patterns
- `observability/` - Logging, metrics, tracing
- `config-lib/` - Configuration loading

**Characteristics:**
- General-purpose, framework-agnostic
- Should be publishable to public registries
- Well-documented with examples
- >80% test coverage required

#### `services/`

**Purpose:** Microservices

**Contents:**
- `api-gateway/` - API Gateway service
- `user-service/` - User management microservice
- `notification-service/` - Notifications microservice
- `worker-service/` - Background worker service

**Characteristics:**
- Deployable independently
- Clear bounded contexts
- May depend on `libs/`
- API-first design

#### `infrastructure/`

**Purpose:** Infrastructure as Code and deployment configurations

**Contents:**
- `terraform/` - Terraform modules
- `kubernetes/` - Kubernetes manifests
- `docker/` - Docker configurations
- `ansible/` - Ansible playbooks
- `helm/` - Helm charts

**Characteristics:**
- Infrastructure as Code (IaC)
- Version controlled
- Environment-specific configurations
- Should NOT contain application code

#### `templates/`

**Purpose:** Project templates for scaffolding

**Contents:**
- `template-commons/` - Shared template resources
- `template-hexagonal/` - Universal hexagonal template
- `template-lang-rust/` - Rust project template
- `template-lang-go/` - Go project template
- `template-lang-typescript/` - TypeScript project template
- `template-lang-python/` - Python project template
- `template-lang-zig/` - Zig project template

**Characteristics:**
- Used for generating new projects
- Should include all standard files (README, CLAUDE.md, etc.)
- Language-specific conventions

#### `governance/`

**Purpose:** Cross-cutting governance and standards

**Contents:**
- `adrs/` - Architecture Decision Records
- `standards/` - Coding standards by language
- `processes/` - Workflow documentation
- `templates/` - Document templates

**Characteristics:**
- Organization-wide standards
- Living documents
- Should be referenced by all projects

#### `tools/`

**Purpose:** Developer tooling and utilities

**Contents:**
- `forge-scripts/` - Custom Forge extensions
- `dev-scripts/` - Development utilities
- `migration-tools/` - Data migration tools
- `ci-tools/` - CI/CD utilities

**Characteristics:**
- Internal developer tools
- Not deployed with applications
- Should be versioned

#### `skills/`

**Purpose:** Agent/SAGE skills for automation

**Contents:**
- Agent skill definitions
- Skill documentation
- Skill implementations

**Characteristics:**
- Used by Forge/SAGE agents
- Specialized for the Phenotype ecosystem
- Should be well-documented

#### `plans/`

**Purpose:** Project plans, RFCs, and roadmaps

**Contents:**
- Project plans (as markdown)
- Request for Comments (RFCs)
- Roadmap documents
- Technical specifications

**Characteristics:**
- Living documents
- Version controlled
- Should be actionable

---

## Migration Mapping

### Current to Proposed

| Current Location | Proposed Location | Notes |
|------------------|-------------------|-------|
| `repos/phenotype-config` | `repos/packages/phenotype-config` | Type A - Phenotype-domain |
| `repos/phenotype-design` | `repos/packages/phenotype-design` | Type A - Phenotype-domain |
| `repos/phenotype-agent-core` | `repos/packages/phenotype-agent` | Type A - Phenotype-domain |
| `repos/phenotype-hexagonal` | `repos/libs/hexagonal-rs` | Type B - Extractable |
| `repos/phenotype-ts-hexagonal` | `repos/libs/hexagonal-ts` | Type B - Extractable |
| `repos/phenotype-py-hexagonal` | `repos/libs/hexagonal-py` | Type B - Extractable |
| `repos/phenotype-go-hexagonal` | `repos/libs/hexagonal-go` | Type B - Extractable |
| `repos/phenotype-xdd-lib` | `repos/libs/xdd-lib-rs` | Type B - Extractable |
| `repos/phenotype-shared/crates/*` | `repos/libs/*` | Type B - Review individually |
| `repos/phenotype-infrakit` | `repos/infrastructure/phenotype-infrakit` | Infrastructure |
| `repos/phenotype-skills-clone` | `repos/governance/skills-catalog` | Governance |
| `repos/template-commons` | `repos/templates/template-commons` | Template |
| `repos/template-lang-*` | `repos/templates/template-lang-*` | Templates |

### New Directories to Create

```bash
mkdir -p repos/{apps,packages,libs,services}
mv repos/phenotype-* repos/packages/ 2>/dev/null || true
mv phenotype-hexagonal repos/libs/hexagonal-rs 2>/dev/null || true
# ... etc
```

---

## Consequences

### Positive

1. **Clear separation** - Easy to find what you're looking for
2. **Scalable** - New directories can be added without clutter
3. **Consistent** - All repos follow the same pattern
4. **Discoverable** - New team members understand structure quickly

### Negative

1. **Migration effort** - Existing repos need to be moved
2. **Git history** - Moving repos changes paths (use `git mv`)
3. **CI/CD updates** - Build configurations may need updates
4. **Import updates** - Package references need updating

### Neutral

1. **GitHub org structure** - Mirrors the logical structure
2. **Learning curve** - Team needs to learn new locations

---

## Alternatives Considered

### Alternative 1: Keep Flat Structure

**Pros:**
- No migration needed
- Simple

**Cons:**
- Doesn't scale
- Becomes harder to navigate over time
- No clear boundaries

**Why not chosen:** Doesn't address the root problem of organization.

### Alternative 2: Group by Language

**Pros:**
- Easy for mono-language developers
- Simple categorization

**Cons:**
- Doesn't reflect architectural boundaries
- Phenotype-specific and generic mixed
- Makes cross-language projects awkward

**Why not chosen:** Doesn't provide architectural clarity.

---

## References

- [xDD Methodology Compendium](../xdd-methodology-compendium.md)
- [ADR-001: Repository Organization](./0001-repository-organization.md)
- [ADR-002: Package Classification Framework](./0002-package-classification-framework.md)
- [ADR-004: Naming Conventions](./0004-naming-conventions.md)

---

## Implementation Notes

### Phase 1 (Foundation)
- Create directory structure
- Create governance documents
- Update ADR references

### Phase 2 (Migration)
- Move Type B packages to `libs/`
- Rename packages (remove `phenotype-` prefix)
- Update import paths

### Phase 3 (Consolidation)
- Move Type A packages to `packages/`
- Archive placeholder repos
- Consolidate duplicate functionality

### Phase 4 (Cleanup)
- Move infrastructure to `infrastructure/`
- Move governance to `governance/`
- Update CI/CD pipelines

---

*Created: 2026-03-25*
*Maintained by: Architecture Guild*

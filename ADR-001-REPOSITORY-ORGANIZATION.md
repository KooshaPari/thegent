# ADR-001: Repository Organization and Hexagonal Architecture

## Status

**Accepted** - 2026-03-25

## Context

The Phenotype ecosystem (`repos/`) has grown organically and exhibits several architectural issues:

### Problems Identified

1. **Namespace Pollution**: ~100 repositories at the top level with no clear categorization
2. **Broken Folder**: `4sgm bifrost-extensions phenotype-config portage cliproxyapi++` contains spaces (breaks tooling)
3. **Legacy Worktrees**: 15+ `*-wtrees` folders violating the worktree governance policy
4. **Inconsistent Structure**: No standard for hexagonal architecture across crates
5. **Libification Gap**: Shared code duplicated across repositories instead of extracted libs

### Decision Drivers

- Need for maintainable code organization as ecosystem grows
- Require clear separation of concerns (apps vs libs vs infra)
- Need consistent architecture patterns (hexagonal) across polyrepo
- Must enable easy discovery of related repositories
- Support for multiple programming languages (Rust, Go, TypeScript, Python)

## Decision

### 1. Repository Namespace Restructuring

Adopt a categorized top-level namespace:

```
repos/
├── apps/                        # Application repositories
│   ├── cli/                    # Command-line applications
│   ├── web/                    # Web applications
│   └── services/               # Microservices
│
├── libs/                        # Shared libraries (libification)
│   ├── rust/                   # Rust crates
│   ├── go/                     # Go modules
│   ├── typescript/             # TypeScript packages
│   └── python/                 # Python packages
│
├── infrastructure/              # DevOps & deployment
├── governance/                  # Project management
├── tooling/                     # Developer tools
└── templates/                   # Project scaffolding
```

### 2. Hexagonal Architecture Standard

All library crates MUST follow Hexagonal Architecture (Ports and Adapters):

```
src/
├── domain/                    # Pure domain logic (ZERO dependencies)
│   ├── entities/             # Business objects with identity
│   ├── value_objects/        # Immutable types
│   ├── services/             # Domain services
│   ├── events/               # Domain events
│   └── ports/                # Port interfaces
│       ├── inbound/          # Primary ports (use cases)
│       └── outbound/          # Secondary ports (infrastructure)
│
├── application/              # Application layer
│   ├── use_cases/           # Use case implementations
│   ├── dto/                 # Data transfer objects
│   ├── commands/            # Command handlers
│   └── queries/             # Query handlers
│
└── adapters/                # Infrastructure adapters
    ├── inbound/            # Primary adapters (API, CLI)
    └── outbound/            # Secondary adapters (DB, Cache)
```

### 3. Dependency Rule

```
Adapters ──implements──► Domain Ports (interfaces)
Application ──uses──────► Domain Ports
Application ──depends───► Domain (ONLY)
Domain ──NO DEPENDENCIES──► Anything external
```

### 4. Worktree Governance

- Legacy `*-wtrees` folders migrated to `.archive/legacy-worktrees/`
- New worktrees created under `worktrees/<project>/<category>/<name>`
- Canonical repositories track `main` only

### 5. Library Extraction

Shared libraries are extracted into `libs/shared/` following the hexagonal pattern:
- `libs/shared/hexagonal/` - Hexagonal architecture base classes and interfaces
- `libs/shared/logging/` - Shared logging adapters
- `libs/shared/metrics/` - Shared metrics collection
- `libs/shared/config/` - Shared configuration management
- `libs/shared/events/` - Shared event bus infrastructure
- `libs/shared/cli/` - Shared CLI utilities
- `libs/shared/telemetry/` - Shared telemetry/tracing

## Consequences

### Positive

- **Discoverability**: Easy to find related repos by category
- **Consistency**: Standard structure across all projects
- **Testability**: Clear boundaries enable unit testing
- **Extensibility**: Easy to swap adapters (DB, cache, etc.)
- **Maintainability**: Isolated domain logic
- **Reusability**: Clear lib extraction opportunities

### Negative

- **Migration Effort**: Existing repos need restructuring
- **Learning Curve**: Team must learn hexagonal patterns
- **Indirection**: More files/modules for simple projects
- **Tooling**: May need scripts to generate structure

### Mitigations

- Provide templates for each language (`template-commons/templates/`)
- Create code generation scripts
- Document anti-patterns to avoid
- Phased migration with backward compatibility

## Implementation

### Phase 1: Namespace Cleanup (Completed)

- [x] Archive broken folder `4sgm bifrost-extensions phenotype-config portage cliproxyapi++`
- [x] Create top-level category directories
- [x] Migrate legacy `*-wtrees` folders to `worktrees/`

### Phase 2: Template Creation (Completed)

- [x] `template-commons/templates/hexagonal-rust/` - Rust crate template
- [x] `template-commons/templates/hexagonal-go/` - Go module template
- [ ] `template-commons/templates/hexagonal-typescript/` - (Future)
- [ ] `template-commons/templates/hexagonal-python/` - (Future)

### Phase 3: Crate Migration (In Progress)

- [x] `phenotype-shared/crates/phenotype-state-machine/` - Refactored
- [ ] `phenotype-shared/crates/phenotype-event-sourcing/` - (Pending)
- [ ] `phenotype-shared/crates/phenotype-cache-adapter/` - (Pending)
- [ ] `phenotype-shared/crates/phenotype-policy-engine/` - (Pending)

### Phase 4: Libification (Planned)

- Audit shared code across repos
- Extract duplicates into `template-commons/`
- Create proper versioning strategy

## Alternatives Considered

| Alternative | Why Not Chosen |
|-------------|----------------|
| Monorepo | Too large, CI blast radius, team autonomy |
| Pure Polyrepo | Duplication, no shared standards |
| Domain-based grouping | Overlapping domains, hard to categorize |
| Layered Architecture | Less explicit boundaries |

## References

- [Hexagonal Architecture - Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture/)
- [Ports and Adapters - ThoughtBot](https://thoughtbot.com/blog/hexagonal-rails)
- [Clean Architecture - Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design - Vaughn Vernon](https://www.amazon.com/dp/0321834577)

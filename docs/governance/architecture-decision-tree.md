# Architecture Decision Tree: Pattern Selection Guide

**Version:** 1.0.0
**Purpose:** Interactive decision tree for selecting appropriate architectural patterns

---

## Quick Decision Tree

```
START: What are you building?
│
├─► Is domain complexity HIGH?
│   └─ YES → Use DDD (Domain-Driven Design)
│           │
│           └─► Is domain EVENT-DRIVEN?
│               └─ YES → Add Event Sourcing
│               └─ NO → Add CQRS if read/write patterns differ
│
├─► Is domain complexity MEDIUM?
│   └─ YES → Use Clean Architecture or Hexagonal
│           │
│           └─► Need to swap implementations?
│               └─ YES → Use Ports & Adapters (Hexagonal)
│               └─ NO → Use Clean Architecture
│
└─► Is domain complexity LOW?
    └─ YES → Use Layered Architecture
            │
            └─► Is it a simple CRUD app?
                └─ YES → Use Repository Pattern
                └─ NO → Add Service Layer

---

ARCHITECTURE TYPE SELECTION:

┌────────────────────────────────────────────────────────────────────┐
│ COMPLEXITY →─────────────► PATTERN                                    │
├────────────────────────────────────────────────────────────────────┤
│ Simple CRUD      →        Layered Architecture + Repository          │
│ Medium Domain    →        Clean Architecture                         │
│ Complex Domain   →        Hexagonal + DDD                            │
│ Event-Driven     →        Event Sourcing + CQRS                     │
│ High-Scale Read  →        CQRS + Read Replicas                      │
│ Distributed      →        Microservices + Saga                       │
│ Real-time        →        EDA + WebSockets                           │
│ Library/SDK     →        Plugin Architecture + Facade                 │
│ Plugin System    →        Extension Points + Strategy Pattern        │
└────────────────────────────────────────────────────────────────────┘
```

---

## Domain Complexity Assessment

### Low Complexity Indicators

- [ ] CRUD operations (Create, Read, Update, Delete)
- [ ] Simple business rules
- [ ] Few entities (< 10)
- [ ] No complex relationships
- [ ] Single domain
- [ ] No need for multiple bounded contexts

**→ Use:** Layered Architecture

### Medium Complexity Indicators

- [ ] Business rules that span multiple entities
- [ ] Some complex validations
- [ ] Multiple domain concepts
- [ ] Need for clear boundaries
- [ ] Testing requirements
- [ ] Potential for future growth

**→ Use:** Clean Architecture

### High Complexity Indicators

- [ ] Complex business domain
- [ ] Ubiquitous language needed
- [ ] Multiple bounded contexts
- [ ] Complex aggregations
- [ ] Eventual consistency acceptable
- [ ] Rich domain models
- [ ] Strategic design required

**→ Use:** Hexagonal + DDD

---

## Pattern Combination Matrix

```
┌──────────────────────┬────────────┬────────────┬───────────┬───────────┬────────────┐
│ Pattern              │ Complexity │ Team Size │ Scale     │ Change    │ Time      │
├──────────────────────┼────────────┼────────────┼───────────┼───────────┼────────────┤
│ Layered              │ Low        │ Any        │ Small     │ Slow      │ Fast      │
│ Clean                │ Medium     │ 2-20       │ Medium    │ Moderate  │ Moderate  │
│ Hexagonal            │ High       │ 2-50       │ Large     │ Fast      │ Slow      │
│ Microservices        │ High       │ 5-100+     │ Very High │ Fast      │ Slowest   │
│ Modular Monolith     │ Medium     │ Any        │ Medium    │ Moderate  │ Moderate  │
│ Serverless           │ Any        │ Any        │ Any       │ Any       │ Moderate  │
└──────────────────────┴────────────┴────────────┴───────────┴───────────┴────────────┘

LEGEND:
- Complexity: How complex the domain/business logic is
- Team Size: Recommended team size
- Scale: Expected load and growth
- Change: How frequently requirements change
- Time: Time to initial implementation
```

---

## Technology Stack → Pattern Mapping

```
┌────────────────────────────────────────────────────────────────────┐
│ TECHNOLOGY STACK → RECOMMENDED PATTERNS                              │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│ RUST                                                               │
│ ├─► Clean Architecture (modules)                                   │
│ ├─► Hexagonal (traits as ports)                                    │
│ └─► Event Sourcing (via async queues)                              │
│                                                                    │
│ TYPESCRIPT/JAVASCRIPT                                              │
│ ├─► Clean Architecture (folders)                                   │
│ ├─► Hexagonal (dependency injection)                                │
│ ├─► DDD (bounded contexts)                                        │
│ └─► Event Sourcing (EventEmitter)                                  │
│                                                                    │
│ PYTHON                                                             │
│ ├─► Clean Architecture (package structure)                        │
│ ├─► Hexagonal (abstract base classes)                             │
│ ├─► DDD (value objects, entities)                                 │
│ └─► CQRS (separate read/write handlers)                           │
│                                                                    │
│ GO                                                                 │
│ ├─► Clean Architecture (packages)                                 │
│ ├─► Hexagonal (interfaces)                                        │
│ ├─► Microservices (goroutines, channels)                           │
│ └─► Event Sourcing (Kafka, NATS)                                  │
│                                                                    │
│ JAVA/KOTLIN                                                        │
│ ├─► Clean Architecture                                             │
│ ├─► Hexagonal (Ports & Adapters)                                  │
│ ├─► DDD (bounded contexts)                                        │
│ ├─► Event Sourcing (Axon, EventStoreDB)                           │
│ └─► CQRS (Axon Framework)                                        │
│                                                                    │
│ ELIXIR/PHOENIX                                                     │
│ ├─► Clean Architecture                                            │
│ ├─► DDD (contexts)                                               │
│ ├─► Event Sourcing (Phoenix.PubSub)                               │
│ └─► CQRS (separate read models)                                   │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## Layer Selection Algorithm

```
┌────────────────────────────────────────────────────────────────────┐
│ LAYERED ARCHITECTURE SELECTION                                      │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│ START: How many layers do you need?                               │
│                                                                    │
│ 1 LAYER (Monolithic)                                              │
│    └─► Single src/ directory                                     │
│        Use for: Scripts, utilities, simple tools                    │
│                                                                    │
│ 2 LAYERS                                                          │
│    ├─► Domain (business logic)                                   │
│    └─► Infrastructure (DB, API)                                  │
│        Use for: Simple services, libraries                         │
│                                                                    │
│ 3 LAYERS (Traditional)                                            │
│    ├─► Presentation (controllers, views)                         │
│    ├─► Business (services, rules)                                │
│    └─► Data (repositories, ORM)                                  │
│        Use for: Web applications, CRUD apps                       │
│                                                                    │
│ 4 LAYERS (Clean)                                                  │
│    ├─► Frameworks & Drivers (infra)                              │
│    ├─► Interface Adapters (controllers, gateways)                 │
│    ├─► Application (use cases)                                   │
│    └─► Enterprise Business Rules (domain)                         │
│        Use for: Enterprise apps, testable systems                  │
│                                                                    │
│ 5+ LAYERS (Hexagonal)                                             │
│    ├─► Domain Core (entities, services, events)                  │
│    ├─► Ports (inbound & outbound interfaces)                    │
│    ├─► Primary Adapters (REST, CLI, UI)                         │
│    ├─► Secondary Adapters (DB, external APIs)                    │
│    └─► Infrastructure (config, DI)                              │
│        Use for: Complex domains, swappable implementations        │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## Code Organization Decision Tree

```
PROJECT TYPE → DIRECTORY STRUCTURE

┌────────────────────────────────────────────────────────────────────┐
│ COMMAND-LINE TOOL                                                  │
├────────────────────────────────────────────────────────────────────┤
│ project/                                                          │
│ ├── src/                    # Source code                           │
│ ├── tests/                  # Tests                                │
│ ├── examples/               # Usage examples                        │
│ ├── benches/                # Benchmarks                           │
│ └── Cargo.toml              # Manifest                             │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│ WEB SERVICE (Monolith)                                             │
├────────────────────────────────────────────────────────────────────┤
│ project/                                                          │
│ ├── src/                                                          │
│ │   ├── domain/            # Entities, value objects, services    │
│ │   ├── application/      # Use cases, handlers                  │
│ │   ├── infrastructure/   # DB, external services               │
│ │   └── interface/        # Controllers, routes                   │
│ ├── tests/                                                         │
│ └── Cargo.toml                                                     │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│ WEB SERVICE (Microservices)                                        │
├────────────────────────────────────────────────────────────────────┤
│ repo/                                                            │
│ ├── services/                                                     │
│ │   ├── user-service/                                            │
│ │   │   ├── src/                                                │
│ │   │   └── Dockerfile                                          │
│ │   ├── order-service/                                          │
│ │   │   ├── src/                                                │
│ │   │   └── Dockerfile                                          │
│ │   └── common/              # Shared libraries                  │
│ ├── api-gateway/                                                 │
│ └── docker-compose.yml                                            │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│ LIBRARY/SDK                                                       │
├────────────────────────────────────────────────────────────────────┤
│ library/                                                         │
│ ├── src/                    # Public API                           │
│ ├── src/private/           # Internal implementation              │
│ ├── benches/               # Benchmarks                           │
│ ├── examples/              # Examples                            │
│ └── Cargo.toml             # [lib] section                        │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│ MONOREPO                                                          │
├────────────────────────────────────────────────────────────────────┤
│ monorepo/                                                        │
│ ├── packages/                 # Publishable packages               │
│ │   ├── utils/                                                │
│ │   └── types/                                                │
│ ├── apps/                    # Applications                       │
│ │   ├── web/                                                  │
│ │   └── api/                                                  │
│ ├── tooling/                 # Build tools, generators            │
│ └── workspace.yaml           # Workspace manifest                  │
└────────────────────────────────────────────────────────────────────┘
```

---

## Integration Pattern Selection

```
┌────────────────────────────────────────────────────────────────────┐
│ HOW DO SERVICES COMMUNICATE?                                       │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│ SYNCHRONOUS (HTTP/gRPC)                                            │
│ ├─► When: Need immediate response                                 │
│ ├─► Pattern: Request/Response                                     │
│ └─► Consider: Circuit Breaker, Retry, Timeout                      │
│                                                                    │
│ ASYNCHRONOUS (Messaging)                                           │
│ ├─► When: Fire-and-forget, eventual consistency OK                │
│ ├─► Pattern: Pub/Sub, Point-to-Point                             │
│ └─► Consider: Outbox, Dead Letter Queue, Idempotency              │
│                                                                    │
│ EVENT-DRIVEN                                                      │
│ ├─► When: Decoupled, real-time reactions                         │
│ ├─► Pattern: Event Streaming, Event Sourcing                     │
│ └─► Consider: Saga, CQRS, Event Replay                           │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│ DATA CONSISTENCY                                                  │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│ STRONG CONSISTENCY (ACID)                                          │
│ └─► Single database, transactions                                 │
│                                                                    │
│ EVENTUAL CONSISTENCY                                              │
│ ├─► Event Sourcing                                               │
│ ├─► Saga (choreography or orchestration)                         │
│ └─► Outbox Pattern                                                │
│                                                                    │
│ READ YOUR OWN WRITES                                              │
│ ├─► Post to write DB, then read from it                          │
│ └─► Or: Redirect reads to write DB temporarily                    │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## Testing Strategy Selection

```
┌────────────────────────────────────────────────────────────────────┐
│ WHAT SHOULD YOU TEST?                                             │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│ UNIT TESTS                                                        │
│ ├─► Test: Domain logic, business rules                           │
│ ├─► Test: Pure functions, value objects                          │
│ └─► Framework: JUnit, pytest, Rust tests                         │
│                                                                    │
│ INTEGRATION TESTS                                                 │
│ ├─► Test: Repository implementations                             │
│ ├─► Test: External API clients                                   │
│ └─► Use: Testcontainers, mocking                                  │
│                                                                    │
│ CONTRACT TESTS                                                   │
│ ├─► Test: API compatibility between services                     │
│ └─► Framework: Pact, Spring Cloud Contract                        │
│                                                                    │
│ E2E TESTS                                                         │
│ ├─► Test: Critical user journeys                                 │
│ ├─► Test: Happy path + key error paths                           │
│ └─► Framework: Cypress, Playwright, Selenium                      │
│                                                                    │
│ PROPERTY-BASED TESTS                                              │
│ ├─► Test: Serialization/deserialization                         │
│ ├─► Test: Mathematical operations                                 │
│ └─► Framework: proptest, Hypothesis, QuickCheck                  │
│                                                                    │
│ MUTATION TESTS                                                   │
│ ├─► Test: Test effectiveness                                      │
│ └─► Tool: Stryker, PITest                                        │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│ TESTING PYRAMID (Target Ratios)                                   │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│                    ▲                                              │
│                   ╱ ╲                                             │
│                  ╱   ╲                                            │
│                 ╱ E2E ╲          10%                             │
│                ╱───────╲                                         │
│               ╱         ╲                                        │
│              ╱ Integration╲      30%                             │
│             ╱─────────────╲                                       │
│            ╱               ╲                                     │
│           ╱     Unit        ╲    60%                            │
│          ╱───────────────────╲                                   │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## Migration Path Recommendations

```
┌────────────────────────────────────────────────────────────────────┐
│ MIGRATION PATHS                                                    │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│ MONOLITH → MODULAR MONOLITH → MICROSERVICES                       │
│                                                                    │
│ Step 1: Establish module boundaries (DDD contexts)                 │
│ Step 2: Make modules independent deployable (still one repo)     │
│ Step 3: Extract modules to separate services                      │
│                                                                    │
│ LEGACY → CLEAN ARCHITECTURE                                       │
│                                                                    │
│ Step 1: Identify domain entities                                   │
│ Step 2: Extract business logic to domain layer                     │
│ Step 3: Create ports interfaces                                    │
│ Step 4: Migrate infrastructure to adapters                        │
│ Step 5: Remove direct infra dependencies from domain               │
│                                                                    │
│ MONOLITH → EVENT SOURCING                                         │
│                                                                    │
│ Step 1: Add event publishing to existing operations                │
│ Step 2: Create read models from events                            │
│ Step 3: Migrate writes to publish events first                    │
│ Step 4: Remove direct state writes                                │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## Anti-Patterns to Avoid

```
┌────────────────────────────────────────────────────────────────────┐
│ COMMON MISTAKES                                                   │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│ ✗ OVER-ENGINEERING                                                │
│   → Start simple, evolve when needed                             │
│   → YAGNI: You Aren't Gonna Need It                              │
│                                                                    │
│ ✗ CHOOSING MICROSERVICES FOR WRONG REASONS                        │
│   → Only if you need: independent deploy, scaling, different teams│
│   → If you don't have these needs, start with monolith            │
│                                                                    │
│ ✗ SKIPPING DOMAIN MODEL                                           │
│   → Don't start with database schema                              │
│   → Start with domain concepts and ubiquitous language            │
│                                                                    │
│ ✗ FORGETTING BOUNDED CONTEXTS                                     │
│   → Don't try to model everything as one big domain               │
│   → DDD shines when you have multiple bounded contexts            │
│                                                                    │
│ ✗ REINVENTING THE WHEEL                                          │
│   → Use existing patterns and libraries                          │
│   → Don't build what's already solved                             │
│                                                                    │
│ ✗ IGNORING TESTING                                                │
│   → TDD saves time in the long run                               │
│   → Tests are documentation and regression protection             │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## See Also

- [xDD Methodologies Encyclopedia](./xdd-methodologies-encyclopedia.md)
- [xDD Quick Reference Card](./xdd-quick-reference.md)
- [Clean Architecture Reference](./clean-architecture.md)
- [Hexagonal Architecture Reference](./hexagonal-architecture.md)
- [ADR Template](./adr-template.md)

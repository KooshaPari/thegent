# Architecture Enforcement Guide

## Overview

All Python projects in the portfolio use **import-linter** to enforce hexagonal architecture layer boundaries. This ensures domain logic stays pure, application logic doesn't depend on infrastructure, and dependencies always point inward.

## How It Works

### The Hexagonal Layers

```
+---------------------------------------------------+
|  infrastructure/   (outermost -- config, DI, boot) |
|  +-----------------------------------------------+ |
|  |  adapters/      (driving + driven)            | |
|  |  +-------------------------------------------+ | |
|  |  |  application/  (use cases, orchestration) | | |
|  |  |  +---------------------------------------+ | | |
|  |  |  |  domain/     (pure business logic)    | | | |
|  |  |  +---------------------------------------+ | | |
|  |  +-------------------------------------------+ | |
|  +-----------------------------------------------+ |
+---------------------------------------------------+
```

**Dependency rule**: Arrows point inward only. An inner layer NEVER imports from an outer layer.

| Layer | Can Import From | Cannot Import From |
|-------|----------------|-------------------|
| domain | stdlib, third-party only | application, adapters, infrastructure |
| application | domain | adapters, infrastructure |
| adapters | domain, application | infrastructure |
| infrastructure | domain, application, adapters | (unrestricted) |

### import-linter Configuration

Each project has an `.importlinter` file at its root defining three contracts:

1. **hexagonal-layers** (type: `layers`) -- Enforces the overall layer ordering
2. **domain-independence** (type: `forbidden`) -- Blocks domain from importing other layers
3. **application-no-adapters** (type: `forbidden`) -- Blocks application from importing adapters/infrastructure

### Running the Check

```bash
# From any project root:
task lint:architecture

# Or directly:
import-linter
```

### CI Integration

The `lint:architecture` task is included in the quality gate pipeline. It runs alongside lint, typecheck, and tests.

## Reading Violation Errors

When import-linter finds a violation, it prints output like:

```
=============
import-linter
=============

CONTRACTS

Hexagonal architecture layer enforcement     BROKEN
Domain layer must not import from other layers  BROKEN

Broken contracts
----------------

Hexagonal architecture layer enforcement
-----------------------------------------

thegent.domain.agents.base is not allowed to import thegent.adapters.driving.cli
- thegent.domain.agents.base -> thegent.adapters.driving.cli (l. 5)

Domain layer must not import from other layers
----------------------------------------------

thegent.domain.models -> thegent.infrastructure.config
- thegent.domain.models (l. 3): import thegent.infrastructure.config
```

### How to Read This

- **Contract name** tells you WHICH rule was broken
- **Module path** tells you WHERE the violation is (`thegent.domain.agents.base`)
- **Arrow** tells you the DIRECTION of the illegal import (`-> thegent.adapters.driving.cli`)
- **Line number** tells you EXACTLY where (`l. 5`)

## How to Fix Violations

### Pattern 1: Domain imports infrastructure (most common)

**Problem**: Domain code imports config, database, or API client directly.

```python
# domain/scoring.py -- VIOLATION
from job_hunter.infrastructure.config import Settings

class Scorer:
    def __init__(self):
        self.settings = Settings()  # domain depends on infrastructure!
```

**Fix**: Use dependency injection. Domain defines a Protocol, infrastructure provides the implementation.

```python
# domain/ports.py
from typing import Protocol

class ScoringConfig(Protocol):
    min_score: float
    weights: dict[str, float]

# domain/scoring.py -- CLEAN
from job_hunter.domain.ports import ScoringConfig

class Scorer:
    def __init__(self, config: ScoringConfig):
        self.config = config  # injected, no infrastructure import
```

### Pattern 2: Application imports adapters

**Problem**: Use case code imports a specific adapter implementation.

```python
# application/search_jobs.py -- VIOLATION
from job_hunter.adapters.driven.scrapers.linkedin import LinkedInScraper

class SearchJobsUseCase:
    def execute(self):
        scraper = LinkedInScraper()  # coupled to specific adapter!
```

**Fix**: Application depends on domain ports, not adapter implementations.

```python
# domain/ports.py
class JobSearcher(Protocol):
    def search(self, query: str) -> list[Job]: ...

# application/search_jobs.py -- CLEAN
from job_hunter.domain.ports import JobSearcher

class SearchJobsUseCase:
    def __init__(self, searcher: JobSearcher):
        self.searcher = searcher  # any implementation works
```

### Pattern 3: Circular layer dependency

**Problem**: Two modules in different layers import each other.

**Fix**: Extract the shared concept into the innermost layer that both depend on. Usually this means creating a Protocol in domain/ that both layers reference.

## Adding import-linter to a New Project

1. Create `.importlinter` at the project root:

```ini
[importlinter]
root_packages =
    your_package

[importlinter:contract:hexagonal-layers]
name = Hexagonal architecture layer enforcement
type = layers
layers =
    your_package.infrastructure
    your_package.adapters
    your_package.application
    your_package.domain

[importlinter:contract:domain-independence]
name = Domain layer must not import from other layers
type = forbidden
source_modules =
    your_package.domain
forbidden_modules =
    your_package.application
    your_package.adapters
    your_package.infrastructure

[importlinter:contract:application-no-adapters]
name = Application layer must not import from adapters or infrastructure
type = forbidden
source_modules =
    your_package.application
forbidden_modules =
    your_package.adapters
    your_package.infrastructure
```

2. Add `import-linter` to dev dependencies in `pyproject.toml`
3. Add `lint:architecture` task to `Taskfile.yml`
4. Create the layer directories with `__init__.py` files

## Coexistence with tach

Some projects (e.g. thegent) also use `tach` for module-level boundary enforcement. The two tools complement each other:

- **tach** enforces boundaries between specific modules (e.g., `agents` cannot import `contracts`)
- **import-linter** enforces layer-level boundaries (e.g., `domain` cannot import `adapters`)

Both can run in the same project. `tach` is more granular; import-linter is more structural.

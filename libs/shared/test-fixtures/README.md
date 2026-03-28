# Test Fixtures

Shared test fixtures for Phenotype ecosystem packages.

## Purpose

Provides common test utilities, mock implementations, and fixture builders that can be shared across all packages following hexagonal/clean architecture patterns.

## Structure

```
test-fixtures/
├── __init__.py
├── src/
│   ├── __init__.py
│   ├── mocks.py          # Mock implementations of ports
│   ├── fixtures.py       # Common test fixtures
│   └── builders.py       # Object builders for tests
├── README.md
└── pyproject.toml
```

## Usage

```python
from test_fixtures import MockPort, FixtureBuilder

# Use mock ports in unit tests
mock_repo = MockRepository()
mock_repo.add_result(some_entity)

# Use fixture builders
user = UserBuilder().with_name("test").build()
```

## Design Principles

- **Isolated**: Each mock is self-contained with no external dependencies
- **Configurable**: Fixtures support customization via builder pattern
- **Type-safe**: Use Python typing for clarity
- **Composable**: Easy to combine fixtures for complex scenarios

## For Package Authors

When writing tests in a package:

1. Import shared fixtures from `test-fixtures`
2. Extend `MockPort` for your specific port interfaces
3. Use `FixtureBuilder` base class for domain objects
4. Keep test logic in `tests/` directory, fixtures in `test_fixtures/`

## Status

**Phase 1**: Structure defined, basic implementations stubbed
**Phase 2**: Add comprehensive mock implementations
**Phase 3**: Add domain-specific builders
**Phase 4**: Add integration test helpers

## Related

- `libs/shared/hexagonal/` - Port interfaces to mock
- `libs/shared/events/` - Event bus for test assertions
- `libs/shared/metrics/` - Metrics collector mocks

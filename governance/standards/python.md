# Python Coding Standards

## Overview

This document defines coding standards for Python projects in the Phenotype ecosystem.

## Related xDD Methodologies

| Method | Application |
|--------|-------------|
| TDD | Write tests before implementation |
| Property-based Testing | Use Hypothesis for core logic |
| Contract Testing | Use pytest-contracts |
| BDD | Use pytest-bdd or behave |

## Project Structure

```
src/
├── domain/
│   ├── __init__.py
│   ├── entities/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── value_objects/
│   │   ├── __init__.py
│   │   └── email.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── user_service.py
│   └── errors.py
├── ports/
│   ├── __init__.py
│   ├── input/
│   │   ├── __init__.py
│   │   ├── commands.py
│   │   └── queries.py
│   └── output/
│       ├── __init__.py
│       └── repositories.py
├── adapters/
│   ├── __init__.py
│   ├── primary/
│   │   ├── __init__.py
│   │   ├── http/
│   │   │   ├── __init__.py
│   │   │   └── controllers.py
│   │   └── cli/
│   └── secondary/
│       ├── __init__.py
│       ├── postgres/
│       │   └── user_repository.py
│       └── redis/
│
└── application/
    ├── __init__.py
    └── services/
```

## Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Package | snake_case | `user_repository` |
| Module | snake_case | `user_repository` |
| Class | PascalCase | `UserRepository` |
| Function | snake_case | `get_user_by_id` |
| Variable | snake_case | `user_id` |
| Constant | SCREAMING_SNAKE_CASE | `MAX_RETRY_COUNT` |
| Private | leading underscore | `_private_method` |
| Protected | leading double underscore | `__protected_method` |
| Type variable | PascalCase | `T`, `UserT` |

## Code Style

### Ruff Configuration

```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
    "RUF",    # Ruff-specific rules
]
ignore = [
    "E501",   # line too long (handled by formatter)
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### Type Hints

```python
# Use type hints for all function signatures
from typing import Protocol, TypeVar, Generic
from dataclasses import dataclass

T = TypeVar("T")


# Good - explicit types
def get_user_by_id(user_id: str) -> User | None:
    ...


# Good - generic types
from collections.abc import Sequence


def get_users_by_ids(user_ids: Sequence[str]) -> list[User]:
    ...


# Good - protocol for interfaces
class UserRepository(Protocol):
    def save(self, user: User) -> None:
        ...

    def find_by_id(self, user_id: str) -> User | None:
        ...
```

### Error Handling

```python
# Custom exceptions
class DomainError(Exception):
    """Base exception for domain errors."""

    def __init__(self, message: str, code: str) -> None:
        super().__init__(message)
        self.code = code


class NotFoundError(DomainError):
    """Raised when an entity is not found."""

    def __init__(self, entity: str, entity_id: str) -> None:
        super().__init__(
            f"{entity} not found: {entity_id}",
            "NOT_FOUND"
        )


class ValidationError(DomainError):
    """Raised when validation fails."""

    def __init__(self, field: str, reason: str) -> None:
        super().__init__(
            f"Validation error for {field}: {reason}",
            "VALIDATION_ERROR"
        )


# Result pattern
from typing import TypeVar, Generic
from dataclasses import dataclass

T = TypeVar("T")
E = TypeVar("E", bound=Exception)


@dataclass
class Ok(Generic[T]):
    value: T


@dataclass
class Err(Generic[E]):
    error: E


Result = Ok[T] | Err[E]


def get_user(user_id: str) -> Result[User, DomainError]:
    ...
```

## Testing

### pytest Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short --strict-markers"
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow running tests",
]
filterwarnings = [
    "error",
    "ignore::UserWarning",
]
```

### Unit Tests

```python
# tests/domain/test_user.py
import pytest
from src.domain.entities.user import User, UserErrors


class TestUser:
    def test_create_valid_user(self) -> None:
        # Given
        email = "test@example.com"
        name = "Test User"

        # When
        result = User.create(email=email, name=name)

        # Then
        assert result.is_ok()
        user = result.unwrap()
        assert user.email.value == email
        assert user.name == name

    def test_create_invalid_email(self) -> None:
        # Given
        invalid_email = "not-an-email"

        # When
        result = User.create(email=invalid_email, name="Test")

        # Then
        assert result.is_err()
        assert isinstance(result.unwrap_err(), UserErrors.InvalidEmail)

    @pytest.mark.parametrize(
        "email,expected_valid",
        [
            ("test@example.com", True),
            ("user.name@domain.co.uk", True),
            ("invalid", False),
            ("@domain.com", False),
            ("user@", False),
        ],
    )
    def test_email_validation(
        self, email: str, expected_valid: bool
    ) -> None:
        result = User.create(email=email, name="Test")
        assert result.is_ok() == expected_valid
```

### Property-Based Tests (Hypothesis)

```python
# tests/domain/property_test_email.py
from hypothesis import given, settings
import hypothesis.strategies as st
from src.domain.value_objects.email import Email, EmailError


@given(emails=st.emails())
@settings(max_examples=100)
def test_email_parsing_valid_input(emails: str) -> None:
    """All valid email formats should parse successfully."""
    result = Email.create(emails)
    assert result.is_ok()


@given(emails=st.from_regex(r"^[a-z]+$", fullmatch=True))
@settings(max_examples=100)
def test_non_email_strings_rejected(emails: str) -> None:
    """Strings without @ should be rejected."""
    result = Email.create(emails)
    assert result.is_err()
```

### Test Coverage

| Type | Minimum Coverage |
|------|------------------|
| Domain | 100% |
| Application | 90% |
| Adapters | 80% |

## Documentation

### Docstrings (Google Style)

```python
def create_user(
    email: str,
    name: str,
    password: str,
) -> Result[User, DomainError]:
    """Create a new user account.

    Creates a new user with the provided email, name, and password.
    The email must be unique and valid format. The password must
    meet minimum security requirements.

    Args:
        email: The user's email address. Must be unique and valid.
        name: The user's display name. Must be 1-100 characters.
        password: The user's password. Must be at least 8 characters.

    Returns:
        Ok[User] if creation succeeded.
        Err[ValidationError] if validation failed.
        Err[DuplicateEmailError] if email already exists.

    Raises:
        None - All errors are returned in Result.

    Example:
        >>> result = create_user(
        ...     email="test@example.com",
        ...     name="Test User",
        ...     password="securepassword123"
        ... )
        >>> if result.is_ok():
        ...     print(f"Created user {result.value.id}")
    """
    ...
```

## Dependencies

### Dependency Rules

| Layer | Allowed Dependencies |
|-------|---------------------|
| Domain | Python stdlib only |
| Ports | Domain, typing |
| Application | Domain, Ports |
| Adapters | Ports, external libraries |

### pyproject.toml Structure

```toml
[project]
name = "hexagonal-py"
version = "1.0.0"
description = "Hexagonal architecture patterns for Python"
requires-python = ">=3.11"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=4.0",
    "pytest-asyncio>=0.23",
    "hypothesis>=6.0",
    "ruff>=0.3",
    "mypy>=1.8",
]
postgres = [
    "asyncpg>=0.29",
]
redis = [
    "redis>=5.0",
]
all = [
    "hexagonal-py[dev,postgres,redis]",
]
```

---

*Maintained by: Architecture Guild*

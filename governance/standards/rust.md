# Rust Coding Standards

## Overview

This document defines coding standards for Rust projects in the Phenotype ecosystem.

## Related xDD Methodologies

| Method | Application |
|--------|-------------|
| TDD | Write tests before implementation |
| Property-based Testing | Use proptest for core logic |
| Contract Testing | Use async-trait for async interfaces |
| BDD | Use rstest for behavior tests |

## Project Structure

```
src/
├── domain/           # Domain layer (zero external deps)
│   ├── mod.rs
│   ├── entities/
│   ├── value_objects/
│   ├── services/
│   ├── aggregates/
│   ├── events/
│   └── errors.rs
├── ports/           # Port interfaces
│   ├── mod.rs
│   ├── input/
│   └── output/
├── adapters/        # Adapter implementations
│   ├── primary/
│   └── secondary/
├── application/     # Application services
└── lib.rs

tests/              # Integration tests
benches/            # Benchmarks
examples/           # Usage examples
```

## Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Crate | kebab-case | `hexagonal-rs` |
| Module | snake_case | `user_repository` |
| Struct | PascalCase | `UserAccount` |
| Enum | PascalCase | `UserStatus` |
| Trait | PascalCase | `UserRepository` |
| Function | snake_case | `get_user_by_id` |
| Variable | snake_case | `user_id` |
| Constant | SCREAMING_SNAKE_CASE | `MAX_RETRY_COUNT` |
| Type parameter | PascalCase | `T`, `E`, `Result` |

## Code Style

### Formatting

Use `rustfmt` with default settings:

```toml
# rustfmt.toml
edition = "2021"
max_width = 100
tab_spaces = 4
```

### Imports

```rust
// Order: std → external → internal
use std::collections::HashMap;

use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::domain::entities::User;
use crate::ports::output::UserRepository;
```

### Error Handling

```rust
// Use thiserror for domain errors
#[derive(Error, Debug)]
pub enum DomainError {
    #[error("Entity not found: {id}")]
    NotFound { id: String },

    #[error("Invalid value for {field}: {reason}")]
    ValidationError { field: String, reason: String },
}

// Use anyhow for application errors
#[derive(Error, Debug)]
pub enum ApplicationError {
    #[error("Database error: {0}")]
    Database(#[from] sqlx::Error),

    #[error("Domain error: {0}")]
    Domain(#[from] DomainError),
}
```

### Async/Await

```rust
// Use async-trait for async trait methods
#[async_trait]
pub trait UserRepository: Send + Sync {
    async fn save(&self, user: User) -> Result<(), RepositoryError>;
    async fn find_by_id(&self, id: Uuid) -> Result<Option<User>, RepositoryError>;
}
```

## Linting

### Required Lints

Add to `lib.rs`:

```rust
#![deny(
    clippy::all,
    clippy::unwrap_used,
    clippy::expect_used,
    clippy::panic,
    rust_2018_idioms,
)]
#![warn(
    clippy::todo,
    clippy::unimplemented,
    missing_docs,
)]
```

### Clippy Rules

```toml
# .cargo/config.toml or clippy.toml
[lints.clippy]
unwrap_used = "deny"
expect_used = "deny"
panic = "deny"
todo = "warn"
unimplemented = "warn"
doc_markdown = "warn"
missing_errors_doc = "warn"
missing_panics_doc = "warn"
```

## Testing

### Unit Tests

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn user_account_creation_valid() {
        // Given
        let email = "test@example.com".parse().unwrap();

        // When
        let user = User::new(email.clone(), "Test User".to_string());

        // Then
        assert!(user.is_ok());
    }

    #[test]
    fn user_account_creation_invalid_email() {
        // Given
        let invalid_email = "not-an-email";

        // When
        let result: Result<User, _> = User::new(
            invalid_email.parse().unwrap(),
            "Test User".to_string(),
        );

        // Then
        assert!(result.is_err());
    }
}
```

### Property-Based Tests (proptest)

```rust
#[cfg(test)]
mod property_tests {
    use proptest::prelude::*;

    proptest! {
        #[test]
        fn email_parsing_preserves_valid_input(email in r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$") {
            let parsed: Result<Email, _> = email.parse();
            prop_assert!(parsed.is_ok());
        }
    }
}
```

### Test Coverage

| Type | Minimum Coverage |
|------|------------------|
| Domain | 100% |
| Ports | 100% |
| Adapters | 80% |
| Application | 90% |

## Documentation

### Required Documentation

Every public item MUST have doc comments:

```rust
/// Creates a new user account.
///
/// # Errors
///
/// Returns [`DomainError::ValidationError`] if the email is invalid
/// or the name is empty.
///
/// # Examples
///
/// ```
/// use domain::entities::User;
///
/// let email: Email = "test@example.com".parse().unwrap();
/// let user = User::new(email, "Test User".to_string());
/// ```
pub fn new(email: Email, name: String) -> Result<Self, DomainError> {
    // ...
}
```

## Dependencies

### Dependency Rules

| Layer | Allowed Dependencies |
|-------|---------------------|
| Domain | `std`, `thiserror`, `serde` (optional) |
| Ports | Domain, `async-trait` |
| Adapters | Ports, External libraries |
| Application | Ports, Domain |

### Workspace Dependencies

```toml
# Workspace Cargo.toml
[workspace.dependencies]
thiserror = "2"
anyhow = "1"
serde = { version = "1", features = ["derive"] }
async-trait = "0.1"

# Use in crate Cargo.toml
[dependencies]
thiserror.workspace = true
anyhow.workspace = true
```

## Feature Flags

```rust
// Use feature flags for optional dependencies
[features]
default = []
async = ["tokio", "async-trait"]
serde = ["dep:serde"]

[dependencies]
serde = { version = "1", optional = true }
tokio = { version = "1", optional = true }
async-trait = { version = "0.1", optional = true }
```

---

*Maintained by: Architecture Guild*

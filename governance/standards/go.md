# Go Coding Standards

## Overview

This document defines coding standards for Go projects in the Phenotype ecosystem.

## Related xDD Methodologies

| Method | Application |
|--------|-------------|
| TDD | Write tests before implementation |
| Property-based Testing | Use go-quickcheck for core logic |
| Contract Testing | Use testify for assertions |
| BDD | Use godog or testify for BDD tests |

## Project Structure

```
{module-name}/
├── internal/
│   ├── domain/
│   │   ├── entities/
│   │   ├── value_objects/
│   │   ├── services/
│   │   └── errors.go
│   ├── ports/
│   │   ├── input/
│   │   └── output/
│   ├── adapters/
│   │   ├── primary/
│   │   │   ├── http/
│   │   │   └── grpc/
│   │   └── secondary/
│   │       ├── postgres/
│   │       ├── redis/
│   │       └── http/
│   └── application/
│       └── services/
├── pkg/                  # Public packages (if any)
├── api/                  # API definitions (proto, openapi)
├── cmd/                  # Command-line applications
│   └── server/
│       └── main.go
├── migrations/           # Database migrations
├── scripts/              # Build scripts
├── docs/                 # Documentation
└── go.mod
```

## Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Module | `github.com/org/{name}` | `github.com/phenotype/hexagonal-go` |
| Package | snake_case | `user_repository` |
| Type/Interface | PascalCase | `UserRepository`, `Service` |
| Function (exported) | PascalCase | `GetUserByID` |
| Function (unexported) | camelCase | `getUserByID` |
| Variable (exported) | PascalCase | `MaxRetries` |
| Variable (unexported) | camelCase | `maxRetries` |
| Constant (exported) | PascalCase | `MaxRetries` |
| Constant (unexported) | camelCase | `maxRetries` |
| Error variable | PascalCase + Err prefix | `ErrUserNotFound` |
| Interface name | PascalCase + er suffix | `Repository`, `Service` |

## Code Style

### Formatting

Use `gofmt` with `goimports`:

```bash
go install golang.org/x/tools/cmd/goimports@latest
```

### Error Handling

```go
// Custom errors
var (
    ErrUserNotFound     = errors.New("user not found")
    ErrInvalidEmail     = errors.New("invalid email format")
    ErrUnauthorized     = errors.New("unauthorized")
)

// Wrapped errors
if err != nil {
    return fmt.Errorf("failed to get user %s: %w", id, err)
}

// Sentinel errors for API
type DomainError struct {
    Code    string
    Message string
    Err     error
}

func (e *DomainError) Error() string {
    return e.Message
}

func (e *DomainError) Unwrap() error {
    return e.Err
}
```

### Context Usage

```go
// Always pass context as first parameter
func (s *UserService) GetUser(ctx context.Context, id string) (*User, error) {
    // ...
}

// Use context for cancellation and timeouts
func (s *UserService) GetUserWithTimeout(ctx context.Context, id string, timeout time.Duration) (*User, error) {
    ctx, cancel := context.WithTimeout(ctx, timeout)
    defer cancel()
    return s.GetUser(ctx, id)
}
```

### Interfaces

```go
// Define interfaces where they're used (consumer)
// Avoid defining interfaces in the package that implements them

// internal/ports/output/user_repository.go
type UserRepository interface {
    Save(ctx context.Context, user *User) error
    FindByID(ctx context.Context, id string) (*User, error)
    Delete(ctx context.Context, id string) error
}

// internal/adapters/secondary/postgres/user_repository.go
type PostgresUserRepository struct {
    db *sqlx.DB
}

func (r *PostgresUserRepository) Save(ctx context.Context, user *User) error {
    // implementation
}
```

## Linting

### golangci-lint Configuration

```yaml
# .golangci.yml
run:
  timeout: 5m
  modules-download-mode: readonly

linters:
  enable:
    - errcheck
    - gosimple
    - govet
    - ineffassign
    - staticcheck
    - typecheck
    - unused
    - gosec
    - prealloc
    - unconvert

linters-settings:
  errcheck:
    check-type-assertions: true
    check-blank: true
  gosec:
    excludes:
      - G104
  govet:
    enable-all: true
```

### Required Linters

| Linter | Why Required |
|--------|--------------|
| `errcheck` | Check error handling |
| `govet` | Check for suspicious code |
| `ineffassign` | Find ineffective assignments |
| `staticcheck` | Static analysis |
| `unused` | Find unused code |

## Testing

### Unit Tests

```go
// internal/domain/user_test.go
package domain

import (
    "testing"
)

func TestUser_New(t *testing.T) {
    tests := []struct {
        name    string
        email   string
        wantErr bool
    }{
        {
            name:    "valid email",
            email:   "test@example.com",
            wantErr: false,
        },
        {
            name:    "invalid email",
            email:   "not-an-email",
            wantErr: true,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            _, err := NewUser(tt.email, "Test User")
            if (err != nil) != tt.wantErr {
                t.Errorf("NewUser() error = %v, wantErr %v", err, tt.wantErr)
            }
        })
    }
}
```

### Table-Driven Tests

```go
func TestEmail_Parse(t *testing.T) {
    tests := []struct {
        name    string
        input   string
        want    Email
        wantErr bool
    }{
        {"valid", "test@example.com", Email{value: "test@example.com"}, false},
        {"invalid no @", "testexample.com", Email{}, true},
        {"invalid no domain", "test@", Email{}, true},
        {"empty", "", Email{}, true},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := ParseEmail(tt.input)
            if (err != nil) != tt.wantErr {
                t.Errorf("ParseEmail() error = %v, wantErr %v", err, tt.wantErr)
                return
            }
            if !tt.wantErr && got != tt.want {
                t.Errorf("ParseEmail() = %v, want %v", got, tt.want)
            }
        })
    }
}
```

### Mock Generation

```bash
# Install mockgen
go install github.com/golang/mock/mockgen@latest

# Generate mocks
mockgen -source=internal/ports/output/user_repository.go \
        -destination=internal/mocks/user_repository_mock.go \
        -package=mocks
```

### Test Coverage

| Type | Minimum Coverage |
|------|------------------|
| Domain | 100% |
| Application | 90% |
| Adapters | 80% |

## Documentation

### Required Documentation

Every exported function MUST have doc comments:

```go
// GetUserByID retrieves a user by their unique identifier.
//
// Returns ErrUserNotFound if the user does not exist.
// The context is used for cancellation and timeouts.
//
// Example:
//
//	ctx := context.Background()
//	user, err := svc.GetUserByID(ctx, "user-123")
func (s *UserService) GetUserByID(ctx context.Context, id string) (*User, error) {
    // ...
}
```

### godoc

```bash
# Generate godoc
go install golang.org/x/tools/cmd/godoc@latest
godoc -http=:8080
```

## Dependencies

### Dependency Rules

```
internal/domain       → stdlib only
internal/ports       → domain, stdlib
internal/application → domain, ports, stdlib
internal/adapters    → ports, external libraries
```

### go.mod Structure

```go
module github.com/phenotype/hexagonal-go

go 1.24

require (
    github.com/jmoiron/sqlx v1.3.5
    github.com/rs/zerolog v1.30.0
)

require (
    // indirect dependencies
)
```

---

*Maintained by: Architecture Guild*

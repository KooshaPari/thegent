# Authentication & Credential Management Consolidation Plan

## Overview

This document outlines the consolidation of BytePort's authentication and credential management systems to use modern, standardized approaches with WorkOS AuthKit and official SDKs.

## Current State Analysis

### Duplicate Authentication Systems
1. **Legacy PASETO System** (`lib/auth.go`):
   - Custom token generation with keyring storage
   - Manual JWT validation and user lookup
   - Cookie-based middleware

2. **Infrastructure Middleware** (`internal/infrastructure/http/middleware/auth.go`):
   - Placeholder token validation
   - Header-based authentication
   - Duplicate logic with different implementation

3. **WorkOS Integration** (`auth_handlers.go`):
   - Partial WorkOS implementation
   - Mixed with legacy token system

### Manual Credential Management
1. **Manual HTTP Clients** (`lib/apilink.go`):
   - Custom HTTP validation for OpenAI, AWS, Portfolio APIs
   - No use of official SDKs
   - Basic error handling

2. **Keyring Dependencies**:
   - Local keyring storage for secrets
   - Not suitable for production deployment
   - Platform-dependent

## Target Architecture

### 1. Unified Authentication with WorkOS AuthKit

```go
// New authentication flow
WorkOS AuthKit → JWT Token → Middleware Validation → User Context
```

**Benefits:**
- Single source of truth for authentication
- Professional SSO/OAuth support
- Reduced maintenance burden
- Better security practices

### 2. Secrets Management Broker

```go
// New secrets management
Secrets Broker → Multiple Providers (Env, AWS Secrets Manager, etc.)
```

**Benefits:**
- Centralized secret management
- Support for multiple backends
- Caching and rotation support
- Production-ready deployment

### 3. Official SDK Integration

```go
// Replace manual HTTP clients
OpenAI SDK, AWS SDK v2, Custom Portfolio Client
```

**Benefits:**
- Better error handling
- Automatic retries and timeouts
- Type-safe APIs
- Official support and updates

## Migration Steps

### Phase 1: Setup New Infrastructure ✅
- [x] Create secrets management broker (`internal/infrastructure/secrets/`)
- [x] Create WorkOS authentication service (`internal/infrastructure/auth/`)
- [x] Create modern credential validator (`internal/infrastructure/clients/`)

### Phase 2: Update Dependencies

```bash
# Add new dependencies
go get github.com/workos/workos-go/v4
go get github.com/sashabaranov/go-openai
go get github.com/aws/aws-sdk-go-v2/config
go get github.com/aws/aws-sdk-go-v2/credentials
go get github.com/aws/aws-sdk-go-v2/service/s3

# Remove old dependencies (after migration)
go mod tidy  # This will remove unused dependencies like go-keyring and PASETO
```

### Phase 3: Update User Model

**Before:**
```go
type User struct {
    UUID     string `json:"uuid" gorm:"primaryKey"`
    Name     string `json:"name"`
    Email    string `json:"email" gorm:"unique"`
    Password string `json:"-"`  // Remove this
    // ... AWS credentials, API keys stored in user model
}
```

**After:**
```go
type User struct {
    UUID        string `json:"uuid" gorm:"primaryKey"`
    WorkOSID    string `json:"workos_id" gorm:"unique"` // WorkOS user ID
    Name        string `json:"name"`
    Email       string `json:"email" gorm:"unique"`
    // Credentials moved to secrets management
}
```

### Phase 4: Replace Authentication Middleware

**Replace:**
- `lib/auth.go` → Remove entirely
- `internal/infrastructure/http/middleware/auth.go` → Use WorkOS service

**New Implementation:**
```go
// In main server setup
secretsBroker := secrets.NewBroker(secrets.BrokerConfig{})
secretsBroker.RegisterProvider("env", secrets.NewEnvironmentProvider())

workosAuth := auth.NewWorkOSAuthService(secretsBroker)
workosAuth.Initialize(ctx)

// Use in routes
router.Use(workosAuth.Middleware())         // Required auth
router.Use(workosAuth.OptionalMiddleware()) // Optional auth
```

### Phase 5: Replace Credential Validation

**Replace:**
- `lib/apilink.go` → Use new credential validator

**New Implementation:**
```go
validator := clients.NewCredentialValidator()

// Validate with official SDKs
err := validator.ValidateOpenAICredentials(ctx, apiKey)
err := validator.ValidateAWSCredentials(ctx, accessKey, secretKey, region)
err := validator.ValidatePortfolioAPI(ctx, endpoint, apiKey)
```

### Phase 6: Update Database Schema

```sql
-- Migration script
ALTER TABLE users ADD COLUMN workos_id VARCHAR(255) UNIQUE;
ALTER TABLE users DROP COLUMN password;
ALTER TABLE users DROP COLUMN aws_access_key_id;
ALTER TABLE users DROP COLUMN aws_secret_access_key;
-- Move API keys to secrets management
```

### Phase 7: Update Routes and Handlers

**Before:**
```go
func handleLogin(c *gin.Context) {
    // Custom password validation
    user := authenticateUser(email, password)
    token := generateCustomToken(user)
}
```

**After:**
```go
func handleWorkOSCallback(c *gin.Context) {
    // WorkOS handles authentication
    tokenResp := workosAuth.ExchangeCodeForToken(ctx, code)
    userInfo := workosAuth.ValidateToken(ctx, tokenResp.AccessToken)
}
```

### Phase 8: Environment Configuration

**New Environment Variables:**
```bash
# WorkOS Configuration
WORKOS_CLIENT_ID=your_client_id
WORKOS_CLIENT_SECRET=your_client_secret  
WORKOS_API_KEY=your_api_key

# API Keys (moved from database)
OPENAI_API_KEY=your_openai_key
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
PORTFOLIO_API_KEY=your_portfolio_key
PORTFOLIO_ROOT_ENDPOINT=https://api.portfolio.example.com
```

**Remove:**
```bash
# No longer needed
SERVICE_KEY=...
ENCRYPTION_KEY=...
# Individual user credentials moved to secrets management
```

## Cleanup Phase

### Files to Remove:
- `lib/auth.go` (replace with WorkOS service)
- `lib/auth_test.go`
- `lib/apilink.go` (replace with credential validator)
- `lib/apilink_test.go`
- `lib/crypto.go` (password hashing no longer needed)
- `lib/crypto_test.go`
- `internal/infrastructure/http/middleware/auth.go` (replace with WorkOS middleware)

### Dependencies to Remove:
- `aidanwoods.dev/go-paseto` (custom token system)
- `github.com/zalando/go-keyring` (local keyring storage)
- `golang.org/x/crypto/argon2` (password hashing)
- Old AWS SDK v1 dependencies

### Database Cleanup:
- Remove password-related columns
- Remove user-specific API key columns
- Add WorkOS ID mapping

## Benefits of Consolidation

### Security Improvements
- Professional authentication provider (WorkOS)
- No local password storage
- Centralized credential management
- Proper secret rotation capabilities

### Code Quality
- Single authentication system
- Official SDK usage
- Better error handling
- Reduced code duplication

### Operational Benefits
- Easier deployment (no keyring dependencies)
- Better monitoring and logging
- Support for multiple secret backends
- Production-ready configuration

### Developer Experience
- Clearer authentication flow
- Type-safe API clients
- Better documentation
- Easier testing

## Testing Strategy

1. **Unit Tests**: Test new services in isolation
2. **Integration Tests**: Test WorkOS flow end-to-end
3. **Migration Tests**: Verify data migration scripts
4. **Backward Compatibility**: Ensure gradual migration is possible

## Rollback Plan

1. Keep old authentication code temporarily
2. Feature flags for new vs old auth
3. Database migrations are reversible
4. Environment variables remain compatible

## Timeline

- **Phase 1**: ✅ Complete (Infrastructure setup)
- **Phase 2**: 1 day (Dependencies)
- **Phase 3**: 1 day (User model update)
- **Phase 4**: 2 days (Middleware replacement)
- **Phase 5**: 1 day (Credential validation)
- **Phase 6**: 1 day (Database migration)
- **Phase 7**: 2 days (Route updates)
- **Phase 8**: 1 day (Configuration)
- **Cleanup**: 1 day (Remove old code)

**Total Estimated Time**: 10 days

## Next Steps

1. Review and approve this plan
2. Create feature branch for consolidation
3. Begin Phase 2 (dependency updates)
4. Test each phase thoroughly before proceeding
5. Document new authentication flow for team
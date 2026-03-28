# Byteport — Architecture Decision Records

---

## ADR-001: Go + GORM for Backend

**Status:** Accepted
**Date:** 2024-12

### Context

Byteport needs a backend that can handle concurrent deployment jobs, long-running provider API calls, and real-time log streaming. The initial prototype used Python but showed performance and concurrency limitations.

### Decision

Use Go with the Gin HTTP framework and GORM ORM for all backend services.

### Rationale

- Go's goroutine model handles concurrent deployment jobs (one per provider call) without thread-pool exhaustion.
- Gin is lightweight, high-performance, and battle-tested for REST APIs.
- GORM provides a productive ORM layer with migration support without requiring raw SQL for standard CRUD.
- Go's static binary simplifies Docker image builds (multi-stage, minimal final image).
- Strong type system catches credential struct mismatches at compile time.

### Alternatives Considered

- **Node.js (Express/Fastify):** Strong async ecosystem but weaker type safety for credential models; team preference for Go.
- **Python (FastAPI):** Already proven inadequate in prototype phase for concurrent jobs.
- **Rust (Axum):** Superior performance but higher implementation cost for CRUD-heavy credential management.

### Consequences

- All new backend features written in Go.
- GORM migrations run on application startup.
- Provider integrations implemented as Go packages under `backend/api/services/`.

---

## ADR-002: Multi-Provider Credential Storage in User Model (Embedded Structs)

**Status:** Accepted
**Date:** 2024-12

### Context

Byteport supports 8+ cloud providers, each with different credential shapes (token, key+secret, JSON blob, etc.). A schema must store these without a separate credentials table per provider.

### Decision

Store all provider credentials as embedded structs on the `User` GORM model, serialized as JSONB columns in PostgreSQL.

### Rationale

- Provider credential sets are user-scoped; embedding avoids complex joins.
- JSONB provides flexible schema evolution (new fields without migrations).
- Embedded structs in Go enforce compile-time field presence.
- Encryption applied at the model layer before persistence (single intercept point).

### Alternatives Considered

- **Separate table per provider:** Explosive table count; cross-provider queries require many joins.
- **Key-value store (Redis):** No relational integrity; harder to audit credential access.
- **Vault (HashiCorp):** Operational overhead not justified for single-user MVP.

### Consequences

- User model grows with each new provider — acceptable for current provider count.
- Adding a provider requires: Go struct field, GORM serializer, UI form, and service integration.
- Credential migration (schema changes) handled via GORM `AutoMigrate`.

---

## ADR-003: WorkOS AuthKit for Authentication

**Status:** Accepted
**Date:** 2025-01

### Context

Byteport initially used a custom JWT auth implementation. Maintenance burden and security surface area were unacceptable for a platform handling cloud credentials.

### Decision

Migrate to WorkOS AuthKit for all authentication flows (email/password, SSO, session management).

### Rationale

- WorkOS AuthKit provides production-grade auth with minimal integration code.
- Built-in SSO support (Google, GitHub, Microsoft) without per-provider OAuth implementation.
- Session management, token refresh, and device tracking are handled by WorkOS.
- Compliance features (audit log, MFA) available as the product scales.
- Frontend SDK (`@workos-inc/authkit-nextjs`) integrates directly with Next.js App Router middleware.

### Alternatives Considered

- **Auth0:** More expensive at scale; heavier SDK footprint.
- **Clerk:** Strong DX but less control over session storage.
- **NextAuth.js (custom):** Full control but re-implements security-critical code.
- **Custom JWT:** Already proven insufficient — this is the migration target.

### Consequences

- All authentication routes delegate to WorkOS.
- Backend validates WorkOS session tokens on each request.
- User records in Byteport DB linked to WorkOS user ID (`workos_id` foreign key).

---

## ADR-004: Next.js 15 + shadcn/ui for Frontend

**Status:** Accepted
**Date:** 2025-01

### Context

Byteport dashboard requires a modern, real-time UI with complex forms (credential management), data tables (deployment lists), and live log streaming. The previous frontend used plain React without a component system.

### Decision

Use Next.js 15 (App Router) with shadcn/ui components and Tailwind CSS v4.

### Rationale

- Next.js 15 App Router enables server components for initial page loads (faster TTI) and client components for interactive deployment forms.
- shadcn/ui provides unstyled, accessible Radix UI components with Tailwind integration — fully owned, not a black-box library.
- Tailwind CSS v4's JIT engine eliminates unused CSS; new cascade layers simplify theming.
- The combination is the current industry standard for production Next.js apps (2025).
- Dark mode first is trivially supported via Tailwind's `dark:` variant.

### Alternatives Considered

- **Remix + shadcn:** Strong alternative; rejected due to team familiarity with Next.js.
- **SvelteKit + shadcn-svelte:** Smaller ecosystem for UI component libraries.
- **Plain React SPA (Vite):** Loses SSR benefits for SEO and initial load.

### Consequences

- Frontend lives in `frontend/web-next/` (Next.js 15 App Router).
- All new UI components must use shadcn/ui primitives or Radix UI directly.
- No plain HTML forms — all forms use shadcn `Form` + `react-hook-form` + `zod`.
- pnpm is the required package manager for the frontend.

---

## ADR-005: Provider Integration Architecture (Service Layer Pattern)

**Status:** Accepted
**Date:** 2025-02

### Context

Each cloud provider has a different API, authentication mechanism, and deployment model. A consistent integration pattern prevents drift and eases onboarding of new providers.

### Decision

Each provider is implemented as a Go package under `backend/api/services/<provider>/` implementing a common `DeploymentProvider` interface.

### Interface (conceptual)

```
type DeploymentProvider interface {
    Deploy(ctx, project, credentials) (DeploymentResult, error)
    Status(ctx, deploymentID, credentials) (DeploymentStatus, error)
    Delete(ctx, deploymentID, credentials) error
    Logs(ctx, deploymentID, credentials) (io.Reader, error)
}
```

### Rationale

- Interface enforces consistent contract across all providers.
- New providers added without modifying existing handler code (open/closed principle).
- Per-package isolation enables independent testing with provider-specific mocks.

### Consequences

- All provider integrations must implement the `DeploymentProvider` interface.
- Provider selection at runtime based on `deployment.Provider` field.
- Integration tests use provider sandbox/test accounts or recorded HTTP fixtures.

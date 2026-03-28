# Byteport — Phased WBS with DAG Dependencies

## Legend

- Status: COMPLETE | IN PROGRESS | PLANNED
- Predecessors: Task IDs that must complete first

---

## Phase 1: Auth Migration (WorkOS) — COMPLETE

| Task ID | Description | Predecessor | Status |
|---------|-------------|-------------|--------|
| P1.1 | Remove custom JWT auth implementation | — | COMPLETE |
| P1.2 | Install WorkOS AuthKit SDK (Go backend) | P1.1 | COMPLETE |
| P1.3 | Install `@workos-inc/authkit-nextjs` frontend SDK | P1.1 | COMPLETE |
| P1.4 | Implement WorkOS session validation middleware (Go) | P1.2 | COMPLETE |
| P1.5 | Implement Next.js middleware for protected routes | P1.3 | COMPLETE |
| P1.6 | Add `workos_id` field to User model + migration | P1.4 | COMPLETE |
| P1.7 | Implement sign-in, sign-up, and sign-out routes | P1.4, P1.5 | COMPLETE |
| P1.8 | Implement session token refresh logic | P1.7 | COMPLETE |
| P1.9 | Auth integration tests (5 FR-AUTH-* cases) | P1.7, P1.8 | COMPLETE |

---

## Phase 2: Multi-Provider Credential UI — COMPLETE

| Task ID | Description | Predecessor | Status |
|---------|-------------|-------------|--------|
| P2.1 | Define credential embedded structs in User model (Go) | P1.6 | COMPLETE |
| P2.2 | Add encryption layer for credential fields | P2.1 | COMPLETE |
| P2.3 | CRUD API endpoints for credentials (GET/POST/DELETE per provider) | P2.2 | COMPLETE |
| P2.4 | Credential settings page (shadcn Form + react-hook-form + zod) | P2.3 | COMPLETE |
| P2.5 | Per-provider credential form components (Vercel, Netlify, Railway, Fly.io, Supabase) | P2.4 | COMPLETE |
| P2.6 | Credential validation tests (FR-CRED-001 to FR-CRED-005) | P2.3 | COMPLETE |

---

## Phase 3: Backend Service Integrations — IN PROGRESS

| Task ID | Description | Predecessor | Status |
|---------|-------------|-------------|--------|
| P3.1 | Define `DeploymentProvider` interface (Go) | P2.3 | COMPLETE |
| P3.2 | Vercel provider integration (deploy, status, delete, logs) | P3.1 | COMPLETE |
| P3.3 | Netlify provider integration | P3.1 | COMPLETE |
| P3.4 | Railway provider integration | P3.1 | COMPLETE |
| P3.5 | Fly.io provider integration | P3.1 | COMPLETE |
| P3.6 | Supabase provider integration | P3.1 | COMPLETE |
| P3.7 | AWS provider integration (Elastic Beanstalk / Lambda) | P3.1 | IN PROGRESS |
| P3.8 | GCP provider integration (Cloud Run) | P3.1 | IN PROGRESS |
| P3.9 | Azure provider integration (App Service) | P3.1 | PLANNED |
| P3.10 | Framework auto-detection service (20+ frameworks) | P3.1 | COMPLETE |
| P3.11 | Buildpack selection engine | P3.10 | COMPLETE |
| P3.12 | Real-time log streaming (SSE or WebSocket) | P3.2, P3.3, P3.4, P3.5 | IN PROGRESS |
| P3.13 | Deployment status polling service | P3.2 through P3.6 | COMPLETE |
| P3.14 | Integration tests for all providers (FR-DEPLOY-001 to FR-DEPLOY-015) | P3.2 through P3.11 | IN PROGRESS |

---

## Phase 4: Project Deployment Workflows — PLANNED

| Task ID | Description | Predecessor | Status |
|---------|-------------|-------------|--------|
| P4.1 | Project CRUD API (create, list, get, update, delete) | P3.1 | PLANNED |
| P4.2 | Project database model + migrations | P4.1 | PLANNED |
| P4.3 | Environment variable storage per project (encrypted) | P4.2 | PLANNED |
| P4.4 | Projects list page (shadcn DataTable) | P4.1 | PLANNED |
| P4.5 | Project detail page (deployments, env vars, provider config) | P4.4 | PLANNED |
| P4.6 | One-click deploy from project UI | P4.5, P3.13 | PLANNED |
| P4.7 | GitHub repo linking (OAuth + webhook) | P4.2 | PLANNED |
| P4.8 | Auto-deploy on push (webhook handler) | P4.7 | PLANNED |
| P4.9 | Self-hosted SSH deployment target support | P3.1 | PLANNED |
| P4.10 | Project management tests (FR-PROJ-001 to FR-PROJ-008) | P4.1 through P4.6 | PLANNED |

---

## Phase 5: LLM Integration — PLANNED

| Task ID | Description | Predecessor | Status |
|---------|-------------|-------------|--------|
| P5.1 | LLM configuration model (OpenAI, Anthropic, vLLM, MLX) | P4.2 | PLANNED |
| P5.2 | LLM credential storage (encrypted, per user) | P5.1 | PLANNED |
| P5.3 | LLM health check endpoint | P5.2 | PLANNED |
| P5.4 | LLM settings UI (shadcn Form, model selector) | P5.2 | PLANNED |
| P5.5 | Provider suggestion service (analyze project -> recommend provider) | P5.2, P3.10 | PLANNED |
| P5.6 | LLM integration tests (FR-LLM-001 to FR-LLM-005) | P5.2 through P5.5 | PLANNED |

---

## DAG Summary

```
P1.1 -> P1.2 -> P1.4 -> P1.7 -> P1.9
P1.1 -> P1.3 -> P1.5 -> P1.7
P1.4 -> P1.6 -> P2.1 -> P2.2 -> P2.3 -> P3.1 -> P3.2..P3.9
                                          P3.1 -> P3.10 -> P3.11
P3.13 -> P4.1 -> P4.2 -> P4.3
                P4.2 -> P5.1 -> P5.2 -> P5.5
P3.10 -> P5.5
```

---

## Phase Completion Summary

| Phase | Status | Completion % |
|-------|--------|-------------|
| Phase 1: Auth Migration | COMPLETE | 100% |
| Phase 2: Credential UI | COMPLETE | 100% |
| Phase 3: Backend Integrations | IN PROGRESS | ~70% |
| Phase 4: Project Workflows | PLANNED | 0% |
| Phase 5: LLM Integration | PLANNED | 0% |

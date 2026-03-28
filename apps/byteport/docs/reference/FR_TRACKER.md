# Byteport — Functional Requirements Tracker

Last updated: 2026-03-28

## FR-AUTH: Authentication

| FR ID | Description | Priority | Status | Test File | Notes |
|-------|-------------|----------|--------|-----------|-------|
| FR-AUTH-001 | Authenticate via WorkOS email/password | P0 | Done | `backend/api/handlers/auth_test.go` | |
| FR-AUTH-002 | Authenticate via OAuth SSO (Google, GitHub) | P0 | Done | `backend/api/handlers/auth_test.go` | |
| FR-AUTH-003 | Session token refresh before expiry | P0 | Done | `backend/api/middleware/auth_test.go` | |
| FR-AUTH-004 | Invalidate all sessions on sign-out | P0 | Done | `backend/api/handlers/auth_test.go` | |
| FR-AUTH-005 | Redirect unauthenticated requests to /login | P0 | Done | `frontend/web-next/middleware.test.ts` | |

## FR-CRED: Credential Management

| FR ID | Description | Priority | Status | Test File | Notes |
|-------|-------------|----------|--------|-----------|-------|
| FR-CRED-001 | Store Vercel tokens encrypted | P0 | Done | `backend/api/services/credentials_test.go` | |
| FR-CRED-002 | Store Netlify tokens encrypted | P0 | Done | `backend/api/services/credentials_test.go` | |
| FR-CRED-003 | Store Railway tokens encrypted | P0 | Done | `backend/api/services/credentials_test.go` | |
| FR-CRED-004 | Store Fly.io tokens encrypted | P0 | Done | `backend/api/services/credentials_test.go` | |
| FR-CRED-005 | Store Supabase URL + service key encrypted | P0 | Done | `backend/api/services/credentials_test.go` | |
| FR-CRED-006 | Store AWS credentials encrypted | P1 | In Progress | — | AWS integration in progress |
| FR-CRED-007 | Store GCP service account JSON encrypted | P1 | In Progress | — | GCP integration in progress |
| FR-CRED-008 | Store Azure credentials encrypted | P1 | Planned | — | |
| FR-CRED-009 | Delete provider credentials | P0 | Done | `backend/api/handlers/credentials_test.go` | |
| FR-CRED-010 | Credential health check + UI status | P1 | Planned | — | |

## FR-DEPLOY: Deployment Execution

| FR ID | Description | Priority | Status | Test File | Notes |
|-------|-------------|----------|--------|-----------|-------|
| FR-DEPLOY-001 | Deploy to Vercel | P0 | Done | `backend/api/services/vercel/vercel_test.go` | |
| FR-DEPLOY-002 | Deploy to Netlify | P0 | Done | `backend/api/services/netlify/netlify_test.go` | |
| FR-DEPLOY-003 | Deploy to Railway | P0 | Done | `backend/api/services/railway/railway_test.go` | |
| FR-DEPLOY-004 | Deploy to Fly.io | P0 | Done | `backend/api/services/flyio/flyio_test.go` | |
| FR-DEPLOY-005 | Deploy to Supabase | P0 | Done | `backend/api/services/supabase/supabase_test.go` | |
| FR-DEPLOY-006 | Deploy to AWS | P1 | In Progress | — | |
| FR-DEPLOY-007 | Deploy to GCP | P1 | In Progress | — | |
| FR-DEPLOY-008 | Deploy to Azure | P1 | Planned | — | |
| FR-DEPLOY-009 | List deployments | P0 | Done | `backend/api/handlers/deployments_test.go` | |
| FR-DEPLOY-010 | Delete deployments | P0 | Done | `backend/api/handlers/deployments_test.go` | |
| FR-DEPLOY-011 | Deployment status transitions | P0 | Done | `backend/api/services/deployment_test.go` | |
| FR-DEPLOY-012 | Real-time log streaming (SSE) | P1 | In Progress | — | |
| FR-DEPLOY-013 | Auto-detect application framework | P0 | Done | `backend/api/services/detector_test.go` | |
| FR-DEPLOY-014 | Select buildpack based on framework | P0 | Done | `backend/api/services/buildpack_test.go` | |
| FR-DEPLOY-015 | Self-hosted SSH deployment | P1 | Planned | — | |

## FR-PROJ: Project Management

| FR ID | Description | Priority | Status | Test File | Notes |
|-------|-------------|----------|--------|-----------|-------|
| FR-PROJ-001 | Create projects (name, description, Git URL) | P0 | Done | `backend/api/handlers/projects_test.go` | |
| FR-PROJ-002 | List projects for user | P0 | Done | `backend/api/handlers/projects_test.go` | |
| FR-PROJ-003 | View project details | P0 | Done | `backend/api/handlers/projects_test.go` | |
| FR-PROJ-004 | Update project settings | P0 | Done | `backend/api/handlers/projects_test.go` | |
| FR-PROJ-005 | Delete project + deployments | P0 | Done | `backend/api/handlers/projects_test.go` | |
| FR-PROJ-006 | Link GitHub repository | P1 | Planned | — | |
| FR-PROJ-007 | One-click deploy from project | P1 | In Progress | — | |
| FR-PROJ-008 | Per-project environment variables | P0 | Done | `backend/api/services/env_test.go` | |

## FR-LLM: AI/LLM Integration

| FR ID | Description | Priority | Status | Test File | Notes |
|-------|-------------|----------|--------|-----------|-------|
| FR-LLM-001 | Store OpenAI API key + model | P1 | Planned | — | |
| FR-LLM-002 | Store Anthropic API key + model | P1 | Planned | — | |
| FR-LLM-003 | Store vLLM endpoint + health check | P2 | Planned | — | |
| FR-LLM-004 | Store MLX endpoint + health check | P2 | Planned | — | |
| FR-LLM-005 | LLM provider suggestion | P2 | Planned | — | |

## Coverage Summary

| Category | Total FRs | Done | In Progress | Planned |
|----------|-----------|------|-------------|---------|
| FR-AUTH | 5 | 5 | 0 | 0 |
| FR-CRED | 10 | 5 | 2 | 3 |
| FR-DEPLOY | 15 | 9 | 3 | 3 |
| FR-PROJ | 8 | 6 | 1 | 1 |
| FR-LLM | 5 | 0 | 0 | 5 |
| **Total** | **43** | **25** | **6** | **12** |

Coverage: **58%** Done, **14%** In Progress, **28%** Planned

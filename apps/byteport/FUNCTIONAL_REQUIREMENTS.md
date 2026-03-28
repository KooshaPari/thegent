# Byteport — Functional Requirements

All requirements are stated as SHALL statements. Each FR is traceable to a PRD epic.

---

## FR-AUTH: Authentication Requirements

Traces to: E1

| ID | SHALL Statement | Priority | Status |
|----|----------------|----------|--------|
| FR-AUTH-001 | The system SHALL authenticate users via WorkOS AuthKit using email/password | P0 | Done |
| FR-AUTH-002 | The system SHALL authenticate users via OAuth SSO (Google, GitHub) through WorkOS | P0 | Done |
| FR-AUTH-003 | The system SHALL refresh session tokens before expiry without user intervention | P0 | Done |
| FR-AUTH-004 | The system SHALL invalidate all active sessions on sign-out | P0 | Done |
| FR-AUTH-005 | The system SHALL redirect unauthenticated requests to `/login` for all protected routes | P0 | Done |

---

## FR-CRED: Credential Management Requirements

Traces to: E2

| ID | SHALL Statement | Priority | Status |
|----|----------------|----------|--------|
| FR-CRED-001 | The system SHALL store Vercel API tokens encrypted per user | P0 | Done |
| FR-CRED-002 | The system SHALL store Netlify API tokens encrypted per user | P0 | Done |
| FR-CRED-003 | The system SHALL store Railway API tokens encrypted per user | P0 | Done |
| FR-CRED-004 | The system SHALL store Fly.io API tokens encrypted per user | P0 | Done |
| FR-CRED-005 | The system SHALL store Supabase project URL and service role key encrypted per user | P0 | Done |
| FR-CRED-006 | The system SHALL store AWS access key ID, secret key, and region encrypted per user | P1 | In Progress |
| FR-CRED-007 | The system SHALL store GCP service account JSON encrypted per user | P1 | In Progress |
| FR-CRED-008 | The system SHALL store Azure subscription ID and client credentials encrypted per user | P1 | Planned |
| FR-CRED-009 | The system SHALL allow users to delete provider credentials at any time | P0 | Done |
| FR-CRED-010 | The system SHALL validate stored credentials against provider APIs and surface health status in the UI | P1 | Planned |

---

## FR-DEPLOY: Deployment Execution Requirements

Traces to: E3

| ID | SHALL Statement | Priority | Status |
|----|----------------|----------|--------|
| FR-DEPLOY-001 | The system SHALL deploy applications to Vercel using stored credentials | P0 | Done |
| FR-DEPLOY-002 | The system SHALL deploy applications to Netlify using stored credentials | P0 | Done |
| FR-DEPLOY-003 | The system SHALL deploy applications to Railway using stored credentials | P0 | Done |
| FR-DEPLOY-004 | The system SHALL deploy applications to Fly.io using stored credentials | P0 | Done |
| FR-DEPLOY-005 | The system SHALL deploy applications to Supabase using stored credentials | P0 | Done |
| FR-DEPLOY-006 | The system SHALL deploy applications to AWS using stored credentials | P1 | In Progress |
| FR-DEPLOY-007 | The system SHALL deploy applications to GCP using stored credentials | P1 | In Progress |
| FR-DEPLOY-008 | The system SHALL deploy applications to Azure using stored credentials | P1 | Planned |
| FR-DEPLOY-009 | The system SHALL list all deployments for the authenticated user | P0 | Done |
| FR-DEPLOY-010 | The system SHALL delete deployments and tear down provider resources | P0 | Done |
| FR-DEPLOY-011 | The system SHALL track deployment status transitions: pending -> building -> live / failed | P0 | Done |
| FR-DEPLOY-012 | The system SHALL stream build logs in real time during deployment | P1 | In Progress |
| FR-DEPLOY-013 | The system SHALL auto-detect the application framework from repository contents | P0 | Done |
| FR-DEPLOY-014 | The system SHALL select the correct buildpack based on detected framework | P0 | Done |
| FR-DEPLOY-015 | The system SHALL support deployment to user-owned SSH targets (self-hosted) | P1 | Planned |

---

## FR-PROJ: Project Management Requirements

Traces to: E4

| ID | SHALL Statement | Priority | Status |
|----|----------------|----------|--------|
| FR-PROJ-001 | The system SHALL allow users to create projects with name, description, and Git URL | P0 | Done |
| FR-PROJ-002 | The system SHALL list all projects for the authenticated user | P0 | Done |
| FR-PROJ-003 | The system SHALL display project details including deployments and environment variables | P0 | Done |
| FR-PROJ-004 | The system SHALL allow users to update project name, description, and environment variables | P0 | Done |
| FR-PROJ-005 | The system SHALL allow users to delete projects and all associated deployments | P0 | Done |
| FR-PROJ-006 | The system SHALL allow linking a GitHub repository to a project | P1 | Planned |
| FR-PROJ-007 | The system SHALL support one-click deploy from a project using stored provider configuration | P1 | In Progress |
| FR-PROJ-008 | The system SHALL store per-project environment variables and inject them at deploy time | P0 | Done |

---

## FR-LLM: AI/LLM Integration Requirements

Traces to: E5

| ID | SHALL Statement | Priority | Status |
|----|----------------|----------|--------|
| FR-LLM-001 | The system SHALL store OpenAI API key and model selection per user | P1 | Planned |
| FR-LLM-002 | The system SHALL store Anthropic API key and model selection per user | P1 | Planned |
| FR-LLM-003 | The system SHALL store vLLM endpoint URL and model ID and perform health checks | P2 | Planned |
| FR-LLM-004 | The system SHALL store MLX local inference endpoint URL and perform health checks | P2 | Planned |
| FR-LLM-005 | The system SHALL use configured LLM to suggest optimal providers based on project analysis | P2 | Planned |

---

## Requirement Status Legend

| Status | Meaning |
|--------|---------|
| Done | Implemented and tested |
| In Progress | Implementation started, not yet tested |
| Planned | Scoped but not started |
| Blocked | Blocked on dependency |

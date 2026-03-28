# Byteport — Product Requirements Document

## Overview

Byteport is a multi-cloud deployment platform that detects application types, selects optimal free-tier providers, and orchestrates deployments across 9+ cloud providers via a CLI, REST API, and web dashboard.

**Product Vision:** Any developer can deploy any application for free in under 5 minutes, without knowing which cloud provider to use.

---

## Epics and User Stories

### E1: Authentication (WorkOS AuthKit)

**Goal:** Secure, frictionless authentication using WorkOS AuthKit with session management.

| Story | Description | Acceptance Criteria |
|-------|-------------|-------------------|
| E1.1 | Sign up with email/password | User can register and receive a session token |
| E1.2 | Sign in with SSO (Google, GitHub) | OAuth redirect completes and user session is established |
| E1.3 | Session refresh and expiry | Tokens are refreshed before expiry; expired tokens redirect to login |
| E1.4 | Sign out | Session is invalidated on all devices |
| E1.5 | Protected routes | Unauthenticated users are redirected to `/login` |

---

### E2: Cloud Credential Management (8 Providers)

**Goal:** Users can store, update, and delete API credentials for each supported cloud provider. Credentials are stored encrypted per-user.

Providers: Vercel, Netlify, Railway, Fly.io, Supabase, AWS, GCP, Azure

| Story | Description | Acceptance Criteria |
|-------|-------------|-------------------|
| E2.1 | Add Vercel credentials | Token stored and validated against Vercel API |
| E2.2 | Add Netlify credentials | Token stored and validated |
| E2.3 | Add Railway credentials | Token stored and validated |
| E2.4 | Add Fly.io credentials | Token stored and validated |
| E2.5 | Add Supabase credentials | Project URL + service key stored |
| E2.6 | Add AWS credentials | Access key + secret + region stored |
| E2.7 | Add GCP credentials | Service account JSON stored |
| E2.8 | Add Azure credentials | Subscription ID + client credentials stored |
| E2.9 | Remove credentials | Provider credentials deleted from user profile |
| E2.10 | Credential health check | UI shows which credentials are valid or expired |

---

### E3: Deployment Execution

**Goal:** Users can create, list, and delete deployments for any supported provider. The system auto-detects project type and builds accordingly.

| Story | Description | Acceptance Criteria |
|-------|-------------|-------------------|
| E3.1 | Create deployment (Vercel) | Project deployed to Vercel; deployment URL returned |
| E3.2 | Create deployment (Netlify) | Project deployed to Netlify; deployment URL returned |
| E3.3 | Create deployment (Railway) | App deployed to Railway with env vars |
| E3.4 | Create deployment (Fly.io) | App deployed via Fly.io API; IP/URL returned |
| E3.5 | Create deployment (Supabase) | DB/edge functions deployed |
| E3.6 | Create deployment (AWS) | App deployed via Elastic Beanstalk or Lambda |
| E3.7 | Create deployment (GCP) | App deployed to Cloud Run or App Engine |
| E3.8 | Create deployment (Azure) | App deployed to App Service |
| E3.9 | List deployments | All deployments for authenticated user listed with status |
| E3.10 | Delete deployment | Deployment torn down on provider; record removed |
| E3.11 | Deployment status polling | Status transitions: pending -> building -> live / failed |
| E3.12 | Deployment logs | Live logs streamed during build phase |
| E3.13 | Auto framework detection | Framework detected from repo (Next.js, Go, Python, Rust, etc.) |
| E3.14 | Buildpack selection | Correct buildpack selected based on framework |
| E3.15 | Self-hosted deployment | Deploy to user-owned SSH targets |

---

### E4: Project Management

**Goal:** Users manage projects as logical containers that group deployments, environment variables, and provider settings.

| Story | Description | Acceptance Criteria |
|-------|-------------|-------------------|
| E4.1 | Create project | Project record created with name, description, Git URL |
| E4.2 | List projects | All projects for authenticated user displayed |
| E4.3 | View project detail | Deployments, env vars, and provider config shown |
| E4.4 | Update project settings | Name, description, env vars updateable |
| E4.5 | Delete project | Project and all linked deployments removed |
| E4.6 | Link GitHub repo | GitHub repo linked to project for auto-deploy |
| E4.7 | Deploy from project | One-click deploy using stored provider config |
| E4.8 | Environment variable management | Per-project env vars stored and injected at deploy time |

---

### E5: AI/LLM Integration

**Goal:** Users can configure and deploy LLM inference endpoints (vLLM, MLX, OpenAI, Anthropic) tied to their Byteport account.

| Story | Description | Acceptance Criteria |
|-------|-------------|-------------------|
| E5.1 | Configure OpenAI endpoint | API key + model selection stored |
| E5.2 | Configure Anthropic endpoint | API key + model selection stored |
| E5.3 | Configure vLLM self-hosted | Endpoint URL + model ID stored; health-check passes |
| E5.4 | Configure MLX on Apple Silicon | Local inference URL stored; health-check passes |
| E5.5 | LLM-assisted deployment suggestions | LLM suggests provider based on project analysis |

---

## Non-Functional Requirements

| Category | Requirement |
|----------|------------|
| Performance | API responses < 200ms (p95, excluding deployment execution) |
| Security | Credentials encrypted at rest; no plaintext secrets in logs |
| Availability | Dashboard uptime >= 99.5% |
| Scalability | Support 1000+ concurrent deployment jobs |
| Observability | All deployment events logged; `/kinfra` dashboard real-time |
| Accessibility | WCAG 2.1 AA for all dashboard pages |

---

## Out of Scope (v1)

- Billing/payment integration
- Team/organization multi-user accounts
- GitHub Actions native integration
- Custom domain management

# Architecture

## System Overview

Byteport follows a hexagonal (ports and adapters) architecture with a Go backend and Next.js 15 frontend.

```
                    ┌─────────────────────────────┐
                    │       Next.js 15 Frontend    │
                    │   shadcn/ui + Tailwind CSS   │
                    └──────────────┬──────────────┘
                                   │ REST / SSE
                    ┌──────────────▼──────────────┐
                    │        Gin HTTP Router       │
                    │   WorkOS AuthKit Middleware  │
                    └──────────────┬──────────────┘
                                   │
               ┌───────────────────▼───────────────────┐
               │           Service Layer                │
               │  DeploymentProvider interface          │
               │  FrameworkDetector                     │
               │  BuildpackSelector                     │
               │  ProjectManager                        │
               └───┬──────────┬────────┬───────────────┘
                   │          │        │
          ┌────────▼──┐ ┌─────▼──┐ ┌──▼──────┐
          │ Provider   │ │  GORM  │ │ WorkOS  │
          │ Adapters   │ │  (PG)  │ │  Auth   │
          │ (Vercel,   │ └────────┘ └─────────┘
          │  Netlify,  │
          │  Railway,  │
          │  Fly.io,   │
          │  Supabase, │
          │  AWS, GCP, │
          │  Azure)    │
          └────────────┘
```

## Key Components

### Backend (`backend/api/`)

| Package | Responsibility |
|---------|---------------|
| `handlers/` | HTTP request handling (Gin route handlers) |
| `middleware/` | Auth validation, request logging, CORS |
| `services/` | Business logic and provider integrations |
| `models/` | GORM data models |
| `services/<provider>/` | Per-provider deployment adapters |

### Frontend (`frontend/web-next/`)

| Directory | Responsibility |
|-----------|---------------|
| `app/` | Next.js App Router pages and layouts |
| `components/` | shadcn/ui + custom components |
| `lib/` | API client, auth utilities |
| `app/(auth)/` | Login, signup, callback routes |
| `app/dashboard/` | Main dashboard, projects, deployments |
| `app/settings/` | Credential management, LLM config |

## Data Flow: Deployment

```
User clicks Deploy
      │
      ▼
POST /api/deployments
      │
      ▼
Auth middleware (WorkOS token validation)
      │
      ▼
DeploymentHandler
      │
      ├── Load project + credentials from DB (GORM)
      ├── Select provider adapter
      ├── Run framework detection
      ├── Run buildpack selection
      │
      ▼
ProviderAdapter.Deploy(ctx, project, credentials)
      │
      ├── Upload artifacts to provider API
      ├── Poll status -> building -> live/failed
      ├── Stream logs via SSE
      │
      ▼
Return DeploymentResult (URL, status, logs)
```

## Authentication Flow

```
User visits /dashboard
      │
      ▼
Next.js middleware checks WorkOS session
      │
      ├─ Valid session -> render page
      └─ No session -> redirect to /login
                            │
                            ▼
                     WorkOS AuthKit UI
                            │
                            ▼
                     OAuth / email auth
                            │
                            ▼
                     WorkOS callback
                            │
                            ▼
                     Set session cookie
                            │
                            ▼
                     Redirect to /dashboard
```

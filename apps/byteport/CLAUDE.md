# Byteport — Claude Code Instructions

## Project Overview

**Byteport** is a cloud deployment platform that automatically detects applications, selects optimal free-tier providers, and deploys to 9+ cloud providers in minutes.

- **Tagline:** Deploy Anything, Anywhere, For Free
- **Dashboard:** `https://byte.kooshapari.com`
- **Infra monitor:** `https://byte.kooshapari.com/kinfra`

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | Go + GORM + Gin at `backend/api/` |
| Frontend | Next.js 15 + shadcn/ui at `frontend/web-next/` |
| Auth | WorkOS AuthKit |
| Database | PostgreSQL (GORM ORM) |
| Orchestrator | `byteport.py` (Python dev runner) |

## Supported Providers

AWS, Azure, GCP, Vercel, Netlify, Railway, Fly.io, Supabase, Render, Neon

## Worktree Discipline

Feature work must use worktrees:

```
.worktrees/<topic>/
```

Do not author feature work directly in `apps/byteport/` canonical folder. Use worktrees for:
- New provider integrations
- Auth migrations
- LLM feature additions
- UI overhauls

## Package Managers

- Backend: Go modules (`go.mod`)
- Frontend: pnpm (`pnpm-lock.yaml`)

## Linting & Formatting

| Layer | Linter | Formatter |
|-------|--------|-----------|
| Backend | golangci-lint | gofumpt |
| Frontend | biome | biome format |

Run quality gates via `task lint` and `task test`.

## Library Preferences

| Purpose | Preferred Library |
|---------|------------------|
| HTTP router | Gin |
| ORM | GORM |
| Frontend UI | shadcn/ui + Radix |
| CSS | Tailwind CSS v4 |
| Icons | Lucide React |
| Auth | WorkOS AuthKit |
| State | Zustand or React Query |
| Testing (Go) | testify |
| Testing (TS) | vitest + testing-library |

## Architecture Pattern

Hexagonal architecture:
- `backend/api/` — HTTP handlers (adapters)
- Domain logic in service layer
- Provider integrations as secondary adapters
- GORM models as persistence layer

## Key Entry Points

- Backend main: `backend/api/main.go`
- Frontend: `frontend/web-next/app/`
- Dev runner: `byteport.py`
- Docs: `docs/`

## Spec Docs

- `PRD.md` — Product requirements and epics
- `ADR.md` — Architecture decision records
- `FUNCTIONAL_REQUIREMENTS.md` — FR-{CAT}-{NNN} requirements
- `PLAN.md` — Phased WBS

## Where to Add New Functionality

| Feature Type | Location |
|-------------|---------|
| New provider integration | `backend/api/services/<provider>/` |
| New API endpoint | `backend/api/handlers/` |
| New frontend page | `frontend/web-next/app/<route>/` |
| New UI component | `frontend/web-next/components/` |
| New LLM model support | `backend/api/services/llm/` |
| New credential type | `backend/api/models/user.go` (embedded struct) |

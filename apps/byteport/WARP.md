# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Architecture Overview

BytePort is a multi-cloud deployment platform with a **hexagonal/clean architecture** backend (Go) and modern Next.js frontend, powered by KInfra orchestration:

```
BytePort/
├── byteport.py              - Main orchestrator (KInfra-powered)
├── backend/api/             - Go API server (Hexagonal Architecture)
│   ├── internal/            - NEW: Hexagonal architecture
│   │   ├── domain/          - Pure business logic (ports)
│   │   ├── application/     - Use cases + DTOs
│   │   ├── infrastructure/  - Adapters (HTTP, DB, Cloud)
│   │   └── container/       - Dependency injection
│   └── (legacy files)       - Preserved for compatibility
├── frontend/web-next/       - Next.js 15 dashboard (React 19)
├── docs/                    - Documentation
└── .env, setup.sh, etc.     - Configuration & scripts
```

### Core Components

1. **KInfra Orchestrator (`byteport.py`)**
   - Manages service lifecycle, port allocation, and Cloudflare tunnels
   - Depends on `~/KInfra/libraries/python` and Pheno-SDK libraries
   - Provides unified entry point for all operations

2. **Go API Server (`backend/api/`)**
   - **Hexagonal Architecture** (Clean Architecture)
     - `internal/domain/` - Pure business logic, entities, value objects, ports
     - `internal/application/` - Use cases, DTOs, orchestration
     - `internal/infrastructure/` - Adapters (HTTP, DB, external services)
     - `internal/container/` - Dependency injection
   - Uses Gin web framework with GORM for PostgreSQL
   - Supports WorkOS AuthKit authentication
   - Custom Go module cache at `.gocache/.gomodcache`
   - **Test Coverage**: 58.2% domain layer (growing)

3. **Next.js Frontend (`frontend/web-next/`)**
   - React 19 with Next.js 15, using pnpm as package manager
   - Radix UI components with Tailwind CSS
   - **State Management**:
     - React Context for authentication
     - Zustand for UI state (sidebar, theme)
     - React Query (planned migration) for server state
   - **Routing**: Canonical URL structure with automatic redirects
   - **Testing**: Vitest for unit tests, Playwright for E2E
   - Environment-aware API configuration

4. **Service Discovery**
   - Dynamic port allocation via KInfra PortRegistry
   - Cloudflare tunnels for public URLs (`byte.kooshapari.com`)
   - Health checks and dependency management

## Essential Commands

### Service Management
```bash
# Start all services (production)
./byteport.py

# Development mode (live reload + logs)
./byteport.py --dev

# Local mode (localhost only, no tunnels)
./byteport.py --local

# Stop all services
./byteport.py --stop

# Check service status
./byteport.py --status

# Quick reset (clears all state)
./quick_fix.sh
```

### First-Time Setup
```bash
# One-time installation
./setup.sh

# Includes:
# - Python dependencies + Pheno-SDK packages
# - Go modules + Air (live reload)
# - Frontend dependencies (pnpm preferred)
# - KInfra verification
```

### Individual Services

**Backend API:**
```bash
cd backend/api

# Development (manual, with logs)
GOCACHE=$(pwd)/.gocache GOMODCACHE=$(pwd)/.gomodcache go run .

# With Air live reload
air

# Build
GOCACHE=$(pwd)/.gocache GOMODCACHE=$(pwd)/.gomodcache go build

# Test
go test ./...
```

**Frontend:**
```bash
cd frontend/web-next

# Development
pnpm dev                    # Production API
pnpm dev:local              # Local API (localhost)

# Build & production
pnpm build
pnpm start

# Lint
pnpm lint
```

### Testing

**Backend (Go)**:
```bash
cd backend/api

# Run all tests
go test ./...

# Run with coverage
go test -cover ./...

# Run specific package
go test ./internal/domain/deployment/...

# Verbose output
go test -v ./...
```

**Current Coverage**: 58.2% (domain layer)
- Domain entity tests
- Status value object tests
- Repository interface tests
- Cloud provider tests

**Frontend (TypeScript)**:
```bash
cd frontend/web-next

# Unit tests (Vitest)
pnpm test                    # Run all tests
pnpm test:watch             # Watch mode
pnpm test:coverage          # With coverage

# E2E tests (Playwright)
pnpm test:e2e               # Run E2E tests
pnpm test:e2e:ui            # Interactive UI mode

# Linting & Type checking
pnpm lint                    # ESLint
pnpm type-check             # TypeScript

# Build (validates all types)
pnpm build
```

**Test Structure**:
```
backend/api/
├── internal/domain/deployment/
│   ├── deployment_test.go          # Entity tests
│   ├── status_test.go              # Value object tests
│   └── service_test.go             # Domain service tests
└── internal/infrastructure/
    └── persistence/
        └── deployment_repository_test.go  # Integration tests

frontend/web-next/
├── components/
│   └── *.test.tsx                  # Component unit tests
├── lib/hooks/
│   └── *.test.ts                   # Hook tests
├── test/
│   └── utils.tsx                   # Test utilities
└── e2e-pages/                      # Playwright page objects
```

## Key Development Patterns

### Environment Configuration

**Multi-layer environment handling:**
1. Root `.env` - shared configuration
2. `backend/.env` - API-specific settings
3. `frontend/web-next/.env.local` - frontend overrides

**Mode switching:**
- `--dev`: Production URLs with live reload
- `--local`: Localhost URLs only
- Default: Production mode with tunnels

### Port Management

**Dynamic allocation via KInfra:**
- API defaults to 8080, frontend to 3000
- Automatic conflict resolution
- Persistent registry at `~/.kinfra/port_registry.json`

### Dependency Management

**Go modules:**
- Isolated cache: `backend/api/.gocache/.gomodcache`
- Offline mode: `GOPROXY=off GONOSUMDB=*`
- Module mode: `go build -mod=mod`

**Node.js:**
- pnpm preferred, npm fallback
- Lock file: `pnpm-lock.yaml`

**Python:**
- Editable installs from Pheno-SDK: `/Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/`
- KInfra path import: `~/KInfra/libraries/python`

### Service Dependencies

**Startup order:**
1. API server (backend/api)
2. Frontend (depends on API)

**Health checks:**
- API: `GET /api/v1/health`
- Frontend: Next.js ready event

## Integration Points

### Pheno-SDK Libraries
- **tui-kit**: Terminal UI components (TunnelStatusWidget, ProgressWidget)
- **process-monitor-sdk**: Process lifecycle management
- All installed via editable installs in setup.sh

### KInfra Infrastructure
- **ServiceOrchestrator**: Manages service lifecycle
- **PortRegistry**: Persistent port allocation
- **TunnelManager**: Cloudflare tunnel automation
- **Not pip-installed**: Path import from `~/KInfra/libraries/python`

### Authentication
- WorkOS AuthKit integration in Next.js frontend
- JWT token handling in Go API
- Environment variables for WorkOS configuration

## Development Workflow

### Quick Start Development
```bash
./quick_fix.sh              # Reset state
./byteport.py --dev          # Start with logs
```

### Making Changes
- **Backend**: Air auto-restarts on Go file changes
- **Frontend**: Next.js Fast Refresh on save
- **Python**: Restart orchestrator to pick up changes

### Debugging
- **Service logs**: Visible in `--dev` mode terminal output
- **Individual logs**: `tail -f api.log` / `tail -f frontend.log`
- **Port conflicts**: Use `./quick_fix.sh` to reset
- **State issues**: Check `~/.kinfra/port_registry.json`

### Common Issues
- **"Unsupported protocol"**: Service not ready yet, check health endpoint
- **Port conflicts**: Multiple services assigned same port → run `./quick_fix.sh`
- **KInfra import errors**: Verify `~/KInfra/libraries/python` exists
- **Pheno-SDK missing**: Run `./setup.sh` to reinstall editable packages

## Production Considerations

### Cloudflare Tunnels
- Domain: `byte.kooshapari.com`
- Authentication required: `cloudflared tunnel login`
- Config stored in `~/.cloudflared/`

### Database
- PostgreSQL connection via GORM
- Connection string in `.env`: `DATABASE_URL`
- Migrations in `backend/migrations/`

### Deployment Modes
- **Production**: `./byteport.py` (background, tunnels)
- **Development**: `./byteport.py --dev` (foreground, tunnels)
- **Local**: `./byteport.py --local` (foreground, localhost only)

## Backend Architecture (Hexagonal/Clean)

### Domain Layer (`internal/domain/`)
**Pure business logic - no external dependencies**

```
internal/domain/deployment/
├── deployment.go        # Core entity with business logic
├── status.go           # Status value object with state machine
├── errors.go           # Domain-specific errors
├── repository.go       # Repository port (interface)
└── service.go          # Domain service for complex logic
```

**Key Concepts**:
- **Entities**: Core business objects (Deployment)
- **Value Objects**: Immutable types with validation (Status)
- **Ports**: Interfaces defining contracts (Repository)
- **Domain Services**: Business logic that doesn't fit in entities
- **Domain Errors**: Type-safe error handling

**Example - Deployment Entity**:
```go
type Deployment struct {
    UUID        string
    Name        string
    Status      Status
    Services    []Service
    // ... business methods
}

func (d *Deployment) SetStatus(newStatus Status) error {
    if !d.Status.CanTransitionTo(newStatus) {
        return ErrInvalidTransition
    }
    d.Status = newStatus
    return nil
}
```

### Application Layer (`internal/application/`)
**Use cases and orchestration**

```
internal/application/
├── dto/                 # Data Transfer Objects
│   ├── deployment_dto.go
│   └── request.go
├── usecases/           # Business use cases
│   ├── create_deployment.go
│   ├── get_deployment.go
│   ├── list_deployments.go
│   ├── terminate_deployment.go
│   └── update_status.go
└── errors.go           # Application errors with HTTP mapping
```

**Key Concepts**:
- **Use Cases**: Single responsibility operations
- **DTOs**: Input/output contracts separate from domain
- **Transaction Management**: Coordinates domain operations
- **Error Translation**: Maps domain errors to application errors

**Example - Create Deployment Use Case**:
```go
type CreateDeploymentUseCase struct {
    repo    domain.Repository
    service *domain.DeploymentService
}

func (uc *CreateDeploymentUseCase) Execute(req CreateDeploymentRequest) (*DeploymentDTO, error) {
    // Validate, create domain entity, save, return DTO
}
```

### Infrastructure Layer (`internal/infrastructure/`)
**Adapters for external concerns**

```
internal/infrastructure/
├── http/               # HTTP adapters (Gin)
│   ├── handlers/
│   │   └── deployment_handler.go
│   └── middleware/
│       └── auth_middleware.go
└── persistence/        # Database adapters (GORM)
    ├── models/
    │   └── deployment_model.go
    ├── mappers/
    │   └── deployment_mapper.go
    └── repositories/
        └── deployment_repository.go
```

**Key Concepts**:
- **HTTP Handlers**: Transform HTTP → DTOs → Use Cases → HTTP
- **Repository Implementations**: Domain repository port → GORM
- **Mappers**: Convert domain entities ↔ persistence models
- **Middleware**: Cross-cutting concerns (auth, logging, CORS)

**Example - HTTP Handler**:
```go
func (h *DeploymentHandler) CreateDeployment(c *gin.Context) {
    var req CreateDeploymentRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(400, ErrorResponse{Error: err.Error()})
        return
    }
    
    dto, err := h.createUseCase.Execute(req)
    // handle response
}
```

### Dependency Injection (`internal/container/`)
**Wire all layers together**

```go
type Container struct {
    db                    *gorm.DB
    deploymentRepo        domain.Repository
    deploymentService     *domain.DeploymentService
    createUseCase         *application.CreateDeploymentUseCase
    deploymentHandler     *http.DeploymentHandler
}

func NewContainer(db *gorm.DB) *Container {
    // Initialize layers bottom-up: infra → app → handlers
}
```

## Frontend Architecture

### Route Structure (Canonical URLs)
**All routes use canonical URLs with automatic redirects from legacy paths**

```
App Routes:
├── /                           # Landing page
├── /auth/
│   ├── /callback              # OAuth callback
│   └── /login                 # Login page
├── /dashboard                 # Main dashboard
├── /deployments               # Deployments list
│   ├── /new                   # Create deployment
│   └── /[id]                  # Deployment details
│       ├── /logs              # Deployment logs
│       └── /metrics           # Deployment metrics
├── /projects                  # Projects list
│   ├── /new                   # Create project
│   └── /[id]                  # Project details
├── /providers                 # Cloud providers
│   └── /[provider]           # Provider config
├── /hosts                     # Host management
│   ├── /new                   # Add host
│   └── /[id]                  # Host details
├── /monitoring                # System monitoring
├── /costs                     # Cost analytics
└── /settings                  # Settings
    ├── /profile              # User profile
    ├── /api-keys             # API key management
    ├── /billing              # Billing settings
    ├── /preferences          # User preferences
    ├── /providers            # Provider settings
    └── /integrations         # Integrations

Legacy Routes (Redirected):
/home/*                        → Redirects to canonical URLs (301)
```

### Component Architecture

```
frontend/web-next/
├── app/                       # Next.js 13+ app directory
│   ├── (auth)/               # Auth route group
│   ├── (dashboard)/          # Dashboard route group
│   │   ├── layout.tsx        # Shared layout
│   │   └── [routes]/         # All app routes
│   └── layout.tsx            # Root layout
├── components/
│   ├── ui/                   # Shadcn/Radix primitives
│   ├── layout/               # Layout components
│   │   ├── Header.tsx        # Dashboard header
│   │   ├── AppShell.tsx      # Main app shell
│   │   └── Breadcrumbs.tsx   # Navigation breadcrumbs
│   ├── sidebar.tsx           # Main navigation sidebar
│   ├── header.tsx            # Global header
│   ├── user-nav.tsx          # User dropdown menu
│   └── [features]/           # Feature-specific components
├── context/
│   └── auth-context.tsx      # Authentication context
├── lib/
│   ├── api.ts               # API client
│   ├── types.ts             # TypeScript types
│   ├── hooks/               # Custom React hooks
│   │   ├── use-sse.ts       # Server-Sent Events
│   │   ├── use-deployments.ts
│   │   └── [more hooks]
│   ├── stores/              # Zustand stores (UI state)
│   └── utils.ts             # Utility functions
└── middleware.ts            # Route redirects + auth
```

### State Management Strategy

```typescript
// Authentication (React Context)
import { useAuth } from '@/context/auth-context';
const { user, status, login, logout } = useAuth();

// UI State (Zustand)
import { useUIStore } from '@/lib/stores';
const { sidebarCollapsed, toggleSidebar } = useUIStore();

// Server State (React Query - planned migration)
import { useQuery } from '@tanstack/react-query';
const { data, isLoading } = useQuery(['deployments'], fetchDeployments);
```

### Real-time Features

**Server-Sent Events (SSE)**:
```typescript
// Live logs streaming
import { useLogStream } from '@/lib/hooks/use-log-stream';
const { logs, isConnected, reconnect } = useLogStream({ deploymentId });

// Deployment status updates
import { useDeploymentStatus } from '@/lib/hooks/use-deployment-status';
const { status, isConnected } = useDeploymentStatus({ deploymentId });

// Real-time metrics
import { useSSE } from '@/lib/hooks/use-sse';
const { state, reconnect } = useSSE(metricsUrl, { onMessage });
```

## API Documentation

### Endpoints

**Deployment Management**:
```
POST   /api/v1/deployments              # Create deployment
GET    /api/v1/deployments              # List deployments
GET    /api/v1/deployments/:id          # Get deployment
PATCH  /api/v1/deployments/:id/status   # Update status
DELETE /api/v1/deployments/:id          # Terminate deployment
GET    /api/v1/deployments/:id/logs     # Stream logs (SSE)
GET    /api/v1/deployments/:id/metrics  # Stream metrics (SSE)
```

**Health & Status**:
```
GET    /api/v1/health                   # Health check
GET    /api/v1/version                  # API version
```

### Request/Response Examples

**Create Deployment**:
```json
POST /api/v1/deployments
{
  "name": "my-app",
  "provider": "aws",
  "region": "us-east-1",
  "services": [
    {
      "name": "web",
      "image": "nginx:latest",
      "ports": [80, 443]
    }
  ],
  "environment": {
    "NODE_ENV": "production"
  }
}

Response: 201 Created
{
  "uuid": "dep-abc123",
  "name": "my-app",
  "status": "pending",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Stream Logs (SSE)**:
```bash
curl -N http://localhost:8080/api/v1/deployments/dep-abc123/logs

data: {"level":"info","message":"Starting deployment","timestamp":"2024-01-15T10:30:01Z"}
data: {"level":"info","message":"Building container","timestamp":"2024-01-15T10:30:05Z"}
```

- **OpenAPI Schema**: `backend/api/openapi.yaml`
- **Live Docs**: `http://localhost:{port}/api/v1/docs` (when running)

## Refactoring Status & Recent Changes

### Completed Phases

#### Phase 1: Critical Cleanup ✅
- Removed legacy bloat directories (.archive/, .history/, __pycache__)
- Secured sensitive .env files (removed from git, created .env.example templates)
- Created SECURITY_ALERT.md with credential rotation instructions
- Fixed Go version in backend go.mod (1.24.0 → 1.23.4)
- Enhanced .gitignore to prevent future secret leaks

#### Phase 2: Backend Hexagonal Architecture ✅
**2,200+ lines of new architecture code**

**2.1 - Domain Layer**:
- Rich deployment entity with business logic (287 lines)
- Status value object with state machine validation
- Domain-specific error types
- Repository port interface
- Domain service for complex business rules

**2.2 - Application Layer**:
- DTOs for all use cases (~609 lines)
- CreateDeployment, GetDeployment, ListDeployments use cases
- TerminateDeployment, UpdateStatus use cases
- Application error types with HTTP mapping
- Transaction coordination logic

**2.3 - Infrastructure Layer**:
- GORM persistence models (~678 lines)
- Domain entity ↔ persistence model mappers
- Repository implementation with full CRUD
- HTTP handlers with Gin framework
- Authentication middleware (JWT)

**2.4 - Dependency Injection**:
- Container pattern for wiring layers
- Bottom-up initialization (infra → app → handlers)
- Clean separation of concerns

**Test Coverage**: 58.2% domain layer
- Deployment entity tests
- Status value object tests
- Cloud provider validation
- All backend tests passing ✅

#### Phase 3: Frontend Consolidation ✅ (Partial)

**3.1-3.3 - Component Consolidation**:
- Removed duplicate Sidebar component
- Removed duplicate Header component
- Unified authentication state (React Context)
- Cleaned up Zustand store (removed user/auth state)

**3.4 - Route Consolidation** ✅:
- Implemented 301 redirects for 8 legacy `/home/*` routes
- Updated all navigation links to canonical URLs
- Created middleware for automatic redirects
- **Production build successful** (6s compile, 30 static pages)
- Fixed 15+ build errors including:
  - Missing DashboardHeader component
  - Playwright test bundling
  - SSE hook type errors
  - LogLevel export naming
  - Middleware authentication chain

**Route Mappings**:
```
/home                      → /dashboard
/home/settings             → /settings
/home/settings/profile     → /settings/profile
/home/settings/integrations → /settings/integrations
/home/projects             → /projects
/home/projects/new         → /projects/new
/home/instances            → /deployments
/home/monitor              → /monitoring
```

### In Progress

#### Phase 3.5-3.6: Frontend State Management
- [ ] React Query migration for server state
- [ ] Remove legacy Zustand store
- [ ] Optimize data fetching patterns
- [ ] Implement optimistic updates

#### Phase 5: Enhanced Testing
- [x] Domain layer tests (58.2%)
- [ ] Application layer tests (use case mocks)
- [ ] Infrastructure integration tests
- [ ] Frontend component tests
- [ ] E2E test suite
- **Target**: 70%+ code coverage

### Future Phases

#### Phase 4: Microservice Boundaries
- Define service boundaries
- Plan event-driven communication
- Design API contracts
- Implement service mesh considerations

#### Phase 6: Documentation & DevOps
- [x] Update WARP.md with architecture
- [ ] Create C4 diagrams
- [ ] Document API contracts
- [ ] CI/CD pipeline enhancements
- [ ] Deployment automation

### Key Metrics

**Codebase Health**:
- Backend test coverage: 58.2%
- Frontend build: ✅ Successful (6s)
- Zero compilation errors
- Legacy code removed: ~660MB

**Architecture Quality**:
- Hexagonal architecture: Fully implemented
- Dependency injection: Container pattern
- Route consolidation: 100% canonical
- Component duplication: Eliminated

**Performance**:
- Frontend build time: 6s
- Static pages generated: 30
- Middleware size: 123 KB
- First Load JS: 102-159 KB per route

### Documentation Resources

**Architecture & Design**:
- `WARP.md` - This file (architecture overview)
- `docs/REFACTORING_SUMMARY.md` - Complete refactoring history
- `docs/PHASE_2_COMPLETE.md` - Backend hexagonal architecture
- `docs/PHASE_3.4_COMPLETE.md` - Route consolidation details
- `docs/ROUTE_CONSOLIDATION.md` - Migration guide

**Security**:
- `docs/SECURITY_ALERT.md` - Credential rotation instructions
- `.env.example` files - Environment templates

**Testing**:
- `backend/api/internal/domain/deployment/*_test.go` - Domain tests
- `frontend/web-next/vitest.config.ts` - Vitest configuration
- `frontend/web-next/playwright.config.ts` - Playwright configuration

### Development Guidelines

**Backend Development**:
1. Start with domain entities and value objects
2. Define repository ports (interfaces)
3. Implement use cases in application layer
4. Add infrastructure adapters last
5. Wire everything in container
6. Write tests for each layer

**Frontend Development**:
1. Use canonical routes only (no `/home/*`)
2. Authentication via React Context
3. UI state via Zustand
4. Server state via React Query (migrating)
5. Real-time features via SSE hooks
6. Type-safe API calls via `lib/api.ts`

**Testing Strategy**:
- Backend: Unit tests for domain, integration tests for infrastructure
- Frontend: Component tests with Vitest, E2E with Playwright
- Target: 70%+ coverage before production
- Run tests before committing

**Code Quality**:
- Use type-safe patterns
- Follow hexagonal architecture principles
- Write self-documenting code
- Keep functions small and focused
- Document complex business logic

### Migration Notes

**From Legacy Routes**:
- All `/home/*` routes redirect to canonical paths (301)
- Update bookmarks to new URLs
- Legacy page files preserved temporarily
- Monitor telemetry before removing legacy files

**From Legacy Stores**:
- Auth state: Use `useAuth()` hook
- UI state: Use `useUIStore()` for sidebar/theme
- Server state: Migrate to React Query
- Do not use legacy global store

**API Integration**:
- Use `lib/api.ts` for all API calls
- Real-time: Use SSE hooks (`useSSE`, `useLogStream`, etc.)
- Error handling: Application errors map to HTTP status
- Authentication: JWT tokens via WorkOS AuthKit

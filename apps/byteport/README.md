# BytePort - Deploy Anything, Anywhere, For Free

> **Production-ready multi-cloud deployment platform with zero-cost optimization**

BytePort automatically detects your application, selects optimal free-tier providers, and deploys everything in minutes. Deploy to Vercel, Render, Supabase, Fly.io, or your own hardware with a single command.

## 🚀 Quick Start

```bash
# Start BytePort services
python byteport.py --dev

# Access dashboard
open https://byte.kooshapari.com
# or local: http://localhost:8001

# Monitor infrastructure
open https://byte.kooshapari.com/kinfra
```

## ✨ Features

- ✅ **Multi-Cloud Support** - 9+ cloud providers (Vercel, Render, Supabase, Neon, Railway, Fly.io, etc.)
- ✅ **Zero-Cost Deployments** - Automatic free-tier optimization ($0/month for most apps)
- ✅ **Self-Hosted Targets** - Deploy to your own machines
- ✅ **Auto-Detection** - Supports 20+ frameworks (Next.js, React, Vue, Go, Python, Rust, etc.)
- ✅ **Three Interfaces** - CLI, REST API, and Web Dashboard
- ✅ **Real-Time Monitoring** - Live logs, metrics, and status via `/kinfra` dashboard
- ✅ **Professional Error Pages** - Cloudflare-like loading/error pages
- ✅ **WorkOS AuthKit Integration** - Secure authentication out of the box

## 📖 Documentation

**Getting Started:**
- [Quick Start Guide](docs/QUICK_START.md)
- [Installation Guide](docs/INSTALLATION.md)
- [Your First Deployment](docs/FIRST_DEPLOYMENT.md)

**User Guides:**
- [CLI Reference](docs/CLI_USER_GUIDE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Web Dashboard](docs/WEB_DASHBOARD_GUIDE.md)
- [OpenAPI Schema](backend/api/openapi.yaml)

**SDKs:**
- [Go SDK](sdk/go/README.md)
- [Python SDK](sdk/python/README.md)
- [TypeScript SDK](sdk/typescript/README.md)

**Advanced:**
- [Self-Hosted Deployment](docs/SELF_HOSTED_GUIDE.md)
- [Multi-Cloud Patterns](docs/HYBRID_DEPLOYMENT_PATTERNS.md)
- [Cost Optimization](docs/COST_OPTIMIZATION.md)

**Architecture:**
- [System Architecture](docs/CLEAN_ARCHITECTURE_DESIGN.md)
- [Cloud Providers](docs/PROVIDER_IMPLEMENTATION_COMPLETE.md)
- [Buildpack System](docs/ENHANCED_BUILDPACK_DESIGN.md)
- [Database Schema](docs/DATABASE_SCHEMA.md)

## 🏗️ Architecture

```
BytePort
├── backend/api          - Go API server (port 8000)
├── frontend/web-next    - Next.js dashboard (port 8001)
└── byteport.py          - KInfra-powered orchestrator

Powered by KInfra:
- Automatic port allocation
- Cloudflare tunnels
- Health monitoring
- Error pages
- Service orchestration
```

## 🛠️ Development

```bash
# Local development (uses localhost ports)
python byteport.py --local

# Development with production URLs
python byteport.py --dev

# Production
python byteport.py

# Stop all services
python byteport.py --stop

# View status
python byteport.py --status
```

## 🧪 Testing

**Quick Start:**
```bash
# Run all tests
python byteport.py --test

# Run unit tests only (backend + frontend)
python byteport.py --test-unit

# Run E2E tests only
python byteport.py --test-e2e

# Using test runner directly
./scripts/test_runner.py --all
./scripts/test_runner.py --backend --coverage
./scripts/test_runner.py --frontend --watch
```

**Test Suites:**
- ✅ **Backend Tests** - Go with testify/suite, in-memory and SQLite testing
- ✅ **Frontend Tests** - Vitest + Testing Library + MSW for API mocking
- ✅ **E2E Tests** - Playwright with Page Object Models
- ✅ **CI/CD** - GitHub Actions with comprehensive workflows

**Documentation:**
- [Testing Guide](TESTING.md) - Complete testing documentation
- [WARP.md](WARP.md) - Architecture and development patterns

## 📊 Monitoring

Access the KInfra dashboard at:
```
https://byte.kooshapari.com/kinfra
```

Shows:
- Real-time service status
- Live logs
- Port/PID information
- Health checks
- Action buttons (restart/stop)

## 🔧 Configuration

### Environment Variables

```bash
# Production (default)
NEXT_PUBLIC_API_URL=https://byte.kooshapari.com/api/v1

# Local development
NEXT_PUBLIC_USE_LOCAL=true  # Set via npm run dev:local
```

### WorkOS AuthKit

```bash
WORKOS_API_KEY='your-key'
WORKOS_CLIENT_ID='your-client-id'
WORKOS_COOKIE_PASSWORD='generate-with-openssl'
NEXT_PUBLIC_WORKOS_REDIRECT_URI='https://byte.kooshapari.com/auth/callback'
```

## 🚢 Deployment Workflow

1. **Detect** - Scan project for framework, runtime, dependencies
2. **Select** - Choose optimal providers based on requirements and cost
3. **Build** - Generate provider-specific configurations
4. **Deploy** - Push to selected providers
5. **Monitor** - Track deployments via dashboard

## 🌐 Supported Platforms

**Cloud Providers:**
- Vercel, Netlify, Render, Railway, Fly.io
- Supabase, Neon (serverless Postgres)
- Upstash (Redis)
- AWS, GCP, Azure

**Self-Hosted:**
- Linux servers (Ubuntu, Debian, CentOS)
- macOS (local development)
- Windows (WSL support)
- Docker containers

## 📝 License

MIT

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 🔗 Links

- **Website:** https://byte.kooshapari.com
- **Dashboard:** https://byte.kooshapari.com/kinfra
- **API Docs:** https://byte.kooshapari.com/api/docs
- **GitHub:** https://github.com/kooshapari/BytePort

# atomsAgent Documentation

Welcome to the atomsAgent documentation. This is your guide to understanding, developing, deploying, and troubleshooting atomsAgent.

## 🚀 Quick Navigation

### Getting Started
- **[Development Guide](./guides/DEVELOPMENT_GUIDE.md)** - Set up your development environment
- **[CLI Reference](./guides/CLI_REFERENCE.md)** - Learn all CLI commands
- **[Troubleshooting Guide](./guides/TROUBLESHOOTING_GUIDE.md)** - Solve common issues

### Architecture & Design
- **[Architecture](./architecture/ARCHITECTURE.md)** - System design and components
- **[API Reference](./api/API_REFERENCE.md)** - Complete API documentation

### Deployment
- **[Cloud Run Setup](./deployment/CLOUD_RUN_SETUP.md)** - Deploy to Google Cloud Run
- **[Deployment Options](./deployment/DEPLOYMENT_OPTIONS.md)** - Compare deployment platforms

### SDK & Integration
- **[SDK Generation](./guides/SDK_GENERATION.md)** - Generate Python/TypeScript SDKs

### Research & Analysis
- **[Deployment Architecture Analysis](./research/DEPLOYMENT_ARCHITECTURE_ANALYSIS.md)** - Why Cloud Run is recommended
- **[API Documentation Tools](./research/API_DOCUMENTATION_TOOLS_ANALYSIS.md)** - Why OpenAPI + Swagger is optimal
- **[Zensical Migration Analysis](./research/ZENSICAL_MIGRATION_ANALYSIS.md)** - Future documentation platform

---

## 📚 Documentation Structure

**Primary Documentation:** All documentation is now served via **MkDocs** at `/wiki`

```
docs/
├── mkdocs/                            # MkDocs documentation (PRIMARY)
│   ├── mkdocs.yml                    # MkDocs configuration
│   ├── docs/                         # Source markdown files
│   │   ├── index.md                  # Home page
│   │   ├── quick-start.md            # Quick start guide
│   │   ├── api/                      # API documentation
│   │   ├── guides/                   # User guides
│   │   ├── architecture/             # Architecture docs
│   │   ├── deployment/               # Deployment guides
│   │   └── research/                 # Research documents
│   └── site/                         # Built site (generated)
│
├── README.md                          # This file (legacy index)
├── guides/                            # Legacy guides (source for MkDocs)
├── deployment/                        # Legacy deployment (source for MkDocs)
├── api/                               # Legacy API docs (source for MkDocs)
├── architecture/                      # Legacy architecture (source for MkDocs)
├── research/                          # Legacy research (source for MkDocs)
├── sessions/                          # Current work tracking
└── archive/                           # Historical documentation
```

**Access Documentation:**
- **MkDocs (Primary)**: http://localhost:8000/wiki
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔑 Key Commands

```bash
# Development
atoms-agent server run --reload        # Start dev server
atoms-agent test                       # Run tests

# Documentation
cd docs/mkdocs && mkdocs serve         # Serve MkDocs locally
cd docs/mkdocs && mkdocs build         # Build MkDocs site
# Access at: http://localhost:8000/wiki (when server is running)

# Deployment
atoms-agent cloud-run deploy           # Deploy to Cloud Run
atoms-agent cloud-run logs             # View logs

# SDK Generation
atoms-agent sdk generate-python        # Generate Python SDK
atoms-agent sdk generate-typescript    # Generate TypeScript SDK
```

## 📖 Reading Paths by Role

### For Developers
1. [Development Guide](./guides/DEVELOPMENT_GUIDE.md) - Setup
2. [CLI Reference](./guides/CLI_REFERENCE.md) - Commands
3. [API Reference](./api/API_REFERENCE.md) - API docs
4. [Architecture](./architecture/ARCHITECTURE.md) - System design

### For DevOps/Operations
1. [Cloud Run Setup](./deployment/CLOUD_RUN_SETUP.md) - Deployment
2. [Deployment Options](./deployment/DEPLOYMENT_OPTIONS.md) - Comparison
3. [Troubleshooting Guide](./guides/TROUBLESHOOTING_GUIDE.md) - Issues

### For SDK Integration
1. [SDK Generation](./guides/SDK_GENERATION.md) - Generate SDKs
2. [API Reference](./api/API_REFERENCE.md) - API endpoints
3. [Troubleshooting Guide](./guides/TROUBLESHOOTING_GUIDE.md) - Issues

## 💬 Support

- **Setup Issues**: See [Development Guide](./guides/DEVELOPMENT_GUIDE.md)
- **Common Problems**: See [Troubleshooting Guide](./guides/TROUBLESHOOTING_GUIDE.md)
- **Command Help**: See [CLI Reference](./guides/CLI_REFERENCE.md)
- **System Understanding**: See [Architecture](./architecture/ARCHITECTURE.md)

---

**Last Updated:** November 2025
**Status:** Production Ready ✅
**Documentation Files:** 12 core files
**Archive:** 100+ historical files


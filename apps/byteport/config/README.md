# BytePort Configuration Guide

This directory contains environment-specific configuration templates and documentation for the BytePort platform.

## Configuration Architecture

BytePort uses a multi-layer configuration approach:

```
Root Config (.env)
    ├── Backend API Config (backend/.env)
    └── Frontend Config (frontend/web-next/.env.local)
```

## Environment Files

### Development
- `.env` (root) - Shared development configuration
- `backend/.env` - API-specific development settings
- `frontend/web-next/.env.local` - Frontend development overrides

### Production
- Use environment variables provided by your hosting platform
- Reference `production.env.template` for required variables
- Never commit production secrets to version control

## Quick Start

### First Time Setup

```bash
# 1. Copy templates
cp config/development.env.template .env
cp config/backend.env.template backend/.env  
cp config/frontend.env.template frontend/web-next/.env.local

# 2. Configure your environment
#    Edit each file and fill in your actual values
#    See "Configuration Variables" section below

# 3. Verify configuration
./byteport.py --status
```

### Rotating Secrets

After a security incident or periodic rotation:

```bash
# 1. Generate new secrets
./scripts/generate-secrets.sh

# 2. Update configuration files
#    - .env
#    - backend/.env
#    - frontend/web-next/.env.local

# 3. Restart services
./byteport.py --stop
./byteport.py
```

## Configuration Variables

### Root Configuration (.env)

#### Application
```bash
# Application Environment
NODE_ENV=development                    # development | production | staging
ENVIRONMENT=development                 # Runtime environment identifier

# Logging
LOG_LEVEL=info                         # debug | info | warn | error
LOG_FORMAT=json                        # json | text
```

#### Service Ports
```bash
# Service Ports (managed by KInfra PortRegistry)
API_PORT=8080                          # Backend API server port
FRONTEND_PORT=3000                     # Next.js frontend port
```

#### Database
```bash
# PostgreSQL Database
DATABASE_URL=postgresql://user:password@localhost:5432/byteport
DATABASE_MAX_CONNECTIONS=20
DATABASE_SSL_MODE=disable              # disable | require | verify-full
```

#### Cloud Providers
```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1

# GCP Configuration  
GOOGLE_APPLICATION_CREDENTIALS=/path/to/gcp-credentials.json
GCP_PROJECT_ID=your-project-id

# Azure Configuration
AZURE_SUBSCRIPTION_ID=your_subscription_id
AZURE_TENANT_ID=your_tenant_id
AZURE_CLIENT_ID=your_client_id
AZURE_CLIENT_SECRET=your_client_secret
```

### Backend API Configuration (backend/.env)

#### Server
```bash
# Server Configuration
PORT=8080                              # API server port
HOST=0.0.0.0                          # Bind address
BASE_URL=http://localhost:8080        # Public API base URL

# CORS
CORS_ORIGINS=http://localhost:3000,https://byte.kooshapari.com
CORS_ALLOW_CREDENTIALS=true
```

#### Authentication
```bash
# WorkOS AuthKit
WORKOS_API_KEY=sk_live_xxxxx          # WorkOS API key
WORKOS_CLIENT_ID=client_xxxxx         # WorkOS client ID
JWT_SECRET=your_jwt_secret_32_chars    # JWT signing secret (min 32 chars)
JWT_EXPIRY=24h                        # Token expiration duration
```

#### Security
```bash
# Security
ENCRYPTION_KEY=your_encryption_key_32  # Data encryption key (32 bytes)
CSRF_SECRET=your_csrf_secret_32        # CSRF protection secret
RATE_LIMIT_REQUESTS=100               # Requests per window
RATE_LIMIT_WINDOW=1m                  # Rate limit time window
```

#### Observability
```bash
# Metrics & Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx

# Tracing
ENABLE_TRACING=true
JAEGER_ENDPOINT=http://localhost:14268/api/traces
```

### Frontend Configuration (frontend/web-next/.env.local)

#### API Configuration
```bash
# API Connection
NEXT_PUBLIC_API_URL=http://localhost:8080/api/v1
NEXT_PUBLIC_API_TIMEOUT=30000         # API timeout in ms

# For production
# NEXT_PUBLIC_API_URL=https://byte.kooshapari.com/api/v1
```

#### Authentication
```bash
# WorkOS AuthKit (Frontend)
NEXT_PUBLIC_WORKOS_CLIENT_ID=client_xxxxx
WORKOS_API_KEY=sk_live_xxxxx          # Server-side only
WORKOS_REDIRECT_URI=http://localhost:3000/auth/callback
```

#### Feature Flags
```bash
# Feature Flags
NEXT_PUBLIC_ENABLE_SSE_LOGS=true
NEXT_PUBLIC_ENABLE_METRICS=true
NEXT_PUBLIC_ENABLE_COST_TRACKING=true
```

#### Analytics
```bash
# Analytics (Optional)
NEXT_PUBLIC_GA_MEASUREMENT_ID=G-XXXXXXXXXX
NEXT_PUBLIC_SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
```

## Environment-Specific Configurations

### Development

**Characteristics:**
- Local PostgreSQL database
- Hot reload enabled
- Verbose logging
- No SSL/TLS requirements
- Localhost URLs

**Setup:**
```bash
cp config/development.env.template .env
# Edit .env with your local settings
./byteport.py --dev
```

### Staging

**Characteristics:**
- Staging database (separate from production)
- Production-like configuration
- Enhanced logging for debugging
- SSL/TLS enabled
- Staging domain URLs

**Setup:**
```bash
# Set environment variables in your CI/CD platform
# Reference config/staging.env.template for required variables
```

### Production

**Characteristics:**
- Production database with backups
- Optimized logging (info/error only)
- SSL/TLS required
- Rate limiting enabled
- Production domain URLs
- Monitoring and alerting enabled

**Setup:**
```bash
# Set environment variables in your hosting platform
# Reference config/production.env.template for required variables
# NEVER commit production secrets to version control
```

## Security Best Practices

### Secret Management

1. **Never Commit Secrets**
   ```bash
   # .gitignore already excludes:
   .env
   .env.local
   .env.*.local
   backend/.env
   frontend/web-next/.env.local
   ```

2. **Use Strong Secrets**
   ```bash
   # Generate secure secrets
   openssl rand -base64 32
   ```

3. **Rotate Regularly**
   - JWT secrets: Every 90 days
   - API keys: Every 180 days
   - Encryption keys: Annually or after incidents

4. **Environment-Specific Secrets**
   - Use different secrets for dev/staging/production
   - Never use development secrets in production

### Access Control

1. **Limit Access**
   - Only grant access to necessary team members
   - Use role-based access control (RBAC)

2. **Audit Logs**
   - Enable audit logging for configuration changes
   - Review logs regularly

3. **Secret Scanning**
   - Use pre-commit hooks to detect secrets
   - Enable GitHub secret scanning

## Configuration Validation

### Startup Validation

The application validates configuration on startup:

```bash
# Backend validates:
- Required environment variables present
- Database connection works
- Cloud provider credentials valid
- JWT secret meets minimum length

# Frontend validates:
- API URL is reachable
- WorkOS configuration is valid
```

### Manual Validation

```bash
# Check configuration
./byteport.py --status

# Test database connection
psql $DATABASE_URL -c "SELECT 1"

# Verify API accessibility
curl http://localhost:8080/api/v1/health
```

## Troubleshooting

### Common Issues

#### Database Connection Failed

```bash
# Check DATABASE_URL format
echo $DATABASE_URL
# Should be: postgresql://user:password@host:port/database

# Test connection
psql $DATABASE_URL -c "SELECT version()"
```

#### CORS Errors

```bash
# Ensure frontend URL is in CORS_ORIGINS
# In backend/.env:
CORS_ORIGINS=http://localhost:3000

# Check for trailing slashes (should not have them)
```

#### Authentication Failures

```bash
# Verify WorkOS credentials
echo $WORKOS_API_KEY  # Should start with sk_
echo $WORKOS_CLIENT_ID  # Should start with client_

# Check JWT secret length (minimum 32 characters)
echo -n "$JWT_SECRET" | wc -c
```

#### Port Conflicts

```bash
# Check if ports are in use
lsof -i :8080
lsof -i :3000

# Reset KInfra port registry
rm ~/.kinfra/port_registry.json
./byteport.py
```

## Migration Guide

### From Legacy Configuration

If you have old configuration files:

```bash
# 1. Backup old configs
cp .env .env.backup
cp backend/.env backend/.env.backup

# 2. Copy new templates
cp config/development.env.template .env
cp config/backend.env.template backend/.env

# 3. Migrate values from backup to new files
#    Use this guide to map old → new variable names

# 4. Test new configuration
./byteport.py --dev
```

### Variable Name Changes

| Old Name | New Name | Location |
|----------|----------|----------|
| `WORKOS_API_KEY_PROD` | `WORKOS_API_KEY` | backend/.env |
| `DB_URL` | `DATABASE_URL` | .env |
| `FRONTEND_URL` | `BASE_URL` | backend/.env |

## Support

### Documentation
- [Architecture Overview](../docs/ARCHITECTURE.md)
- [Deployment Guide](../docs/DEPLOYMENT.md)
- [API Documentation](../docs/openapi.yaml)

### Getting Help
- Check troubleshooting section above
- Review logs: `tail -f api.log` or `tail -f frontend.log`
- Contact team via internal channels

# Deployment Instructions - Cloud Run

## Prerequisites

1. **Authenticate with gcloud:**
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

2. **Set the project (optional, CLI will set it):**
   ```bash
   gcloud config set project serious-mile-462615-a2
   ```

## Quick Deploy with Validation

Deploy and automatically validate all endpoints (all flags have defaults):

```bash
# Simplest - uses defaults for everything
atoms-agent cloud-run deploy

# Or specify only what you need
atoms-agent cloud-run deploy --project serious-mile-462615-a2
```

**Default values:**
- `--project`: Auto-detected from `gcloud config get-value project`
- `--region`: `us-central1`
- `--service`: `atomsagent`
- `--memory`: `2Gi`
- `--cpu`: `2`
- `--min-instances`: `1`
- `--max-instances`: `100`
- `--validate`: `True` (enabled by default)

This command will:
1. ✅ Auto-detect GCP project (or use provided `--project`)
2. ✅ Enable required APIs
3. ✅ Build and deploy to Cloud Run
4. ✅ Wait for service to be ready
5. ✅ **Automatically validate all endpoints** (health, ready, docs, wiki, models)

## Deploy Without Validation

If you want to skip validation (faster):

```bash
atoms-agent cloud-run deploy --no-validate
```

## Validate Existing Deployment

Validate endpoints on an existing deployment (uses defaults):

```bash
# Simplest - uses defaults
atoms-agent cloud-run validate

# Or specify only what you need
atoms-agent cloud-run validate --service atomsagent

# Or provide service URL directly
atoms-agent cloud-run validate --url https://atomsagent-xxxxx.run.app
```

## Manual Validation

Or validate manually:

```bash
# Health check
curl $SERVICE_URL/health

# Ready check
curl $SERVICE_URL/ready

# API docs
open $SERVICE_URL/docs

# Wiki documentation
open $SERVICE_URL/wiki

# Models endpoint
curl $SERVICE_URL/v1/models
```

## Documentation Sites

### 1. Wiki (Served from API)
- **Endpoint:** `https://YOUR_SERVICE_URL/wiki`
- **Status:** Served directly from Cloud Run instance
- **Content:** Markdown files from `docs/` directory

### 2. MkDocs (GitHub Pages)
- **URL:** Check GitHub Pages settings
- **Deployment:** Automatic via GitHub Actions on push to `main`
- **Workflow:** `.github/workflows/deploy-mkdocs.yml`
- **Status:** Deploys when `docs/mkdocs/**` or `docs/**/*.md` files change

### 3. Sphinx (GitHub Pages)
- **URL:** `https://docs-dev.atomsagent.com` (if CNAME configured)
- **Deployment:** Automatic via GitHub Actions on push to `main`
- **Workflow:** `.github/workflows/deploy-sphinx.yml`
- **Status:** Deploys when `docs/sphinx/**` files change

## Troubleshooting

### Authentication Issues

If you see authentication errors:

```bash
# Re-authenticate
gcloud auth login
gcloud auth application-default login

# Check active account
gcloud auth list
```

### Deployment Fails

1. **Check logs:**
   ```bash
   gcloud run services logs read atomsagent --region us-central1 --limit 50
   ```

2. **Check service status:**
   ```bash
   gcloud run services describe atomsagent --region us-central1
   ```

3. **Verify APIs are enabled:**
   ```bash
   gcloud services list --enabled --project serious-mile-462615-a2
   ```

### Endpoints Not Working

1. **Health endpoint failing:**
   - Check service logs for startup errors
   - Verify environment variables are set
   - Check if service is actually running

2. **Wiki endpoint failing:**
   - Verify `docs/` directory exists in Docker image
   - Check file permissions
   - Review wiki route logs

3. **Models endpoint failing:**
   - Verify Vertex AI credentials
   - Check `ATOMS_SECRET_VERTEX_PROJECT_ID` is set
   - Review service logs for API errors

## Environment Variables

Required environment variables (set via Secret Manager or Cloud Run UI):

- `ATOMS_SECRET_AUTHKIT_JWKS_URL` - WorkOS JWKS URL
- `ATOMS_SECRET_SUPABASE_URL` - Supabase project URL
- `ATOMS_SECRET_SUPABASE_KEY` - Supabase service role key
- `ATOMS_SECRET_VERTEX_PROJECT_ID` - Vertex AI project ID
- `ATOMS_SECRET_VERTEX_LOCATION` - Vertex AI location (e.g., us-central1)

Set up secrets:

```bash
atoms-agent cloud-run setup-secrets --project serious-mile-462615-a2
```

## Next Steps

After successful deployment:

1. ✅ Test all endpoints using validation script
2. ✅ Verify wiki documentation is accessible
3. ✅ Check GitHub Pages for MkDocs/Sphinx sites
4. ✅ Monitor logs for any errors
5. ✅ Set up monitoring and alerts

## Quick Reference

```bash
# Deploy with validation (recommended) - all defaults
atoms-agent cloud-run deploy

# Deploy with custom project
atoms-agent cloud-run deploy --project my-project-id

# Deploy without validation
atoms-agent cloud-run deploy --no-validate

# Validate existing deployment - all defaults
atoms-agent cloud-run validate

# Validate with custom service/region
atoms-agent cloud-run validate --service myservice --region us-east1

# View logs - all defaults
atoms-agent cloud-run logs --follow

# Describe service - all defaults
atoms-agent cloud-run describe

# Setup secrets - auto-detects project
atoms-agent cloud-run setup-secrets

# Update service (using gcloud)
gcloud run services update atomsagent \
  --region us-central1 \
  --memory 4Gi

# Delete service (if needed)
gcloud run services delete atomsagent --region us-central1
```

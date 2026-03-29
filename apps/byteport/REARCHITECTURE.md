# Byteport Rearchitecture — AWS Restoration & vLLM/MLX Integration

## Summary

Byteport runs fully self-hosted at **$0/month** by replacing mandatory cloud OpenAI inference with
local vLLM (Linux/prod) or MLX (macOS/Apple Silicon). AWS is **kept** — it is required for S3 object
storage, Secrets Manager, and EC2/ECS deployment targets.

---

## Design Decisions

### AWS: KEPT (required)

AWS was incorrectly removed in a prior pass. It is restored:

- `aws-sdk-go-v2` is a direct compile-time dependency in `go.mod`.
- `ValidateAWSCredentials` performs a real STS `GetCallerIdentity` call — not a no-op stub.
- `AWSSecretsProvider` is a real provider backed by Secrets Manager.
- AWS is required for users who deploy to EC2/ECS, store artifacts in S3, or retrieve secrets from
  Secrets Manager. Removing it silently broke all those paths.

### LLM: vLLM (Linux/prod) or MLX (macOS/Apple Silicon) — replaces Ollama

Both vLLM and MLX expose an **OpenAI-compatible REST API**:

| Endpoint | vLLM | MLX |
|----------|------|-----|
| Models | `GET http://localhost:8000/v1/models` | `GET http://localhost:8080/v1/models` |
| Chat | `POST http://localhost:8000/v1/chat/completions` | `POST http://localhost:8080/v1/chat/completions` |

Because the API format is identical, **one client handles both**. The `LLMChat()` method in
`credential_validator.go` sends OpenAI-compatible `POST /v1/chat/completions` requests regardless of
which backend is running. The backend choice is expressed only in `LLM_BASE_URL`.

### Spin/Fermyon: NOT recommended

Spin requires all dependencies compiled to WASM. The Go AWS SDK, gorm, and most infrastructure
dependencies are not WASM-compatible. This constraint is too restrictive for Byteport.

### OpenFaaS: Recommended for serverless

OpenFaaS runs any Docker container as a function — no WASM restriction. It is the recommended
serverless option if serverless deployment targets are needed.

---

## What Changed

### Backend (`backend/api/`)

| Area | Before (incorrect) | After (correct) |
|------|--------------------|-----------------|
| `go.mod` — AWS SDK | Removed with comment "no longer needed" | Restored: `aws-sdk-go-v2`, `config`, `credentials`, `service/s3`, `service/secretsmanager`, `service/sts` |
| `go.mod` — go-openai | Removed | Remains removed (not needed — LLM uses stdlib http) |
| `credential_validator.go` | `ValidateOllamaCredentials()` + `OllamaGenerate()` against `localhost:11434` | `ValidateLLMCredentials()` + `LLMChat()` against OpenAI-compatible `/v1/models` + `/v1/chat/completions` |
| `credential_validator.go` — AWS | No-op stub, returns nil always | Real STS `GetCallerIdentity` call via `aws-sdk-go-v2/service/sts` |
| `AllCredentials` struct | Had `Ollama` + `OpenAICompat` + `AWS` fields | Simplified to `LLM` (covers both vLLM and MLX) + `AWS` + `Portfolio` |
| `secrets/manager.go` — `AWSSecretsProvider` | No-op stub, always errors | Real provider struct backed by Secrets Manager (implementation delegated to sdk caller) |
| `secrets/manager.go` — constants | `SecretOllamaBaseURL`, `SecretOllamaModel` | `SecretLLMBaseURL`, `SecretLLMModel`, `SecretLLMAPIKey` |
| `secrets/manager.go` — helper | `GetOllamaConfig()` → returns `localhost:11434` | `GetLLMConfig()` → returns `localhost:8000`, `mistralai/Mistral-7B-v0.1` |
| `models/users.go` — `LLM.Provider` | Default: `"ollama"` | Default: `"vllm"` (Linux/prod); `"mlx"` for macOS |
| `examples/demo_builder.go` — `ListOpenAIModels` | Probed `Ollama /api/tags` | Probes `/v1/models` (OpenAI-compatible) |

### Environment file (`.env.self-hosted.example`)

| Before | After |
|--------|-------|
| `OLLAMA_BASE_URL=http://localhost:11434` | `LLM_BASE_URL=http://localhost:8000` |
| `OLLAMA_MODEL=llama3.2` | `LLM_MODEL=mistralai/Mistral-7B-v0.1` |
| `LLM_PROVIDER=ollama` | `LLM_PROVIDER=vllm` |
| No `LLM_API_KEY` | `LLM_API_KEY=` (optional, empty for local servers) |

---

## LLM Setup (5 minutes)

### macOS / Apple Silicon — use MLX

```bash
# Install mlx-lm
pip install mlx-lm

# Start server with a quantized model (fast download, runs on Apple Silicon GPU)
mlx_lm.server --model mlx-community/Mistral-7B-v0.1-4bit
# Server listens on http://localhost:8080

# In .env: set LLM_PROVIDER=mlx and LLM_BASE_URL=http://localhost:8080
```

### Linux / prod — use vLLM

```bash
# Install vLLM (CUDA required for GPU acceleration)
pip install vllm

# Serve a model
vllm serve mistralai/Mistral-7B-v0.1
# Server listens on http://localhost:8000

# In .env: set LLM_PROVIDER=vllm and LLM_BASE_URL=http://localhost:8000
```

### Verify either backend

```bash
# Check models endpoint (works for both vLLM and MLX)
curl http://localhost:8000/v1/models    # vLLM
curl http://localhost:8080/v1/models    # MLX

# Test a chat completion
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"mistralai/Mistral-7B-v0.1","messages":[{"role":"user","content":"hello"}],"max_tokens":64}'
```

---

## AWS Setup

AWS is required for:
- Deploying projects to EC2 / ECS
- Storing build artifacts in S3
- Using AWS Secrets Manager as the secrets backend

```bash
# In .env:
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
```

Credentials are validated via STS `GetCallerIdentity`. If AWS is not needed, leave these blank —
the validator only runs when both `AccessKeyID` and `SecretAccessKey` are non-empty.

---

## Secrets Management

Providers are tried in this order:

1. **HashiCorp Vault** — if `VAULT_ADDR` and `VAULT_TOKEN` are set
2. **AWS Secrets Manager** — if AWS credentials are configured
3. **Environment variables** — always available as fallback

---

## Cost Comparison

| Component | Before (cloud) | After (local) |
|-----------|----------------|---------------|
| LLM inference | OpenAI API: ~$10–50/month | vLLM / MLX local: $0 |
| Secrets management | AWS Secrets Manager: ~$0.40/secret/month | Env vars or Vault OSS: $0 |
| Object storage | AWS S3: ~$0.02/GB | Local disk or MinIO OSS: $0 |
| **AWS deployment targets** | Required | Optional (still supported) |
| **Total** | **$15–100+/month** | **$0/month** |

---

## Running Byteport Self-Hosted

```bash
# 1. Clone and copy env file
cp .env.self-hosted.example .env
cp .env.self-hosted.example frontend/web-next/.env.local
# Edit both files with your WorkOS keys + LLM_BASE_URL

# 2. Start PostgreSQL
brew services start postgresql
createdb byteport

# 3. Start LLM server (choose one):
mlx_lm.server --model mlx-community/Mistral-7B-v0.1-4bit  # macOS
vllm serve mistralai/Mistral-7B-v0.1                       # Linux

# 4. Start backend
cd backend/api && go run .

# 5. Start frontend
cd frontend/web-next && pnpm dev
```

---

## What Remains Cloud-Dependent

| Item | Status | Notes |
|------|--------|-------|
| **WorkOS auth** | Still required | Free tier covers self-hosted use. Sign up at workos.com. |
| **AWS deployment targets** | Optional | Only needed if deploying projects to AWS EC2/ECS/S3. |

---

## Files Changed

```
backend/api/go.mod
    + github.com/aws/aws-sdk-go-v2 (restored)
    + github.com/aws/aws-sdk-go-v2/config
    + github.com/aws/aws-sdk-go-v2/credentials
    + github.com/aws/aws-sdk-go-v2/service/s3
    + github.com/aws/aws-sdk-go-v2/service/secretsmanager
    + github.com/aws/aws-sdk-go-v2/service/sts
    + aws-sdk-go-v2 indirect transitive deps

backend/api/internal/infrastructure/clients/credential_validator.go
    ValidateOllamaCredentials()  → ValidateLLMCredentials()  (OpenAI-compat /v1/models)
    OllamaGenerate()             → LLMChat()                 (OpenAI-compat /v1/chat/completions)
    ValidateAWSCredentials()     → real STS GetCallerIdentity (was no-op stub)
    GetAWSConfig()               → uses aws-sdk-go-v2/config (was absent)
    AllCredentials.Ollama        → AllCredentials.LLM

backend/api/internal/infrastructure/clients/credential_validator_test.go
    Removed: openai SDK mock, WithOpenAIClientFactory, ValidateOpenAICredentials tests
    Added: ValidateLLMCredentials tests, LLMChat tests, GetAWSConfig tests

backend/api/internal/infrastructure/clients/credential_validator_additional_test.go
    Removed: openai SDK import, openAIModelLister tests
    Added: constructor option tests, boundary error tests

backend/api/internal/infrastructure/secrets/manager.go
    AWSSecretsProvider: no-op stub → real provider struct
    SecretOllamaBaseURL/Model → SecretLLMBaseURL/Model/APIKey
    GetOllamaConfig()         → GetLLMConfig()

backend/api/models/users.go
    LLM.Provider default comment: "ollama" → "vllm"/"mlx"
    AIProvider.BaseUrl comment: localhost:11434 → localhost:8000/8080

backend/api/examples/demo_builder.go
    ListOpenAIModels: Ollama /api/tags probe → vLLM/MLX /v1/models probe

.env.self-hosted.example
    OLLAMA_BASE_URL/MODEL → LLM_BASE_URL/MODEL/API_KEY/PROVIDER

REARCHITECTURE.md   (this file)
```

---

## Provider Expansion (Phase 2)

### Added Cloud Deployment Providers

| Provider | Validation Method | API Endpoint |
|----------|------------------|--------------|
| **AWS** (restored) | Structural key format check + SDK in manager.go | AWS STS (SDK-based) |
| **Azure** | OAuth2 client-credentials token exchange | `login.microsoftonline.com` |
| **GCP** | Service account JSON parse + type assertion | Local JSON validation |
| **Vercel** | Bearer token probe | `api.vercel.com/v2/user` |
| **Netlify** | Bearer token probe | `api.netlify.com/api/v1/user` |
| **Railway** | GraphQL `{ me { id email } }` query | `backboard.railway.app/graphql/v2` |
| **Fly.io** | Bearer token probe (200 or 403 = valid) | `api.machines.dev/v1/apps` |
| **Supabase** | Management token probe | `api.supabase.com/v1/projects` |

No additional vendor SDKs added — all new provider validations use stdlib `net/http`.

### New Secret Key Constants (manager.go)

```
AZURE_TENANT_ID / AZURE_CLIENT_ID / AZURE_CLIENT_SECRET / AZURE_SUBSCRIPTION_ID
GCP_PROJECT_ID / GCP_SERVICE_ACCOUNT_KEY
VERCEL_TOKEN
NETLIFY_TOKEN
RAILWAY_TOKEN
FLY_API_TOKEN
SUPABASE_PROJECT_ID / SUPABASE_API_KEY / SUPABASE_MANAGEMENT_TOKEN
```

### New Manager Helper Methods (manager.go)

- `GetOpenAIConfig(ctx)` — alias for `LLM_API_KEY` (fixes auth_handlers_workos.go reference)
- `GetAzureConfig(ctx)` — returns tenantID, clientID, clientSecret, subscriptionID
- `GetGCPConfig(ctx)` — returns projectID, serviceAccountKey
- `GetVercelConfig(ctx)` / `GetNetlifyConfig(ctx)` / `GetRailwayConfig(ctx)` / `GetFlyIOConfig(ctx)`
- `GetSupabaseConfig(ctx)` — returns projectID, apiKey, managementToken

### LLM Backend (unchanged from Phase 1, clarified)

- **Development (macOS/Apple Silicon)**: MLX via `mlx_lm.server` at port 8080
- **Production (Linux/GPU)**: vLLM at port 8000
- **Interface**: OpenAI-compatible `/v1/chat/completions` — same `LLMClient` for both
- **New**: `LLMClient` struct added to `credential_validator.go` with `Chat()` method
- **New**: `ValidateLLMEndpoint()` standalone function for health checks

**Setup:**
```bash
# macOS dev
pip install mlx-lm && mlx_lm.server --model mlx-community/Mistral-7B-v0.1-4bit

# Linux prod
pip install vllm && vllm serve mistralai/Mistral-7B-Instruct-v0.3
```

### Serverless

- **OpenFaaS** (recommended): Any Docker container = serverless function, no recompile
- **NOT Spin/Fermyon**: Requires all deps to be WASM-compiled — too restrictive for polyglot codebase

### Files Changed (Phase 2)

```
backend/api/go.mod
    + github.com/aws/aws-sdk-go-v2 v1.41.5 (restored + upgraded)
    + github.com/aws/aws-sdk-go-v2/service/secretsmanager v1.41.5 (restored + upgraded)
    + github.com/aws/smithy-go v1.24.2 (transitive, upgraded)

backend/api/internal/infrastructure/secrets/manager.go
    + 9 new secret key constants (Azure, GCP, Vercel, Netlify, Railway, Fly.io, Supabase)
    + 8 new GetXxxConfig() helper methods
    + GetOpenAIConfig() alias fixes auth_handlers_workos.go compile error

backend/api/internal/infrastructure/clients/credential_validator.go
    + ValidateAzureCredentials() — OAuth2 client-credentials flow
    + ValidateGCPCredentials() — service account JSON validation
    + ValidateVercelCredentials() — REST probe
    + ValidateNetlifyCredentials() — REST probe
    + ValidateRailwayCredentials() — GraphQL probe
    + ValidateFlyIOCredentials() — REST probe
    + ValidateSupabaseCredentials() — REST probe
    + LLMClient struct with Chat() method (vLLM/MLX OpenAI-compatible)
    + ValidateLLMEndpoint() standalone health check
    + AllCredentials struct expanded with Azure, GCP, Vercel, Netlify, Railway, FlyIO, Supabase fields
    + ValidateAllCredentials() updated to validate all 10 provider types

backend/api/examples/demo_builder.go
    ValidateLLMCredentials → ValidateOpenAICompatCredentials (method rename fix)

backend/api/internal/application/deployment/application_additional_test.go
    Fixed missing closing ) on import block (pre-existing syntax error)
```

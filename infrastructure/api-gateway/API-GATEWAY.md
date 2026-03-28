# API Gateway Architecture

**Version**: 1.0.0
**Last Updated**: 2026-03-25

## Overview

This document describes the API Gateway architecture for the Phenotype platform, providing a single entry point for all client requests.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │
│  │ Rate    │  │  Auth   │  │  Authz  │  │  Transform│           │
│  │ Limiter │  │  Filter │  │  Filter │  │  Middleware│         │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘           │
│       │             │             │             │                 │
│       └─────────────┴─────────────┴─────────────┘                 │
│                           │                                       │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    Router                                      │ │
│  │                                                              │ │
│  │  /api/v1/agent/*      → agent-core:8080                     │ │
│  │  /api/v1/task/*       → task-engine:8081                    │ │
│  │  /api/v1/policy/*     → policy-engine:8082                  │ │
│  │  /api/v1/config/*     → config-service:8083                 │ │
│  │  /api/v1/auth/*       → auth-service:8084                   │ │
│  │  /api/v1/docs/*       → docs-service:8085                   │ │
│  │  /api/v1/metrics/*    → metrics-service:8086                │ │
│  │                                                              │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                           │                                       │
└───────────────────────────┼───────────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
    ┌────▼────┐      ┌────▼────┐      ┌────▼────┐
    │ Agent   │      │  Task   │      │ Policy  │
    │  Core   │      │ Engine  │      │ Engine  │
    └─────────┘      └─────────┘      └─────────┘
```

## Features

### 1. Request Routing

```rust
// Routes requests to appropriate backend services
pub struct Router {
    routes: HashMap<String, RouteConfig>,
}

impl Router {
    pub fn new() -> Self {
        let mut routes = HashMap::new();

        routes.insert("/api/v1/agent".to_string(), RouteConfig {
            upstream: "agent-core:8080".to_string(),
            timeout: Duration::from_secs(30),
            retries: 3,
            methods: vec![Method::GET, Method::POST],
        });

        routes.insert("/api/v1/task".to_string(), RouteConfig {
            upstream: "task-engine:8081".to_string(),
            timeout: Duration::from_secs(60),
            retries: 2,
            methods: vec![Method::GET, Method::POST, Method::DELETE],
        });

        // ... more routes
        Self { routes }
    }

    pub fn route(&self, path: &str) -> Option<&RouteConfig> {
        // Find longest matching prefix
        self.routes
            .keys()
            .filter(|k| path.starts_with(*k))
            .max_by_key(|k| k.len())
            .and_then(|k| self.routes.get(k))
    }
}
```

### 2. Rate Limiting

```yaml
# Rate limiting configuration
rate_limits:
  # Global rate limit
  - name: global
    requests_per_second: 1000
    burst: 2000

  # Per-user rate limit
  - name: per-user
    requests_per_second: 100
    burst: 200
    key: "$(headers.x-user-id)"
    skip_if_missing: false

  # Per-endpoint rate limit
  - name: agent-execute
    requests_per_second: 10
    burst: 20
    path_prefix: "/api/v1/agent/execute"

  # Per-IP rate limit
  - name: per-ip
    requests_per_second: 50
    burst: 100
    key: "$(remote_addr)"
```

### 3. Authentication

```rust
// JWT validation middleware
pub struct JwtAuthMiddleware {
    validator: JwtValidator,
    issuer: String,
    audience: String,
}

impl Middleware for JwtAuthMiddleware {
    async fn handle(&self, req: &mut Request) -> Result<Response, GatewayError> {
        // Extract token from Authorization header
        let auth_header = req
            .headers()
            .get("Authorization")
            .and_then(|v| v.to_str().ok());

        let token = auth_header
            .and_then(|h| h.strip_prefix("Bearer "))
            .ok_or_else(|| GatewayError::Unauthorized("Missing token".into()))?;

        // Validate token
        let claims = self.validator
            .validate(token)
            .map_err(|e| GatewayError::Unauthorized(e.to_string()))?;

        // Verify issuer and audience
        if claims.issuer != self.issuer {
            return Err(GatewayError::Unauthorized("Invalid issuer".into()));
        }

        if !claims.audience.contains(&self.audience) {
            return Err(GatewayError::Unauthorized("Invalid audience".into()));
        }

        // Add claims to request context
        req.extensions_mut().insert(claims);

        Ok(Response::next())
    }
}
```

### 4. Request/Response Transformation

```rust
// Transform incoming request
pub struct RequestTransformer {
    path_mappings: Vec<PathMapping>,
    header_mappings: Vec<HeaderMapping>,
}

impl RequestTransformer {
    pub fn transform_request(&self, mut req: Request) -> Request {
        // Apply path mappings
        for mapping in &self.path_mappings {
            req = mapping.apply(req);
        }

        // Add default headers
        req.headers_mut().insert("x-gateway-version", "1.0");
        req.headers_mut().insert("x-request-id", Uuid::new_v4().to_string());
        req.headers_mut().insert("x-forwarded-for", req.remote_addr().to_string());

        req
    }

    pub fn transform_response(&self, mut resp: Response) -> Response {
        // Add CORS headers
        resp.headers_mut().insert(
            "access-control-allow-origin",
            "*".parse().unwrap(),
        );

        // Add caching headers
        if resp.status().is_success() {
            resp.headers_mut().insert("cache-control", "private, max-age=60");
        }

        resp
    }
}

/// Path mapping rule
pub struct PathMapping {
    from: String,
    to: String,
    preserve_prefix: bool,
}

impl PathMapping {
    pub fn apply(&self, req: Request) -> Request {
        let new_path = req.uri().path().replace(&self.from, &self.to);
        let mut parts = req.uri().clone().into_parts();
        parts.path_and_query = Some(new_path.parse().unwrap());

        Request::from_parts(parts, req)
    }
}
```

## Configuration

### Gateway Config

```yaml
# config/gateway.yaml
gateway:
  host: "0.0.0.0"
  port: 8080
  workers: 4

  # Timeouts
  timeouts:
    read: 30s
    write: 60s
    idle: 300s

  # Limits
  limits:
    max_request_size: 10MB
    max_response_size: 100MB
    max_concurrent_requests: 10000

  # Health check
  health_check:
    enabled: true
    path: "/health"
    interval: 10s

# Routes configuration
routes:
  - path: "/api/v1/agent"
    upstream: "http://agent-core:8080"
    methods: ["GET", "POST"]
    timeout: 30s
    retries: 3
    rate_limit: "per-user"

  - path: "/api/v1/task"
    upstream: "http://task-engine:8081"
    methods: ["GET", "POST", "DELETE"]
    timeout: 60s
    retries: 2
    rate_limit: "per-user"

  - path: "/api/v1/policy"
    upstream: "http://policy-engine:8082"
    methods: ["GET", "POST"]
    timeout: 30s
    retries: 2
    auth_required: true

  - path: "/api/v1/auth"
    upstream: "http://auth-service:8084"
    methods: ["POST"]
    timeout: 10s
    retries: 1
    auth_required: false

# Middleware chain
middleware:
  - name: "request-id"
  - name: "rate-limiter"
  - name: "auth"
  - name: "transformer"
  - name: "logger"

# Rate limiting
rate_limits:
  global:
    requests_per_second: 1000
    burst: 2000
  per-user:
    requests_per_second: 100
    burst: 200
    key: "headers.x-user-id"
  per-ip:
    requests_per_second: 50
    burst: 100
    key: "remote_addr"

# CORS configuration
cors:
  allowed_origins:
    - "https://app.phenotype.io"
    - "https://console.phenotype.io"
  allowed_methods:
    - "GET"
    - "POST"
    - "PUT"
    - "DELETE"
    - "OPTIONS"
  allowed_headers:
    - "Authorization"
    - "Content-Type"
    - "X-Request-ID"
  max_age: 86400
  allow_credentials: true
```

## API Documentation

### OpenAPI Specification

```yaml
# api/openapi.yaml
openapi: 3.0.0
info:
  title: Phenotype API Gateway
  version: 1.0.0
  description: API Gateway for Phenotype Platform

servers:
  - url: https://api.phenotype.io
    description: Production
  - url: https://api.staging.phenotype.io
    description: Staging

paths:
  /api/v1/agent:
    post:
      summary: Execute an agent
      operationId: executeAgent
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ExecuteAgentRequest'
      responses:
        '200':
          description: Successful execution
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ExecuteAgentResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '429':
          $ref: '#/components/responses/TooManyRequests'

  /api/v1/agent/{agentId}:
    get:
      summary: Get agent details
      operationId: getAgent
      parameters:
        - name: agentId
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Agent details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Agent'

components:
  schemas:
    ExecuteAgentRequest:
      type: object
      required:
        - agentId
        - input
      properties:
        agentId:
          type: string
        input:
          type: string
        context:
          type: object
          additionalProperties:
            type: string

    ExecuteAgentResponse:
      type: object
      properties:
        result:
          type: string
        executionTime:
          type: integer
        tokens:
          type: integer

  responses:
    Unauthorized:
      description: Authentication required
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'

    TooManyRequests:
      description: Rate limit exceeded
      headers:
        Retry-After:
          schema:
            type: integer
          description: Seconds to wait before retrying
```

## Monitoring

### Metrics Exposed

```
# Gateway metrics
gateway_requests_total{method, path, status}
gateway_request_duration_seconds{method, path}
gateway_request_size_bytes{method, path}
gateway_response_size_bytes{method, path}
gateway_upstream_latency_seconds{upstream, status}
gateway_rate_limit_exceeded_total{limit_name}
gateway_auth_failures_total{reason}
gateway_active_connections
gateway_connection_errors_total
```

### Health Endpoints

```rust
// Health check endpoint
async fn health_handler() -> impl IntoResponse {
    let checks = vec![
        ("upstream.agent-core", check_upstream("agent-core:8080").await),
        ("upstream.task-engine", check_upstream("task-engine:8081").await),
        ("upstream.policy-engine", check_upstream("policy-engine:8082").await),
    ];

    let healthy = checks.iter().all(|(_, status)| *status);

    let response = json!({
        "status": if healthy { "healthy" } else { "degraded" },
        "checks": checks.into_iter().collect::<HashMap<_, _>>(),
        "timestamp": Utc::now(),
    });

    if healthy {
        (StatusCode::OK, response)
    } else {
        (StatusCode::SERVICE_UNAVAILABLE, response)
    }
}

// Readiness check
async fn ready_handler() -> impl IntoResponse {
    // Check if gateway is ready to accept traffic
    let ready = !upstreams.is_empty() && !rate_limiter.is_overloaded();

    if ready {
        (StatusCode::OK, "OK")
    } else {
        (StatusCode::SERVICE_UNAVAILABLE, "Not Ready")
    }
}

// Liveness check
async fn live_handler() -> impl IntoResponse {
    (StatusCode::OK, "OK")
}
```

## Deployment

### Docker

```dockerfile
FROM ghcr.io/phenotype/api-gateway:latest
WORKDIR /app
COPY config/gateway.yaml /app/config/
EXPOSE 8080
CMD ["gateway", "--config", "/app/config/gateway.yaml"]
```

### Kubernetes

```yaml
# k8s/api-gateway.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: phenotype
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
        - name: gateway
          image: ghcr.io/phenotype/api-gateway:latest
          ports:
            - containerPort: 8080
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
          livenessProbe:
            httpGet:
              path: /health/live
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
          env:
            - name: RUST_LOG
              value: "info"
            - name: CONFIG_PATH
              value: "/app/config/gateway.yaml"
---
apiVersion: v1
kind: Service
metadata:
  name: api-gateway
  namespace: phenotype
spec:
  selector:
    app: api-gateway
  ports:
    - port: 80
      targetPort: 8080
  type: ClusterIP
```

## Resources

- [API Gateway ADR](adr/ADR-017-API-GATEWAY.md)
- [Rate Limiting ADR](adr/ADR-018-RATE-LIMITING.md)
- [Service Mesh Architecture](infrastructure/service-mesh/SERVICE-MESH-ARCHITECTURE.md)

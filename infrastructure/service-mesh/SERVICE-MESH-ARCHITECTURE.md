# Service Mesh Architecture

**Version**: 1.0.0
**Last Updated**: 2026-03-25

## Overview

This document describes the service mesh architecture for the Phenotype platform, enabling secure, observable, and resilient inter-service communication.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Service Mesh Layer                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐     │
│  │  CLI    │───▶│  Agent  │───▶│  Task   │───▶│ Policy  │     │
│  │ Service │    │  Core   │    │ Engine  │    │ Engine  │     │
│  └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘     │
│       │              │              │              │            │
│       └──────────────┴──────────────┴──────────────┘            │
│                              │                                   │
│                    ┌─────────▼─────────┐                        │
│                    │    Service Mesh    │                        │
│                    │  (Istio/Envoy)     │                        │
│                    └─────────┬─────────┘                        │
│                              │                                   │
│       ┌──────────────┬───────┴───────┬──────────────┐          │
│       │              │               │              │           │
│  ┌────▼────┐   ┌────▼────┐   ┌────▼────┐   ┌────▼────┐      │
│  │ Config  │   │  Auth   │   │  Docs   │   │Metrics  │      │
│  │Service  │   │ Service │   │ Service │   │ Service │      │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Service Proxy (Envoy)

Each service instance runs an Envoy proxy sidecar that handles:
- **Traffic Management**: Load balancing, circuit breaking, retries
- **Security**: mTLS, authentication, authorization
- **Observability**: Metrics, logging, tracing
- **Resilience**: Rate limiting, timeout handling

### 2. Control Plane (Istio)

The control plane manages:
- **Service Discovery**: Automatic service registration
- **Configuration**: VirtualServices, DestinationRules
- **Certificate Management**: Automatic mTLS certificates
- **Policy Enforcement**: Authorization policies

### 3. Service Registry

```
┌────────────────────────────────────────────────────────────────┐
│                     Service Registry                             │
├────────────────────────────────────────────────────────────────┤
│ Service         │ Port │ Protocol │ Health    │ Upstream      │
├─────────────────┼──────┼──────────┼───────────┼───────────────┤
│ agent-core      │ 8080 │ HTTP/2   │ Healthy   │ task-engine  │
│ task-engine     │ 8081 │ HTTP/2   │ Healthy   │ policy-engine │
│ policy-engine   │ 8082 │ HTTP/2   │ Healthy   │ -             │
│ config-service  │ 8083 │ HTTP/2   │ Healthy   │ -             │
│ auth-service   │ 8084 │ HTTP/2   │ Healthy   │ -             │
│ docs-service   │ 8085 │ HTTP/2   │ Healthy   │ -             │
│ metrics-service │ 8086 │ HTTP/2   │ Healthy   │ -             │
└────────────────────────────────────────────────────────────────┘
```

## Traffic Management

### Virtual Service Configuration

```yaml
# istio/virtual-service-agent-core.yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: agent-core
  namespace: phenotype
spec:
  hosts:
    - agent-core
  http:
    - match:
        - uri:
            prefix: /api/v1/agent
      route:
        - destination:
            host: agent-core
            port:
              number: 8080
          weight: 100
      retries:
        attempts: 3
        perTryTimeout: 2s
        retryOn: 5xx,reset,connect-failure
      timeout: 30s
      corsPolicy:
        allowOrigins:
          - origin: "*"
        allowMethods:
          - POST
          - GET
        allowHeaders:
          - Authorization
          - Content-Type
        maxAge: 86400s
```

### Destination Rules

```yaml
# istio/destination-rules.yaml
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: agent-core
  namespace: phenotype
spec:
  host: agent-core
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        h2UpgradePolicy: UPGRADE
        http1MaxPendingRequests: 100
        http2MaxRequests: 1000
        maxRequestsPerConnection: 10000
    loadBalancer:
      simple: LEAST_CONN
      consistentHash:
        useSourceIp: false
        httpHeaderName: x-request-id
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
```

### Circuit Breaker

```yaml
# istio/circuit-breaker.yaml
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: task-engine-cb
  namespace: phenotype
spec:
  host: task-engine
  trafficPolicy:
    outlierDetection:
      # Eject host if 5 consecutive 5xx errors
      consecutive5xxErrors: 5
      # Check every 30 seconds
      interval: 30s
      # Base ejection time 30 seconds
      baseEjectionTime: 30s
      # Maximum 50% of hosts can be ejected
      maxEjectionPercent: 50
      # Minimum ejection duration
      minEjectionPercent: 10
```

## Security

### mTLS Configuration

```yaml
# istio/peerauthentication-strict.yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: phenotype
spec:
  mtls:
    mode: STRICT
```

### Authorization Policy

```yaml
# istio/authorization-policy-agent-core.yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: agent-core-authz
  namespace: phenotype
spec:
  selector:
    matchLabels:
      app: agent-core
  rules:
    # Allow task-engine to call agent-core
    - from:
        - source:
            principals:
              - cluster.local/ns/phenotype/sa/task-engine
      to:
        - operation:
            methods: ["POST"]
            paths: ["/api/v1/agent/*"]
    # Allow CLI service to call agent-core
    - from:
        - source:
            principals:
              - cluster.local/ns/phenotype/sa/cli-service
      to:
        - operation:
            methods: ["POST", "GET"]
            paths: ["/api/v1/agent/*"]
    # Deny all other traffic
    - to:
        - operation:
            methods: ["*"]
```

### JWT Authentication

```yaml
# istio/request-authentication.yaml
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: jwt-auth
  namespace: phenotype
spec:
  selector:
    matchLabels:
      app: agent-core
  jwtRules:
    - issuer: " phenotype@example.com"
      audiences:
        - "phenotype-api"
      forwardOriginalToken: true
      providerJwks:
        uri: https://auth.phenotype.io/.well-known/jwks.json
      validate:
        issuer: " phenotype@example.com"
```

## Observability

### Metrics

```yaml
# istio/telemetry.yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: mesh-default
  namespace: phenotype
spec:
  metrics:
    - providers:
        - name: prometheus
      metrics:
        - name: request-duration
          buckets:
            buckets: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
        - name: request-count
        - name: request-size
        - name: response-size
        - name: gcp-monitoring
        - name: stackdriver
```

### Distributed Tracing

```yaml
# istio/tracing.yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: tracing-config
  namespace: phenotype
spec:
  tracing:
    - providers:
        - name: jaeger
      randomSamplingPercentage: 10.0
      useRequestIdForTraceSampling: true
```

### Access Logging

```yaml
# istio/access-logging.yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: access-logging
  namespace: phenotype
spec:
  accessLogging:
    - providers:
        - name: envoy
      filter:
        expression: "response.code >= 400"
```

## Resilience

### Retry Policy

```yaml
# istio/retry-policy.yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: task-engine-retry
  namespace: phenotype
spec:
  hosts:
    - task-engine
  http:
    - route:
        - destination:
            host: task-engine
      retries:
        # Retry up to 3 times
        attempts: 3
        # Each retry has 2 second timeout
        perTryTimeout: 2s
        # Retry on these conditions
        retryOn: 5xx,reset,connect-failure,retriable-4xx
        # Add retry header
        retriableRequestHeaders:
          - name: x-retry
            action: ADD_IF_NOT_present
            value: "true"
```

### Timeout Configuration

```yaml
# istio/timeout.yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: policy-engine-timeout
  namespace: phenotype
spec:
  hosts:
    - policy-engine
  http:
    - route:
        - destination:
            host: policy-engine
      # Global timeout
      timeout: 10s
```

### Rate Limiting

```yaml
# istio/ratelimit.yaml
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: ratelimit-global
  namespace: phenotype
spec:
  workloadSelector:
    labels:
      app: agent-core
  configPatches:
    - applyTo: HTTP_FILTER
      match:
        context: SIDECAR_INBOUND
        listener:
          filterChain:
            filter:
              name: envoy.filters.network.http_connection_manager
      patch:
        operation: INSERT_BEFORE
        value:
          name: envoy.filters.http.local_ratelimit
          typed_config:
            "@type": type.googleapis.com/udpa.type.v1.TypedStruct
            type_url: type.googleapis.com/envoy.extensions.filters.http.local_ratelimit.v3.LocalRateLimit
            value:
              stat_prefix: http_local_rate_limiter
              token_bucket:
                max_tokens: 1000
                tokens_per_fill: 1000
                fill_interval: 1s
              filter_enabled:
                runtime_key: local_rate_limit_enabled
                default_value:
                  numerator: 100
                  denominator: HUNDRED
```

## Deployment

### Helm Values

```yaml
# values.yaml
global:
  meshID: phenotype-mesh
  multiCluster:
    clusterName: phenotype-us-east1

  # mTLS configuration
  mtls:
    enabled: true
    auto: true

  # Tracing configuration
  tracing:
    enabled: true
    provider: jaeger
    samplingRate: 10

  # Logging configuration
  logging:
    level: info
    format: json

# Istio ingress gateway
ingress:
  enabled: true
  replicas: 2
  service:
    type: LoadBalancer
  ports:
    - name: http
      port: 80
      targetPort: 8080
    - name: https
      port: 443
      targetPort: 8443

# Service-specific overrides
services:
  agent-core:
    replicas: 3
    resources:
      requests:
        cpu: 500m
        memory: 512Mi
      limits:
        cpu: 2000m
        memory: 2Gi
    autoscaling:
      enabled: true
      minReplicas: 2
      maxReplicas: 10
      targetCPUUtilizationPercentage: 70

  task-engine:
    replicas: 3
    resources:
      requests:
        cpu: 250m
        memory: 256Mi
      limits:
        cpu: 1000m
        memory: 1Gi
```

## Monitoring Dashboards

### Service Health Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│                     Service Health Dashboard                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Service      │ Health │ Requests │ Latency │ Errors │ mTLS    │
│  ─────────────┼────────┼──────────┼─────────┼────────┼────────  │
│  agent-core   │   ✓    │  1.2k/s  │   45ms  │  0.1%  │   ✓     │
│  task-engine  │   ✓    │    800/s │   23ms  │  0.05% │   ✓     │
│  policy-eng.  │   ✓    │    500/s │   12ms  │  0.01% │   ✓     │
│  config-svc   │   ✓    │    200/s │    8ms  │     0% │   ✓     │
│  auth-service │   ✓    │    300/s │   15ms  │  0.02% │   ✓     │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Resources

- [Istio Documentation](https://istio.io/latest/docs/)
- [Envoy Proxy Documentation](https://www.envoyproxy.io/docs)
- [Service Mesh Architecture ADR](adr/ADR-015-SERVICE-MESH.md)

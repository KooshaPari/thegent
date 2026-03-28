# Inter-Service Communication

**Version**: 1.0.0
**Last Updated**: 2026-03-25

## Overview

This document describes the inter-service communication patterns and implementation for the Phenotype platform.

## Communication Patterns

### 1. Synchronous (Request-Response)

Used for:
- Real-time queries
- User-facing APIs
- Blocking operations

```rust
// Synchronous gRPC call
let response = client
    .task_engine()
    .create_task(CreateTaskRequest {
        name: "process-order".to_string(),
        payload: Some(payload),
    })
    .await
    .map_err(|e| ServiceError::Communication(e.to_string()))?;
```

### 2. Asynchronous (Event-Driven)

Used for:
- Non-blocking operations
- Broadcasting events
- Decoupled services

```rust
// Publish event to message bus
event_bus
    .publish(TaskCompletedEvent {
        task_id: task_id.clone(),
        result: result.clone(),
        timestamp: Utc::now(),
    })
    .await?;
```

### 3. Streaming

Used for:
- Long-running operations
- Real-time updates
- Agent execution

```rust
// Bidirectional streaming
let stream = client
    .agent()
    .execute_streaming(ExecuteRequest {
        agent_id: agent_id.clone(),
        input: input.clone(),
    })
    .await?;

while let Some(chunk) = stream.next().await {
    tx.send(chunk?).await?;
}
```

## gRPC Service Definitions

### Agent Core Service

```protobuf
// proto/agent/v1/agent.proto
syntax = "proto3";

package agent.v1;

import "google/protobuf/any.proto";
import "google/protobuf/timestamp.proto";

service AgentService {
    // Unary calls
    rpc CreateAgent(CreateAgentRequest) returns (CreateAgentResponse);
    rpc GetAgent(GetAgentRequest) returns (GetAgentResponse);
    rpc ListAgents(ListAgentsRequest) returns (ListAgentsResponse);
    rpc DeleteAgent(DeleteAgentRequest) returns (DeleteAgentResponse);

    // Server-side streaming
    rpc ExecuteStreaming(ExecuteRequest) returns (stream ExecuteResponse);

    // Bidirectional streaming
    rpc Chat(stream ChatMessage) returns (stream ChatMessage);

    // Long-running operations
    rpc GetOperation(GetOperationRequest) returns (Operation);
    rpc CancelOperation(CancelOperationRequest) returns (CancelOperationResponse);
}

message CreateAgentRequest {
    string name = 1;
    string model = 2;
    repeated string tools = 3;
    string instructions = 4;
    map<string, string> metadata = 5;
}

message CreateAgentResponse {
    Agent agent = 1;
}

message Agent {
    string id = 1;
    string name = 2;
    string model = 3;
    repeated string tools = 4;
    string instructions = 5;
    google.protobuf.Timestamp created_at = 6;
    google.protobuf.Timestamp updated_at = 7;
    AgentStatus status = 8;
    map<string, string> metadata = 9;
}

enum AgentStatus {
    AGENT_STATUS_UNSPECIFIED = 0;
    AGENT_STATUS_IDLE = 1;
    AGENT_STATUS_RUNNING = 2;
    AGENT_STATUS_PAUSED = 3;
    AGENT_STATUS_ERROR = 4;
}

message ExecuteRequest {
    string agent_id = 1;
    string input = 2;
    map<string, string> context = 3;
    ExecuteOptions options = 4;
}

message ExecuteOptions {
    int32 max_tokens = 1;
    float temperature = 2;
    repeated string stop_sequences = 3;
    bool stream = 4;
}

message ExecuteResponse {
    string content = 1;
    string tool_call = 2;
    google.protobuf.Any metadata = 3;
    bool is_final = 4;
}
```

### Task Engine Service

```protobuf
// proto/task/v1/task.proto
syntax = "proto3";

package task.v1;

import "google/protobuf/any.proto";
import "google/protobuf/timestamp.proto";
import "google/protobuf/duration.proto";

service TaskService {
    rpc CreateTask(CreateTaskRequest) returns (CreateTaskResponse);
    rpc GetTask(GetTaskRequest) returns (GetTaskResponse);
    rpc ListTasks(ListTasksRequest) returns (ListTasksResponse);
    rpc UpdateTask(UpdateTaskRequest) returns (UpdateTaskResponse);
    rpc DeleteTask(DeleteTaskRequest) returns (DeleteTaskResponse);

    // Task execution
    rpc ExecuteTask(ExecuteTaskRequest) returns (ExecuteTaskResponse);
    rpc GetTaskResult(GetTaskResultRequest) returns (GetTaskResultResponse);

    // Task scheduling
    rpc ScheduleTask(ScheduleTaskRequest) returns (ScheduleTaskResponse);
    rpc CancelScheduledTask(CancelScheduledTaskRequest) returns (CancelScheduledTaskResponse);
}

message Task {
    string id = 1;
    string name = 2;
    string description = 3;
    TaskSpec spec = 4;
    TaskStatus status = 5;
    google.protobuf.Timestamp created_at = 6;
    google.protobuf.Timestamp started_at = 7;
    google.protobuf.Timestamp completed_at = 8;
    google.protobuf.Duration duration = 9;
    google.protobuf.Any result = 10;
    TaskError error = 11;
}

message TaskSpec {
    string type = 1;
    map<string, google.protobuf.Any> config = 2;
    repeated string dependencies = 3;
}

enum TaskStatus {
    TASK_STATUS_UNSPECIFIED = 0;
    TASK_STATUS_PENDING = 1;
    TASK_STATUS_RUNNING = 2;
    TASK_STATUS_COMPLETED = 3;
    TASK_STATUS_FAILED = 4;
    TASK_STATUS_CANCELLED = 5;
    TASK_STATUS_TIMEOUT = 6;
}

message CreateTaskRequest {
    string name = 1;
    string description = 2;
    TaskSpec spec = 3;
}

message ExecuteTaskRequest {
    string task_id = 1;
    map<string, google.protobuf.Any> input = 2;
}
```

## Client Implementation

### Service Client with Retries

```rust
// src/adapters/outbound/grpc_client.rs

use std::time::Duration;
use tonic::{
    transport::{Channel, Endpoint},
    Request, Response, Status,
};
use tower::{Service, ServiceBuilder};
use tower_retry::{Policy, Retry};
use tower_timeout::Timeout;
use opentelemetry::global;

pub struct ServiceClient {
    channel: Channel,
    timeout: Duration,
}

impl ServiceClient {
    pub async fn connect(addr: &str) -> Result<Self, ServiceError> {
        let channel = Endpoint::from_static(addr)
            .connect()
            .await
            .map_err(|e| ServiceError::Connection(e.to_string()))?;

        Ok(Self {
            channel,
            timeout: Duration::from_secs(30),
        })
    }

    pub async fn call<T, R>(
        &self,
        method: &str,
        request: T,
    ) -> Result<Response<R>, ServiceError>
    where
        T: Clone + Send + Sync + 'static,
        R: Send + 'static,
    {
        let channel = self.channel.clone();

        // Build retry middleware
        let retry_policy = RetryPolicy::new(
            3,                                      // max retries
            Duration::from_millis(100),             // base delay
            vec![StatusCode::UNAVAILABLE, StatusCode::RESOURCE_EXHAUSTED],
        );

        let service = ServiceBuilder::new()
            .layer(retry_policy)
            .layer(Timeout::new(self.timeout))
            .service(channel);

        // Make the call
        let request = Request::new(request);
        let response = service
            .oneshot(request)
            .await
            .map_err(|e| ServiceError::Communication(e.to_string()))?;

        Ok(response)
    }
}

/// Retry policy for gRPC calls
#[derive(Clone)]
pub struct RetryPolicy {
    max_retries: u32,
    base_delay: Duration,
    retryable_codes: Vec<StatusCode>,
}

impl RetryPolicy {
    pub fn new(max_retries: u32, base_delay: Duration, retryable_codes: Vec<StatusCode>) -> Self {
        Self {
            max_retries,
            base_delay,
            retryable_codes,
        }
    }
}

impl Policy<Request<()>, Response<()>, ServiceError> for RetryPolicy {
    type Failure = ServiceError;

    fn retry(&mut self, _request: &Request<()>, result: Result<&Response<()>, &ServiceError>) -> Option<Result<Request<()>, ServiceError>> {
        match result {
            Ok(_) => None, // Success, don't retry
            Err(e) => {
                if self.retryable_codes.contains(&e.code()) && self.max_retries > 0 {
                    self.max_retries -= 1;
                    Some(Ok(()))
                } else {
                    None
                }
            }
        }
    }
}
```

## Event Bus

### Event Publishing

```rust
// src/adapters/outbound/event_bus.rs

use std::collections::HashMap;
use async_trait::async_trait;
use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use uuid::Uuid;

/// Event trait - all domain events implement this
pub trait Event: Serialize + Send + Sync {
    fn event_type(&self) -> &str;
    fn event_id(&self) -> String;
    fn occurred_at(&self) -> DateTime<Utc>;
}

/// Event bus port - defines how events are published
#[async_trait]
pub trait EventBusPort: Send + Sync {
    async fn publish<E: Event>(&self, event: E) -> Result<(), EventBusError>;
    async fn publish_batch<E: Event>(&self, events: Vec<E>) -> Result<(), EventBusError>;
    async fn subscribe(&self, topic: &str, handler: EventHandler) -> Result<SubscriptionId, EventBusError>;
}

/// Kafka event bus adapter
pub struct KafkaEventBus {
    brokers: Vec<String>,
    producer: AsyncProducer,
    serializer: JsonSerializer,
}

#[async_trait]
impl EventBusPort for KafkaEventBus {
    async fn publish<E: Event>(&self, event: E) -> Result<(), EventBusError> {
        let topic = format!("phenotype.{}", event.event_type());
        let payload = self.serializer.serialize(&event)?;

        let record = FutureRecord::to(&topic)
            .payload(&payload)
            .key(&event.event_id());

        self.producer
            .send(record)
            .await
            .map_err(|e| EventBusError::Publish(e.to_string()))?;

        Ok(())
    }

    async fn publish_batch<E: Event>(&self, events: Vec<E>) -> Result<(), EventBusError> {
        let mut futures = Vec::new();

        for event in events {
            let topic = format!("phenotype.{}", event.event_type());
            let payload = self.serializer.serialize(&event)?;

            let record = FutureRecord::to(&topic)
                .payload(&payload)
                .key(&event.event_id());

            futures.push(self.producer.send(record));
        }

        // Wait for all to complete
        futures::future::join_all(futures)
            .await
            .into_iter()
            .collect::<Result<Vec<_>, _>>()
            .map_err(|e| EventBusError::Publish(e.to_string()))?;

        Ok(())
    }
}

/// Event subscription
#[derive(Clone)]
pub struct SubscriptionId(String);

impl SubscriptionId {
    pub fn new() -> Self {
        Self(Uuid::new_v4().to_string())
    }
}

/// Event handler function type
pub type EventHandler = Arc<dyn Fn(EventEnvelope) -> BoxFuture<Result<(), EventHandlerError>> + Send + Sync>;

/// Event envelope with metadata
#[derive(Serialize, Deserialize)]
pub struct EventEnvelope {
    pub id: String,
    pub event_type: String,
    pub topic: String,
    pub partition: i32,
    pub offset: i64,
    pub timestamp: DateTime<Utc>,
    pub headers: HashMap<String, String>,
    pub payload: serde_json::Value,
}
```

## Service Discovery

### DNS-Based Discovery

```rust
// src/adapters/outbound/service_discovery.rs

use std::net::SocketAddr;
use trust_dns_resolver::TokioAsyncResolver;
use crate::domain::errors::ServiceError;

/// DNS-based service discovery
pub struct DnsServiceDiscovery {
    resolver: TokioAsyncResolver,
    domain: String,
}

impl DnsServiceDiscovery {
    pub fn new(domain: &str) -> Self {
        let resolver = TokioAsyncResolver::tokio_from_system_conf()
            .expect("Failed to create DNS resolver");

        Self {
            resolver,
            domain: domain.to_string(),
        }
    }

    /// Discover service endpoints via DNS SRV records
    pub async fn discover(&self, service: &str) -> Result<Vec<SocketAddr>, ServiceError> {
        let query = format!("{}.{}", service, self.domain);

        // Query SRV records
        let srv_lookup = self.resolver.srv_lookup(format!("_grpc._tcp.{}", query))
            .await
            .map_err(|e| ServiceError::Discovery(e.to_string()))?;

        let mut addresses = Vec::new();

        for srv_record in srv_lookup {
            // Look up A/AAAA records for each target
            let lookup = self.resolver.lookup_ip(srv_record.target().to_string())
                .await
                .map_err(|e| ServiceError::Discovery(e.to_string()))?;

            for ip in lookup {
                addresses.push(SocketAddr::new(ip, srv_record.port()));
            }
        }

        Ok(addresses)
    }

    /// Discover with load balancing
    pub async fn discover_with_lb(
        &self,
        service: &str,
    ) -> Result<LoadBalancedEndpoint, ServiceError> {
        let endpoints = self.discover(service).await?;

        Ok(LoadBalancedEndpoint::new(endpoints))
    }
}

/// Simple round-robin load balancer
pub struct LoadBalancedEndpoint {
    endpoints: Vec<SocketAddr>,
    current: std::sync::atomic::AtomicUsize,
}

impl LoadBalancedEndpoint {
    pub fn new(endpoints: Vec<SocketAddr>) -> Self {
        Self {
            endpoints,
            current: 0.into(),
        }
    }

    pub fn next(&self) -> Option<SocketAddr> {
        if self.endpoints.is_empty() {
            return None;
        }

        let idx = self.current.fetch_add(1, std::sync::atomic::Ordering::Relaxed)
            % self.endpoints.len();

        Some(self.endpoints[idx])
    }
}
```

## Health Checking

### Health Check Implementation

```rust
// src/adapters/outbound/health_check.rs

use std::time::Duration;
use tonic::{transport::Channel, health::pb::HealthCheckRequest};
use crate::domain::errors::ServiceError;

/// Health status of a service
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum HealthStatus {
    Healthy,
    Unhealthy,
    Unknown,
}

/// Health check result
#[derive(Debug)]
pub struct HealthCheckResult {
    pub service: String,
    pub status: HealthStatus,
    pub latency: Duration,
    pub message: Option<String>,
}

/// Health checker for gRPC services
pub struct GrpcHealthChecker {
    channel: Channel,
}

impl GrpcHealthChecker {
    pub fn new(channel: Channel) -> Self {
        Self { channel }
    }

    pub async fn check(&self, service_name: &str) -> HealthCheckResult {
        let start = std::time::Instant::now();

        let request = Request::new(HealthCheckRequest {
            service: service_name.to_string(),
        });

        match self.channel.ready().await {
            Ok(()) => {
                let latency = start.elapsed();
                HealthCheckResult {
                    service: service_name.to_string(),
                    status: HealthStatus::Healthy,
                    latency,
                    message: None,
                }
            }
            Err(e) => {
                let latency = start.elapsed();
                HealthCheckResult {
                    service: service_name.to_string(),
                    status: HealthStatus::Unhealthy,
                    latency,
                    message: Some(e.to_string()),
                }
            }
        }
    }
}

/// Periodic health checker
pub struct HealthChecker {
    services: HashMap<String, GrpcHealthChecker>,
    interval: Duration,
}

impl HealthChecker {
    pub fn new(interval: Duration) -> Self {
        Self {
            services: HashMap::new(),
            interval,
        }
    }

    pub fn register(&mut self, name: &str, channel: Channel) {
        self.services.insert(name.to_string(), GrpcHealthChecker::new(channel));
    }

    pub async fn check_all(&self) -> Vec<HealthCheckResult> {
        let mut results = Vec::new();

        for (name, checker) in &self.services {
            results.push(checker.check(name).await);
        }

        results
    }
}
```

## Distributed Tracing

### Trace Context Propagation

```rust
// src/application/tracing.rs

use opentelemetry::{
    trace::{Span, Tracer, SpanKind, Status, TraceFlags},
    context::{Context, Scope},
    propagation::{Extractor, Injector},
};
use opentelemetry_otlp::WithExportConfig;

/// Extract trace context from gRPC metadata
pub struct GrpcTraceExtractor;

impl Extractor for GrpcTraceExtractor {
    fn get(&self, key: &str) -> Option<&str> {
        // Extract from gRPC metadata
        None // Implementation depends on gRPC library
    }

    fn keys(&self) -> Vec<&str> {
        vec!["traceparent", "tracestate"]
    }
}

/// Inject trace context into gRPC metadata
pub struct GrpcTraceInjector;

impl Injector for GrpcTraceInjector {
    fn set(&mut self, key: &str, value: String) {
        // Inject into gRPC metadata
    }
}

/// Create a traced gRPC call
pub async fn traced_call<F, T>(
    tracer: &Tracer,
    span_name: &str,
    service: &str,
    operation: F,
) -> Result<T, ServiceError>
where
    F: Future<Output = Result<T, ServiceError>>,
{
    let span = tracer
        .span_builder(span_name)
        .with_span_kind(SpanKind::Client)
        .with_attribute("rpc.service", service)
        .start_with_context(tracer, &Context::current());

    let result = operation.await;

    match &result {
        Ok(_) => span.set_status(Status::Ok),
        Err(e) => {
            span.set_status(Status::Error);
            span.record_exception(e);
        }
    }

    result
}
```

## Resources

- [gRPC Documentation](https://grpc.io/docs/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Event-Driven Architecture ADR](adr/ADR-016-EVENT-DRIVEN-ARCHITECTURE.md)

# ADR-009: Telemetry and Observability Strategy

**Date**: 2026-04-05  
**Status**: Accepted  
**Deciders**: Agent  

## Context

thegent operates complex multi-agent workflows with tiered sandboxing. To ensure reliability, debug issues, and optimize performance, we need comprehensive telemetry covering:

1. **Metrics**: Quantitative measurements (latency, throughput, error rates)
2. **Tracing**: Request flows across services
3. **Logging**: Structured event records
4. **Alerting**: Proactive notification of issues

## Decision Drivers

- **Debuggability**: Trace issues across agent/sandbox boundary
- **Performance**: Identify bottlenecks in execution pipeline
- **Reliability**: Detect and alert on failures
- **Compliance**: Audit trail for enterprise customers
- **Cost**: Reasonable overhead (<5% of execution time)

## Metrics Strategy

### Core Metrics

```rust
// Agent metrics
pub struct AgentMetrics {
    pub agents_active: Gauge<u64>,
    pub agents_total: Counter<u64>,
    pub task_duration_seconds: Histogram<f64>,
    pub task_success_total: Counter<u64>,
    pub task_failure_total: Counter<u64>,
    pub iteration_count: Histogram<u32>,
}

// Sandbox metrics
pub struct SandboxMetrics {
    pub sandboxes_active: Gauge<u64>,
    pub sandboxes_created_total: Counter<u64>,
    pub sandboxes_destroyed_total: Counter<u64>,
    pub creation_duration_seconds: Histogram<f64>,
    pub execution_duration_seconds: Histogram<f64>,
    pub memory_usage_bytes: Gauge<u64>,
    pub cpu_usage_percent: Gauge<f64>,
}

// Tier-specific metrics
pub struct TierMetrics {
    pub tier_0_active: Gauge<u64>,
    pub tier_1_active: Gauge<u64>,
    pub tier_2_active: Gauge<u64>,
    pub tier_3_active: Gauge<u64>,
    pub tier_4_active: Gauge<u64>,
    pub tier_5_active: Gauge<u64>,
}

// Trust evaluation metrics
pub struct TrustMetrics {
    pub evaluations_total: Counter<u64>,
    pub trust_levels: Counter<Vec<String>>,  // Labels: trusted, community, untrusted
    pub overrides_total: Counter<u64>,
    pub static_analysis_duration_seconds: Histogram<f64>,
}
```

### Metrics Collection

```rust
pub struct MetricsCollector {
    registry: metrics::Registry,
    exporter: Box<dyn MetricsExporter>,
}

impl MetricsCollector {
    pub fn new() -> Self {
        let registry = metrics::Registry::new();
        
        // Register standard metrics
        let agent_metrics = AgentMetrics::register(&registry);
        let sandbox_metrics = SandboxMetrics::register(&registry);
        let tier_metrics = TierMetrics::register(&registry);
        let trust_metrics = TrustMetrics::register(&registry);
        
        // Configure exporter (Prometheus by default)
        let exporter = PrometheusExporter::new();
        
        Self {
            registry,
            exporter: Box::new(exporter),
        }
    }
    
    pub fn record_task_execution(&self, task: &Task, result: &TaskResult) {
        let duration = result
            .completed_at
            .duration_since(task.started_at.unwrap_or_else(Utc::now))
            .unwrap_or_default();
        
        self.agent_metrics
            .task_duration_seconds
            .record(duration.as_secs_f64());
        
        if result.error.is_some() {
            self.agent_metrics.task_failure_total.increment(1);
        } else {
            self.agent_metrics.task_success_total.increment(1);
        }
    }
}
```

### Prometheus Export

```yaml
# Prometheus scrape config
scrape_configs:
  - job_name: 'thegent'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

```rust
// Expose metrics endpoint
async fn metrics_handler() -> impl IntoResponse {
    let encoder = PrometheusEncoder::new();
    let metric_families = collector::gather();
    
    let mut output = Vec::new();
    encoder.encode(&metric_families, &mut output).unwrap();
    
    Response::builder()
        .header("Content-Type", encoder.format_type())
        .body(output.into())
}
```

## Tracing Strategy

### Distributed Tracing

```rust
pub struct TracingConfig {
    pub service_name: String,
    pub exporter: TracingExporter,
    pub sampling_rate: f64,
}

#[derive(Debug, Clone)]
pub struct SpanContext {
    pub trace_id: TraceId,
    pub span_id: SpanId,
    pub parent_id: Option<SpanId>,
    pub sampled: bool,
}

impl SpanContext {
    pub fn current() -> Option<Self> {
        // Extract from TLS or propagate from headers
    }
}

// Span creation
pub trait Traceable {
    fn trace_id(&self) -> TraceId;
}

impl Traceable for Task {
    fn trace_id(&self) -> TraceId {
        self.trace_id.unwrap_or_else(TraceId::new)
    }
}

// Annotation
pub struct Span {
    context: SpanContext,
    name: String,
    start_time: Instant,
    attributes: Vec<KeyValue>,
    events: Vec<SpanEvent>,
}

impl Span {
    pub fn new(name: &str) -> Self {
        Self {
            context: SpanContext::current().unwrap_or_default(),
            name: name.to_string(),
            start_time: Instant::now(),
            attributes: Vec::new(),
            events: Vec::new(),
        }
    }
    
    pub fn with_attribute(mut self, key: &str, value: Value) -> Self {
        self.attributes.push(KeyValue { key: key.to_string(), value });
        self
    }
    
    pub fn record(&self) {
        // Export span to collector
    }
}
```

### Trace Propagation

```rust
// Propagate trace context through MCP
pub struct TraceMiddleware;

impl<F> Middleware<F> for TraceMiddleware {
    fn handle(&self, req: Request, next: Next) -> Response {
        // Extract trace context from headers
        let trace_context = extract_trace_context(req.headers());
        
        // Inject into request context
        let span = Span::new("mcp_request")
            .with_attribute("request.id", req.id.clone().into());
        
        let result = next.run(req, trace_context);
        
        span.record();
        result
    }
}

// Propagate through event bus
pub struct NatsTraceInjector;

impl MessageInterceptor for NatsTraceInjector {
    fn on_publish(&self, msg: &mut NatsMessage) {
        if let Some(ctx) = SpanContext::current() {
            msg.headers.insert("trace-id", ctx.trace_id.to_string());
            msg.headers.insert("span-id", ctx.span_id.to_string());
        }
    }
}
```

## Logging Strategy

### Structured Logging

```rust
pub struct Logger {
    dispatcher: Dispatch,
}

impl Logger {
    pub fn new(config: &LoggingConfig) -> Self {
        let dispatcher = Dispatch::new()
            .format(|out, message, record| {
                out.finish(format_args!(
                    "{} {} {} {} {}",
                    message.timestamp(),
                    record.level(),
                    record.target(),
                    record.line(),
                    message.text()
                ))
            })
            .chain(self.stdout_writer())
            .chain(self.file_writer(&config.file_path));
        
        Self { dispatcher }
    }
}

// Log levels by component
pub enum LogLevel {
    Error,   // Agent failures, sandbox errors
    Warn,    // Retries, degraded performance
    Info,    // Task lifecycle, agent events
    Debug,   // Sandbox operations, detailed flows
    Trace,   // Function entry/exit, variable dumps
}

// Log event schema
pub struct LogEvent {
    pub timestamp: DateTime<Utc>,
    pub level: LogLevel,
    pub target: String,
    pub message: String,
    pub trace_id: Option<TraceId>,
    pub span_id: Option<SpanId>,
    pub attributes: HashMap<String, Value>,
    pub stack_trace: Option<String>,
}
```

### Log Correlation

```rust
// Correlate logs with traces
pub struct LogCorrelator;

impl LogCorrelator {
    pub fn enrich(&self, log: &mut LogEvent) {
        if let Some(ctx) = SpanContext::current() {
            log.trace_id = Some(ctx.trace_id);
            log.span_id = Some(ctx.span_id);
        }
        
        // Add resource info
        log.attributes.insert("service".into(), "thegent".into());
        log.attributes.insert("version".into(), env!("CARGO_PKG_VERSION").into());
    }
}
```

## Alerting Strategy

### Alert Definitions

```yaml
# alerts.yaml
groups:
  - name: thegent.agent
    rules:
      - alert: AgentTaskFailureRate
        expr: |
          rate(thegent_tasks_failed_total[5m]) 
          / rate(thegent_tasks_total[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High agent task failure rate"
          description: "Task failure rate is {{ $value | humanizePercentage }}"

      - alert: AgentHighLatency
        expr: |
          histogram_quantile(0.99, rate(thegent_task_duration_seconds_bucket[5m])) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High task latency"
          description: "P99 latency is {{ $value }}s"

  - name: thegent.sandbox
    rules:
      - alert: SandboxCreationFailure
        expr: |
          rate(thegent_sandbox_errors_total[5m]) > 0.05
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Sandbox creation failures"
          
      - alert: SandboxMemoryExhaustion
        expr: |
          thegent_sandbox_memory_usage_bytes / thegent_sandbox_memory_limit_bytes > 0.9
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Sandbox memory near limit"
```

### Alert Routing

```rust
pub enum AlertSeverity {
    Info,
    Warning,
    Critical,
}

pub trait AlertNotifier: Send + Sync {
    fn send(&self, alert: &Alert) -> Result<()>;
}

// Notification channels
pub struct SlackNotifier {
    webhook_url: String,
}

pub struct PagerDutyNotifier {
    api_key: String,
}

pub struct EmailNotifier {
    smtp_config: SmtpConfig,
    recipients: Vec<String>,
}
```

## Dashboard

### Key Dashboards

1. **Executive Overview**: Tasks/min, success rate, active agents
2. **Agent Performance**: Latency by tier, failure reasons, iteration counts
3. **Sandbox Operations**: Active by tier, creation latency, memory usage
4. **Trust Evaluation**: Evaluations by level, override frequency
5. **Resource Utilization**: CPU, memory, network by tier

## Consequences

### Positive
- **Full observability**: Know exactly what's happening
- **Performance optimization**: Identify bottlenecks
- **Proactive alerting**: Fix issues before users notice
- **Compliance**: Audit trail for enterprise

### Negative
- **Storage costs**: Log/trace retention adds up
- **Performance overhead**: ~2-5% for instrumentation
- **Complexity**: Multiple systems to operate

## References

- OpenTelemetry: https://opentelemetry.io/
- Prometheus: https://prometheus.io/
- Grafana: https://grafana.com/
- Structured logging: https://www.innoq.com/en/blog/structured-logging/

---

*This ADR will be updated as implementation progresses*

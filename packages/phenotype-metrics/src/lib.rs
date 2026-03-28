//! Phenotype Metrics - Observability and metrics collection framework
//!
//! Provides comprehensive metrics collection for:
//! - Request/response metrics (latency, throughput)
//! - Business metrics (orders, transactions, conversions)
//! - System metrics (CPU, memory, disk usage)
//! - Custom application metrics
//! - Prometheus-compatible output

use std::sync::Arc;
use std::time::{Duration, SystemTime};
use std::collections::HashMap;

/// Metric types supported by the framework
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum MetricType {
    Counter,
    Gauge,
    Histogram,
    Timer,
}

/// A single metric value
#[derive(Debug, Clone)]
pub struct MetricValue {
    pub name: String,
    pub value: f64,
    pub metric_type: MetricType,
    pub timestamp: SystemTime,
    pub labels: HashMap<String, String>,
}

/// Metrics registry for collecting and exporting metrics
pub struct MetricsRegistry {
    metrics: Arc<std::sync::Mutex<HashMap<String, MetricValue>>>,
}

impl MetricsRegistry {
    /// Create a new metrics registry
    pub fn new() -> Self {
        Self {
            metrics: Arc::new(std::sync::Mutex::new(HashMap::new())),
        }
    }

    /// Record a counter metric
    pub fn increment_counter(&self, name: &str, value: f64) {
        let mut metrics = self.metrics.lock().unwrap();
        let metric = metrics
            .entry(name.to_string())
            .or_insert_with(|| MetricValue {
                name: name.to_string(),
                value: 0.0,
                metric_type: MetricType::Counter,
                timestamp: SystemTime::now(),
                labels: HashMap::new(),
            });
        metric.value += value;
    }

    /// Record a gauge metric
    pub fn set_gauge(&self, name: &str, value: f64) {
        let mut metrics = self.metrics.lock().unwrap();
        metrics.insert(
            name.to_string(),
            MetricValue {
                name: name.to_string(),
                value,
                metric_type: MetricType::Gauge,
                timestamp: SystemTime::now(),
                labels: HashMap::new(),
            },
        );
    }

    /// Record a timer metric
    pub fn record_timer(&self, name: &str, duration: Duration) {
        let millis = duration.as_millis() as f64;
        let mut metrics = self.metrics.lock().unwrap();
        metrics.insert(
            name.to_string(),
            MetricValue {
                name: name.to_string(),
                value: millis,
                metric_type: MetricType::Timer,
                timestamp: SystemTime::now(),
                labels: HashMap::new(),
            },
        );
    }

    /// Get all metrics in Prometheus format
    pub fn export_prometheus(&self) -> String {
        let metrics = self.metrics.lock().unwrap();
        let mut output = String::new();
        for (_, metric) in metrics.iter() {
            output.push_str(&format!(
                "{} {} {}\n",
                metric.name,
                metric.value,
                metric
                    .timestamp
                    .duration_since(SystemTime::UNIX_EPOCH)
                    .unwrap_or_default()
                    .as_millis()
            ));
        }
        output
    }
}

impl Default for MetricsRegistry {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_counter_increment() {
        let registry = MetricsRegistry::new();
        registry.increment_counter("requests", 1.0);
        registry.increment_counter("requests", 1.0);
        let output = registry.export_prometheus();
        assert!(output.contains("requests"));
        assert!(output.contains(" 2 "));
    }

    #[test]
    fn test_gauge_set() {
        let registry = MetricsRegistry::new();
        registry.set_gauge("memory_usage", 512.5);
        let output = registry.export_prometheus();
        assert!(output.contains("memory_usage"));
        assert!(output.contains("512.5"));
    }

    #[test]
    fn test_timer_record() {
        let registry = MetricsRegistry::new();
        registry.record_timer("response_time", Duration::from_millis(100));
        let output = registry.export_prometheus();
        assert!(output.contains("response_time"));
        assert!(output.contains("100"));
    }

    #[test]
    fn test_prometheus_export() {
        let registry = MetricsRegistry::new();
        registry.increment_counter("requests", 1.0);
        let output = registry.export_prometheus();
        assert!(output.contains("requests 1"));
    }
}

//! Phenotype Shared Metrics - Observability metrics collection interface
//!
//! Provides a language-agnostic metrics interface for the Phenotype ecosystem.
//!
//! # Metric Types
//!
//! - `Counter` - Incremental values (e.g., request counts)
//! - `Gauge` - Point-in-time values (e.g., memory usage)
//! - `Histogram` - Distribution of values (e.g., response sizes)
//! - `Timer` - Duration measurements (e.g., latency)
//!
//! # Usage
//!
//! ```rust
//! use phenotype_metrics::prelude::*;
//!
//! let registry = MetricsRegistry::new();
//! registry.increment_counter("requests_total", 1.0);
//! registry.set_gauge("memory_bytes", 1024.0);
//! let prometheus_output = registry.export_prometheus();
//! ```
//!
//! # Architecture
//!
//! This trait-based interface allows each language implementation to provide
//! idiomatic metrics while maintaining ecosystem-wide consistency.

use std::time::{Duration, SystemTime};
use std::collections::HashMap;

// ============================================================================
// Metric Types
// ============================================================================

/// Metric types supported across the Phenotype ecosystem
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum MetricType {
    /// Incremental counter - values only increase
    Counter,
    /// Point-in-time gauge - can go up or down
    Gauge,
    /// Histogram - distribution of values
    Histogram,
    /// Timer - duration measurements
    Timer,
}

/// A single metric data point
#[derive(Debug, Clone)]
pub struct MetricValue {
    /// Metric name (e.g., "requests_total", "memory_bytes")
    pub name: String,
    /// Numeric value
    pub value: f64,
    /// Type of metric
    pub metric_type: MetricType,
    /// When the metric was recorded
    pub timestamp: SystemTime,
    /// Key-value labels for dimensionality
    pub labels: HashMap<String, String>,
}

impl MetricValue {
    /// Create a new metric value
    pub fn new(name: &str, value: f64, metric_type: MetricType) -> Self {
        Self {
            name: name.to_string(),
            value,
            metric_type,
            timestamp: SystemTime::now(),
            labels: HashMap::new(),
        }
    }

    /// Create with labels
    pub fn with_labels(mut self, labels: HashMap<String, String>) -> Self {
        self.labels = labels;
        self
    }
}

// ============================================================================
// Metrics Registry Trait (Port Interface)
// ============================================================================

/// Port interface for metrics collection
/// Implement this trait to create a custom metrics backend
pub trait MetricsPort: Send + Sync {
    /// Record a counter increment
    fn increment_counter(&self, name: &str, value: f64);

    /// Set a gauge value
    fn set_gauge(&self, name: &str, value: f64);

    /// Record a histogram observation
    fn observe_histogram(&self, name: &str, value: f64);

    /// Record a timer duration
    fn record_timer(&self, name: &str, duration: Duration);

    /// Export all metrics in Prometheus format
    fn export_prometheus(&self) -> String;
}

/// Default in-memory metrics registry implementation
pub struct MetricsRegistry {
    metrics: std::sync::Arc<std::sync::Mutex<HashMap<String, MetricValue>>>,
}

impl MetricsRegistry {
    /// Create a new metrics registry
    pub fn new() -> Self {
        Self {
            metrics: std::sync::Arc::new(std::sync::Mutex::new(HashMap::new())),
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

    /// Record a histogram observation
    pub fn observe_histogram(&self, name: &str, value: f64) {
        let mut metrics = self.metrics.lock().unwrap();
        metrics.insert(
            name.to_string(),
            MetricValue {
                name: name.to_string(),
                value,
                metric_type: MetricType::Histogram,
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

    /// Get all metrics in Prometheus exposition format
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

impl MetricsPort for MetricsRegistry {
    fn increment_counter(&self, name: &str, value: f64) {
        self.increment_counter(name, value);
    }

    fn set_gauge(&self, name: &str, value: f64) {
        self.set_gauge(name, value);
    }

    fn observe_histogram(&self, name: &str, value: f64) {
        self.observe_histogram(name, value);
    }

    fn record_timer(&self, name: &str, duration: Duration) {
        self.record_timer(name, duration);
    }

    fn export_prometheus(&self) -> String {
        self.export_prometheus()
    }
}

// ============================================================================
// Prelude
// ============================================================================

/// Common imports for metrics usage
pub mod prelude {
    pub use super::{MetricType, MetricValue, MetricsPort, MetricsRegistry};
}

// ============================================================================
// Tests
// ============================================================================

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

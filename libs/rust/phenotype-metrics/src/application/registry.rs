//! Metrics registry - Central registration and access point for metrics.
//!
//! The registry follows the singleton pattern but is more testable
//! than a true global. It manages metric lifecycle and provides
//! thread-safe access.

use crate::domain::{
    Counter, Gauge, Histogram, HistogramOptions, Metric, MetricError,
    MetricResult, MetricType, Summary, SummaryOptions,
};
use std::collections::HashMap;
use std::sync::{Arc, RwLock};

/// Thread-safe metrics registry.
#[derive(Debug, Default)]
pub struct Registry {
    metrics: Arc<RwLock<HashMap<String, Metric>>>,
}

impl Registry {
    /// Create a new registry.
    pub fn new() -> Self {
        Self {
            metrics: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    /// Register a counter metric.
    pub fn counter(&self, name: &str, description: &str) -> MetricResult<Counter> {
        let metric = Metric::new(
            name.to_string(),
            description.to_string(),
            MetricType::Counter,
        )?;
        let counter = metric.counter()?;
        self.register(metric)?;
        Ok(counter)
    }

    /// Register a gauge metric.
    pub fn gauge(&self, name: &str, description: &str) -> MetricResult<Gauge> {
        let metric = Metric::new(
            name.to_string(),
            description.to_string(),
            MetricType::Gauge,
        )?;
        let gauge = metric.gauge()?;
        self.register(metric)?;
        Ok(gauge)
    }

    /// Register a histogram metric.
    pub fn histogram(
        &self,
        name: &str,
        description: &str,
        options: HistogramOptions,
    ) -> MetricResult<Histogram> {
        let metric = Metric::new(
            name.to_string(),
            description.to_string(),
            MetricType::Histogram(options),
        )?;
        let histogram = metric.histogram()?;
        self.register(metric)?;
        Ok(histogram)
    }

    /// Register a summary metric.
    pub fn summary(
        &self,
        name: &str,
        description: &str,
        options: SummaryOptions,
    ) -> MetricResult<Summary> {
        let metric = Metric::new(
            name.to_string(),
            description.to_string(),
            MetricType::Summary(options),
        )?;
        let summary = metric.summary()?;
        self.register(metric)?;
        Ok(summary)
    }

    /// Register a metric.
    fn register(&self, metric: Metric) -> MetricResult<()> {
        let mut metrics = self.metrics.write().map_err(|_| {
            MetricError::registration_failed("unknown", "lock poisoned")
        })?;

        if metrics.contains_key(metric.name()) {
            return Err(MetricError::registration_failed(
                metric.name(),
                "already registered",
            ));
        }

        metrics.insert(metric.name().to_string(), metric);
        Ok(())
    }

    /// Get a metric by name.
    pub fn get(&self, name: &str) -> Option<Metric> {
        self.metrics.read().ok()?.get(name).cloned()
    }

    /// Get all registered metric names.
    pub fn names(&self) -> Vec<String> {
        self.metrics
            .read()
            .map(|m| m.keys().cloned().collect())
            .unwrap_or_default()
    }

    /// Unregister a metric.
    pub fn unregister(&self, name: &str) -> bool {
        self.metrics.write().ok().map(|mut m| m.remove(name).is_some()).unwrap_or(false)
    }
}

impl Clone for Registry {
    fn clone(&self) -> Self {
        Self {
            metrics: Arc::clone(&self.metrics),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_register_counter() {
        let registry = Registry::new();
        let counter = registry.counter("requests", "Total requests").unwrap();
        counter.inc();
        assert_eq!(counter.get(), 1);
    }

    #[test]
    fn test_register_gauge() {
        let registry = Registry::new();
        let gauge = registry.gauge("temperature", "Current temperature").unwrap();
        gauge.set(25.5);
        assert_eq!(gauge.get(), 25.5);
    }

    #[test]
    fn test_duplicate_registration() {
        let registry = Registry::new();
        registry.counter("requests", "Total requests").unwrap();
        let result = registry.counter("requests", "Total requests");
        assert!(result.is_err());
    }

    #[test]
    fn test_unregister() {
        let registry = Registry::new();
        registry.counter("requests", "Total requests").unwrap();
        assert!(registry.unregister("requests"));
        assert!(!registry.unregister("requests"));
    }
}

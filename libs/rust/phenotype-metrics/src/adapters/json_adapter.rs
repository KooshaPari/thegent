//! JSON adapter - Export metrics in JSON format.
//!
//! This adapter exports metrics in JSON format for programmatic
//! consumption or debugging purposes.

use crate::application::Registry;
use crate::domain::Metric;
use std::collections::HashMap;

/// JSON format adapter.
#[derive(Debug)]
pub struct JsonAdapter {
    registry: Registry,
}

impl JsonAdapter {
    /// Create a new adapter.
    pub fn new(registry: Registry) -> Self {
        Self { registry }
    }

    /// Export all metrics as a JSON value.
    ///
    /// Returns a representation suitable for serialization.
    pub fn export(&self) -> JsonMetrics {
        let mut metrics = Vec::new();

        for name in self.registry.names() {
            if let Some(metric) = self.registry.get(&name) {
                metrics.push(self.export_metric(&metric));
            }
        }

        JsonMetrics { metrics }
    }

    fn export_metric(&self, metric: &Metric) -> JsonMetric {
        let labels: HashMap<String, String> = metric
            .labels()
            .iter()
            .map(|(k, v)| (k.clone(), v.clone()))
            .collect();

        let value = match metric.metric_type() {
            crate::domain::MetricType::Counter => {
                if let Ok(counter) = metric.counter() {
                    serde_json::json!({"type": "counter", "value": counter.get()})
                } else {
                    serde_json::json!({"type": "counter", "value": null})
                }
            }
            crate::domain::MetricType::Gauge => {
                if let Ok(gauge) = metric.gauge() {
                    serde_json::json!({"type": "gauge", "value": gauge.get()})
                } else {
                    serde_json::json!({"type": "gauge", "value": null})
                }
            }
            crate::domain::MetricType::Histogram(_) => {
                if let Ok(histogram) = metric.histogram() {
                    serde_json::json!({
                        "type": "histogram",
                        "count": histogram.count(),
                        "sum": histogram.sum(),
                        "buckets": histogram.buckets()
                    })
                } else {
                    serde_json::json!({"type": "histogram", "value": null})
                }
            }
            crate::domain::MetricType::Summary(_) => {
                if let Ok(summary) = metric.summary() {
                    serde_json::json!({
                        "type": "summary",
                        "quantiles": summary.quantiles()
                    })
                } else {
                    serde_json::json!({"type": "summary", "value": null})
                }
            }
        };

        JsonMetric {
            name: metric.name().to_string(),
            description: metric.description().to_string(),
            labels,
            value,
        }
    }
}

/// JSON representation of all metrics.
#[derive(Debug, serde::Serialize)]
pub struct JsonMetrics {
    #[serde(rename = "metrics")]
    pub metrics: Vec<JsonMetric>,
}

/// JSON representation of a single metric.
#[derive(Debug, serde::Serialize)]
pub struct JsonMetric {
    pub name: String,
    pub description: String,
    pub labels: HashMap<String, String>,
    pub value: serde_json::Value,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_export_json() {
        let registry = Registry::new();
        let counter = registry.counter("requests", "Total requests").unwrap();
        counter.inc_by(10).unwrap();

        let adapter = JsonAdapter::new(registry);
        let json = adapter.export();

        assert_eq!(json.metrics.len(), 1);
        assert_eq!(json.metrics[0].name, "requests");
        assert_eq!(json.metrics[0].description, "Total requests");
    }
}

//! Prometheus adapter - Export metrics in Prometheus format.
//!
//! This adapter exports metrics in the Prometheus text format,
//! suitable for scraping by Prometheus or compatible systems.

use crate::application::Registry;
use crate::domain::{Metric, MetricType};

/// Prometheus format adapter.
#[derive(Debug)]
pub struct PrometheusAdapter {
    registry: Registry,
}

impl PrometheusAdapter {
    /// Create a new adapter.
    pub fn new(registry: Registry) -> Self {
        Self { registry }
    }

    /// Export all metrics in Prometheus format.
    pub fn export(&self) -> String {
        let mut output = String::new();

        for name in self.registry.names() {
            if let Some(metric) = self.registry.get(&name) {
                self.export_metric(&mut output, &metric);
            }
        }

        output
    }

    fn export_metric(&self, output: &mut String, metric: &Metric) {
        // Export metric metadata
        let metric_type = match &metric.metric_type() {
            MetricType::Counter => "counter",
            MetricType::Gauge => "gauge",
            MetricType::Histogram(_) => "histogram",
            MetricType::Summary(_) => "summary",
        };

        // HELP comment
        output.push_str(&format!("# HELP {} {}\n", metric.name(), metric.description()));
        // TYPE comment
        output.push_str(&format!("# TYPE {} {}\n", metric.name(), metric_type));

        match metric.metric_type() {
            MetricType::Counter => {
                output.push_str(&format!(
                    "{}{} {}\n",
                    metric.name(),
                    self.format_labels(metric.labels()),
                    metric.counter().map(|c| c.get()).unwrap_or(0)
                ));
            }
            MetricType::Gauge => {
                output.push_str(&format!(
                    "{}{} {}\n",
                    metric.name(),
                    self.format_labels(metric.labels()),
                    metric.gauge().map(|g| g.get()).unwrap_or(0.0)
                ));
            }
            MetricType::Histogram(ref opts) => {
                if let Ok(histogram) = metric.histogram() {
                    let sum = histogram.sum();
                    let count = histogram.count();
                    let buckets = histogram.buckets();

                    for (i, bound) in opts.bounds.iter().enumerate() {
                        let bucket_count = buckets.get(i).copied().unwrap_or(0);
                        output.push_str(&format!(
                            "{}_bucket{}{}} {}\n",
                            metric.name(),
                            self.format_labels(metric.labels()),
                            bound,
                            bucket_count
                        ));
                    }

                    output.push_str(&format!(
                        "{}_sum{} {}\n",
                        metric.name(),
                        self.format_labels(metric.labels()),
                        sum
                    ));
                    output.push_str(&format!(
                        "{}_count{} {}\n",
                        metric.name(),
                        self.format_labels(metric.labels()),
                        count
                    ));
                }
            }
            MetricType::Summary(_) => {
                if let Ok(summary) = metric.summary() {
                    for quantile in [0.5, 0.9, 0.99] {
                        output.push_str(&format!(
                            "{}{{{quantile=\"{}\"}}} {}\n",
                            metric.name(),
                            self.format_labels(metric.labels()),
                            summary.quantile(quantile).unwrap_or(0.0)
                        ));
                    }
                }
            }
        }
    }

    fn format_labels(&self, labels: &[(String, String)]) -> String {
        if labels.is_empty() {
            return String::new();
        }

        let parts: Vec<String> = labels
            .iter()
            .map(|(k, v)| format!("{}=\"{}\"", k, v))
            .collect();

        format!("{{{}}}", parts.join(","))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::domain::HistogramOptions;

    #[test]
    fn test_export_counter() {
        let registry = Registry::new();
        let counter = registry.counter("requests", "Total requests").unwrap();
        counter.inc_by(42).unwrap();

        let adapter = PrometheusAdapter::new(registry);
        let output = adapter.export();

        assert!(output.contains("# HELP requests Total requests"));
        assert!(output.contains("# TYPE requests counter"));
        assert!(output.contains("requests 42"));
    }

    #[test]
    fn test_export_gauge() {
        let registry = Registry::new();
        let gauge = registry.gauge("temperature", "Current temperature").unwrap();
        gauge.set(25.5).unwrap();

        let adapter = PrometheusAdapter::new(registry);
        let output = adapter.export();

        assert!(output.contains("# HELP temperature Current temperature"));
        assert!(output.contains("# TYPE temperature gauge"));
        assert!(output.contains("temperature 25.5"));
    }
}

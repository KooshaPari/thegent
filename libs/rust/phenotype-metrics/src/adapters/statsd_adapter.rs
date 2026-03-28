//! StatsD adapter - Export metrics in StatsD/DogStatsD format.
//!
//! This adapter exports metrics in the StatsD protocol format,
//! suitable for sending to StatsD, DogStatsD, or Telegraf.

use crate::application::Registry;
use crate::domain::Metric;

/// StatsD protocol adapter.
#[derive(Debug)]
pub struct StatsdAdapter {
    registry: Registry,
}

impl StatsdAdapter {
    /// Create a new adapter.
    pub fn new(registry: Registry) -> Self {
        Self { registry }
    }

    /// Export all metrics in StatsD format.
    ///
    /// Returns a vector of strings, each representing a metric line.
    pub fn export(&self) -> Vec<String> {
        let mut lines = Vec::new();

        for name in self.registry.names() {
            if let Some(metric) = self.registry.get(&name) {
                lines.extend(self.export_metric(&metric));
            }
        }

        lines
    }

    fn export_metric(&self, metric: &Metric) -> Vec<String> {
        let mut lines = Vec::new();
        let name = metric.name();
        let labels = metric.labels();

        // StatsD doesn't support labels directly, so we encode them in the metric name
        let base_name = if labels.is_empty() {
            name.to_string()
        } else {
            let label_str = labels
                .iter()
                .map(|(k, v)| format!("{}_{}", k, v))
                .collect::<Vec<_>>()
                .join("_");
            format!("{}_{}", name, label_str)
        };

        match metric.metric_type() {
            crate::domain::MetricType::Counter => {
                if let Ok(counter) = metric.counter() {
                    let value = counter.get();
                    lines.push(format!("{}:{}|c", base_name, value));
                }
            }
            crate::domain::MetricType::Gauge => {
                if let Ok(gauge) = metric.gauge() {
                    let value = gauge.get();
                    lines.push(format!("{}:{}|g", base_name, value));
                }
            }
            crate::domain::MetricType::Histogram(_) => {
                if let Ok(histogram) = metric.histogram() {
                    // Export histogram as timing
                    let sum = histogram.sum();
                    let count = histogram.count();
                    if count > 0 {
                        let mean = sum / count as f64;
                        lines.push(format!("{}:{:.2}|ms", base_name, mean));
                    }
                }
            }
            crate::domain::MetricType::Summary(_) => {
                if let Ok(summary) = metric.summary() {
                    // Export summary quantiles
                    for quantile in [0.5, 0.9, 0.99] {
                        if let Ok(value) = summary.quantile(quantile) {
                            lines.push(format!(
                                "{}:{}|{}",
                                format!("{}_p{}", base_name, (quantile * 100.0) as u32),
                                value,
                                "g" // Gauge
                            ));
                        }
                    }
                }
            }
        }

        lines
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_export_counter() {
        let registry = Registry::new();
        let counter = registry.counter("requests", "Total requests").unwrap();
        counter.inc_by(5).unwrap();

        let adapter = StatsdAdapter::new(registry);
        let lines = adapter.export();

        assert!(lines.iter().any(|l| l.contains("requests:5|c")));
    }

    #[test]
    fn test_export_gauge() {
        let registry = Registry::new();
        let gauge = registry.gauge("temperature", "Current temperature").unwrap();
        gauge.set(25.5).unwrap();

        let adapter = StatsdAdapter::new(registry);
        let lines = adapter.export();

        assert!(lines.iter().any(|l| l.contains("temperature:25.5|g")));
    }
}

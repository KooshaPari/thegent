//! Metric definition.

use crate::domain::{Label, MetricType, MetricUnit};
use core::fmt;

/// Metric identifier.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MetricId {
    name: String,
    namespace: Option<String>,
    subsystem: Option<String>,
}

impl MetricId {
    /// Create a new metric ID.
    pub fn new(name: impl Into<String>) -> Self {
        Self {
            name: name.into(),
            namespace: None,
            subsystem: None,
        }
    }

    /// Set the namespace.
    pub fn namespace(mut self, ns: impl Into<String>) -> Self {
        self.namespace = Some(ns.into());
        self
    }

    /// Set the subsystem.
    pub fn subsystem(mut self, sub: impl Into<String>) -> Self {
        self.subsystem = Some(sub.into());
        self
    }

    /// Get the full name (namespace_subsystem_name).
    pub fn full_name(&self) -> String {
        let mut parts = Vec::new();
        if let Some(ns) = &self.namespace {
            parts.push(ns.clone());
        }
        if let Some(sub) = &self.subsystem {
            parts.push(sub.clone());
        }
        parts.push(self.name.clone());
        parts.join("_")
    }

    /// Get the Prometheus name (namespace_subsystem_name).
    pub fn prometheus_name(&self) -> String {
        self.full_name()
    }
}

impl fmt::Display for MetricId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.full_name())
    }
}

/// Metric definition.
#[derive(Debug)]
pub struct Metric {
    id: MetricId,
    metric_type: MetricType,
    description: String,
    unit: MetricUnit,
    labels: Vec<Label>,
}

impl Metric {
    /// Create a new metric.
    pub fn new(
        name: impl Into<String>,
        metric_type: MetricType,
        description: impl Into<String>,
    ) -> Self {
        Self {
            id: MetricId::new(name),
            metric_type,
            description: description.into(),
            unit: MetricUnit::default(),
            labels: Vec::new(),
        }
    }

    /// Set the namespace.
    pub fn namespace(mut self, ns: impl Into<String>) -> Self {
        self.id.namespace = Some(ns.into());
        self
    }

    /// Set the subsystem.
    pub fn subsystem(mut self, sub: impl Into<String>) -> Self {
        self.id.subsystem = Some(sub.into());
        self
    }

    /// Set the unit.
    pub fn unit(mut self, unit: MetricUnit) -> Self {
        self.unit = unit;
        self
    }

    /// Add a label.
    pub fn label(mut self, label: Label) -> Self {
        self.labels.push(label);
        self
    }

    /// Add multiple labels.
    pub fn labels(mut self, labels: impl IntoIterator<Item = Label>) -> Self {
        self.labels.extend(labels);
        self
    }

    /// Get the metric ID.
    pub fn id(&self) -> &MetricId {
        &self.id
    }

    /// Get the metric type.
    pub fn metric_type(&self) -> MetricType {
        self.metric_type
    }

    /// Get the description.
    pub fn description(&self) -> &str {
        &self.description
    }

    /// Get the unit.
    pub fn unit(&self) -> MetricUnit {
        self.unit
    }

    /// Get the labels.
    pub fn labels(&self) -> &[Label] {
        &self.labels
    }
}

/// Builder for creating metrics.
pub struct MetricBuilder {
    name: String,
    metric_type: MetricType,
    description: String,
    namespace: Option<String>,
    subsystem: Option<String>,
    unit: MetricUnit,
    labels: Vec<Label>,
}

impl MetricBuilder {
    /// Create a new builder.
    pub fn new(name: impl Into<String>, metric_type: MetricType, description: impl Into<String>) -> Self {
        Self {
            name: name.into(),
            metric_type,
            description: description.into(),
            namespace: None,
            subsystem: None,
            unit: MetricUnit::default(),
            labels: Vec::new(),
        }
    }

    /// Set the namespace.
    pub fn namespace(mut self, ns: impl Into<String>) -> Self {
        self.namespace = Some(ns.into());
        self
    }

    /// Set the subsystem.
    pub fn subsystem(mut self, sub: impl Into<String>) -> Self {
        self.subsystem = Some(sub.into());
        self
    }

    /// Set the unit.
    pub fn unit(mut self, unit: MetricUnit) -> Self {
        self.unit = unit;
        self
    }

    /// Add a label.
    pub fn label(mut self, label: Label) -> Self {
        self.labels.push(label);
        self
    }

    /// Build the metric.
    pub fn build(self) -> Metric {
        let mut metric = Metric::new(self.name, self.metric_type, self.description)
            .unit(self.unit)
            .labels(self.labels);
        
        if let Some(ns) = self.namespace {
            metric = metric.namespace(ns);
        }
        if let Some(sub) = self.subsystem {
            metric = metric.subsystem(sub);
        }
        
        metric
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_metric_id() {
        let id = MetricId::new("requests")
            .namespace("http")
            .subsystem("server");
        
        assert_eq!(id.full_name(), "http_server_requests");
    }

    #[test]
    fn test_metric_builder() {
        let metric = MetricBuilder::new("request_duration", MetricType::Histogram, "Request duration in seconds")
            .namespace("http")
            .unit(MetricUnit::Seconds)
            .label(Label::new("method"))
            .label(Label::new("status"))
            .build();
        
        assert_eq!(metric.id().full_name(), "http_request_duration");
        assert_eq!(metric.labels().len(), 2);
    }
}

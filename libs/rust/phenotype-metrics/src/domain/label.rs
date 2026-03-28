//! Label types for metrics.

use core::fmt;

/// Label for metrics.
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct Label {
    name: String,
    description: Option<String>,
}

impl Label {
    /// Create a new label.
    pub fn new(name: impl Into<String>) -> Self {
        Self {
            name: name.into(),
            description: None,
        }
    }

    /// Set the description.
    pub fn description(mut self, desc: impl Into<String>) -> Self {
        self.description = Some(desc.into());
        self
    }

    /// Get the label name.
    pub fn name(&self) -> &str {
        &self.name
    }

    /// Get the description.
    pub fn description(&self) -> Option<&str> {
        self.description.as_deref()
    }

    /// Format as Prometheus label (name="value").
    pub fn format(&self, value: &str) -> String {
        format!("{}=\"{}\"", self.name, value)
    }
}

impl fmt::Display for Label {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.name)
    }
}

impl From<&str> for Label {
    fn from(s: &str) -> Self {
        Self::new(s)
    }
}

impl From<String> for Label {
    fn from(s: String) -> Self {
        Self::new(s)
    }
}

/// Label set for a metric observation.
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct LabelSet {
    values: Vec<(String, String)>,
}

impl LabelSet {
    /// Create a new label set.
    pub fn new() -> Self {
        Self {
            values: Vec::new(),
        }
    }

    /// Add a label value.
    pub fn with(mut self, name: impl Into<String>, value: impl Into<String>) -> Self {
        self.values.push((name.into(), value.into()));
        self
    }

    /// Add multiple label values.
    pub fn with_labels(mut self, labels: impl IntoIterator<Item = (String, String)>) -> Self {
        self.values.extend(labels);
        self
    }

    /// Get a value by name.
    pub fn get(&self, name: &str) -> Option<&str> {
        self.values.iter()
            .find(|(n, _)| n == name)
            .map(|(_, v)| v.as_str())
    }

    /// Get all values.
    pub fn values(&self) -> &[(String, String)] {
        &self.values
    }

    /// Format as Prometheus label set.
    pub fn prometheus_format(&self) -> String {
        if self.values.is_empty() {
            String::new()
        } else {
            let parts: Vec<String> = self.values.iter()
                .map(|(n, v)| format!("{}=\"{}\"", n, v))
                .collect();
            format!("{{{}}}", parts.join(","))
        }
    }
}

impl Default for LabelSet {
    fn default() -> Self {
        Self::new()
    }
}

impl From<LabelSet> for Vec<(String, String)> {
    fn from(set: LabelSet) -> Self {
        set.values
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_label() {
        let label = Label::new("method")
            .description("HTTP method");
        
        assert_eq!(label.name(), "method");
        assert_eq!(label.format("GET"), "method=\"GET\"");
    }

    #[test]
    fn test_label_set() {
        let set = LabelSet::new()
            .with("method", "GET")
            .with("status", "200");
        
        assert_eq!(set.get("method"), Some("GET"));
        assert_eq!(set.prometheus_format(), "{method=\"GET\",status=\"200\"}");
    }
}

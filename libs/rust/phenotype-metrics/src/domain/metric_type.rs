//! Metric types for observability.
//!
//! This module contains pure domain types for different metric types.

use core::fmt;

/// Metric types supported by the library.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MetricType {
    /// Counter - monotonically increasing value
    Counter,
    /// Gauge - can go up or down
    Gauge,
    /// Histogram - distribution of values
    Histogram,
    /// Summary - quantile-based aggregation
    Summary,
}

impl MetricType {
    /// Get the Prometheus type name.
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::Counter => "counter",
            Self::Gauge => "gauge",
            Self::Histogram => "histogram",
            Self::Summary => "summary",
        }
    }
}

impl fmt::Display for MetricType {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.as_str())
    }
}

/// Unit of measurement for metrics.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum MetricUnit {
    /// Seconds
    Seconds,
    /// Milliseconds
    Milliseconds,
    /// Microseconds
    Microseconds,
    /// Nanoseconds
    Nanoseconds,
    /// Bytes
    Bytes,
    /// Kilobytes
    Kilobytes,
    /// Megabytes
    Megabytes,
    /// Gigabytes
    Gigabytes,
    /// Percent
    Percent,
    /// Count (no unit)
    Count,
    /// Requests
    Requests,
    /// Errors
    Errors,
    /// Custom unit
    Custom(String),
}

impl MetricUnit {
    /// Parse from string.
    pub fn from_str(s: &str) -> Option<Self> {
        match s.to_lowercase().as_str() {
            "seconds" | "s" => Some(Self::Seconds),
            "milliseconds" | "ms" => Some(Self::Milliseconds),
            "microseconds" | "us" => Some(Self::Microseconds),
            "nanoseconds" | "ns" => Some(Self::Nanoseconds),
            "bytes" | "b" => Some(Self::Bytes),
            "kilobytes" | "kb" => Some(Self::Kilobytes),
            "megabytes" | "mb" => Some(Self::Megabytes),
            "gigabytes" | "gb" => Some(Self::Gigabytes),
            "percent" | "%" => Some(Self::Percent),
            "count" | "c" => Some(Self::Count),
            "requests" | "req" => Some(Self::Requests),
            "errors" | "err" => Some(Self::Errors),
            other => Some(Self::Custom(other.to_string())),
        }
    }

    /// Get the Prometheus unit suffix.
    pub fn suffix(&self) -> &str {
        match self {
            Self::Seconds => "_seconds",
            Self::Milliseconds => "_milliseconds",
            Self::Microseconds => "_microseconds",
            Self::Nanoseconds => "_nanoseconds",
            Self::Bytes => "_bytes",
            Self::Kilobytes => "_kilobytes",
            Self::Megabytes => "_megabytes",
            Self::Gigabytes => "_gigabytes",
            Self::Percent => "_percent",
            Self::Count => "_total",
            Self::Requests => "_requests_total",
            Self::Errors => "_errors_total",
            Self::Custom(_) => "",
        }
    }
}

impl Default for MetricUnit {
    fn default() -> Self {
        Self::Count
    }
}

impl fmt::Display for MetricUnit {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Custom(s) => write!(f, "{}", s),
            Self::Seconds => write!(f, "seconds"),
            Self::Milliseconds => write!(f, "milliseconds"),
            Self::Microseconds => write!(f, "microseconds"),
            Self::Nanoseconds => write!(f, "nanoseconds"),
            Self::Bytes => write!(f, "bytes"),
            Self::Kilobytes => write!(f, "kilobytes"),
            Self::Megabytes => write!(f, "megabytes"),
            Self::Gigabytes => write!(f, "gigabytes"),
            Self::Percent => write!(f, "percent"),
            Self::Count => write!(f, "count"),
            Self::Requests => write!(f, "requests"),
            Self::Errors => write!(f, "errors"),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_metric_type() {
        assert_eq!(MetricType::Counter.as_str(), "counter");
        assert_eq!(MetricType::Gauge.as_str(), "gauge");
    }

    #[test]
    fn test_metric_unit() {
        assert_eq!(MetricUnit::Seconds.suffix(), "_seconds");
        assert_eq!(MetricUnit::Bytes.suffix(), "_bytes");
        assert_eq!(MetricUnit::Count.suffix(), "_total");
    }
}

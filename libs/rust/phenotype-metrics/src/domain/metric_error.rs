//! Metric error types.

use core::fmt;

/// Error codes for metrics errors.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MetricErrorCode {
    /// Metric not found.
    MetricNotFound,
    /// Invalid metric type.
    InvalidMetricType,
    /// Invalid label.
    InvalidLabel,
    /// Registration failed.
    RegistrationFailed,
    /// Recording failed.
    RecordingFailed,
    /// Export failed.
    ExportFailed,
    /// Unknown error.
    Unknown,
}

impl MetricErrorCode {
    /// Convert to string.
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::MetricNotFound => "METRIC_NOT_FOUND",
            Self::InvalidMetricType => "INVALID_METRIC_TYPE",
            Self::InvalidLabel => "INVALID_LABEL",
            Self::RegistrationFailed => "REGISTRATION_FAILED",
            Self::RecordingFailed => "RECORDING_FAILED",
            Self::ExportFailed => "EXPORT_FAILED",
            Self::Unknown => "UNKNOWN",
        }
    }
}

/// Metric error type.
#[derive(Debug)]
pub struct MetricError {
    code: MetricErrorCode,
    message: String,
}

impl MetricError {
    /// Create a new error.
    pub fn new(code: MetricErrorCode, message: impl Into<String>) -> Self {
        Self {
            code,
            message: message.into(),
        }
    }

    /// Get error code.
    pub fn code(&self) -> MetricErrorCode {
        self.code
    }

    /// Get message.
    pub fn message(&self) -> &str {
        &self.message
    }

    /// Create a metric not found error.
    pub fn metric_not_found(name: &str) -> Self {
        Self::new(
            MetricErrorCode::MetricNotFound,
            format!("metric '{}' not found", name),
        )
    }

    /// Create a registration failed error.
    pub fn registration_failed(name: &str, reason: &str) -> Self {
        Self::new(
            MetricErrorCode::RegistrationFailed,
            format!("failed to register metric '{}': {}", name, reason),
        )
    }

    /// Create an invalid label error.
    pub fn invalid_label(name: &str) -> Self {
        Self::new(
            MetricErrorCode::InvalidLabel,
            format!("invalid label '{}'", name),
        )
    }
}

impl fmt::Display for MetricError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "[{}] {}", self.code.as_str(), self.message)
    }
}

impl core::error::Error for MetricError {}

/// Result type for metric operations.
pub type MetricResult<T> = Result<T, MetricError>;

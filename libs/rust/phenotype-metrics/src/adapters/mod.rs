//! Adapters layer - Output adapters for metrics export.
//!
//! This layer contains implementations for exporting metrics to
//! various monitoring systems.

mod prometheus_adapter;
mod statsd_adapter;
mod json_adapter;

pub use prometheus_adapter::PrometheusAdapter;
pub use statsd_adapter::StatsdAdapter;
pub use json_adapter::JsonAdapter;

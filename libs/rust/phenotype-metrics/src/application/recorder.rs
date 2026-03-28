//! Metrics recorder - Convenience trait for recording metrics.
//!
//! This module provides a trait that can be implemented on
//! metric types for convenient recording operations.

use crate::domain::{Counter, Gauge, Histogram, MetricResult, Summary};

/// Trait for recording metrics.
///
/// This trait provides a unified interface for recording
/// different metric types. It can be extended with adapters
/// for different monitoring systems.
pub trait Recorder {
    /// Record a counter increment.
    fn record_counter(&self, name: &str, value: u64) -> MetricResult<()>;

    /// Record a gauge set.
    fn record_gauge(&self, name: &str, value: f64) -> MetricResult<()>;

    /// Record a histogram observation.
    fn record_histogram(&self, name: &str, value: f64) -> MetricResult<()>;

    /// Record a summary observation.
    fn record_summary(&self, name: &str, value: f64) -> MetricResult<()>;
}

/// Extension trait for Counter.
pub trait CounterExt {
    /// Increment by one.
    fn inc(&self) -> MetricResult<()>;

    /// Increment by a value.
    fn inc_by(&self, value: u64) -> MetricResult<()>;
}

impl CounterExt for Counter {
    fn inc(&self) -> MetricResult<()> {
        self.add(1)
    }

    fn inc_by(&self, value: u64) -> MetricResult<()> {
        self.add(value)
    }
}

/// Extension trait for Gauge.
pub trait GaugeExt {
    /// Increment by one.
    fn inc(&self) -> MetricResult<()>;

    /// Increment by a value.
    fn inc_by(&self, value: f64) -> MetricResult<()>;

    /// Decrement by one.
    fn dec(&self) -> MetricResult<()>;

    /// Decrement by a value.
    fn dec_by(&self, value: f64) -> MetricResult<()>;
}

impl GaugeExt for Gauge {
    fn inc(&self) -> MetricResult<()> {
        self.add(1.0)
    }

    fn inc_by(&self, value: f64) -> MetricResult<()> {
        self.add(value)
    }

    fn dec(&self) -> MetricResult<()> {
        self.sub(1.0)
    }

    fn dec_by(&self, value: f64) -> MetricResult<()> {
        self.sub(value)
    }
}

/// Extension trait for Histogram.
pub trait HistogramExt {
    /// Observe a value.
    fn observe(&self, value: f64) -> MetricResult<()>;

    /// Observe with timing.
    fn observe_duration<F>(&self, f: F) -> MetricResult<F::Output>
    where
        F: FnOnce();
}

impl HistogramExt for Histogram {
    fn observe(&self, value: f64) -> MetricResult<()> {
        self.observe(value)
    }

    fn observe_duration<F>(&self, f: F) -> MetricResult<F::Output>
    where
        F: FnOnce(),
    {
        let start = std::time::Instant::now();
        f();
        let duration = start.elapsed().as_secs_f64();
        self.observe(duration)?;
        Ok(f())
    }
}

/// Extension trait for Summary.
pub trait SummaryExt {
    /// Observe a value.
    fn observe(&self, value: f64) -> MetricResult<()>;
}

impl SummaryExt for Summary {
    fn observe(&self, value: f64) -> MetricResult<()> {
        self.observe(value)
    }
}

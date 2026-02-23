//! SLO (Service Level Objective) regulation and monitoring

use serde::{Deserialize, Serialize};

/// Monitors and regulates actions to meet defined Service Level Objectives
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SloRegulator {
    latency_slo_ms: f64,
    error_slo_rate: f64,
    metrics: Vec<ExecutionMetric>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutionMetric {
    pub latency_ms: f64,
    pub success: bool,
}

impl SloRegulator {
    pub fn new(latency_slo_ms: f64, error_slo_rate: f64) -> Self {
        Self {
            latency_slo_ms,
            error_slo_rate,
            metrics: Vec::new(),
        }
    }

    pub fn record_execution(&mut self, latency_ms: f64, success: bool) {
        self.metrics.push(ExecutionMetric { latency_ms, success });
    }

    pub fn is_compliant(&self) -> bool {
        if self.metrics.is_empty() {
            return true;
        }

        // Check last 100 metrics
        let recent: Vec<_> = self.metrics.iter().rev().take(100).collect();
        
        let total_latency: f64 = recent.iter().map(|m| m.latency_ms).sum();
        let avg_latency = total_latency / recent.len() as f64;
        
        let error_count = recent.iter().filter(|m| !m.success).count() as f64;
        let error_rate = error_count / recent.len() as f64;

        avg_latency <= self.latency_slo_ms && error_rate <= self.error_slo_rate
    }

    pub fn metrics_count(&self) -> usize {
        self.metrics.len()
    }

    pub fn clear_metrics(&mut self) {
        self.metrics.clear();
    }
}

#[cfg(feature = "python")]
pub mod python {
    use super::*;
    use pyo3::prelude::*;

    #[pyclass]
    pub struct PySloRegulator {
        inner: SloRegulator,
    }

    #[pymethods]
    impl PySloRegulator {
        #[new]
        fn new(latency_slo_ms: Option<f64>, error_slo_rate: Option<f64>) -> Self {
            Self {
                inner: SloRegulator::new(
                    latency_slo_ms.unwrap_or(500.0),
                    error_slo_rate.unwrap_or(0.01),
                ),
            }
        }

        fn record_execution(&mut self, latency_ms: f64, success: bool) {
            self.inner.record_execution(latency_ms, success);
        }

        fn is_compliant(&self) -> bool {
            self.inner.is_compliant()
        }

        fn metrics_count(&self) -> usize {
            self.inner.metrics_count()
        }

        fn clear_metrics(&mut self) {
            self.inner.clear_metrics();
        }
    }
}

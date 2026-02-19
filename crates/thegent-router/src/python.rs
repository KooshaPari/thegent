//! Python FFI bindings for the Pareto routing engine.
//!
//! Exports Rust types and methods to Python via PyO3:
//! - RiskCalculator: Calculate risk scores from task factors
//! - ParetoRouter: Route tasks based on risk assessment with hysteresis
//! - RoutingMode: Enum for routing modes (Lifecycle, TheGent)
//! - RoutingDecision: Result of a routing decision
//! - RouterMetrics: Metrics from routing decisions

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use crate::risk::{RiskCalculator, RiskFactors, ComplexityLevel};
use crate::router::{ParetoRouter, RouterConfig, RoutingMode, RoutingDecision, RouterMetrics};

/// Routing mode enum exposed to Python.
#[pyclass]
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum PyRoutingMode {
    #[pyo3(name = "LIFECYCLE")]
    Lifecycle,
    #[pyo3(name = "THEGENT")]
    TheGent,
}

impl From<RoutingMode> for PyRoutingMode {
    fn from(mode: RoutingMode) -> Self {
        match mode {
            RoutingMode::Lifecycle => PyRoutingMode::Lifecycle,
            RoutingMode::TheGent => PyRoutingMode::TheGent,
        }
    }
}

impl From<PyRoutingMode> for RoutingMode {
    fn from(mode: PyRoutingMode) -> Self {
        match mode {
            PyRoutingMode::Lifecycle => RoutingMode::Lifecycle,
            PyRoutingMode::TheGent => RoutingMode::TheGent,
        }
    }
}

#[pymethods]
impl PyRoutingMode {
    fn __repr__(&self) -> String {
        match self {
            PyRoutingMode::Lifecycle => "RoutingMode.LIFECYCLE".to_string(),
            PyRoutingMode::TheGent => "RoutingMode.THEGENT".to_string(),
        }
    }
}

/// Complexity level enum exposed to Python.
#[pyclass]
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum PyComplexityLevel {
    #[pyo3(name = "SIMPLE")]
    Simple,
    #[pyo3(name = "MODERATE")]
    Moderate,
    #[pyo3(name = "COMPLEX")]
    Complex,
    #[pyo3(name = "VERY_COMPLEX")]
    VeryComplex,
}

impl From<ComplexityLevel> for PyComplexityLevel {
    fn from(level: ComplexityLevel) -> Self {
        match level {
            ComplexityLevel::Simple => PyComplexityLevel::Simple,
            ComplexityLevel::Moderate => PyComplexityLevel::Moderate,
            ComplexityLevel::Complex => PyComplexityLevel::Complex,
            ComplexityLevel::VeryComplex => PyComplexityLevel::VeryComplex,
        }
    }
}

impl From<PyComplexityLevel> for ComplexityLevel {
    fn from(level: PyComplexityLevel) -> Self {
        match level {
            PyComplexityLevel::Simple => ComplexityLevel::Simple,
            PyComplexityLevel::Moderate => ComplexityLevel::Moderate,
            PyComplexityLevel::Complex => ComplexityLevel::Complex,
            PyComplexityLevel::VeryComplex => ComplexityLevel::VeryComplex,
        }
    }
}

#[pymethods]
impl PyComplexityLevel {
    fn __repr__(&self) -> String {
        match self {
            PyComplexityLevel::Simple => "ComplexityLevel.SIMPLE".to_string(),
            PyComplexityLevel::Moderate => "ComplexityLevel.MODERATE".to_string(),
            PyComplexityLevel::Complex => "ComplexityLevel.COMPLEX".to_string(),
            PyComplexityLevel::VeryComplex => "ComplexityLevel.VERY_COMPLEX".to_string(),
        }
    }
}

/// Risk factors for calculating task risk.
#[pyclass]
pub struct PyRiskFactors {
    complexity: ComplexityLevel,
    cost_cents: usize,
    dependency_count: usize,
    security_sensitive: bool,
    max_cost_cents: usize,
}

#[pymethods]
impl PyRiskFactors {
    /// Create a new RiskFactors with the given complexity level.
    #[new]
    fn new(complexity: PyComplexityLevel) -> Self {
        let factors = RiskFactors::new(complexity.into());
        PyRiskFactors {
            complexity: factors.complexity,
            cost_cents: factors.cost_cents,
            dependency_count: factors.dependency_count,
            security_sensitive: factors.security_sensitive,
            max_cost_cents: factors.max_cost_cents,
        }
    }

    /// Create RiskFactors with all parameters.
    #[staticmethod]
    fn with_all(
        complexity: PyComplexityLevel,
        cost_cents: usize,
        dependency_count: usize,
        security_sensitive: bool,
        max_cost_cents: usize,
    ) -> Self {
        PyRiskFactors {
            complexity: complexity.into(),
            cost_cents,
            dependency_count,
            security_sensitive,
            max_cost_cents,
        }
    }

    fn __repr__(&self) -> String {
        format!(
            "RiskFactors(complexity={:?}, cost={}, deps={}, security={}, max={})",
            self.complexity, self.cost_cents, self.dependency_count, self.security_sensitive, self.max_cost_cents
        )
    }
}

/// Routing decision result.
#[pyclass]
pub struct PyRoutingDecision {
    #[pyo3(get)]
    pub mode: PyRoutingMode,
    #[pyo3(get)]
    pub risk_score: f64,
    #[pyo3(get)]
    pub rationale: String,
}

#[pymethods]
impl PyRoutingDecision {
    fn __repr__(&self) -> String {
        format!(
            "RoutingDecision(mode={:?}, risk_score={:.2}, rationale='{}')",
            self.mode, self.risk_score, self.rationale
        )
    }
}

/// Risk calculator for task risk assessment.
#[pyclass]
pub struct PyRiskCalculator {
    calculator: RiskCalculator,
}

#[pymethods]
impl PyRiskCalculator {
    /// Create a new risk calculator.
    #[new]
    fn new() -> Self {
        PyRiskCalculator {
            calculator: RiskCalculator::new(),
        }
    }

    /// Calculate risk score from risk factors.
    fn calculate(&self, factors: &PyRiskFactors) -> f64 {
        let rust_factors = RiskFactors {
            complexity: factors.complexity,
            cost_cents: factors.cost_cents,
            dependency_count: factors.dependency_count,
            security_sensitive: factors.security_sensitive,
            max_cost_cents: factors.max_cost_cents,
        };
        self.calculator.calculate(&rust_factors)
    }

    fn __repr__(&self) -> String {
        "RiskCalculator()".to_string()
    }
}

/// Router metrics.
#[pyclass]
pub struct PyRouterMetrics {
    #[pyo3(get)]
    pub total_decisions: usize,
    #[pyo3(get)]
    pub lifecycle_count: usize,
    #[pyo3(get)]
    pub thegent_count: usize,
    #[pyo3(get)]
    pub route_changes: usize,
    #[pyo3(get)]
    pub hysteresis_activations: usize,
}

#[pymethods]
impl PyRouterMetrics {
    /// Calculate Lifecycle percentage.
    fn lifecycle_percentage(&self) -> f64 {
        if self.total_decisions == 0 {
            return 0.0;
        }
        (self.lifecycle_count as f64 / self.total_decisions as f64) * 100.0
    }

    /// Calculate TheGent percentage.
    fn thegent_percentage(&self) -> f64 {
        if self.total_decisions == 0 {
            return 0.0;
        }
        (self.thegent_count as f64 / self.total_decisions as f64) * 100.0
    }

    fn __repr__(&self) -> String {
        format!(
            "RouterMetrics(total={}, lifecycle={}, thegent={}, changes={}, hysteresis={})",
            self.total_decisions, self.lifecycle_count, self.thegent_count,
            self.route_changes, self.hysteresis_activations
        )
    }
}

/// Pareto router with hysteresis.
#[pyclass]
pub struct PyParetoRouter {
    router: ParetoRouter,
}

#[pymethods]
impl PyParetoRouter {
    /// Create a new router with default configuration.
    #[new]
    fn new() -> Self {
        PyParetoRouter {
            router: ParetoRouter::new(),
        }
    }

    /// Create a router with custom thresholds.
    #[staticmethod]
    fn with_thresholds(low_threshold: f64, high_threshold: f64) -> PyResult<Self> {
        if low_threshold >= high_threshold {
            return Err(PyValueError::new_err(
                "low_threshold must be less than high_threshold",
            ));
        }
        if low_threshold < 0.0 || low_threshold > 1.0 {
            return Err(PyValueError::new_err("low_threshold must be in [0.0, 1.0]"));
        }
        if high_threshold < 0.0 || high_threshold > 1.0 {
            return Err(PyValueError::new_err("high_threshold must be in [0.0, 1.0]"));
        }

        let config = RouterConfig {
            low_threshold,
            high_threshold,
        };

        Ok(PyParetoRouter {
            router: ParetoRouter::with_config(config),
        })
    }

    /// Route a task based on risk assessment.
    fn route(&self, factors: &PyRiskFactors) -> PyRoutingDecision {
        let rust_factors = RiskFactors {
            complexity: factors.complexity,
            cost_cents: factors.cost_cents,
            dependency_count: factors.dependency_count,
            security_sensitive: factors.security_sensitive,
            max_cost_cents: factors.max_cost_cents,
        };

        let decision = self.router.route(&rust_factors);
        PyRoutingDecision {
            mode: decision.mode.into(),
            risk_score: decision.risk_score,
            rationale: decision.rationale,
        }
    }

    /// Route with session-aware hysteresis.
    fn route_with_session(&self, session_id: &str, factors: &PyRiskFactors) -> PyRoutingDecision {
        let rust_factors = RiskFactors {
            complexity: factors.complexity,
            cost_cents: factors.cost_cents,
            dependency_count: factors.dependency_count,
            security_sensitive: factors.security_sensitive,
            max_cost_cents: factors.max_cost_cents,
        };

        let decision = self.router.route_with_session(session_id, &rust_factors);
        PyRoutingDecision {
            mode: decision.mode.into(),
            risk_score: decision.risk_score,
            rationale: decision.rationale,
        }
    }

    /// Get current metrics.
    fn get_metrics(&self) -> PyRouterMetrics {
        let metrics = self.router.get_metrics();
        PyRouterMetrics {
            total_decisions: metrics.total_decisions,
            lifecycle_count: metrics.lifecycle_count,
            thegent_count: metrics.thegent_count,
            route_changes: metrics.route_changes,
            hysteresis_activations: metrics.hysteresis_activations,
        }
    }

    /// Get Lifecycle percentage.
    fn lifecycle_percentage(&self) -> f64 {
        self.router.lifecycle_percentage()
    }

    fn __repr__(&self) -> String {
        "ParetoRouter()".to_string()
    }
}

/// Python module for thegent_router.
#[pymodule]
fn thegent_router(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyRoutingMode>()?;
    m.add_class::<PyComplexityLevel>()?;
    m.add_class::<PyRiskFactors>()?;
    m.add_class::<PyRoutingDecision>()?;
    m.add_class::<PyRiskCalculator>()?;
    m.add_class::<PyRouterMetrics>()?;
    m.add_class::<PyParetoRouter>()?;

    m.add("__doc__", "Pareto routing engine with hysteresis for task distribution")?;
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;

    Ok(())
}

// SPDX-License-Identifier: MIT OR Apache-2.0
//! PyO3 bindings for thegent-policy.

use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::collections::HashMap;
use std::sync::Arc;

use crate::{ComplianceRule, CostEnforcer, EvaluationContext, PolicyEngine};

/// Python-facing PolicyEngine wrapper.
#[pyclass(name = "PolicyEngine")]
pub struct PyPolicyEngine {
    engine: Arc<PolicyEngine>,
}

#[pymethods]
impl PyPolicyEngine {
    /// Create a PolicyEngine from a TOML config file path.
    #[new]
    fn new(config_path: String) -> PyResult<Self> {
        let engine = PolicyEngine::new(&config_path)
            .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
        Ok(Self {
            engine: Arc::new(engine),
        })
    }

    /// Evaluate a rule by ID against a context dict.
    ///
    /// Args:
    ///     rule_id: The rule identifier (e.g. "FR-GOV-001")
    ///     context: Dict with keys like "cost_per_call", "call_count", "agent_id"
    ///
    /// Returns:
    ///     Dict with "passed" (bool), "reason" (str), "latency_ms" (int), "rule_id" (str)
    fn evaluate(
        &self,
        py: Python<'_>,
        rule_id: String,
        context: HashMap<String, String>,
    ) -> PyResult<Py<PyDict>> {
        let ctx = EvaluationContext::from_map(context);
        let result = self
            .engine
            .evaluate_by_id(&rule_id, &ctx)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;

        let dict = PyDict::new(py);
        dict.set_item("rule_id", result.rule_id)?;
        dict.set_item("passed", result.passed)?;
        dict.set_item("reason", result.reason)?;
        dict.set_item("latency_ms", result.latency_ms)?;
        Ok(dict.into())
    }

    /// Evaluate a rule expression directly (without config lookup).
    ///
    /// Args:
    ///     rule_id: Identifier for the rule
    ///     category: Category string (e.g. "cost_governance")
    ///     expression: Rule expression (e.g. "cost_per_call <= 0.01")
    ///     context: Dict with evaluation context
    ///
    /// Returns:
    ///     Dict with "passed", "reason", "latency_ms", "rule_id"
    fn evaluate_rule(
        &self,
        py: Python<'_>,
        rule_id: String,
        category: String,
        expression: String,
        context: HashMap<String, String>,
    ) -> PyResult<Py<PyDict>> {
        let rule = ComplianceRule {
            id: rule_id,
            category,
            expression,
        };
        let ctx = EvaluationContext::from_map(context);
        let result = self
            .engine
            .evaluate(&rule, &ctx)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;

        let dict = PyDict::new(py);
        dict.set_item("rule_id", result.rule_id)?;
        dict.set_item("passed", result.passed)?;
        dict.set_item("reason", result.reason)?;
        dict.set_item("latency_ms", result.latency_ms)?;
        Ok(dict.into())
    }
}

/// Python-facing CostEnforcer wrapper.
#[pyclass(name = "CostEnforcer")]
pub struct PyCostEnforcer {
    enforcer: CostEnforcer,
}

#[pymethods]
impl PyCostEnforcer {
    #[new]
    fn new(daily_limit: f64) -> Self {
        Self {
            enforcer: CostEnforcer::new(daily_limit),
        }
    }

    /// Check if budget is available for the given amount (does not deduct).
    fn check_budget(&self, amount: f64) -> PyResult<bool> {
        self.enforcer
            .check_budget_available(amount)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))
    }

    /// Attempt to spend the given amount. Returns true if budget allows, false otherwise.
    fn can_spend(&self, amount: f64) -> bool {
        self.enforcer.can_spend(amount)
    }

    /// Get remaining budget.
    fn remaining(&self) -> f64 {
        self.enforcer.remaining()
    }

    /// Reset spent amount to zero.
    fn reset(&self) {
        self.enforcer.reset();
    }
}

/// Register the thegent_policy Python module.
#[pymodule]
pub fn thegent_policy(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyPolicyEngine>()?;
    m.add_class::<PyCostEnforcer>()?;
    Ok(())
}

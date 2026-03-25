//! Policy management module - ported from Python governance/policy.py

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Manages system-wide policies and their evaluation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PolicyManager {
    policies: HashMap<String, serde_json::Value>,
}

impl PolicyManager {
    pub fn new(initial_policies: Option<HashMap<String, serde_json::Value>>) -> Self {
        Self {
            policies: initial_policies.unwrap_or_default(),
        }
    }

    pub fn update(&mut self, new_policies: HashMap<String, serde_json::Value>) {
        self.policies.extend(new_policies);
    }

    pub fn get_policy(&self, key: &str) -> Option<&serde_json::Value> {
        self.policies.get(key)
    }

    pub fn get_policy_f64(&self, key: &str) -> Option<f64> {
        self.policies.get(key).and_then(|v| v.as_f64())
    }

    pub fn get_policy_str(&self, key: &str) -> Option<String> {
        self.policies
            .get(key)
            .and_then(|v| v.as_str().map(String::from))
    }
}

/// Represents an autonomous learning session bounded by policy
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LearningSession {
    policy_manager: PolicyManager,
    cost_cap: f64,
    active: bool,
}

impl LearningSession {
    pub fn new(policy_manager: PolicyManager) -> Self {
        let cost_cap = policy_manager.get_policy_f64("cost_cap").unwrap_or(10.0);
        Self {
            policy_manager,
            cost_cap,
            active: false,
        }
    }

    pub fn start(&mut self) {
        self.active = true;
    }

    pub fn is_valid(&mut self) -> bool {
        // Refresh from policy manager
        if let Some(new_cap) = self.policy_manager.get_policy_f64("cost_cap") {
            self.cost_cap = new_cap;
        }
        self.active
    }

    pub fn cost_cap(&self) -> f64 {
        self.cost_cap
    }

    pub fn is_active(&self) -> bool {
        self.active
    }
}

#[cfg(all(feature = "python", not(test), not(debug_assertions)))]
pub mod python {
    use super::*;
    use pyo3::prelude::*;

    #[pyclass]
    #[derive(Clone)]
    pub struct PyPolicyManager {
        inner: PolicyManager,
    }

    #[pymethods]
    impl PyPolicyManager {
        #[new]
        fn new(initial_policies: Option<HashMap<String, Py<PyAny>>>) -> Self {
            let mut policies = HashMap::new();
            if let Some(initial) = initial_policies {
                Python::with_gil(|py| {
                    for (k, v) in initial {
                        let v = v.bind(py);
                        if let Ok(s) = v.extract::<String>() {
                            policies.insert(k, serde_json::Value::String(s));
                        } else if let Ok(n) = v.extract::<f64>() {
                            policies.insert(k, serde_json::Value::Number(serde_json::Number::from_f64(n).unwrap_or(serde_json::Number::from(0))));
                        } else if let Ok(b) = v.extract::<bool>() {
                            policies.insert(k, serde_json::Value::Bool(b));
                        }
                    }
                });
            }
            Self {
                inner: PolicyManager::new(Some(policies)),
            }
        }

        fn update(&mut self, new_policies: HashMap<String, Py<PyAny>>) {
            let mut converted = HashMap::new();
            Python::with_gil(|py| {
                for (k, v) in new_policies {
                    let v = v.bind(py);
                    if let Ok(s) = v.extract::<String>() {
                        converted.insert(k, serde_json::Value::String(s));
                    } else if let Ok(n) = v.extract::<f64>() {
                        converted.insert(k, serde_json::Value::Number(serde_json::Number::from_f64(n).unwrap_or(serde_json::Number::from(0))));
                    } else if let Ok(b) = v.extract::<bool>() {
                        converted.insert(k, serde_json::Value::Bool(b));
                    }
                }
            });
            self.inner.update(converted);
        }

        fn get_policy(&self, key: &str) -> Option<String> {
            self.inner
                .get_policy(key)
                .and_then(|v| serde_json::to_string(v).ok())
        }
    }

    #[pyclass]
    pub struct PyLearningSession {
        inner: LearningSession,
    }

    #[pymethods]
    impl PyLearningSession {
        #[new]
        fn new(policy_manager: PyPolicyManager) -> Self {
            Self {
                inner: LearningSession::new(policy_manager.inner),
            }
        }

        fn start(&mut self) {
            self.inner.start();
        }

        fn is_valid(&mut self) -> bool {
            self.inner.is_valid()
        }

        fn cost_cap(&self) -> f64 {
            self.inner.cost_cap()
        }

        fn is_active(&self) -> bool {
            self.inner.is_active()
        }
    }
}

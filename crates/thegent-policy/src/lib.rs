//! Policy engine and compliance evaluation for thegent.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

mod compliance;
mod cost_enforcer;
mod engine;
mod errors;
mod evaluator;
#[cfg(feature = "python")]
pub mod python;

pub use compliance::ComplianceChecker;
pub use cost_enforcer::CostEnforcer;
pub use engine::PolicyEngine;
pub use errors::PolicyError;
pub use evaluator::{ComplianceRule, EvaluationContext, EvaluationResult};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct PolicyConfig {
    pub version: String,
    pub policies: Vec<Policy>,
    #[serde(default)]
    pub globals: HashMap<String, String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Policy {
    pub id: String,
    pub category: String,
    pub rules: Vec<String>,
    pub enabled: bool,
}

//! Policy engine and compliance evaluation for thegent.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

mod compliance;
mod cost_enforcer;
mod engine;
mod errors;
mod evaluator;
mod policy;
#[cfg(all(feature = "python", not(test), not(debug_assertions)))]
pub mod python;
mod slo;
mod trust;

pub use compliance::ComplianceChecker;
pub use cost_enforcer::CostEnforcer;
pub use engine::PolicyEngine;
pub use errors::PolicyError;
pub use evaluator::{ComplianceRule, EvaluationContext, EvaluationResult};
pub use policy::{LearningSession, PolicyManager};
pub use slo::SloRegulator;
pub use trust::{EvaluationResult as TrustEvaluationResult, TrustBoundaryChecker, TrustLevel};

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

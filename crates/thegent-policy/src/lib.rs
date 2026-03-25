//! Policy engine and compliance evaluation for thegent.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

mod compliance;
mod cost_enforcer;
mod engine;
mod errors;
mod evaluator;
mod policy;
mod slo;
mod trust;
#[cfg(all(feature = "python", not(test), not(debug_assertions)))]
pub mod python;

pub use compliance::ComplianceChecker;
pub use cost_enforcer::CostEnforcer;
pub use engine::PolicyEngine;
pub use errors::PolicyError;
pub use evaluator::{ComplianceRule, EvaluationContext, EvaluationResult};
pub use policy::{PolicyManager, LearningSession};
pub use slo::SloRegulator;
pub use trust::{TrustBoundaryChecker, TrustLevel, EvaluationResult as TrustEvaluationResult};

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

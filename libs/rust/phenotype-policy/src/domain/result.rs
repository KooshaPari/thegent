//! Evaluation Result - The result of evaluating a policy or rule.

use std::collections::HashMap;
use chrono::{DateTime, Utc};

use super::Effect;

/// The result of a policy evaluation.
#[derive(Debug, Clone)]
pub struct EvaluationResult {
    /// The decision (ALLOW or DENY)
    decision: Decision,
    /// The policy/rule that produced this result
    policy_name: String,
    /// Timestamp of evaluation
    evaluated_at: DateTime<Utc>,
    /// Additional metadata
    metadata: HashMap<String, String>,
}

/// The decision made by a policy evaluation.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Decision {
    /// The request is allowed
    Allow,
    /// The request is denied
    Deny,
    /// The policy doesn't apply to this request
    NotApplicable,
    /// An error occurred during evaluation
    Indeterminate,
}

impl EvaluationResult {
    /// Create a new evaluation result.
    pub fn new(effect: Effect, policy_name: impl Into<String>) -> Self {
        let decision = match effect {
            Effect::Allow => Decision::Allow,
            Effect::Deny => Decision::Deny,
            Effect::NotApplicable => Decision::NotApplicable,
            Effect::Indeterminate => Decision::Indeterminate,
        };

        Self {
            decision,
            policy_name: policy_name.into(),
            evaluated_at: Utc::now(),
            metadata: HashMap::new(),
        }
    }

    /// Create an ALLOW result.
    pub fn allow(policy_name: impl Into<String>) -> Self {
        Self::new(Effect::Allow, policy_name)
    }

    /// Create a DENY result.
    pub fn deny(policy_name: impl Into<String>) -> Self {
        Self::new(Effect::Deny, policy_name)
    }

    /// Create a NOT_APPLICABLE result.
    pub fn not_applicable(policy_name: impl Into<String>) -> Self {
        Self::new(Effect::NotApplicable, policy_name)
    }

    /// Create an INDETERMINATE result.
    pub fn indeterminate(policy_name: impl Into<String>) -> Self {
        Self::new(Effect::Indeterminate, policy_name)
    }

    /// Get the decision.
    pub fn decision(&self) -> Decision {
        self.decision
    }

    /// Check if the result is ALLOW.
    pub fn is_allowed(&self) -> bool {
        self.decision == Decision::Allow
    }

    /// Check if the result is DENY.
    pub fn is_denied(&self) -> bool {
        self.decision == Decision::Deny
    }

    /// Check if the policy didn't apply.
    pub fn is_not_applicable(&self) -> bool {
        self.decision == Decision::NotApplicable
    }

    /// Check if there was an error.
    pub fn is_indeterminate(&self) -> bool {
        self.decision == Decision::Indeterminate
    }

    /// Get the policy name.
    pub fn policy_name(&self) -> &str {
        &self.policy_name
    }

    /// Get the evaluation timestamp.
    pub fn evaluated_at(&self) -> DateTime<Utc> {
        self.evaluated_at
    }

    /// Add metadata.
    pub fn with_metadata(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.metadata.insert(key.into(), value.into());
        self
    }

    /// Get metadata.
    pub fn metadata(&self) -> &HashMap<String, String> {
        &self.metadata
    }

    /// Combine this result with another using deny-overrides.
    pub fn combine_deny_overrides(self, other: EvaluationResult) -> Self {
        match (self.decision, other.decision) {
            (Decision::Deny, _) | (_, Decision::Deny) => {
                EvaluationResult::deny(format!("{} AND {}", self.policy_name, other.policy_name))
            }
            (Decision::Indeterminate, _) | (_, Decision::Indeterminate) => {
                EvaluationResult::indeterminate(format!("{} AND {}", self.policy_name, other.policy_name))
            }
            (Decision::Allow, _) | (_, Decision::Allow) => {
                EvaluationResult::allow(format!("{} AND {}", self.policy_name, other.policy_name))
            }
            _ => EvaluationResult::not_applicable("all-not-applicable"),
        }
    }

    /// Combine this result with another using permit-overrides.
    pub fn combine_permit_overrides(self, other: EvaluationResult) -> Self {
        match (self.decision, other.decision) {
            (Decision::Allow, _) | (_, Decision::Allow) => {
                EvaluationResult::allow(format!("{} OR {}", self.policy_name, other.policy_name))
            }
            (Decision::Indeterminate, _) | (_, Decision::Indeterminate) => {
                EvaluationResult::indeterminate(format!("{} OR {}", self.policy_name, other.policy_name))
            }
            (Decision::Deny, _) | (_, Decision::Deny) => {
                EvaluationResult::deny(format!("{} OR {}", self.policy_name, other.policy_name))
            }
            _ => EvaluationResult::not_applicable("all-not-applicable"),
        }
    }
}

impl Default for Decision {
    fn default() -> Self {
        Decision::NotApplicable
    }
}

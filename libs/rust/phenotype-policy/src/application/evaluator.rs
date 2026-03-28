//! Policy Evaluator - Evaluates policies against context.
//!
//! The evaluator is the core component that makes authorization decisions.

use std::sync::Arc;

use crate::domain::{
    Effect, EvaluationResult, Policy, PolicyContext, PolicyError, PolicyResult, Rule,
};

/// Policy evaluator - Makes authorization decisions.
pub struct PolicyEvaluator {
    /// Combining algorithm to use
    combining_algorithm: CombiningAlgorithm,
}

/// Combining algorithms determine how multiple rules/policies are combined.
#[derive(Debug, Clone, Copy)]
pub enum CombiningAlgorithm {
    /// Deny-overrides: If any rule denies, the result is deny
    DenyOverrides,
    /// Permit-overrides: If any rule permits, the result is permit
    PermitOverrides,
    /// First-applicable: First applicable rule wins
    FirstApplicable,
    /// Only-one-applicable: Only one rule can apply
    OnlyOneApplicable,
}

impl Default for CombiningAlgorithm {
    fn default() -> Self {
        CombiningAlgorithm::DenyOverrides
    }
}

impl PolicyEvaluator {
    /// Create a new policy evaluator with default settings.
    pub fn new() -> Self {
        Self {
            combining_algorithm: CombiningAlgorithm::default(),
        }
    }

    /// Create with a specific combining algorithm.
    pub fn with_algorithm(algorithm: CombiningAlgorithm) -> Self {
        Self { combining_algorithm: algorithm }
    }

    /// Evaluate a single policy against a context.
    pub fn evaluate_policy(
        &self,
        policy: &Policy,
        context: &dyn PolicyContext,
    ) -> PolicyResult<EvaluationResult> {
        if policy.rules().is_empty() {
            // No rules - use the policy's default effect
            return Ok(EvaluationResult::new(policy.effect(), policy.name()));
        }

        let mut results: Vec<EvaluationResult> = Vec::new();

        for rule in policy.rules() {
            let result = self.evaluate_rule(rule, context);
            results.push(result);
        }

        let combined = self.combine_results(results, policy.name());
        Ok(combined)
    }

    /// Evaluate a single rule against a context.
    pub fn evaluate_rule(
        &self,
        rule: &Rule,
        context: &dyn PolicyContext,
    ) -> EvaluationResult {
        rule.evaluate(context)
    }

    /// Evaluate multiple policies against a context.
    pub fn evaluate_policies(
        &self,
        policies: &[Arc<Policy>],
        context: &dyn PolicyContext,
    ) -> PolicyResult<EvaluationResult> {
        if policies.is_empty() {
            return Err(PolicyError::evaluation_error("No policies to evaluate"));
        }

        let mut results: Vec<EvaluationResult> = Vec::new();

        for policy in policies {
            // Check if policy target matches
            if let Some(target) = policy.target() {
                let resource = context.get("resource.id").unwrap_or_default();
                let action = context.get("action").unwrap_or_default();
                let subject = context.get("subject.id").unwrap_or_default();

                if !target.matches(&resource, &action, &subject) {
                    continue;
                }
            }

            let result = self.evaluate_policy(policy, context)?;
            results.push(result);
        }

        if results.is_empty() {
            // No policies applied - default to deny for safety
            return Ok(EvaluationResult::deny("no-applicable-policies"));
        }

        let combined = self.combine_results(results, "policy-set");
        Ok(combined)
    }

    /// Combine multiple evaluation results.
    fn combine_results(
        &self,
        results: Vec<EvaluationResult>,
        name: &str,
    ) -> EvaluationResult {
        match self.combining_algorithm {
            CombiningAlgorithm::DenyOverrides => {
                results.into_iter().fold(
                    EvaluationResult::not_applicable("start"),
                    |acc, r| acc.combine_deny_overrides(r),
                )
            }
            CombiningAlgorithm::PermitOverrides => {
                results.into_iter().fold(
                    EvaluationResult::not_applicable("start"),
                    |acc, r| acc.combine_permit_overrides(r),
                )
            }
            CombiningAlgorithm::FirstApplicable => {
                results.into_iter()
                    .find(|r| !r.is_not_applicable())
                    .unwrap_or_else(|| EvaluationResult::not_applicable(name))
            }
            CombiningAlgorithm::OnlyOneApplicable => {
                let applicable: Vec<_> = results.into_iter()
                    .filter(|r| !r.is_not_applicable())
                    .collect();
                
                if applicable.len() == 1 {
                    applicable.into_iter().next().unwrap()
                } else if applicable.is_empty() {
                    EvaluationResult::not_applicable(name)
                } else {
                    EvaluationResult::indeterminate("multiple-applicable")
                }
            }
        }
    }
}

impl Default for PolicyEvaluator {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::domain::{PolicyContext, SimpleContext};

    fn create_test_policy() -> Policy {
        Policy::allow("test-policy")
            .with_rule(Rule::allow("rule1"))
            .with_rule(Rule::deny("rule2"))
    }

    #[test]
    fn test_deny_overrides() {
        let evaluator = PolicyEvaluator::with_algorithm(CombiningAlgorithm::DenyOverrides);
        let policy = create_test_policy();
        let context = SimpleContext::new();

        let result = evaluator.evaluate_policy(&policy, &context).unwrap();

        // Deny-overrides should return Deny because rule2 is Deny
        assert!(result.is_denied());
    }

    #[test]
    fn test_permit_overrides() {
        let evaluator = PolicyEvaluator::with_algorithm(CombiningAlgorithm::PermitOverrides);
        let policy = create_test_policy();
        let context = SimpleContext::new();

        let result = evaluator.evaluate_policy(&policy, &context).unwrap();

        // Permit-overrides should return Allow because rule1 is Allow
        assert!(result.is_allowed());
    }

    #[test]
    fn test_first_applicable() {
        let evaluator = PolicyEvaluator::with_algorithm(CombiningAlgorithm::FirstApplicable);
        let policy = create_test_policy();
        let context = SimpleContext::new();

        let result = evaluator.evaluate_policy(&policy, &context).unwrap();

        // First-applicable should return the first applicable rule
        assert!(result.is_allowed());
    }
}

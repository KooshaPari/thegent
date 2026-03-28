//! Policy Engine SDK - High-level policy evaluation API.

use std::sync::Arc;

use crate::application::{PolicyEvaluator, PolicyRegistry, CombiningAlgorithm};
use crate::domain::{Policy, PolicyContext, EvaluationResult, PolicyResult};

/// Policy Engine - High-level API for policy evaluation.
///
/// This is the main entry point for the SDK.
pub struct PolicyEngine {
    /// The policy evaluator
    evaluator: PolicyEvaluator,
    /// The policy registry
    registry: Arc<PolicyRegistry>,
}

impl PolicyEngine {
    /// Create a new policy engine.
    pub fn new() -> Self {
        Self {
            evaluator: PolicyEvaluator::new(),
            registry: Arc::new(PolicyRegistry::new()),
        }
    }

    /// Create with a specific combining algorithm.
    pub fn with_algorithm(algorithm: CombiningAlgorithm) -> Self {
        Self {
            evaluator: PolicyEvaluator::with_algorithm(algorithm),
            registry: Arc::new(PolicyRegistry::new()),
        }
    }

    /// Create with a pre-configured registry.
    pub fn with_registry(registry: Arc<PolicyRegistry>) -> Self {
        Self {
            evaluator: PolicyEvaluator::new(),
            registry,
        }
    }

    /// Register a policy.
    pub fn register(&self, policy: Policy) -> PolicyResult<()> {
        self.registry.register(policy)
    }

    /// Evaluate a request against a specific policy.
    pub fn evaluate_policy(
        &self,
        policy_name: &str,
        context: &dyn PolicyContext,
    ) -> PolicyResult<EvaluationResult> {
        let policy = self.registry.get(policy_name)?;
        self.evaluator.evaluate_policy(&policy, context)
    }

    /// Evaluate a request against all registered policies.
    pub fn evaluate(&self, context: &dyn PolicyContext) -> PolicyResult<EvaluationResult> {
        let policies = self.registry.get_all()?;
        self.evaluator.evaluate_policies(&policies, context)
    }

    /// Evaluate against a policy set.
    pub fn evaluate_policy_set(
        &self,
        set_name: &str,
        context: &dyn PolicyContext,
    ) -> PolicyResult<EvaluationResult> {
        let policies = self.registry.get_policy_set(set_name)?;
        self.evaluator.evaluate_policies(&policies, context)
    }

    /// Check if a request is allowed.
    pub fn is_allowed(
        &self,
        context: &dyn PolicyContext,
    ) -> PolicyResult<bool> {
        Ok(self.evaluate(context)?.is_allowed())
    }

    /// Get the policy registry.
    pub fn registry(&self) -> Arc<PolicyRegistry> {
        Arc::clone(&self.registry)
    }
}

impl Default for PolicyEngine {
    fn default() -> Self {
        Self::new()
    }
}

/// Extension trait for building contexts fluently.
pub trait ContextBuilder {
    fn subject(self, id: &str, role: &str) -> Self;
    fn resource(self, resource_type: &str, id: &str) -> Self;
    fn action(self, action: &str) -> Self;
    fn environment(self, key: &str, value: &str) -> Self;
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::domain::{PolicyContext, SimpleContext, Policy, Effect, Rule};

    #[test]
    fn test_simple_evaluation() {
        let engine = PolicyEngine::new();

        let policy = Policy::allow("test-policy")
            .with_rule(Rule::allow("test-rule"));

        engine.register(policy).unwrap();

        let context = SimpleContext::new()
            .with_subject("user:123", "admin")
            .with_resource("todo", "todo:456")
            .with_action("read");

        let result = engine.evaluate(&context).unwrap();
        assert!(result.is_allowed());
    }

    #[test]
    fn test_is_allowed() {
        let engine = PolicyEngine::new();

        let policy = Policy::allow("read-policy");
        engine.register(policy).unwrap();

        let context = SimpleContext::new();
        let is_allowed = engine.is_allowed(&context).unwrap();
        assert!(is_allowed);
    }
}

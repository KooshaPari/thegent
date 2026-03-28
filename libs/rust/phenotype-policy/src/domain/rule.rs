//! Rule - A single rule within a policy.
//!
//! Rules are the building blocks of policies.

use std::fmt::Debug;

use super::{Condition, Effect, EvaluationResult};

/// Rule - A single authorization rule.
///
/// A rule consists of:
/// - A name
/// - An effect (ALLOW or DENY)
/// - A condition that must be satisfied
#[derive(Debug, Clone)]
pub struct Rule {
    /// Rule name
    name: String,
    /// The effect of this rule
    effect: Effect,
    /// The condition that must be satisfied
    condition: Option<Condition>,
    /// Description
    description: Option<String>,
}

impl Rule {
    /// Create a new rule.
    pub fn new(name: impl Into<String>, effect: Effect) -> Self {
        Self {
            name: name.into(),
            effect,
            condition: None,
            description: None,
        }
    }

    /// Create an ALLOW rule.
    pub fn allow(name: impl Into<String>) -> Self {
        Self::new(name, Effect::Allow)
    }

    /// Create a DENY rule.
    pub fn deny(name: impl Into<String>) -> Self {
        Self::new(name, Effect::Deny)
    }

    /// Get the name.
    pub fn name(&self) -> &str {
        &self.name
    }

    /// Get the effect.
    pub fn effect(&self) -> Effect {
        self.effect
    }

    /// Get the condition.
    pub fn condition(&self) -> Option<&Condition> {
        self.condition.as_ref()
    }

    /// Set the condition.
    pub fn with_condition<C>(mut self, condition: C) -> Self
    where
        C: Fn(&dyn super::PolicyContext) -> bool + 'static,
    {
        self.condition = Some(Condition::new(condition));
        self
    }

    /// Set the description.
    pub fn with_description(mut self, description: impl Into<String>) -> Self {
        self.description = Some(description.into());
        self
    }

    /// Evaluate this rule against a context.
    pub fn evaluate(&self, ctx: &dyn super::PolicyContext) -> EvaluationResult {
        match &self.condition {
            Some(cond) => {
                if cond.evaluate(ctx) {
                    EvaluationResult::new(self.effect, self.name.clone())
                } else {
                    EvaluationResult::not_applicable(self.name.clone())
                }
            }
            None => EvaluationResult::new(self.effect, self.name.clone()),
        }
    }
}

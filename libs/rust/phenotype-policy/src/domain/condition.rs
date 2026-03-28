//! Condition - Represents a condition that must be satisfied for a rule.
//!
//! Conditions are functions that evaluate to true or false based on context.

use std::fmt::Debug;

/// A condition is a predicate that evaluates against a policy context.
#[derive(Debug, Clone)]
pub struct Condition {
    /// The condition function
    evaluator: Box<dyn Fn(&dyn super::PolicyContext) -> bool + Send + Sync>,
}

impl Condition {
    /// Create a new condition from a function.
    pub fn new<F>(evaluator: F) -> Self
    where
        F: Fn(&dyn super::PolicyContext) -> bool + Send + Sync + 'static,
    {
        Self {
            evaluator: Box::new(evaluator),
        }
    }

    /// Evaluate this condition against a context.
    pub fn evaluate(&self, ctx: &dyn super::PolicyContext) -> bool {
        (self.evaluator)(ctx)
    }
}

impl<F> From<F> for Condition
where
    F: Fn(&dyn super::PolicyContext) -> bool + Send + Sync + 'static,
{
    fn from(evaluator: F) -> Self {
        Self::new(evaluator)
    }
}

/// Combinators for combining conditions.
impl Condition {
    /// Logical AND of two conditions.
    pub fn and(self, other: Condition) -> Self {
        let a = self.evaluator;
        let b = other.evaluator;
        Self::new(move |ctx| a(ctx) && b(ctx))
    }

    /// Logical OR of two conditions.
    pub fn or(self, other: Condition) -> Self {
        let a = self.evaluator;
        let b = other.evaluator;
        Self::new(move |ctx| a(ctx) || b(ctx))
    }

    /// Logical NOT of this condition.
    pub fn not(self) -> Self {
        let a = self.evaluator;
        Self::new(move |ctx| !a(ctx))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::domain::PolicyContext;

    struct MockContext {
        values: std::collections::HashMap<String, String>,
    }

    impl PolicyContext for MockContext {
        fn get(&self, key: &str) -> Option<String> {
            self.values.get(key).cloned()
        }
    }

    #[test]
    fn test_simple_condition() {
        let cond = Condition::new(|ctx| {
            ctx.get("role").map(|r| r == "admin").unwrap_or(false)
        });

        let ctx = MockContext {
            values: vec![("role".to_string(), "admin".to_string())]
                .into_iter()
                .collect(),
        };

        assert!(cond.evaluate(&ctx));
    }

    #[test]
    fn test_and_condition() {
        let cond1 = Condition::new(|ctx| ctx.get("role") == Some("admin".to_string()));
        let cond2 = Condition::new(|ctx| ctx.get("action") == Some("delete".to_string()));

        let combined = cond1.and(cond2);

        let ctx = MockContext {
            values: vec![
                ("role".to_string(), "admin".to_string()),
                ("action".to_string(), "delete".to_string()),
            ]
            .into_iter()
            .collect(),
        };

        assert!(combined.evaluate(&ctx));
    }

    #[test]
    fn test_not_condition() {
        let cond = Condition::new(|ctx| ctx.get("role") == Some("admin".to_string()));
        let neg = cond.not();

        let ctx = MockContext {
            values: vec![("role".to_string(), "user".to_string())]
                .into_iter()
                .collect(),
        };

        assert!(neg.evaluate(&ctx));
    }
}

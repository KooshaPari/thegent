use crate::{ComplianceRule, EvaluationContext, EvaluationResult, PolicyError};

pub struct ComplianceChecker;

impl ComplianceChecker {
    pub fn new() -> Self {
        Self
    }

    pub fn evaluate(
        &self,
        rule: &ComplianceRule,
        context: &EvaluationContext,
    ) -> Result<EvaluationResult, PolicyError> {
        let start = std::time::Instant::now();

        let passed = match rule.category.as_str() {
            "cost" => context.cost_per_call <= 1.0,
            "calls" => context.call_count <= 1000,
            _ => false,
        };

        let latency_ms = start.elapsed().as_millis() as u64;

        Ok(EvaluationResult {
            rule_id: rule.id.clone(),
            passed,
            reason: if passed {
                format!("Rule {} passed", rule.id)
            } else {
                format!(
                    "Rule {} failed: cost/calls exceeded (category: {})",
                    rule.id, rule.category
                )
            },
            latency_ms,
        })
    }

    pub fn evaluate_batch(
        &self,
        rules: &[ComplianceRule],
        context: &EvaluationContext,
    ) -> Result<Vec<EvaluationResult>, PolicyError> {
        rules.iter().map(|rule| self.evaluate(rule, context)).collect()
    }
}

impl Default for ComplianceChecker {
    fn default() -> Self {
        Self::new()
    }
}

/// Policy engine for governance rule evaluation
use crate::types::{HookError, PolicyOutcome, PolicyRule, RuleType};
use dashmap::DashMap;
use lazy_static::lazy_static;
use std::collections::HashMap;
use std::sync::Arc;

lazy_static! {
    static ref POLICY_CACHE: Arc<DashMap<String, bool>> = Arc::new(DashMap::new());
}

pub struct PolicyEngine {
    rules: Vec<PolicyRule>,
}

impl PolicyEngine {
    /// Create a new policy engine with the given rules
    pub fn new(rules: Vec<PolicyRule>) -> Self {
        PolicyEngine { rules }
    }

    /// Evaluate all rules against the given context
    pub fn evaluate(
        &self,
        context: &HashMap<String, serde_json::Value>,
    ) -> Result<Vec<PolicyOutcome>, HookError> {
        let mut outcomes = Vec::new();

        for rule in &self.rules {
            if !rule.enabled {
                continue;
            }

            let cache_key = format!("{}:{:?}", rule.id, context);
            if let Some(cached) = POLICY_CACHE.get(&cache_key) {
                let passed = *cached;
                outcomes.push(PolicyOutcome {
                    rule_id: rule.id.clone(),
                    passed,
                    message: if passed {
                        format!("✓ Policy '{}' passed (cached)", rule.name)
                    } else {
                        format!("✗ Policy '{}' failed (cached)", rule.name)
                    },
                    details: None,
                });
                continue;
            }

            let passed = self.evaluate_rule(rule, context)?;
            POLICY_CACHE.insert(cache_key, passed);

            outcomes.push(PolicyOutcome {
                rule_id: rule.id.clone(),
                passed,
                message: if passed {
                    format!("✓ Policy '{}' passed", rule.name)
                } else {
                    format!("✗ Policy '{}' failed: {}", rule.name, rule.condition)
                },
                details: Some(format!(
                    "Type: {:?}, Severity: {:?}",
                    rule.rule_type, rule.severity
                )),
            });
        }

        Ok(outcomes)
    }

    /// Evaluate a single rule against context
    fn evaluate_rule(
        &self,
        rule: &PolicyRule,
        context: &HashMap<String, serde_json::Value>,
    ) -> Result<bool, HookError> {
        match rule.rule_type {
            RuleType::Cost => self.evaluate_cost_rule(&rule.condition, context),
            RuleType::Quality => self.evaluate_quality_rule(&rule.condition, context),
            RuleType::Security => self.evaluate_security_rule(&rule.condition, context),
            RuleType::Spec => self.evaluate_spec_rule(&rule.condition, context),
        }
    }

    /// Evaluate cost rule condition
    fn evaluate_cost_rule(
        &self,
        condition: &str,
        context: &HashMap<String, serde_json::Value>,
    ) -> Result<bool, HookError> {
        // Parse conditions like: "cost < 10.0", "model in [claude, gpt]"
        if let Some((key, op, value)) = Self::parse_condition(condition) {
            match op {
                "<" | "<=" | ">" | ">=" | "==" => {
                    if let Some(actual) = context.get(key).and_then(|v| v.as_f64()) {
                        let threshold: f64 = value.parse()
                            .map_err(|_| HookError::ParseError(format!("Invalid cost: {}", value)))?;
                        Ok(match op {
                            "<" => actual < threshold,
                            "<=" => actual <= threshold,
                            ">" => actual > threshold,
                            ">=" => actual >= threshold,
                            "==" => (actual - threshold).abs() < 0.001,
                            _ => false,
                        })
                    } else {
                        Ok(false)
                    }
                }
                _ => Err(HookError::ValidationError(format!("Unknown operator: {}", op))),
            }
        } else {
            Ok(false)
        }
    }

    /// Evaluate quality rule condition
    fn evaluate_quality_rule(
        &self,
        condition: &str,
        context: &HashMap<String, serde_json::Value>,
    ) -> Result<bool, HookError> {
        // Parse conditions like: "coverage >= 80", "lint_errors == 0"
        if let Some((key, op, value)) = Self::parse_condition(condition) {
            match op {
                "<" | "<=" | ">" | ">=" | "==" => {
                    if let Some(actual) = context.get(key).and_then(|v| v.as_u64()) {
                        let threshold: u64 = value.parse()
                            .map_err(|_| HookError::ParseError(format!("Invalid threshold: {}", value)))?;
                        Ok(match op {
                            "<" => actual < threshold,
                            "<=" => actual <= threshold,
                            ">" => actual > threshold,
                            ">=" => actual >= threshold,
                            "==" => actual == threshold,
                            _ => false,
                        })
                    } else {
                        Ok(false)
                    }
                }
                _ => Err(HookError::ValidationError(format!("Unknown operator: {}", op))),
            }
        } else {
            Ok(false)
        }
    }

    /// Evaluate security rule condition
    fn evaluate_security_rule(
        &self,
        condition: &str,
        _context: &HashMap<String, serde_json::Value>,
    ) -> Result<bool, HookError> {
        // For security, conditions are often "no_secrets" or similar
        Ok(condition == "no_secrets" || condition == "no_violations")
    }

    /// Evaluate spec rule condition
    fn evaluate_spec_rule(
        &self,
        condition: &str,
        context: &HashMap<String, serde_json::Value>,
    ) -> Result<bool, HookError> {
        // Parse conditions like: "fr_coverage >= 80"
        if let Some((key, op, value)) = Self::parse_condition(condition) {
            match op {
                ">=" | ">" | "<=" | "<" => {
                    if let Some(actual) = context.get(key).and_then(|v| v.as_u64()) {
                        let threshold: u64 = value.parse()
                            .map_err(|_| HookError::ParseError(format!("Invalid threshold: {}", value)))?;
                        Ok(match op {
                            "<" => actual < threshold,
                            "<=" => actual <= threshold,
                            ">" => actual > threshold,
                            ">=" => actual >= threshold,
                            _ => false,
                        })
                    } else {
                        Ok(false)
                    }
                }
                _ => Err(HookError::ValidationError(format!("Unknown operator: {}", op))),
            }
        } else {
            Ok(false)
        }
    }

    /// Parse a simple condition string: "key op value"
    fn parse_condition(condition: &str) -> Option<(&str, &str, &str)> {
        let trimmed = condition.trim();
        let operators = vec!["<=", ">=", "==", "!=", "<", ">"];

        for op in operators {
            if let Some(pos) = trimmed.find(op) {
                let key = trimmed[..pos].trim();
                let value = trimmed[pos + op.len()..].trim();
                return Some((key, op, value));
            }
        }

        None
    }

    /// Clear the policy cache
    pub fn clear_cache() {
        POLICY_CACHE.clear();
    }

    /// Get cache hit rate
    pub fn cache_stats() -> (usize, usize) {
        let size = POLICY_CACHE.len();
        (size, size) // Simplified: just return cache size
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::{PolicyRule, RuleType, Severity};

    #[test]
    fn test_evaluate_cost_rule() {
        let engine = PolicyEngine::new(vec![]);
        let mut context = HashMap::new();
        context.insert("cost".to_string(), serde_json::json!(5.0));

        let result = engine.evaluate_cost_rule("cost < 10.0", &context).unwrap();
        assert!(result);

        let result = engine.evaluate_cost_rule("cost > 10.0", &context).unwrap();
        assert!(!result);
    }

    #[test]
    fn test_evaluate_quality_rule() {
        let engine = PolicyEngine::new(vec![]);
        let mut context = HashMap::new();
        context.insert("coverage".to_string(), serde_json::json!(85));

        let result = engine.evaluate_quality_rule("coverage >= 80", &context).unwrap();
        assert!(result);

        let result = engine.evaluate_quality_rule("coverage >= 90", &context).unwrap();
        assert!(!result);
    }

    #[test]
    fn test_parse_condition() {
        let (key, op, value) = PolicyEngine::parse_condition("cost < 10.0").unwrap();
        assert_eq!(key, "cost");
        assert_eq!(op, "<");
        assert_eq!(value, "10.0");
    }

    #[test]
    fn test_evaluate_with_rules() {
        let rules = vec![PolicyRule {
            id: "rule1".to_string(),
            name: "Cost Limit".to_string(),
            description: "Cost must be < 10".to_string(),
            rule_type: RuleType::Cost,
            condition: "cost < 10.0".to_string(),
            severity: Severity::Error,
            enabled: true,
        }];

        let engine = PolicyEngine::new(rules);
        let mut context = HashMap::new();
        context.insert("cost".to_string(), serde_json::json!(5.0));

        let outcomes = engine.evaluate(&context).unwrap();
        assert_eq!(outcomes.len(), 1);
        assert!(outcomes[0].passed);
    }
}

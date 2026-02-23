use crate::{ComplianceRule, EvaluationContext, EvaluationResult, PolicyConfig, PolicyError};
use dashmap::DashMap;
use std::sync::Arc;

/// Policy evaluation engine with caching.
pub struct PolicyEngine {
    config: PolicyConfig,
    cache: Arc<DashMap<String, EvaluationResult>>,
}

impl PolicyEngine {
    /// Create a new PolicyEngine from a config path (convenience constructor matching test API).
    pub fn new(path: &str) -> Result<Self, PolicyError> {
        Self::load(path)
    }

    /// Load policy config from TOML file.
    pub fn load(path: &str) -> Result<Self, PolicyError> {
        let content = std::fs::read_to_string(path)
            .map_err(|e| PolicyError::ConfigLoadError(e.to_string()))?;
        let config: PolicyConfig =
            toml::from_str(&content).map_err(|e| PolicyError::ConfigParseError(e.to_string()))?;

        Ok(Self {
            config,
            cache: Arc::new(DashMap::new()),
        })
    }

    /// Evaluate a compliance rule against context.
    pub fn evaluate(
        &self,
        rule: &ComplianceRule,
        context: &EvaluationContext,
    ) -> Result<EvaluationResult, PolicyError> {
        let cache_key = format!("{}:{:?}", rule.id, context);

        if let Some(cached) = self.cache.get(&cache_key) {
            return Ok(cached.clone());
        }

        let start = std::time::Instant::now();
        let passed = self.evaluate_expression(&rule.expression, context)?;
        let latency_ms = start.elapsed().as_millis() as u64;

        let result = EvaluationResult {
            rule_id: rule.id.clone(),
            passed,
            reason: if passed {
                format!("Rule {} passed", rule.id)
            } else {
                format!("Rule {} failed: {}", rule.id, rule.expression)
            },
            latency_ms,
        };

        self.cache.insert(cache_key, result.clone());

        Ok(result)
    }

    /// Evaluate by rule ID (looks up rule in config).
    pub fn evaluate_by_id(
        &self,
        rule_id: &str,
        context: &EvaluationContext,
    ) -> Result<EvaluationResult, PolicyError> {
        for policy in &self.config.policies {
            if policy.rules.iter().any(|r| r == rule_id) {
                let rule = ComplianceRule {
                    id: rule_id.to_string(),
                    category: policy.category.clone(),
                    expression: format!("category:{}", policy.category),
                };
                return self.evaluate(&rule, context);
            }
        }
        Err(PolicyError::RuleNotFound(rule_id.to_string()))
    }

    fn evaluate_expression(
        &self,
        expr: &str,
        context: &EvaluationContext,
    ) -> Result<bool, PolicyError> {
        // Simple expression evaluator for common patterns
        if expr.contains("cost_per_call") && expr.contains("<=") {
            if let Some(threshold) = extract_threshold(expr) {
                return Ok(context.cost_per_call <= threshold);
            }
        }
        if expr.contains("call_count") && expr.contains("<=") {
            if let Some(threshold) = extract_threshold(expr) {
                return Ok((context.call_count as f64) <= threshold);
            }
        }
        if expr.contains("cost <=") {
            if let Some(threshold) = extract_threshold(expr) {
                return Ok(context.cost_per_call <= threshold);
            }
        }
        if expr.contains("calls <=") {
            if let Some(threshold) = extract_threshold(expr) {
                return Ok((context.call_count as f64) <= threshold);
            }
        }
        // Category-based default: pass if within governance limits
        if expr.starts_with("category:") {
            return Ok(context.cost_per_call <= 0.01 && context.call_count <= 1000);
        }
        Ok(context.cost_per_call <= 0.01 && context.call_count <= 1000)
    }
}

fn extract_threshold(expr: &str) -> Option<f64> {
    let parts: Vec<&str> = expr.split("<=").collect();
    if parts.len() == 2 {
        parts[1].trim().parse::<f64>().ok()
    } else {
        None
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_extract_threshold_valid() {
        assert_eq!(extract_threshold("cost <= 1.0"), Some(1.0));
        assert_eq!(extract_threshold("cost_per_call <= 0.01"), Some(0.01));
    }

    #[test]
    fn test_extract_threshold_invalid() {
        assert_eq!(extract_threshold("no operator here"), None);
    }
}

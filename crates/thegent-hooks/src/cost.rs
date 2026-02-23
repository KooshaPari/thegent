/// Cost estimation for various LLM providers
use crate::types::{CostEstimate, HookError};
use std::collections::HashMap;

pub struct CostCalculator {
    pricing: HashMap<String, ModelPricing>,
}

#[derive(Clone, Debug)]
struct ModelPricing {
    input_cost_per_mtok: f64, // Cost per million tokens
    output_cost_per_mtok: f64,
}

impl CostCalculator {
    /// Create a new cost calculator with default pricing
    pub fn new() -> Self {
        let mut pricing = HashMap::new();

        // Claude models
        pricing.insert(
            "claude-opus-4.6".to_string(),
            ModelPricing {
                input_cost_per_mtok: 15.0,
                output_cost_per_mtok: 75.0,
            },
        );
        pricing.insert(
            "claude-sonnet-4.6".to_string(),
            ModelPricing {
                input_cost_per_mtok: 3.0,
                output_cost_per_mtok: 15.0,
            },
        );
        pricing.insert(
            "claude-haiku-4.5".to_string(),
            ModelPricing {
                input_cost_per_mtok: 0.8,
                output_cost_per_mtok: 4.0,
            },
        );

        // GPT models
        pricing.insert(
            "gpt-5".to_string(),
            ModelPricing {
                input_cost_per_mtok: 3.0,
                output_cost_per_mtok: 12.0,
            },
        );
        pricing.insert(
            "gpt-5-mini".to_string(),
            ModelPricing {
                input_cost_per_mtok: 0.15,
                output_cost_per_mtok: 0.6,
            },
        );

        // Gemini models
        pricing.insert(
            "gemini-3-flash".to_string(),
            ModelPricing {
                input_cost_per_mtok: 0.075,
                output_cost_per_mtok: 0.3,
            },
        );

        CostCalculator { pricing }
    }

    /// Calculate cost for a given model and token counts
    pub fn calculate(
        &self,
        model: &str,
        input_tokens: u32,
        output_tokens: u32,
    ) -> Result<CostEstimate, HookError> {
        let pricing = self
            .pricing
            .get(model)
            .ok_or_else(|| HookError::UnknownModel(model.to_string()))?;

        let input_cost = (input_tokens as f64 / 1_000_000.0) * pricing.input_cost_per_mtok;
        let output_cost = (output_tokens as f64 / 1_000_000.0) * pricing.output_cost_per_mtok;
        let total_cost = input_cost + output_cost;

        Ok(CostEstimate {
            model: model.to_string(),
            input_tokens,
            output_tokens,
            input_cost_usd: input_cost,
            output_cost_usd: output_cost,
            total_cost_usd: total_cost,
        })
    }

    /// Add custom pricing for a model
    pub fn add_model_pricing(
        &mut self,
        model: &str,
        input_cost_per_mtok: f64,
        output_cost_per_mtok: f64,
    ) {
        self.pricing.insert(
            model.to_string(),
            ModelPricing {
                input_cost_per_mtok,
                output_cost_per_mtok,
            },
        );
    }

    /// Get list of known models
    pub fn known_models(&self) -> Vec<String> {
        self.pricing.keys().cloned().collect()
    }

    /// Calculate cost-to-value ratio (lower is better)
    pub fn cost_to_value_ratio(&self, model: &str, quality_score: f64) -> Result<f64, HookError> {
        if quality_score <= 0.0 {
            return Err(HookError::ValidationError(
                "Quality score must be > 0".to_string(),
            ));
        }

        // Base cost estimate: 1000 input, 500 output tokens
        let estimate = self.calculate(model, 1000, 500)?;
        Ok(estimate.total_cost_usd / quality_score)
    }
}

impl Default for CostCalculator {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_calculate_cost_known_model() {
        let calc = CostCalculator::new();
        let estimate = calc.calculate("claude-haiku-4.5", 1000, 500).unwrap();

        assert_eq!(estimate.model, "claude-haiku-4.5");
        assert_eq!(estimate.input_tokens, 1000);
        assert_eq!(estimate.output_tokens, 500);
        assert!(estimate.input_cost_usd > 0.0);
        assert!(estimate.output_cost_usd > 0.0);
    }

    #[test]
    fn test_calculate_cost_unknown_model() {
        let calc = CostCalculator::new();
        let result = calc.calculate("unknown-model", 1000, 500);
        assert!(result.is_err());
    }

    #[test]
    fn test_add_custom_model() {
        let mut calc = CostCalculator::new();
        calc.add_model_pricing("custom-model", 5.0, 10.0);

        let estimate = calc.calculate("custom-model", 1000, 500).unwrap();
        assert_eq!(estimate.model, "custom-model");
        assert!((estimate.input_cost_usd - 0.005).abs() < 0.0001);
    }

    #[test]
    fn test_cost_accuracy_within_5_percent() {
        let calc = CostCalculator::new();
        let estimate = calc.calculate("claude-haiku-4.5", 1000, 500).unwrap();

        // Verify cost calculation is accurate
        let expected_input = (1000.0 / 1_000_000.0) * 0.8;
        let expected_output = (500.0 / 1_000_000.0) * 4.0;

        assert!((estimate.input_cost_usd - expected_input).abs() < 0.00001);
        assert!((estimate.output_cost_usd - expected_output).abs() < 0.00001);
    }

    #[test]
    fn test_known_models() {
        let calc = CostCalculator::new();
        let models = calc.known_models();
        assert!(models.contains(&"claude-haiku-4.5".to_string()));
        assert!(models.contains(&"gemini-3-flash".to_string()));
        assert!(models.len() >= 6);
    }
}

/// Configuration loading and parsing
use crate::types::{HookConfig, HookError, PolicyRule, QualityThresholds, SecurityRule};
use serde_json::Value;
use std::fs;
use std::path::Path;

pub struct ConfigLoader;

impl ConfigLoader {
    /// Load configuration from YAML or JSON file
    pub fn load<P: AsRef<Path>>(path: P) -> Result<HookConfig, HookError> {
        let path = path.as_ref();
        let contents = fs::read_to_string(path)
            .map_err(|e| HookError::IoError(format!("Failed to read config file: {}", e)))?;

        let extension = path.extension().and_then(|s| s.to_str()).unwrap_or("json");

        match extension {
            "yaml" | "yml" => Self::parse_yaml(&contents),
            "json" => Self::parse_json(&contents),
            _ => Err(HookError::ParseError("Unsupported file format".to_string())),
        }
    }

    /// Parse YAML configuration
    fn parse_yaml(contents: &str) -> Result<HookConfig, HookError> {
        let value: serde_yaml::Value =
            serde_yaml::from_str(contents).map_err(|e| HookError::YamlError(e.to_string()))?;

        let json_value =
            serde_json::to_value(&value).map_err(|e| HookError::JsonError(e.to_string()))?;

        Self::parse_config_value(&json_value)
    }

    /// Parse JSON configuration
    fn parse_json(contents: &str) -> Result<HookConfig, HookError> {
        let value: Value =
            serde_json::from_str(contents).map_err(|e| HookError::JsonError(e.to_string()))?;

        Self::parse_config_value(&value)
    }

    /// Parse configuration from JSON value
    fn parse_config_value(value: &Value) -> Result<HookConfig, HookError> {
        let policies = value
            .get("policies")
            .and_then(|v| v.as_array())
            .map(|arr| {
                arr.iter()
                    .filter_map(|p| serde_json::from_value::<PolicyRule>(p.clone()).ok())
                    .collect()
            })
            .unwrap_or_default();

        let quality_thresholds = value
            .get("quality_thresholds")
            .and_then(|v| serde_json::from_value::<QualityThresholds>(v.clone()).ok())
            .unwrap_or(QualityThresholds::default());

        let security_rules = value
            .get("security_rules")
            .and_then(|v| v.as_array())
            .map(|arr| {
                arr.iter()
                    .filter_map(|s| serde_json::from_value::<SecurityRule>(s.clone()).ok())
                    .collect()
            })
            .unwrap_or_default();

        let cost_limits = value
            .get("cost_limits")
            .and_then(|v| {
                let obj = v.as_object()?;
                let mut limits = std::collections::HashMap::new();
                for (k, v) in obj.iter() {
                    if let Some(cost) = v.as_f64() {
                        limits.insert(k.clone(), cost);
                    }
                }
                Some(limits)
            })
            .unwrap_or_default();

        Ok(HookConfig {
            policies,
            cost_limits,
            quality_thresholds,
            security_rules,
        })
    }
}

impl Default for QualityThresholds {
    fn default() -> Self {
        QualityThresholds {
            min_coverage: 80.0,
            max_lint_errors: 0,
            max_cyclomatic_complexity: 10,
            max_cognitive_complexity: 15,
            max_function_lines: 40,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_empty_config() {
        let json = "{}";
        let config = ConfigLoader::parse_json(json).unwrap();
        assert_eq!(config.policies.len(), 0);
        assert_eq!(config.cost_limits.len(), 0);
    }

    #[test]
    fn test_parse_config_with_policies() {
        let json = r#"
        {
            "policies": [
                {
                    "id": "p1",
                    "name": "Test Policy",
                    "description": "A test",
                    "rule_type": "cost",
                    "condition": "true",
                    "severity": "error",
                    "enabled": true
                }
            ]
        }
        "#;
        let config = ConfigLoader::parse_json(json).unwrap();
        assert_eq!(config.policies.len(), 1);
        assert_eq!(config.policies[0].id, "p1");
    }
}

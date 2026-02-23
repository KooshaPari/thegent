use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ComplianceRule {
    pub id: String,
    pub category: String,
    pub expression: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default, PartialEq)]
pub struct EvaluationContext {
    pub cost_per_call: f64,
    pub call_count: u64,
    pub agent_id: String,
    pub timestamp: String,
}

impl EvaluationContext {
    pub fn from_map(map: HashMap<String, String>) -> Self {
        Self {
            cost_per_call: map
                .get("cost_per_call")
                .and_then(|v| v.parse().ok())
                .unwrap_or(0.0),
            call_count: map
                .get("call_count")
                .and_then(|v| v.parse().ok())
                .unwrap_or(0),
            agent_id: map.get("agent_id").cloned().unwrap_or_default(),
            timestamp: map.get("timestamp").cloned().unwrap_or_default(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct EvaluationResult {
    pub rule_id: String,
    pub passed: bool,
    pub reason: String,
    pub latency_ms: u64,
}

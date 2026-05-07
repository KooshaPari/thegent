use regex::Regex;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashMap;
use std::sync::OnceLock;

/// Spiral configuration output structure.
#[derive(Serialize)]
pub struct SpiralConfigOutput {
    pub source: String,
    pub max_failed_tests: String,
    pub max_flaky_tests: String,
    pub max_missing_test_pairs: String,
    pub max_missing_test_types: String,
    pub max_test_evidence_age_minutes: String,
    pub max_build_evidence_age_minutes: String,
    pub max_e2e_evidence_age_minutes: String,
    pub streak_trigger: String,
    pub require_e2e_first: String,
    pub require_env_ready_first: String,
}

impl Default for SpiralConfigOutput {
    fn default() -> Self {
        Self {
            source: "defaults".to_string(),
            max_failed_tests: "10".to_string(),
            max_flaky_tests: "8".to_string(),
            max_missing_test_pairs: "0".to_string(),
            max_missing_test_types: "0".to_string(),
            max_test_evidence_age_minutes: "90".to_string(),
            max_build_evidence_age_minutes: "90".to_string(),
            max_e2e_evidence_age_minutes: "180".to_string(),
            streak_trigger: "2".to_string(),
            require_e2e_first: "true".to_string(),
            require_env_ready_first: "true".to_string(),
        }
    }
}

/// Spiral metric record from spiral.json.
#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct SpiralMetricRecord {
    pub generated_at: String,
    #[serde(default)]
    pub session_id: String,
    #[serde(default)]
    pub status: String,
    #[serde(default)]
    pub severity: String,
    #[serde(default)]
    pub reason: String,
    #[serde(default)]
    pub violations: i64,
    #[serde(default)]
    pub streak: i64,
    #[serde(default)]
    pub interrupt: bool,
    #[serde(default)]
    pub metrics: Value,
}

impl Default for SpiralMetricRecord {
    fn default() -> Self {
        Self {
            generated_at: String::new(),
            session_id: String::new(),
            status: String::new(),
            severity: String::new(),
            reason: String::new(),
            violations: 0,
            streak: 0,
            interrupt: false,
            metrics: Value::Null,
        }
    }
}

/// Spiral trend analysis output.
#[derive(Serialize)]
pub struct SpiralTrendOutput {
    pub source_file: String,
    pub samples_total: usize,
    pub window_used: usize,
    pub breach_count: usize,
    pub breach_rate: f64,
    pub interrupt_count: usize,
    pub max_streak: i64,
    pub open_breach_streak: usize,
    pub mttr_proxy_cycles: Option<f64>,
    pub violations_delta: i64,
    pub stale_test_evidence_events: usize,
    pub stale_build_evidence_events: usize,
    pub stale_e2e_evidence_events: usize,
    pub pressure_score: f64,
    pub policy_band: String,
    pub latest_status: String,
    pub latest_severity: String,
    pub latest_generated_at: String,
}

/// Spiral selector canonicalization output.
#[derive(Serialize)]
pub struct SpiralSelectorOutput {
    pub raw: String,
    pub cleaned_raw: String,
    pub canonical: String,
    pub selected_mode: bool,
}

/// Parse spiral config from TOML content.
pub fn parse_spiral_config(content: &str) -> SpiralConfigOutput {
    let mut config = SpiralConfigOutput::default();
    config.source = "parsed".to_string();

    // Simple TOML parsing for [spiral] section
    let in_spiral = Regex::new(r"(?m)^\[spiral\]").unwrap();
    let key_value = Regex::new(r"(?m)^(\w+)\s*=\s*(.+)").unwrap();

    if in_spiral.is_match(content) {
        for cap in key_value.captures_iter(content) {
            if let (Some(key), Some(val)) = (cap.get(1), cap.get(2)) {
                let k = key.as_str();
                let v = val.as_str().trim_matches('"').trim();
                match k {
                    "max_failed_tests" => config.max_failed_tests = v.to_string(),
                    "max_flaky_tests" => config.max_flaky_tests = v.to_string(),
                    "max_missing_test_pairs" => config.max_missing_test_pairs = v.to_string(),
                    "max_missing_test_types" => config.max_missing_test_types = v.to_string(),
                    "max_test_evidence_age_minutes" => {
                        config.max_test_evidence_age_minutes = v.to_string()
                    }
                    "max_build_evidence_age_minutes" => {
                        config.max_build_evidence_age_minutes = v.to_string()
                    }
                    "max_e2e_evidence_age_minutes" => {
                        config.max_e2e_evidence_age_minutes = v.to_string()
                    }
                    "streak_trigger" => config.streak_trigger = v.to_string(),
                    "require_e2e_first" => config.require_e2e_first = v.to_string(),
                    "require_env_ready_first" => config.require_env_ready_first = v.to_string(),
                    _ => {}
                }
            }
        }
    }

    config
}

/// Build trend data from spiral records.
pub fn build_spiral_trend(
    records: &[SpiralMetricRecord],
    window: usize,
) -> SpiralTrendOutput {
    let samples_total = records.len();
    let window_used = window.min(samples_total);
    let window_records = if window > 0 {
        &records[records.len().saturating_sub(window_used)..]
    } else {
        records
    };

    let breach_count = window_records
        .iter()
        .filter(|r| r.status == "breach" || r.severity == "error")
        .count();
    let breach_rate = if window_used > 0 {
        breach_count as f64 / window_used as f64
    } else {
        0.0
    };

    let interrupt_count = window_records.iter().filter(|r| r.interrupt).count();
    let max_streak = window_records
        .iter()
        .map(|r| r.streak)
        .max()
        .unwrap_or(0);

    let latest = window_records.last();

    SpiralTrendOutput {
        source_file: String::new(),
        samples_total,
        window_used,
        breach_count,
        breach_rate,
        interrupt_count,
        max_streak,
        open_breach_streak: 0,
        mttr_proxy_cycles: None,
        violations_delta: 0,
        stale_test_evidence_events: 0,
        stale_build_evidence_events: 0,
        stale_e2e_evidence_events: 0,
        pressure_score: 0.0,
        policy_band: String::new(),
        latest_status: latest.map(|r| r.status.clone()).unwrap_or_default(),
        latest_severity: latest.map(|r| r.severity.clone()).unwrap_or_default(),
        latest_generated_at: latest
            .map(|r| r.generated_at.clone())
            .unwrap_or_default(),
    }
}

/// Canonicalize a spiral selector string.
pub fn canonicalize_selector(raw: &str) -> SpiralSelectorOutput {
    let cleaned = raw.trim().to_string();
    let canonical = cleaned
        .to_lowercase()
        .replace(" ", "_")
        .replace("-", "_");

    let selected_mode = canonical.contains("selected")
        || canonical.contains("mode")
        || canonical.contains("strict");

    SpiralSelectorOutput {
        raw: raw.to_string(),
        cleaned_raw: cleaned,
        canonical,
        selected_mode,
    }
}

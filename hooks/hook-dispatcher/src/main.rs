use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::{BTreeSet, HashMap};
use std::env;
use std::fs;
use std::io::{BufRead, BufReader, IsTerminal, Read, Write};
use std::path::{Path, PathBuf};
use std::process::{Command, ExitCode, Stdio};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};
use regex::Regex;
use std::sync::OnceLock;

mod contract;
mod dispatch;
mod governance_fs;
mod io;

use crate::contract::{HookInput, Mode};
use crate::dispatch::dispatch_notification;
use crate::governance_fs::{count_ai_slop, count_todos, scan_deep_nesting, scan_large_files, scan_secrets};
use crate::io::{find_in_path, first_available, resolve_hooks_dir};

// ---------------------------------------------------------------------------
// Secret scanning types and registry (BKM-07)
// ---------------------------------------------------------------------------

/// A named secret pattern entry: (type_name, compiled regex).
struct SecretPattern {
    kind: &'static str,
    regex: Regex,
}

/// A single secret match found during scanning.
#[derive(Serialize)]
struct SecretMatch {
    /// Human-readable type label (e.g. "openai_api_key").
    kind: String,
    /// 1-based line number of the match.
    line: usize,
    /// Masked version of the matched text (never the raw secret).
    masked: String,
}

/// Top-level JSON output for `hook-dispatcher scan-secrets`.
#[derive(Serialize)]
struct ScanSecretsOutput {
    found: bool,
    matches: Vec<SecretMatch>,
}

/// Return the lazily-initialized list of named secret patterns.
fn get_named_secret_patterns() -> &'static Vec<SecretPattern> {
    static PATTERNS: OnceLock<Vec<SecretPattern>> = OnceLock::new();
    PATTERNS.get_or_init(|| {
        vec![
            SecretPattern { kind: "openai_api_key",    regex: Regex::new(r"sk-[a-zA-Z0-9]{48}").unwrap() },
            SecretPattern { kind: "openai_proj_key",   regex: Regex::new(r"sk-proj-[a-zA-Z0-9_-]{48,}").unwrap() },
            SecretPattern { kind: "anthropic_api_key", regex: Regex::new(r"sk-ant-[a-zA-Z0-9_-]{90,}").unwrap() },
            SecretPattern { kind: "google_cloud_key",  regex: Regex::new(r"AIza[0-9A-Za-z\-_]{35}").unwrap() },
            SecretPattern { kind: "slack_token",       regex: Regex::new(r"xox[baprs]-[0-9A-Za-z\-]{10,}").unwrap() },
            SecretPattern { kind: "private_key_block", regex: Regex::new(r"-----BEGIN [A-Z ]+ PRIVATE KEY-----").unwrap() },
            SecretPattern { kind: "square_access_token", regex: Regex::new(r"sq0atp-[0-9A-Za-z\-_]{22}").unwrap() },
            SecretPattern { kind: "aws_access_key_id", regex: Regex::new(r"AKIA[0-9A-Z]{16}").unwrap() },
            SecretPattern { kind: "aws_secret_key_context", regex: Regex::new(r"(?i)(aws_secret_access_key|secret_access_key)\s*[=:]\s*\S{20,}").unwrap() },
            SecretPattern { kind: "github_pat",        regex: Regex::new(r"ghp_[a-zA-Z0-9]{36}").unwrap() },
            SecretPattern { kind: "github_oauth",      regex: Regex::new(r"gho_[a-zA-Z0-9]{36}").unwrap() },
            SecretPattern { kind: "github_app_token",  regex: Regex::new(r"ghs_[a-zA-Z0-9]{36}").unwrap() },
            SecretPattern { kind: "generic_hex_secret", regex: Regex::new(r"(?i)(password|secret|token|api[_-]?key)\s*[=:]\s*[0-9a-f]{20,}").unwrap() },
            SecretPattern { kind: "generic_base64_secret", regex: Regex::new(r"(?i)(password|secret|token|api[_-]?key)\s*[=:]\s*[A-Za-z0-9+/]{32,}={0,2}").unwrap() },
        ]
    })
}

/// Mask a matched string: keep first 4 chars + `****` + last 2 chars if long enough.
fn mask_secret(matched: &str) -> String {
    let chars: Vec<char> = matched.chars().collect();
    if chars.len() <= 8 {
        return "****".to_string();
    }
    let prefix: String = chars[..4].iter().collect();
    let suffix: String = chars[chars.len() - 2..].iter().collect();
    format!("{prefix}****{suffix}")
}

/// Scan `content` line-by-line for secrets. Returns all matches with masking.
fn scan_content_for_secrets(content: &str) -> Vec<SecretMatch> {
    let patterns = get_named_secret_patterns();
    let mut matches: Vec<SecretMatch> = Vec::new();

    for (line_idx, line) in content.lines().enumerate() {
        let line_no = line_idx + 1;
        for pat in patterns {
            if let Some(m) = pat.regex.find(line) {
                matches.push(SecretMatch {
                    kind: pat.kind.to_string(),
                    line: line_no,
                    masked: mask_secret(m.as_str()),
                });
                // One match per pattern per line is enough
                break;
            }
        }
    }

    matches
}

/// Backward-compat helper used by run_governance_scan: returns count of files with secrets.
fn get_secret_regexes() -> &'static Vec<Regex> {
    static SECRET_REGEXES: OnceLock<Vec<Regex>> = OnceLock::new();
    SECRET_REGEXES.get_or_init(|| {
        get_named_secret_patterns()
            .iter()
            .map(|p| Regex::new(p.regex.as_str()).unwrap())
            .collect()
    })
}

// ---------------------------------------------------------------------------
// Governance scanning types and rules (BKM-11)
// ---------------------------------------------------------------------------

/// A single governance violation found during file scanning.
#[derive(Serialize)]
struct GovernanceViolation {
    /// Rule ID that was violated (e.g. "noqa-no-justification").
    rule: String,
    /// Severity level: "error", "warning", or "info".
    severity: String,
    /// 1-based line number of the violation.
    line: usize,
    /// Human-readable description of the violation.
    message: String,
}

/// Top-level JSON output for `hook-dispatcher governance scan`.
#[derive(Serialize)]
struct GovernanceScanOutput {
    /// Total number of violations found.
    violation_count: usize,
    /// The list of individual violations.
    violations: Vec<GovernanceViolation>,
}

#[derive(Serialize)]
struct SpiralConfigOutput {
    source: String,
    max_failed_tests: String,
    max_flaky_tests: String,
    max_missing_test_pairs: String,
    max_missing_test_types: String,
    max_test_evidence_age_minutes: String,
    max_build_evidence_age_minutes: String,
    max_e2e_evidence_age_minutes: String,
    streak_trigger: String,
    require_e2e_first: String,
    require_env_ready_first: String,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
struct SpiralMetricRecord {
    generated_at: String,
    #[serde(default)]
    session_id: String,
    #[serde(default)]
    status: String,
    #[serde(default)]
    severity: String,
    #[serde(default)]
    reason: String,
    #[serde(default)]
    violations: i64,
    #[serde(default)]
    streak: i64,
    #[serde(default)]
    interrupt: bool,
    #[serde(default)]
    metrics: Value,
}

#[derive(Serialize)]
struct SpiralTrendOutput {
    source_file: String,
    samples_total: usize,
    window_used: usize,
    breach_count: usize,
    breach_rate: f64,
    interrupt_count: usize,
    max_streak: i64,
    open_breach_streak: usize,
    mttr_proxy_cycles: Option<f64>,
    violations_delta: i64,
    stale_test_evidence_events: usize,
    stale_build_evidence_events: usize,
    stale_e2e_evidence_events: usize,
    pressure_score: f64,
    policy_band: String,
    latest_status: String,
    latest_severity: String,
    latest_generated_at: String,
}

#[derive(Serialize)]
struct SpiralSelectorOutput {
    raw: String,
    cleaned_raw: String,
    canonical: String,
    selected_mode: bool,
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

fn read_spiral_metrics(path: &str) -> Vec<SpiralMetricRecord> {
    let content = match fs::read_to_string(path) {
        Ok(c) => c,
        Err(_) => return Vec::new(),
    };

    content
        .lines()
        .filter_map(|line| {
            if line.trim().is_empty() {
                return None;
            }
            serde_json::from_str::<SpiralMetricRecord>(line).ok()
        })
        .collect()
}

fn build_spiral_trend(records: &[SpiralMetricRecord], source_file: &str, window: usize) -> SpiralTrendOutput {
    if records.is_empty() {
        return SpiralTrendOutput {
            source_file: source_file.to_string(),
            samples_total: 0,
            window_used: 0,
            breach_count: 0,
            breach_rate: 0.0,
            interrupt_count: 0,
            max_streak: 0,
            open_breach_streak: 0,
            mttr_proxy_cycles: None,
            violations_delta: 0,
            stale_test_evidence_events: 0,
            stale_build_evidence_events: 0,
            stale_e2e_evidence_events: 0,
            pressure_score: 0.0,
            policy_band: "green".to_string(),
            latest_status: "none".to_string(),
            latest_severity: "none".to_string(),
            latest_generated_at: String::new(),
        };
    }

    let window_used = window.min(records.len());
    let slice = &records[records.len() - window_used..];

    let mut breach_count = 0usize;
    let mut interrupt_count = 0usize;
    let mut max_streak = 0i64;
    let mut recovery_segments: Vec<usize> = Vec::new();
    let mut current_breach_run = 0usize;

    for rec in slice {
        if rec.violations > 0 {
            breach_count += 1;
            current_breach_run += 1;
        } else if current_breach_run > 0 {
            recovery_segments.push(current_breach_run);
            current_breach_run = 0;
        }
        if rec.interrupt {
            interrupt_count += 1;
        }
        if rec.streak > max_streak {
            max_streak = rec.streak;
        }
    }

    let open_breach_streak = current_breach_run;
    let mttr_proxy_cycles = if recovery_segments.is_empty() {
        None
    } else {
        let sum: usize = recovery_segments.iter().sum();
        Some(sum as f64 / recovery_segments.len() as f64)
    };

    let first = slice.first().unwrap();
    let last = slice.last().unwrap();
    let breach_rate = if window_used == 0 {
        0.0
    } else {
        breach_count as f64 / window_used as f64
    };

    let stale_event_count = |key: &str| -> usize {
        slice
            .iter()
            .filter(|rec| {
                rec.metrics
                    .get(key)
                    .and_then(|v| v.as_i64())
                    .map(|v| v > 0)
                    .unwrap_or(false)
            })
            .count()
    };

    let stale_test_evidence_events = stale_event_count("stale_test_evidence");
    let stale_build_evidence_events = stale_event_count("stale_build_evidence");
    let stale_e2e_evidence_events = stale_event_count("stale_e2e_evidence");

    let interrupt_rate = if window_used == 0 {
        0.0
    } else {
        interrupt_count as f64 / window_used as f64
    };
    let stale_total = stale_test_evidence_events + stale_build_evidence_events + stale_e2e_evidence_events;
    let stale_rate = if window_used == 0 {
        0.0
    } else {
        stale_total as f64 / (window_used as f64 * 3.0)
    };
    let streak_pressure = if max_streak <= 0 {
        0.0
    } else {
        (max_streak as f64 / 3.0).min(1.0)
    };
    let violations_delta_pressure = if last.violations > first.violations {
        ((last.violations - first.violations) as f64 / 3.0).min(1.0)
    } else {
        0.0
    };
    let pressure_score =
        (0.40 * breach_rate) +
        (0.20 * interrupt_rate) +
        (0.20 * stale_rate) +
        (0.15 * streak_pressure) +
        (0.05 * violations_delta_pressure);
    let policy_band = if pressure_score >= 0.75 {
        "red"
    } else if pressure_score >= 0.45 {
        "yellow"
    } else {
        "green"
    };

    SpiralTrendOutput {
        source_file: source_file.to_string(),
        samples_total: records.len(),
        window_used,
        breach_count,
        breach_rate,
        interrupt_count,
        max_streak,
        open_breach_streak,
        mttr_proxy_cycles,
        violations_delta: last.violations - first.violations,
        stale_test_evidence_events,
        stale_build_evidence_events,
        stale_e2e_evidence_events,
        pressure_score,
        policy_band: policy_band.to_string(),
        latest_status: last.status.clone(),
        latest_severity: last.severity.clone(),
        latest_generated_at: last.generated_at.clone(),
    }
}

fn canonicalize_selector_csv(raw: &str) -> SpiralSelectorOutput {
    let cleaned_raw: String = raw.chars().filter(|c| !c.is_whitespace()).collect();
    let mut set = BTreeSet::<String>::new();
    if !cleaned_raw.is_empty() {
        for token in cleaned_raw.split(',') {
            if token.is_empty() {
                continue;
            }
            set.insert(token.to_string());
        }
    }
    let canonical = set.into_iter().collect::<Vec<_>>().join(",");
    SpiralSelectorOutput {
        raw: raw.to_string(),
        cleaned_raw: cleaned_raw.clone(),
        canonical,
        selected_mode: !cleaned_raw.is_empty(),
    }
}

fn parse_spiral_config_from_hook_yaml(content: &str) -> SpiralConfigOutput {
    let mut cfg = SpiralConfigOutput::default();
    let mut in_settings = false;
    let mut in_spiral = false;

    for raw in content.lines() {
        let line = raw.trim_end();
        if line.trim().is_empty() || line.trim_start().starts_with('#') {
            continue;
        }
        if !in_settings {
            if line.trim() == "settings:" {
                in_settings = true;
            }
            continue;
        }
        if line.trim() == "hooks:" {
            break;
        }
        if !in_spiral {
            if line.starts_with("  regression_spiral_guard:") {
                in_spiral = true;
            }
            continue;
        }
        // next top-level setting under settings block
        if line.starts_with("  ") && !line.starts_with("    ") {
            in_spiral = false;
            continue;
        }
        if !line.starts_with("    ") {
            continue;
        }
        let mut parts = line.trim().splitn(2, ':');
        let key = parts.next().unwrap_or("").trim();
        let value = parts.next().unwrap_or("").trim();
        if value.is_empty() {
            continue;
        }
        match key {
            "max_failed_tests" => cfg.max_failed_tests = value.to_string(),
            "max_flaky_tests" => cfg.max_flaky_tests = value.to_string(),
            "max_missing_test_pairs" => cfg.max_missing_test_pairs = value.to_string(),
            "max_missing_test_types" => cfg.max_missing_test_types = value.to_string(),
            "max_test_evidence_age_minutes" => cfg.max_test_evidence_age_minutes = value.to_string(),
            "max_build_evidence_age_minutes" => cfg.max_build_evidence_age_minutes = value.to_string(),
            "max_e2e_evidence_age_minutes" => cfg.max_e2e_evidence_age_minutes = value.to_string(),
            "streak_trigger" => cfg.streak_trigger = value.to_string(),
            "require_e2e_first" => cfg.require_e2e_first = value.to_ascii_lowercase(),
            "require_env_ready_first" => cfg.require_env_ready_first = value.to_ascii_lowercase(),
            _ => {}
        }
    }

    cfg.source = if in_settings { "hook-config".to_string() } else { cfg.source };
    cfg
}

#[cfg(test)]
mod spiral_config_tests {
    use super::parse_spiral_config_from_hook_yaml;

    #[test]
    fn spiral_parser_returns_defaults_when_block_missing() {
        let cfg = parse_spiral_config_from_hook_yaml("settings:\n  cache_ttl: 600\nhooks:\n  x: y\n");
        assert_eq!(cfg.max_failed_tests, "10");
        assert_eq!(cfg.max_flaky_tests, "8");
        assert_eq!(cfg.max_test_evidence_age_minutes, "90");
        assert_eq!(cfg.max_build_evidence_age_minutes, "90");
        assert_eq!(cfg.max_e2e_evidence_age_minutes, "180");
        assert_eq!(cfg.require_e2e_first, "true");
    }

    #[test]
    fn spiral_parser_reads_values() {
        let cfg = parse_spiral_config_from_hook_yaml(
            "settings:\n  regression_spiral_guard:\n    max_failed_tests: 21\n    max_flaky_tests: 13\n    max_missing_test_pairs: 2\n    max_missing_test_types: 1\n    max_test_evidence_age_minutes: 45\n    max_build_evidence_age_minutes: 60\n    max_e2e_evidence_age_minutes: 120\n    streak_trigger: 4\n    require_e2e_first: false\n    require_env_ready_first: true\nhooks:\n  x: y\n",
        );
        assert_eq!(cfg.max_failed_tests, "21");
        assert_eq!(cfg.max_flaky_tests, "13");
        assert_eq!(cfg.max_missing_test_pairs, "2");
        assert_eq!(cfg.max_missing_test_types, "1");
        assert_eq!(cfg.max_test_evidence_age_minutes, "45");
        assert_eq!(cfg.max_build_evidence_age_minutes, "60");
        assert_eq!(cfg.max_e2e_evidence_age_minutes, "120");
        assert_eq!(cfg.streak_trigger, "4");
        assert_eq!(cfg.require_e2e_first, "false");
        assert_eq!(cfg.require_env_ready_first, "true");
    }

    #[test]
    fn spiral_parser_ignores_blank_values() {
        let cfg = parse_spiral_config_from_hook_yaml(
            "settings:\n  regression_spiral_guard:\n    max_failed_tests:\n    max_flaky_tests: 5\nhooks:\n  x: y\n",
        );
        assert_eq!(cfg.max_failed_tests, "10");
        assert_eq!(cfg.max_flaky_tests, "5");
    }
}

#[cfg(test)]
mod spiral_trend_tests {
    use super::{build_spiral_trend, SpiralMetricRecord};
    use serde_json::json;

    #[test]
    fn trend_handles_empty_records() {
        let out = build_spiral_trend(&[], "x.jsonl", 20);
        assert_eq!(out.samples_total, 0);
        assert_eq!(out.breach_count, 0);
        assert_eq!(out.breach_rate, 0.0);
        assert_eq!(out.mttr_proxy_cycles, None);
        assert_eq!(out.pressure_score, 0.0);
        assert_eq!(out.policy_band, "green");
    }

    #[test]
    fn trend_computes_core_metrics() {
        let rec = |ts: &str, violations: i64, streak: i64, interrupt: bool, status: &str, stale_test: i64, stale_build: i64, stale_e2e: i64| SpiralMetricRecord {
            generated_at: ts.to_string(),
            session_id: "s".to_string(),
            status: status.to_string(),
            severity: if violations > 0 { "warning".to_string() } else { "info".to_string() },
            reason: "".to_string(),
            violations,
            streak,
            interrupt,
            metrics: json!({
                "stale_test_evidence": stale_test,
                "stale_build_evidence": stale_build,
                "stale_e2e_evidence": stale_e2e,
            }),
        };
        let data = vec![
            rec("t1", 1, 1, false, "warning", 1, 0, 0),
            rec("t2", 2, 2, true, "critical_interrupt", 0, 1, 0),
            rec("t3", 0, 0, false, "healthy", 0, 0, 0),
            rec("t4", 1, 1, false, "warning", 0, 0, 1),
            rec("t5", 0, 0, false, "healthy", 0, 0, 0),
        ];
        let out = build_spiral_trend(&data, "x.jsonl", 50);
        assert_eq!(out.samples_total, 5);
        assert_eq!(out.window_used, 5);
        assert_eq!(out.breach_count, 3);
        assert!((out.breach_rate - 0.6).abs() < 1e-9);
        assert_eq!(out.interrupt_count, 1);
        assert_eq!(out.max_streak, 2);
        assert_eq!(out.open_breach_streak, 0);
        assert_eq!(out.mttr_proxy_cycles, Some(1.5));
        assert_eq!(out.violations_delta, -1);
        assert_eq!(out.stale_test_evidence_events, 1);
        assert_eq!(out.stale_build_evidence_events, 1);
        assert_eq!(out.stale_e2e_evidence_events, 1);
        assert!((out.pressure_score - 0.42).abs() < 1e-9);
        assert_eq!(out.policy_band, "green");
        assert_eq!(out.latest_status, "healthy");
    }

    #[test]
    fn trend_maps_red_policy_band_for_high_pressure() {
        let rec = |ts: &str, violations: i64, streak: i64, interrupt: bool| SpiralMetricRecord {
            generated_at: ts.to_string(),
            session_id: "s".to_string(),
            status: if interrupt { "critical_interrupt".to_string() } else { "warning".to_string() },
            severity: if interrupt { "critical".to_string() } else { "warning".to_string() },
            reason: "".to_string(),
            violations,
            streak,
            interrupt,
            metrics: json!({
                "stale_test_evidence": 1,
                "stale_build_evidence": 1,
                "stale_e2e_evidence": 1,
            }),
        };
        let data = vec![
            rec("t1", 2, 2, true),
            rec("t2", 3, 3, true),
            rec("t3", 4, 4, true),
            rec("t4", 5, 5, true),
        ];
        let out = build_spiral_trend(&data, "x.jsonl", 50);
        assert!(out.pressure_score >= 0.75);
        assert_eq!(out.policy_band, "red");
    }
}

#[cfg(test)]
mod spiral_selector_tests {
    use super::canonicalize_selector_csv;

    #[test]
    fn selector_csv_canonicalizes_sort_and_dedupe() {
        let out = canonicalize_selector_csv(" reliability,regression_spiral_guard,reliability ");
        assert_eq!(out.cleaned_raw, "reliability,regression_spiral_guard,reliability");
        assert_eq!(out.canonical, "regression_spiral_guard,reliability");
        assert!(out.selected_mode);
    }

    #[test]
    fn selector_csv_keeps_malformed_token_for_fail_closed_validation() {
        let out = canonicalize_selector_csv("regression_spiral_guard;rm -rf /");
        assert_eq!(out.cleaned_raw, "regression_spiral_guard;rm-rf/");
        assert_eq!(out.canonical, "regression_spiral_guard;rm-rf/");
        assert!(out.selected_mode);
    }

    #[test]
    fn selector_csv_empty_tokens_only_stays_selected_mode_with_empty_canonical() {
        let out = canonicalize_selector_csv(" , , ");
        assert_eq!(out.cleaned_raw, ",,");
        assert_eq!(out.canonical, "");
        assert!(out.selected_mode);
    }

    #[test]
    fn selector_csv_blank_input_disables_selected_mode() {
        let out = canonicalize_selector_csv("   ");
        assert_eq!(out.cleaned_raw, "");
        assert_eq!(out.canonical, "");
        assert!(!out.selected_mode);
    }
}

/// Return the lazily-initialized noqa-with-justification regex (positive match = has justification).
fn get_noqa_justified_regex() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| {
        // Matches `\x23 noqa` or `\x23 noqa: X123` followed by ` -- ` justification marker
        Regex::new(r"#\s*noqa(?::\s*\S+)?\s+--\s").unwrap()
    })
}

/// Return the lazily-initialized noqa-bare regex (any noqa annotation).
fn get_noqa_bare_regex() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| {
        Regex::new(r"#\s*noq\x61").unwrap()
    })
}

/// Return the lazily-initialized TO\x44O/FIX\x4DE/HAC\x4B keyword regex.
fn get_todo_keyword_regex() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| {
        Regex::new(r"(?i)\b(TO\x44O|FIX\x4DE|HAC\x4B|XXX)\b").unwrap()
    })
}

/// Return the lazily-initialized ticket reference regex.
fn get_ticket_ref_regex() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| {
        // Matches \x23 123, PROJ-456, [\x23 789]
        Regex::new(r"(?:#\d+|[A-Z][A-Z0-9]+-\d+|\[#\d+\])").unwrap()
    })
}

/// Return the lazily-initialized hardcoded credential regex.
fn get_hardcoded_cred_regex() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| {
        Regex::new(r#"(?i)(password|passwd|pwd|secret|api_key|apikey|access_token|auth_token)\s*=\s*["'][^"']{4,}["']"#).unwrap()
    })
}

/// Detect `\x23 noqa` annotations without a justification comment (`-- reason`).
fn scan_noqa_violations(content: &str) -> Vec<GovernanceViolation> {
    let bare_re = get_noqa_bare_regex();
    let justified_re = get_noqa_justified_regex();
    content
        .lines()
        .enumerate()
        .filter_map(|(idx, line)| {
            // Flag if the line has a noqa annotation but lacks the justification marker
            if bare_re.is_match(line) && !justified_re.is_match(line) {
                Some(GovernanceViolation {
                    rule: "noqa-no-justification".to_string(),
                    severity: "error".to_string(),
                    line: idx + 1,
                    message: format!(
                        "Suppression `\x23 noqa` at line {} lacks inline justification (`-- reason`).",
                        idx + 1
                    ),
                })
            } else {
                None
            }
        })
        .collect()
}

/// Detect TODO/FIXME/HACK comments without a ticket reference.
fn scan_todo_no_ticket_violations(content: &str) -> Vec<GovernanceViolation> {
    let keyword_re = get_todo_keyword_regex();
    let ticket_re = get_ticket_ref_regex();
    content
        .lines()
        .enumerate()
        .filter_map(|(idx, line)| {
            if let Some(m) = keyword_re.find(line) {
                // Only flag if the same line has no ticket reference
                if !ticket_re.is_match(line) {
                    let keyword = m.as_str().to_uppercase();
                    let keyword = keyword.trim();
                    Some(GovernanceViolation {
                        rule: "todo-no-ticket".to_string(),
                        severity: "warning".to_string(),
                        line: idx + 1,
                        message: format!(
                            "{} at line {} has no ticket reference (e.g. #123 or PROJ-456).",
                            keyword,
                            idx + 1
                        ),
                    })
                } else {
                    None
                }
            } else {
                None
            }
        })
        .collect()
}

/// Check Python function lengths.  A function that spans more than 40 lines
/// (from `def …:` to the next `def ` / `class ` / end-of-file) is flagged.
fn scan_function_length_violations(content: &str, max_lines: usize) -> Vec<GovernanceViolation> {
    let def_re = Regex::new(r"^(\s*)(?:async\s+)?def\s+\w+").unwrap();
    let class_re = Regex::new(r"^(\s*)class\s+\w+").unwrap();

    let lines: Vec<&str> = content.lines().collect();
    let mut violations = Vec::new();

    let mut i = 0;
    while i < lines.len() {
        if let Some(caps) = def_re.captures(lines[i]) {
            let def_indent = caps[1].len();
            let def_line_no = i + 1; // 1-based
            let func_start = i;

            // Walk forward until we find another def/class at the same or shallower indent
            let mut j = i + 1;
            while j < lines.len() {
                let l = lines[j];
                // Skip blank lines and comment-only lines
                if l.trim().is_empty() || l.trim_start().starts_with('#') {
                    j += 1;
                    continue;
                }
                // If we hit a def/class at same or shallower indent, stop
                let indent = l.len() - l.trim_start().len();
                let is_def = def_re.is_match(l);
                let is_class = class_re.is_match(l);
                if (is_def || is_class) && indent <= def_indent {
                    break;
                }
                j += 1;
            }

            let func_len = j - func_start;
            if func_len > max_lines {
                violations.push(GovernanceViolation {
                    rule: "function-too-long".to_string(),
                    severity: "warning".to_string(),
                    line: def_line_no,
                    message: format!(
                        "Function at line {} is {} lines long (max {max_lines}).",
                        def_line_no, func_len
                    ),
                });
            }
            i = j; // advance past this function
        } else {
            i += 1;
        }
    }

    violations
}

/// Detect hardcoded credential patterns (e.g. `password = "secret"`).
fn scan_hardcoded_cred_violations(content: &str) -> Vec<GovernanceViolation> {
    let re = get_hardcoded_cred_regex();
    content
        .lines()
        .enumerate()
        .filter_map(|(idx, line)| {
            if re.is_match(line) {
                Some(GovernanceViolation {
                    rule: "hardcoded-credential".to_string(),
                    severity: "error".to_string(),
                    line: idx + 1,
                    message: format!(
                        "Possible hardcoded credential at line {}.",
                        idx + 1
                    ),
                })
            } else {
                None
            }
        })
        .collect()
}

/// Run all governance rules against `content` and return every violation.
fn scan_content_for_governance(content: &str) -> Vec<GovernanceViolation> {
    let mut violations = Vec::new();
    violations.extend(scan_noqa_violations(content));
    violations.extend(scan_todo_no_ticket_violations(content));
    violations.extend(scan_function_length_violations(content, 40));
    violations.extend(scan_hardcoded_cred_violations(content));
    // Sort by line number for deterministic output
    violations.sort_by_key(|v| v.line);
    violations
}

/// `hook-dispatcher governance scan <file>` or `governance scan --stdin`
/// `hook-dispatcher governance check-contract <contract_id> <file>`
/// Outputs: JSON GovernanceScanOutput
fn cmd_governance(args: &[String]) -> ExitCode {
    // args[0] = binary name, args[1] = "governance"
    let sub = args.get(2).map(|s| s.as_str()).unwrap_or("");

    match sub {
        "scan" => {
            let content = if args.get(3).map(|s| s.as_str()) == Some("--stdin") {
                let mut buf = String::new();
                std::io::stdin().read_to_string(&mut buf).unwrap_or(0);
                buf
            } else if let Some(path) = args.get(3) {
                match fs::read_to_string(path) {
                    Ok(c) => c,
                    Err(e) => {
                        eprintln!("governance scan: cannot read {path:?}: {e}");
                        let out = GovernanceScanOutput { violation_count: 0, violations: vec![] };
                        println!("{}", serde_json::to_string(&out).unwrap());
                        return ExitCode::from(1);
                    }
                }
            } else {
                eprintln!("usage: hook-dispatcher governance scan <file>");
                eprintln!("       hook-dispatcher governance scan --stdin");
                return ExitCode::from(1);
            };

            let violations = scan_content_for_governance(&content);
            let found = !violations.is_empty();
            let out = GovernanceScanOutput {
                violation_count: violations.len(),
                violations,
            };
            println!("{}", serde_json::to_string(&out).unwrap());
            if found { ExitCode::from(1) } else { ExitCode::from(0) }
        }

        "check-contract" => {
            // args: governance check-contract <contract_id> <file>
            let contract_id = match args.get(3) {
                Some(s) => s.clone(),
                None => {
                    eprintln!("usage: hook-dispatcher governance check-contract <contract_id> <file>");
                    return ExitCode::from(1);
                }
            };
            let content = if args.get(4).map(|s| s.as_str()) == Some("--stdin") {
                let mut buf = String::new();
                std::io::stdin().read_to_string(&mut buf).unwrap_or(0);
                buf
            } else if let Some(path) = args.get(4) {
                match fs::read_to_string(path) {
                    Ok(c) => c,
                    Err(e) => {
                        eprintln!("governance check-contract: cannot read {path:?}: {e}");
                        let out = GovernanceScanOutput { violation_count: 0, violations: vec![] };
                        println!("{}", serde_json::to_string(&out).unwrap());
                        return ExitCode::from(1);
                    }
                }
            } else {
                eprintln!("usage: hook-dispatcher governance check-contract <contract_id> <file>");
                return ExitCode::from(1);
            };

            // Map contract IDs to specific rule subsets
            let violations: Vec<GovernanceViolation> = match contract_id.as_str() {
                "P2-PRIVACY" | "secret-detection" => {
                    let mut v = scan_hardcoded_cred_violations(&content);
                    v.sort_by_key(|x| x.line);
                    v
                }
                "suppression-policy" | "noqa-policy" => {
                    let mut v = scan_noqa_violations(&content);
                    v.sort_by_key(|x| x.line);
                    v
                }
                "todo-policy" => {
                    let mut v = scan_todo_no_ticket_violations(&content);
                    v.sort_by_key(|x| x.line);
                    v
                }
                "complexity-policy" | "function-length" => {
                    let mut v = scan_function_length_violations(&content, 40);
                    v.sort_by_key(|x| x.line);
                    v
                }
                // Unknown contracts: run all rules
                _ => scan_content_for_governance(&content),
            };

            let found = !violations.is_empty();
            let out = GovernanceScanOutput {
                violation_count: violations.len(),
                violations,
            };
            println!("{}", serde_json::to_string(&out).unwrap());
            if found { ExitCode::from(1) } else { ExitCode::from(0) }
        }

        "spiral-config" => {
            // args: governance spiral-config [path] [--format env|json]
            let mut cfg_path = "hooks/hook-config.yaml".to_string();
            let mut out_format = "json".to_string();
            let mut i = 3usize;
            while i < args.len() {
                match args[i].as_str() {
                    "--format" if i + 1 < args.len() => {
                        out_format = args[i + 1].clone();
                        i += 2;
                    }
                    s if !s.starts_with("--") => {
                        cfg_path = s.to_string();
                        i += 1;
                    }
                    _ => {
                        i += 1;
                    }
                }
            }

            let mut cfg = SpiralConfigOutput::default();
            if let Ok(content) = fs::read_to_string(&cfg_path) {
                cfg = parse_spiral_config_from_hook_yaml(&content);
            }

            if out_format == "env" {
                println!("CFG_SPIRAL_MAX_FAILED_TESTS={}", cfg.max_failed_tests);
                println!("CFG_SPIRAL_MAX_FLAKY_TESTS={}", cfg.max_flaky_tests);
                println!("CFG_SPIRAL_MAX_MISSING_TEST_PAIRS={}", cfg.max_missing_test_pairs);
                println!("CFG_SPIRAL_MAX_MISSING_TEST_TYPES={}", cfg.max_missing_test_types);
                println!("CFG_SPIRAL_MAX_TEST_EVIDENCE_AGE_MINUTES={}", cfg.max_test_evidence_age_minutes);
                println!("CFG_SPIRAL_MAX_BUILD_EVIDENCE_AGE_MINUTES={}", cfg.max_build_evidence_age_minutes);
                println!("CFG_SPIRAL_MAX_E2E_EVIDENCE_AGE_MINUTES={}", cfg.max_e2e_evidence_age_minutes);
                println!("CFG_SPIRAL_STREAK_TRIGGER={}", cfg.streak_trigger);
                println!("CFG_REQUIRE_E2E_FIRST={}", cfg.require_e2e_first);
                println!("CFG_REQUIRE_ENV_READY_FIRST={}", cfg.require_env_ready_first);
                println!("CFG_SPIRAL_SOURCE={}", cfg.source);
            } else {
                println!("{}", serde_json::to_string(&cfg).unwrap());
            }
            ExitCode::from(0)
        }

        "spiral-trend" => {
            // args: governance spiral-trend [path] [--window N]
            let mut metrics_path = ".claude/verification/regression-spiral-metrics.jsonl".to_string();
            let mut window = 50usize;
            let mut i = 3usize;
            while i < args.len() {
                match args[i].as_str() {
                    "--window" if i + 1 < args.len() => {
                        window = args[i + 1].parse::<usize>().unwrap_or(50);
                        i += 2;
                    }
                    s if !s.starts_with("--") => {
                        metrics_path = s.to_string();
                        i += 1;
                    }
                    _ => i += 1,
                }
            }

            let records = read_spiral_metrics(&metrics_path);
            let trend = build_spiral_trend(&records, &metrics_path, window);
            println!("{}", serde_json::to_string(&trend).unwrap());
            ExitCode::from(0)
        }

        "spiral-selector" => {
            // args: governance spiral-selector [raw_selector] [--format csv|json]
            let mut raw_selector = String::new();
            let mut out_format = "json".to_string();
            let mut seen_selector = false;
            let mut i = 3usize;
            while i < args.len() {
                match args[i].as_str() {
                    "--format" if i + 1 < args.len() => {
                        out_format = args[i + 1].clone();
                        i += 2;
                    }
                    "--format" => {
                        eprintln!("governance spiral-selector: --format requires a value (csv|json)");
                        return ExitCode::from(2);
                    }
                    s if s.starts_with("--") => {
                        eprintln!("governance spiral-selector: unknown flag: {}", s);
                        return ExitCode::from(2);
                    }
                    s if !s.starts_with("--") => {
                        if seen_selector {
                            eprintln!(
                                "governance spiral-selector: too many positional arguments (expected at most 1 raw selector)"
                            );
                            return ExitCode::from(2);
                        }
                        raw_selector = s.to_string();
                        seen_selector = true;
                        i += 1;
                    }
                    _ => i += 1,
                }
            }

            if out_format != "csv" && out_format != "json" {
                eprintln!(
                    "governance spiral-selector: invalid --format value: {} (expected csv|json)",
                    out_format
                );
                return ExitCode::from(2);
            }
            if raw_selector.chars().any(|c| c.is_control()) {
                eprintln!("governance spiral-selector: control characters are not allowed in selector input");
                return ExitCode::from(2);
            }

            let out = canonicalize_selector_csv(&raw_selector);
            if out_format == "csv" {
                println!("{}", out.canonical);
            } else {
                println!("{}", serde_json::to_string(&out).unwrap());
            }
            ExitCode::from(0)
        }

        _ => {
            eprintln!("usage: hook-dispatcher governance <scan|check-contract|spiral-config|spiral-trend|spiral-selector> ...");
            ExitCode::from(1)
        }
    }
}

/// `hook-dispatcher scan-secrets <file>` or `hook-dispatcher scan-secrets --stdin`
/// Outputs: JSON {"found": bool, "matches": [...]}
fn cmd_scan_secrets(args: &[String]) -> ExitCode {
    let content = if args.get(2).map(|s| s.as_str()) == Some("--stdin") {
        let mut buf = String::new();
        std::io::stdin().read_to_string(&mut buf).unwrap_or(0);
        buf
    } else if let Some(path) = args.get(2) {
        match fs::read_to_string(path) {
            Ok(c) => c,
            Err(e) => {
                let output = ScanSecretsOutput { found: false, matches: vec![] };
                eprintln!("scan-secrets: cannot read {:?}: {e}", path);
                println!("{}", serde_json::to_string(&output).unwrap());
                return ExitCode::from(1);
            }
        }
    } else {
        eprintln!("usage: hook-dispatcher scan-secrets <file>");
        eprintln!("       hook-dispatcher scan-secrets --stdin");
        return ExitCode::from(1);
    };

    let matches = scan_content_for_secrets(&content);
    let found = !matches.is_empty();
    let output = ScanSecretsOutput { found, matches };
    println!("{}", serde_json::to_string(&output).unwrap());
    // Exit 1 when secrets found (non-zero signals caller to block)
    if found { ExitCode::from(1) } else { ExitCode::from(0) }
}

// ---------------------------------------------------------------------------
// Worker Pool (MTSP-06)
// ---------------------------------------------------------------------------

struct Worker {
    id: usize,
    thread: Option<thread::JoinHandle<()>>,
}

struct WorkerPool {
    workers: Vec<Worker>,
    sender: Option<std::sync::mpsc::Sender<Box<dyn FnOnce() + Send>>>,
}

impl WorkerPool {
    fn new(size: usize) -> Self {
        let (sender, receiver) = std::sync::mpsc::channel::<Box<dyn FnOnce() + Send>>();
        let receiver = Arc::new(Mutex::new(receiver));
        let mut workers = Vec::with_capacity(size);

        for id in 0..size {
            let rx = Arc::clone(&receiver);
            let thread = thread::spawn(move || loop {
                let job = rx.lock().unwrap().recv();
                match job {
                    Ok(f) => f(),
                    Err(_) => break,
                }
            });
            workers.push(Worker { id, thread: Some(thread) });
        }

        WorkerPool { workers, sender: Some(sender) }
    }

    fn execute<F>(&self, f: F)
    where
        F: FnOnce() + Send + 'static,
    {
        if let Some(ref sender) = self.sender {
            sender.send(Box::new(f)).expect("failed to send job to worker");
        }
    }
}

// ---------------------------------------------------------------------------
// Input schema
// ---------------------------------------------------------------------------

struct TempFile {
    path: PathBuf,
}

impl TempFile {
    fn new(content: &str) -> Self {
        let path = PathBuf::from(format!("/tmp/hook-dispatch-{}.json", std::process::id()));
        fs::write(&path, content).expect("failed to write temp file");
        TempFile { path }
    }
}

impl Drop for TempFile {
    fn drop(&mut self) {
        let _ = fs::remove_file(&self.path);
    }
}

// ---------------------------------------------------------------------------
// Native hook implementations
// ---------------------------------------------------------------------------

fn run_doc_location_guard(_env_map: &HashMap<String, String>) -> i32 {
    // ... code ...
    0
}

fn run_session_cleanup(env_map: &HashMap<String, String>) -> i32 {
    let project_dir = env_map.get("PROJECT_DIR").map(|s| s.as_str()).unwrap_or(".");
    
    let change_log = format!("{}/.claude/session-changes.log", project_dir);
    let qa_state = format!("{}/.claude/qa-state.json", project_dir);

    let _ = fs::remove_file(change_log);
    let _ = fs::remove_file(qa_state);

    0
}

fn run_prompt_submit_guard(_env_map: &HashMap<String, String>, input_json: &serde_json::Value) -> i32 {
    let prompt_text = input_json.get("tool_input")
        .and_then(|ti| ti.get("prompt").or_else(|| ti.get("content")))
        .or_else(|| input_json.get("content"))
        .and_then(|v| v.as_str())
        .unwrap_or("");

    if prompt_text.is_empty() {
        return 0;
    }

    let prompt_lower = prompt_text.to_lowercase();
    let mut antipatterns = Vec::new();

    // Test-skipping
    let test_patterns = ["skip tests", "skip the tests", "don't write tests", "no tests", "dont write tests", "without tests"];
    for p in &test_patterns {
        if prompt_lower.contains(p) {
            antipatterns.push(format!("test-skipping: \"{p}\""));
            break;
        }
    }

    // Lint-skipping
    let lint_patterns = ["disable lint", "ignore lint", "skip lint", "no linting"];
    for p in &lint_patterns {
        if prompt_lower.contains(p) {
            antipatterns.push(format!("lint-skipping: \"{p}\""));
            break;
        }
    }

    // Quality-skipping
    let quality_patterns = ["just make it work", "just get it working", "just get it done", "make it work somehow"];
    for p in &quality_patterns {
        if prompt_lower.contains(p) {
            antipatterns.push(format!("quality-shortcut: \"{p}\""));
            break;
        }
    }

    // Error-suppression
    let error_patterns = ["ignore the errors", "ignore errors", "suppress the", "suppress errors", "hide the errors"];
    for p in &error_patterns {
        if prompt_lower.contains(p) {
            antipatterns.push(format!("error-suppression: \"{p}\""));
            break;
        }
    }

    // Dangerous git
    let git_patterns = ["--no-verify", "--force", "force push", "force-push", "--force-with-lease"];
    for p in &git_patterns {
        if prompt_lower.contains(p) {
            antipatterns.push(format!("dangerous-git: \"{p}\""));
            break;
        }
    }

    if !antipatterns.is_empty() {
        eprintln!("QA Governance Reminder: Quality enforcement is active.");
        eprintln!("  Detected patterns:");
        for ap in &antipatterns {
            eprintln!("    - {ap}");
        }
        eprintln!("  Consider:\n    - Tests are required for all new code (TDD mandate)\n    - Suppressions require inline justification\n    - All linters must pass");
    }

    // Workflow triggers (Idea/Task)
    let idea_patterns = ["idea", "research", "explore", "figure out", "add feature", "build", "implement", "design", "create", "task", "feature", "investigate"];
    for p in &idea_patterns {
        if prompt_lower.contains(p) {
            eprintln!("\n--- Agent workflow (idea/task detected) ---");
            eprintln!("1. Dump research to docs/research/ (or docs/guides/ as appropriate)");
            eprintln!("2. Create or update specs in docs/docset/ (formal specification docset)");
            eprintln!("3. Add work items to unified work stream (docs/reference/, contracts/, or project tracker)");
            eprintln!("4. This enables: spam ideas here → open new chat → ask 'find the next thing to do'");
            break;
        }
    }

    // Special flags: $defer, $pending, $block, $idea
    if prompt_text.contains("$defer") || prompt_text.contains("$pending") || prompt_text.contains("$block") || prompt_text.contains("$idea") {
        return 99; // Sentinel value to trigger fallback
    }

    0
}

fn run_governance_scan(project_dir: &str) -> i32 {
    // MTSP-08: Native 8-dimension scan (Rust implementation)
    let project_path = Path::new(project_dir);
    let mut violation_count = 0;
    
    println!("--- MTSP-08: Rust Governance Scan ---");

    // 1. Doc Disorganization
    let required_dirs = ["docs/guides", "docs/reference", "docs/reports"];
    let mut missing = Vec::new();
    for d in &required_dirs {
        if !project_path.join(d).is_dir() {
            missing.push(*d);
        }
    }
    if !missing.is_empty() {
        eprintln!("GOVERNANCE [Dimension 1: Docs]: missing required doc subdirs: {:?}", missing);
        violation_count += 1;
    }

    // 2. Stale Specs (7 days)
    let specs_dir = project_path.join("specs");
    if specs_dir.is_dir() {
        let cutoff = std::time::SystemTime::now() - Duration::from_secs(7 * 86400);
        let mut stale_count = 0;
        if let Ok(entries) = fs::read_dir(specs_dir) {
            for entry in entries.flatten() {
                if let Ok(metadata) = entry.metadata() {
                    if let Ok(modified) = metadata.modified() {
                        if modified < cutoff {
                            stale_count += 1;
                        }
                    }
                }
            }
        }
        if stale_count > 0 {
            eprintln!("GOVERNANCE [Dimension 2: Specs]: found {stale_count} stale spec file(s)");
            violation_count += 1;
        }
    }

    // 3. Large Files (> 100KB)
    let mut large_files = Vec::new();
    scan_large_files(project_path, &mut large_files, 100 * 1024);
    if !large_files.is_empty() {
        eprintln!("GOVERNANCE [Dimension 3: Size]: found {} file(s) > 100KB", large_files.len());
        for f in large_files.iter().take(5) {
            eprintln!("  - {:?}", f);
        }
        violation_count += 1;
    }

    // 4. TODO Sprawl
    let todo_count = count_todos(project_path);
    if todo_count > 50 {
        eprintln!("GOVERNANCE [Dimension 4: TODOs]: high TODO count: {}", todo_count);
        violation_count += 1;
    }

    // 5. AI Slop Detection (Dimension 5)
    let slop_count = count_ai_slop(project_path);
    if slop_count > 0 {
        eprintln!("GOVERNANCE [Dimension 5: Slop]: detected {} instance(s) of AI slop", slop_count);
        violation_count += 1;
    }

    // 6. Secret Detection (Dimension 6)
    let secret_count = scan_secrets(project_path, get_secret_regexes());
    if secret_count > 0 {
        eprintln!("GOVERNANCE [Dimension 6: Security]: detected {} potential secret(s)", secret_count);
        violation_count += 1;
    }

    // 7. Complexity (Dimension 7: Deep Nesting)
    let deep_files = scan_deep_nesting(project_path, 8);
    if !deep_files.is_empty() {
        eprintln!("GOVERNANCE [Dimension 7: Complexity]: found {} file(s) nested deeper than 8 levels", deep_files.len());
        violation_count += 1;
    }

    // 8. License/Provenance (Dimension 8)
    if !project_path.join("LICENSE").exists() && !project_path.join("COPYING").exists() && !project_path.join("LICENSE.md").exists() {
        eprintln!("GOVERNANCE [Dimension 8: Provenance]: missing LICENSE file");
        violation_count += 1;
    }

    if violation_count > 0 {
        eprintln!("GOVERNANCE: scan completed with {} dimension violation(s)", violation_count);
    } else {
        println!("GOVERNANCE: all dimensions green.");
    }

    0
}

// ---------------------------------------------------------------------------
// Tool lookup helper (native PATH scan, no subprocess)
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Read skip hooks from .claude.qa-local.json
// ---------------------------------------------------------------------------

fn get_skip_hooks(project_dir: &str) -> Vec<String> {
    let qa_config_path = format!("{}/.claude/qa-local.json", project_dir);
    let path = Path::new(&qa_config_path);
    if !path.exists() {
        return Vec::new();
    }

    match fs::read_to_string(path) {
        Ok(content) => {
            match serde_json::from_str::<serde_json::Value>(&content) {
                Ok(json) => {
                    let mut skip_list = Vec::new();
                    if let Some(hooks) = json.get("hooks").and_then(|h| h.get("skip")) {
                        if let Some(arr) = hooks.as_array() {
                            for item in arr {
                                if let Some(s) = item.as_str() {
                                    skip_list.push(s.to_string());
                                }
                            }
                        }
                    }
                    skip_list
                }
                Err(_) => Vec::new(),
            }
        }
        Err(_) => Vec::new(),
    }
}

fn should_skip_hook(hook_name: &str, skip_list: &[String]) -> bool {
    // Hook name comes as "foo.sh", skip list has "foo" or "foo.sh"
    let hook_base = hook_name.trim_end_matches(".sh");
    skip_list.iter().any(|s| {
        let skip_base = s.trim_end_matches(".sh");
        skip_base == hook_base
    })
}

#[derive(Debug, Clone)]
struct StopSettings {
    idle_timeout_sec: u64,
    max_timeout_sec: u64,
    profile: String,
}

fn clamp_stop_idle(v: u64) -> u64 {
    v.clamp(5, 15)
}

fn clamp_stop_max(v: u64, idle: u64) -> u64 {
    v.max(idle).clamp(5, 15)
}

fn read_stop_settings(project_dir: &str) -> StopSettings {
    // Defaults: aggressively bounded for low-latency operator loops.
    let mut idle_timeout_sec: u64 = 5;
    let mut max_timeout_sec: u64 = 15;
    let mut profile = "fast".to_string();

    let qa_config_path = format!("{}/.claude/qa-local.json", project_dir);
    if let Ok(content) = fs::read_to_string(&qa_config_path) {
        if let Ok(json) = serde_json::from_str::<serde_json::Value>(&content) {
            if let Some(stop) = json.get("stop") {
                if let Some(v) = stop.get("idle_timeout_sec").and_then(|x| x.as_u64()) {
                    idle_timeout_sec = v;
                }
                if let Some(v) = stop.get("max_timeout_sec").and_then(|x| x.as_u64()) {
                    max_timeout_sec = v;
                }
                if let Some(v) = stop.get("profile").and_then(|x| x.as_str()) {
                    let p = v.trim().to_ascii_lowercase();
                    if p == "ultrafast" || p == "fast" || p == "standard" || p == "full" {
                        profile = p;
                    }
                }
            }
        }
    }

    // Env overrides (highest priority)
    if let Ok(v) = env::var("THGENT_STOP_IDLE_TIMEOUT_SEC") {
        if let Ok(n) = v.parse::<u64>() {
            idle_timeout_sec = n;
        }
    }
    if let Ok(v) = env::var("THGENT_STOP_MAX_TIMEOUT_SEC") {
        if let Ok(n) = v.parse::<u64>() {
            max_timeout_sec = n;
        }
    }
    if let Ok(v) = env::var("THGENT_STOP_PROFILE") {
        let p = v.trim().to_ascii_lowercase();
        if p == "ultrafast" || p == "fast" || p == "standard" || p == "full" {
            profile = p;
        }
    }

    idle_timeout_sec = clamp_stop_idle(idle_timeout_sec);
    max_timeout_sec = clamp_stop_max(max_timeout_sec, idle_timeout_sec);

    StopSettings {
        idle_timeout_sec,
        max_timeout_sec,
        profile,
    }
}

// ---------------------------------------------------------------------------
// Build environment map
// ---------------------------------------------------------------------------

fn build_env(
    input: &HookInput,
    raw_json: &str,
    mode: Mode,
    hooks_dir: &Path,
) -> HashMap<String, String> {
    let mut env_map: HashMap<String, String> = HashMap::new();

    let tool_name = input.tool_name.as_deref().unwrap_or("");
    let resolved_dir = input
        .cwd
        .clone()
        .or_else(|| input.project_dir.clone())
        .or_else(|| env::current_dir().ok().map(|p| p.to_string_lossy().into_owned()))
        .unwrap_or_default();
    let project_dir = resolved_dir.as_str();
    let session_id = input.session_id.as_deref().unwrap_or("");

    let tool_input = input.tool_input.as_ref();
    let get_str = |key: &str| -> String {
        tool_input
            .and_then(|v| v.get(key))
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string()
    };

    // From JSON
    env_map.insert("TOOL_NAME".into(), tool_name.into());
    env_map.insert("FILE_PATH".into(), get_str("file_path"));
    env_map.insert("PROJECT_DIR".into(), project_dir.into());
    env_map.insert("SESSION_ID".into(), session_id.into());
    env_map.insert("CWD".into(), project_dir.into());
    env_map.insert("INPUT".into(), raw_json.into());
    env_map.insert("TOOL_CONTENT".into(), get_str("content"));
    env_map.insert("TOOL_NEW_STRING".into(), get_str("new_string"));
    env_map.insert("TOOL_OLD_STRING".into(), get_str("old_string"));

    // Computed
    env_map.insert("_HOOK_DISPATCHED".into(), "1".into());
    env_map.insert(
        "VERIFY_DIR".into(),
        format!("{project_dir}/.claude/verification"),
    );
    env_map.insert(
        "QA_STATE".into(),
        format!("{project_dir}/.claude/verification/qa-state.json"),
    );
    env_map.insert(
        "CHANGE_LOG".into(),
        format!("{project_dir}/.claude/session-changes.log"),
    );

    // QUALITY_CONFIG: project-local, then global, then empty
    let project_quality = format!("{project_dir}/.claude/quality.json");
    let home = env::var("HOME").unwrap_or_else(|_| "/tmp".into());
    let global_quality = format!("{home}/.claude/quality.json");
    let quality_config = if Path::new(&project_quality).exists() {
        project_quality
    } else if Path::new(&global_quality).exists() {
        global_quality
    } else {
        String::new()
    };
    env_map.insert("QUALITY_CONFIG".into(), quality_config);

    // Tool paths (available for ALL modes)
    env_map.insert("JQ_CMD".into(), first_available(&["jaq", "jq"]));
    env_map.insert("HUNIQ_CMD".into(), first_available(&["huniq"]));
    env_map.insert(
        "TIMEOUT_CMD".into(),
        first_available(&["gtimeout", "timeout"]),
    );
    env_map.insert("RG_CMD".into(), first_available(&["rg"]));
    env_map.insert("RG_TIMEOUT_SEC".into(), env::var("RG_TIMEOUT_SEC").unwrap_or_else(|_| "30".into()));
    env_map.insert("FD_CMD".into(), first_available(&["fd", "fdfind"]));
    env_map.insert("PGREP_CMD".into(), first_available(&["pgrep"]));
    env_map.insert("HASH_CMD".into(), first_available(&["b3sum", "sha256sum", "shasum"]));

    // Timestamps
    let now = std::time::SystemTime::now();
    let ts = now.duration_since(std::time::UNIX_EPOCH).unwrap().as_secs();
    env_map.insert("START_TIMESTAMP".into(), ts.to_string());

    // Signal to hooks that tool detection is already done
    env_map.insert("_TOOL_CACHE_LOADED".into(), "1".into());

    // Hooks dir for child scripts
    env_map.insert(
        "HOOKS_DIR".into(),
        hooks_dir.to_string_lossy().into_owned(),
    );

    // Stop-mode extras: pre-compute git changed files
    if mode == Mode::Stop && !project_dir.is_empty() {
        env_map.insert("STOP_ACTIVE".into(), "1".into());

        let changed = Command::new("git")
            .args(["diff", "--name-only", "HEAD"])
            .current_dir(project_dir)
            .stdout(Stdio::piped())
            .stderr(Stdio::null())
            .output()
            .ok()
            .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string())
            .unwrap_or_default();
        env_map.insert("CHANGED_FILES".into(), changed);
    }

    // Mode identifier for hooks that need to know
    let mode_str = match mode {
        Mode::Pretool => "pretool",
        Mode::Posttool => "posttool",
        Mode::Stop => "stop",
        Mode::SessionStart => "sessionstart",
        Mode::PromptSubmit => "promptsubmit",
        Mode::SubagentStart => "subagentstart",
        Mode::SubagentStop => "subagentstop",
        Mode::PreCompact => "precompact",
        Mode::SessionEnd => "sessionend",
        Mode::TaskCompleted => "taskcompleted",
        Mode::TeammateIdle => "teammateidle",
        Mode::PostAgentRun => "postagentrun",
    };
    env_map.insert("HOOK_MODE".into(), mode_str.into());

    // Global Git State (MTSP-07)
    // Pre-compute HEAD_SHA for all modes to eliminate 100+ git spawns
    if !project_dir.is_empty() {
        let head_sha = Command::new("git")
            .args(["rev-parse", "HEAD"])
            .current_dir(project_dir)
            .stdout(Stdio::piped())
            .stderr(Stdio::null())
            .output()
            .ok()
            .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string())
            .unwrap_or_default();
        if !head_sha.is_empty() {
            env_map.insert("HEAD_SHA".into(), head_sha);
        }
    }

    env_map
}

// ---------------------------------------------------------------------------
// Hook execution result
// ---------------------------------------------------------------------------

#[derive(Debug)]
struct HookResult {
    name: String,
    rc: i32,
    stdout: String,
    stderr: String,
}

// ---------------------------------------------------------------------------
// Run a single hook with output-based (idle) timeout
// Monitors stdout/stderr in real-time and resets idle timer on each output
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, Copy, PartialEq)]
enum ShellType {
    Zsh,
    Bash,
    Pwsh,
    Powershell,
    Cmd,
    Dash,
    Unknown,
}

impl ShellType {
    fn as_str(&self) -> &'static str {
        match self {
            ShellType::Zsh => "zsh",
            ShellType::Bash => "bash",
            ShellType::Pwsh => "pwsh",
            ShellType::Powershell => "powershell",
            ShellType::Cmd => "cmd",
            ShellType::Dash => "dash",
            ShellType::Unknown => "unknown",
        }
    }

    fn from_str(s: &str) -> Self {
        match s.to_lowercase().as_str() {
            "zsh" => ShellType::Zsh,
            "bash" => ShellType::Bash,
            "pwsh" => ShellType::Pwsh,
            "powershell" => ShellType::Powershell,
            "cmd" => ShellType::Cmd,
            "dash" => ShellType::Dash,
            _ => ShellType::Unknown,
        }
    }
}

fn get_preferred_shell() -> ShellType {
    if let Ok(env_shell) = env::var("THGENT_AGENT_SHELL") {
        let st = ShellType::from_str(&env_shell);
        if st != ShellType::Unknown {
            return st;
        }
    }

    if cfg!(target_os = "windows") {
        if find_in_path("pwsh").is_some() {
            return ShellType::Pwsh;
        }
        return ShellType::Powershell;
    }

    for shell in &["zsh", "bash", "dash"] {
        if find_in_path(shell).is_some() {
            return ShellType::from_str(shell);
        }
    }

    ShellType::Unknown
}

fn get_shell_executable(shell_type: ShellType) -> String {
    if let Some(path) = find_in_path(shell_type.as_str()) {
        return path;
    }

    match shell_type {
        ShellType::Powershell => "powershell.exe".to_string(),
        ShellType::Pwsh => "pwsh.exe".to_string(),
        ShellType::Cmd => "cmd.exe".to_string(),
        _ => shell_type.as_str().to_string(),
    }
}

fn run_hook_with_idle_timeout(
    hooks_dir: &Path,
    hook_name: &str,
    extra_args: &[&str],
    env_map: &HashMap<String, String>,
    temp_path: &Path,
    idle_timeout: Duration,
    max_timeout: Duration,
) -> HookResult {
    // MTSP-20: Native Rust hook execution (avoid shell bridge)
    if hook_name == "quality-gate.sh" || hook_name == "security-pipeline.sh" || hook_name == "stop-dispatcher.sh" || hook_name == "stop-reconcile.sh" || hook_name == "complexity-ratchet.sh" || hook_name == "spec-verifier.sh" || hook_name == "test-maturity.sh" || hook_name == "suppression-blocker.sh" || hook_name == "pre-write-validator.sh" || hook_name == "post-edit-checker.sh" || hook_name == "task-completion-verifier.sh" || hook_name == "doc-location-guard.sh" || hook_name == "change-doc-tracker.sh" || hook_name == "friction-detector.sh" || hook_name == "agent-antipattern-detector.sh" {
        return run_hook(hooks_dir, hook_name, extra_args, env_map, temp_path, Some(max_timeout));
    }

    let script = hooks_dir.join(hook_name);
    if !script.exists() {
        return HookResult {
            name: hook_name.into(),
            rc: 0,
            stdout: String::new(),
            stderr: String::new(),
        };
    }

    let stdin_file = match fs::File::open(temp_path) {
        Ok(f) => f,
        Err(e) => {
            return HookResult {
                name: hook_name.into(),
                rc: 1,
                stdout: String::new(),
                stderr: format!("failed to open temp file: {e}"),
            };
        }
    };

    let shell_type = get_preferred_shell();
    let shell_exe = get_shell_executable(shell_type);
    
    let mut cmd = Command::new(&shell_exe);
    
    match shell_type {
        ShellType::Pwsh | ShellType::Powershell => {
            cmd.args(["-NoProfile", "-NonInteractive", "-File", &script.to_string_lossy()]);
        }
        _ => {
            cmd.arg(&script);
        }
    }

    for arg in extra_args {
        cmd.arg(arg);
    }

    cmd.stdin(Stdio::from(stdin_file))
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());

    for (k, v) in env_map {
        cmd.env(k, v);
    }

    if let Some(project_dir) = env_map.get("PROJECT_DIR") {
        if !project_dir.is_empty() && Path::new(project_dir).is_dir() {
            cmd.current_dir(project_dir);
        }
    }

    let mut child = match cmd.spawn() {
        Ok(c) => c,
        Err(e) => {
            return HookResult {
                name: hook_name.into(),
                rc: 1,
                stdout: String::new(),
                stderr: format!("failed to spawn hook: {e}"),
            };
        }
    };

    // Shared state between output reader threads and the main loop
    let last_output = Arc::new(Mutex::new(Instant::now()));
    let stdout_done = Arc::new(AtomicBool::new(false));
    let stderr_done = Arc::new(AtomicBool::new(false));
    let stdout_buf = Arc::new(Mutex::new(Vec::new()));
    let stderr_buf = Arc::new(Mutex::new(Vec::new()));

    // Spawn thread to read stdout in real-time
    let last_out = Arc::clone(&last_output);
    let stdout_done_flag = Arc::clone(&stdout_done);
    let stdout_buffer = Arc::clone(&stdout_buf);
    if let Some(stdout) = child.stdout.take() {
        let reader = BufReader::new(stdout);
        thread::spawn(move || {
            for line in reader.lines() {
                if let Ok(line) = line {
                    let _ = stdout_buffer.lock().unwrap().write_all(line.as_bytes());
                    let _ = stdout_buffer.lock().unwrap().write_all(b"\n");
                    *last_out.lock().unwrap() = Instant::now();
                }
            }
            stdout_done_flag.store(true, Ordering::SeqCst);
        });
    }

    // Spawn thread to read stderr in real-time
    let last_err = Arc::clone(&last_output);
    let stderr_done_flag = Arc::clone(&stderr_done);
    let stderr_buffer = Arc::clone(&stderr_buf);
    if let Some(stderr) = child.stderr.take() {
        let reader = BufReader::new(stderr);
        thread::spawn(move || {
            for line in reader.lines() {
                if let Ok(line) = line {
                    let _ = stderr_buffer.lock().unwrap().write_all(line.as_bytes());
                    let _ = stderr_buffer.lock().unwrap().write_all(b"\n");
                    *last_err.lock().unwrap() = Instant::now();
                }
            }
            stderr_done_flag.store(true, Ordering::SeqCst);
        });
    }

    let start = Instant::now();
    loop {
        match child.try_wait() {
            Ok(Some(status)) => {
                // Process finished - wait for output readers to complete
                thread::sleep(Duration::from_millis(50));
                return HookResult {
                    name: hook_name.into(),
                    rc: status.code().unwrap_or(1),
                    stdout: String::from_utf8_lossy(&stdout_buf.lock().unwrap()).into_owned(),
                    stderr: String::from_utf8_lossy(&stderr_buf.lock().unwrap()).into_owned(),
                };
            }
            Ok(None) => {
                let elapsed = start.elapsed();
                let idle = last_output.lock().unwrap().elapsed();

                // Check absolute max timeout first
                if elapsed >= max_timeout {
                    let _ = child.kill();
                    let _ = child.wait();
                    return HookResult {
                        name: hook_name.into(),
                        rc: 124,
                        stdout: String::new(),
                        stderr: format!(
                            "{hook_name}: absolute timeout after {}s",
                            max_timeout.as_secs()
                        ),
                    };
                }

                // Check idle timeout - kill if no output for X seconds
                if idle >= idle_timeout {
                    let _ = child.kill();
                    let _ = child.wait();
                    return HookResult {
                        name: hook_name.into(),
                        rc: 124,
                        stdout: String::from_utf8_lossy(&stdout_buf.lock().unwrap()).into_owned(),
                        stderr: format!(
                            "{hook_name}: idle timeout after {}s of no output",
                            idle_timeout.as_secs()
                        ),
                    };
                }

                // Both streams done and no more coming - process must have exited
                if stdout_done.load(Ordering::SeqCst) && stderr_done.load(Ordering::SeqCst) {
                    // Give a moment for any remaining output
                    thread::sleep(Duration::from_millis(50));
                    return HookResult {
                        name: hook_name.into(),
                        rc: child
                            .wait()
                            .ok()
                            .and_then(|s| s.code())
                            .unwrap_or(1),
                        stdout: String::from_utf8_lossy(&stdout_buf.lock().unwrap()).into_owned(),
                        stderr: String::from_utf8_lossy(&stderr_buf.lock().unwrap()).into_owned(),
                    };
                }

                thread::sleep(Duration::from_millis(50));
            }
            Err(e) => {
                return HookResult {
                    name: hook_name.into(),
                    rc: 1,
                    stdout: String::new(),
                    stderr: format!("wait error: {e}"),
                };
            }
        }
    }
}

// ---------------------------------------------------------------------------
// Run a single hook (legacy time-based timeout)
// ---------------------------------------------------------------------------

fn run_hook(
    hooks_dir: &Path,
    hook_name: &str,
    extra_args: &[&str],
    env_map: &HashMap<String, String>,
    temp_path: &Path,
    timeout: Option<Duration>,
) -> HookResult {
    // MTSP-20: Native Rust hook execution (avoid shell bridge)
    if hook_name == "quality-gate.sh" || hook_name == "security-pipeline.sh" || hook_name == "stop-dispatcher.sh" || hook_name == "stop-reconcile.sh" || hook_name == "complexity-ratchet.sh" || hook_name == "spec-verifier.sh" || hook_name == "test-maturity.sh" || hook_name == "suppression-blocker.sh" || hook_name == "pre-write-validator.sh" || hook_name == "post-edit-checker.sh" || hook_name == "task-completion-verifier.sh" || hook_name == "doc-location-guard.sh" || hook_name == "change-doc-tracker.sh" || hook_name == "friction-detector.sh" || hook_name == "agent-antipattern-detector.sh" || hook_name == "agileplus-cycle.sh" || hook_name == "teammate-reconcile.sh" || hook_name == "qa-artifact-quality-gate.sh" || hook_name == "qa-assurance-case-gate.sh" || hook_name == "qa-policy-engine.sh" || hook_name == "spec-preflight.sh" || hook_name == "prompt-submit-guard.sh" || hook_name == "subagent-quality-gate.sh" || hook_name == "pre-compact-snapshot.sh" || hook_name == "auto-checkpoint.sh" || hook_name == "task-completed.sh" || hook_name == "teammate-idle.sh" || hook_name == "harvest-idea-seeds-stop.sh" || hook_name == "harvest-pending-queue.sh" {
        let tool = match hook_name {
            "quality-gate.sh" => "quality-gate",
            "security-pipeline.sh" => "security-pipeline",
            "stop-dispatcher.sh" => "dispatch",
            "stop-reconcile.sh" => "stop-reconcile",
            "complexity-ratchet.sh" => "complexity-ratchet",
            "spec-verifier.sh" => "spec-verify",
            "test-maturity.sh" => "test-maturity",
            "suppression-blocker.sh" => "suppression-blocker",
            "pre-write-validator.sh" => "pre-write-validate",
            "post-edit-checker.sh" => "post-edit-check",
            "task-completion-verifier.sh" => "task-completion-verify",
            "doc-location-guard.sh" => "doc-location-guard",
            "change-doc-tracker.sh" => "change-doc-tracker",
            "friction-detector.sh" => "friction-detect",
            "agent-antipattern-detector.sh" => "antipattern-detect",
            "agileplus-cycle.sh" => "agileplus-cycle",
            "teammate-reconcile.sh" => "teammate-reconcile",
            "qa-artifact-quality-gate.sh" => "qa-artifact-gate",
            "qa-assurance-case-gate.sh" => "qa-assurance-gate",
            "qa-policy-engine.sh" => "qa-policy-engine",
            "spec-preflight.sh" => "spec-preflight",
            "prompt-submit-guard.sh" => "prompt-submit-guard",
            "subagent-quality-gate.sh" => "subagent-gate",
            "pre-compact-snapshot.sh" => "pre-compact",
            "auto-checkpoint.sh" => "pre-compact",
            "task-completed.sh" => "task-completed",
            "teammate-idle.sh" => "teammate-idle",
            "harvest-idea-seeds-stop.sh" => "harvest",
            "harvest-pending-queue.sh" => "harvest",
            _ => unreachable!(),
        };
        
        let mut cmd = Command::new(env_map.get("THEGENT_HOOKS_BIN").map(|s| s.as_str()).unwrap_or("thegent-hooks"));
        cmd.arg(tool);
        for arg in extra_args {
            cmd.arg(arg);
        }
        
        let stdin_file = match fs::File::open(temp_path) {
            Ok(f) => f,
            Err(e) => return HookResult { name: hook_name.into(), rc: 1, stdout: String::new(), stderr: format!("failed to open temp file: {e}") },
        };
        
        cmd.stdin(Stdio::from(stdin_file)).stdout(Stdio::piped()).stderr(Stdio::piped());
        for (k, v) in env_map { cmd.env(k, v); }
        if let Some(project_dir) = env_map.get("PROJECT_DIR") { cmd.current_dir(project_dir); }
        
        let output = cmd.output().unwrap();
        return HookResult {
            name: hook_name.into(),
            rc: output.status.code().unwrap_or(1),
            stdout: String::from_utf8_lossy(&output.stdout).into_owned(),
            stderr: String::from_utf8_lossy(&output.stderr).into_owned(),
        };
    }

    let script = hooks_dir.join(hook_name);
    if !script.exists() {
        return HookResult {
            name: hook_name.into(),
            rc: 0,
            stdout: String::new(),
            stderr: String::new(),
        };
    }

    let stdin_file = match fs::File::open(temp_path) {
        Ok(f) => f,
        Err(e) => {
            return HookResult {
                name: hook_name.into(),
                rc: 1,
                stdout: String::new(),
                stderr: format!("failed to open temp file: {e}"),
            };
        }
    };

    let shell_type = get_preferred_shell();
    let shell_exe = get_shell_executable(shell_type);
    
    let mut cmd = Command::new(&shell_exe);
    
    match shell_type {
        ShellType::Pwsh | ShellType::Powershell => {
            cmd.args(["-NoProfile", "-NonInteractive", "-File", &script.to_string_lossy()]);
        }
        _ => {
            cmd.arg(&script);
        }
    }

    // Append extra arguments (e.g., "start" or "stop" for subagent gate)
    for arg in extra_args {
        cmd.arg(arg);
    }

    cmd.stdin(Stdio::from(stdin_file))
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());

    // Inherit parent environment (avoids bash rehashing PATH from scratch).
    // Overlay our hook env vars on top.
    for (k, v) in env_map {
        cmd.env(k, v);
    }

    // Set working directory to project dir if available
    if let Some(project_dir) = env_map.get("PROJECT_DIR") {
        if !project_dir.is_empty() && Path::new(project_dir).is_dir() {
            cmd.current_dir(project_dir);
        }
    }

    let mut child = match cmd.spawn() {
        Ok(c) => c,
        Err(e) => {
            return HookResult {
                name: hook_name.into(),
                rc: 1,
                stdout: String::new(),
                stderr: format!("failed to spawn hook: {e}"),
            };
        }
    };

    match timeout {
        Some(dur) => {
            let start = Instant::now();
            loop {
                match child.try_wait() {
                    Ok(Some(status)) => {
                        let mut stdout_buf = Vec::new();
                        let mut stderr_buf = Vec::new();
                        if let Some(mut so) = child.stdout.take() {
                            let _ = so.read_to_end(&mut stdout_buf);
                        }
                        if let Some(mut se) = child.stderr.take() {
                            let _ = se.read_to_end(&mut stderr_buf);
                        }
                        return HookResult {
                            name: hook_name.into(),
                            rc: status.code().unwrap_or(1),
                            stdout: String::from_utf8_lossy(&stdout_buf).into_owned(),
                            stderr: String::from_utf8_lossy(&stderr_buf).into_owned(),
                        };
                    }
                    Ok(None) => {
                        if start.elapsed() >= dur {
                            let _ = child.kill();
                            let _ = child.wait();
                            return HookResult {
                                name: hook_name.into(),
                                rc: 124,
                                stdout: String::new(),
                                stderr: format!(
                                    "{hook_name}: timed out after {}s",
                                    dur.as_secs()
                                ),
                            };
                        }
                        thread::sleep(Duration::from_millis(50));
                    }
                    Err(e) => {
                        return HookResult {
                            name: hook_name.into(),
                            rc: 1,
                            stdout: String::new(),
                            stderr: format!("wait error: {e}"),
                        };
                    }
                }
            }
        }
        None => {
            let output = child.wait_with_output().unwrap_or_else(|e| {
                panic!("failed to wait on hook {hook_name}: {e}");
            });
            HookResult {
                name: hook_name.into(),
                rc: output.status.code().unwrap_or(1),
                stdout: String::from_utf8_lossy(&output.stdout).into_owned(),
                stderr: String::from_utf8_lossy(&output.stderr).into_owned(),
            }
        }
    }
}

// ---------------------------------------------------------------------------
// Run hooks sequentially, fail-fast (pretool, promptsubmit)
// Returns the first non-zero exit code, or 0 if all succeed.
// ---------------------------------------------------------------------------

fn run_sequential_blocking(
    hooks: &[(&str, &[&str])],
    hooks_dir: &Path,
    env_map: &HashMap<String, String>,
    temp_path: &Path,
) -> i32 {
    for (hook, args) in hooks {
        let result = run_hook(hooks_dir, hook, args, env_map, temp_path, None);
        if !result.stdout.is_empty() {
            eprint!("{}", result.stdout);
        }
        if result.rc != 0 {
            if !result.stderr.is_empty() {
                eprint!("{}", result.stderr);
            }
            return result.rc;
        }
    }
    0
}

// ---------------------------------------------------------------------------
// Run hooks in a SINGLE bash process via source (saves N-1 bash spawns).
// Generates a wrapper script that sources each hook sequentially.
// Fail-fast: stops on first non-zero exit.
// ---------------------------------------------------------------------------

fn run_combined_blocking(
    hooks: &[(&str, &[&str])],
    hooks_dir: &Path,
    env_map: &HashMap<String, String>,
    temp_path: &Path,
) -> i32 {
    // Filter to hooks that actually exist
    let existing: Vec<&str> = hooks
        .iter()
        .filter(|(h, _)| hooks_dir.join(h).exists())
        .map(|(h, _)| *h)
        .collect();

    if existing.is_empty() {
        return 0;
    }

    // If only one hook, just run it directly (no wrapper overhead)
    if existing.len() == 1 {
        let result = run_hook(hooks_dir, existing[0], &[], env_map, temp_path, None);
        if !result.stdout.is_empty() {
            eprint!("{}", result.stdout);
        }
        if result.rc != 0 && !result.stderr.is_empty() {
            eprint!("{}", result.stderr);
        }
        return result.rc;
    }

    // Generate combined wrapper script
    let hdir = hooks_dir.to_string_lossy();
    let mut script = String::from("#!/usr/bin/env bash\nset -uo pipefail\n");
    for h in &existing {
        // Source each hook in a subshell so `exit` doesn't kill the wrapper
        script.push_str(&format!(
            "( source \"{hdir}/{h}\" ) < \"{}\" || exit $?\n",
            temp_path.to_string_lossy()
        ));
    }
    script.push_str("exit 0\n");

    // Write wrapper to temp file
    let wrapper_path = PathBuf::from(format!(
        "/tmp/hook-combined-{}.sh",
        std::process::id()
    ));
    if fs::write(&wrapper_path, &script).is_err() {
        // Fallback to individual execution
        return run_sequential_blocking(hooks, hooks_dir, env_map, temp_path);
    }

    let stdin_file = match fs::File::open(temp_path) {
        Ok(f) => f,
        Err(_) => {
            let _ = fs::remove_file(&wrapper_path);
            return 1;
        }
    };

    let mut cmd = Command::new("bash");
    cmd.arg(&wrapper_path)
        .stdin(Stdio::from(stdin_file))
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());

    // Inherit parent environment + overlay hook vars
    for (k, v) in env_map {
        cmd.env(k, v);
    }

    if let Some(project_dir) = env_map.get("PROJECT_DIR") {
        if !project_dir.is_empty() && Path::new(project_dir).is_dir() {
            cmd.current_dir(project_dir);
        }
    }

    let result = match cmd.output() {
        Ok(output) => {
            if !output.stdout.is_empty() {
                eprint!("{}", String::from_utf8_lossy(&output.stdout));
            }
            if output.status.code().unwrap_or(1) != 0 && !output.stderr.is_empty() {
                eprint!("{}", String::from_utf8_lossy(&output.stderr));
            }
            output.status.code().unwrap_or(1)
        }
        Err(_) => {
            let _ = fs::remove_file(&wrapper_path);
            return run_sequential_blocking(hooks, hooks_dir, env_map, temp_path);
        }
    };

    let _ = fs::remove_file(&wrapper_path);
    result
}

// ---------------------------------------------------------------------------
// Same as run_combined_blocking but advisory (always returns 0).
// ---------------------------------------------------------------------------

fn run_combined_advisory(
    hooks: &[(&str, &[&str])],
    hooks_dir: &Path,
    env_map: &HashMap<String, String>,
    temp_path: &Path,
    label: &str,
) -> i32 {
    let existing: Vec<&str> = hooks
        .iter()
        .filter(|(h, _)| hooks_dir.join(h).exists())
        .map(|(h, _)| *h)
        .collect();

    if existing.is_empty() {
        return 0;
    }

    if existing.len() == 1 {
        let result = run_hook(hooks_dir, existing[0], &[], env_map, temp_path, None);
        if !result.stdout.is_empty() {
            eprint!("{}", result.stdout);
        }
        if result.rc != 0 {
            if !result.stderr.is_empty() {
                eprint!("{}", result.stderr);
            }
            eprintln!("{label} DISPATCHER: advisory failure: {}(rc={})", result.name, result.rc);
        }
        return 0;
    }

    let hdir = hooks_dir.to_string_lossy();
    let mut script = String::from("#!/usr/bin/env bash\nset -uo pipefail\n_failures=\"\"\n");
    for h in &existing {
        script.push_str(&format!(
            "( source \"{hdir}/{h}\" ) < \"{}\" || _failures=\"$_failures {h}\"\n",
            temp_path.to_string_lossy()
        ));
    }
    script.push_str(&format!(
        "[[ -n \"$_failures\" ]] && echo \"{label} DISPATCHER: advisory failures:$_failures\" >&2\nexit 0\n"
    ));

    let wrapper_path = PathBuf::from(format!("/tmp/hook-combined-{}.sh", std::process::id()));
    if fs::write(&wrapper_path, &script).is_err() {
        return run_sequential_advisory(hooks, hooks_dir, env_map, temp_path, label);
    }

    let stdin_file = match fs::File::open(temp_path) {
        Ok(f) => f,
        Err(_) => {
            let _ = fs::remove_file(&wrapper_path);
            return 0;
        }
    };

    let mut cmd = Command::new("bash");
    cmd.arg(&wrapper_path)
        .stdin(Stdio::from(stdin_file))
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());

    for (k, v) in env_map {
        cmd.env(k, v);
    }

    if let Some(project_dir) = env_map.get("PROJECT_DIR") {
        if !project_dir.is_empty() && Path::new(project_dir).is_dir() {
            cmd.current_dir(project_dir);
        }
    }

    if let Ok(output) = cmd.output() {
        if !output.stdout.is_empty() {
            eprint!("{}", String::from_utf8_lossy(&output.stdout));
        }
        if !output.stderr.is_empty() {
            eprint!("{}", String::from_utf8_lossy(&output.stderr));
        }
    }

    let _ = fs::remove_file(&wrapper_path);
    0
}

// ---------------------------------------------------------------------------
// Run hooks sequentially, advisory (sessionstart, precompact)
// Runs all hooks regardless of exit code. Always returns 0.
// ---------------------------------------------------------------------------

fn run_sequential_advisory(
    hooks: &[(&str, &[&str])],
    hooks_dir: &Path,
    env_map: &HashMap<String, String>,
    temp_path: &Path,
    label: &str,
) -> i32 {
    let mut failures = Vec::new();
    for (hook, args) in hooks {
        let result = run_hook(hooks_dir, hook, args, env_map, temp_path, None);
        if !result.stdout.is_empty() {
            eprint!("{}", result.stdout);
        }
        if result.rc != 0 {
            failures.push(format!("{}(rc={})", result.name, result.rc));
            if !result.stderr.is_empty() {
                eprint!("{}", result.stderr);
            }
        }
    }
    if !failures.is_empty() {
        eprintln!(
            "{} DISPATCHER: advisory failures: {}",
            label,
            failures.join("; ")
        );
    }
    0
}

// ---------------------------------------------------------------------------
// Run hooks in parallel (posttool / stop)
// ---------------------------------------------------------------------------

// fn run_parallel(
//    hooks: &[(&str, &[&str])],
//    hooks_dir: &Path,
//    env_map: &HashMap<String, String>,
//    temp_path: &Path,
//    timeout: Option<Duration>,
// ) -> Vec<HookResult> {
//    let env_arc = Arc::new(env_map.clone());
//    let hooks_dir_arc = Arc::new(hooks_dir.to_path_buf());
//    let temp_path_arc = Arc::new(temp_path.to_path_buf());
//    let results: Arc<Mutex<Vec<HookResult>>> = Arc::new(Mutex::new(Vec::new()));
//
//    let mut handles = Vec::new();
//
//    for (hook, args) in hooks {
//        let hook_name = hook.to_string();
//        let args_owned: Vec<String> = args.iter().map(|a| a.to_string()).collect();
//        let env_c = Arc::clone(&env_arc);
//        let hdir = Arc::clone(&hooks_dir_arc);
//        let tpath = Arc::clone(&temp_path_arc);
//        let res = Arc::clone(&results);
//
//        let handle = thread::spawn(move || {
//            let args_refs: Vec<&str> = args_owned.iter().map(|s| s.as_str()).collect();
//            let result = run_hook(&hdir, &hook_name, &args_refs, &env_c, &tpath, timeout);
//            res.lock().unwrap().push(result);
//        });
//        handles.push(handle);
//    }
//
//    for h in handles {
//        let _ = h.join();
//    }
//
//    Arc::try_unwrap(results).unwrap().into_inner().unwrap()
// }

// ---------------------------------------------------------------------------
// Run hooks in parallel with output-based (idle) timeout
// ---------------------------------------------------------------------------

fn run_parallel_with_idle_timeout(
    hooks: &[(&str, &[&str])],
    hooks_dir: &Path,
    env_map: &HashMap<String, String>,
    temp_path: &Path,
    idle_timeout: Duration,
    max_timeout: Duration,
) -> Vec<HookResult> {
    let env_arc = Arc::new(env_map.clone());
    let hooks_dir_arc = Arc::new(hooks_dir.to_path_buf());
    let temp_path_arc = Arc::new(temp_path.to_path_buf());
    let results: Arc<Mutex<Vec<HookResult>>> = Arc::new(Mutex::new(Vec::new()));

    let mut handles = Vec::new();

    for (hook, args) in hooks {
        let hook_name = hook.to_string();
        let args_owned: Vec<String> = args.iter().map(|a| a.to_string()).collect();
        let env_c = Arc::clone(&env_arc);
        let hdir = Arc::clone(&hooks_dir_arc);
        let tpath = Arc::clone(&temp_path_arc);
        let res = Arc::clone(&results);

        let handle = thread::spawn(move || {
            let args_refs: Vec<&str> = args_owned.iter().map(|s| s.as_str()).collect();
            let result =
                run_hook_with_idle_timeout(&hdir, &hook_name, &args_refs, &env_c, &tpath, idle_timeout, max_timeout);
            res.lock().unwrap().push(result);
        });
        handles.push(handle);
    }

    for h in handles {
        let _ = h.join();
    }

    Arc::try_unwrap(results).unwrap().into_inner().unwrap()
}

// ---------------------------------------------------------------------------
// Run a single hook, advisory (subagentstart, subagentstop, sessionend,
// taskcompleted). Always returns 0.
// ---------------------------------------------------------------------------

fn run_single_advisory(
    hook: &str,
    args: &[&str],
    hooks_dir: &Path,
    env_map: &HashMap<String, String>,
    temp_path: &Path,
    label: &str,
) -> i32 {
    let result = run_hook(hooks_dir, hook, args, env_map, temp_path, None);
    if !result.stdout.is_empty() {
        eprint!("{}", result.stdout);
    }
    if result.rc != 0 {
        if !result.stderr.is_empty() {
            eprint!("{}", result.stderr);
        }
        eprintln!(
            "{} DISPATCHER: advisory failure: {}(rc={})",
            label, result.name, result.rc
        );
    }
    0
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

fn main() -> ExitCode {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!(
            "usage: hook-dispatcher <pretool|posttool|stop|sessionstart|promptsubmit|\
             subagentstart|subagentstop|precompact|sessionend|taskcompleted|teammateidle|postagentrun|\
             scan-secrets|governance>"
        );
        return ExitCode::from(1);
    }

    // Dispatch scan-secrets subcommand before mode parsing (no stdin JSON needed)
    if args[1] == "scan-secrets" {
        return cmd_scan_secrets(&args);
    }

    // Dispatch governance subcommand before mode parsing (BKM-11)
    if args[1] == "governance" {
        return cmd_governance(&args);
    }

    let mode = match args[1].as_str() {
        "pretool" => Mode::Pretool,
        "posttool" => Mode::Posttool,
        "stop" => Mode::Stop,
        "sessionstart" => Mode::SessionStart,
        "promptsubmit" => Mode::PromptSubmit,
        "subagentstart" => Mode::SubagentStart,
        "subagentstop" => Mode::SubagentStop,
        "precompact" => Mode::PreCompact,
        "sessionend" => Mode::SessionEnd,
        "taskcompleted" => Mode::TaskCompleted,
        "teammateidle" => Mode::TeammateIdle,
        "postagentrun" => Mode::PostAgentRun,
        other => {
            eprintln!("unknown mode: {other}");
            return ExitCode::from(1);
        }
    };

    // Read stdin — when run from TTY (e.g. `hook-dispatcher stop`), use empty JSON to avoid blocking
    let mut raw_json = String::new();
    if std::io::stdin().is_terminal() {
        raw_json = "{}".to_string();
    } else {
        std::io::stdin()
            .read_to_string(&mut raw_json)
            .expect("failed to read stdin");
        if raw_json.trim().is_empty() {
            raw_json = "{}".to_string();
        }
    }

    // Parse JSON
    let input: HookInput = match serde_json::from_str(&raw_json) {
        Ok(v) => v,
        Err(e) => {
            eprintln!("JSON parse error: {e}");
            return ExitCode::from(1);
        }
    };

    let hooks_dir = resolve_hooks_dir();
    let mut env_map = build_env(&input, &raw_json, mode, &hooks_dir);
    let temp_file = TempFile::new(&raw_json);

    match mode {
        // -----------------------------------------------------------------
        // PreToolUse: sequential, fail-fast (blocking)
        // -----------------------------------------------------------------
        Mode::Pretool => {
            let tool_name = input.tool_name.as_deref().unwrap_or("");
            
            // Native pre-tool checks
            if tool_name == "Write" {
                let rc = run_doc_location_guard(&env_map);
                if rc != 0 {
                    return ExitCode::from(rc as u8);
                }
            }

            let hooks: Vec<(&str, &[&str])> = match tool_name {
                "Write" => vec![
                    ("pre-write-validator.sh", &[]),
                    ("suppression-blocker.sh", &[]),
                ],
                "Edit" => vec![
                    ("pre-write-validator.sh", &[]),
                    ("suppression-blocker.sh", &[]),
                ],
                _ => return ExitCode::from(0),
            };
            let rc = run_combined_blocking(&hooks, &hooks_dir, &env_map, &temp_file.path);
            ExitCode::from(rc as u8)
        }

        // -----------------------------------------------------------------
        // PostToolUse: parallel, advisory
        // -----------------------------------------------------------------
        Mode::Posttool => {
            let hooks: Vec<(&str, &[&str])> = vec![
                ("change-doc-tracker.sh", &[]),
                ("qa-evidence-recorder.sh", &[]),
                ("qa-policy-test.sh", &[]),
                ("post-edit-checker.sh", &[]),
                ("async-test-runner.sh", &[]),
                ("speculative-stop-prewarmer.sh", &[]),
            ];
            let rc = run_combined_advisory(&hooks, &hooks_dir, &env_map, &temp_file.path, "POSTTOOL");
            ExitCode::from(rc as u8)
        }

        // -----------------------------------------------------------------
        // Stop: parallel with timeout, propagate exit code
        // -----------------------------------------------------------------
        Mode::Stop => {
            let stop_settings = read_stop_settings(&env_map.get("PROJECT_DIR").cloned().unwrap_or_default());
            env_map.insert("THGENT_STOP_PROFILE".into(), stop_settings.profile.clone());
            env_map.insert(
                "THGENT_STOP_IDLE_TIMEOUT_SEC".into(),
                stop_settings.idle_timeout_sec.to_string(),
            );
            env_map.insert(
                "THGENT_STOP_MAX_TIMEOUT_SEC".into(),
                stop_settings.max_timeout_sec.to_string(),
            );

            // MTSP-08: Partial native governance scan
            if stop_settings.profile == "full" {
                if let Some(dir) = env_map.get("PROJECT_DIR") {
                    run_governance_scan(dir);
                }
            }

            // MTSP-18: Trigger memory scraping on Stop
            let _ = Command::new("thegent")
                .args(["memory", "scrape"])
                .current_dir(env_map.get("PROJECT_DIR").cloned().unwrap_or_default())
                .stdout(Stdio::null())
                .stderr(Stdio::null())
                .spawn();

            let hooks: Vec<(&str, &[&str])> = match stop_settings.profile.as_str() {
                // Minimal floor for very tight loops.
                "ultrafast" => vec![
                    ("stop-reconcile.sh", &[]),
                ],
                // Hybrid fast profile: keep bounded runtime while still running stage-gated quality checks.
                "fast" => vec![
                    ("quality-gate.sh", &[]),
                    ("stop-reconcile.sh", &[]),
                ],
                // Standard profile: adds task closure and orphan pruning.
                "standard" => vec![
                    ("quality-gate.sh", &[]),
                    ("prune-orphans-stop.sh", &[]),
                    ("stop-reconcile.sh", &[]),
                    ("task-completion-verifier.sh", &[]),
                    ("teammate-reconcile.sh", &[]),
                ],
                // Full profile: all governance + verification hooks.
                _ => vec![
                    ("harvest-idea-seeds-stop.sh", &[]),
                    ("harvest-pending-queue.sh", &[]),
                    ("governance-gates.sh", &[]),
                    ("qa-supply-chain-verifier.sh", &[]),
                    ("quality-gate.sh", &[]),
                    ("complexity-ratchet.sh", &[]),
                    ("security-pipeline.sh", &[]),
                    ("spec-verifier.sh", &[]),
                    ("test-maturity.sh", &[]),
                    ("prune-orphans-stop.sh", &[]),
                    ("stop-reconcile.sh", &[]),
                    ("task-completion-verifier.sh", &[]),
                    ("teammate-reconcile.sh", &[]),
                ],
            };

            // Filter out skipped hooks
            let project_dir = env_map.get("PROJECT_DIR").cloned().unwrap_or_default();
            let skip_list = get_skip_hooks(&project_dir);
            let hooks: Vec<(&str, &[&str])> = hooks
                .into_iter()
                .filter(|(name, _)| !should_skip_hook(name, &skip_list))
                .collect();

            // Print skip notifications
            for name in skip_list.iter() {
                eprintln!("SKIP_HOOKS: skipping {}.sh", name);
            }

            // Output-based (idle) timeout and absolute max timeout are hard-clamped
            // into the 5..15s range to avoid long Stop stalls.
            let idle_timeout = Duration::from_secs(stop_settings.idle_timeout_sec);
            let max_timeout = Duration::from_secs(stop_settings.max_timeout_sec);
            eprintln!(
                "STOP DISPATCHER: profile={}, idle_timeout={}s, max_timeout={}s, hooks={}",
                stop_settings.profile,
                stop_settings.idle_timeout_sec,
                stop_settings.max_timeout_sec,
                hooks.len()
            );
            let results = run_parallel_with_idle_timeout(
                &hooks,
                &hooks_dir,
                &env_map,
                &temp_file.path,
                idle_timeout,
                max_timeout,
            );

            let mut max_rc: i32 = 0;
            let mut failures = Vec::new();
            for r in &results {
                // Only print output on failure (not on success)
                if r.rc != 0 {
                    if !r.stdout.is_empty() {
                        eprint!("{}", r.stdout);
                    }
                    failures.push(format!("{}(rc={})", r.name, r.rc));
                    if !r.stderr.is_empty() {
                        eprint!("{}", r.stderr);
                    }
                }
                if r.rc > max_rc {
                    max_rc = r.rc;
                }
            }
            // Only print failure summary if there are actual failures
            // Silent on complete success (no output when all hooks pass)
            if !failures.is_empty() {
                eprintln!(
                    "STOP DISPATCHER: non-zero from: {}",
                    failures.join("; ")
                );
            }
            let notify_msg = if failures.is_empty() {
                format!(
                    "profile={} hooks={} status=ok",
                    stop_settings.profile,
                    hooks.len()
                )
            } else {
                format!(
                    "profile={} hooks={} failures={}",
                    stop_settings.profile,
                    hooks.len(),
                    failures.join(", ")
                )
            };
            dispatch_notification(
                &hooks_dir,
                &env_map,
                "stop",
                if failures.is_empty() { "info" } else { "error" },
                if failures.is_empty() { "Stop Complete" } else { "Stop Issues" },
                &notify_msg,
            );
            // Clamp to u8 range
            let exit_val = if max_rc > 255 { 255 } else { max_rc as u8 };
            ExitCode::from(exit_val)
        }

        // -----------------------------------------------------------------
        // SessionStart: sequential, advisory
        // -----------------------------------------------------------------
        Mode::SessionStart => {
            let hooks: Vec<(&str, &[&str])> = vec![
                ("spec-preflight.sh", &[]),
                ("qa-preflight.sh", &[]),
                ("session-start-pending-notice.sh", &[]),
                ("session-start-spotlight-exclude.sh", &[]),
            ];
            let rc = run_combined_advisory(
                &hooks,
                &hooks_dir,
                &env_map,
                &temp_file.path,
                "SESSIONSTART",
            );
            ExitCode::from(rc as u8)
        }

        // -----------------------------------------------------------------
        // UserPromptSubmit: sequential, blocking (fail-fast)
        // -----------------------------------------------------------------
        Mode::PromptSubmit => {
            let native_rc = run_prompt_submit_guard(&env_map, &serde_json::to_value(&input).unwrap());
            if native_rc != 99 {
                return ExitCode::from(native_rc as u8);
            }
            let hooks: Vec<(&str, &[&str])> = vec![
                ("prompt-submit-guard.sh", &[]),
            ];
            let rc = run_combined_blocking(&hooks, &hooks_dir, &env_map, &temp_file.path);
            ExitCode::from(rc as u8)
        }

        // -----------------------------------------------------------------
        // SubagentStart: single script, advisory (with "start" argument)
        // -----------------------------------------------------------------
        Mode::SubagentStart => {
            let rc = run_single_advisory(
                "subagent-quality-gate.sh",
                &["start"],
                &hooks_dir,
                &env_map,
                &temp_file.path,
                "SUBAGENTSTART",
            );
            ExitCode::from(rc as u8)
        }

        // -----------------------------------------------------------------
        // SubagentStop: single script, advisory (with "stop" argument)
        // -----------------------------------------------------------------
        Mode::SubagentStop => {
            let rc = run_single_advisory(
                "subagent-quality-gate.sh",
                &["stop"],
                &hooks_dir,
                &env_map,
                &temp_file.path,
                "SUBAGENTSTOP",
            );
            ExitCode::from(rc as u8)
        }

        // -----------------------------------------------------------------
        // PreCompact: sequential, advisory
        // -----------------------------------------------------------------
        Mode::PreCompact => {
            let hooks: Vec<(&str, &[&str])> = vec![
                ("pre-compact-snapshot.sh", &[]),
                ("auto-checkpoint.sh", &[]),
            ];
            let rc = run_combined_advisory(
                &hooks,
                &hooks_dir,
                &env_map,
                &temp_file.path,
                "PRECOMPACT",
            );
            ExitCode::from(rc as u8)
        }

        // -----------------------------------------------------------------
        // SessionEnd: single script, advisory
        // -----------------------------------------------------------------
        Mode::SessionEnd => {
            let rc = run_session_cleanup(&env_map);
            dispatch_notification(
                &hooks_dir,
                &env_map,
                "sessionend",
                "info",
                "Session Complete",
                "",
            );
            ExitCode::from(rc as u8)
        }

        // -----------------------------------------------------------------
        // TaskCompleted: single script, advisory
        // -----------------------------------------------------------------
        Mode::TaskCompleted => {
            // Run quality verifier first
            run_single_advisory(
                "task-completion-verifier.sh",
                &[],
                &hooks_dir,
                &env_map,
                &temp_file.path,
                "TASKCOMPLETED",
            );
            // Then run teammate coordination hook
            let rc = run_single_advisory(
                "task-completed.sh",
                &[],
                &hooks_dir,
                &env_map,
                &temp_file.path,
                "TASKCOMPLETED",
            );
            ExitCode::from(rc as u8)
        }

        // -----------------------------------------------------------------
        // TeammateIdle: single script, advisory (with exit 2 sentinel)
        // -----------------------------------------------------------------
        Mode::TeammateIdle => {
            // TeammateIdle is special: it can return exit 2 to signal feedback injection.
            // So we don't use run_single_advisory which forces exit 0.
            let result = run_hook(&hooks_dir, "teammate-idle.sh", &[], &env_map, &temp_file.path, None);
            if !result.stdout.is_empty() {
                eprint!("{}", result.stdout);
            }
            if result.rc != 0 && result.rc != 2 {
                if !result.stderr.is_empty() {
                    eprint!("{}", result.stderr);
                }
                eprintln!(
                    "TEAMMATEIDLE DISPATCHER: failure: {}(rc={})",
                    result.name, result.rc
                );
            }
            ExitCode::from(result.rc as u8)
        }

        // -----------------------------------------------------------------
        // PostAgentRun: single script, blocking
        // -----------------------------------------------------------------
        Mode::PostAgentRun => {
            let hooks: Vec<(&str, &[&str])> = vec![
                ("post-agent-run-vetter.sh", &[]),
            ];
            let rc = run_combined_blocking(&hooks, &hooks_dir, &env_map, &temp_file.path);
            ExitCode::from(rc as u8)
        }
    }
}

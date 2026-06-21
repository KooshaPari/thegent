// SPDX-License-Identifier: MIT OR Apache-2.0
use std::collections::HashMap;
use std::io::{self, Read};
use std::process::ExitCode;

use serde::Deserialize;
use serde_json::Value;
use thegent_hooks::{PolicyEngine, PolicyRule, QualityMetrics, QualityThresholds};

#[derive(Debug, Deserialize)]
struct QualityGateInput {
    #[serde(default)]
    rules: Vec<PolicyRule>,
    #[serde(default)]
    context: HashMap<String, Value>,
    #[serde(default)]
    quality: QualityMetrics,
    thresholds: QualityThresholds,
}

fn main() -> ExitCode {
    let mut stdin = String::new();
    if let Err(err) = io::stdin().read_to_string(&mut stdin) {
        eprintln!("quality-gate: failed to read stdin: {err}");
        return ExitCode::from(124);
    }

    let input: QualityGateInput = match serde_json::from_str(&stdin) {
        Ok(v) => v,
        Err(err) => {
            eprintln!("quality-gate: invalid input JSON: {err}");
            return ExitCode::from(124);
        }
    };

    let mut violations: Vec<String> = Vec::new();
    let engine = PolicyEngine::new(input.rules);
    match engine.evaluate(&input.context) {
        Ok(outcomes) => {
            for outcome in outcomes {
                if !outcome.passed {
                    violations.push(format!(
                        "policy {} failed: {}",
                        outcome.rule_id, outcome.message
                    ));
                }
            }
        }
        Err(err) => {
            eprintln!("quality-gate: policy evaluation failed: {err}");
            return ExitCode::from(124);
        }
    }

    if input.quality.coverage_percent < input.thresholds.min_coverage {
        violations.push(format!(
            "coverage below threshold: {:.2} < {:.2}",
            input.quality.coverage_percent, input.thresholds.min_coverage
        ));
    }
    if input.quality.lint_errors > input.thresholds.max_lint_errors {
        violations.push(format!(
            "lint errors above threshold: {} > {}",
            input.quality.lint_errors, input.thresholds.max_lint_errors
        ));
    }
    if input.quality.cyclomatic_complexity > input.thresholds.max_cyclomatic_complexity {
        violations.push(format!(
            "cyclomatic complexity above threshold: {} > {}",
            input.quality.cyclomatic_complexity, input.thresholds.max_cyclomatic_complexity
        ));
    }
    if input.quality.cognitive_complexity > input.thresholds.max_cognitive_complexity {
        violations.push(format!(
            "cognitive complexity above threshold: {} > {}",
            input.quality.cognitive_complexity, input.thresholds.max_cognitive_complexity
        ));
    }
    if input.quality.function_max_lines > input.thresholds.max_function_lines {
        violations.push(format!(
            "max function lines above threshold: {} > {}",
            input.quality.function_max_lines, input.thresholds.max_function_lines
        ));
    }

    if violations.is_empty() {
        println!("quality-gate: pass");
        ExitCode::SUCCESS
    } else {
        for v in violations {
            eprintln!("{v}");
        }
        ExitCode::from(1)
    }
}

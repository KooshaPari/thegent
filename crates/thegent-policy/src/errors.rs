// SPDX-License-Identifier: MIT OR Apache-2.0
use thiserror::Error;

#[derive(Error, Debug)]
pub enum PolicyError {
    #[error("Failed to load config: {0}")]
    ConfigLoadError(String),

    #[error("Failed to parse config: {0}")]
    ConfigParseError(String),

    #[error("Rule not found: {0}")]
    RuleNotFound(String),

    #[error("Evaluation error: {0}")]
    EvaluationError(String),
}

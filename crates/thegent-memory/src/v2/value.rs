// SPDX-License-Identifier: MIT OR Apache-2.0
//! Value + error types for the v2 memory port.

use serde::{Deserialize, Serialize};
use thiserror::Error;

/// Scope of a memory operation. The composite router dispatches by scope
/// (Episodic → supermemory, Identity → letta, ProjectKnowledge → cognee,
/// Fallback → mem0).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum MemoryScope {
    /// Session / conversation history (the smfs filesystem layer).
    Episodic,
    /// Per-agent identity / persistent state (Letta subconscious blocks).
    Identity,
    /// Project knowledge graph (Cognee KG).
    ProjectKnowledge,
    /// Fallback when the primary for a scope is unavailable.
    Fallback,
}

impl MemoryScope {
    pub fn as_str(&self) -> &'static str {
        match self {
            MemoryScope::Episodic => "episodic",
            MemoryScope::Identity => "identity",
            MemoryScope::ProjectKnowledge => "project_knowledge",
            MemoryScope::Fallback => "fallback",
        }
    }
}

impl std::fmt::Display for MemoryScope {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(self.as_str())
    }
}

/// The value stored under a (`scope`, `key`). Backends accept strings
/// natively; binary blobs go through a hex/base64 transport (depending
/// on the backend's preference) at the adapter boundary.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(untagged)]
pub enum MemoryValue {
    Text(String),
    Binary(Vec<u8>),
    Json(serde_json::Value),
}

impl From<&str> for MemoryValue {
    fn from(s: &str) -> Self {
        MemoryValue::Text(s.to_string())
    }
}

impl From<String> for MemoryValue {
    fn from(s: String) -> Self {
        MemoryValue::Text(s)
    }
}

impl From<Vec<u8>> for MemoryValue {
    fn from(v: Vec<u8>) -> Self {
        MemoryValue::Binary(v)
    }
}

impl From<&[u8]> for MemoryValue {
    fn from(v: &[u8]) -> Self {
        MemoryValue::Binary(v.to_vec())
    }
}

impl From<serde_json::Value> for MemoryValue {
    fn from(v: serde_json::Value) -> Self {
        MemoryValue::Json(v)
    }
}

/// A recall query. The `text` field is the natural-language / keyword query
/// that the backend's retriever matches against. `limit` caps the result
/// count; `min_score` filters low-relevance hits (where supported).
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct MemoryQuery {
    pub text: String,
    pub limit: usize,
    pub min_score: Option<f32>,
}

impl MemoryQuery {
    pub fn new(text: impl Into<String>) -> Self {
        Self {
            text: text.into(),
            limit: 10,
            min_score: None,
        }
    }

    pub fn with_limit(mut self, limit: usize) -> Self {
        self.limit = limit;
        self
    }

    pub fn with_min_score(mut self, score: f32) -> Self {
        self.min_score = Some(score);
        self
    }
}

/// A single record returned from `recall`.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct MemoryRecord {
    pub id: String,
    pub scope: MemoryScope,
    pub key: String,
    pub value: MemoryValue,
    pub score: Option<f32>,
}

#[derive(Debug, Error)]
pub enum MemoryError {
    #[error("network error: {0}")]
    Network(String),

    #[error("backend returned status {status}: {body}")]
    Backend { status: u16, body: String },

    #[error("not found: scope={scope} key={key}")]
    NotFound { scope: MemoryScope, key: String },

    #[error("serialization error: {0}")]
    Serde(String),

    #[error("backend unavailable: {0}")]
    Unavailable(String),

    #[error("invalid argument: {0}")]
    Invalid(String),

    #[error("internal error: {0}")]
    Internal(String),
}

impl From<reqwest::Error> for MemoryError {
    fn from(e: reqwest::Error) -> Self {
        if e.is_connect() || e.is_timeout() {
            MemoryError::Unavailable(e.to_string())
        } else {
            MemoryError::Network(e.to_string())
        }
    }
}

impl From<serde_json::Error> for MemoryError {
    fn from(e: serde_json::Error) -> Self {
        MemoryError::Serde(e.to_string())
    }
}
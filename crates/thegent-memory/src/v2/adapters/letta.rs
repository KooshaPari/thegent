// SPDX-License-Identifier: MIT OR Apache-2.0
//! [`LettaAdapter`] — subconscious memory blocks per-agent identity.
//!
//! Talks to the Letta server (`letta-ai/letta`) over its REST API
//! (default `http://127.0.0.1:8283`, surfaced by the `pheno-letta` sidecar
//! in `pheno-forge-plugins`). Only the `Identity` scope is supported; other
//! scopes return [`MemoryError::Invalid`].
//!
//! Letta's "subconscious" is the auto-managed trio of:
//! - `core_memory` — in-context blocks (label/value pairs visible to the LLM)
//! - `archival_memory` — vector store, out-of-context, persistent
//! - `recall_memory` — conversation history
//!
//! We map `store` → archival `insert`, `recall` → archival `search`,
//! `forget` → archival `delete`.

use async_trait::async_trait;
use reqwest::Client;
use serde::{Deserialize, Serialize};

use crate::v2::adapters::default_base_url;
use crate::v2::port::{MemoryPort, MemoryProvider};
use crate::v2::value::{
    MemoryError, MemoryQuery, MemoryRecord, MemoryScope, MemoryValue,
};

pub struct LettaAdapter {
    base_url: String,
    client: Client,
}

impl LettaAdapter {
    pub fn default_endpoint() -> Self {
        Self::new(default_base_url(MemoryProvider::Letta).to_string())
    }

    pub fn new(base_url: String) -> Self {
        Self {
            base_url,
            client: Client::new(),
        }
    }
}

#[derive(Debug, Serialize)]
struct ArchivalInsertRequest<'a> {
    agent_id: &'a str,
    content: &'a str,
    #[serde(skip_serializing_if = "Option::is_none")]
    name: Option<&'a str>,
}

#[derive(Debug, Deserialize)]
struct ArchivalInsertResponse {
    id: String,
}

#[derive(Debug, Serialize)]
struct ArchivalSearchRequest<'a> {
    agent_id: &'a str,
    query: &'a str,
    #[serde(rename = "limit")]
    limit: usize,
}

#[derive(Debug, Deserialize)]
struct ArchivalSearchResponse {
    passages: Vec<ArchivalPassage>,
}

#[derive(Debug, Deserialize)]
struct ArchivalPassage {
    id: String,
    text: String,
    #[serde(default)]
    score: Option<f32>,
}

#[async_trait]
impl MemoryPort for LettaAdapter {
    async fn store(
        &self,
        scope: MemoryScope,
        key: &str,
        value: MemoryValue,
    ) -> Result<String, MemoryError> {
        if scope != MemoryScope::Identity {
            return Err(MemoryError::Invalid(format!(
                "LettaAdapter only supports Identity scope (got {:?})",
                scope
            )));
        }
        let content = match &value {
            MemoryValue::Text(s) => s.as_str(),
            MemoryValue::Json(v) => &serde_json::to_string(v)?,
            MemoryValue::Binary(_) => {
                return Err(MemoryError::Invalid(
                    "binary blobs not supported by LettaAdapter; pre-encode".into(),
                ))
            }
        };
        let req = ArchivalInsertRequest {
            agent_id: key, // key = letta agent_id
            content,
            name: None,
        };
        let resp = self
            .client
            .post(format!("{}/v1/agents/{}/archival-memory", self.base_url, key))
            .json(&req)
            .send()
            .await?;
        let status = resp.status();
        if !status.is_success() {
            let body = resp.text().await.unwrap_or_default();
            return Err(MemoryError::Backend {
                status: status.as_u16(),
                body,
            });
        }
        let parsed: ArchivalInsertResponse = resp.json().await?;
        Ok(parsed.id)
    }

    async fn recall(
        &self,
        scope: MemoryScope,
        query: MemoryQuery,
    ) -> Result<Vec<MemoryRecord>, MemoryError> {
        if scope != MemoryScope::Identity {
            return Err(MemoryError::Invalid(format!(
                "LettaAdapter only supports Identity scope (got {:?})",
                scope
            )));
        }
        // For recall without an explicit agent_id we use a wildcard endpoint.
        let req = ArchivalSearchRequest {
            agent_id: "_any_",
            query: &query.text,
            limit: query.limit,
        };
        let resp = self
            .client
            .post(format!("{}/v1/agents/_any_/archival-memory/search", self.base_url))
            .json(&req)
            .send()
            .await?;
        let status = resp.status();
        if !status.is_success() {
            let body = resp.text().await.unwrap_or_default();
            return Err(MemoryError::Backend {
                status: status.as_u16(),
                body,
            });
        }
        let parsed: ArchivalSearchResponse = resp.json().await?;
        Ok(parsed
            .passages
            .into_iter()
            .map(|p| {
                let id = p.id.clone();
                MemoryRecord {
                    id,
                    scope,
                    key: p.id,
                    value: MemoryValue::Text(p.text),
                    score: p.score,
                }
            })
            .collect())
    }

    async fn forget(&self, scope: MemoryScope, key: &str) -> Result<(), MemoryError> {
        if scope != MemoryScope::Identity {
            return Err(MemoryError::Invalid(format!(
                "LettaAdapter only supports Identity scope (got {:?})",
                scope
            )));
        }
        let resp = self
            .client
            .delete(format!("{}/v1/agents/{}/archival-memory/{}", self.base_url, key, key))
            .send()
            .await?;
        let status = resp.status();
        if status.is_success() || status.as_u16() == 404 {
            return Ok(());
        }
        let body = resp.text().await.unwrap_or_default();
        Err(MemoryError::Backend {
            status: status.as_u16(),
            body,
        })
    }

    async fn list_scopes(&self) -> Result<Vec<MemoryScope>, MemoryError> {
        Ok(vec![MemoryScope::Identity])
    }

    fn provider(&self) -> MemoryProvider {
        MemoryProvider::Letta
    }
}
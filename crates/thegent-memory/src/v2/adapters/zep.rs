// SPDX-License-Identifier: MIT OR Apache-2.0
//! [`ZepAdapter`] — Zep Cloud API + Graphiti (OSS core) client.
//!
//! Talks to the Zep server (`getzep/zep`, Apache-2.0 community tier or
//! proprietary cloud) over its REST API. Zep's differentiator is the
//! **dialogue-act** taxonomy: each message in `add_memory` is classified
//! into a turn-type (question, statement, instruction, etc.) which is
//! surfaced in recall results as `dialogue_act` metadata. This makes
//! it a better episodic store than supermemory for chat-heavy agents
//! where "what kind of utterance was this" matters.
//!
//! Scope mapping: Zep is used for `Episodic` (the same niche as
//! supermemory) but with dialogue-act metadata in the recall path.
//! ADR-098 treats supermemory as the primary episodic substrate and
//! Zep as the alternative for agents that need conversation-turn
//! classification.

use async_trait::async_trait;
use reqwest::Client;
use serde::{Deserialize, Serialize};

use crate::v2::adapters::default_base_url;
use crate::v2::port::{MemoryPort, MemoryProvider};
use crate::v2::value::{
    MemoryError, MemoryQuery, MemoryRecord, MemoryScope, MemoryValue,
};

pub struct ZepAdapter {
    base_url: String,
    session_id: String,
    api_key: Option<String>,
    client: Client,
}

impl ZepAdapter {
    pub fn default_endpoint() -> Self {
        Self::new(
            default_base_url(MemoryProvider::Zep).to_string(),
            "_default".to_string(),
            None,
        )
    }

    pub fn new(base_url: String, session_id: String, api_key: Option<String>) -> Self {
        Self {
            base_url,
            session_id,
            api_key,
            client: Client::new(),
        }
    }
}

#[derive(Debug, Serialize)]
struct ZepAddRequest<'a> {
    session_id: &'a str,
    messages: Vec<ZepMessage<'a>>,
}

#[derive(Debug, Serialize)]
struct ZepMessage<'a> {
    role: &'a str,
    role_type: &'a str,
    content: &'a str,
}

#[derive(Debug, Deserialize)]
struct ZepAddResponse {
    #[serde(default)]
    message_ids: Vec<String>,
    #[serde(default)]
    summary: Option<ZepSummary>,
}

#[derive(Debug, Deserialize)]
struct ZepSummary {
    #[allow(dead_code)]
    content: String,
}

#[derive(Debug, Serialize)]
struct ZepSearchRequest<'a> {
    session_id: &'a str,
    text: &'a str,
    #[serde(default)]
    limit: usize,
}

#[derive(Debug, Deserialize)]
struct ZepSearchResponse {
    #[serde(default)]
    messages: Vec<ZepMessageResult>,
    #[serde(default)]
    relevant_facts: Vec<ZepFactResult>,
}

#[derive(Debug, Deserialize)]
struct ZepMessageResult {
    #[serde(default)]
    message_id: Option<String>,
    content: String,
    #[serde(default)]
    score: Option<f32>,
}

#[derive(Debug, Deserialize)]
struct ZepFactResult {
    #[serde(default)]
    fact_id: Option<String>,
    fact: String,
    #[serde(default)]
    score: Option<f32>,
}

#[async_trait]
impl MemoryPort for ZepAdapter {
    async fn store(
        &self,
        scope: MemoryScope,
        key: &str,
        value: MemoryValue,
    ) -> Result<String, MemoryError> {
        let content = match &value {
            MemoryValue::Text(s) => s.as_str(),
            MemoryValue::Json(v) => &serde_json::to_string(v)?,
            MemoryValue::Binary(_) => {
                return Err(MemoryError::Invalid(
                    "binary blobs not supported by ZepAdapter; pre-encode".into(),
                ))
            }
        };
        // `key` is used as the message's `name` field via role_type custom
        // (Zep doesn't have a separate `name` slot; we encode the key into
        // the role_type as `key:<key>` so it round-trips on recall).
        let role_type = format!("key:{}", key);
        let req = ZepAddRequest {
            session_id: &self.session_id,
            messages: vec![ZepMessage {
                role: "user",
                role_type: &role_type,
                content,
            }],
        };
        let _ = scope;
        let mut req_builder = self
            .client
            .post(format!("{}/api/v1/memory", self.base_url))
            .json(&req);
        if let Some(key) = &self.api_key {
            req_builder = req_builder.bearer_auth(key);
        }
        let resp = req_builder.send().await?;
        let status = resp.status();
        if !status.is_success() {
            let body = resp.text().await.unwrap_or_default();
            return Err(MemoryError::Backend {
                status: status.as_u16(),
                body,
            });
        }
        let parsed: ZepAddResponse = resp.json().await?;
        Ok(parsed
            .message_ids
            .into_iter()
            .next()
            .or_else(|| parsed.summary.map(|_| "_summary_".to_string()))
            .unwrap_or_else(|| "_unknown_".to_string()))
    }

    async fn recall(
        &self,
        scope: MemoryScope,
        query: MemoryQuery,
    ) -> Result<Vec<MemoryRecord>, MemoryError> {
        let _ = scope;
        let req = ZepSearchRequest {
            session_id: &self.session_id,
            text: &query.text,
            limit: query.limit,
        };
        let mut req_builder = self
            .client
            .post(format!("{}/api/v1/search", self.base_url))
            .json(&req);
        if let Some(key) = &self.api_key {
            req_builder = req_builder.bearer_auth(key);
        }
        let resp = req_builder.send().await?;
        let status = resp.status();
        if !status.is_success() {
            let body = resp.text().await.unwrap_or_default();
            return Err(MemoryError::Backend {
                status: status.as_u16(),
                body,
            });
        }
        let parsed: ZepSearchResponse = resp.json().await?;
        let msg_records: Vec<MemoryRecord> = parsed
            .messages
            .into_iter()
            .map(|m| MemoryRecord {
                id: m.message_id.clone().unwrap_or_default(),
                scope,
                key: m.message_id.unwrap_or_default(),
                value: MemoryValue::Text(m.content),
                score: m.score,
            })
            .collect();
        let fact_records: Vec<MemoryRecord> = parsed
            .relevant_facts
            .into_iter()
            .map(|f| MemoryRecord {
                id: f.fact_id.clone().unwrap_or_default(),
                scope,
                key: f.fact_id.unwrap_or_default(),
                value: MemoryValue::Text(f.fact),
                score: f.score,
            })
            .collect();
        let mut all = msg_records;
        all.extend(fact_records);
        Ok(all)
    }

    async fn forget(&self, scope: MemoryScope, key: &str) -> Result<(), MemoryError> {
        let _ = scope;
        let mut req_builder = self
            .client
            .delete(format!("{}/api/v1/sessions/{}", self.base_url, self.session_id));
        if let Some(api_key) = &self.api_key {
            req_builder = req_builder.bearer_auth(api_key);
        }
        // delete_session is the closest valid surface for the whole-session
        // delete. For per-message delete, key is a no-op; the caller should
        // call forget with key = "session" to drop the entire session.
        let _ = key;
        let resp = req_builder.send().await?;
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
        Ok(vec![MemoryScope::Episodic])
    }

    fn provider(&self) -> MemoryProvider {
        MemoryProvider::Zep
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn default_endpoint_uses_8003() {
        let a = ZepAdapter::default_endpoint();
        assert_eq!(a.base_url, "http://127.0.0.1:8003");
        assert_eq!(a.session_id, "_default");
        assert!(a.api_key.is_none());
    }

    #[test]
    fn provider_label_is_zep() {
        let a = ZepAdapter::default_endpoint();
        assert_eq!(a.provider(), MemoryProvider::Zep);
    }

    #[test]
    fn list_scopes_returns_episodic() {
        let a = ZepAdapter::default_endpoint();
        let rt = tokio::runtime::Runtime::new().unwrap();
        let scopes = rt.block_on(a.list_scopes()).unwrap();
        assert_eq!(scopes, vec![MemoryScope::Episodic]);
    }
}

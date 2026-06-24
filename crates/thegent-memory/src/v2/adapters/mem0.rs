// SPDX-License-Identifier: MIT OR Apache-2.0
//! [`Mem0Adapter`] — fallback memory store.
//!
//! Talks to the Mem0 server (`mem0ai/mem0`, Apache-2.0) over its REST API
//! (default `http://127.0.0.1:8000`, surfaced by the `pheno-mem0` sidecar
//! in `pheno-forge-plugins`). The composite router invokes this adapter
//! only when a primary adapter returns [`MemoryError::Unavailable`], or
//! when the caller explicitly addresses `MemoryScope::Fallback`.

use async_trait::async_trait;
use reqwest::Client;
use serde::{Deserialize, Serialize};

use crate::v2::adapters::default_base_url;
use crate::v2::port::{MemoryPort, MemoryProvider};
use crate::v2::value::{
    MemoryError, MemoryQuery, MemoryRecord, MemoryScope, MemoryValue,
};

pub struct Mem0Adapter {
    base_url: String,
    client: Client,
}

impl Mem0Adapter {
    pub fn default_endpoint() -> Self {
        Self::new(default_base_url(MemoryProvider::Mem0).to_string())
    }

    pub fn new(base_url: String) -> Self {
        Self {
            base_url,
            client: Client::new(),
        }
    }
}

#[derive(Debug, Serialize)]
struct Mem0AddRequest<'a> {
    #[serde(rename = "user_id")]
    user_id: &'a str,
    messages: Vec<Mem0Message<'a>>,
}

#[derive(Debug, Serialize)]
struct Mem0Message<'a> {
    role: &'a str,
    content: &'a str,
}

#[derive(Debug, Deserialize)]
struct Mem0AddResponse {
    id: String,
}

#[derive(Debug, Serialize)]
struct Mem0SearchRequest<'a> {
    #[serde(rename = "user_id")]
    user_id: &'a str,
    query: &'a str,
    #[serde(rename = "limit")]
    limit: usize,
}

#[derive(Debug, Deserialize)]
struct Mem0SearchResponse {
    results: Vec<Mem0Result>,
}

#[derive(Debug, Deserialize)]
struct Mem0Result {
    id: String,
    memory: String,
    #[serde(default)]
    score: Option<f32>,
}

#[async_trait]
impl MemoryPort for Mem0Adapter {
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
                    "binary blobs not supported by Mem0Adapter; pre-encode".into(),
                ))
            }
        };
        let req = Mem0AddRequest {
            user_id: key,
            messages: vec![Mem0Message { role: "user", content }],
        };
        let _ = scope;
        let resp = self
            .client
            .post(format!("{}/v1/memories/", self.base_url))
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
        let parsed: Mem0AddResponse = resp.json().await?;
        Ok(parsed.id)
    }

    async fn recall(
        &self,
        scope: MemoryScope,
        query: MemoryQuery,
    ) -> Result<Vec<MemoryRecord>, MemoryError> {
        let _ = scope;
        let req = Mem0SearchRequest {
            user_id: "_any_",
            query: &query.text,
            limit: query.limit,
        };
        let resp = self
            .client
            .post(format!("{}/v1/memories/search", self.base_url))
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
        let parsed: Mem0SearchResponse = resp.json().await?;
        Ok(parsed
            .results
            .into_iter()
            .map(|r| MemoryRecord {
                id: r.id.clone(),
                scope,
                key: r.id,
                value: MemoryValue::Text(r.memory),
                score: r.score,
            })
            .collect())
    }

    async fn forget(&self, scope: MemoryScope, key: &str) -> Result<(), MemoryError> {
        let _ = scope;
        let resp = self
            .client
            .delete(format!("{}/v1/memories/{}", self.base_url, key))
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
        Ok(vec![MemoryScope::Fallback])
    }

    fn provider(&self) -> MemoryProvider {
        MemoryProvider::Mem0
    }
}
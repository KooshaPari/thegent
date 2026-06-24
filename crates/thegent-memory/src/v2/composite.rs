// SPDX-License-Identifier: MIT OR Apache-2.0
//! [`CompositeAdapter`] — dispatches memory ops to the right backend by
//! [`MemoryScope`].
//!
//! Routing (per ADR-096, locked 2026-06-23):
//! - `Episodic`         → supermemory  (smfs filesystem)
//! - `Identity`         → letta        (subconscious blocks)
//! - `ProjectKnowledge` → cognee       (knowledge graph)
//! - `Fallback`         → mem0
//!
//! Any backend that returns [`MemoryError::Unavailable`] triggers a single
//! fallback hop to the `Fallback` (mem0) port. Other errors propagate.

use std::sync::Arc;

use async_trait::async_trait;

use crate::v2::port::{MemoryPort, MemoryProvider};
use crate::v2::value::{
    MemoryError, MemoryQuery, MemoryRecord, MemoryScope, MemoryValue,
};

/// Routes by [`MemoryScope`] across four single-scope adapters. Construct
/// with [`CompositeAdapter::new`].
pub struct CompositeAdapter {
    supermemory: Arc<dyn MemoryPort>,
    letta: Arc<dyn MemoryPort>,
    cognee: Arc<dyn MemoryPort>,
    mem0: Arc<dyn MemoryPort>,
}

impl CompositeAdapter {
    pub fn new(
        supermemory: Arc<dyn MemoryPort>,
        letta: Arc<dyn MemoryPort>,
        cognee: Arc<dyn MemoryPort>,
        mem0: Arc<dyn MemoryPort>,
    ) -> Self {
        Self {
            supermemory,
            letta,
            cognee,
            mem0,
        }
    }

    /// Pick the adapter for a scope. Public so tests can verify routing
    /// without going through the trait methods.
    pub fn route(&self, scope: MemoryScope) -> &Arc<dyn MemoryPort> {
        match scope {
            MemoryScope::Episodic => &self.supermemory,
            MemoryScope::Identity => &self.letta,
            MemoryScope::ProjectKnowledge => &self.cognee,
            MemoryScope::Fallback => &self.mem0,
        }
    }
}

#[async_trait]
impl MemoryPort for CompositeAdapter {
    async fn store(
        &self,
        scope: MemoryScope,
        key: &str,
        value: MemoryValue,
    ) -> Result<String, MemoryError> {
        match self.route(scope).store(scope, key, value.clone()).await {
            Ok(id) => Ok(id),
            Err(MemoryError::Unavailable(reason)) => {
                tracing::warn!(
                    scope = scope.as_str(),
                    reason = %reason,
                    "primary unavailable; falling back to mem0",
                );
                self.mem0.store(scope, key, value).await
            }
            Err(e) => Err(e),
        }
    }

    async fn recall(
        &self,
        scope: MemoryScope,
        query: MemoryQuery,
    ) -> Result<Vec<MemoryRecord>, MemoryError> {
        match self.route(scope).recall(scope, query.clone()).await {
            Ok(recs) => Ok(recs),
            Err(MemoryError::Unavailable(reason)) => {
                tracing::warn!(
                    scope = scope.as_str(),
                    reason = %reason,
                    "primary unavailable; falling back to mem0",
                );
                self.mem0.recall(scope, query).await
            }
            Err(e) => Err(e),
        }
    }

    async fn forget(&self, scope: MemoryScope, key: &str) -> Result<(), MemoryError> {
        match self.route(scope).forget(scope, key).await {
            Ok(()) => Ok(()),
            Err(MemoryError::Unavailable(reason)) => {
                tracing::warn!(
                    scope = scope.as_str(),
                    reason = %reason,
                    "primary unavailable; falling back to mem0",
                );
                self.mem0.forget(scope, key).await
            }
            Err(e) => Err(e),
        }
    }

    async fn list_scopes(&self) -> Result<Vec<MemoryScope>, MemoryError> {
        Ok(vec![
            MemoryScope::Episodic,
            MemoryScope::Identity,
            MemoryScope::ProjectKnowledge,
            MemoryScope::Fallback,
        ])
    }

    fn provider(&self) -> MemoryProvider {
        MemoryProvider::Composite
    }
}
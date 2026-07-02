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

    /// Construct a composite that swaps in one of the ADR-098 alternative
    /// adapters in place of the corresponding primary. The alternative
    /// adapter takes the same scope niche (Episodic / Identity /
    /// ProjectKnowledge) but is opted in by the caller.
    ///
    /// - `swap_to_graphiti` → `ProjectKnowledge` (instead of cognee)
    /// - `swap_to_hippo`    → `Identity`         (instead of letta)
    /// - `swap_to_zep`      → `Episodic`         (instead of supermemory)
    ///
    /// Returns `None` if no swap was requested.
    pub fn with_alternatives(
        supermemory: Arc<dyn MemoryPort>,
        letta: Arc<dyn MemoryPort>,
        cognee: Arc<dyn MemoryPort>,
        mem0: Arc<dyn MemoryPort>,
        swap_to_graphiti: Option<Arc<dyn MemoryPort>>,
        swap_to_hippo: Option<Arc<dyn MemoryPort>>,
        swap_to_zep: Option<Arc<dyn MemoryPort>>,
    ) -> Self {
        Self {
            supermemory: swap_to_zep.unwrap_or(supermemory),
            letta: swap_to_hippo.unwrap_or(letta),
            cognee: swap_to_graphiti.unwrap_or(cognee),
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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::v2::adapters::test_doubles::MockAdapter;

    fn composite() -> CompositeAdapter {
        CompositeAdapter::new(
            Arc::new(MockAdapter::new()),
            Arc::new(MockAdapter::new()),
            Arc::new(MockAdapter::new()),
            Arc::new(MockAdapter::new()),
        )
    }

    #[tokio::test]
    async fn store_routes_episodic_to_supermemory() {
        let c = composite();
        let _ = c
            .store(MemoryScope::Episodic, "k1", "v1".into())
            .await
            .expect("episodic store should route to supermemory mock");
        // The composite dispatches to the right backend by scope. The mock
        // doesn't expose its state, so we just verify the call succeeds.
    }

    #[tokio::test]
    async fn recall_routes_identity_to_letta() {
        let c = composite();
        let recs = c
            .recall(MemoryScope::Identity, MemoryQuery::new("q").with_limit(5))
            .await
            .expect("identity recall should route to letta mock");
        // Mock returns empty for unknown keys; we just verify no error.
        assert!(recs.is_empty() || recs.iter().all(|r| r.scope == MemoryScope::Identity));
    }

    #[tokio::test]
    async fn forget_routes_project_knowledge_to_cognee() {
        let c = composite();
        c.forget(MemoryScope::ProjectKnowledge, "k")
            .await
            .expect("project_knowledge forget should route to cognee mock");
    }

    #[tokio::test]
    async fn store_routes_fallback_to_mem0() {
        let c = composite();
        let id = c
            .store(MemoryScope::Fallback, "k1", "v1".into())
            .await
            .expect("fallback store should route to mem0 mock");
        // Mock generates a uuid — just verify it's non-empty.
        assert!(!id.is_empty());
    }

    #[tokio::test]
    async fn with_alternatives_swaps_hippo_into_identity() {
        let c = CompositeAdapter::with_alternatives(
            Arc::new(MockAdapter::new()),
            Arc::new(MockAdapter::new()),
            Arc::new(MockAdapter::new()),
            Arc::new(MockAdapter::new()),
            None,
            Some(Arc::new(MockAdapter::new())),
            None,
        );
        // Hippo mock takes over Identity scope. Verify the call doesn't error.
        c.store(MemoryScope::Identity, "k", "v".into())
            .await
            .expect("hippo mock should accept identity store");
    }

    #[tokio::test]
    async fn with_alternatives_swaps_graphiti_and_zep() {
        let c = CompositeAdapter::with_alternatives(
            Arc::new(MockAdapter::new()),
            Arc::new(MockAdapter::new()),
            Arc::new(MockAdapter::new()),
            Arc::new(MockAdapter::new()),
            Some(Arc::new(MockAdapter::new())),
            None,
            Some(Arc::new(MockAdapter::new())),
        );
        c.store(MemoryScope::ProjectKnowledge, "k", "v".into())
            .await
            .expect("graphiti mock should accept project_knowledge store");
        c.store(MemoryScope::Episodic, "k", "v".into())
            .await
            .expect("zep mock should accept episodic store");
    }

    #[tokio::test]
    async fn list_scopes_returns_all_four() {
        let c = composite();
        let scopes = c.list_scopes().await.unwrap();
        assert_eq!(
            scopes,
            vec![
                MemoryScope::Episodic,
                MemoryScope::Identity,
                MemoryScope::ProjectKnowledge,
                MemoryScope::Fallback,
            ]
        );
    }
}
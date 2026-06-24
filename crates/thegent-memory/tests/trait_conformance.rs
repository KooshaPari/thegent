// SPDX-License-Identifier: MIT OR Apache-2.0
//! Trait conformance suite for [`MemoryPort`].
//!
//! Every adapter in the v2 module must satisfy these invariants. Adapters
//! that fail any case have a regression in their `MemoryPort`
//! implementation.
//!
//! Live integration with external sidecars (Supermemory, Letta, Cognee,
//! Mem0) is verified separately via `#[ignore]`'d tests that require a
//! running stack; here we exercise the in-process mock and the composite.

use std::sync::Arc;

use thegent_memory::v2::adapters::MockAdapter;
use thegent_memory::v2::{
    CogneeAdapter, CompositeAdapter, LettaAdapter, Mem0Adapter, MemoryPort, MemoryProvider,
    MemoryQuery, MemoryScope, SupermemoryAdapter,
};

#[tokio::test]
async fn mock_satisfies_trait_conformance() {
    let mock: Arc<dyn MemoryPort> = Arc::new(MockAdapter::new());
    assert_conformance(mock).await;
}

#[tokio::test]
async fn composite_with_mocks_round_trips() {
    let c = CompositeAdapter::new(
        Arc::new(MockAdapter::new()),
        Arc::new(MockAdapter::new()),
        Arc::new(MockAdapter::new()),
        Arc::new(MockAdapter::new()),
    );
    let id = c
        .store(MemoryScope::Episodic, "ck1", "hello".into())
        .await
        .unwrap();
    assert!(!id.is_empty());
    let recs = c
        .recall(MemoryScope::Episodic, MemoryQuery::new("hello"))
        .await
        .unwrap();
    assert_eq!(recs.len(), 1);
    c.forget(MemoryScope::Episodic, "ck1").await.unwrap();
}

#[tokio::test]
async fn composite_routes_each_scope_to_expected_provider() {
    let sm: Arc<dyn MemoryPort> = Arc::new(SupermemoryAdapter::default_endpoint());
    let lt: Arc<dyn MemoryPort> = Arc::new(LettaAdapter::default_endpoint());
    let cg: Arc<dyn MemoryPort> = Arc::new(CogneeAdapter::default_endpoint());
    let m0: Arc<dyn MemoryPort> = Arc::new(Mem0Adapter::default_endpoint());
    let c = CompositeAdapter::new(
        sm.clone(),
        lt.clone(),
        cg.clone(),
        m0.clone(),
    );

    assert_eq!(c.route(MemoryScope::Episodic).provider(), MemoryProvider::Supermemory);
    assert_eq!(c.route(MemoryScope::Identity).provider(), MemoryProvider::Letta);
    assert_eq!(c.route(MemoryScope::ProjectKnowledge).provider(), MemoryProvider::Cognee);
    assert_eq!(c.route(MemoryScope::Fallback).provider(), MemoryProvider::Mem0);
}

#[tokio::test]
async fn composite_provider_label_is_composite() {
    let c = CompositeAdapter::new(
        Arc::new(MockAdapter::new()),
        Arc::new(MockAdapter::new()),
        Arc::new(MockAdapter::new()),
        Arc::new(MockAdapter::new()),
    );
    assert_eq!(c.provider(), MemoryProvider::Composite);
}

#[tokio::test]
async fn each_adapter_reports_correct_scope_and_provider() {
    let sm: Arc<dyn MemoryPort> = Arc::new(SupermemoryAdapter::default_endpoint());
    let lt: Arc<dyn MemoryPort> = Arc::new(LettaAdapter::default_endpoint());
    let cg: Arc<dyn MemoryPort> = Arc::new(CogneeAdapter::default_endpoint());
    let m0: Arc<dyn MemoryPort> = Arc::new(Mem0Adapter::default_endpoint());

    assert_eq!(sm.list_scopes().await.unwrap(), vec![MemoryScope::Episodic]);
    assert_eq!(lt.list_scopes().await.unwrap(), vec![MemoryScope::Identity]);
    assert_eq!(cg.list_scopes().await.unwrap(), vec![MemoryScope::ProjectKnowledge]);
    assert_eq!(m0.list_scopes().await.unwrap(), vec![MemoryScope::Fallback]);

    assert_eq!(sm.provider(), MemoryProvider::Supermemory);
    assert_eq!(lt.provider(), MemoryProvider::Letta);
    assert_eq!(cg.provider(), MemoryProvider::Cognee);
    assert_eq!(m0.provider(), MemoryProvider::Mem0);
}

#[tokio::test]
async fn non_default_scope_is_rejected_by_single_scope_adapters() {
    let sm: Arc<dyn MemoryPort> = Arc::new(SupermemoryAdapter::default_endpoint());
    let r = sm.store(MemoryScope::Identity, "k", "v".into()).await;
    assert!(r.is_err());
}

#[tokio::test]
async fn provider_label_strings_are_stable() {
    assert_eq!(MemoryProvider::Supermemory.as_str(), "supermemory");
    assert_eq!(MemoryProvider::Letta.as_str(), "letta");
    assert_eq!(MemoryProvider::Cognee.as_str(), "cognee");
    assert_eq!(MemoryProvider::Mem0.as_str(), "mem0");
    assert_eq!(MemoryProvider::Composite.as_str(), "composite");

    assert_eq!(MemoryScope::Episodic.as_str(), "episodic");
    assert_eq!(MemoryScope::Identity.as_str(), "identity");
    assert_eq!(MemoryScope::ProjectKnowledge.as_str(), "project_knowledge");
    assert_eq!(MemoryScope::Fallback.as_str(), "fallback");
}

/// Trait conformance check: every implementation of `MemoryPort` must
/// satisfy these invariants.
async fn assert_conformance(p: Arc<dyn MemoryPort>) {
    // Provider label is set.
    let _ = p.provider();

    // list_scopes returns a Vec (possibly empty for a fresh adapter).
    let _scopes = p.list_scopes().await.expect("list_scopes");

    let key = format!("conformance-{}", uuid::Uuid::new_v4());
    let id = p
        .store(MemoryScope::Episodic, &key, "conformance-value".into())
        .await
        .expect("store");
    assert!(!id.is_empty());

    let recs = p
        .recall(
            MemoryScope::Episodic,
            MemoryQuery::new("conformance-value").with_limit(5),
        )
        .await
        .expect("recall");
    assert!(!recs.is_empty(), "recall should find the stored record");

    // forget is idempotent.
    p.forget(MemoryScope::Episodic, &key).await.expect("forget");
    p.forget(MemoryScope::Episodic, &key).await.expect("forget idempotent");
}
// SPDX-License-Identifier: MIT OR Apache-2.0
//! Adapters that implement [`MemoryPort`] over external memory engines.
//!
//! Each adapter is single-scope (its `list_scopes` returns exactly one
//! [`MemoryScope`]) and is safe to compose via [`crate::v2::CompositeAdapter`].

pub mod cognee;
pub mod graphiti;
pub mod hippo;
pub mod letta;
pub mod mem0;
pub mod supermemory;
pub mod test_doubles;
pub mod zep;

pub use cognee::CogneeAdapter;
pub use graphiti::GraphitiAdapter;
pub use hippo::HippoAdapter;
pub use letta::LettaAdapter;
pub use mem0::Mem0Adapter;
pub use supermemory::SupermemoryAdapter;
pub use test_doubles::MockAdapter;
pub use zep::ZepAdapter;

/// Default base URL for a given provider — used by `*::default_endpoint()`
/// constructors so tests can wire composites without reading env vars.
pub fn default_base_url(provider: crate::v2::MemoryProvider) -> &'static str {
    match provider {
        crate::v2::MemoryProvider::Supermemory => "http://127.0.0.1:3030",
        crate::v2::MemoryProvider::Letta => "http://127.0.0.1:8283",
        crate::v2::MemoryProvider::Cognee => "stdio://cognee-mcp",
        crate::v2::MemoryProvider::Mem0 => "http://127.0.0.1:8000",
        crate::v2::MemoryProvider::Graphiti => "http://127.0.0.1:8001",
        crate::v2::MemoryProvider::Hippo => "http://127.0.0.1:8002",
        crate::v2::MemoryProvider::Zep => "http://127.0.0.1:8003",
        crate::v2::MemoryProvider::Composite => panic!("Composite has no base URL"),
    }
}
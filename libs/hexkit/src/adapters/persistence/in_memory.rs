//! In-Memory Repository

use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;
use crate::domain::Entity;

/// Simple in-memory repository implementation
pub struct InMemoryRepository<T: Clone> {
    store: Arc<RwLock<HashMap<String, T>>>,
}

impl<T: Clone> InMemoryRepository<T> {
    pub fn new() -> Self {
        Self {
            store: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    pub async fn save(&self, key: String, entity: T) {
        let mut store = self.store.write().await;
        store.insert(key, entity);
    }

    pub async fn find_by_id(&self, key: &str) -> Option<T> {
        let store = self.store.read().await;
        store.get(key).cloned()
    }

    pub async fn find_all(&self) -> Vec<T> {
        let store = self.store.read().await;
        store.values().cloned().collect()
    }

    pub async fn delete(&self, key: &str) {
        let mut store = self.store.write().await;
        store.remove(key);
    }
}

impl<T: Clone> Default for InMemoryRepository<T> {
    fn default() -> Self {
        Self::new()
    }
}

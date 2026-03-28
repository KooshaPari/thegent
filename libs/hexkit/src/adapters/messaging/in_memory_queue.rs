//! In-Memory Message Queue

use std::collections::VecDeque;
use std::sync::Arc;
use tokio::sync::RwLock;

/// Simple in-memory message queue
pub struct InMemoryQueue<T> {
    queue: Arc<RwLock<VecDeque<T>>>,
}

impl<T> InMemoryQueue<T> {
    pub fn new() -> Self {
        Self {
            queue: Arc::new(RwLock::new(VecDeque::new())),
        }
    }

    pub async fn enqueue(&self, item: T) {
        let mut queue = self.queue.write().await;
        queue.push_back(item);
    }

    pub async fn dequeue(&self) -> Option<T> {
        let mut queue = self.queue.write().await;
        queue.pop_front()
    }

    pub async fn len(&self) -> usize {
        let queue = self.queue.read().await;
        queue.len()
    }

    pub async fn is_empty(&self) -> bool {
        let queue = self.queue.read().await;
        queue.is_empty()
    }
}

impl<T> Default for InMemoryQueue<T> {
    fn default() -> Self {
        Self::new()
    }
}

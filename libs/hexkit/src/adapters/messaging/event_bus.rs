//! Event Bus Adapter

use tokio::sync::broadcast;
use crate::domain::DomainEvent;

/// Simple in-memory event bus
pub struct EventBus<E: DomainEvent + Clone> {
    sender: broadcast::Sender<E>,
}

impl<E: DomainEvent + Clone> EventBus<E> {
    pub fn new(capacity: usize) -> Self {
        let (sender, _) = broadcast::channel(capacity);
        Self { sender }
    }

    pub fn subscribe(&self) -> broadcast::Receiver<E> {
        self.sender.subscribe()
    }

    pub async fn publish(&self, event: E) {
        let _ = self.sender.send(event);
    }
}

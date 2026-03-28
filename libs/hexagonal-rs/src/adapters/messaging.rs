//! Messaging Adapter
//!
//! This adapter provides messaging capabilities for domain events.

use async_trait::async_trait;
use std::collections::HashMap;
use std::sync::{Arc, RwLock};
use crate::HexagonalResult;
use crate::domain::DomainEvent;
use crate::ports::output::{MessageBusPort, OutputPort};

/// In-memory message bus implementation.
pub struct InMemoryMessageBus<E>
where
    E: DomainEvent + 'static,
{
    subscribers: RwLock<HashMap<String, Vec<Arc<dyn MessageHandler<E>>>>>,
}

impl<E> InMemoryMessageBus<E>
where
    E: DomainEvent + 'static,
{
    pub fn new() -> Self {
        Self {
            subscribers: RwLock::new(HashMap::new()),
        }
    }
}

impl<E> Default for InMemoryMessageBus<E>
where
    E: DomainEvent + 'static,
{
    fn default() -> Self {
        Self::new()
    }
}

impl<E> OutputPort for InMemoryMessageBus<E>
where
    E: DomainEvent + 'static,
{}

#[async_trait]
impl<E> MessageBusPort<E> for InMemoryMessageBus<E>
where
    E: DomainEvent + 'static,
{
    async fn publish(&self, topic: &str, event: E) -> HexagonalResult<()> {
        let handlers = {
            let subscribers = self
                .subscribers
                .read()
                .map_err(|_| crate::HexagonalError::Adapter("message bus lock poisoned".to_string()))?;
            subscribers.get(topic).cloned().unwrap_or_default()
        };

        for handler in handlers {
            handler.handle(&event).await?;
        }
        Ok(())
    }

    async fn publish_batch(&self, topic: &str, events: Vec<E>) -> HexagonalResult<()> {
        for event in events {
            self.publish(topic, event).await?;
        }
        Ok(())
    }
}

impl<E> InMemoryMessageBus<E>
where
    E: DomainEvent + 'static,
{
    pub fn subscribe<H: MessageHandler<E> + 'static>(&self, topic: String, handler: Arc<H>) -> HexagonalResult<()> {
        let mut subscribers = self
            .subscribers
            .write()
            .map_err(|_| crate::HexagonalError::Adapter("message bus lock poisoned".to_string()))?;
        subscribers
            .entry(topic)
            .or_insert_with(Vec::new)
            .push(handler);
        Ok(())
    }
}

/// Trait for message handlers.
#[async_trait]
pub trait MessageHandler<E>: Send + Sync {
    async fn handle(&self, event: &E) -> HexagonalResult<()>;
}

/// Event publisher helper.
pub struct EventPublisher<E>
where
    E: DomainEvent + 'static,
{
    bus: Arc<InMemoryMessageBus<E>>,
    topic: String,
}

impl<E> EventPublisher<E>
where
    E: DomainEvent + 'static,
{
    pub fn new(bus: Arc<InMemoryMessageBus<E>>, topic: impl Into<String>) -> Self {
        Self {
            bus,
            topic: topic.into(),
        }
    }

    pub async fn publish(&self, event: E) -> HexagonalResult<()> {
        self.bus.publish(&self.topic, event).await
    }
}

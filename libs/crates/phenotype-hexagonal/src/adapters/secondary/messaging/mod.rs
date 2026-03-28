//! Messaging Adapters
//! 
//! Message queue and event bus implementations.

/// Message error type
#[derive(Debug)]
pub struct MessagingError {
    pub code: String,
    pub message: String,
}

impl MessagingError {
    pub fn publish_failed(topic: impl Into<String>, msg: impl Into<String>) -> Self {
        Self {
            code: "PUBLISH_FAILED".into(),
            message: format!("Failed to publish to {}: {}", topic.into(), msg.into()),
        }
    }
    
    pub fn connection_error(msg: impl Into<String>) -> Self {
        Self {
            code: "CONNECTION_ERROR".into(),
            message: msg.into(),
        }
    }
}

impl std::fmt::Display for MessagingError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "[{}] {}", self.code, self.message)
    }
}

impl std::error::Error for MessagingError {}

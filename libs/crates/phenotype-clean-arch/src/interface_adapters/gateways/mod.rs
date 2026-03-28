//! Gateways
//! 
//! Interfaces for external resources (database, external services).

use async_trait::async_trait;

/// Repository gateway trait
#[async_trait]
pub trait Repository<E, Id>: Send + Sync {
    async fn save(&self, entity: E) -> Result<(), GatewayError>;
    async fn find_by_id(&self, id: Id) -> Result<Option<E>, GatewayError>;
    async fn delete(&self, id: Id) -> Result<(), GatewayError>;
}

/// External service gateway trait
#[async_trait]
pub trait ExternalService<T, R>: Send + Sync {
    async fn call(&self, request: T) -> Result<R, GatewayError>;
}

/// Gateway error
#[derive(Debug)]
pub struct GatewayError {
    pub code: String,
    pub message: String,
}

impl GatewayError {
    pub fn new(code: impl Into<String>, message: impl Into<String>) -> Self {
        Self {
            code: code.into(),
            message: message.into(),
        }
    }
}

impl std::fmt::Display for GatewayError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "[{}] {}", self.code, self.message)
    }
}

impl std::error::Error for GatewayError {}

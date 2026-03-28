//! Use Cases
//! 
//! Application business rules that define how entities interact.

use async_trait::async_trait;

/// Use case trait
pub trait UseCase<I, O>: Send + Sync {
    fn execute(&self, input: I) -> O;
}

/// Async use case trait
#[async_trait]
pub trait AsyncUseCase<I, O>: Send + Sync {
    async fn execute(&self, input: I) -> Result<O, UseCaseError>;
}

/// Use case error
#[derive(Debug)]
pub struct UseCaseError {
    pub code: String,
    pub message: String,
}

impl UseCaseError {
    pub fn new(code: impl Into<String>, message: impl Into<String>) -> Self {
        Self {
            code: code.into(),
            message: message.into(),
        }
    }
}

impl std::fmt::Display for UseCaseError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "[{}] {}", self.code, self.message)
    }
}

impl std::error::Error for UseCaseError {}

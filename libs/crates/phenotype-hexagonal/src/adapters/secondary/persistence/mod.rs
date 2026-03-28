//! Persistence Adapters
//! 
//! Database and storage implementations.

/// Repository error type
#[derive(Debug)]
pub struct RepositoryError {
    pub code: String,
    pub message: String,
}

impl RepositoryError {
    pub fn not_found(id: impl Into<String>) -> Self {
        Self {
            code: "NOT_FOUND".into(),
            message: format!("Entity not found: {}", id.into()),
        }
    }
    
    pub fn already_exists(id: impl Into<String>) -> Self {
        Self {
            code: "ALREADY_EXISTS".into(),
            message: format!("Entity already exists: {}", id.into()),
        }
    }
    
    pub fn constraint_violation(msg: impl Into<String>) -> Self {
        Self {
            code: "CONSTRAINT_VIOLATION".into(),
            message: msg.into(),
        }
    }
}

impl std::fmt::Display for RepositoryError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "[{}] {}", self.code, self.message)
    }
}

impl std::error::Error for RepositoryError {}

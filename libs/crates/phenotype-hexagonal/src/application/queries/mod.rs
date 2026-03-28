//! Application Queries
//! 
//! Queries represent operations that read state without modification.

/// Marker trait for queries
pub trait Query<T>: Send + Sync {
    // Queries carry the criteria for finding data
}

/// Query result type
pub type QueryResult<T> = Result<T, QueryError>;

/// Query error type
#[derive(Debug)]
pub struct QueryError {
    pub code: String,
    pub message: String,
}

impl QueryError {
    pub fn new(code: impl Into<String>, message: impl Into<String>) -> Self {
        Self {
            code: code.into(),
            message: message.into(),
        }
    }
}

impl std::fmt::Display for QueryError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "[{}] {}", self.code, self.message)
    }
}

impl std::error::Error for QueryError {}

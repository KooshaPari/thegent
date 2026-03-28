//! Cache Adapters
//! 
//! Caching implementations.

/// Cache error type
#[derive(Debug)]
pub struct CacheError {
    pub code: String,
    pub message: String,
}

impl CacheError {
    pub fn key_not_found(key: impl Into<String>) -> Self {
        Self {
            code: "KEY_NOT_FOUND".into(),
            message: format!("Cache key not found: {}", key.into()),
        }
    }
    
    pub fn serialization_error(msg: impl Into<String>) -> Self {
        Self {
            code: "SERIALIZATION_ERROR".into(),
            message: msg.into(),
        }
    }
}

impl std::fmt::Display for CacheError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "[{}] {}", self.code, self.message)
    }
}

impl std::error::Error for CacheError {}

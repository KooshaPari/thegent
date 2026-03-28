//! Database Frameworks & Drivers
//! 
//! Database-specific implementations.

/// Database configuration
#[derive(Debug, Clone)]
pub struct DatabaseConfig {
    pub url: String,
    pub max_connections: u32,
    pub timeout_seconds: u64,
}

impl Default for DatabaseConfig {
    fn default() -> Self {
        Self {
            url: "postgres://localhost/app".into(),
            max_connections: 10,
            timeout_seconds: 30,
        }
    }
}

/// Database connection pool trait
pub trait ConnectionPool: Send + Sync {
    fn acquire(&self) -> Result<Box<dyn PooledConnection>, DatabaseError>;
}

/// Pooled connection
pub trait PooledConnection: Send + Sync {
    fn execute(&self, sql: &str) -> Result<(), DatabaseError>;
}

/// Database error
#[derive(Debug)]
pub struct DatabaseError {
    pub code: String,
    pub message: String,
}

impl DatabaseError {
    pub fn connection_failed(msg: impl Into<String>) -> Self {
        Self {
            code: "CONNECTION_FAILED".into(),
            message: msg.into(),
        }
    }
    
    pub fn query_failed(msg: impl Into<String>) -> Self {
        Self {
            code: "QUERY_FAILED".into(),
            message: msg.into(),
        }
    }
}

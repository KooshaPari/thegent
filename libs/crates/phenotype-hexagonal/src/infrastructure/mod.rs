//! Infrastructure layer - Configuration and dependency injection
//! 
//! This module contains:
//! - Configuration structures
//! - Dependency injection setup
//! - Framework integration

/// Application configuration
#[derive(Debug, Clone)]
pub struct AppConfig {
    pub database_url: String,
    pub cache_url: Option<String>,
    pub messaging_url: Option<String>,
    pub log_level: String,
}

impl Default for AppConfig {
    fn default() -> Self {
        Self {
            database_url: "postgres://localhost/app".into(),
            cache_url: None,
            messaging_url: None,
            log_level: "info".into(),
        }
    }
}

/// Dependency injection container
pub struct Container {
    config: AppConfig,
}

impl Container {
    pub fn new(config: AppConfig) -> Self {
        Self { config }
    }
    
    pub fn config(&self) -> &AppConfig {
        &self.config
    }
}

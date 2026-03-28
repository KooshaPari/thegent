//! External Services
//! 
//! External service implementations.

/// External API client
pub trait ExternalClient: Send + Sync {
    fn call(&self, request: ExternalRequest) -> Result<ExternalResponse, ExternalError>;
}

/// External request
#[derive(Debug, Clone)]
pub struct ExternalRequest {
    pub url: String,
    pub method: String,
    pub headers: std::collections::HashMap<String, String>,
    pub body: Option<Vec<u8>>,
}

/// External response
#[derive(Debug)]
pub struct ExternalResponse {
    pub status: u16,
    pub headers: std::collections::HashMap<String, String>,
    pub body: Vec<u8>,
}

/// External error
#[derive(Debug)]
pub struct ExternalError {
    pub code: String,
    pub message: String,
}

impl ExternalError {
    pub fn timeout() -> Self {
        Self {
            code: "TIMEOUT".into(),
            message: "Request timed out".into(),
        }
    }
    
    pub fn connection_refused() -> Self {
        Self {
            code: "CONNECTION_REFUSED".into(),
            message: "Connection refused".into(),
        }
    }
}

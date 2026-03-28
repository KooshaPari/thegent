//! Web Frameworks & Drivers
//! 
//! Web framework implementations.

/// HTTP server configuration
#[derive(Debug, Clone)]
pub struct HttpConfig {
    pub host: String,
    pub port: u16,
    pub workers: usize,
}

impl Default for HttpConfig {
    fn default() -> Self {
        Self {
            host: "0.0.0.0".into(),
            port: 8080,
            workers: 4,
        }
    }
}

/// HTTP middleware trait
pub trait Middleware: Send + Sync {
    fn process(&self, request: HttpRequest) -> HttpResponse;
}

/// HTTP request
#[derive(Debug)]
pub struct HttpRequest {
    pub method: String,
    pub path: String,
    pub headers: std::collections::HashMap<String, String>,
    pub body: Vec<u8>,
}

/// HTTP response
#[derive(Debug)]
pub struct HttpResponse {
    pub status: u16,
    pub headers: std::collections::HashMap<String, String>,
    pub body: Vec<u8>,
}

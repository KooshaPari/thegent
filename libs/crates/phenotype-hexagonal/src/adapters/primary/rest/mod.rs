//! REST Adapter
//! 
//! HTTP/REST API adapter implementation.

/// REST controller base
pub trait RestController: Send + Sync {
    // Implement HTTP endpoints
}

/// Request wrapper
#[derive(Debug)]
pub struct HttpRequest {
    pub method: String,
    pub path: String,
    pub headers: std::collections::HashMap<String, String>,
    pub body: Option<Vec<u8>>,
}

/// Response wrapper
#[derive(Debug)]
pub struct HttpResponse {
    pub status: u16,
    pub headers: std::collections::HashMap<String, String>,
    pub body: Option<Vec<u8>>,
}

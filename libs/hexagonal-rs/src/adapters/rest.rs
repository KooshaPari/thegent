//! REST API Adapter
//!
//! This adapter provides a REST API interface for the application.

use async_trait::async_trait;
use serde::Serialize;
use std::sync::Arc;
use crate::application::handler::RequestHandler;

/// REST route definition
#[derive(Debug, Clone)]
pub struct Route {
    pub method: HttpMethod,
    pub path: String,
    pub handler: String,
}

/// HTTP methods
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum HttpMethod {
    Get,
    Post,
    Put,
    Patch,
    Delete,
    Options,
}

/// REST request
#[derive(Debug, Clone)]
pub struct RestRequest {
    pub method: HttpMethod,
    pub path: String,
    pub headers: std::collections::HashMap<String, String>,
    pub body: Option<serde_json::Value>,
    pub query_params: std::collections::HashMap<String, String>,
    pub path_params: std::collections::HashMap<String, String>,
}

/// REST response
#[derive(Debug, Clone, Serialize)]
pub struct RestResponse<T: Serialize> {
    pub status: u16,
    pub headers: std::collections::HashMap<String, String>,
    pub body: Option<T>,
    pub error: Option<RestError>,
}

impl<T: Serialize> RestResponse<T> {
    pub fn success(status: u16, body: T) -> Self {
        Self {
            status,
            headers: std::collections::HashMap::new(),
            body: Some(body),
            error: None,
        }
    }
    
    pub fn error(status: u16, error: RestError) -> Self {
        Self {
            status,
            headers: std::collections::HashMap::new(),
            body: None,
            error: Some(error),
        }
    }
}

/// REST error
#[derive(Debug, Clone, Serialize)]
pub struct RestError {
    pub code: String,
    pub message: String,
    pub details: Option<serde_json::Value>,
}

impl RestError {
    pub fn new(code: impl Into<String>, message: impl Into<String>) -> Self {
        Self {
            code: code.into(),
            message: message.into(),
            details: None,
        }
    }
    
    pub fn with_details(mut self, details: serde_json::Value) -> Self {
        self.details = Some(details);
        self
    }
}

/// REST controller trait
#[async_trait]
pub trait RestController: Send + Sync {
    fn routes(&self) -> Vec<Route>;

    async fn handle(&self, request: RestRequest) -> serde_json::Value;
}

/// REST adapter that implements input port
pub struct RestAdapter<H, R>
where
    H: RequestHandler<RestRequest, R>,
    R: Serialize,
{
    handler: Arc<H>,
    _phantom: std::marker::PhantomData<R>,
}

impl<H, R> RestAdapter<H, R>
where
    H: RequestHandler<RestRequest, R> + 'static,
    R: Serialize,
{
    pub fn new(handler: Arc<H>) -> Self {
        Self {
            handler,
            _phantom: std::marker::PhantomData,
        }
    }
}

impl<H, R> crate::ports::InputPort for RestAdapter<H, R>
where
    H: RequestHandler<RestRequest, R>,
    R: Serialize + Send + Sync,
{}

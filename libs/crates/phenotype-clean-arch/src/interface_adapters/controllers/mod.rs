//! Controllers
//!
//! Receive external input and convert it for use by the application.

use crate::frameworks_drivers::web::{HttpRequest, HttpResponse};

/// Type alias for request - using HttpRequest from frameworks_drivers
pub type Request = HttpRequest;

/// Type alias for response - using HttpResponse from frameworks_drivers
pub type Response = HttpResponse;

/// HTTP controller trait
pub trait Controller: Send + Sync {
    fn handle(&self, request: Request) -> Response;
}

/// CLI controller trait
pub trait CliController: Send + Sync {
    fn execute(&self, args: Vec<String>) -> Result<(), ControllerError>;
}

/// Controller error
#[derive(Debug)]
pub struct ControllerError {
    pub message: String,
}

impl ControllerError {
    pub fn new(msg: impl Into<String>) -> Self {
        Self { message: msg.into() }
    }
}

impl std::fmt::Display for ControllerError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.message)
    }
}

impl std::error::Error for ControllerError {}

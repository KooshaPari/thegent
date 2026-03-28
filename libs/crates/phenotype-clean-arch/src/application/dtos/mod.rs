//! Data Transfer Objects
//! 
//! Objects used to transfer data between layers.

use serde::{Serialize, Deserialize};

/// Request DTO marker
pub trait Request: Send + Sync + for<'de> Deserialize<'de> {}

/// Response DTO marker
pub trait Response: Send + Sync + Serialize {}

/// Generic request/response types
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EmptyRequest;

impl Request for EmptyRequest {}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EmptyResponse;

impl Response for EmptyResponse {}

/// Result type for use cases
pub type UseCaseResult<T> = Result<T, super::UseCaseError>;

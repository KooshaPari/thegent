//! Data Transfer Objects
//!
//! DTOs are simple data structures used to transfer data between layers.
//! They should not contain any business logic.

use serde::{Serialize, Deserialize};

/// Generic DTO wrapper
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DTO<T> {
    pub data: T,
    pub meta: DtoMeta,
}

impl<T> DTO<T> {
    pub fn new(data: T) -> Self {
        Self {
            data,
            meta: DtoMeta::default(),
        }
    }
    
    pub fn with_meta(data: T, meta: DtoMeta) -> Self {
        Self { data, meta }
    }
}

impl<T> From<T> for DTO<T> {
    fn from(value: T) -> Self {
        DTO::new(value)
    }
}

/// Metadata for DTOs
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct DtoMeta {
    pub version: Option<String>,
    pub timestamp: Option<chrono::DateTime<chrono::Utc>>,
    pub request_id: Option<String>,
    pub pagination: Option<PaginationMeta>,
}

impl DtoMeta {
    pub fn with_version(version: impl Into<String>) -> Self {
        Self {
            version: Some(version.into()),
            ..Default::default()
        }
    }
    
    pub fn with_request_id(id: impl Into<String>) -> Self {
        Self {
            request_id: Some(id.into()),
            ..Default::default()
        }
    }
}

/// Pagination metadata
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PaginationMeta {
    pub page: usize,
    pub page_size: usize,
    pub total: u64,
    pub total_pages: usize,
}

impl PaginationMeta {
    pub fn new(page: usize, page_size: usize, total: u64) -> Self {
        Self {
            total_pages: ((total as f64) / (page_size as f64)).ceil() as usize,
            page,
            page_size,
            total,
        }
    }
}

/// Command DTO - for write operations
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Command {
    pub command_type: String,
    pub payload: serde_json::Value,
    pub metadata: std::collections::HashMap<String, String>,
}

impl Command {
    pub fn new(command_type: impl Into<String>, payload: serde_json::Value) -> Self {
        Self {
            command_type: command_type.into(),
            payload,
            metadata: std::collections::HashMap::new(),
        }
    }
    
    pub fn with_metadata(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.metadata.insert(key.into(), value.into());
        self
    }
}

/// Query DTO - for read operations
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Query {
    pub query_type: String,
    pub filters: Vec<QueryFilter>,
    pub pagination: Option<PaginationInput>,
}

impl Query {
    pub fn new(query_type: impl Into<String>) -> Self {
        Self {
            query_type: query_type.into(),
            filters: Vec::new(),
            pagination: None,
        }
    }
    
    pub fn with_filter(mut self, filter: QueryFilter) -> Self {
        self.filters.push(filter);
        self
    }
}

/// Query filter
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QueryFilter {
    pub field: String,
    pub operator: FilterOperator,
    pub value: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum FilterOperator {
    Eq,
    Ne,
    Gt,
    Lt,
    Gte,
    Lte,
    Contains,
    StartsWith,
    In,
}

/// Pagination input
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PaginationInput {
    pub page: usize,
    pub page_size: usize,
}

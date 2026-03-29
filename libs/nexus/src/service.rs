//! Service and endpoint definitions

/// A service endpoint
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct Endpoint {
    /// The address of the endpoint (e.g., "localhost:8080")
    pub addr: String,
    /// Optional metadata for the endpoint
    pub metadata: Option<String>,
}

impl Endpoint {
    /// Create a new endpoint
    pub fn new(addr: impl Into<String>) -> Self {
        Self {
            addr: addr.into(),
            metadata: None,
        }
    }

    /// Create an endpoint with metadata
    pub fn with_metadata(mut self, metadata: impl Into<String>) -> Self {
        self.metadata = Some(metadata.into());
        self
    }
}

/// A registered service
#[derive(Debug, Clone)]
pub struct Service {
    /// The name of the service
    pub name: String,
    /// The endpoint for the service
    pub endpoint: Endpoint,
    /// Optional tags for the service
    pub tags: Vec<String>,
}

impl Service {
    /// Create a new service
    pub fn new(name: impl Into<String>, endpoint: Endpoint) -> Self {
        Self {
            name: name.into(),
            endpoint,
            tags: Vec::new(),
        }
    }

    /// Create a service with tags
    pub fn with_tags(mut self, tags: Vec<String>) -> Self {
        self.tags = tags;
        self
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_endpoint_creation() {
        let endpoint = Endpoint::new("localhost:8080");
        assert_eq!(endpoint.addr, "localhost:8080");
    }

    #[test]
    fn test_service_creation() {
        let service = Service::new("user-svc", Endpoint::new("localhost:8080"));
        assert_eq!(service.name, "user-svc");
    }
}

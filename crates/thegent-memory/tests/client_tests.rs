//! Integration tests for SupermemoryClient

use thegent_memory::*;

#[tokio::test]
async fn test_client_initialization() {
    let auth = AuthMethod::ApiKey("test_key".to_string());
    let client = SupermemoryClient::new(
        "https://api.example.com".to_string(),
        "project-1".to_string(),
        auth,
    )
    .await
    .expect("Client creation failed");

    assert_eq!(client.project_id(), "project-1");
    assert_eq!(client.base_url(), "https://api.example.com");
}

#[tokio::test]
async fn test_invalid_project_id_rejects_empty() {
    let auth = AuthMethod::ApiKey("test_key".to_string());
    let result = SupermemoryClient::new(
        "https://api.example.com".to_string(),
        "".to_string(),
        auth,
    )
    .await;

    assert!(result.is_err());
    match result {
        Err(Error::InvalidProject(_)) => {},
        _ => panic!("Expected InvalidProject error"),
    }
}

#[tokio::test]
async fn test_api_key_auth_header() {
    let auth = AuthMethod::ApiKey("secret_key".to_string());
    let header = auth.to_header_value();
    assert_eq!(header, "Bearer secret_key");
}

#[tokio::test]
async fn test_oauth_auth_header() {
    let auth = AuthMethod::OAuth2("oauth_token".to_string());
    let header = auth.to_header_value();
    assert_eq!(header, "Bearer oauth_token");
}

#[test]
fn test_knowledge_node_creation() {
    let node = KnowledgeNode::new("node1".to_string(), "TestEntity".to_string());
    assert_eq!(node.id, "node1");
    assert_eq!(node.entity, "TestEntity");
    assert!(node.relationships.is_empty());
    assert!(node.metadata.is_empty());
}

#[test]
fn test_relationship_creation() {
    let rel = Relationship::new(
        "depends_on".to_string(),
        "other_entity".to_string(),
    );
    assert_eq!(rel.relationship_type, "depends_on");
    assert_eq!(rel.target, "other_entity");
}

#[test]
fn test_query_result_pagination() {
    let result = QueryResult {
        nodes: vec![],
        total: 100,
        offset: 0,
        limit: 10,
    };

    assert!(result.has_more());
    assert_eq!(result.next_offset(), 10);
}

#[test]
fn test_query_result_last_page() {
    let result = QueryResult {
        nodes: vec![],
        total: 100,
        offset: 90,
        limit: 10,
    };

    assert!(!result.has_more());
}

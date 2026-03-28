//! Policy Client - HTTP client for remote policy evaluation.

use std::collections::HashMap;
use std::sync::Arc;

use crate::domain::{EvaluationResult, PolicyContext, PolicyResult};

/// Policy client - Client for remote policy evaluation.
///
/// This client can be used to evaluate policies on a remote
/// policy service (e.g., OPA, Open Policy Agent).
pub struct PolicyClient {
    /// Base URL for the policy service
    base_url: String,
    /// HTTP client
    client: reqwest::Client,
    /// Default timeout
    timeout: std::time::Duration,
}

impl PolicyClient {
    /// Create a new policy client.
    pub fn new(base_url: impl Into<String>) -> Self {
        Self {
            base_url: base_url.into().trim_end_matches('/').to_string(),
            client: reqwest::Client::new(),
            timeout: std::time::Duration::from_secs(30),
        }
    }

    /// Create with a custom HTTP client.
    pub fn with_client(base_url: impl Into<String>, client: reqwest::Client) -> Self {
        Self {
            base_url: base_url.into().trim_end_matches('/').to_string(),
            client,
            timeout: std::time::Duration::from_secs(30),
        }
    }

    /// Set the request timeout.
    pub fn with_timeout(mut self, timeout: std::time::Duration) -> Self {
        self.timeout = timeout;
        self
    }

    /// Evaluate a request against all policies.
    pub async fn evaluate(
        &self,
        context: &dyn PolicyContext,
    ) -> PolicyResult<EvaluationResult> {
        let url = format!("{}/v1/data/allow", self.base_url);
        
        let request = crate::adapters::PolicyServiceRequest {
            input: context.all(),
        };

        let response = self.client
            .post(&url)
            .json(&request)
            .timeout(self.timeout)
            .send()
            .await
            .map_err(|e| crate::domain::PolicyError::EvaluationError { 
                message: format!("Request failed: {}", e) 
            })?;

        if !response.status().is_success() {
            return Err(crate::domain::PolicyError::EvaluationError { 
                message: format!("Server returned: {}", response.status()) 
            });
        }

        let body = response.json::<crate::adapters::PolicyServiceResponse>()
            .await
            .map_err(|e| crate::domain::PolicyError::EvaluationError { 
                message: format!("Failed to parse response: {}", e) 
            })?;

        Ok(body.into())
    }

    /// Check if a request is allowed.
    pub async fn is_allowed(
        &self,
        context: &dyn PolicyContext,
    ) -> PolicyResult<bool> {
        Ok(self.evaluate(context).await?.is_allowed())
    }
}

/// Request body for policy service.
#[derive(serde::Serialize)]
pub struct PolicyServiceRequest {
    pub input: HashMap<String, String>,
}

/// Response from policy service.
#[derive(serde::Deserialize)]
pub struct PolicyServiceResponse {
    pub result: PolicyServiceResult,
}

/// Result from policy service.
#[derive(serde::Deserialize)]
pub struct PolicyServiceResult {
    #[serde(rename = "allow")]
    pub allow: Option<bool>,
}

impl From<PolicyServiceResponse> for EvaluationResult {
    fn from(response: PolicyServiceResponse) -> Self {
        match response.result.allow {
            Some(true) => EvaluationResult::allow("remote-service"),
            Some(false) => EvaluationResult::deny("remote-service"),
            None => EvaluationResult::not_applicable("remote-service"),
        }
    }
}

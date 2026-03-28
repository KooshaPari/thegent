//! HTTP types for API operations.
//!
//! This module contains pure HTTP types without external dependencies.

use core::fmt;

/// HTTP methods.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum HttpMethod {
    Get,
    Post,
    Put,
    Patch,
    Delete,
    Head,
    Options,
}

impl HttpMethod {
    /// Convert to HTTP method string.
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::Get => "GET",
            Self::Post => "POST",
            Self::Put => "PUT",
            Self::Patch => "PATCH",
            Self::Delete => "DELETE",
            Self::Head => "HEAD",
            Self::Options => "OPTIONS",
        }
    }
}

impl fmt::Display for HttpMethod {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.as_str())
    }
}

/// HTTP status codes.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum StatusCode {
    // 1xx Informational
    Continue,
    SwitchingProtocols,
    
    // 2xx Success
    Ok,
    Created,
    Accepted,
    NoContent,
    
    // 3xx Redirection
    MovedPermanently,
    Found,
    SeeOther,
    NotModified,
    
    // 4xx Client Errors
    BadRequest,
    Unauthorized,
    Forbidden,
    NotFound,
    MethodNotAllowed,
    Conflict,
    UnprocessableEntity,
    TooManyRequests,
    
    // 5xx Server Errors
    InternalServerError,
    NotImplemented,
    BadGateway,
    ServiceUnavailable,
    GatewayTimeout,
    
    // Custom
    Unknown(u16),
}

impl StatusCode {
    /// Create from u16 status code.
    pub fn from_u16(code: u16) -> Self {
        match code {
            100 => Self::Continue,
            101 => Self::SwitchingProtocols,
            200 => Self::Ok,
            201 => Self::Created,
            202 => Self::Accepted,
            204 => Self::NoContent,
            301 => Self::MovedPermanently,
            302 => Self::Found,
            303 => Self::SeeOther,
            304 => Self::NotModified,
            400 => Self::BadRequest,
            401 => Self::Unauthorized,
            403 => Self::Forbidden,
            404 => Self::NotFound,
            405 => Self::MethodNotAllowed,
            409 => Self::Conflict,
            422 => Self::UnprocessableEntity,
            429 => Self::TooManyRequests,
            500 => Self::InternalServerError,
            501 => Self::NotImplemented,
            502 => Self::BadGateway,
            503 => Self::ServiceUnavailable,
            504 => Self::GatewayTimeout,
            n => Self::Unknown(n),
        }
    }

    /// Convert to u16.
    pub fn as_u16(&self) -> u16 {
        match self {
            Self::Continue => 100,
            Self::SwitchingProtocols => 101,
            Self::Ok => 200,
            Self::Created => 201,
            Self::Accepted => 202,
            Self::NoContent => 204,
            Self::MovedPermanently => 301,
            Self::Found => 302,
            Self::SeeOther => 303,
            Self::NotModified => 304,
            Self::BadRequest => 400,
            Self::Unauthorized => 401,
            Self::Forbidden => 403,
            Self::NotFound => 404,
            Self::MethodNotAllowed => 405,
            Self::Conflict => 409,
            Self::UnprocessableEntity => 422,
            Self::TooManyRequests => 429,
            Self::InternalServerError => 500,
            Self::NotImplemented => 501,
            Self::BadGateway => 502,
            Self::ServiceUnavailable => 503,
            Self::GatewayTimeout => 504,
            Self::Unknown(n) => *n,
        }
    }

    /// Check if status is success (2xx).
    pub fn is_success(&self) -> bool {
        matches!(self, Self::Ok | Self::Created | Self::Accepted | Self::NoContent)
    }

    /// Check if status is redirect (3xx).
    pub fn is_redirect(&self) -> bool {
        matches!(self, Self::MovedPermanently | Self::Found | Self::SeeOther | Self::NotModified)
    }

    /// Check if status is client error (4xx).
    pub fn is_client_error(&self) -> bool {
        matches!(self,
            Self::BadRequest | Self::Unauthorized | Self::Forbidden |
            Self::NotFound | Self::MethodNotAllowed | Self::Conflict |
            Self::UnprocessableEntity | Self::TooManyRequests
        )
    }

    /// Check if status is server error (5xx).
    pub fn is_server_error(&self) -> bool {
        matches!(self,
            Self::InternalServerError | Self::NotImplemented |
            Self::BadGateway | Self::ServiceUnavailable | Self::GatewayTimeout
        )
    }

    /// Get reason phrase.
    pub fn reason_phrase(&self) -> &'static str {
        match self {
            Self::Continue => "Continue",
            Self::SwitchingProtocols => "Switching Protocols",
            Self::Ok => "OK",
            Self::Created => "Created",
            Self::Accepted => "Accepted",
            Self::NoContent => "No Content",
            Self::MovedPermanently => "Moved Permanently",
            Self::Found => "Found",
            Self::SeeOther => "See Other",
            Self::NotModified => "Not Modified",
            Self::BadRequest => "Bad Request",
            Self::Unauthorized => "Unauthorized",
            Self::Forbidden => "Forbidden",
            Self::NotFound => "Not Found",
            Self::MethodNotAllowed => "Method Not Allowed",
            Self::Conflict => "Conflict",
            Self::UnprocessableEntity => "Unprocessable Entity",
            Self::TooManyRequests => "Too Many Requests",
            Self::InternalServerError => "Internal Server Error",
            Self::NotImplemented => "Not Implemented",
            Self::BadGateway => "Bad Gateway",
            Self::ServiceUnavailable => "Service Unavailable",
            Self::GatewayTimeout => "Gateway Timeout",
            Self::Unknown(_) => "Unknown",
        }
    }
}

impl fmt::Display for StatusCode {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{} {}", self.as_u16(), self.reason_phrase())
    }
}

/// Media types.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum MediaType {
    Json,
    Xml,
    Html,
    Text,
    FormData,
    UrlEncoded,
    Binary,
    Custom(String),
}

impl MediaType {
    /// Parse from string.
    pub fn from_str(s: &str) -> Self {
        match s.split(';').next().unwrap_or(s).trim() {
            "application/json" | "text/json" => Self::Json,
            "application/xml" | "text/xml" => Self::Xml,
            "text/html" => Self::Html,
            "text/plain" => Self::Text,
            "multipart/form-data" => Self::FormData,
            "application/x-www-form-urlencoded" => Self::UrlEncoded,
            _ if s.starts_with("application/") || s.starts_with("image/") || s.starts_with("audio/") || s.starts_with("video/") => Self::Binary,
            other => Self::Custom(other.to_string()),
        }
    }

    /// Get content type header value.
    pub fn as_content_type(&self) -> &'static str {
        match self {
            Self::Json => "application/json",
            Self::Xml => "application/xml",
            Self::Html => "text/html",
            Self::Text => "text/plain",
            Self::FormData => "multipart/form-data",
            Self::UrlEncoded => "application/x-www-form-urlencoded",
            Self::Binary => "application/octet-stream",
            Self::Custom(s) => s,
        }
    }
}

impl Default for MediaType {
    fn default() -> Self {
        Self::Json
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_status_code_conversion() {
        assert_eq!(StatusCode::from_u16(200), StatusCode::Ok);
        assert_eq!(StatusCode::from_u16(404), StatusCode::NotFound);
        assert_eq!(StatusCode::from_u16(500), StatusCode::InternalServerError);
        assert_eq!(StatusCode::from_u16(999), StatusCode::Unknown(999));
    }

    #[test]
    fn test_status_code_is_success() {
        assert!(StatusCode::Ok.is_success());
        assert!(StatusCode::Created.is_success());
        assert!(!StatusCode::BadRequest.is_success());
    }

    #[test]
    fn test_media_type() {
        assert_eq!(MediaType::from_str("application/json"), MediaType::Json);
        assert_eq!(MediaType::from_str("text/plain"), MediaType::Text);
    }
}

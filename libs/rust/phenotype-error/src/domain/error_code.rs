//! Error codes - Standardized error codes for the Phenotype ecosystem.
//!
//! Error codes follow the format: CATEGORY_SPECIFIC_ERROR
//! - Use uppercase with underscores
//! - Be specific about the error type
//! - Include category prefix for organization

use std::fmt;

/// Error codes for the Phenotype ecosystem.
///
/// Categories:
/// - 1000-1999: General errors
/// - 2000-2999: Validation errors
/// - 3000-3999: Domain errors
/// - 4000-4999: Infrastructure errors
/// - 5000-5999: Authentication errors
/// - 6000-6999: Authorization errors
/// - 7000-7999: External service errors
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
#[non_exhaustive]
pub enum ErrorCode {
    // General errors (1000-1999)
    /// Unknown error.
    Unknown = 1000,
    /// Operation not implemented.
    NotImplemented = 1001,
    /// Invalid state.
    InvalidState = 1002,
    /// Timeout.
    Timeout = 1003,
    /// Cancellation.
    Cancelled = 1004,
    /// Precondition failed.
    PreconditionFailed = 1005,
    /// Postcondition failed.
    PostconditionFailed = 1006,

    // Validation errors (2000-2999)
    /// Validation error.
    ValidationError = 2000,
    /// Invalid input.
    InvalidInput = 2001,
    /// Missing required field.
    MissingRequiredField = 2002,
    /// Invalid format.
    InvalidFormat = 2003,
    /// Invalid length.
    InvalidLength = 2004,
    /// Invalid type.
    InvalidType = 2005,
    /// Out of range.
    OutOfRange = 2006,

    // Domain errors (3000-3999)
    /// Entity not found.
    EntityNotFound = 3000,
    /// Duplicate entity.
    DuplicateEntity = 3001,
    /// Business rule violation.
    BusinessRuleViolation = 3002,
    /// Invalid state transition.
    InvalidStateTransition = 3003,
    /// Aggregate error.
    AggregateError = 3004,
    /// Concurrency error.
    ConcurrencyError = 3005,

    // Infrastructure errors (4000-4999)
    /// Database error.
    DatabaseError = 4000,
    /// Cache error.
    CacheError = 4001,
    /// Network error.
    NetworkError = 4002,
    /// Connection error.
    ConnectionError = 4003,
    /// Storage error.
    StorageError = 4004,
    /// Configuration error.
    ConfigurationError = 4005,

    // Authentication errors (5000-5999)
    /// Authentication error.
    AuthenticationError = 5000,
    /// Token expired.
    TokenExpired = 5001,
    /// Token invalid.
    TokenInvalid = 5002,
    /// Token missing.
    TokenMissing = 5003,
    /// Credentials invalid.
    CredentialsInvalid = 5004,

    // Authorization errors (6000-6999)
    /// Authorization error.
    AuthorizationError = 6000,
    /// Permission denied.
    PermissionDenied = 6001,
    /// Access denied.
    AccessDenied = 6002,
    /// Resource forbidden.
    ResourceForbidden = 6003,

    // External service errors (7000-7999)
    /// External service error.
    ExternalServiceError = 7000,
    /// External service unavailable.
    ExternalServiceUnavailable = 7001,
    /// External service timeout.
    ExternalServiceTimeout = 7002,
    /// Rate limit exceeded.
    RateLimitExceeded = 7003,

    // Math errors (8000-8999)
    /// Division by zero.
    DivisionByZero = 8000,
    /// Overflow.
    Overflow = 8001,
    /// Underflow.
    Underflow = 8002,
    /// Precision loss.
    PrecisionLoss = 8003,
}

impl ErrorCode {
    /// Get the numeric code.
    pub fn code(&self) -> u16 {
        *self as u16
    }

    /// Get the category name.
    pub fn category(&self) -> &'static str {
        match self {
            // General
            Self::Unknown | Self::NotImplemented | Self::InvalidState | Self::Timeout
            | Self::Cancelled | Self::PreconditionFailed | Self::PostconditionFailed => {
                "general"
            }
            // Validation
            Self::ValidationError | Self::InvalidInput | Self::MissingRequiredField
            | Self::InvalidFormat | Self::InvalidLength | Self::InvalidType | Self::OutOfRange => {
                "validation"
            }
            // Domain
            Self::EntityNotFound | Self::DuplicateEntity | Self::BusinessRuleViolation
            | Self::InvalidStateTransition | Self::AggregateError | Self::ConcurrencyError => {
                "domain"
            }
            // Infrastructure
            Self::DatabaseError | Self::CacheError | Self::NetworkError | Self::ConnectionError
            | Self::StorageError | Self::ConfigurationError => "infrastructure",
            // Authentication
            Self::AuthenticationError | Self::TokenExpired | Self::TokenInvalid
            | Self::TokenMissing | Self::CredentialsInvalid => "authentication",
            // Authorization
            Self::AuthorizationError | Self::PermissionDenied | Self::AccessDenied
            | Self::ResourceForbidden => "authorization",
            // External
            Self::ExternalServiceError | Self::ExternalServiceUnavailable
            | Self::ExternalServiceTimeout | Self::RateLimitExceeded => "external",
            // Math
            Self::DivisionByZero | Self::Overflow | Self::Underflow | Self::PrecisionLoss => {
                "math"
            }
        }
    }

    /// Get a description.
    pub fn description(&self) -> &'static str {
        match self {
            Self::Unknown => "An unknown error occurred",
            Self::NotImplemented => "This operation is not implemented",
            Self::InvalidState => "The state is invalid",
            Self::Timeout => "The operation timed out",
            Self::Cancelled => "The operation was cancelled",
            Self::PreconditionFailed => "A precondition was not met",
            Self::PostconditionFailed => "A postcondition was not met",
            Self::ValidationError => "Validation failed",
            Self::InvalidInput => "The input is invalid",
            Self::MissingRequiredField => "A required field is missing",
            Self::InvalidFormat => "The format is invalid",
            Self::InvalidLength => "The length is invalid",
            Self::InvalidType => "The type is invalid",
            Self::OutOfRange => "The value is out of range",
            Self::EntityNotFound => "The entity was not found",
            Self::DuplicateEntity => "A duplicate entity exists",
            Self::BusinessRuleViolation => "A business rule was violated",
            Self::InvalidStateTransition => "The state transition is invalid",
            Self::AggregateError => "An aggregate error occurred",
            Self::ConcurrencyError => "A concurrency error occurred",
            Self::DatabaseError => "A database error occurred",
            Self::CacheError => "A cache error occurred",
            Self::NetworkError => "A network error occurred",
            Self::ConnectionError => "A connection error occurred",
            Self::StorageError => "A storage error occurred",
            Self::ConfigurationError => "A configuration error occurred",
            Self::AuthenticationError => "Authentication failed",
            Self::TokenExpired => "The token has expired",
            Self::TokenInvalid => "The token is invalid",
            Self::TokenMissing => "The token is missing",
            Self::CredentialsInvalid => "The credentials are invalid",
            Self::AuthorizationError => "Authorization failed",
            Self::PermissionDenied => "Permission was denied",
            Self::AccessDenied => "Access was denied",
            Self::ResourceForbidden => "The resource is forbidden",
            Self::ExternalServiceError => "An external service error occurred",
            Self::ExternalServiceUnavailable => "The external service is unavailable",
            Self::ExternalServiceTimeout => "The external service timed out",
            Self::RateLimitExceeded => "The rate limit was exceeded",
            Self::DivisionByZero => "Division by zero",
            Self::Overflow => "Arithmetic overflow",
            Self::Underflow => "Arithmetic underflow",
            Self::PrecisionLoss => "Precision loss occurred",
        }
    }

    /// Parse from string.
    pub fn parse(s: &str) -> Option<Self> {
        match s.to_uppercase().as_str() {
            "UNKNOWN" => Some(Self::Unknown),
            "NOT_IMPLEMENTED" => Some(Self::NotImplemented),
            "INVALID_STATE" => Some(Self::InvalidState),
            "TIMEOUT" => Some(Self::Timeout),
            "CANCELLED" => Some(Self::Cancelled),
            "PRECONDITION_FAILED" => Some(Self::PreconditionFailed),
            "POSTCONDITION_FAILED" => Some(Self::PostconditionFailed),
            "VALIDATION_ERROR" => Some(Self::ValidationError),
            "INVALID_INPUT" => Some(Self::InvalidInput),
            "MISSING_REQUIRED_FIELD" => Some(Self::MissingRequiredField),
            "INVALID_FORMAT" => Some(Self::InvalidFormat),
            "INVALID_LENGTH" => Some(Self::InvalidLength),
            "INVALID_TYPE" => Some(Self::InvalidType),
            "OUT_OF_RANGE" => Some(Self::OutOfRange),
            "ENTITY_NOT_FOUND" => Some(Self::EntityNotFound),
            "DUPLICATE_ENTITY" => Some(Self::DuplicateEntity),
            "BUSINESS_RULE_VIOLATION" => Some(Self::BusinessRuleViolation),
            "INVALID_STATE_TRANSITION" => Some(Self::InvalidStateTransition),
            "AGGREGATE_ERROR" => Some(Self::AggregateError),
            "CONCURRENCY_ERROR" => Some(Self::ConcurrencyError),
            "DATABASE_ERROR" => Some(Self::DatabaseError),
            "CACHE_ERROR" => Some(Self::CacheError),
            "NETWORK_ERROR" => Some(Self::NetworkError),
            "CONNECTION_ERROR" => Some(Self::ConnectionError),
            "STORAGE_ERROR" => Some(Self::StorageError),
            "CONFIGURATION_ERROR" => Some(Self::ConfigurationError),
            "AUTHENTICATION_ERROR" => Some(Self::AuthenticationError),
            "TOKEN_EXPIRED" => Some(Self::TokenExpired),
            "TOKEN_INVALID" => Some(Self::TokenInvalid),
            "TOKEN_MISSING" => Some(Self::TokenMissing),
            "CREDENTIALS_INVALID" => Some(Self::CredentialsInvalid),
            "AUTHORIZATION_ERROR" => Some(Self::AuthorizationError),
            "PERMISSION_DENIED" => Some(Self::PermissionDenied),
            "ACCESS_DENIED" => Some(Self::AccessDenied),
            "RESOURCE_FORBIDDEN" => Some(Self::ResourceForbidden),
            "EXTERNAL_SERVICE_ERROR" => Some(Self::ExternalServiceError),
            "EXTERNAL_SERVICE_UNAVAILABLE" => Some(Self::ExternalServiceUnavailable),
            "EXTERNAL_SERVICE_TIMEOUT" => Some(Self::ExternalServiceTimeout),
            "RATE_LIMIT_EXCEEDED" => Some(Self::RateLimitExceeded),
            "DIVISION_BY_ZERO" => Some(Self::DivisionByZero),
            "OVERFLOW" => Some(Self::Overflow),
            "UNDERFLOW" => Some(Self::Underflow),
            "PRECISION_LOSS" => Some(Self::PrecisionLoss),
            _ => None,
        }
    }
}

impl fmt::Display for ErrorCode {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{:?}", self)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_error_code_category() {
        assert_eq!(ErrorCode::Unknown.category(), "general");
        assert_eq!(ErrorCode::ValidationError.category(), "validation");
        assert_eq!(ErrorCode::EntityNotFound.category(), "domain");
        assert_eq!(ErrorCode::DatabaseError.category(), "infrastructure");
    }

    #[test]
    fn test_error_code_description() {
        assert!(!ErrorCode::Unknown.description().is_empty());
        assert!(!ErrorCode::EntityNotFound.description().is_empty());
    }

    #[test]
    fn test_error_code_parse() {
        assert_eq!(ErrorCode::parse("ENTITY_NOT_FOUND"), Some(ErrorCode::EntityNotFound));
        assert_eq!(ErrorCode::parse("entity_not_found"), Some(ErrorCode::EntityNotFound));
        assert_eq!(ErrorCode::parse("invalid"), None);
    }
}

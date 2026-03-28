// Package errors contains error types for the SDK.
package errors

import (
	"errors"
	"fmt"
)

// Error codes
const (
	CodeSDKError           = "SDK_ERROR"
	CodeConfigError        = "CONFIG_ERROR"
	CodeAuthError         = "AUTH_ERROR"
	CodeRateLimitError    = "RATE_LIMIT_ERROR"
	CodeAPIError          = "API_ERROR"
	CodeNetworkError      = "NETWORK_ERROR"
	CodeTimeoutError      = "TIMEOUT_ERROR"
	CodeValidationError   = "VALIDATION_ERROR"
	CodeNotFoundError     = "NOT_FOUND_ERROR"
)

// SDKError is the base error type.
type SDKError struct {
	Code    string
	Message string
	Cause   error
	Context map[string]interface{}
}

func (e *SDKError) Error() string {
	if e.Cause != nil {
		return fmt.Sprintf("[%s] %s: %v", e.Code, e.Message, e.Cause)
	}
	return fmt.Sprintf("[%s] %s", e.Code, e.Message)
}

func (e *SDKError) Unwrap() error {
	return e.Cause
}

// ConfigError is a configuration error.
type ConfigError struct {
	SDKError
}

func NewConfigError(message string) *ConfigError {
	return &ConfigError{
		SDKError: SDKError{
			Code:    CodeConfigError,
			Message: message,
		},
	}
}

// AuthError is an authentication error.
type AuthError struct {
	SDKError
}

func NewAuthError(message string) *AuthError {
	return &AuthError{
		SDKError: SDKError{
			Code:    CodeAuthError,
			Message: message,
		},
	}
}

// RateLimitError is a rate limit error.
type RateLimitError struct {
	SDKError
	RetryAfter int
}

func NewRateLimitError(retryAfter int) *RateLimitError {
	return &RateLimitError{
		SDKError: SDKError{
			Code:    CodeRateLimitError,
			Message: "Rate limit exceeded",
		},
		RetryAfter: retryAfter,
	}
}

// APIError is an API error.
type APIError struct {
	SDKError
	StatusCode int
}

func NewAPIError(statusCode int, message string) *APIError {
	return &APIError{
		SDKError: SDKError{
			Code:    fmt.Sprintf("%s_%d", CodeAPIError, statusCode),
			Message: message,
		},
		StatusCode: statusCode,
	}
}

// NetworkError is a network error.
type NetworkError struct {
	SDKError
}

func NewNetworkError(message string) *NetworkError {
	return &NetworkError{
		SDKError: SDKError{
			Code:    CodeNetworkError,
			Message: message,
		},
	}
}

// TimeoutError is a timeout error.
type TimeoutError struct {
	SDKError
}

func NewTimeoutError() *TimeoutError {
	return &TimeoutError{
		SDKError: SDKError{
			Code:    CodeTimeoutError,
			Message: "Request timed out",
		},
	}
}

// ValidationError is a validation error.
type ValidationError struct {
	SDKError
	FieldErrors []FieldError
}

type FieldError struct {
	Field   string
	Message string
}

func NewValidationError(message string) *ValidationError {
	return &ValidationError{
		SDKError: SDKError{
			Code:    CodeValidationError,
			Message: message,
		},
	}
}

// NotFoundError is a not found error.
type NotFoundError struct {
	SDKError
	ResourceType string
	ResourceID   string
}

func NewNotFoundError(resourceType, resourceID string) *NotFoundError {
	return &NotFoundError{
		SDKError: SDKError{
			Code:    CodeNotFoundError,
			Message: fmt.Sprintf("%s '%s' not found", resourceType, resourceID),
		},
		ResourceType: resourceType,
		ResourceID:   resourceID,
	}
}

// IsRetryable returns true if the error is retryable.
func IsRetryable(err error) bool {
	var rateLimitErr *RateLimitError
	if errors.As(err, &rateLimitErr) {
		return true
	}

	var networkErr *NetworkError
	if errors.As(err, &networkErr) {
		return true
	}

	var timeoutErr *TimeoutError
	if errors.As(err, &timeoutErr) {
		return true
	}

	return false
}

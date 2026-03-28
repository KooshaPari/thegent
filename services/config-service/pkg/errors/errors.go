// Package errors provides unified error handling for Phenotype services.
package errors

import (
	"fmt"
	"net/http"
)

// Error kinds categorize errors by their nature.
type Kind string

const (
	KindValidation    Kind = "validation"
	KindNotFound      Kind = "not_found"
	KindConflict      Kind = "conflict"
	KindUnauthorized   Kind = "unauthorized"
	KindInternal       Kind = "internal"
)

// DomainError represents a domain-level error.
type DomainError struct {
	Kind       Kind   `json:"kind"`
	Code       string `json:"code"`
	Message    string `json:"message"`
	Field      string `json:"field,omitempty"`
	details    string
	httpStatus int
}

func (e *DomainError) Error() string {
	if e.details != "" {
		return fmt.Sprintf("%s: %s (%s)", e.Code, e.Message, e.details)
	}
	return fmt.Sprintf("%s: %s", e.Code, e.Message)
}

// WithDetails adds additional details to the error.
func (e *DomainError) WithDetails(details string) *DomainError {
	return &DomainError{
		Kind:       e.Kind,
		Code:       e.Code,
		Message:    e.Message,
		Field:      e.Field,
		details:    details,
		httpStatus: e.httpStatus,
	}
}

// WithField adds field information for validation errors.
func (e *DomainError) WithField(field string) *DomainError {
	return &DomainError{
		Kind:       e.Kind,
		Code:       e.Code,
		Message:    e.Message,
		Field:      field,
		details:    e.details,
		httpStatus: e.httpStatus,
	}
}

// HTTPStatus returns the appropriate HTTP status code.
func (e *DomainError) HTTPStatus() int {
	if e.httpStatus != 0 {
		return e.httpStatus
	}
	switch e.Kind {
	case KindValidation:
		return http.StatusBadRequest
	case KindNotFound:
		return http.StatusNotFound
	case KindConflict:
		return http.StatusConflict
	case KindUnauthorized:
		return http.StatusUnauthorized
	default:
		return http.StatusInternalServerError
	}
}

// NewValidationError creates a new validation error.
func NewValidationError(message string) *DomainError {
	return &DomainError{
		Kind:       KindValidation,
		Code:       "VALIDATION_ERROR",
		Message:    message,
		httpStatus: http.StatusBadRequest,
	}
}

// NewNotFoundError creates a new not found error.
func NewNotFoundError(resource, id string) *DomainError {
	return &DomainError{
		Kind:       KindNotFound,
		Code:       "NOT_FOUND",
		Message:    fmt.Sprintf("%s not found: %s", resource, id),
		httpStatus: http.StatusNotFound,
	}
}

// NewConflictError creates a new conflict error.
func NewConflictError(message string) *DomainError {
	return &DomainError{
		Kind:       KindConflict,
		Code:       "CONFLICT",
		Message:    message,
		httpStatus: http.StatusConflict,
	}
}

// NewInternalError creates a new internal error.
func NewInternalError(message string) *DomainError {
	return &DomainError{
		Kind:       KindInternal,
		Code:       "INTERNAL_ERROR",
		Message:    message,
		httpStatus: http.StatusInternalServerError,
	}
}

// IsDomainError checks if an error is a DomainError.
func IsDomainError(err error) bool {
	_, ok := err.(*DomainError)
	return ok
}

// AsDomainError converts an error to DomainError if possible.
func AsDomainError(err error) (*DomainError, bool) {
	if de, ok := err.(*DomainError); ok {
		return de, true
	}
	return NewInternalError(err.Error()), false
}

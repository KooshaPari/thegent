package byteport

import "fmt"

// BytePortError represents a BytePort SDK error
type BytePortError struct {
	Message    string
	StatusCode int
	Details    string
}

func (e *BytePortError) Error() string {
	if e.Details != "" {
		return fmt.Sprintf("BytePort API error (status %d): %s - %s", e.StatusCode, e.Message, e.Details)
	}
	return fmt.Sprintf("BytePort API error (status %d): %s", e.StatusCode, e.Message)
}

// NewBytePortError creates a new BytePortError
func NewBytePortError(message string, statusCode int, details string) *BytePortError {
	return &BytePortError{
		Message:    message,
		StatusCode: statusCode,
		Details:    details,
	}
}

// IsNotFoundError returns true if the error is a 404 Not Found error
func IsNotFoundError(err error) bool {
	if bpErr, ok := err.(*BytePortError); ok {
		return bpErr.StatusCode == 404
	}
	return false
}

// IsBadRequestError returns true if the error is a 400 Bad Request error
func IsBadRequestError(err error) bool {
	if bpErr, ok := err.(*BytePortError); ok {
		return bpErr.StatusCode == 400
	}
	return false
}

// IsServerError returns true if the error is a 5xx server error
func IsServerError(err error) bool {
	if bpErr, ok := err.(*BytePortError); ok {
		return bpErr.StatusCode >= 500
	}
	return false
}

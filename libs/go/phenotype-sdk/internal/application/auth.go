// Package application contains application services.
package application

import (
	"sync"
	"time"

	"github.com/phenotype/go-sdk/internal/domain"
)

// AuthService handles authentication.
type AuthService struct {
	config       *domain.Config
	accessToken  string
	refreshToken string
	expiresAt    time.Time
	mu           sync.RWMutex
}

// NewAuthService creates a new auth service.
func NewAuthService(config *domain.Config) *AuthService {
	return &AuthService{
		config: config,
	}
}

// GetHeaders returns the authentication headers.
func (s *AuthService) GetHeaders() map[string]string {
	s.mu.RLock()
	defer s.mu.RUnlock()

	headers := make(map[string]string)

	if s.config.APIKey != "" {
		headers["Authorization"] = "Bearer " + s.config.APIKey
	}

	if s.accessToken != "" {
		if time.Now().After(s.expiresAt.Add(-time.Minute)) {
			// Token expired or about to expire
			headers["Authorization"] = "Bearer " + s.accessToken
		}
	}

	return headers
}

// SetTokens sets the authentication tokens.
func (s *AuthService) SetTokens(accessToken, refreshToken string, expiresInSeconds int) {
	s.mu.Lock()
	defer s.mu.Unlock()

	s.accessToken = accessToken
	s.refreshToken = refreshToken
	s.expiresAt = time.Now().Add(time.Duration(expiresInSeconds) * time.Second)
}

// Clear clears all tokens.
func (s *AuthService) Clear() {
	s.mu.Lock()
	defer s.mu.Unlock()

	s.accessToken = ""
	s.refreshToken = ""
	s.expiresAt = time.Time{}
}

// IsExpired returns true if the token is expired.
func (s *AuthService) IsExpired() bool {
	s.mu.RLock()
	defer s.mu.RUnlock()

	if s.accessToken == "" {
		return true
	}

	return time.Now().After(s.expiresAt.Add(-time.Minute))
}

// NewRateLimitError creates a rate limit error.
func NewRateLimitError(retryAfter string) error {
	var retryAfterSecs int
	if retryAfter != "" {
		// Parse retry-after header
		// Could use strconv.Atoi here
	}

	return &domain.RateLimitError{
		Code:        domain.CodeRateLimitError,
		Message:     "Rate limit exceeded",
		RetryAfter: retryAfterSecs,
	}
}
